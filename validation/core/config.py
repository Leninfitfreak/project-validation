from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml
from dotenv import dotenv_values


@dataclass
class ValidationConfig:
    root: Path
    env: dict[str, str]
    settings: dict[str, Any]
    users: dict[str, Any]
    products: dict[str, Any]
    screenshot_targets: dict[str, Any]

    @property
    def docs_dir(self) -> Path:
        return self.root / self.settings["defaults"]["paths"]["docs"]

    @property
    def artifacts_dir(self) -> Path:
        return self.root / self.settings["defaults"]["paths"]["artifacts"]

    @property
    def validation_output_dir(self) -> Path:
        return self.root / self.settings["defaults"]["paths"]["validation_output"]

    def screenshot_dir(self, category: str) -> Path:
        relative = self.settings["defaults"]["paths"]["screenshots"][category]
        return self.root / relative


def load_config(root: Path) -> ValidationConfig:
    env = {key: value for key, value in dotenv_values(root / '.env').items() if value is not None}
    env.update({key: value for key, value in os.environ.items() if value is not None})
    env.setdefault('DEPLOYMENT_POC_ROOT', str((root.parent / 'deployment-poc').resolve()))
    env.setdefault('LENINKART_INFRA_ROOT', str((root.parent / 'leninkart-infra').resolve()))
    env.setdefault('LENINKART_FRONTEND_ROOT', str((root.parent / 'leninkart-frontend').resolve()))
    env.setdefault('LENINKART_PRODUCT_SERVICE_ROOT', str((root.parent / 'leninkart-product-service').resolve()))
    env.setdefault('LENINKART_ORDER_SERVICE_ROOT', str((root.parent / 'leninkart-order-service').resolve()))
    env.setdefault('DEPLOYMENT_POC_REPO', 'Leninfitfreak/deployment-poc')
    env.setdefault('DEPLOYMENT_POC_BRANCH', 'main')
    env.setdefault('DEPLOYMENT_POC_GITOPS_REPO', 'Leninfitfreak/leninkart-infra')
    env.setdefault('DEPLOYMENT_POC_GITOPS_BRANCH', 'dev')
    env.setdefault('DEPLOYMENT_POC_WORKFLOW_FILE', 'deploy-from-jira.yml')
    env.setdefault('DEPLOYMENT_POC_TICKET', '')
    env.setdefault('DEPLOYMENT_POC_ARGOCD_APP', '')
    env.setdefault('DEPLOYMENT_POC_VALUES_PATH', '')
    env.setdefault('DEPLOYMENT_POC_RUNNER_NAME', 'leninkart-runner')
    env.setdefault('LATEST_TAG_EXPECTED_SERVICE', '')
    env.setdefault('LATEST_TAG_EXPECTED_VALUE', '')
    env.setdefault('VALIDATION_TARGET_APP', 'product-service')
    env.setdefault('VALIDATION_TARGET_ENV', 'dev')
    env.setdefault('VALIDATION_REQUESTED_VERSION', 'latest-dev')
    env.setdefault('VALIDATION_TRIGGER_SERVICE_CI', 'true')
    env.setdefault('VALIDATION_TRIGGER_DEPLOYMENT', 'true')
    env.setdefault('JIRA_VALIDATION_PROJECT_KEY', 'SCRUM')
    env.setdefault('JIRA_UI_PROOF_ENABLED', 'false')
    env.setdefault('INGRESS_URL', 'http://127.0.0.1/')
    env.setdefault('ARGOCD_URL', 'http://127.0.0.1:8085')
    env.setdefault('VAULT_URL', 'http://127.0.0.1:8205')
    env.setdefault('GRAFANA_URL', 'http://127.0.0.1:3000')
    env.setdefault('PROMETHEUS_URL', 'http://127.0.0.1:9090')
    env.setdefault('LOKI_URL', 'http://127.0.0.1:3100')
    env.setdefault('TEMPO_URL', 'http://127.0.0.1:3200')
    settings = yaml.safe_load((root / 'validation' / 'data' / 'validation_config.yaml').read_text(encoding='utf-8'))
    users = json.loads((root / 'validation' / 'data' / 'test_users.json').read_text(encoding='utf-8'))
    products = json.loads((root / 'validation' / 'data' / 'test_products.json').read_text(encoding='utf-8'))
    screenshot_targets = json.loads((root / 'validation' / 'data' / 'screenshot_targets.json').read_text(encoding='utf-8'))
    return ValidationConfig(
        root=root,
        env=env,
        settings=settings,
        users=users,
        products=products,
        screenshot_targets=screenshot_targets,
    )
