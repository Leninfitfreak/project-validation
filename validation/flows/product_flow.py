from __future__ import annotations

from playwright.sync_api import Page

from validation.core.config import ValidationConfig
from validation.core.reporting import RunRecorder, StepResult
from validation.core.screenshots import capture_when_ready
from validation.core.waits import wait_for_condition, wait_for_text


def run(page: Page, config: ValidationConfig, recorder: RunRecorder) -> list[dict]:
    waits = config.settings["defaults"]["waits"]
    image_rules = config.settings["defaults"]["screenshot_quality"]
    timeout = waits["timeout_ms"]
    long_timeout = waits["long_timeout_ms"]
    products = config.products["products"]

    for index, product in enumerate(products):
        page.locator('input[name="name"]').fill(product["name"])
        page.locator('input[name="price"]').fill(str(product["price"]))
        page.locator('input[name="description"]').fill(product["description"])
        if index == 0:
            capture_when_ready(
                page,
                config.screenshot_dir("application") / "product-form.png",
                verify=lambda: wait_for_condition(
                    page,
                    "filled product form",
                    lambda: page.locator('input[name="name"]').input_value() == product["name"],
                    timeout,
                ),
                retries=waits["retry_count"],
                retry_wait_ms=waits["retry_sleep_ms"],
                timeout_ms=timeout,
                image_rules=image_rules,
            )
            recorder.add_step(StepResult("APP-005", "application", "Product creation form", "PASS", "Filled product form captured", "screenshots/application/product-form.png"))
        page.get_by_role("button", name="Add product").click()
        wait_for_text(page, product["name"], long_timeout)

    capture_when_ready(
        page,
        config.screenshot_dir("application") / "product-list.png",
        verify=lambda: (
            wait_for_text(page, products[0]["name"], long_timeout),
            wait_for_text(page, products[1]["name"], long_timeout),
        ),
        retries=waits["retry_count"],
        retry_wait_ms=waits["retry_sleep_ms"],
        timeout_ms=long_timeout,
        image_rules=image_rules,
    )
    recorder.add_step(StepResult("APP-006", "application", "Product list with created items", "PASS", "Created products visible in list", "screenshots/application/product-list.png"))
    return products
