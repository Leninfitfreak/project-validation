from __future__ import annotations

from playwright.sync_api import Locator, Page

from validation.core.waits import wait_for_condition


def body_text(page: Page) -> str:
    return page.text_content("body") or ""


def click_if_visible(locator: Locator) -> bool:
    try:
        if locator.count() and locator.first.is_visible():
            locator.first.click()
            return True
    except Exception:
        return False
    return False


def wait_for_body_contains(page: Page, text: str, timeout_ms: int) -> None:
    wait_for_condition(
        page,
        f"body contains {text}",
        lambda: text in body_text(page),
        timeout_ms,
    )


def scroll_text_into_view(page: Page, text: str) -> None:
    page.locator(f"text={text}").first.scroll_into_view_if_needed()

