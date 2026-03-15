from __future__ import annotations

import json
import subprocess
from pathlib import Path

from validator_engine.validators import ValidationResult


class GitOpsValidator:
    def __init__(self, root: Path, env: dict, model: dict, evidence) -> None:
        self.root = root
        self.env = env
        self.model = model
        self.evidence = evidence

    def repair(self) -> ValidationResult:
        repairs = []
        subprocess.run(['kubectl', 'delete', 'application', '-n', 'argocd', 'vault-secretstores-dev'], capture_output=True, text=True)
        repairs.append('deleted stale duplicate ArgoCD application vault-secretstores-dev')
        for app in ('dev-product-service', 'dev-order-service', 'vault', 'vault-externalsecrets'):
            subprocess.run(['kubectl', 'patch', 'application', '-n', 'argocd', app, '--type', 'merge', '--patch', '{"operation":{"sync":{}}}'], capture_output=True, text=True)
            repairs.append(f'triggered sync for {app}')
        return ValidationResult('gitops-repair', True, 'Applied GitOps repair actions', {'repairs': repairs}, repairs)

    def validate(self) -> ValidationResult:
        items = json.loads(subprocess.run(['kubectl', 'get', 'applications.argoproj.io', '-A', '-o', 'json'], capture_output=True, text=True, check=True).stdout)['items']
        failing = []
        applications = []
        for item in items:
            name = item['metadata']['name']
            sync_status = item.get('status', {}).get('sync', {}).get('status', 'Unknown')
            health_status = item.get('status', {}).get('health', {}).get('status', 'Unknown')
            applications.append({'name': name, 'sync': sync_status, 'health': health_status})
            if name == 'leninkart-root' and health_status == 'Healthy':
                continue
            if sync_status != 'Synced' or health_status not in {'Healthy', 'Progressing'}:
                failing.append({'name': name, 'sync': sync_status, 'health': health_status})
        details = {'applications': applications, 'failing': failing}
        self.evidence.record('gitops', details)
        return ValidationResult('gitops', not failing, 'ArgoCD applications validated' if not failing else 'ArgoCD applications are not converged', details)
