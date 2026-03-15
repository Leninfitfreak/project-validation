from __future__ import annotations

import json
import subprocess
from pathlib import Path

from validator_engine.validators import ValidationResult


class VaultValidator:
    def __init__(self, root: Path, env: dict, model: dict, evidence) -> None:
        self.root = root
        self.env = env
        self.model = model
        self.evidence = evidence

    def repair(self) -> ValidationResult:
        status = subprocess.run(['kubectl', 'exec', '-n', 'vault', 'vault-0', '--', 'vault', 'status', '-format=json'], capture_output=True, text=True)
        repairs = []
        if status.returncode == 0:
            payload = json.loads(status.stdout)
            if payload.get('sealed'):
                subprocess.run(['kubectl', 'exec', '-n', 'vault', 'vault-0', '--', 'vault', 'operator', 'unseal', self.env['VAULT_UNSEAL_KEY']], capture_output=True, text=True)
                repairs.append('unsealed vault')
        return ValidationResult('vault-repair', True, 'Applied Vault repair actions', {'repairs': repairs}, repairs)

    def validate(self) -> ValidationResult:
        pod = json.loads(subprocess.run(['kubectl', 'get', 'pods', '-n', 'vault', '-o', 'json'], capture_output=True, text=True, check=True).stdout)
        vault_ready = any(item['metadata']['name'] == 'vault-0' and all(cs.get('ready') for cs in item['status'].get('containerStatuses', [])) for item in pod['items'])
        ext = json.loads(subprocess.run(['kubectl', 'get', 'externalsecret', '-n', 'dev', '-o', 'json'], capture_output=True, text=True, check=True).stdout)
        unsynced = [item['metadata']['name'] for item in ext['items'] if not any(cond.get('type') == 'Ready' and cond.get('status') == 'True' for cond in item.get('status', {}).get('conditions', []))]
        details = {'vault_ready': vault_ready, 'unsynced_external_secrets': unsynced}
        self.evidence.record('vault', details)
        return ValidationResult('vault', vault_ready and not unsynced, 'Vault validated' if vault_ready and not unsynced else 'Vault or ExternalSecrets not healthy', details)
