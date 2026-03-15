from __future__ import annotations

from pathlib import Path

import requests

from validator_engine.playwright_runner import PlaywrightRunner
from validator_engine.validators import ValidationResult


class ObservabilityTests:
    SECTIONS = [
        {
            'test_id': 'OBS-001', 'slug': 'observer-home', 'path': '/home', 'title': 'Observer Stack home dashboard',
            'required_texts': ['observer stack', 'dashboards'], 'min_body_chars': 250,
            'data_terms': ['services', 'alerts', 'dashboards'], 'required_data': False, 'critical': True,
            'explanation': 'The home dashboard is the landing surface for the observability workspace and confirms that the main telemetry navigation is available to the operator.',
        },
        {
            'test_id': 'OBS-004', 'slug': 'observer-services', 'path': '/services', 'title': 'Services overview',
            'required_texts': ['services'], 'min_body_chars': 250,
            'data_terms': ['product-service', 'order-service'], 'required_data': True, 'critical': True,
            'explanation': 'The services overview shows discovered application services and their top-level health signals such as throughput, latency, and error context.',
        },
        {
            'test_id': 'OBS-004', 'slug': 'observer-product-service', 'path': '/services', 'click_text': 'product-service', 'title': 'Product service metrics page',
            'required_texts': ['latency'], 'min_body_chars': 220,
            'data_terms': ['throughput', 'error', 'latency'], 'required_data': True, 'critical': True,
            'explanation': 'The product-service detail page exposes service-specific latency, throughput, and error panels for the product and auth workflow.',
        },
        {
            'test_id': 'OBS-004', 'slug': 'observer-order-service', 'path': '/services', 'click_text': 'order-service', 'title': 'Order service metrics page',
            'required_texts': ['latency'], 'min_body_chars': 220,
            'data_terms': ['throughput', 'error', 'latency'], 'required_data': True, 'critical': True,
            'explanation': 'The order-service detail page validates that downstream Kafka consumption and PostgreSQL-backed order reads are represented in the service view.',
        },
        {
            'test_id': 'OBS-007', 'slug': 'observer-dashboard-list', 'path': '/dashboard', 'title': 'Dashboard inventory',
            'required_texts': ['dashboard'], 'min_body_chars': 180,
            'data_terms': ['leninkart', 'dashboard'], 'required_data': False, 'critical': False,
            'explanation': 'The dashboard inventory shows the available curated observability boards, including the LeninKart-specific dashboard set.',
        },
        {
            'test_id': 'OBS-007', 'slug': 'observer-dashboard-detail', 'path': '/dashboard', 'dashboard_click': True, 'title': 'LeninKart dashboard detail',
            'required_texts': ['dashboard'], 'min_body_chars': 220,
            'data_terms': ['kafka throughput', 'database wait time'], 'required_data': True, 'critical': True,
            'explanation': 'The LeninKart dashboard detail correlates application latency, database wait, and Kafka throughput in one operational view.',
        },
        {
            'test_id': 'OBS-005', 'slug': 'observer-traces', 'path': '/traces-explorer', 'title': 'Traces explorer',
            'required_texts': ['trace'], 'min_body_chars': 250,
            'data_terms': ['product-service', 'order-service'], 'required_data': True, 'critical': True,
            'explanation': 'The traces explorer confirms distributed request traces from the frontend-driven product and order flow are ingested and queryable.',
        },
        {
            'test_id': 'OBS-006', 'slug': 'observer-logs', 'path': '/logs/logs-explorer', 'title': 'Logs explorer',
            'required_texts': ['logs'], 'min_body_chars': 250,
            'data_terms': ['product-service', 'order-service'], 'required_data': True, 'critical': True,
            'explanation': 'The logs explorer validates that application logs from the Spring services are visible in the observability stack and can be correlated with traces.',
        },
        {
            'test_id': 'KTEL-004', 'slug': 'observer-messaging-overview', 'path': '/messaging-queues/overview', 'title': 'Messaging queues overview',
            'required_texts': ['messaging'], 'min_body_chars': 180,
            'data_terms': ['kafka', 'product-orders'], 'required_data': True, 'critical': True,
            'explanation': 'The messaging overview shows queue-level telemetry derived from Kafka spans and broker metrics for the application event pipeline.',
        },
        {
            'test_id': 'KTEL-004', 'slug': 'observer-kafka-detail', 'path': '/messaging-queues/kafka', 'title': 'Kafka telemetry detail',
            'required_texts': ['kafka'], 'min_body_chars': 180,
            'data_terms': ['product-orders', 'throughput', 'messages'], 'required_data': False, 'critical': False,
            'explanation': 'The Kafka detail page focuses specifically on topic-level telemetry and verifies that the product-orders topic is visible from the observability UI.',
        },
        {
            'test_id': 'OBS-004', 'slug': 'observer-service-map', 'path': '/service-map', 'title': 'Service dependency map',
            'required_texts': ['service map'], 'min_body_chars': 180,
            'data_terms': ['product-service', 'order-service', 'kafka'], 'required_data': False, 'critical': False,
            'explanation': 'The service map visualizes inter-service dependencies, including the Kafka edge between product-service and order-service.',
        },
        {
            'test_id': 'OBS-007', 'slug': 'observer-infra-hosts', 'path': '/infrastructure-monitoring/hosts', 'title': 'Infrastructure hosts monitoring',
            'required_texts': ['hosts'], 'min_body_chars': 120,
            'data_terms': ['host', 'cpu', 'memory'], 'required_data': False, 'critical': False,
            'explanation': 'The hosts view represents infrastructure-level metrics for the monitored environment.',
        },
        {
            'test_id': 'OBS-007', 'slug': 'observer-infra-kubernetes', 'path': '/infrastructure-monitoring/kubernetes', 'title': 'Kubernetes infrastructure monitoring',
            'required_texts': ['kubernetes'], 'min_body_chars': 120,
            'data_terms': ['node', 'pod', 'cluster'], 'required_data': False, 'critical': False,
            'explanation': 'The Kubernetes infrastructure view shows cluster-level telemetry such as node and pod health surfaces.',
        },
        {
            'test_id': 'OBS-009', 'slug': 'observer-exceptions', 'path': '/exceptions', 'title': 'Exception tracking',
            'required_texts': ['exception'], 'min_body_chars': 100,
            'data_terms': ['exception', 'error'], 'required_data': False, 'critical': False,
            'explanation': 'The exceptions section is used to inspect aggregated application exceptions when exception telemetry is available.',
        },
        {
            'test_id': 'OBS-009', 'slug': 'observer-api-monitoring', 'path': '/api-monitoring/explorer', 'title': 'External API monitoring',
            'required_texts': ['api monitoring'], 'min_body_chars': 100,
            'data_terms': ['latency', 'request'], 'required_data': False, 'critical': False,
            'explanation': 'The API monitoring explorer is intended for upstream and downstream API observation when external API traffic is instrumented.',
        },
        {
            'test_id': 'OBS-009', 'slug': 'observer-usage-explorer', 'path': '/usage-explorer', 'title': 'Telemetry cost and usage analytics',
            'required_texts': ['usage'], 'min_body_chars': 100,
            'data_terms': ['usage', 'ingested', 'cost'], 'required_data': False, 'critical': False,
            'explanation': 'The usage explorer provides telemetry volume and cost analytics for the observability platform itself.',
        },
        {
            'test_id': 'OBS-009', 'slug': 'observer-alerts', 'path': '/alerts/overview', 'title': 'Alerts overview',
            'required_texts': ['alert'], 'min_body_chars': 160,
            'data_terms': ['triggered alerts', 'alert rules', 'configuration'], 'required_data': False, 'critical': False,
            'explanation': 'The alerts overview confirms that the alerting subsystem is available and exposes rules, triggered alerts, and configuration surfaces.',
        },
        {
            'test_id': 'OBS-011', 'slug': 'observer-ai-observer', 'path': '/ai-observer', 'title': 'Embedded AI Observer dashboard',
            'required_texts': ['ai observer'], 'min_body_chars': 180,
            'data_terms': ['root cause', 'topology', 'incident'], 'required_data': True, 'critical': True,
            'explanation': 'The embedded AI Observer route connects the core observability workspace to the Deep Observer analysis experience.',
        },
    ]

    def __init__(self, root: Path, env: dict, model: dict, evidence, catalog) -> None:
        self.root = root
        self.env = env
        self.model = model
        self.evidence = evidence
        self.test_ids = catalog.require('OBS-001', 'OBS-004', 'OBS-005', 'OBS-006', 'OBS-007', 'OBS-008', 'OBS-009', 'OBS-011', 'KTEL-001', 'KTEL-004', 'UI-004')

    def repair(self) -> list[str]:
        return []

    def _login(self, runner: PlaywrightRunner):
        page = runner.new_page()
        page.goto(self.env['OBSERVER_STACK_URL'].rstrip('/'), wait_until='domcontentloaded', timeout=120000)
        runner.wait_for_valid_state(page, required_selectors=['input[type="email"]'], required_texts=['sign in'], min_body_chars=80)
        page.locator('input[type="email"]').fill(self.env['OBSERVER_STACK_USER'])
        password_locator = page.locator('input[type="password"]')
        if password_locator.count() == 0 or not password_locator.first.is_visible():
            try:
                page.get_by_role('button', name='Next').click(timeout=10000)
            except Exception:
                page.get_by_role('button', name='Continue').click(timeout=10000)
            password_locator.first.wait_for(state='visible', timeout=15000)
        password_locator.first.fill(self.env['OBSERVER_STACK_PASSWORD'])
        try:
            page.get_by_role('button', name='Sign in with Password').click(timeout=15000)
        except Exception:
            page.get_by_role('button', name='Sign In').click(timeout=15000)
        page.wait_for_timeout(8000)
        return page

    def _capture_section(self, runner: PlaywrightRunner, page, spec: dict) -> dict:
        path = spec['path']
        url = self.env['OBSERVER_STACK_URL'].rstrip('/') + path
        last_error = ''
        for _ in range(3):
            try:
                page.goto(url, wait_until='domcontentloaded', timeout=120000)
                page.wait_for_timeout(7000)
                if spec.get('click_text'):
                    page.get_by_text(spec['click_text'], exact=False).first.click(timeout=10000)
                    page.wait_for_timeout(5000)
                if spec.get('dashboard_click'):
                    try:
                        page.get_by_text('LeninKart', exact=False).first.click(timeout=5000)
                        page.wait_for_timeout(5000)
                    except Exception:
                        links = page.locator('a[href*="/dashboard/"]')
                        if links.count() > 0:
                            links.first.click(timeout=5000)
                            page.wait_for_timeout(5000)
                runner.wait_for_valid_state(page, required_texts=spec.get('required_texts'), min_body_chars=spec.get('min_body_chars', 150), timeout_ms=90000)
                body = runner._body_text(page).lower()
                data_terms = [term.lower() for term in spec.get('data_terms', [])]
                data_present = not data_terms or any(term in body for term in data_terms)
                if spec.get('required_data') and not data_present:
                    last_error = f"required data not present for {spec['title']}"
                    page.wait_for_timeout(5000)
                    continue
                file_name = runner.screenshot(page, spec['test_id'], spec['slug'])
                return {
                    'title': spec['title'],
                    'path': path,
                    'url': page.url,
                    'screenshot': file_name,
                    'explanation': spec['explanation'],
                    'data_present': data_present,
                    'required_data': spec.get('required_data', False),
                    'critical': spec.get('critical', False),
                    'matched_terms': [term for term in spec.get('data_terms', []) if term.lower() in body],
                    'status': 'ok',
                }
            except Exception as exc:
                last_error = str(exc)
                page.wait_for_timeout(3000)
        if spec.get('critical'):
            raise RuntimeError(f"Failed to capture {spec['title']}: {last_error}")
        return {
            'title': spec['title'],
            'path': path,
            'url': url,
            'screenshot': '',
            'explanation': spec['explanation'],
            'data_present': False,
            'required_data': spec.get('required_data', False),
            'critical': spec.get('critical', False),
            'matched_terms': [],
            'status': f'not-captured: {last_error}',
        }

    def run(self, context: dict) -> ValidationResult:
        saved = []
        sections = []
        traffic = context.get('traffic', {})
        with PlaywrightRunner(self.root, self.env, self.model, self.evidence) as runner:
            page = self._login(runner)
            for spec in self.SECTIONS:
                section = self._capture_section(runner, page, spec)
                sections.append(section)
                if section.get('screenshot'):
                    saved.append(section['screenshot'])
            detected_services = {
                'frontend': runner.observer_service_present('frontend'),
                'product-service': runner.observer_service_present('product-service'),
                'order-service': runner.observer_service_present('order-service'),
            }
        services_ok = requests.get(self.env['OBSERVER_STACK_URL'] + '/api/v1/health', timeout=20).status_code == 200
        kafka_metrics_raw = requests.get('http://127.0.0.1:7071/metrics', timeout=20).text
        kafka_metrics = 'product-orders' in kafka_metrics_raw and 'kafka_server_brokertopicmetrics_messagesinpersec_count_total' in kafka_metrics_raw
        topology_nodes = []
        topology_resp = requests.get(self.env['DEEP_OBSERVER_API_URL'].replace('/health', '/api/topology'), timeout=30)
        if topology_resp.ok:
            topology_json = topology_resp.json()
            topology_nodes = [node.get('label') or node.get('id') for node in topology_json.get('nodes', [])]
        fallback_detected = {
            'frontend': detected_services['frontend'] or 'frontend' in topology_nodes,
            'product-service': detected_services['product-service'] or 'product-service' in topology_nodes,
            'order-service': detected_services['order-service'] or 'order-service' in topology_nodes,
        }
        required_detected = fallback_detected['product-service'] and fallback_detected['order-service']
        critical_sections = [section for section in sections if section['critical']]
        critical_ok = all(section['status'] == 'ok' for section in critical_sections)
        success = services_ok and kafka_metrics and required_detected and critical_ok and len(saved) >= 10 and bool(traffic.get('orders_requested', 0) >= 20)
        details = {
            'screenshots': saved,
            'sections': sections,
            'observer_health': services_ok,
            'kafka_metrics': kafka_metrics,
            'detected_services': detected_services,
            'fallback_detected_services': fallback_detected,
            'topology_nodes': topology_nodes,
            'frontend_service_detected': fallback_detected['frontend'],
            'required_service_detection_ok': required_detected,
            'critical_sections_ok': critical_ok,
        }
        self.evidence.record_result('observability', details)
        return ValidationResult('observability', success, 'Observability validation passed' if success else 'Observability validation failed', details, test_ids=self.test_ids)


