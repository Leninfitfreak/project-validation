from __future__ import annotations

from playwright.sync_api import Page

from validation.core.config import ValidationConfig
from validation.core.reporting import RunRecorder, StepResult
from validation.core.screenshots import capture_when_ready
from validation.core.waits import wait_for_condition, wait_for_text


def _order_ledger_visible(page: Page, product_name: str) -> bool:
    body = page.text_content("body") or ""
    return product_name in body and "Status: CREATED" in body


def run(page: Page, config: ValidationConfig, recorder: RunRecorder, products: list[dict]) -> None:
    waits = config.settings["defaults"]["waits"]
    image_rules = config.settings["defaults"]["screenshot_quality"]
    timeout = waits["timeout_ms"]
    long_timeout = waits["long_timeout_ms"]

    target_product = products[0]
    target_card = page.locator(".card", has=page.get_by_text(target_product["name"], exact=True)).first
    target_card.get_by_role("button", name="Buy").click()

    # The frontend now refreshes the order ledger asynchronously after the buy call.
    # Poll the live UI instead of forcing full-page reloads, which can hang while the SPA
    # still has active network work in flight.
    wait_for_condition(
        page,
        "order ledger populated",
        lambda: _order_ledger_visible(page, target_product["name"]),
        long_timeout,
    )

    capture_when_ready(
        page,
        config.screenshot_dir("application") / "order-ledger.png",
        verify=lambda: (
            wait_for_text(page, "Order Ledger", timeout),
            wait_for_text(page, target_product["name"], long_timeout),
            wait_for_text(page, "Status: CREATED", long_timeout),
        ),
        retries=waits["retry_count"],
        retry_wait_ms=waits["retry_sleep_ms"],
        timeout_ms=long_timeout,
        image_rules=image_rules,
    )
    recorder.add_step(StepResult("APP-007", "application", "Order ledger populated", "PASS", "Order row visible after buy flow", "screenshots/application/order-ledger.png"))

    capture_when_ready(
        page,
        config.screenshot_dir("application") / "user-activity.png",
        verify=lambda: (
            wait_for_text(page, "User Activity Overview", timeout),
            wait_for_condition(
                page,
                "user activity populated",
                lambda: "No order activity yet." not in (page.text_content("body") or ""),
                long_timeout,
            ),
        ),
        retries=waits["retry_count"],
        retry_wait_ms=waits["retry_sleep_ms"],
        timeout_ms=long_timeout,
        image_rules=image_rules,
    )
    recorder.add_step(StepResult("APP-008", "application", "User activity overview", "PASS", "User activity panel visible", "screenshots/application/user-activity.png"))
