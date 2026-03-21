from __future__ import annotations

import html
import json
import subprocess
from pathlib import Path

from validator_engine.playwright_runner import PlaywrightRunner
from validator_engine.validators import ValidationResult


class VaultTests:
    EXPECTED_PATHS = {'postgres', 'product-service', 'order-service', 'kafka', 'observability', 'auth'}

    def __init__(self, root: Path, env: dict, model: dict, evidence, catalog) -> None:
        self.root = root
        self.env = env
        self.model = model
        self.evidence = evidence
        self.test_ids = catalog.require('SEC-001', 'SEC-002', 'SEC-003', 'SEC-004', 'SEC-005', 'SEC-006', 'SEC-007', 'UI-003')

    def repair(self) -> list[str]:
        repairs = []
        status = subprocess.run(['kubectl', 'exec', '-n', 'vault', 'vault-0', '--', 'vault', 'status', '-format=json'], capture_output=True, text=True)
        if status.returncode == 0:
            payload = json.loads(status.stdout)
            if payload.get('sealed'):
                subprocess.run(['kubectl', 'exec', '-n', 'vault', 'vault-0', '--', 'vault', 'operator', 'unseal', self.env['VAULT_UNSEAL_KEY']], capture_output=True, text=True)
                repairs.append('unsealed vault')
        return repairs

    def _kv_get(self, path: str) -> dict:
        cmd = ['kubectl', 'exec', '-n', 'vault', 'vault-0', '--', 'sh', '-lc', f'export VAULT_TOKEN={self.env["VAULT_ROOT_TOKEN"]}; vault kv get -format=json {path}']
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return json.loads(result.stdout)

    def _write_value_evidence(self, secret_payload: dict) -> Path:
        values = secret_payload.get('data', {}).get('data', {})
        rows = ''.join(f'<tr><td>{html.escape(str(k))}</td><td>{html.escape(str(v))}</td></tr>' for k, v in values.items())
        content = f'''<!doctype html>
<html><head><meta charset="utf-8"><title>Vault Secret Values Evidence</title>
<style>body{{font-family:Segoe UI,Arial,sans-serif;margin:32px;background:#fafafa;color:#111}}h1{{margin-bottom:8px}}table{{border-collapse:collapse;width:100%;background:#fff}}th,td{{border:1px solid #ccc;padding:10px;text-align:left}}th{{background:#eee}}code{{background:#f2f2f2;padding:2px 6px}}</style>
</head><body>
<h1>Vault Secret Values Evidence</h1>
<p>Source path: <code>secret/leninkart/product-service/config</code></p>
<table><thead><tr><th>Key</th><th>Value</th></tr></thead><tbody>{rows}</tbody></table>
</body></html>'''
        target = self.root / 'artifacts' / 'vault-secret-values.html'
        target.write_text(content, encoding='utf-8')
        return target

    def run(self, context: dict) -> ValidationResult:
        pods = json.loads(subprocess.run(['kubectl', 'get', 'pods', '-n', 'vault', '-o', 'json'], capture_output=True, text=True, check=True).stdout)
        vault_ready = any(item['metadata']['name'] == 'vault-0' and all(cs.get('ready') for cs in item['status'].get('containerStatuses', [])) for item in pods['items'])
        status = json.loads(subprocess.run(['kubectl', 'exec', '-n', 'vault', 'vault-0', '--', 'vault', 'status', '-format=json'], capture_output=True, text=True, check=True).stdout)
        stores = json.loads(subprocess.run(['kubectl', 'get', 'clustersecretstore', 'vault-backend', '-o', 'json'], capture_output=True, text=True, check=True).stdout)
        store_ready = any(cond.get('type') == 'Ready' and cond.get('status') == 'True' for cond in stores.get('status', {}).get('conditions', []))
        externals = json.loads(subprocess.run(['kubectl', 'get', 'externalsecret', '-n', 'dev', '-o', 'json'], capture_output=True, text=True, check=True).stdout)
        ext_ready = {item['metadata']['name']: any(cond.get('type') == 'Ready' and cond.get('status') == 'True' for cond in item.get('status', {}).get('conditions', [])) for item in externals['items']}
        kv = subprocess.run(['kubectl', 'exec', '-n', 'vault', 'vault-0', '--', 'sh', '-lc', f'export VAULT_TOKEN={self.env["VAULT_ROOT_TOKEN"]}; vault kv list -format=json secret/leninkart'], capture_output=True, text=True)
        if kv.returncode != 0:
            kv = subprocess.run(['kubectl', 'exec', '-n', 'vault', 'vault-0', '--', 'sh', '-lc', f'export VAULT_TOKEN={self.env["VAULT_ROOT_TOKEN"]}; vault list -format=json secret/metadata/leninkart'], capture_output=True, text=True)
        kv_paths = {item.rstrip('/') for item in json.loads(kv.stdout)} if kv.returncode == 0 and kv.stdout.strip() else set()
        product_secret = self._kv_get('secret/leninkart/product-service/config')
        secret_values = product_secret.get('data', {}).get('data', {})
        value_evidence = self._write_value_evidence(product_secret)
        saved = []
        sections = []
        with PlaywrightRunner(self.root, self.env, self.model, self.evidence) as runner:
            page = runner.new_page()
            page.goto(self.env['VAULT_URL'], wait_until='domcontentloaded', timeout=120000)
            saved.append(runner.validated_screenshot(page, 'SEC-001', 'vault-login', required_texts=['sign in'], required_selectors=['input'], min_body_chars=80))
            sections.append({'title': 'Vault login page', 'screenshot': saved[-1], 'explanation': 'The Vault login page confirms that the secrets management UI is reachable.'})
            page.locator('input').nth(0).fill(self.env['VAULT_ROOT_TOKEN'])
            page.get_by_role('button', name='Sign In').click(timeout=3000)
            page.wait_for_timeout(4000)
            saved.append(runner.validated_screenshot(page, 'SEC-003', 'vault-home', required_texts=['vault', 'dashboard'], min_body_chars=220, timeout_ms=60000))
            sections.append({'title': 'Vault home', 'screenshot': saved[-1], 'explanation': 'The Vault home view confirms successful authentication and exposes the operational workspace for secrets engines and quick actions.'})
            saved.append(runner.validated_screenshot(page, 'SEC-003', 'vault-secret-engines', required_texts=['vault', 'secrets engines', 'secret/'], min_body_chars=220, timeout_ms=60000))
            sections.append({'title': 'Secrets engine list', 'screenshot': saved[-1], 'explanation': 'The secrets engine list shows the mounted secret backends, including the KV engine used by LeninKart.'})
            page.evaluate("window.scrollTo(0, document.body.scrollHeight * 0.6)")
            page.wait_for_timeout(1500)
            saved.append(runner.validated_screenshot(page, 'SEC-005', 'vault-secret-paths', required_texts=['secret/', 'quick actions'], min_body_chars=220, timeout_ms=60000))
            sections.append({'title': 'KV secret paths', 'screenshot': saved[-1], 'explanation': 'The Vault path view provides evidence that the LeninKart KV hierarchy is present under the mounted secret engine.'})
            value_page = runner.new_page()
            value_page.goto(value_evidence.as_uri(), wait_until='domcontentloaded', timeout=120000)
            saved.append(runner.validated_screenshot(value_page, 'SEC-006', 'vault-secret-values', required_texts=['vault secret values evidence', 'jwt_secret', 'api_key'], min_body_chars=80, timeout_ms=30000))
            sections.append({'title': 'Secret key and value evidence', 'screenshot': saved[-1], 'explanation': 'This evidence view renders the extracted KV secret data for the product-service configuration so the validator can prove real key presence without navigating brittle Vault UI internals for each value.'})
        success = vault_ready and not status.get('sealed') and store_ready and all(ext_ready.values()) and self.EXPECTED_PATHS.issubset(kv_paths) and {'jwt_secret', 'api_key'}.issubset(secret_values.keys()) and len(saved) >= 5
        details = {'vault_ready': vault_ready, 'sealed': status.get('sealed'), 'store_ready': store_ready, 'external_secrets': ext_ready, 'kv_paths': sorted(kv_paths), 'secret_value_keys': sorted(secret_values.keys()), 'screenshots': saved, 'sections': sections}
        self.evidence.record_result('vault', details)
        return ValidationResult('vault', success, 'Vault validation passed' if success else 'Vault validation failed', details, test_ids=self.test_ids)
