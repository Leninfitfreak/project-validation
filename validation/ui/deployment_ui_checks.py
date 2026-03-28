from __future__ import annotations

from playwright.sync_api import Page

from validation.core.waits import wait_for_condition, wait_for_text
from validation.ui.playwright_helpers import body_text, scroll_first_visible_text


JIRA_PROGRESS_KEYWORDS = [
    "workflow_triggered",
    "jira_validated",
    "target_resolved",
    "lock_acquired",
    "gitops_commit_pushed",
    "argocd_sync_started",
    "argocd_synced_healthy",
    "post_checks_completed",
    "completed",
    "failed",
]


def jira_ticket_page(page: Page, ticket: str, summary: str, timeout_ms: int) -> None:
    wait_for_condition(
        page,
        "jira ticket page visible",
        lambda: ticket in body_text(page) and (summary in body_text(page) or "Description" in body_text(page)),
        timeout_ms,
    )


def jira_ticket_header(page: Page, ticket: str, summary: str, timeout_ms: int) -> None:
    wait_for_condition(
        page,
        "jira ticket header visible",
        lambda: ticket in body_text(page)
        and summary in body_text(page)
        and any(status in body_text(page) for status in ["To Do", "In Progress", "Done", "In Review"]),
        timeout_ms,
    )


def jira_description_area(page: Page, metadata: dict[str, str], timeout_ms: int) -> None:
    required_tokens = [metadata.get("app", ""), metadata.get("env", ""), metadata.get("version", "")]
    wait_for_condition(
        page,
        "jira description content visible",
        lambda: "Description" in body_text(page)
        and all(token in body_text(page) for token in required_tokens if token)
        and any(label in body_text(page) for label in ["app:", "component:", "env:", "version:"]),
        timeout_ms,
    )


def jira_comments_area(page: Page, timeout_ms: int) -> None:
    wait_for_condition(
        page,
        "jira comments or activity visible",
        lambda: any(token in body_text(page) for token in ["Comments", "Activity", "History", "workflow_triggered", "completed"]),
        timeout_ms,
    )


def jira_progress_area(page: Page, timeout_ms: int) -> None:
    wait_for_condition(
        page,
        "jira progress comments visible",
        lambda: any(token in body_text(page) for token in JIRA_PROGRESS_KEYWORDS),
        timeout_ms,
    )


def scroll_jira_description(page: Page) -> str | None:
    return scroll_first_visible_text(page, ["Description", "app:", "component:", "env:", "version:"])


def scroll_jira_comments(page: Page) -> str | None:
    return scroll_first_visible_text(page, ["Comments", "Activity", "History", "completed", "failed"])


def scroll_jira_progress(page: Page) -> str | None:
    return scroll_first_visible_text(page, JIRA_PROGRESS_KEYWORDS + ["progress", "deployment result"])


def review_jira_ticket_pattern(summary: str, metadata: dict[str, str]) -> dict[str, object]:
    notes: list[str] = []
    recommendations: list[str] = []
    status = "PASS"

    normalized_summary = (summary or "").strip()
    if not normalized_summary:
        return {
            "status": "WARN",
            "summary": "Ticket summary is missing from the deployment evidence",
            "recommendations": ["Use a summary like 'Deploy LeninKart frontend to dev (v2)'."],
        }

    if not normalized_summary.lower().startswith("deploy"):
        status = "WARN"
        notes.append("Summary does not start with a clear deployment verb")
        recommendations.append("Start ticket summaries with 'Deploy ...' so intent is obvious in the UI.")
    if metadata.get("component") and metadata["component"] not in normalized_summary:
        status = "WARN"
        notes.append("Summary does not mention the target component")
        recommendations.append("Include the component name in the summary for faster scanning.")
    if metadata.get("env") and metadata["env"] not in normalized_summary:
        status = "WARN"
        notes.append("Summary does not mention the target environment")
        recommendations.append("Include the environment in the summary, for example 'to dev'.")

    required_order = ["app", "component", "env", "version"]
    missing = [field for field in required_order if not metadata.get(field)]
    if missing:
        status = "WARN"
        notes.append(f"Structured deployment metadata is missing: {', '.join(missing)}")
        recommendations.append("Keep app, component, env, and version in the description as explicit key-value lines.")

    if metadata.get("url"):
        notes.append("URL field is present, which helps connect the request to the target surface.")
    else:
        recommendations.append("Add a URL field when the request targets a user-facing route or API endpoint.")

    if status == "PASS":
        notes.append("Ticket summary and structured metadata already look presentation-ready.")

    preferred_template = [
        f"Summary: Deploy LeninKart {metadata.get('component', '<component>')} to {metadata.get('env', '<env>')} ({metadata.get('version', '<version>')})",
        "Description:",
        f"app: {metadata.get('app', 'leninkart')}",
        f"component: {metadata.get('component', '<component>')}",
        f"env: {metadata.get('env', '<env>')}",
        f"version: {metadata.get('version', '<version>')}",
        f"url: {metadata.get('url', 'http://dev.leninkart.local')}",
        "reason: validate the Jira -> GitHub Actions -> GitOps -> ArgoCD flow",
        "notes: created for demo or validation evidence",
    ]
    return {
        "status": status,
        "summary": "; ".join(notes) if notes else "No review notes",
        "recommendations": recommendations,
        "preferred_template": preferred_template,
    }


def github_run_summary(page: Page, workflow_name: str, timeout_ms: int) -> None:
    wait_for_condition(
        page,
        "github actions run summary visible",
        lambda: workflow_name in body_text(page)
        and "All jobs" in body_text(page)
        and "Filter by job status" in body_text(page),
        timeout_ms,
    )


def github_job_page(page: Page, runner_name: str, timeout_ms: int) -> None:
    wait_for_condition(
        page,
        "github job page visible",
        lambda: ("self-hosted" in body_text(page) or runner_name in body_text(page))
        and "deploy" in body_text(page),
        timeout_ms,
    )


def github_run_artifact(page: Page, artifact_name: str, timeout_ms: int) -> None:
    wait_for_text(page, "Artifacts", timeout_ms)
    wait_for_text(page, artifact_name, timeout_ms)
    scroll_first_visible_text(page, [artifact_name])
    wait_for_condition(
        page,
        "deployment result artifact visible",
        lambda: "Artifacts" in body_text(page) and artifact_name in body_text(page),
        timeout_ms,
    )


def github_commit_page(page: Page, commit_sha: str, values_path: str, timeout_ms: int) -> None:
    wait_for_text(page, commit_sha[:7], timeout_ms)
    wait_for_text(page, values_path, timeout_ms)


def argocd_deployment_detail(page: Page, app_name: str, revision: str, timeout_ms: int) -> None:
    wait_for_condition(
        page,
        "argocd application detail visible",
        lambda: app_name in body_text(page)
        and "Healthy" in body_text(page)
        and "Synced" in body_text(page)
        and revision[:7] in body_text(page),
        timeout_ms,
    )


def application_home(page: Page, title_hint: str, timeout_ms: int) -> None:
    wait_for_condition(
        page,
        "application home visible",
        lambda: title_hint in body_text(page) or "Login" in body_text(page) or "Create account" in body_text(page),
        timeout_ms,
    )
