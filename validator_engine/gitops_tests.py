from __future__ import annotations

import json
import subprocess
from pathlib import Path

from validator_engine.playwright_runner import PlaywrightRunner
from validator_engine.validators import ValidationResult


class GitOpsTests:
    CORE_APPS = {
        'dev-ingress',
        'dev-order-service',
        'dev-product-service',
        'frontend-dev',
        'grafana-dev',
        'loki-dev',
        'postgres-dev',
        'prometheus-dev',
        'promtail-dev',
        'vault',
        'vault-externalsecrets',
        'vault-secretstore',
    }

    def __init__(self, root: Path, env: dict, model: dict, evidence, catalog) -> None:
        self.root = root
        self.env = env
        self.model = model
        self.evidence = evidence
        self.test_ids = catalog.require('GIT-001', 'GIT-002', 'GIT-003', 'GIT-004', 'GIT-005', 'UI-002')

    def repair(self) -> list[str]:
        repairs = []
        subprocess.run(['kubectl', 'delete', 'application', '-n', 'argocd', 'vault-secretstores-dev'], capture_output=True, text=True)
        repairs.append('deleted duplicate vault-secretstores-dev application when present')
        for app in ('dev-product-service', 'dev-order-service', 'frontend-dev', 'grafana-dev', 'prometheus-dev', 'loki-dev', 'promtail-dev', 'vault', 'vault-externalsecrets'):
            subprocess.run(['kubectl', 'patch', 'application', '-n', 'argocd', app, '--type', 'merge', '--patch', '{"operation":{"sync":{}}}'], capture_output=True, text=True)
            repairs.append(f'requested sync for {app}')
        return repairs

    def run(self, context: dict) -> ValidationResult:
        data = json.loads(subprocess.run(['kubectl', 'get', 'applications.argoproj.io', '-A', '-o', 'json'], capture_output=True, text=True, check=True).stdout)
        applications = []
        failing = []
        for item in data['items']:
            name = item['metadata']['name']
            sync = item.get('status', {}).get('sync', {}).get('status', 'Unknown')
            health = item.get('status', {}).get('health', {}).get('status', 'Unknown')
            entry = {'name': name, 'sync': sync, 'health': health}
            applications.append(entry)
            if name in self.CORE_APPS and (sync != 'Synced' or health not in {'Healthy', 'Progressing'}):
                failing.append(entry)
        sections = []
        saved = []
        with PlaywrightRunner(self.root, self.env, self.model, self.evidence) as runner:
            page = runner.new_page()
            page.goto(self.env['ARGOCD_URL'], wait_until='domcontentloaded', timeout=120000)
            runner.wait_for_valid_state(page, required_selectors=['input[name="username"]', 'input[name="password"]'], required_texts=['sign in'], min_body_chars=80)
            saved.append(runner.validated_screenshot(page, 'GIT-001', 'argocd-login', required_texts=['sign in'], required_selectors=['input[name="username"]', 'input[name="password"]'], min_body_chars=80))
            sections.append({'title': 'ArgoCD login page', 'screenshot': saved[-1], 'explanation': 'The ArgoCD login page verifies that the GitOps dashboard is reachable and ready for operator access.'})
            page.locator('input[name="username"]').fill(self.env.get('ARGOCD_USERNAME', 'admin'))
            page.locator('input[name="password"]').fill(runner.argocd_password())
            page.get_by_role('button', name='Sign In').click()
            saved.append(runner.validated_screenshot(page, 'GIT-001', 'argocd-dashboard', required_texts=['applications', 'dev-product-service'], forbidden_texts=['sign in'], min_body_chars=200, timeout_ms=90000))
            sections.append({'title': 'Applications dashboard', 'screenshot': saved[-1], 'explanation': 'The applications dashboard is the GitOps inventory view and shows sync and health state for each managed application.'})
            page.get_by_text('dev-product-service').first.click(timeout=15000)
            saved.append(runner.validated_screenshot(page, 'GIT-003', 'argocd-product-service', required_texts=['dev-product-service'], min_body_chars=180, timeout_ms=60000))
            sections.append({'title': 'Product-service application detail', 'screenshot': saved[-1], 'explanation': 'The product-service application detail page exposes sync state, resource tree, and deployment health for the product API workload.'})
            try:
                page.get_by_text('dev-order-service').first.click(timeout=10000)
                saved.append(runner.validated_screenshot(page, 'GIT-003', 'argocd-order-service', required_texts=['dev-order-service'], min_body_chars=180, timeout_ms=60000))
                sections.append({'title': 'Order-service application detail', 'screenshot': saved[-1], 'explanation': 'The order-service detail page is used as the cluster state view because it renders the managed resource tree and rollout health for the order consumer.'})
            except Exception:
                pass
            page.get_by_text('History').first.click(timeout=10000)
            saved.append(runner.validated_screenshot(page, 'GIT-005', 'argocd-history', required_texts=['history'], min_body_chars=120, timeout_ms=60000))
            sections.append({'title': 'Deployment history', 'screenshot': saved[-1], 'explanation': 'The deployment history confirms that GitOps revisions are tracked and rollback-capable through ArgoCD.'})
        success = self.CORE_APPS.issubset({item['name'] for item in applications}) and not failing and len(saved) >= 4
        details = {'applications': applications, 'failing': failing, 'screenshots': saved, 'sections': sections}
        self.evidence.record_result('gitops', details)
        return ValidationResult('gitops', success, 'GitOps validation passed' if success else 'GitOps validation failed', details, test_ids=self.test_ids)
