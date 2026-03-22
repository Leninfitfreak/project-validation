from __future__ import annotations

import json
import subprocess
from pathlib import Path

from validator_engine.validators import ValidationResult


class InfraTests:
    BAD_WAITING = {'CrashLoopBackOff', 'ImagePullBackOff', 'Error', 'Pending', 'NotReady'}

    def __init__(self, root: Path, env: dict, model: dict, evidence, catalog) -> None:
        self.root = root
        self.env = env
        self.model = model
        self.evidence = evidence
        self.test_ids = catalog.require('INF-001', 'INF-002', 'INF-003', 'INF-004', 'INF-005', 'INF-006')

    def _json(self, *args: str) -> dict:
        result = subprocess.run(['kubectl', *args, '-o', 'json'], capture_output=True, text=True, check=True)
        return json.loads(result.stdout)

    def repair(self) -> list[str]:
        return []

    def run(self, context: dict) -> ValidationResult:
        nodes = self._json('get', 'nodes')['items']
        namespaces = {item['metadata']['name'] for item in self._json('get', 'ns')['items']}
        pods = self._json('get', 'pods', '-A')['items']
        services = self._json('get', 'svc', '-A')['items']
        ingresses = self._json('get', 'ingress', '-A')['items']
        core = {
            'frontend': False,
            'product-service': False,
            'order-service': False,
            'postgres': False,
            'grafana': False,
            'prometheus': False,
            'loki': False,
            'promtail': False,
        }
        bad = []
        for pod in pods:
            namespace = pod['metadata']['namespace']
            name = pod['metadata']['name']
            if namespace != 'dev':
                continue
            for key in core:
                if key in name and pod['status'].get('phase') == 'Running':
                    ready = all(cs.get('ready') for cs in pod['status'].get('containerStatuses', []))
                    core[key] = core[key] or ready
            reasons = []
            for status in pod['status'].get('containerStatuses', []):
                waiting = status.get('state', {}).get('waiting', {})
                reason = waiting.get('reason')
                if reason in self.BAD_WAITING:
                    reasons.append(reason)
            if any(k in name for k in core) and reasons:
                bad.append({'name': name, 'reasons': reasons})
        ingress_paths = []
        for ingress in ingresses:
            for rule in ingress.get('spec', {}).get('rules', []):
                for path in rule.get('http', {}).get('paths', []):
                    ingress_paths.append(path.get('path'))
        success = all(cs['type'] == 'Ready' and cs['status'] == 'True' for cs in nodes[0]['status']['conditions'] if cs['type'] == 'Ready') and {'argocd', 'dev', 'vault', 'external-secrets-system', 'ingress-nginx'}.issubset(namespaces) and all(core.values()) and {'/', '/auth', '/api/products', '/api/orders'}.issubset(set(ingress_paths)) and not bad
        details = {'nodes': [node['metadata']['name'] for node in nodes], 'namespaces': sorted(namespaces), 'core_workloads': core, 'service_count': len(services), 'ingress_paths': sorted(set(ingress_paths)), 'bad_core_pods': bad}
        self.evidence.record_result('infra', details)
        return ValidationResult('infra', success, 'Infrastructure validation passed' if success else 'Infrastructure validation failed', details, test_ids=self.test_ids)
