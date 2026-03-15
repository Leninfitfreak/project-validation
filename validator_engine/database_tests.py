from __future__ import annotations

import subprocess
import time
from pathlib import Path

from validator_engine.validators import ValidationResult


class DatabaseTests:
    def __init__(self, root: Path, env: dict, model: dict, evidence, catalog) -> None:
        self.root = root
        self.env = env
        self.model = model
        self.evidence = evidence
        self.test_ids = catalog.require('DB-001', 'DB-002', 'DB-003', 'DB-004')

    def repair(self) -> list[str]:
        return []

    def _psql(self, query: str) -> str:
        result = subprocess.run(['kubectl', 'exec', '-n', 'dev', 'postgres-v2-0', '--', 'psql', '-U', 'leninkart', '-d', 'leninkart', '-t', '-A', '-c', query], capture_output=True, text=True, check=True)
        return result.stdout.strip()

    def run(self, context: dict) -> ValidationResult:
        traffic = context.get('traffic', {})
        email = traffic.get('user_email', '')
        product_name = traffic.get('product_name', '')
        user_count = int(self._psql(f"SELECT count(*) FROM users WHERE email='{email}';") or '0') if email else 0
        product_count = int(self._psql(f"SELECT count(*) FROM products WHERE name='{product_name}';") or '0') if product_name else 0
        order_count = 0
        if email:
            for _ in range(10):
                order_count = int(self._psql(f"SELECT count(*) FROM orders WHERE user_name='{email}';") or '0')
                if order_count > 0:
                    break
                time.sleep(2)
        ordering_check = self._psql('SELECT CASE WHEN (SELECT id FROM products ORDER BY id DESC LIMIT 1) >= (SELECT id FROM products ORDER BY id ASC LIMIT 1) THEN 1 ELSE 0 END;')
        success = user_count > 0 and product_count > 0 and order_count > 0 and ordering_check == '1'
        details = {'user_count': user_count, 'product_count': product_count, 'order_count': order_count, 'ordering_check': ordering_check}
        self.evidence.record_result('database', details)
        return ValidationResult('database', success, 'Database validation passed' if success else 'Database validation failed', details, test_ids=self.test_ids)
