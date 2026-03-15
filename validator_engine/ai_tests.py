from __future__ import annotations

from pathlib import Path

import requests

from validator_engine.playwright_runner import PlaywrightRunner
from validator_engine.validators import ValidationResult


class AITests:
    def __init__(self, root: Path, env: dict, model: dict, evidence, catalog) -> None:
        self.root = root
        self.env = env
        self.model = model
        self.evidence = evidence
        self.test_ids = catalog.require('AI-001', 'AI-002', 'AI-003', 'AI-004', 'AI-005', 'UI-005')

    def repair(self) -> list[str]:
        return []

    def run(self, context: dict) -> ValidationResult:
        saved = []
        sections = []
        incidents = requests.get(self.env['DEEP_OBSERVER_API_URL'].replace('/health', '/api/incidents'), timeout=30)
        topology = requests.get(self.env['DEEP_OBSERVER_API_URL'].replace('/health', '/api/topology'), timeout=30)
        incident_items = incidents.json() if incidents.ok else []
        first_incident = incident_items[0] if incident_items else {}
        first_incident_id = first_incident.get('incident_id', '')
        first_service = first_incident.get('service', '')
        incident_detail_ok = False
        if first_incident_id:
            detail = requests.get(self.env['DEEP_OBSERVER_API_URL'].replace('/health', f'/api/incidents/{first_incident_id}'), timeout=30)
            incident_detail_ok = detail.status_code == 200
        with PlaywrightRunner(self.root, self.env, self.model, self.evidence) as runner:
            page = runner.new_page()
            page.goto(self.env['DEEP_OBSERVER_URL'].rstrip('/'), wait_until='domcontentloaded', timeout=120000)
            page.wait_for_timeout(10000)
            saved.append(
                runner.validated_screenshot(
                    page,
                    'AI-002',
                    'deep-observer-home',
                    required_texts=['deep observer', 'root cause analysis', 'live telemetry'],
                    min_body_chars=250,
                    timeout_ms=60000,
                )
            )
            sections.append({'title': 'Deep Observer dashboard', 'screenshot': saved[-1], 'explanation': 'The Deep Observer dashboard is the AI observability landing page that correlates metrics, logs, traces, topology, and incidents.'})
            page.evaluate('window.scrollTo(0, 200)')
            page.wait_for_timeout(1500)
            saved.append(
                runner.validated_screenshot(
                    page,
                    'AI-003',
                    'deep-observer-topology',
                    required_texts=['service topology graph', 'incident details panel'],
                    min_body_chars=500,
                    timeout_ms=60000,
                )
            )
            sections.append({'title': 'AI topology graph', 'screenshot': saved[-1], 'explanation': 'The topology graph shows how Deep Observer reconstructs service dependencies from telemetry, including the product-service to Kafka to order-service path.'})
            page.evaluate('window.scrollTo(0, document.body.scrollHeight * 0.45)')
            page.wait_for_timeout(1500)
            saved.append(
                runner.validated_screenshot(
                    page,
                    'AI-004',
                    'deep-observer-incident-panel',
                    required_texts=['reasoning summary', 'root cause service', 'signals detected'],
                    min_body_chars=500,
                    timeout_ms=60000,
                )
            )
            sections.append({'title': 'Incident details panel', 'screenshot': saved[-1], 'explanation': 'The incident details panel exposes the reasoning summary, detected signals, root cause hypothesis, and suggested remediation actions.'})
            if first_incident_id:
                detail_page = runner.new_page()
                detail_page.goto(self.env['DEEP_OBSERVER_URL'].rstrip('/') + f'/incidents/{first_incident_id}', wait_until='domcontentloaded', timeout=120000)
                detail_page.wait_for_timeout(8000)
                saved.append(
                    runner.validated_screenshot(
                        detail_page,
                        'AI-004',
                        'deep-observer-incident-detail',
                        required_texts=['reasoning summary', 'root cause service'],
                        min_body_chars=400,
                        timeout_ms=60000,
                    )
                )
                sections.append({'title': 'Incident detail route', 'screenshot': saved[-1], 'explanation': 'The incident detail route is the drill-down surface for a specific incident and provides durable evidence of the AI reasoning and telemetry context for a selected root cause case.'})
        success = (
            requests.get(self.env['DEEP_OBSERVER_API_URL'], timeout=20).status_code == 200
            and incidents.status_code == 200
            and topology.status_code == 200
            and incident_detail_ok
            and bool(first_service)
            and len(saved) >= 3
        )
        details = {
            'screenshots': saved,
            'sections': sections,
            'incident_count': len(incident_items),
            'topology_status': topology.status_code,
            'first_incident_id': first_incident_id,
            'first_service': first_service,
            'incident_detail_ok': incident_detail_ok,
        }
        self.evidence.record_result('ai', details)
        return ValidationResult('ai', success, 'AI validation passed' if success else 'AI validation failed', details, test_ids=self.test_ids)
