from __future__ import annotations

from validation.core.assertions import assert_text


def targets_page(page, timeout_ms: int) -> None:
    assert_text(page, "Target health", timeout_ms)
    assert_text(page, "product-service", timeout_ms)
    assert_text(page, "order-service", timeout_ms)
