from __future__ import annotations

from playwright.sync_api import Page

from validation.core.config import ValidationConfig
from validation.core.waits import wait_for_condition
from validation.ui.playwright_helpers import body_text, click_if_visible


JIRA_LOGIN_TEXTS = ["Log in", "Continue", "Atlassian", "Sign up"]


def jira_ui_available(config: ValidationConfig) -> bool:
    template = (config.env.get("JIRA_TICKET_URL_TEMPLATE") or "").strip()
    base = (config.env.get("JIRA_BASE_URL") or "").strip()
    return bool(template or base)


def jira_ui_login_available(config: ValidationConfig) -> bool:
    username = (config.env.get("JIRA_USERNAME") or config.env.get("JIRA_EMAIL") or "").strip()
    password = (config.env.get("JIRA_PASSWORD") or "").strip()
    return jira_ui_available(config) and bool(username and password)


def jira_ticket_url(config: ValidationConfig, ticket: str) -> str:
    template = (config.env.get("JIRA_TICKET_URL_TEMPLATE") or "").strip()
    if template:
        return template.format(ticket=ticket)
    return config.env["JIRA_BASE_URL"].rstrip("/") + f"/browse/{ticket}"


def jira_ui_prereq_message(config: ValidationConfig) -> str:
    if not jira_ui_available(config):
        return "JIRA_BASE_URL or JIRA_TICKET_URL_TEMPLATE is not configured in project-validation/.env"
    if not jira_ui_login_available(config):
        return "JIRA_USERNAME or JIRA_EMAIL plus JIRA_PASSWORD is required for Jira browser login"
    return "Jira UI login prerequisites are available"


def page_looks_like_jira_login(page: Page) -> bool:
    text = body_text(page)
    return any(token in text for token in JIRA_LOGIN_TEXTS) and (
        page.locator('input[type="email"]').count() > 0
        or page.locator('input[type="password"]').count() > 0
        or page.locator('input#username').count() > 0
    )


def ensure_jira_login(page: Page, config: ValidationConfig, timeout_ms: int) -> None:
    username = (config.env.get("JIRA_USERNAME") or config.env.get("JIRA_EMAIL") or "").strip()
    password = (config.env.get("JIRA_PASSWORD") or "").strip()
    if not username or not password:
        raise RuntimeError(jira_ui_prereq_message(config))

    wait_for_condition(
        page,
        "jira page visible",
        lambda: page.locator("body").count() > 0,
        timeout_ms,
    )
    if not page_looks_like_jira_login(page):
        return

    click_if_visible(page.locator('button:has-text("Continue with email")'))
    click_if_visible(page.locator('button:has-text("Continue")'))

    email_locators = [
        page.locator('input[type="email"]'),
        page.locator('input[name="username"]'),
        page.locator('input#username'),
    ]
    active_email = next((locator.first for locator in email_locators if locator.count()), None)
    if active_email is None:
        raise RuntimeError("Jira login page did not expose an email/username field")
    active_email.fill(username)
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
    active_password = next((locator.first for locator in password_locators if locator.count()), None)
    if active_password is None:
        raise RuntimeError("Jira login page did not expose a password field")
    active_password.fill(password)
    click_if_visible(page.locator('button:has-text("Log in")'))
    click_if_visible(page.locator('button:has-text("Continue")'))
    click_if_visible(page.locator('input#login-submit'))
    wait_for_condition(
        page,
        "jira issue page visible after login",
        lambda: not page_looks_like_jira_login(page),
        timeout_ms,
    )


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
