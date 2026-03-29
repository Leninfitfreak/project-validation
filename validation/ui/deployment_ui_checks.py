from __future__ import annotations

from playwright.sync_api import Page

from validation.core.waits import wait_for_condition, wait_for_text
from validation.ui.playwright_helpers import body_text


def github_run_summary(page: Page, workflow_name: str, timeout_ms: int) -> None:
    wait_for_condition(
        page,
        'github actions run summary visible',
        lambda: workflow_name in body_text(page)
        and 'All jobs' in body_text(page)
        and 'Filter by job status' in body_text(page),
        timeout_ms,
    )


def github_job_page(page: Page, runner_name: str, timeout_ms: int) -> None:
    wait_for_condition(
        page,
        'github job page visible',
        lambda: ('self-hosted' in body_text(page) or runner_name in body_text(page))
        and 'deploy' in body_text(page).lower(),
        timeout_ms,
    )


def github_run_artifact(page: Page, artifact_name: str, timeout_ms: int) -> None:
    wait_for_text(page, 'Artifacts', timeout_ms)
    wait_for_text(page, artifact_name, timeout_ms)
    wait_for_condition(
        page,
        'deployment result artifact visible',
        lambda: 'Artifacts' in body_text(page) and artifact_name in body_text(page),
        timeout_ms,
    )


def github_commit_page(page: Page, commit_sha: str, values_path: str, timeout_ms: int) -> None:
    wait_for_text(page, commit_sha[:7], timeout_ms)
    wait_for_text(page, values_path, timeout_ms)


def github_file_page(page: Page, file_path: str, expected_texts: list[str], timeout_ms: int) -> None:
    wait_for_condition(
        page,
        'github file page visible',
        lambda: file_path in body_text(page)
        and all(text in body_text(page) for text in expected_texts if text),
        timeout_ms,
    )


def argocd_deployment_detail(page: Page, app_name: str, revision: str, timeout_ms: int) -> None:
    wait_for_condition(
        page,
        'argocd application page visible',
        lambda: app_name in body_text(page) and ('Application Details' in body_text(page) or 'Applications' in body_text(page)),
        timeout_ms,
    )


def application_home(page: Page, title_hint: str, timeout_ms: int) -> None:
    wait_for_condition(
        page,
        'application home visible',
        lambda: title_hint in body_text(page) or 'Login' in body_text(page) or 'Create account' in body_text(page),
        timeout_ms,
    )


def jira_issue_page(page: Page, issue_key: str, expected_texts: list[str], timeout_ms: int) -> None:
    wait_for_text(page, issue_key, timeout_ms)
    for text in expected_texts:
        if text:
            wait_for_text(page, text, timeout_ms)
