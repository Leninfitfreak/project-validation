from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class EvidenceCollector:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.artifacts = root / 'artifacts'
        self.logs = root / 'logs'
        self.artifacts.mkdir(exist_ok=True)
        self.logs.mkdir(exist_ok=True)
        self.records: dict[str, Any] = {'results': {}, 'screenshots': {}, 'repairs': []}

    def record(self, key: str, value: Any) -> None:
        self.records[key] = value
        self.flush()

    def record_result(self, key: str, value: Any) -> None:
        self.records.setdefault('results', {})[key] = value
        self.flush()

    def add_repair(self, value: str) -> None:
        self.records.setdefault('repairs', []).append(value)
        self.flush()

    def add_screenshot(self, test_id: str, file_name: str) -> None:
        self.records.setdefault('screenshots', {}).setdefault(test_id, []).append(file_name)
        self.flush()

    def flush(self) -> None:
        (self.artifacts / 'evidence.json').write_text(json.dumps(self.records, indent=2), encoding='utf-8')
