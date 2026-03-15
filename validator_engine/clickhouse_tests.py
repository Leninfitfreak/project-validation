from __future__ import annotations

import subprocess
from pathlib import Path

from validator_engine.validators import ValidationResult


class ClickHouseTests:
    REQUIRED_DATABASES = {'signoz_traces', 'signoz_metrics', 'signoz_logs', 'signoz_meter', 'signoz_metadata'}
    REQUIRED_TABLES = {
        'signoz_traces': 'distributed_signoz_index_v3',
        'signoz_metrics': 'distributed_time_series_v4',
        'signoz_logs': 'distributed_logs_v2',
    }

    def __init__(self, root: Path, env: dict, model: dict, evidence, catalog) -> None:
        self.root = root
        self.env = env
        self.model = model
        self.evidence = evidence
        self.test_ids = catalog.require('CH-001', 'CH-002', 'CH-003', 'CH-004', 'CH-005', 'CH-006')

    def repair(self) -> list[str]:
        return []

    def _query(self, sql: str) -> str:
        result = subprocess.run(['docker', 'exec', 'signoz-clickhouse', 'bash', '-lc', f'clickhouse-client --query "{sql}"'], capture_output=True, text=True, check=True)
        return result.stdout.strip()

    def run(self, context: dict) -> ValidationResult:
        running = subprocess.run(['docker', 'inspect', 'signoz-clickhouse', '--format', '{{.State.Running}}'], capture_output=True, text=True).stdout.strip() == 'true'
        databases = {line.strip() for line in self._query('SHOW DATABASES').splitlines() if line.strip()}
        trace_tables = {line.strip() for line in self._query('SHOW TABLES FROM signoz_traces').splitlines() if line.strip()}
        metric_tables = {line.strip() for line in self._query('SHOW TABLES FROM signoz_metrics').splitlines() if line.strip()}
        log_tables = {line.strip() for line in self._query('SHOW TABLES FROM signoz_logs').splitlines() if line.strip()}
        trace_rows = int(self._query('SELECT count() FROM signoz_traces.distributed_signoz_index_v3'))
        metric_rows = int(self._query('SELECT count() FROM signoz_metrics.distributed_time_series_v4'))
        log_rows = int(self._query('SELECT count() FROM signoz_logs.distributed_logs_v2'))
        success = running and self.REQUIRED_DATABASES.issubset(databases) and self.REQUIRED_TABLES['signoz_traces'] in trace_tables and self.REQUIRED_TABLES['signoz_metrics'] in metric_tables and self.REQUIRED_TABLES['signoz_logs'] in log_tables and trace_rows > 0 and metric_rows > 0 and log_rows > 0
        details = {'running': running, 'databases': sorted(databases), 'trace_rows': trace_rows, 'metric_rows': metric_rows, 'log_rows': log_rows}
        self.evidence.record_result('clickhouse', details)
        return ValidationResult('clickhouse', success, 'ClickHouse validation passed' if success else 'ClickHouse validation failed', details, test_ids=self.test_ids)
