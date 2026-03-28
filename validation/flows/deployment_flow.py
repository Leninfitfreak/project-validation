from __future__ import annotations

import json

from playwright.sync_api import Page

from validation.checks import deployment_poc_checks
from validation.core.config import ValidationConfig
from validation.core.reporting import RunRecorder, StepResult
from validation.core.screenshots import capture_when_ready
from validation.ui import deployment_ui_checks, login_flows
from validation.ui.playwright_helpers import scroll_top


def _capture_jira_views(page: Page, config: ValidationConfig, recorder: RunRecorder, payload: dict, timeout: int, waits: dict, image_rules: dict) -> tuple[str, list[str], dict[str, object]]:
    jira_ticket = payload["jira_ticket"]
    jira_url = login_flows.jira_ticket_url(config, jira_ticket)
    review = deployment_ui_checks.review_jira_ticket_pattern(payload.get("issue_summary", ""), payload.get("metadata", {}))
    warnings: list[str] = []

    page.goto(jira_url, wait_until="domcontentloaded")
    login_flows.ensure_jira_login(page, config, timeout)
    deployment_ui_checks.jira_ticket_page(page, jira_ticket, payload.get("issue_summary", ""), timeout)

    capture_when_ready(
        page,
        config.screenshot_dir("jira") / "jira-ticket-overview.png",
        prepare=lambda: scroll_top(page),
        verify=lambda: deployment_ui_checks.jira_ticket_header(page, jira_ticket, payload.get("issue_summary", ""), timeout),
        retries=waits["retry_count"],
        retry_wait_ms=waits["retry_sleep_ms"],
        timeout_ms=timeout,
        image_rules=image_rules,
        full_page=False,
    )
    recorder.add_step(StepResult("JIRA-001", "jira", "Jira ticket overview", "PASS", "Real Jira ticket header captured with ticket key, summary, and visible status", "screenshots/jira/jira-ticket-overview.png"))

    capture_when_ready(
        page,
        config.screenshot_dir("jira") / "jira-ticket-details.png",
        prepare=lambda: deployment_ui_checks.scroll_jira_description(page),
        verify=lambda: deployment_ui_checks.jira_description_area(page, payload.get("metadata", {}), timeout),
        retries=waits["retry_count"],
        retry_wait_ms=waits["retry_sleep_ms"],
        timeout_ms=timeout,
        image_rules=image_rules,
        full_page=False,
    )
    recorder.add_step(StepResult("JIRA-002", "jira", "Jira ticket details", "PASS", "Description and deployment metadata are readable in the Jira UI", "screenshots/jira/jira-ticket-details.png"))

    capture_when_ready(
        page,
        config.screenshot_dir("jira") / "jira-ticket-comments.png",
        prepare=lambda: deployment_ui_checks.scroll_jira_comments(page),
        verify=lambda: deployment_ui_checks.jira_comments_area(page, timeout),
        retries=waits["retry_count"],
        retry_wait_ms=waits["retry_sleep_ms"],
        timeout_ms=timeout,
        image_rules=image_rules,
        full_page=False,
    )
    recorder.add_step(StepResult("JIRA-003", "jira", "Jira comments and activity", "PASS", "Jira activity or comments area is visible as real workflow evidence", "screenshots/jira/jira-ticket-comments.png"))

    progress_status = "PASS"
    progress_detail = "Jira activity feed shows deployment progress comments from the workflow lifecycle"
    try:
        capture_when_ready(
            page,
            config.screenshot_dir("jira") / "jira-ticket-progress.png",
            prepare=lambda: deployment_ui_checks.scroll_jira_progress(page),
            verify=lambda: deployment_ui_checks.jira_progress_area(page, timeout),
            retries=waits["retry_count"],
            retry_wait_ms=waits["retry_sleep_ms"],
            timeout_ms=timeout,
            image_rules=image_rules,
            full_page=False,
        )
    except Exception as exc:
        progress_status = "WARN"
        progress_detail = f"Jira comments area was captured, but explicit stage markers were not confirmed in the visible activity feed: {exc}"
        warnings.append(progress_detail)
    recorder.add_step(StepResult("JIRA-004", "jira", "Jira deployment progress view", progress_status, progress_detail, "screenshots/jira/jira-ticket-progress.png" if progress_status == "PASS" else None))

    capture_when_ready(
        page,
        config.screenshot_dir("jira") / "jira-ticket-final-state.png",
        prepare=lambda: scroll_top(page),
        verify=lambda: deployment_ui_checks.jira_ticket_header(page, jira_ticket, payload.get("issue_summary", ""), timeout),
        retries=waits["retry_count"],
        retry_wait_ms=waits["retry_sleep_ms"],
        timeout_ms=timeout,
        image_rules=image_rules,
        full_page=False,
    )
    recorder.add_step(StepResult("JIRA-005", "jira", "Jira final state", "PASS", "Final Jira ticket state captured with status visible in the real issue UI", "screenshots/jira/jira-ticket-final-state.png"))

    review_status = str(review.get("status", "WARN"))
    review_detail = str(review.get("summary", "Jira ticket review completed"))
    if review_status != "PASS":
        warnings.extend(str(item) for item in review.get("recommendations", []))
    recorder.add_step(StepResult("JIRA-006", "jira", "Jira ticket professionalism review", review_status, review_detail))
    return "direct_gui", warnings, review


def run(page: Page, config: ValidationConfig, recorder: RunRecorder) -> None:
    waits = config.settings["defaults"]["waits"]
    image_rules = config.settings["defaults"]["screenshot_quality"]
    timeout = waits["timeout_ms"]
    long_timeout = waits["long_timeout_ms"]

    summary = deployment_poc_checks.latest_successful_deployment_run(config)
    validation = deployment_poc_checks.validate_consistency(config, summary)
    payload = summary["payload"]
    target = payload["target"]

    warnings: list[str] = []
    jira_proof_mode = "unavailable"
    jira_ticket = payload["jira_ticket"]
    jira_review: dict[str, object] = {
        "status": "WARN",
        "summary": "Jira browser review was not attempted.",
        "recommendations": [],
    }

    if login_flows.jira_ui_available(config):
        try:
            jira_proof_mode, jira_warnings, jira_review = _capture_jira_views(
                page,
                config,
                recorder,
                payload,
                long_timeout,
                waits,
                image_rules,
            )
            warnings.extend(jira_warnings)
        except Exception as exc:
            jira_warning = f"Direct Jira browser proof could not be captured: {exc}"
            jira_screenshot = None
            jira_page_url = page.url or ""
            if "/login/mfa" in jira_page_url:
                jira_warning = (
                    "Direct Jira browser proof could not be captured: Atlassian prompted for an emailed MFA code, "
                    "so unattended validation could not reach the issue page."
                )
                jira_screenshot = "screenshots/jira/jira-login-challenge.png"
                try:
                    capture_when_ready(
                        page,
                        config.screenshot_dir("jira") / "jira-login-challenge.png",
                        require_no_loading=False,
                        verify=lambda: page.title() or page.url,
                        retries=1,
                        retry_wait_ms=0,
                        timeout_ms=timeout,
                        image_rules=image_rules,
                        full_page=False,
                    )
                except Exception:
                    jira_screenshot = None
            warnings.append(jira_warning)
            recorder.add_step(
                StepResult(
                    "JIRA-001",
                    "jira",
                    "Jira ticket UI evidence",
                    "WARN",
                    jira_warning,
                    jira_screenshot,
                )
            )
            jira_review = {
                "status": "WARN",
                "summary": jira_warning,
                "recommendations": [login_flows.jira_ui_prereq_message(config)],
            }
    else:
        prereq = login_flows.jira_ui_prereq_message(config)
        warnings.append(prereq)
        recorder.add_step(
            StepResult(
                "JIRA-001",
                "jira",
                "Jira ticket UI evidence",
                "WARN",
                f"Real Jira UI proof is not configured: {prereq}",
            )
        )
        jira_review = deployment_ui_checks.review_jira_ticket_pattern(payload.get("issue_summary", ""), payload.get("metadata", {}))
        recorder.add_step(
            StepResult(
                "JIRA-006",
                "jira",
                "Jira ticket professionalism review",
                str(jira_review.get("status", "WARN")),
                str(jira_review.get("summary", "Ticket pattern review completed from deployment metadata.")),
            )
        )

    page.goto(summary["run_url"], wait_until="domcontentloaded")
    capture_when_ready(
        page,
        config.screenshot_dir("deployment") / "github-actions-run-summary.png",
        require_no_loading=False,
        verify=lambda: deployment_ui_checks.github_run_summary(page, summary["workflow_name"], long_timeout),
        retries=waits["retry_count"],
        retry_wait_ms=waits["retry_sleep_ms"],
        timeout_ms=long_timeout,
        image_rules=image_rules,
        full_page=False,
    )
    recorder.add_step(StepResult("DEP-002", "deployment", "GitHub Actions deployment run summary", "PASS", "Real GitHub Actions workflow run page captured with job summary visible", "screenshots/deployment/github-actions-run-summary.png"))

    page.goto(summary["job_url"], wait_until="domcontentloaded")
    capture_when_ready(
        page,
        config.screenshot_dir("deployment") / "github-actions-runner-proof.png",
        require_no_loading=False,
        verify=lambda: deployment_ui_checks.github_job_page(page, summary["runner_name"], long_timeout),
        retries=waits["retry_count"],
        retry_wait_ms=waits["retry_sleep_ms"],
        timeout_ms=long_timeout,
        image_rules=image_rules,
        full_page=False,
    )
    recorder.add_step(StepResult("DEP-003", "deployment", "GitHub Actions runner proof", "PASS", "Real GitHub job page captured with the self-hosted runner details visible", "screenshots/deployment/github-actions-runner-proof.png"))

    page.goto(summary["run_url"], wait_until="domcontentloaded")
    capture_when_ready(
        page,
        config.screenshot_dir("deployment") / "deployment-result-proof.png",
        require_no_loading=False,
        verify=lambda: deployment_ui_checks.github_run_artifact(page, "deployment-result", long_timeout),
        retries=waits["retry_count"],
        retry_wait_ms=waits["retry_sleep_ms"],
        timeout_ms=long_timeout,
        image_rules=image_rules,
        full_page=False,
    )
    recorder.add_step(StepResult("DEP-004", "deployment", "deployment-poc result proof", "PASS", "Real GitHub workflow run page captured with the deployment-result artifact visible as primary browser proof", "screenshots/deployment/deployment-result-proof.png"))

    commit_url = f"https://github.com/{config.env['DEPLOYMENT_POC_GITOPS_REPO']}/commit/{payload['gitops_commit']}"
    page.goto(commit_url, wait_until="domcontentloaded")
    capture_when_ready(
        page,
        config.screenshot_dir("deployment") / "gitops-commit-proof.png",
        require_no_loading=False,
        verify=lambda: deployment_ui_checks.github_commit_page(page, payload["gitops_commit"], target["values_path"], long_timeout),
        retries=waits["retry_count"],
        retry_wait_ms=waits["retry_sleep_ms"],
        timeout_ms=long_timeout,
        image_rules=image_rules,
        full_page=False,
    )
    recorder.add_step(StepResult("DEP-005", "deployment", "GitOps commit proof", "PASS", "Real public GitHub commit page shows the leninkart-infra revision and changed values file", "screenshots/deployment/gitops-commit-proof.png"))

    argocd_page = page.context.new_page()
    try:
        argocd_page.goto(config.env["ARGOCD_URL"], wait_until="domcontentloaded")
        login_flows.ensure_argocd_login(argocd_page, config, long_timeout)
        argocd_page.goto(f"{config.env['ARGOCD_URL'].rstrip('/')}/applications/{target['argocd_app']}", wait_until="domcontentloaded")
        capture_when_ready(
            argocd_page,
            config.screenshot_dir("deployment") / "argocd-deployment-app.png",
            require_no_loading=False,
            verify=lambda: deployment_ui_checks.argocd_deployment_detail(argocd_page, target["argocd_app"], payload["gitops_commit"], long_timeout),
            retries=waits["retry_count"],
            retry_wait_ms=waits["retry_sleep_ms"],
            timeout_ms=long_timeout,
            image_rules=image_rules,
            full_page=False,
        )
    finally:
        argocd_page.close()
    recorder.add_step(StepResult("DEP-006", "deployment", "ArgoCD deployment application proof", "PASS", "Real ArgoCD application page shows Synced and Healthy on the expected revision", "screenshots/deployment/argocd-deployment-app.png"))

    app_page = page.context.new_page()
    try:
        app_page.goto(config.env["INGRESS_URL"], wait_until="domcontentloaded")
        capture_when_ready(
            app_page,
            config.screenshot_dir("deployment") / "application-home-proof.png",
            require_no_loading=False,
            verify=lambda: deployment_ui_checks.application_home(app_page, "LeninKart", long_timeout),
            retries=waits["retry_count"],
            retry_wait_ms=waits["retry_sleep_ms"],
            timeout_ms=long_timeout,
            image_rules=image_rules,
            full_page=False,
        )
    finally:
        app_page.close()
    recorder.add_step(StepResult("DEP-007", "deployment", "Application deployment proof", "PASS", "Real browser screenshot confirms the deployed LeninKart application is reachable", "screenshots/deployment/application-home-proof.png"))

    validation_summary = {
        "jira_ticket": jira_ticket,
        "jira_proof_mode": jira_proof_mode,
        "jira_review": jira_review,
        "run_id": summary["run_id"],
        "run_number": summary["run_number"],
        "run_url": summary["run_url"],
        "job_url": summary["job_url"],
        "runner_name": summary["runner_name"],
        "workflow_name": summary["workflow_name"],
        "deployment_action": payload.get("deployment_action"),
        "requested_version": target.get("requested_version"),
        "resolved_version": target.get("resolved_version"),
        "gitops_commit": payload.get("gitops_commit"),
        "values_path": target.get("values_path"),
        "argocd_app": target.get("argocd_app"),
        "argocd_sync": validation["argocd_sync"],
        "argocd_health": validation["argocd_health"],
        "argocd_revision": validation["argocd_revision"],
        "gitops_head": validation["gitops_head"],
        "verdict": "PASS" if jira_proof_mode == "direct_gui" else "PASS_WITH_WARNINGS",
        "warnings": warnings,
        "supporting_artifact_path": summary["artifact_path"],
    }
    summary_path = config.artifacts_dir / "deployment-poc-validation-summary.json"
    summary_path.write_text(json.dumps(validation_summary, indent=2), encoding="utf-8")
    recorder.add_artifact(summary_path)
