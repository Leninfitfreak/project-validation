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


def scroll_text_into_view(page: Page, text: str) -> bool:
    locator = page.locator(f"text={text}")
    if locator.count():
        locator.first.scroll_into_view_if_needed(timeout=5000)
        page.wait_for_timeout(250)
        return True
    return False


def scroll_first_visible_text(page: Page, texts: list[str]) -> str | None:
    for text in texts:
        if scroll_text_into_view(page, text):
            return text
    return None


def scroll_top(page: Page) -> None:
    page.evaluate("window.scrollTo(0, 0)")
    page.wait_for_timeout(250)
