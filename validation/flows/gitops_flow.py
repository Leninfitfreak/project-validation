from __future__ import annotations

from playwright.sync_api import Page

from validation.checks import argocd_checks
from validation.core.config import ValidationConfig
from validation.core.reporting import RunRecorder, StepResult
from validation.core.screenshots import capture_when_ready


def run(page: Page, config: ValidationConfig, recorder: RunRecorder) -> None:
    waits = config.settings["defaults"]["waits"]
    image_rules = config.settings["defaults"]["screenshot_quality"]
    timeout = waits["timeout_ms"]
    long_timeout = waits["long_timeout_ms"]

    page.goto(config.env["ARGOCD_URL"], wait_until="domcontentloaded")
    capture_when_ready(
        page,
        config.screenshot_dir("gitops") / "argocd-login.png",
        require_no_loading=False,
        verify=lambda: argocd_checks.login_page(page, timeout),
        retries=waits["retry_count"],
        retry_wait_ms=waits["retry_sleep_ms"],
        timeout_ms=timeout,
        image_rules=image_rules,
    )
    recorder.add_step(StepResult("GIT-001", "gitops", "ArgoCD login page", "PASS", "ArgoCD login visible", "screenshots/gitops/argocd-login.png"))

    page.locator('input[name="username"]').fill(config.env["ARGOCD_USERNAME"])
    page.locator('input[name="password"]').fill(config.env["ARGOCD_PASSWORD"])
    page.get_by_role("button", name="Sign In").click()

    expected_apps = config.settings["defaults"]["gitops"]["expected_apps"]
    capture_when_ready(
        page,
        config.screenshot_dir("gitops") / "argocd-app-list.png",
        require_no_loading=False,
        verify=lambda: argocd_checks.app_list(page, long_timeout),
        retries=waits["retry_count"],
        retry_wait_ms=waits["retry_sleep_ms"],
        timeout_ms=long_timeout,
        image_rules=image_rules,
    )
    recorder.add_step(StepResult("GIT-002", "gitops", "ArgoCD applications list", "PASS", "Core app names visible", "screenshots/gitops/argocd-app-list.png"))

    page.get_by_text("dev-product-service", exact=False).first.click()
    capture_when_ready(
        page,
        config.screenshot_dir("gitops") / "argocd-app-detail.png",
        require_no_loading=False,
        verify=lambda: argocd_checks.app_detail(page, "dev-product-service", long_timeout),
        retries=waits["retry_count"],
        retry_wait_ms=waits["retry_sleep_ms"],
        timeout_ms=long_timeout,
        image_rules=image_rules,
    )
    recorder.add_step(StepResult("GIT-003", "gitops", "ArgoCD app detail", "PASS", "Selected app detail visible", "screenshots/gitops/argocd-app-detail.png"))
