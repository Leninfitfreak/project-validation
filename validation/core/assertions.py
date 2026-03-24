from __future__ import annotations

from playwright.sync_api import Page

from .waits import wait_for_condition, wait_for_text


def assert_text(page: Page, text: str, timeout_ms: int) -> None:
    wait_for_text(page, text, timeout_ms)


def assert_row_count(page: Page, selector: str, minimum: int, timeout_ms: int) -> None:
    wait_for_condition(
        page,
        f"{selector} row count >= {minimum}",
        lambda: page.locator(selector).count() >= minimum,
        timeout_ms,
    )


def assert_not_contains(page: Page, text: str, timeout_ms: int) -> None:
    wait_for_condition(
        page,
        f"page does not contain {text}",
        lambda: text not in (page.text_content("body") or ""),
        timeout_ms,
    )
