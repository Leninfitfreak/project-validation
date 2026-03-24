from __future__ import annotations

import time

from playwright.sync_api import Page

from validation.checks import frontend_checks
from validation.core.config import ValidationConfig
from validation.core.reporting import RunRecorder, StepResult
from validation.core.screenshots import capture_when_ready
from validation.core.waits import wait_for_selector, wait_for_text


def unique_user(config: ValidationConfig) -> dict[str, str]:
    template = config.users["signup_user"]
    stamp = str(int(time.time()))
    return {
        "full_name": template["full_name"],
        "email": f"{template['email_prefix']}+{stamp}@{template['email_domain']}",
        "password": template["password"],
    }


def run(page: Page, config: ValidationConfig, recorder: RunRecorder) -> dict[str, str]:
    waits = config.settings["defaults"]["waits"]
    image_rules = config.settings["defaults"]["screenshot_quality"]
    timeout = waits["timeout_ms"]
    long_timeout = waits["long_timeout_ms"]
    user = unique_user(config)

    page.goto(config.env["INGRESS_URL"], wait_until="domcontentloaded")
    capture_when_ready(
        page,
        config.screenshot_dir("application") / "frontend-login.png",
        verify=lambda: frontend_checks.login_page(page, timeout),
        retries=waits["retry_count"],
        retry_wait_ms=waits["retry_sleep_ms"],
        timeout_ms=timeout,
        image_rules=image_rules,
    )
    recorder.add_step(StepResult("APP-001", "application", "Frontend login page", "PASS", "Login page visible", "screenshots/application/frontend-login.png"))

    page.get_by_role("button", name="Create account").click()
    capture_when_ready(
        page,
        config.screenshot_dir("application") / "frontend-signup.png",
        verify=lambda: (
            frontend_checks.signup_page(page, timeout),
            wait_for_selector(page, 'input[name="fullName"]', timeout),
            wait_for_selector(page, 'input[name="confirmPassword"]', timeout),
        ),
        retries=waits["retry_count"],
        retry_wait_ms=waits["retry_sleep_ms"],
        timeout_ms=timeout,
        image_rules=image_rules,
    )
    recorder.add_step(StepResult("APP-002", "application", "Frontend signup page", "PASS", "Signup form visible", "screenshots/application/frontend-signup.png"))

    page.locator('input[name="fullName"]').fill(user["full_name"])
    page.locator('input[name="email"]').fill(user["email"])
    page.locator('input[name="password"]').fill(user["password"])
    page.locator('input[name="confirmPassword"]').fill(user["password"])
    page.get_by_role("button", name="Create account").click()

    capture_when_ready(
        page,
        config.screenshot_dir("application") / "frontend-signup-success.png",
        verify=lambda: wait_for_text(page, "Account created successfully", long_timeout),
        retries=waits["retry_count"],
        retry_wait_ms=waits["retry_sleep_ms"],
        timeout_ms=long_timeout,
        image_rules=image_rules,
    )
    recorder.add_step(StepResult("APP-003", "application", "Signup success state", "PASS", "Signup success notice visible", "screenshots/application/frontend-signup-success.png"))

    page.locator('input[name="email"]').fill(user["email"])
    page.locator('input[name="password"]').fill(user["password"])
    page.get_by_role("button", name="Login").click()

    capture_when_ready(
        page,
        config.screenshot_dir("application") / "frontend-dashboard.png",
        verify=lambda: frontend_checks.dashboard_ready(page, long_timeout),
        retries=waits["retry_count"],
        retry_wait_ms=waits["retry_sleep_ms"],
        timeout_ms=long_timeout,
        image_rules=image_rules,
    )
    recorder.add_step(StepResult("APP-004", "application", "Authenticated dashboard", "PASS", "Dashboard fully visible", "screenshots/application/frontend-dashboard.png"))
    return user
