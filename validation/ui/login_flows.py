from __future__ import annotations

from playwright.sync_api import Locator

from validation.core.config import ValidationConfig
from validation.core.waits import wait_for_condition
from validation.ui.playwright_helpers import body_text


def _first_visible(locator: Locator) -> Locator | None:
    try:
        count = locator.count()
    except Exception:
        return None
    for index in range(count):
        candidate = locator.nth(index)
        try:
            if candidate.is_visible():
                return candidate
        except Exception:
            continue
    return None


def ensure_argocd_login(page, config: ValidationConfig, timeout_ms: int) -> None:
    wait_for_condition(
        page,
        'argocd login form or application list visible',
        lambda: page.locator('input[name="username"]').count() > 0 or 'Applications' in body_text(page),
        timeout_ms,
    )
    if page.locator('input[name="username"]').count():
        page.locator('input[name="username"]').fill(config.env['ARGOCD_USERNAME'])
        page.locator('input[name="password"]').fill(config.env['ARGOCD_PASSWORD'])
        page.get_by_role('button', name='Sign In').click()
        wait_for_condition(
            page,
            'argocd applications visible after login',
            lambda: 'Applications' in body_text(page) and page.locator('input[name="username"]').count() == 0,
            timeout_ms,
        )


def ensure_jira_login(page, config: ValidationConfig, timeout_ms: int) -> None:
    issue_key = config.env.get('DEPLOYMENT_POC_TICKET', '').strip()
    wait_for_condition(
        page,
        'jira page or login form visible',
        lambda: issue_key in body_text(page)
        or page.locator('input#username').count() > 0
        or page.locator('input[name="username"]').count() > 0
        or page.locator('input#password').count() > 0,
        timeout_ms,
    )

    username_input = _first_visible(page.locator('input#username')) or _first_visible(page.locator('input[name="username"]'))
    if username_input is not None:
        username_input.fill(config.env['JIRA_USERNAME'])
        if page.locator('#login-submit').count() > 0:
            page.locator('#login-submit').click()
        elif page.get_by_role('button', name='Continue').count() > 0:
            page.get_by_role('button', name='Continue').click()
        wait_for_condition(
            page,
            'jira password form or issue page visible',
            lambda: (_first_visible(page.locator('input#password')) is not None) or issue_key in body_text(page),
            timeout_ms,
        )

    password_input = _first_visible(page.locator('input#password')) or _first_visible(page.locator('input[name="password"]'))
    if password_input is not None:
        password_input.fill(config.env['JIRA_PASSWORD'])
        if page.locator('#login-submit').count() > 0:
            page.locator('#login-submit').click()
        elif page.get_by_role('button', name='Log in').count() > 0:
            page.get_by_role('button', name='Log in').click()

    wait_for_condition(
        page,
        'jira issue visible after login',
        lambda: issue_key in body_text(page),
        timeout_ms,
    )
