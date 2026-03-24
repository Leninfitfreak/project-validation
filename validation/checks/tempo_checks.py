from __future__ import annotations

from validation.core.assertions import assert_text
from validation.core.waits import wait_for_condition


def search_results(page, service_name: str, timeout_ms: int) -> None:
    assert_text(page, service_name, timeout_ms)
    wait_for_condition(
        page,
        f"tempo results visible for {service_name}",
        lambda: page.get_by_text(service_name, exact=False).count() > 0,
        timeout_ms,
    )


def trace_detail(page, service_name: str, timeout_ms: int) -> None:
    assert_text(page, service_name, timeout_ms)
    assert_text(page, "Trace", timeout_ms)
