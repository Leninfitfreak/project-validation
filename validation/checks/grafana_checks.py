from __future__ import annotations

from validation.core.assertions import assert_text
from validation.core.waits import wait_for_condition


def login_page(page, timeout_ms: int) -> None:
    assert_text(page, "Welcome to Grafana", timeout_ms)


def dashboard_list(page, timeout_ms: int) -> None:
    assert_text(page, "LeninKart Platform Overview", timeout_ms)
    assert_text(page, "LeninKart Product Service Overview", timeout_ms)
    assert_text(page, "LeninKart Order Service Overview", timeout_ms)


def dashboard_ready(page, title: str, panel_hint: str, timeout_ms: int) -> None:
    assert_text(page, title, timeout_ms)
    assert_text(page, panel_hint, timeout_ms)
    wait_for_condition(
        page,
        f"{title} dashboard shell settled",
        lambda: "Cancel" not in (page.text_content("body") or ""),
        timeout_ms,
    )

    if title == "LeninKart Logs Overview":
        wait_for_condition(
            page,
            "logs dashboard populated",
            lambda: _logs_dashboard_populated(page),
            timeout_ms,
        )


def _logs_dashboard_populated(page) -> bool:
    body = page.text_content("body") or ""
    if "Cancel" in body or "No data" in body:
        return False
    log_markers = ("INFO", "WARN", "ERROR", "product-service", "order-service", "trace_id", "timestamp")
    return sum(1 for marker in log_markers if marker in body) >= 2
