from __future__ import annotations

import time
from pathlib import Path

import requests

from validator_engine.playwright_runner import PlaywrightRunner
from validator_engine.validators import ValidationResult


class ObservabilityTests:
    REQUIRED_DASHBOARDS = [
        'LeninKart Platform Overview',
        'LeninKart Product Service Overview',
        'LeninKart Order Service Overview',
        'LeninKart Logs Overview',
        'LeninKart Kafka Overview',
    ]

    def __init__(self, root: Path, env: dict, model: dict, evidence, catalog) -> None:
        self.root = root
        self.env = env
        self.model = model
        self.evidence = evidence
        self.test_ids = catalog.require('OBS-001', 'OBS-004', 'OBS-006', 'OBS-007', 'OBS-009', 'UI-004')

    def repair(self) -> list[str]:
        return []

    def _grafana_auth(self) -> tuple[str, str]:
        return self.env.get('GRAFANA_USERNAME', 'admin'), self.env.get('GRAFANA_PASSWORD', '')

    def _grafana_get(self, path: str) -> requests.Response:
        user, password = self._grafana_auth()
        return requests.get(
            self.env['GRAFANA_URL'].rstrip('/') + path,
            auth=(user, password),
            timeout=30,
        )

    def _dashboard_inventory(self) -> list[dict]:
        response = self._grafana_get('/api/search?type=dash-db&query=LeninKart')
        response.raise_for_status()
        return response.json()

    def _query_loki(self, query: str) -> dict:
        end_ns = time.time_ns()
        start_ns = end_ns - (10 * 60 * 1_000_000_000)
        response = requests.get(
            self.env['LOKI_URL'].rstrip('/') + '/loki/api/v1/query_range',
            params={
                'query': query,
                'limit': 10,
                'start': str(start_ns),
                'end': str(end_ns),
                'direction': 'backward',
            },
            timeout=30,
        )
        response.raise_for_status()
        return response.json()

    def _login_grafana(self, runner: PlaywrightRunner):
        page = runner.new_page()
        self._goto(page, self.env['GRAFANA_URL'].rstrip('/') + '/login')
        runner.wait_for_valid_state(
            page,
            required_texts=['grafana'],
            required_selectors=['input[name="user"]', 'input[name="password"]'],
            min_body_chars=100,
            timeout_ms=90000,
        )
        runner.screenshot(page, 'OBS-001', 'grafana-login')
        page.locator('input[name="user"]').fill(self.env.get('GRAFANA_USERNAME', 'admin'))
        page.locator('input[name="password"]').fill(self.env.get('GRAFANA_PASSWORD', ''))
        page.get_by_role('button', name='Log in').click()
        runner.wait_for_valid_state(
            page,
            required_texts=['home', 'dashboards'],
            forbidden_texts=['welcome back'],
            min_body_chars=120,
            timeout_ms=90000,
        )
        return page

    def _goto(self, page, url: str) -> None:
        try:
            page.goto(url, wait_until='domcontentloaded', timeout=120000)
        except Exception as exc:
            if 'ERR_ABORTED' not in str(exc):
                raise
            page.wait_for_timeout(3000)

    def _capture_dashboard(self, runner: PlaywrightRunner, page, dashboard: dict, test_id: str, slug: str) -> str:
        self._goto(page, self.env['GRAFANA_URL'].rstrip('/') + dashboard['url'])
        runner.wait_for_valid_state(
            page,
            required_texts=[dashboard['title'].lower()],
            min_body_chars=120,
            timeout_ms=90000,
        )
        return runner.screenshot(page, test_id, slug)

    def run(self, context: dict) -> ValidationResult:
        grafana_health = False
        healthy_jobs: set[str] = set()
        dashboard_map: dict[str, dict] = {}
        missing_dashboards: list[str] = []
        log_streams: list[dict] = []
        screenshots: list[str] = []
        sections: list[dict] = []
        with PlaywrightRunner(self.root, self.env, self.model, self.evidence) as runner:
            grafana_health = requests.get(self.env['GRAFANA_URL'].rstrip('/') + '/api/health', timeout=20).status_code == 200
            prometheus_targets = requests.get(self.env['PROMETHEUS_URL'].rstrip('/') + '/api/v1/targets', timeout=30).json()
            active_targets = prometheus_targets.get('data', {}).get('activeTargets', [])
            healthy_jobs = {
                item['labels'].get('job')
                for item in active_targets
                if item.get('health') == 'up'
            }

            dashboards = self._dashboard_inventory()
            dashboard_map = {item['title']: item for item in dashboards}
            missing_dashboards = [title for title in self.REQUIRED_DASHBOARDS if title not in dashboard_map]

            log_query = self._query_loki('{namespace="dev",service=~"product-service|order-service"}')
            log_streams = log_query.get('data', {}).get('result', [])

            page = self._login_grafana(runner)

            dashboard_list_url = next(iter(dashboard_map.values()), {}).get('folderUrl', '/dashboards')
            self._goto(page, self.env['GRAFANA_URL'].rstrip('/') + dashboard_list_url)
            runner.wait_for_valid_state(page, required_texts=['dashboards'], min_body_chars=120, timeout_ms=90000)
            screenshots.append(runner.screenshot(page, 'OBS-007', 'grafana-dashboard-list'))
            sections.append({
                'title': 'Grafana dashboard inventory',
                'url': page.url,
                'screenshot': screenshots[-1],
                'explanation': 'The dashboard inventory confirms that the curated LeninKart Grafana dashboards are provisioned and operator-visible.',
            })

            for title, test_id, slug, explanation in [
                ('LeninKart Platform Overview', 'OBS-007', 'grafana-platform-overview', 'The platform overview is the primary Grafana showcase board for application health, traffic, and Kafka activity.'),
                ('LeninKart Product Service Overview', 'OBS-007', 'grafana-product-service-overview', 'The product-service overview exposes HTTP and business metrics for auth and product flows.'),
                ('LeninKart Order Service Overview', 'OBS-007', 'grafana-order-service-overview', 'The order-service overview confirms order consumption and retrieval metrics are available in Grafana.'),
                ('LeninKart Logs Overview', 'OBS-006', 'grafana-logs-overview', 'The logs overview demonstrates that Loki-backed application logs are visible through Grafana.'),
            ]:
                dashboard = dashboard_map.get(title)
                if not dashboard:
                    continue
                screenshots.append(self._capture_dashboard(runner, page, dashboard, test_id, slug))
                sections.append({
                    'title': title,
                    'url': self.env['GRAFANA_URL'].rstrip('/') + dashboard['url'],
                    'screenshot': screenshots[-1],
                    'explanation': explanation,
                })

            prom_page = runner.new_page()
            self._goto(prom_page, self.env['PROMETHEUS_URL'].rstrip('/') + '/targets')
            runner.wait_for_valid_state(
                prom_page,
                required_texts=['endpoint', 'product-service', 'order-service', 'kafka-platform'],
                min_body_chars=120,
                timeout_ms=90000,
            )
            screenshots.append(runner.screenshot(prom_page, 'OBS-004', 'prometheus-targets'))
            sections.append({
                'title': 'Prometheus targets',
                'url': prom_page.url,
                'screenshot': screenshots[-1],
                'explanation': 'The Prometheus targets page verifies that product-service, order-service, Kafka, and Prometheus itself are being scraped successfully.',
            })

        required_jobs = {'product-service', 'order-service', 'kafka-platform', 'prometheus'}
        success = (
            grafana_health
            and required_jobs.issubset(healthy_jobs)
            and not missing_dashboards
            and len(log_streams) > 0
            and len(screenshots) >= 5
        )
        details = {
            'grafana_health': grafana_health,
            'healthy_prometheus_jobs': sorted(healthy_jobs),
            'missing_dashboards': missing_dashboards,
            'dashboard_titles': sorted(dashboard_map),
            'log_stream_count': len(log_streams),
            'screenshots': screenshots,
            'sections': sections,
        }
        self.evidence.record_result('observability', details)
        return ValidationResult(
            'observability',
            success,
            'Observability validation passed' if success else 'Observability validation failed',
            details,
            test_ids=self.test_ids,
        )
