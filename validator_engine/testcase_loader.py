from __future__ import annotations

import re
from pathlib import Path


class TestCaseCatalog:
    TEST_PATTERN = re.compile(r'^\|\s*([A-Z]+-\d+)\s*\|\s*([^|]+?)\s*\|')

    def __init__(self, path: Path) -> None:
        self.path = path
        self.raw = path.read_text(encoding='utf-8')
        self.cases = self._parse()

    def _parse(self) -> dict[str, str]:
        cases: dict[str, str] = {}
        for line in self.raw.splitlines():
            match = self.TEST_PATTERN.match(line.strip())
            if match:
                cases[match.group(1)] = match.group(2).strip()
        return cases

    def require(self, *test_ids: str) -> list[str]:
        missing = [test_id for test_id in test_ids if test_id not in self.cases]
        if missing:
            raise ValueError(f'Missing test cases in {self.path}: {", ".join(missing)}')
        return list(test_ids)

    def by_prefix(self, prefix: str) -> list[str]:
        return sorted(test_id for test_id in self.cases if test_id.startswith(prefix))
