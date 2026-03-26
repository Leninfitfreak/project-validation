from __future__ import annotations

import json
from pathlib import Path

import requests
import yaml
from playwright.sync_api import Page

from validation.core.config import ValidationConfig
from validation.core.shell import run as shell_run
from validation.core.waits import wait_for_condition, wait_for_text


def deployment_roots(config: ValidationConfig) -> tuple[Path, Path]:
    deployment_root = Path(config.env["DEPLOYMENT_POC_ROOT"]).expanduser().resolve()
    gitops_root = Path(config.env["LENINKART_INFRA_ROOT"]).expanduser().resolve()
    return deployment_root, gitops_root


def latest_successful_deployment_run(config: ValidationConfig) -> dict:
    deployment_root, _ = deployment_roots(config)
    ticket = config.env["DEPLOYMENT_POC_TICKET"]
    candidates: list[dict] = []
    for artifact in (deployment_root / "artifacts").glob("run-*/deployment-result/deployment-result.json"):
        payload = json.loads(artifact.read_text(encoding="utf-8"))
        if payload.get("jira_ticket") != ticket or payload.get("outcome") != "success":
            continue
        run_id = int(artifact.parents[1].name.split("-")[1])
        candidates.append({"run_id": run_id, "payload": payload, "path": artifact})
    if not candidates:
        raise RuntimeError(f"No successful deployment-poc artifact found locally for ticket {ticket}")
    latest = max(candidates, key=lambda item: item["run_id"])

    repo = config.env["DEPLOYMENT_POC_REPO"]
    workflow_file = config.env["DEPLOYMENT_POC_WORKFLOW_FILE"]
    api_base = config.settings["defaults"]["deployment_poc"]["github_api_base"]
    headers = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}

    run_resp = requests.get(f"{api_base}/repos/{repo}/actions/runs/{latest['run_id']}", headers=headers, timeout=30)
    run_resp.raise_for_status()
    run_data = run_resp.json()
    if run_data.get("status") != "completed" or run_data.get("conclusion") != "success":
        raise RuntimeError(f"Latest deployment run {latest['run_id']} is not a successful completed workflow run")
    if not str(run_data.get("path", "")).endswith(workflow_file):
        raise RuntimeError(f"Run {latest['run_id']} does not belong to {workflow_file}")

    jobs_resp = requests.get(f"{api_base}/repos/{repo}/actions/runs/{latest['run_id']}/jobs", headers=headers, timeout=30)
    jobs_resp.raise_for_status()
    jobs = jobs_resp.json().get("jobs", [])
    if not jobs:
        raise RuntimeError(f"No GitHub Actions jobs were returned for run {latest['run_id']}")
    job = jobs[0]

    return {
        "run_id": latest["run_id"],
        "run_number": run_data.get("run_number"),
        "run_url": run_data.get("html_url"),
        "job_name": job.get("name"),
        "job_url": job.get("html_url"),
        "runner_name": job.get("runner_name"),
        "runner_group_name": job.get("runner_group_name"),
        "labels": job.get("labels", []),
        "steps": job.get("steps", []),
        "head_sha": run_data.get("head_sha"),
        "workflow_name": run_data.get("name"),
        "payload": latest["payload"],
        "artifact_path": str(latest["path"]),
    }


def validate_consistency(config: ValidationConfig, summary: dict) -> dict:
    _, gitops_root = deployment_roots(config)
    payload = summary["payload"]
    target = payload["target"]
    expected_app = config.env["DEPLOYMENT_POC_ARGOCD_APP"]
    expected_values_path = config.env["DEPLOYMENT_POC_VALUES_PATH"]
    expected_runner = config.settings["defaults"]["deployment_poc"]["expected_runner_name"]
    acceptable_actions = set(config.settings["defaults"]["deployment_poc"]["acceptable_actions"])

    if payload.get("deployment_action") not in acceptable_actions:
        raise RuntimeError(f"Unexpected deployment action: {payload.get('deployment_action')}")
    if summary.get("runner_name") != expected_runner:
        raise RuntimeError(f"Deployment workflow used unexpected runner: {summary.get('runner_name')}")
    if target.get("argocd_app") != expected_app:
        raise RuntimeError(f"Deployment result resolved unexpected ArgoCD app: {target.get('argocd_app')}")
    if target.get("values_path") != expected_values_path:
        raise RuntimeError(f"Deployment result resolved unexpected values path: {target.get('values_path')}")

    shell_run(["git", "fetch", "origin", config.env["DEPLOYMENT_POC_GITOPS_BRANCH"]], cwd=gitops_root)
    gitops_head = shell_run(["git", "rev-parse", f"origin/{config.env['DEPLOYMENT_POC_GITOPS_BRANCH']}"], cwd=gitops_root)
    values_payload = yaml.safe_load((gitops_root / target["values_path"]).read_text(encoding="utf-8"))
    current_tag = str(values_payload.get("image", {}).get("tag", "")).strip()

    app_json = shell_run(
        ["kubectl", "get", "application", target["argocd_app"], "-n", "argocd", "-o", "json"]
    )
    if int(app_json["returncode"]) != 0:
        raise RuntimeError(f"kubectl get application failed: {app_json['stderr']}")
    app_payload = json.loads(str(app_json["stdout"]))
    status = app_payload.get("status", {})
    sync_status = status.get("sync", {}).get("status")
    health_status = status.get("health", {}).get("status")
    revision = status.get("sync", {}).get("revision")

    if sync_status != "Synced" or health_status != "Healthy":
        raise RuntimeError(
            f"ArgoCD app {target['argocd_app']} is not healthy: sync={sync_status}, health={health_status}"
        )
    if revision != payload.get("gitops_commit"):
        raise RuntimeError(
            f"ArgoCD app {target['argocd_app']} revision mismatch: expected {payload.get('gitops_commit')} got {revision}"
        )
    if current_tag != target.get("resolved_version"):
        raise RuntimeError(
            f"GitOps values file {target['values_path']} does not match resolved version {target.get('resolved_version')}"
        )
    if payload.get("gitops_commit") != gitops_head["stdout"].strip():
        raise RuntimeError(
            f"GitOps branch head mismatch: expected {payload.get('gitops_commit')} got {gitops_head['stdout'].strip()}"
        )

    return {
        "gitops_head": gitops_head["stdout"].strip(),
        "current_tag": current_tag,
        "argocd_sync": sync_status,
        "argocd_health": health_status,
        "argocd_revision": revision,
    }


def github_run_summary(page: Page, workflow_name: str, timeout_ms: int) -> None:
    wait_for_condition(
        page,
        "github actions run summary visible",
        lambda: workflow_name in (page.text_content("body") or "")
        and "All jobs" in (page.text_content("body") or "")
        and "Filter by job status" in (page.text_content("body") or ""),
        timeout_ms,
    )


def github_commit_page(page: Page, commit_sha: str, values_path: str, timeout_ms: int) -> None:
    wait_for_text(page, commit_sha[:7], timeout_ms)
    wait_for_text(page, values_path, timeout_ms)


def argocd_deployment_detail(page: Page, app_name: str, revision: str, timeout_ms: int) -> None:
    wait_for_text(page, app_name, timeout_ms)
    wait_for_text(page, "Healthy", timeout_ms)
    wait_for_text(page, "Synced", timeout_ms)
    wait_for_condition(
        page,
        "frontend deployment revision visible",
        lambda: revision[:7] in (page.text_content("body") or ""),
        timeout_ms,
    )
