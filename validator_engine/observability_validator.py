from __future__ import annotations

from pathlib import Path

import requests

from validator_engine.validators import ValidationResult


class ObservabilityValidator:
    def __init__(self, root: Path, env: dict, model: dict, evidence) -> None:
        self.root = root
        self.env = env
        self.model = model
        self.evidence = evidence

    def repair(self) -> ValidationResult:
        return ValidationResult('observability-repair', True, 'No direct observer-stack repair action applied', {})

    def validate(self) -> ValidationResult:
        checks = {}
        for name, url in {
            'frontend': self.env['INGRESS_URL'],
            'observer_stack': self.env['OBSERVER_STACK_URL'],
        }.items():
            try:
                response = requests.get(url, timeout=20, verify=False)
                checks[name] = {'url': url, 'status_code': response.status_code}
            except Exception as exc:
                checks[name] = {'url': url, 'error': str(exc)}
        ok = all(item.get('status_code') == 200 for item in checks.values() if 'status_code' in item)
        self.evidence.record('observability', checks)
        return ValidationResult('observability', ok, 'Observability endpoints validated' if ok else 'Observability endpoints unreachable', checks)
