from __future__ import annotations

import json

from validation.checks import deployment_poc_checks
from validation.core.config import ValidationConfig
from validation.core.reporting import RunRecorder, StepResult
from validation.core.screenshots import capture_when_ready
from validation.ui import deployment_ui_checks, login_flows


def run(page, config: ValidationConfig, recorder: RunRecorder) -> None:
    waits = config.settings["defaults"]["waits"]
    image_rules = config.settings["defaults"]["screenshot_quality"]
    long_timeout = waits["long_timeout_ms"]

    summary = deployment_poc_checks.latest_successful_deployment_run(config)
    validation = deployment_poc_checks.validate_consistency(config, summary)
    payload = summary["payload"]
    target = payload["target"]

    warnings: list[str] = [
        "Jira browser UI proof is intentionally out of scope for the final supported validation flow because Atlassian MFA is not automated in project-validation."
    ]

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
        "jira_ticket": payload["jira_ticket"],
        "jira_proof_mode": "unsupported",
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
        "verdict": "PASS_WITH_WARNINGS",
        "warnings": warnings,
        "supporting_artifact_path": summary["artifact_path"],
    }
    summary_path = config.artifacts_dir / "deployment-poc-validation-summary.json"
    summary_path.write_text(json.dumps(validation_summary, indent=2), encoding="utf-8")
    recorder.add_artifact(summary_path)
