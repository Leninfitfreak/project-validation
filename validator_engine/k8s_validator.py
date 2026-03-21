from __future__ import annotations

import json
import subprocess
from pathlib import Path

from validator_engine.validators import ValidationResult


class K8sValidator:
    BAD_STATES = {'CrashLoopBackOff', 'ImagePullBackOff', 'Error', 'Pending', 'NotReady'}

    def __init__(self, root: Path, env: dict, model: dict, evidence) -> None:
        self.root = root
        self.env = env
        self.model = model
        self.evidence = evidence

    def _kubectl_json(self, args: list[str]) -> dict:
        result = subprocess.run(['kubectl', *args, '-o', 'json'], capture_output=True, text=True, check=True)
        return json.loads(result.stdout)

    def repair(self) -> ValidationResult:
        repairs: list[str] = []
        return ValidationResult('k8s-repair', True, 'No Kubernetes repair actions applied', {'repairs': repairs}, repairs)

    def validate(self) -> ValidationResult:
        pods = self._kubectl_json(['get', 'pods', '-A'])['items']
        bad = []
        for pod in pods:
            phase = pod['status'].get('phase', '')
            if phase == 'Succeeded':
                continue
            reasons = []
            for status in pod['status'].get('containerStatuses', []):
                waiting = status.get('state', {}).get('waiting', {})
                reason = waiting.get('reason')
                if reason in self.BAD_STATES:
                    reasons.append(reason)
            if phase in {'Pending', 'Failed'} or reasons:
                bad.append({'namespace': pod['metadata']['namespace'], 'name': pod['metadata']['name'], 'phase': phase, 'reasons': reasons})
        details = {
            'bad_pods': bad,
            'nodes': len(self._kubectl_json(['get', 'nodes'])['items']),
            'services': len(self._kubectl_json(['get', 'svc', '-A'])['items']),
            'ingresses': len(self._kubectl_json(['get', 'ingress', '-A'])['items']),
        }
        self.evidence.record('k8s', details)
        return ValidationResult('kubernetes', not bad, 'Kubernetes infrastructure validated' if not bad else 'Kubernetes has failing pods', details)
