from __future__ import annotations

from playwright.sync_api import Page

from validation.core.config import ValidationConfig
from validation.core.reporting import RunRecorder, StepResult
from validation.core.screenshots import capture_when_ready
from validation.core.waits import wait_for_condition, wait_for_text


def _order_ledger_visible(page: Page, product_name: str) -> bool:
    body = page.text_content("body") or ""
    return product_name in body and "Status: CREATED" in body


def _orders_api_snapshot(page: Page, product_name: str) -> dict:
    script = """async (productName) => {
        const token = window.localStorage.getItem('token');
        const response = await fetch('/api/orders?_ts=' + Date.now(), {
            headers: token ? { Authorization: `Bearer ${token}` } : {},
            cache: 'no-store',
        });
        let data = null;
        try {
            data = await response.json();
        } catch (error) {
            data = null;
        }
        return {
            status: response.status,
            reachable: response.status < 500,
            hasCreatedOrder: Array.isArray(data) && data.some((order) => order.productName === productName && order.status === 'CREATED'),
        };
    }"""
    return page.evaluate(script, product_name)


def run(page: Page, config: ValidationConfig, recorder: RunRecorder, products: list[dict]) -> None:
    waits = config.settings["defaults"]["waits"]
    image_rules = config.settings["defaults"]["screenshot_quality"]
    timeout = waits["timeout_ms"]
    long_timeout = waits["long_timeout_ms"]
    api_timeout = max(long_timeout, 180000)

    target_product = products[0]

    wait_for_condition(
        page,
        "orders api reachable",
        lambda: bool(_orders_api_snapshot(page, target_product["name"])["reachable"]),
        api_timeout,
    )

    target_card = page.locator(".card", has=page.get_by_text(target_product["name"], exact=True)).first
    target_card.get_by_role("button", name="Buy").click()

    wait_for_condition(
        page,
        "order created in backend or visible in ledger",
        lambda: _order_ledger_visible(page, target_product["name"]) or bool(_orders_api_snapshot(page, target_product["name"])["hasCreatedOrder"]),
        api_timeout,
    )

    if not _order_ledger_visible(page, target_product["name"]):
        page.goto(config.env["INGRESS_URL"], wait_until="domcontentloaded")
        wait_for_text(page, "Order Ledger", long_timeout)
        wait_for_condition(
            page,
            "order ledger populated",
            lambda: _order_ledger_visible(page, target_product["name"]),
            api_timeout,
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
