from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class ValidationResult:
    name: str
    success: bool
    summary: str
    details: dict[str, Any] = field(default_factory=dict)
    repairs: list[str] = field(default_factory=list)
    test_ids: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
