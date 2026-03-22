from __future__ import annotations

import base64
import os
import re
import subprocess
from pathlib import Path


class SecretsLoader:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.secret_file = self._locate_secret_file()
        self.env_file = root / '.env'

    def _locate_secret_file(self) -> Path | None:
        for name in ('local-secrets.txt', 'local-secrets.txt.txt'):
            candidate = self.root / name
            if candidate.exists():
                return candidate
        return None

    def _extract(self, pattern: str, text: str) -> str:
        match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
        return match.group(1).strip() if match else ''

    def _kubectl_secret(self, namespace: str, name: str, key: str) -> str:
        try:
            result = subprocess.run(
                ['kubectl', 'get', 'secret', '-n', namespace, name, '-o', f'jsonpath={{.data.{key}}}'],
                check=True,
                capture_output=True,
                text=True,
            )
            raw = result.stdout.strip()
            return base64.b64decode(raw).decode() if raw else ''
        except Exception:
            return ''

    def ensure_env(self) -> dict[str, str]:
        text = self.secret_file.read_text(encoding='utf-8') if self.secret_file else ''
        observer_user = self._extract(r'username\s*:\s*(.+)', text)
        observer_password = self._extract(r'password\s*:\s*(.+)', text)
        vault_root_token = self._extract(r'Initial root token\s*\n\s*(.+)', text)
        vault_unseal_key = self._extract(r'Key\s+1\s*\n\s*(.+)', text)
        argocd_password = self._extract(r'ARGOCD_PASSWORD\s*[:=]\s*(.+)', text) or self._kubectl_secret('argocd', 'argocd-initial-admin-secret', 'password')
        argocd_user = self._extract(r'ARGOCD_USERNAME\s*[:=]\s*(.+)', text) or 'admin'
        grafana_user = self._kubectl_secret('dev', 'grafana-admin-secret', 'admin-user') or 'admin'
        grafana_password = self._kubectl_secret('dev', 'grafana-admin-secret', 'admin-password')
        env = {
            'PLATFORM_ENV': 'local',
            'KUBE_NAMESPACE': 'dev',
            'INGRESS_URL': 'http://127.0.0.1/',
            'ARGOCD_URL': 'http://127.0.0.1:8085',
            'VAULT_URL': 'http://127.0.0.1:8205',
            'GRAFANA_URL': 'http://127.0.0.1:3000',
            'PROMETHEUS_URL': 'http://127.0.0.1:9090',
            'LOKI_URL': 'http://127.0.0.1:3100',
            'GRAFANA_USERNAME': grafana_user,
            'GRAFANA_PASSWORD': grafana_password,
            'OBSERVER_STACK_USER': observer_user,
            'OBSERVER_STACK_PASSWORD': observer_password,
            'VAULT_ROOT_TOKEN': vault_root_token,
            'VAULT_UNSEAL_KEY': vault_unseal_key,
            'ARGOCD_USERNAME': argocd_user,
            'ARGOCD_PASSWORD': argocd_password,
        }
        self.env_file.write_text('\n'.join(f'{key}={value}' for key, value in env.items()) + '\n', encoding='utf-8')
        os.environ.update(env)
        return env
