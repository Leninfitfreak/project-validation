from __future__ import annotations

import json
import shutil
import site
import sys
from pathlib import Path

usersite = site.getusersitepackages()
if usersite not in sys.path:
    sys.path.append(usersite)

from validator_engine.api_tests import ApiTests
from validator_engine.clickhouse_tests import ClickHouseTests
from validator_engine.database_tests import DatabaseTests
from validator_engine.diagram_generator import DiagramGenerator
from validator_engine.documentation_builder import DocumentationBuilder
from validator_engine.evidence_collector import EvidenceCollector
from validator_engine.frontend_tests import FrontendTests
from validator_engine.gitops_tests import GitOpsTests
from validator_engine.infra_tests import InfraTests
from validator_engine.kafka_tests import KafkaTests
from validator_engine.observability_tests import ObservabilityTests
from validator_engine.otel_pipeline_tests import OTelPipelineTests
from validator_engine.performance_tests import PerformanceTests
from validator_engine.secrets_loader import SecretsLoader
from validator_engine.testcase_loader import TestCaseCatalog
from validator_engine.traffic_generator import TrafficGenerator
from validator_engine.validators import ValidationResult
from validator_engine.vault_tests import VaultTests


class ValidationEngine:
    def __init__(self) -> None:
        self.root = Path(__file__).resolve().parent.parent
        self.artifacts = self.root / 'artifacts'
        self.logs = self.root / 'logs'
        self.docs = self.root / 'docs'
        self.diagrams = self.docs / 'diagrams'
        self.screenshots = self.root / 'screenshots'
        self.validation_output = self.root / 'validation-output'
        for path in (self.artifacts, self.logs, self.docs, self.diagrams, self.screenshots, self.validation_output):
            path.mkdir(parents=True, exist_ok=True)
        self._reset_screenshot_dirs()
        self.env = SecretsLoader(self.root).ensure_env()
        self.evidence = EvidenceCollector(self.root)
        self.model = self.discover_architecture()
        self.catalog = TestCaseCatalog(self.root / 'testcases.md')

    def _reset_screenshot_dirs(self) -> None:
        for base in (self.screenshots, self.docs / 'screenshots', self.validation_output):
            if base.exists():
                shutil.rmtree(base)
            base.mkdir(parents=True, exist_ok=True)

    def discover_architecture(self) -> dict:
        return {
            'repositories': {
                'infra': r'C:\Projects\Services\leninkart-infra',
                'observer_stack': r'C:\Projects\Services\observer-stack',
                'kafka_platform': r'C:\Projects\Services\kafka-platform',
                'frontend': r'C:\Projects\Services\leninkart-frontend',
                'product_service': r'C:\Projects\Services\leninkart-product-service',
                'order_service': r'C:\Projects\Services\leninkart-order-service',
            },
            'services': ['frontend', 'product-service', 'order-service', 'postgres', 'kafka', 'otel-collector', 'observer-stack', 'clickhouse'],
            'kafka_topics': ['product-orders', 'product-events', 'order-events', 'order-created'],
            'testcases_path': str(self.root / 'testcases.md'),
            'port_forwards': {
                'argocd': ('argocd', 'svc/argocd-server', '8085:80'),
                'vault': ('vault', 'svc/vault-ui', '8205:8200'),
            },
        }

    def _modules(self):
        return [
            InfraTests(self.root, self.env, self.model, self.evidence, self.catalog),
            GitOpsTests(self.root, self.env, self.model, self.evidence, self.catalog),
            VaultTests(self.root, self.env, self.model, self.evidence, self.catalog),
            KafkaTests(self.root, self.env, self.model, self.evidence, self.catalog),
            FrontendTests(self.root, self.env, self.model, self.evidence, self.catalog),
            ApiTests(self.root, self.env, self.model, self.evidence, self.catalog),
            DatabaseTests(self.root, self.env, self.model, self.evidence, self.catalog),
            OTelPipelineTests(self.root, self.env, self.model, self.evidence, self.catalog),
            ClickHouseTests(self.root, self.env, self.model, self.evidence, self.catalog),
            ObservabilityTests(self.root, self.env, self.model, self.evidence, self.catalog),
            PerformanceTests(self.root, self.env, self.model, self.evidence, self.catalog),
        ]

    def _run_module(self, module, context: dict) -> ValidationResult:
        try:
            return module.run(context)
        except Exception as exc:
            details = {'error': str(exc), 'module': module.__class__.__name__}
            self.evidence.record_result(module.__class__.__name__, details)
            return ValidationResult(module.__class__.__name__, False, f'{module.__class__.__name__} raised an exception', details, test_ids=getattr(module, 'test_ids', []))

    def _export_validation_output(self, docs: list[str], screenshots: list[str]) -> None:
        folders = {
            'frontend': {'FE-'},
            'observability': {'OBS-', 'KTEL-', 'AI-'},
            'vault': {'SEC-'},
            'argocd': {'GIT-'},
            'reports': set(),
        }
        for folder in folders:
            (self.validation_output / folder).mkdir(parents=True, exist_ok=True)
        for name in screenshots:
            source = self.screenshots / name
            target_folder = 'observability'
            for folder, prefixes in folders.items():
                if prefixes and any(name.startswith(prefix) for prefix in prefixes):
                    target_folder = folder
                    break
            shutil.copy2(source, self.validation_output / target_folder / name)
        for doc_name in docs:
            source = self.docs / doc_name
            if source.exists():
                shutil.copy2(source, self.validation_output / 'reports' / doc_name)
        evidence_json = self.artifacts / 'evidence.json'
        if evidence_json.exists():
            shutil.copy2(evidence_json, self.validation_output / 'reports' / 'evidence.json')

    def run(self) -> int:
        context: dict = {}
        traffic_generator = TrafficGenerator(self.root, self.env, self.model, self.evidence)
        final_results: list[dict] = []
        stable = False
        modules = self._modules()
        for cycle in range(1, 4):
            cycle_results = []
            for module in modules[:4]:
                for repair in module.repair():
                    self.evidence.add_repair(repair)
                cycle_results.append(self._run_module(module, context).to_dict())
            try:
                context['traffic'] = traffic_generator.run()
            except Exception as exc:
                context['traffic'] = {'error': str(exc), 'screenshots': [], 'timings': {}}
            for module in modules[4:]:
                for repair in module.repair():
                    self.evidence.add_repair(repair)
                cycle_results.append(self._run_module(module, context).to_dict())
            final_results = cycle_results
            if all(item['success'] for item in cycle_results):
                stable = True
                break
        docs_screenshots = self.docs / 'screenshots'
        docs_screenshots.mkdir(exist_ok=True)
        screenshots = [str(path.relative_to(self.screenshots)).replace('\\', '/') for path in self.screenshots.rglob('*.png')]
        for name in screenshots:
            source = self.screenshots / name
            target = docs_screenshots / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
        diagrams = DiagramGenerator(self.docs, self.diagrams).generate(self.model)
        docs = DocumentationBuilder(self.docs).build(self.model, self.evidence, final_results, diagrams, screenshots)
        self._export_validation_output(docs, screenshots)
        mkdocs_build = self._build_mkdocs()
        payload = {
            'architecture': self.model,
            'results': final_results,
            'stable': stable,
            'mkdocs_build': mkdocs_build,
            'screenshots': screenshots,
            'docs': docs,
            'evidence': self.evidence.records,
        }
        (self.artifacts / 'validation-results.json').write_text(json.dumps(payload, indent=2), encoding='utf-8')
        return 0 if stable and mkdocs_build['ok'] else 1

    def _build_mkdocs(self) -> dict:
        import subprocess
        result = subprocess.run([sys.executable, '-m', 'mkdocs', 'build'], cwd=self.root, capture_output=True, text=True)
        return {'ok': result.returncode == 0, 'stdout': result.stdout, 'stderr': result.stderr}


def main() -> int:
    return ValidationEngine().run()
