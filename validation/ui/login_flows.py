from __future__ import annotations

from validation.core.config import ValidationConfig
from validation.core.waits import wait_for_condition
from validation.ui.playwright_helpers import body_text


def ensure_argocd_login(page, config: ValidationConfig, timeout_ms: int) -> None:
    wait_for_condition(
        page,
        "argocd login form or application list visible",
        lambda: page.locator('input[name="username"]').count() > 0 or "Applications" in body_text(page),
        timeout_ms,
    )
    if page.locator('input[name="username"]').count():
        page.locator('input[name="username"]').fill(config.env["ARGOCD_USERNAME"])
        page.locator('input[name="password"]').fill(config.env["ARGOCD_PASSWORD"])
        page.get_by_role("button", name="Sign In").click()
        wait_for_condition(
            page,
            "argocd applications visible after login",
            lambda: "Applications" in body_text(page) and page.locator('input[name="username"]').count() == 0,
            timeout_ms,
        )
