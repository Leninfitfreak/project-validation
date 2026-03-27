from __future__ import annotations

from playwright.sync_api import Page

from validation.core.config import ValidationConfig
from validation.core.waits import wait_for_condition
from validation.ui.playwright_helpers import body_text, click_if_visible


def jira_ui_available(config: ValidationConfig) -> bool:
    template = (config.env.get("JIRA_TICKET_URL_TEMPLATE") or "").strip()
    base = (config.env.get("JIRA_BASE_URL") or "").strip()
    return bool(template or base)


def jira_ticket_url(config: ValidationConfig, ticket: str) -> str:
    template = (config.env.get("JIRA_TICKET_URL_TEMPLATE") or "").strip()
    if template:
        return template.format(ticket=ticket)
    return config.env["JIRA_BASE_URL"].rstrip("/") + f"/browse/{ticket}"


def try_login_jira(page: Page, config: ValidationConfig, timeout_ms: int) -> bool:
    email = (config.env.get("JIRA_EMAIL") or config.env.get("JIRA_USERNAME") or "").strip()
    password = (config.env.get("JIRA_PASSWORD") or "").strip()
    if not email or not password:
        return False

    click_if_visible(page.locator('button:has-text("Continue with email")'))
    click_if_visible(page.locator('button:has-text("Continue")'))

    email_locators = [
        page.locator('input[type="email"]'),
        page.locator('input[name="username"]'),
        page.locator('input#username'),
    ]
    for locator in email_locators:
        if locator.count():
            locator.first.fill(email)
            break
    else:
        return False

    click_if_visible(page.locator('button:has-text("Continue")'))
    click_if_visible(page.locator('input#login-submit'))

    password_locators = [
        page.locator('input[type="password"]'),
        page.locator('input[name="password"]'),
        page.locator('input#password'),
    ]
    wait_for_condition(
        page,
        "jira password field visible",
        lambda: any(locator.count() for locator in password_locators),
        timeout_ms,
    )
    for locator in password_locators:
        if locator.count():
            locator.first.fill(password)
            break

    click_if_visible(page.locator('button:has-text("Log in")'))
    click_if_visible(page.locator('button:has-text("Continue")'))
    click_if_visible(page.locator('input#login-submit'))
    return True


def ensure_argocd_login(page: Page, config: ValidationConfig, timeout_ms: int) -> None:
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
