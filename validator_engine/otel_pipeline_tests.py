from __future__ import annotations

import json
import subprocess
from pathlib import Path

from validator_engine.validators import ValidationResult


class OTelPipelineTests:
    def __init__(self, root: Path, env: dict, model: dict, evidence, catalog) -> None:
        self.root = root
        self.env = env
        self.model = model
        self.evidence = evidence
        self.test_ids = catalog.require('OTEL-001', 'OTEL-002', 'OTEL-003', 'OTEL-004', 'OTEL-005')

    def repair(self) -> list[str]:
        return []

    def run(self, context: dict) -> ValidationResult:
        pods = json.loads(subprocess.run(['kubectl', 'get', 'pods', '-n', 'dev', '-o', 'json'], capture_output=True, text=True, check=True).stdout)['items']
        cluster_collector = any('otel-collector' in item['metadata']['name'] and all(cs.get('ready') for cs in item['status'].get('containerStatuses', [])) for item in pods)
        host_collector = subprocess.run(['docker', 'inspect', 'signoz-otel-collector', '--format', '{{.State.Running}}'], capture_output=True, text=True).stdout.strip() == 'true'
        product_docker = Path(r'C:\Projects\Services\leninkart-product-service\Dockerfile').read_text(encoding='utf-8')
        order_docker = Path(r'C:\Projects\Services\leninkart-order-service\Dockerfile').read_text(encoding='utf-8')
        config_ok = all(token in product_docker for token in ['-javaagent:/otel/opentelemetry-javaagent.jar', 'otel.exporter.otlp.endpoint']) and all(token in order_docker for token in ['-javaagent:/otel/opentelemetry-javaagent.jar', 'otel.exporter.otlp.endpoint'])
        details = {'cluster_collector_ready': cluster_collector, 'host_collector_running': host_collector, 'service_dockerfiles_configured_for_otel': config_ok, 'traffic_generated': bool(context.get('traffic', {}).get('token'))}
        success = cluster_collector and host_collector and config_ok and bool(context.get('traffic', {}).get('token'))
        self.evidence.record_result('otel_pipeline', details)
        return ValidationResult('otel_pipeline', success, 'OTEL pipeline validation passed' if success else 'OTEL pipeline validation failed', details, test_ids=self.test_ids)
