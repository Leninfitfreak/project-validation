from __future__ import annotations

import time
from typing import Callable

from playwright.sync_api import Locator, Page


def wait_for_text(page: Page, text: str, timeout_ms: int) -> None:
    page.get_by_text(text, exact=False).first.wait_for(state="visible", timeout=timeout_ms)


def wait_for_selector(page: Page, selector: str, timeout_ms: int) -> Locator:
    locator = page.locator(selector).first
    locator.wait_for(state="visible", timeout=timeout_ms)
    return locator


def wait_for_count(page: Page, selector: str, minimum: int, timeout_ms: int) -> None:
    deadline = time.time() + (timeout_ms / 1000)
    while time.time() < deadline:
        if page.locator(selector).count() >= minimum:
            return
        page.wait_for_timeout(500)
    raise TimeoutError(f"selector {selector} count did not reach {minimum}")


def wait_for_condition(page: Page, description: str, fn: Callable[[], bool], timeout_ms: int) -> None:
    deadline = time.time() + (timeout_ms / 1000)
    while time.time() < deadline:
        try:
            if fn():
                return
        except Exception:
            pass
        page.wait_for_timeout(500)
    raise TimeoutError(f"condition timed out: {description}")


def wait_for_no_loading(page: Page, timeout_ms: int) -> None:
    deadline = time.time() + (timeout_ms / 1000)
    forbidden = ("loading", "please wait", "processing", "spinner")
    while time.time() < deadline:
        body = (page.text_content("body") or "").lower()
        if not any(token in body for token in forbidden):
            return
        page.wait_for_timeout(500)
    raise TimeoutError("page remained in loading state")
