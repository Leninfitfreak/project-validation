from __future__ import annotations

import io
import json
import subprocess
import zipfile
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


def github_auth(config: ValidationConfig) -> tuple[str, str] | None:
    username = config.env.get("GITHUB_USERNAME", "").strip()
    password = config.env.get("GITHUB_PASSWORD_OR_TOKEN", "").strip()
    if username and password:
        return username, password

    proc = subprocess.run(
        ["git", "credential", "fill"],
        input="protocol=https\nhost=github.com\n\n",
        text=True,
        capture_output=True,
        check=False,
    )
    if proc.returncode != 0:
        return None

    creds: dict[str, str] = {}
    for line in proc.stdout.splitlines():
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        creds[key.strip()] = value.strip()
    if creds.get("username") and creds.get("password"):
        return creds["username"], creds["password"]
    return None


def github_headers() -> dict[str, str]:
    return {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }


def api_get_json(url: str, auth: tuple[str, str] | None = None) -> dict:
    response = requests.get(url, headers=github_headers(), auth=auth, timeout=30)
    response.raise_for_status()
    return response.json()


def download_deployment_payload(repo: str, artifact_id: int, auth: tuple[str, str] | None) -> dict:
    if auth is None:
        raise RuntimeError(
            "GitHub Actions artifact download requires authentication. "
            "Provide GITHUB_USERNAME/GITHUB_PASSWORD_OR_TOKEN locally or ensure a GitHub credential helper is configured."
        )
    archive_url = f"https://api.github.com/repos/{repo}/actions/artifacts/{artifact_id}/zip"
    response = requests.get(archive_url, headers=github_headers(), auth=auth, timeout=60)
    response.raise_for_status()
    with zipfile.ZipFile(io.BytesIO(response.content)) as archive:
        return json.loads(archive.read("deployment-result.json").decode("utf-8-sig"))




def current_gitops_head(config: ValidationConfig) -> str | None:
    _, gitops_root = deployment_roots(config)
    result = shell_run(["git", "rev-parse", f"origin/{config.env['DEPLOYMENT_POC_GITOPS_BRANCH']}"], cwd=gitops_root)
    if int(result["returncode"]) != 0:
        return None
    return str(result["stdout"]).strip() or None


def latest_successful_deployment_run(config: ValidationConfig) -> dict:
    repo = config.env["DEPLOYMENT_POC_REPO"]
    workflow_file = config.env["DEPLOYMENT_POC_WORKFLOW_FILE"]
    api_base = config.settings["defaults"]["deployment_poc"]["github_api_base"]
    auth = github_auth(config)
    ticket_filter = config.env.get("DEPLOYMENT_POC_TICKET", "").strip()
    preferred_head = None if ticket_filter else current_gitops_head(config)

    runs_url = f"{api_base}/repos/{repo}/actions/workflows/{workflow_file}/runs?status=completed&per_page=20"
    runs = api_get_json(runs_url, auth=auth).get("workflow_runs", [])
    if not runs:
        raise RuntimeError(f"No completed workflow runs were returned for {workflow_file}")

    selected_fallback: dict | None = None

    for run_data in runs:
        if run_data.get("status") != "completed" or run_data.get("conclusion") != "success":
            continue
        run_id = int(run_data["id"])
        if not str(run_data.get("path", "")).endswith(workflow_file):
            continue

        artifacts = api_get_json(f"{api_base}/repos/{repo}/actions/runs/{run_id}/artifacts", auth=auth).get("artifacts", [])
        artifact = next((item for item in artifacts if item.get("name") == "deployment-result" and not item.get("expired")), None)
        if artifact is None:
            continue

        payload = download_deployment_payload(repo, int(artifact["id"]), auth=auth)
        if payload.get("outcome") != "success":
            continue
        if ticket_filter and payload.get("jira_ticket") != ticket_filter:
            continue

        jobs = api_get_json(f"{api_base}/repos/{repo}/actions/runs/{run_id}/jobs", auth=auth).get("jobs", [])
        if not jobs:
            raise RuntimeError(f"No GitHub Actions jobs were returned for run {run_id}")
        job = jobs[0]
        candidate = {
            "run_id": run_id,
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
            "payload": payload,
            "artifact_path": f"github-actions://{repo}/runs/{run_id}/artifacts/{artifact['id']}",
        }
        if preferred_head and payload.get("gitops_commit") == preferred_head:
            return candidate
        if selected_fallback is None:
            selected_fallback = candidate

    if selected_fallback is not None:
        return selected_fallback
    if ticket_filter:
        raise RuntimeError(f"No successful deployment-poc workflow run with deployment-result artifact was found for ticket {ticket_filter}")
    raise RuntimeError("No successful deployment-poc workflow run with deployment-result artifact was found")


def validate_consistency(config: ValidationConfig, summary: dict) -> dict:
    _, gitops_root = deployment_roots(config)
    payload = summary["payload"]
    target = payload["target"]
    deployment_settings = config.settings["defaults"]["deployment_poc"]
    expected_runner = deployment_settings.get("expected_runner_name", "")
    required_runner_labels = {label.casefold() for label in deployment_settings.get("required_runner_labels", [])}
    acceptable_actions = set(deployment_settings["acceptable_actions"])

    if payload.get("deployment_action") not in acceptable_actions:
        raise RuntimeError(f"Unexpected deployment action: {payload.get('deployment_action')}")
    if expected_runner and summary.get("runner_name") != expected_runner:
        raise RuntimeError(f"Deployment workflow used unexpected runner: {summary.get('runner_name')}")
    actual_labels = {str(label).casefold() for label in summary.get("labels", [])}
    missing_labels = sorted(required_runner_labels - actual_labels)
    if missing_labels:
        raise RuntimeError(
            f"Deployment workflow runner labels are incomplete: missing {', '.join(missing_labels)}"
        )

    shell_run(["git", "fetch", "origin", config.env["DEPLOYMENT_POC_GITOPS_BRANCH"]], cwd=gitops_root)
    gitops_head = shell_run(["git", "rev-parse", f"origin/{config.env['DEPLOYMENT_POC_GITOPS_BRANCH']}"], cwd=gitops_root)
    values_file = shell_run(
        ["git", "show", f"origin/{config.env['DEPLOYMENT_POC_GITOPS_BRANCH']}:{target['values_path']}"],
        cwd=gitops_root,
    )
    if int(values_file["returncode"]) != 0:
        raise RuntimeError(f"Unable to read GitOps file {target['values_path']} from origin/{config.env['DEPLOYMENT_POC_GITOPS_BRANCH']}: {values_file['stderr']}")
    values_payload = yaml.safe_load(str(values_file["stdout"]))
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
    if current_tag != target.get("resolved_version"):
        raise RuntimeError(
            f"GitOps values file {target['values_path']} does not match resolved version {target.get('resolved_version')}"
        )

    current_head = gitops_head["stdout"].strip()
    requested_commit = str(payload.get("gitops_commit") or "").strip()
    revision_advanced = False
    if revision != requested_commit:
        ancestor_check = shell_run(["git", "merge-base", "--is-ancestor", requested_commit, revision], cwd=gitops_root)
        if int(ancestor_check["returncode"]) != 0 or current_tag != target.get("resolved_version"):
            raise RuntimeError(
                f"ArgoCD app {target['argocd_app']} revision mismatch: expected deployment commit {requested_commit} but live revision is {revision}"
            )
        revision_advanced = True
    if revision != current_head and current_tag != target.get("resolved_version"):
        raise RuntimeError(
            f"GitOps branch head mismatch: expected resolved version {target.get('resolved_version')} at head {current_head}"
        )

    return {
        "gitops_head": current_head,
        "current_tag": current_tag,
        "argocd_sync": sync_status,
        "argocd_health": health_status,
        "argocd_revision": revision,
        "revision_advanced": revision_advanced,
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
