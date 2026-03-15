from __future__ import annotations

from pathlib import Path

from validator_engine.playwright_runner import PlaywrightRunner
from validator_engine.validators import ValidationResult


class PerformanceTests:
    THRESHOLDS = {
        'auth_page_seconds': 12,
        'dashboard_seconds': 15,
        'product_create_seconds': 15,
        'order_ledger_seconds': 180,
    }

    def __init__(self, root: Path, env: dict, model: dict, evidence, catalog) -> None:
        self.root = root
        self.env = env
        self.model = model
        self.evidence = evidence
        self.test_ids = catalog.require('PERF-001', 'PERF-002', 'PERF-003', 'PERF-004')

    def repair(self) -> list[str]:
        return []

    def run(self, context: dict) -> ValidationResult:
        timings = context.get('traffic', {}).get('timings', {})
        failures = {key: value for key, value in timings.items() if value > self.THRESHOLDS.get(key, 999)}
        details = {'timings': timings, 'thresholds': self.THRESHOLDS, 'failures': failures}
        self.evidence.record_result('performance', details)
        return ValidationResult('performance', not failures and bool(timings), 'Performance validation passed' if not failures and timings else 'Performance validation failed', details, test_ids=self.test_ids)
