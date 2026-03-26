from __future__ import annotations

import json
from html import escape
from pathlib import Path

from playwright.sync_api import Page

from validation.checks import deployment_poc_checks
from validation.core.config import ValidationConfig
from validation.core.reporting import RunRecorder, StepResult
from validation.core.screenshots import capture_when_ready
from validation.core.waits import wait_for_condition, wait_for_text


def _write_html(target: Path, title: str, body: str) -> Path:
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        "\n".join(
            [
                "<!doctype html>",
                "<html><head><meta charset='utf-8'>",
                f"<title>{escape(title)}</title>",
                "<style>body{font-family:Segoe UI,Arial,sans-serif;background:#f6f8fb;color:#1f2937;margin:0;padding:32px;}main{max-width:1100px;margin:0 auto;background:white;border-radius:16px;padding:32px;box-shadow:0 8px 24px rgba(0,0,0,.08);}h1,h2{margin-top:0;}pre{background:#111827;color:#e5e7eb;padding:16px;border-radius:12px;overflow:auto;}dl{display:grid;grid-template-columns:220px 1fr;gap:12px 18px;}dt{font-weight:700;}dd{margin:0;} .note{background:#fff7ed;border:1px solid #fdba74;padding:12px 16px;border-radius:12px;}</style>",
                "</head><body><main>",
                body,
                "</main></body></html>",
            ]
        ),
        encoding="utf-8",
    )
    return target


def _jira_fallback_html(config: ValidationConfig, summary: dict) -> Path:
    payload = summary["payload"]
    target = config.artifacts_dir / "deployment-poc" / "jira-ticket-proof.html"
    metadata_lines = "\n".join(
        f"<dt>{escape(key)}</dt><dd>{escape(str(value))}</dd>"
        for key, value in payload.get("metadata", {}).items()
    )
    body = (
        f"<h1>Jira Ticket Evidence: {escape(payload.get('jira_ticket', ''))}</h1>"
        f"<p>{escape(payload.get('issue_summary', ''))}</p>"
        "<div class='note'><strong>Fallback mode:</strong> A browser-authenticated Jira session was not configured in "
        "project-validation, so this screenshot is rendered from the successful deployment artifact for honest proof of "
        "the ticket metadata used by the workflow.</div>"
        "<h2>Parsed Metadata</h2>"
        f"<dl>{metadata_lines}</dl>"
    )
    return _write_html(target, f"Jira Ticket Evidence {payload.get('jira_ticket', '')}", body)


def _result_html(config: ValidationConfig, summary: dict, validation: dict) -> Path:
    payload = summary["payload"]
    target = config.artifacts_dir / "deployment-poc" / "deployment-result-proof.html"
    detail_rows = [
        ("Jira ticket", payload.get("jira_ticket", "")),
        ("Workflow run", f"#{summary.get('run_number', '')}"),
        ("Runner", summary.get("runner_name", "")),
        ("Deployment action", payload.get("deployment_action", "")),
        ("Requested version", payload.get("target", {}).get("requested_version", "")),
        ("Resolved version", payload.get("target", {}).get("resolved_version", "")),
        ("GitOps commit", payload.get("gitops_commit", "")),
        ("ArgoCD app", payload.get("target", {}).get("argocd_app", "")),
        ("Sync", validation.get("argocd_sync", "")),
        ("Health", validation.get("argocd_health", "")),
    ]
    rows = "\n".join(f"<dt>{escape(k)}</dt><dd>{escape(str(v))}</dd>" for k, v in detail_rows)
    body = (
        "<h1>Deployment Result Proof</h1>"
        "<p>Readable deployment-poc evidence generated from the latest successful workflow artifact.</p>"
        f"<dl>{rows}</dl>"
        "<h2>Deployment Result JSON</h2>"
        f"<pre>{escape(json.dumps(payload, indent=2))}</pre>"
    )
    return _write_html(target, "Deployment Result Proof", body)


def _runner_html(config: ValidationConfig, summary: dict) -> Path:
    target = config.artifacts_dir / "deployment-poc" / "github-actions-runner-proof.html"
    label_items = "".join(f"<li>{escape(str(label))}</li>" for label in summary.get("labels", []))
    step_items = "".join(
        f"<li>{escape(str(step.get('name', '')))} - {escape(str(step.get('conclusion', '')))}</li>"
        for step in summary.get("steps", [])
    )
    body = (
        "<h1>GitHub Actions Runner Proof</h1>"
        "<p>Rendered from the public GitHub Actions jobs API for the validated deployment run.</p>"
        "<h2>Runner</h2>"
        f"<dl><dt>Runner name</dt><dd>{escape(str(summary.get('runner_name', '')))}</dd>"
        f"<dt>Runner group</dt><dd>{escape(str(summary.get('runner_group_name', '')))}</dd>"
        f"<dt>Job name</dt><dd>{escape(str(summary.get('job_name', '')))}</dd>"
        f"<dt>Job URL</dt><dd>{escape(str(summary.get('job_url', '')))}</dd></dl>"
        "<h2>Runner labels</h2>"
        f"<ul>{label_items}</ul>"
        "<h2>Completed steps</h2>"
        f"<ul>{step_items}</ul>"
    )
    return _write_html(target, "GitHub Actions Runner Proof", body)


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
    jira_proof_mode = "artifact_fallback"
    jira_url_template = config.env.get("JIRA_TICKET_URL_TEMPLATE", "").strip()
    jira_ticket = payload["jira_ticket"]

    if jira_url_template:
        jira_url = jira_url_template.format(ticket=jira_ticket)
        try:
            page.goto(jira_url, wait_until="domcontentloaded")
            capture_when_ready(
                page,
                config.screenshot_dir("deployment") / "jira-ticket-proof.png",
                require_no_loading=False,
                verify=lambda: (
                    wait_for_text(page, jira_ticket, long_timeout),
                    wait_for_text(page, payload.get("issue_summary", ""), long_timeout),
                ),
                retries=waits["retry_count"],
                retry_wait_ms=waits["retry_sleep_ms"],
                timeout_ms=long_timeout,
                image_rules=image_rules,
            )
            jira_proof_mode = "direct_gui"
        except Exception:
            warnings.append(
                "Direct Jira browser proof was not reachable from project-validation, so artifact-backed Jira ticket proof was used."
            )

    if jira_proof_mode != "direct_gui":
        fallback_html = _jira_fallback_html(config, summary)
        page.goto(fallback_html.resolve().as_uri(), wait_until="domcontentloaded")
        capture_when_ready(
            page,
            config.screenshot_dir("deployment") / "jira-ticket-proof.png",
            require_no_loading=False,
            verify=lambda: (
                wait_for_text(page, "Jira Ticket Evidence", timeout),
                wait_for_text(page, jira_ticket, timeout),
                wait_for_text(page, payload.get("issue_summary", ""), timeout),
            ),
            retries=waits["retry_count"],
            retry_wait_ms=waits["retry_sleep_ms"],
            timeout_ms=timeout,
            image_rules=image_rules,
        )

    recorder.add_step(
        StepResult(
            "DEP-001",
            "deployment",
            "Jira ticket proof",
            "PASS",
            "Deployment ticket proof captured from the live Jira page or an honest artifact-backed fallback",
            "screenshots/deployment/jira-ticket-proof.png",
        )
    )

    page.goto(summary["run_url"], wait_until="domcontentloaded")
    capture_when_ready(
        page,
        config.screenshot_dir("deployment") / "github-actions-run-summary.png",
        require_no_loading=False,
        verify=lambda: deployment_poc_checks.github_run_summary(page, summary["workflow_name"], long_timeout),
        retries=waits["retry_count"],
        retry_wait_ms=waits["retry_sleep_ms"],
        timeout_ms=long_timeout,
        image_rules=image_rules,
    )
    recorder.add_step(
        StepResult(
            "DEP-002",
            "deployment",
            "GitHub Actions deployment run summary",
            "PASS",
            "Public workflow run summary loaded with successful deployment job visible",
            "screenshots/deployment/github-actions-run-summary.png",
        )
    )

    runner_html = _runner_html(config, summary)
    page.goto(runner_html.resolve().as_uri(), wait_until="domcontentloaded")
    capture_when_ready(
        page,
        config.screenshot_dir("deployment") / "github-actions-runner-proof.png",
        require_no_loading=False,
        verify=lambda: (
            wait_for_text(page, "GitHub Actions Runner Proof", timeout),
            wait_for_text(page, summary["runner_name"], timeout),
            wait_for_text(page, "self-hosted", timeout),
            wait_for_text(page, "Windows", timeout),
        ),
        retries=waits["retry_count"],
        retry_wait_ms=waits["retry_sleep_ms"],
        timeout_ms=timeout,
        image_rules=image_rules,
    )
    recorder.add_step(
        StepResult(
            "DEP-003",
            "deployment",
            "GitHub Actions runner proof",
            "PASS",
            "Readable runner proof confirms the validated deployment run used the expected self-hosted runner and labels",
            "screenshots/deployment/github-actions-runner-proof.png",
            "artifacts/deployment-poc/github-actions-runner-proof.html",
        )
    )

    result_html = _result_html(config, summary, validation)
    page.goto(result_html.resolve().as_uri(), wait_until="domcontentloaded")
    capture_when_ready(
        page,
        config.screenshot_dir("deployment") / "deployment-result-proof.png",
        require_no_loading=False,
        verify=lambda: (
            wait_for_text(page, "Deployment Result Proof", timeout),
            wait_for_text(page, payload.get("jira_ticket", ""), timeout),
            wait_for_text(page, payload.get("gitops_commit", "")[:7], timeout),
        ),
        retries=waits["retry_count"],
        retry_wait_ms=waits["retry_sleep_ms"],
        timeout_ms=timeout,
        image_rules=image_rules,
    )
    recorder.add_step(
        StepResult(
            "DEP-004",
            "deployment",
            "deployment-poc result proof",
            "PASS",
            "Readable deployment result artifact rendered with ticket, action, commit, and ArgoCD details",
            "screenshots/deployment/deployment-result-proof.png",
            "artifacts/deployment-poc/deployment-result-proof.html",
        )
    )

    commit_url = f"https://github.com/{config.env['DEPLOYMENT_POC_GITOPS_REPO']}/commit/{payload['gitops_commit']}"
    page.goto(commit_url, wait_until="domcontentloaded")
    capture_when_ready(
        page,
        config.screenshot_dir("deployment") / "gitops-commit-proof.png",
        require_no_loading=False,
        verify=lambda: deployment_poc_checks.github_commit_page(page, payload["gitops_commit"], target["values_path"], long_timeout),
        retries=waits["retry_count"],
        retry_wait_ms=waits["retry_sleep_ms"],
        timeout_ms=long_timeout,
        image_rules=image_rules,
    )
    recorder.add_step(
        StepResult(
            "DEP-005",
            "deployment",
            "GitOps commit proof",
            "PASS",
            "Public GitHub commit page shows the relevant leninkart-infra revision and target values file path",
            "screenshots/deployment/gitops-commit-proof.png",
        )
    )

    page.goto(config.env["ARGOCD_URL"], wait_until="domcontentloaded")
    wait_for_condition(
        page,
        "argocd login form or application list visible",
        lambda: page.locator('input[name="username"]').count() > 0
        or "Applications" in (page.text_content("body") or ""),
        long_timeout,
    )
    if page.locator('input[name="username"]').count():
        page.locator('input[name="username"]').fill(config.env["ARGOCD_USERNAME"])
        page.locator('input[name="password"]').fill(config.env["ARGOCD_PASSWORD"])
        page.get_by_role("button", name="Sign In").click()
    wait_for_text(page, "Applications", long_timeout)
    wait_for_text(page, target["argocd_app"], long_timeout)
    page.get_by_text(target["argocd_app"], exact=False).first.click()
    capture_when_ready(
        page,
        config.screenshot_dir("deployment") / "argocd-deployment-app.png",
        require_no_loading=False,
        verify=lambda: deployment_poc_checks.argocd_deployment_detail(page, target["argocd_app"], payload["gitops_commit"], long_timeout),
        retries=waits["retry_count"],
        retry_wait_ms=waits["retry_sleep_ms"],
        timeout_ms=long_timeout,
        image_rules=image_rules,
    )
    recorder.add_step(
        StepResult(
            "DEP-006",
            "deployment",
            "ArgoCD deployment application proof",
            "PASS",
            "ArgoCD application detail shows the validated app as Synced and Healthy on the expected revision",
            "screenshots/deployment/argocd-deployment-app.png",
        )
    )

    validation_summary = {
        "jira_ticket": jira_ticket,
        "jira_proof_mode": jira_proof_mode,
        "run_id": summary["run_id"],
        "run_number": summary["run_number"],
        "run_url": summary["run_url"],
        "runner_name": summary["runner_name"],
        "job_url": summary["job_url"],
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
        "verdict": "PASS",
        "warnings": warnings,
    }
    summary_path = config.artifacts_dir / "deployment-poc-validation-summary.json"
    summary_path.write_text(json.dumps(validation_summary, indent=2), encoding="utf-8")
    recorder.add_artifact(summary_path)
