from __future__ import annotations

from pathlib import Path

from validator_engine.validators import ValidationResult


class FrontendTests:
    def __init__(self, root: Path, env: dict, model: dict, evidence, catalog) -> None:
        self.root = root
        self.env = env
        self.model = model
        self.evidence = evidence
        self.test_ids = catalog.require('FE-001', 'FE-002', 'FE-004', 'FE-008', 'FE-009', 'FE-010', 'UI-001', 'UI-006')

    def repair(self) -> list[str]:
        return []

    def run(self, context: dict) -> ValidationResult:
        traffic = context.get('traffic', {})
        screenshots = traffic.get('screenshots', [])
        success = (
            bool(traffic.get('token'))
            and len(screenshots) >= 5
            and traffic.get('product_visible')
            and traffic.get('order_ledger_visible')
            and traffic.get('orders_requested', 0) >= 1
            and not traffic.get('error')
        )
        details = {
            'user_email': traffic.get('user_email'),
            'product_name': traffic.get('product_name'),
            'product_visible': traffic.get('product_visible'),
            'order_ledger_visible': traffic.get('order_ledger_visible'),
            'screenshots': screenshots,
            'timings': traffic.get('timings', {}),
            'orders_requested': traffic.get('orders_requested'),
        }
        self.evidence.record_result('frontend', details)
        return ValidationResult('frontend', success, 'Frontend workflow validation passed' if success else 'Frontend workflow validation failed', details, test_ids=self.test_ids)
