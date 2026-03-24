from __future__ import annotations

from validation.core.assertions import assert_text
from validation.core.waits import wait_for_condition


def logs_ready(page, service_name: str, timeout_ms: int) -> None:
    assert_text(page, "Loki", timeout_ms)
    assert_text(page, "Logs volume", timeout_ms)
    wait_for_condition(
        page,
        f"loki logs visible for {service_name}",
        lambda: (page.text_content("body") or "").count(service_name) >= 2,
        timeout_ms,
    )
