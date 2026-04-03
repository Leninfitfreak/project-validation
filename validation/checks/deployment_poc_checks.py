from __future__ import annotations

import io
import json
import subprocess
import time
import zipfile
from pathlib import Path

import requests
import yaml
from playwright.sync_api import Page

from validation.core.config import ValidationConfig
from validation.core.shell import run as shell_run
from validation.core.waits import wait_for_condition, wait_for_text


SERVICE_ROOT_ENV = {
    'frontend': 'LENINKART_FRONTEND_ROOT',
    'product-service': 'LENINKART_PRODUCT_SERVICE_ROOT',
    'order-service': 'LENINKART_ORDER_SERVICE_ROOT',
}


def deployment_roots(config: ValidationConfig) -> tuple[Path, Path]:
    deployment_root = Path(config.env['DEPLOYMENT_POC_ROOT']).expanduser().resolve()
    gitops_root = Path(config.env['LENINKART_INFRA_ROOT']).expanduser().resolve()
    return deployment_root, gitops_root


def github_auth(config: ValidationConfig) -> tuple[str, str] | None:
    username = config.env.get('GITHUB_USERNAME', '').strip()
    password = config.env.get('GITHUB_PASSWORD_OR_TOKEN', '').strip()
    if username and password:
        return username, password

    proc = subprocess.run(
        ['git', 'credential', 'fill'],
        input='protocol=https\nhost=github.com\n\n',
        text=True,
        capture_output=True,
        check=False,
    )
    if proc.returncode != 0:
        return None

    creds: dict[str, str] = {}
    for line in proc.stdout.splitlines():
        if '=' not in line:
            continue
        key, value = line.split('=', 1)
        creds[key.strip()] = value.strip()
    if creds.get('username') and creds.get('password'):
        return creds['username'], creds['password']
    return None


def github_headers() -> dict[str, str]:
    return {
        'Accept': 'application/vnd.github+json',
        'X-GitHub-Api-Version': '2022-11-28',
    }


def api_get_json(url: str, auth: tuple[str, str] | None = None) -> dict:
    response = requests.get(url, headers=github_headers(), auth=auth, timeout=30)
    response.raise_for_status()
    return response.json()


def api_get_json_or_none(url: str, auth: tuple[str, str] | None = None) -> dict | None:
    response = requests.get(url, headers=github_headers(), auth=auth, timeout=30)
    if response.status_code == 404:
        return None
    response.raise_for_status()
    return response.json()


def download_deployment_payload(repo: str, artifact_id: int, auth: tuple[str, str] | None) -> dict:
    if auth is None:
        raise RuntimeError(
            'GitHub Actions artifact download requires authentication. '
            'Provide GITHUB_USERNAME/GITHUB_PASSWORD_OR_TOKEN locally or ensure a GitHub credential helper is configured.'
        )
    archive_url = f'https://api.github.com/repos/{repo}/actions/artifacts/{artifact_id}/zip'
    response = requests.get(archive_url, headers=github_headers(), auth=auth, timeout=60)
    response.raise_for_status()
    with zipfile.ZipFile(io.BytesIO(response.content)) as archive:
        return json.loads(archive.read('deployment-result.json').decode('utf-8-sig'))


def current_gitops_head(config: ValidationConfig) -> str | None:
    _, gitops_root = deployment_roots(config)
    result = shell_run(['git', 'rev-parse', f"origin/{config.env['DEPLOYMENT_POC_GITOPS_BRANCH']}"], cwd=gitops_root)
    if int(result['returncode']) != 0:
        return None
    return str(result['stdout']).strip() or None


def latest_successful_deployment_run(config: ValidationConfig) -> dict:
    repo = config.env['DEPLOYMENT_POC_REPO']
    workflow_file = config.env['DEPLOYMENT_POC_WORKFLOW_FILE']
    api_base = config.settings['defaults']['deployment_poc']['github_api_base']
    auth = github_auth(config)
    ticket_filter = config.env.get('DEPLOYMENT_POC_TICKET', '').strip()
    preferred_head = None if ticket_filter else current_gitops_head(config)

    runs_url = f'{api_base}/repos/{repo}/actions/workflows/{workflow_file}/runs?status=completed&per_page=20'
    runs = api_get_json(runs_url, auth=auth).get('workflow_runs', [])
    if not runs:
        raise RuntimeError(f'No completed workflow runs were returned for {workflow_file}')

    selected_fallback: dict | None = None

    for run_data in runs:
        if run_data.get('status') != 'completed' or run_data.get('conclusion') != 'success':
            continue
        run_id = int(run_data['id'])
        if not str(run_data.get('path', '')).endswith(workflow_file):
            continue

        artifacts = api_get_json(f'{api_base}/repos/{repo}/actions/runs/{run_id}/artifacts', auth=auth).get('artifacts', [])
        artifact = next((item for item in artifacts if item.get('name') == 'deployment-result' and not item.get('expired')), None)
        if artifact is None:
            continue

        payload = download_deployment_payload(repo, int(artifact['id']), auth=auth)
        if payload.get('outcome') != 'success':
            continue
        if ticket_filter and payload.get('jira_ticket') != ticket_filter:
            continue

        jobs = api_get_json(f'{api_base}/repos/{repo}/actions/runs/{run_id}/jobs', auth=auth).get('jobs', [])
        if not jobs:
            raise RuntimeError(f'No GitHub Actions jobs were returned for run {run_id}')
        job = jobs[0]
        candidate = {
            'run_id': run_id,
            'run_number': run_data.get('run_number'),
            'run_url': run_data.get('html_url'),
            'job_name': job.get('name'),
            'job_url': job.get('html_url'),
            'runner_name': job.get('runner_name'),
            'runner_group_name': job.get('runner_group_name'),
            'labels': job.get('labels', []),
            'steps': job.get('steps', []),
            'head_sha': run_data.get('head_sha'),
            'workflow_name': run_data.get('name'),
            'payload': payload,
            'artifact_path': f'github-actions://{repo}/runs/{run_id}/artifacts/{artifact["id"]}',
        }
        if preferred_head and payload.get('gitops_commit') == preferred_head:
            return candidate
        if selected_fallback is None:
            selected_fallback = candidate

    if selected_fallback is not None:
        return selected_fallback
    if ticket_filter:
        raise RuntimeError(f'No successful deployment-poc workflow run with deployment-result artifact was found for ticket {ticket_filter}')
    raise RuntimeError('No successful deployment-poc workflow run with deployment-result artifact was found')


def deployment_poc_latest_tags(config: ValidationConfig) -> dict:
    deployment_root, _ = deployment_roots(config)
    shell_run(['git', 'fetch', 'origin', config.env['DEPLOYMENT_POC_BRANCH']], cwd=deployment_root)
    latest_tags_path = config.settings['defaults']['deployment_poc']['latest_tags_file']
    payload = shell_run(
        ['git', 'show', f"origin/{config.env['DEPLOYMENT_POC_BRANCH']}:{latest_tags_path}"],
        cwd=deployment_root,
    )
    if int(payload['returncode']) != 0:
        raise RuntimeError(f"Unable to read {latest_tags_path} from origin/{config.env['DEPLOYMENT_POC_BRANCH']}: {payload['stderr']}")
    content = str(payload['stdout'])
    utf8_bom_bytes = ''.join(chr(code) for code in (0xEF, 0xBB, 0xBF))
    if content.startswith(utf8_bom_bytes):
        content = content[3:]
    content = content.lstrip('\ufeff')
    parsed = yaml.safe_load(content) or {}
    if 'services' not in parsed:
        parsed = {
            key.replace(utf8_bom_bytes, '').lstrip('\ufeff') if isinstance(key, str) else key: value
            for key, value in parsed.items()
        }
    return parsed


def service_ci_run_for_tag(config: ValidationConfig, app_key: str, image_tag: str) -> dict | None:
    service_cfg = ((config.settings['defaults']['deployment_poc'].get('service_ci', {}) or {}).get(app_key, {}) or {})
    repo = str(service_cfg.get('repo', '')).strip()
    workflow_file = str(service_cfg.get('workflow_file', '')).strip()
    if not repo or not workflow_file or not str(image_tag).isdigit():
        return None
    auth = github_auth(config)
    api_base = config.settings['defaults']['deployment_poc']['github_api_base']
    run_data = api_get_json_or_none(f'{api_base}/repos/{repo}/actions/runs/{image_tag}', auth=auth)
    if not run_data:
        return None
    if not str(run_data.get('path', '')).endswith(workflow_file):
        return None
    jobs = api_get_json(f'{api_base}/repos/{repo}/actions/runs/{image_tag}/jobs', auth=auth).get('jobs', [])
    job = jobs[0] if jobs else {}
    return {
        'repo': repo,
        'workflow_file': workflow_file,
        'workflow_name': run_data.get('name') or service_cfg.get('workflow_name', ''),
        'run_id': int(image_tag),
        'run_number': run_data.get('run_number'),
        'run_url': run_data.get('html_url'),
        'job_url': job.get('html_url', run_data.get('html_url')),
        'conclusion': run_data.get('conclusion'),
        'status': run_data.get('status'),
        'head_branch': run_data.get('head_branch'),
        'display_title': run_data.get('display_title') or run_data.get('name'),
    }


def validate_service_ci_metadata_contract(config: ValidationConfig, app_key: str) -> dict:
    root_path = Path(config.env[SERVICE_ROOT_ENV[app_key]]).expanduser().resolve()
    service_cfg = config.settings['defaults']['deployment_poc']['service_ci'][app_key]
    workflow_path = root_path / '.github' / 'workflows' / service_cfg['workflow_file']
    text = workflow_path.read_text(encoding='utf-8')
    has_control_repo = 'deployment-poc' in text and 'config/latest_tags.yaml' in text
    mutates_gitops = any(token in text for token in ['leninkart-infra', 'values-dev.yaml', 'values-staging.yaml', 'values-prod.yaml'])
    return {
        'workflow_path': str(workflow_path),
        'publishes_latest_tag_metadata': has_control_repo,
        'direct_gitops_update_removed': not mutates_gitops,
    }


def validate_consistency(config: ValidationConfig, summary: dict) -> dict:
    deployment_root, gitops_root = deployment_roots(config)
    payload = summary['payload']
    target = payload['target']
    deployment_settings = config.settings['defaults']['deployment_poc']
    expected_runner = deployment_settings.get('expected_runner_name', '')
    required_runner_labels = {label.casefold() for label in deployment_settings.get('required_runner_labels', [])}
    acceptable_actions = set(deployment_settings['acceptable_actions'])

    if payload.get('deployment_action') not in acceptable_actions:
        raise RuntimeError(f"Unexpected deployment action: {payload.get('deployment_action')}")
    if expected_runner and summary.get('runner_name') != expected_runner:
        raise RuntimeError(f"Deployment workflow used unexpected runner: {summary.get('runner_name')}")
    actual_labels = {str(label).casefold() for label in summary.get('labels', [])}
    missing_labels = sorted(required_runner_labels - actual_labels)
    if missing_labels:
        raise RuntimeError(f"Deployment workflow runner labels are incomplete: missing {', '.join(missing_labels)}")

    shell_run(['git', 'fetch', 'origin', config.env['DEPLOYMENT_POC_GITOPS_BRANCH']], cwd=gitops_root)
    gitops_head = shell_run(['git', 'rev-parse', f"origin/{config.env['DEPLOYMENT_POC_GITOPS_BRANCH']}"], cwd=gitops_root)
    values_file = shell_run(
        ['git', 'show', f"origin/{config.env['DEPLOYMENT_POC_GITOPS_BRANCH']}:{target['values_path']}"],
        cwd=gitops_root,
    )
    if int(values_file['returncode']) != 0:
        raise RuntimeError(f"Unable to read GitOps file {target['values_path']} from origin/{config.env['DEPLOYMENT_POC_GITOPS_BRANCH']}: {values_file['stderr']}")
    values_payload = yaml.safe_load(str(values_file['stdout']))
    current_tag = str(values_payload.get('image', {}).get('tag', '')).strip()

    app_json = shell_run(['kubectl', 'get', 'application', target['argocd_app'], '-n', 'argocd', '-o', 'json'])
    if int(app_json['returncode']) != 0:
        raise RuntimeError(f"kubectl get application failed: {app_json['stderr']}")
    app_payload = json.loads(str(app_json['stdout']))
    status = app_payload.get('status', {})
    sync_status = status.get('sync', {}).get('status')
    health_status = status.get('health', {}).get('status')
    revision = status.get('sync', {}).get('revision')

    if sync_status != 'Synced' or health_status != 'Healthy':
        raise RuntimeError(f"ArgoCD app {target['argocd_app']} is not healthy: sync={sync_status}, health={health_status}")
    if current_tag != target.get('resolved_version'):
        raise RuntimeError(f"GitOps values file {target['values_path']} does not match resolved version {target.get('resolved_version')}")

    current_head = gitops_head['stdout'].strip()
    requested_commit = str(payload.get('gitops_commit') or '').strip()
    revision_advanced = False
    if revision != requested_commit:
        ancestor_check = shell_run(['git', 'merge-base', '--is-ancestor', requested_commit, revision], cwd=gitops_root)
        if int(ancestor_check['returncode']) != 0 or current_tag != target.get('resolved_version'):
            raise RuntimeError(
                f"ArgoCD app {target['argocd_app']} revision mismatch: expected deployment commit {requested_commit} but live revision is {revision}"
            )
        revision_advanced = True
    if revision != current_head and current_tag != target.get('resolved_version'):
        raise RuntimeError(f"GitOps branch head mismatch: expected resolved version {target.get('resolved_version')} at head {current_head}")

    latest_tags_payload = deployment_poc_latest_tags(config)
    latest_tags_file = deployment_settings['latest_tags_file']
    latest_entry = (((latest_tags_payload.get('services', {}) or {}).get(target['app_key'], {}) or {}).get(target['environment'], {}) or {})
    latest_value = str(latest_entry.get('latest', '')).strip()

    version_source = str(target.get('version_source') or '').strip()
    resolved_version = str(target.get('resolved_version') or '').strip()
    latest_tag_matches_resolved = latest_value == resolved_version if version_source == 'latest_tag_metadata' else True

    service_ci_contract = validate_service_ci_metadata_contract(config, target['app_key'])
    if not service_ci_contract['publishes_latest_tag_metadata']:
        raise RuntimeError(f"Service CI workflow no longer shows latest tag metadata publishing for {target['app_key']}")
    if not service_ci_contract['direct_gitops_update_removed']:
        raise RuntimeError(f"Service CI workflow still appears to modify GitOps directly for {target['app_key']}")

    service_ci_run = service_ci_run_for_tag(config, target['app_key'], str(target.get('resolved_version') or ''))
    service_ci_run_found = service_ci_run is not None
    service_ci_run_success = not service_ci_run or service_ci_run.get('conclusion') == 'success'
    if service_ci_run and service_ci_run.get('conclusion') != 'success':
        raise RuntimeError(f"Service CI run for tag {target.get('resolved_version')} is not successful")

    expected_latest_service = str(config.env.get('LATEST_TAG_EXPECTED_SERVICE', '') or target['app_key']).strip()
    expected_latest_value = str(config.env.get('LATEST_TAG_EXPECTED_VALUE', '')).strip()
    expected_latest_match = True
    expected_service_ci_run = None
    if expected_latest_value and expected_latest_service == target['app_key']:
        expected_latest_match = latest_value == expected_latest_value
        expected_service_ci_run = service_ci_run_for_tag(config, target['app_key'], expected_latest_value)

    jira_progress = json.loads(str(payload.get('jira_progress_json') or '{}'))
    jira_feedback = json.loads(str(payload.get('jira_feedback_json') or '{}'))
    expected_progress_stages = [
        'workflow_triggered',
        'jira_validated',
        'target_resolved',
        'lock_acquired',
        'gitops_commit_pushed',
        'argocd_sync_started',
        'argocd_synced_healthy',
        'post_checks_completed',
        'completed',
    ]
    posted_stages = [
        str(item.get('stage') or '').strip()
        for item in jira_progress.get('posted_stages', [])
        if item.get('posted')
    ]
    missing_progress_stages = [stage for stage in expected_progress_stages if stage not in posted_stages]
    if missing_progress_stages:
        raise RuntimeError(f"Jira progress stages missing from deployment feedback: {', '.join(missing_progress_stages)}")

    jira_snapshot = jira_issue_snapshot(config, payload['jira_ticket'])
    jira_comment_blob = '\n\n'.join(jira_snapshot['comment_texts'])
    missing_comment_stages = [stage for stage in expected_progress_stages if stage not in jira_comment_blob]
    if missing_comment_stages:
        raise RuntimeError(f"Jira issue comments are missing lifecycle stages: {', '.join(missing_comment_stages)}")
    if 'Deployment result:' not in jira_comment_blob:
        raise RuntimeError('Jira issue comments are missing the final deployment result comment')

    jira_final_status = str(jira_feedback.get('final_status') or '').strip()
    if jira_final_status and jira_snapshot['status_name'] != jira_final_status:
        raise RuntimeError(
            f"Jira final status mismatch: workflow recorded {jira_final_status} but issue is {jira_snapshot['status_name']}"
        )
    if jira_feedback.get('comment_result') not in {'success', '', None}:
        raise RuntimeError(f"Jira final feedback comment failed: {jira_feedback.get('comment_result')}")
    if not bool(jira_feedback.get('policy_satisfied', False)):
        raise RuntimeError('Jira final feedback policy was not satisfied')

    deployment_root_fetch = shell_run(['git', 'fetch', 'origin', config.env['DEPLOYMENT_POC_BRANCH']], cwd=deployment_root)
    if int(deployment_root_fetch['returncode']) != 0:
        raise RuntimeError(f"Unable to fetch deployment-poc origin/{config.env['DEPLOYMENT_POC_BRANCH']}: {deployment_root_fetch['stderr']}")
    deployment_head = shell_run(['git', 'rev-parse', f"origin/{config.env['DEPLOYMENT_POC_BRANCH']}"], cwd=deployment_root)

    return {
        'gitops_head': current_head,
        'current_tag': current_tag,
        'argocd_sync': sync_status,
        'argocd_health': health_status,
        'argocd_revision': revision,
        'revision_advanced': revision_advanced,
        'version_source': version_source,
        'version_reference': str(target.get('version_reference') or ''),
        'image_repository': str(target.get('image_repository') or latest_entry.get('image', '') or '').strip(),
        'latest_tags_file': latest_tags_file,
        'latest_tag_value': latest_value,
        'latest_tag_matches_resolved': latest_tag_matches_resolved,
        'latest_tag_updated_at': str(latest_entry.get('updated_at', '')).strip(),
        'latest_tag_source_repo': str(latest_entry.get('source_repo', '')).strip(),
        'latest_tag_source_branch': str(latest_entry.get('source_branch', '')).strip(),
        'service_ci_contract': service_ci_contract,
        'service_ci_run': service_ci_run,
        'service_ci_run_found': service_ci_run_found,
        'service_ci_run_success': service_ci_run_success,
        'expected_latest_service': expected_latest_service,
        'expected_latest_value': expected_latest_value,
        'expected_latest_match': expected_latest_match,
        'expected_service_ci_run': expected_service_ci_run,
        'jira_ticket_url': jira_snapshot['issue_url'],
        'jira_issue_status': jira_snapshot['status_name'],
        'jira_comments_total': jira_snapshot['comments_total'],
        'jira_expected_progress_stages': expected_progress_stages,
        'jira_posted_progress_stages': posted_stages,
        'jira_missing_progress_stages': missing_progress_stages,
        'jira_missing_comment_stages': missing_comment_stages,
        'jira_feedback': jira_feedback,
        'deployment_poc_branch': config.env['DEPLOYMENT_POC_BRANCH'],
        'deployment_poc_head': str(deployment_head['stdout']).strip(),
    }


def github_run_summary(page: Page, workflow_name: str, timeout_ms: int) -> None:
    wait_for_condition(
        page,
        'github actions run summary visible',
        lambda: workflow_name in (page.text_content('body') or '')
        and 'All jobs' in (page.text_content('body') or '')
        and 'Filter by job status' in (page.text_content('body') or ''),
        timeout_ms,
    )


def github_commit_page(page: Page, commit_sha: str, values_path: str, timeout_ms: int) -> None:
    wait_for_text(page, commit_sha[:7], timeout_ms)
    wait_for_text(page, values_path, timeout_ms)


def argocd_deployment_detail(page: Page, app_name: str, revision: str, timeout_ms: int) -> None:
    wait_for_text(page, app_name, timeout_ms)
    wait_for_text(page, 'Healthy', timeout_ms)
    wait_for_text(page, 'Synced', timeout_ms)
    wait_for_condition(
        page,
        'frontend deployment revision visible',
        lambda: revision[:7] in (page.text_content('body') or ''),
        timeout_ms,
    )



def _truthy(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return str(value).strip().lower() in {'1', 'true', 'yes', 'on'}


def _looks_like_project_key(value: str) -> bool:
    trimmed = value.strip()
    return bool(trimmed) and len(trimmed) <= 15 and trimmed.replace('-', '').isalnum() and trimmed.upper() == trimmed


def jira_api_credentials(config: ValidationConfig) -> tuple[str, str, str]:
    base_url = str(config.env.get('JIRA_BASE_URL') or config.env.get('JIRA_URL') or '').strip().rstrip('/')
    email = str(config.env.get('JIRA_EMAIL') or config.env.get('JIRA_USERNAME') or '').strip()
    token = str(config.env.get('JIRA_API_TOKEN') or '').strip()
    if not token:
        fallback = str(config.env.get('JIRA_PROJECT_KEY') or '').strip()
        if fallback and not _looks_like_project_key(fallback):
            token = fallback
    if not base_url or not email or not token:
        raise RuntimeError('Jira API validation requires JIRA_BASE_URL/JIRA_URL, JIRA_EMAIL/JIRA_USERNAME, and JIRA_API_TOKEN or equivalent local token configuration')
    return base_url, email, token


def jira_validation_project_key(config: ValidationConfig) -> str:
    configured = str(config.env.get('JIRA_VALIDATION_PROJECT_KEY') or '').strip()
    if configured:
        return configured
    fallback = str(config.env.get('JIRA_PROJECT_KEY') or '').strip()
    if _looks_like_project_key(fallback):
        return fallback
    return 'SCRUM'


def jira_request(config: ValidationConfig, method: str, path: str, *, json_payload: dict | None = None) -> dict:
    base_url, email, token = jira_api_credentials(config)
    response = requests.request(
        method,
        f'{base_url}{path}',
        auth=(email, token),
        headers={'Accept': 'application/json', 'Content-Type': 'application/json'},
        json=json_payload,
        timeout=30,
    )
    if response.status_code == 401:
        raise RuntimeError('Jira API authentication failed during validation')
    response.raise_for_status()
    if not response.text.strip():
        return {}
    return response.json()


def jira_doc_to_text(value: dict | list | str | None) -> str:
    chunks: list[str] = []

    def walk(node: dict | list | str | None) -> None:
        if isinstance(node, str):
            if node.strip():
                chunks.append(node.strip())
            return
        if isinstance(node, list):
            for item in node:
                walk(item)
            return
        if isinstance(node, dict):
            text = str(node.get('text') or '').strip()
            if text:
                chunks.append(text)
            for item in node.get('content', []):
                walk(item)

    walk(value)
    return '\n'.join(chunks)


def jira_issue_snapshot(config: ValidationConfig, issue_key: str) -> dict:
    issue = jira_request(config, 'GET', f'/rest/api/3/issue/{issue_key}?fields=summary,status')
    comments_payload = jira_request(config, 'GET', f'/rest/api/3/issue/{issue_key}/comment')
    comments = comments_payload.get('comments', [])
    comment_texts = [jira_doc_to_text(item.get('body')) for item in comments]
    return {
        'issue_key': issue_key,
        'issue_url': f"{(config.env.get('JIRA_BASE_URL') or config.env.get('JIRA_URL') or '').rstrip('/')}/browse/{issue_key}",
        'summary': ((issue.get('fields') or {}).get('summary') or '').strip(),
        'status_name': (((issue.get('fields') or {}).get('status') or {}).get('name') or '').strip(),
        'comments_total': len(comments),
        'comment_texts': comment_texts,
    }


def create_validation_jira_ticket(config: ValidationConfig, app_key: str, requested_version: str, environment: str) -> dict:
    project_key = jira_validation_project_key(config)
    component = 'ui' if app_key == 'frontend' else 'backend'
    summary = f'Auto Validation - {app_key} {requested_version} deployment'
    description_lines = [
        f'app: {app_key}',
        f'env: {environment}',
        f'version: {requested_version}',
        f'component: {component}',
        'reason: automated end-to-end platform validation',
    ]
    payload = {
        'fields': {
            'project': {'key': project_key},
            'summary': summary,
            'issuetype': {'name': 'Task'},
            'description': {
                'type': 'doc',
                'version': 1,
                'content': [
                    {'type': 'paragraph', 'content': [{'type': 'text', 'text': line}]}
                    for line in description_lines
                ],
            },
        }
    }
    created = jira_request(config, 'POST', '/rest/api/3/issue', json_payload=payload)
    issue_key = str(created.get('key') or '').strip()
    if not issue_key:
        raise RuntimeError('Jira validation ticket creation did not return an issue key')
    snapshot = jira_issue_snapshot(config, issue_key)
    return {
        'key': issue_key,
        'url': snapshot['issue_url'],
        'summary': summary,
        'description': '\n'.join(description_lines),
        'status_name': snapshot['status_name'],
    }


def run_job_details(config: ValidationConfig, repo: str, run_id: int) -> dict:
    api_base = config.settings['defaults']['deployment_poc']['github_api_base']
    auth = github_auth(config)
    jobs = api_get_json(f'{api_base}/repos/{repo}/actions/runs/{run_id}/jobs', auth=auth).get('jobs', [])
    if not jobs:
        raise RuntimeError(f'No jobs were returned for {repo} run {run_id}')
    job = jobs[0]
    return {
        'job_name': job.get('name', ''),
        'job_url': job.get('html_url', ''),
        'runner_name': job.get('runner_name', ''),
        'runner_group_name': job.get('runner_group_name', ''),
        'labels': job.get('labels', []),
        'steps': job.get('steps', []),
    }


def latest_successful_workflow_run(config: ValidationConfig, repo: str, workflow_file: str, *, branch: str = '', per_page: int = 20) -> dict:
    for run_data in workflow_runs(config, repo, workflow_file, per_page=per_page):
        if run_data.get('status') != 'completed' or run_data.get('conclusion') != 'success':
            continue
        if branch and str(run_data.get('head_branch') or '') != branch:
            continue
        if not str(run_data.get('path', '')).endswith(workflow_file):
            continue
        details = run_job_details(config, repo, int(run_data['id']))
        return {
            'repo': repo,
            'workflow_file': workflow_file,
            'workflow_name': run_data.get('name', workflow_file),
            'run_id': int(run_data['id']),
            'run_number': run_data.get('run_number'),
            'run_url': run_data.get('html_url', ''),
            'head_branch': run_data.get('head_branch', ''),
            'head_sha': run_data.get('head_sha', ''),
            **details,
        }
    raise RuntimeError(f'No successful workflow run found for {repo}/{workflow_file} on branch {branch or "<any>"}')


def workflow_runs(config: ValidationConfig, repo: str, workflow_file: str, *, per_page: int = 20) -> list[dict]:
    api_base = config.settings['defaults']['deployment_poc']['github_api_base']
    auth = github_auth(config)
    url = f'{api_base}/repos/{repo}/actions/workflows/{workflow_file}/runs?per_page={per_page}'
    return api_get_json(url, auth=auth).get('workflow_runs', [])


def dispatch_workflow(config: ValidationConfig, repo: str, workflow_file: str, ref: str, inputs: dict[str, str | bool] | None = None) -> None:
    auth = github_auth(config)
    if auth is None:
        raise RuntimeError('GitHub workflow dispatch requires local GitHub credentials')
    api_base = config.settings['defaults']['deployment_poc']['github_api_base']
    response = requests.post(
        f'{api_base}/repos/{repo}/actions/workflows/{workflow_file}/dispatches',
        headers=github_headers(),
        auth=auth,
        json={'ref': ref, 'inputs': inputs or {}},
        timeout=30,
    )
    if response.status_code not in {200, 201, 204}:
        raise RuntimeError(f'GitHub workflow dispatch failed for {repo}/{workflow_file}: {response.status_code} {response.text}')


def wait_for_new_workflow_run(config: ValidationConfig, repo: str, workflow_file: str, existing_ids: set[int], *, branch: str, timeout_seconds: int = 300) -> dict:
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        for run_data in workflow_runs(config, repo, workflow_file, per_page=10):
            if int(run_data['id']) in existing_ids:
                continue
            if branch and str(run_data.get('head_branch') or '') != branch:
                continue
            if str(run_data.get('path', '')).endswith(workflow_file):
                return run_data
        time.sleep(5)
    raise RuntimeError(f'No new workflow run appeared for {repo}/{workflow_file}')


def wait_for_completed_workflow_run(config: ValidationConfig, repo: str, run_id: int, *, timeout_seconds: int = 3600) -> dict:
    api_base = config.settings['defaults']['deployment_poc']['github_api_base']
    auth = github_auth(config)
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        run_data = api_get_json(f'{api_base}/repos/{repo}/actions/runs/{run_id}', auth=auth)
        if run_data.get('status') == 'completed':
            return run_data
        time.sleep(10)
    raise RuntimeError(f'Workflow run {repo}/{run_id} did not complete in time')


def prepare_validation_run(config: ValidationConfig) -> dict:
    if str(config.env.get('DEPLOYMENT_POC_TICKET') or '').strip() or not _truthy(config.env.get('VALIDATION_TRIGGER_DEPLOYMENT'), default=True):
        return latest_successful_deployment_run(config)

    app_key = str(config.env.get('VALIDATION_TARGET_APP') or 'product-service').strip()
    environment = str(config.env.get('VALIDATION_TARGET_ENV') or 'dev').strip()
    requested_version = str(config.env.get('VALIDATION_REQUESTED_VERSION') or 'latest-dev').strip()
    service_cfg = ((config.settings['defaults']['deployment_poc'].get('service_ci', {}) or {}).get(app_key, {}) or {})

    orchestration: dict[str, object] = {
        'target_app': app_key,
        'environment': environment,
        'requested_version': requested_version,
    }

    if _truthy(config.env.get('VALIDATION_TRIGGER_SERVICE_CI'), default=True) and service_cfg:
        repo = str(service_cfg.get('repo') or '').strip()
        workflow_file = str(service_cfg.get('workflow_file') or '').strip()
        branch = 'main' if environment == 'prod' else environment
        existing_ids = {int(item['id']) for item in workflow_runs(config, repo, workflow_file, per_page=10)}
        dispatch_workflow(config, repo, workflow_file, branch)
        service_run = wait_for_new_workflow_run(config, repo, workflow_file, existing_ids, branch=branch, timeout_seconds=300)
        service_run = wait_for_completed_workflow_run(config, repo, int(service_run['id']), timeout_seconds=3600)
        if service_run.get('conclusion') != 'success':
            raise RuntimeError(f'Service CI workflow failed for {app_key}: {service_run.get("html_url")}')
        config.env['LATEST_TAG_EXPECTED_SERVICE'] = app_key
        config.env['LATEST_TAG_EXPECTED_VALUE'] = str(service_run['id'])
        orchestration['service_ci_run_id'] = int(service_run['id'])
        orchestration['service_ci_run_url'] = service_run.get('html_url', '')

    ticket = create_validation_jira_ticket(config, app_key, requested_version, environment)
    config.env['DEPLOYMENT_POC_TICKET'] = ticket['key']
    orchestration['jira_ticket'] = ticket

    repo = config.env['DEPLOYMENT_POC_REPO']
    workflow_file = config.env['DEPLOYMENT_POC_WORKFLOW_FILE']
    existing_ids = {int(item['id']) for item in workflow_runs(config, repo, workflow_file, per_page=10)}
    dispatch_workflow(
        config,
        repo,
        workflow_file,
        config.env['DEPLOYMENT_POC_BRANCH'],
        {
            'jira_ticket': ticket['key'],
            'trigger_argocd_sync': False,
            'test_mode': False,
            'rollback_to_last_success': False,
        },
    )
    deploy_run = wait_for_new_workflow_run(config, repo, workflow_file, existing_ids, branch=config.env['DEPLOYMENT_POC_BRANCH'], timeout_seconds=300)
    deploy_run = wait_for_completed_workflow_run(config, repo, int(deploy_run['id']), timeout_seconds=3600)
    if deploy_run.get('conclusion') != 'success':
        raise RuntimeError(f'deploy-from-jira workflow failed: {deploy_run.get("html_url")}')

    last_error = None
    for _ in range(24):
        try:
            summary = latest_successful_deployment_run(config)
            summary['orchestration'] = orchestration
            return summary
        except RuntimeError as exc:
            last_error = exc
            time.sleep(5)
    raise last_error or RuntimeError('deployment-result artifact did not become available in time')
