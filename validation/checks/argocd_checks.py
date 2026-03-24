from __future__ import annotations

from validation.core.assertions import assert_text


def login_page(page, timeout_ms: int) -> None:
    assert_text(page, "Username", timeout_ms)
    assert_text(page, "Password", timeout_ms)


def app_list(page, timeout_ms: int) -> None:
    assert_text(page, "leninkart-root", timeout_ms)
    assert_text(page, "dev-product-service", timeout_ms)


def app_detail(page, app_name: str, timeout_ms: int) -> None:
    assert_text(page, app_name, timeout_ms)
    assert_text(page, "Healthy", timeout_ms)
    assert_text(page, "Synced", timeout_ms)
