from __future__ import annotations

from validation.core.assertions import assert_text


def login_page(page, timeout_ms: int) -> None:
    assert_text(page, "LeninKart E-Commerce Portal", timeout_ms)
    assert_text(page, "Sign in to workspace", timeout_ms)


def signup_page(page, timeout_ms: int) -> None:
    assert_text(page, "Create your account", timeout_ms)


def dashboard_ready(page, timeout_ms: int) -> None:
    assert_text(page, "LeninKart E-Commerce Operations", timeout_ms)
    assert_text(page, "Product Catalog", timeout_ms)
    assert_text(page, "Order Ledger", timeout_ms)
