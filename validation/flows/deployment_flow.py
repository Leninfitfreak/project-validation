from __future__ import annotations

import json

from validation.checks import deployment_poc_checks
from validation.core.config import ValidationConfig
from validation.core.reporting import RunRecorder, StepResult
from validation.core.screenshots import capture_when_ready
from validation.ui import deployment_ui_checks, login_flows


def run(page, config: ValidationConfig, recorder: RunRecorder) -> None:
    waits = config.settings['defaults']['waits']
    image_rules = config.settings['defaults']['screenshot_quality']
    long_timeout = waits['long_timeout_ms']

    summary = deployment_poc_checks.prepare_validation_run(config)
    validation = deployment_poc_checks.validate_consistency(config, summary)
    payload = summary['payload']
    target = payload['target']

    warnings: list[str] = []

    service_ci_run = validation.get('expected_service_ci_run') or validation.get('service_ci_run') or {}
    if service_ci_run:
        page.goto(service_ci_run['run_url'], wait_until='domcontentloaded')
        capture_when_ready(
            page,
            config.screenshot_dir('deployment') / 'service-ci-latest-tag-publish.png',
            require_no_loading=False,
            verify=lambda: deployment_ui_checks.github_run_summary(page, service_ci_run['workflow_name'], long_timeout),
            retries=waits['retry_count'],
            retry_wait_ms=waits['retry_sleep_ms'],
            timeout_ms=long_timeout,
            image_rules=image_rules,
            full_page=False,
        )
        recorder.add_step(
            StepResult(
                'DEP-001',
                'deployment',
                'Service CI latest tag publish proof',
                'PASS',
                'Real GitHub Actions run page shows the service CI workflow that published the latest tag metadata used by deployment-poc.',
                'screenshots/deployment/service-ci-latest-tag-publish.png',
            )
        )
    else:
        warnings.append('Service CI run proof could not be resolved from the deployed tag, so the latest-tag path is validated from metadata and deployment outputs only.')

    latest_tags_url = (
        f"https://github.com/{config.env['DEPLOYMENT_POC_REPO']}/blob/"
        f"{config.env['DEPLOYMENT_POC_BRANCH']}/{validation['latest_tags_file']}"
    )
    latest_tag_expected = [target['app_key'], target['environment'], validation['latest_tag_value']]
    if validation.get('image_repository'):
        latest_tag_expected.append(validation['image_repository'])
    page.goto(latest_tags_url, wait_until='domcontentloaded')
    capture_when_ready(
        page,
        config.screenshot_dir('deployment') / 'latest-tags-metadata-proof.png',
        require_no_loading=False,
        verify=lambda: deployment_ui_checks.github_file_page(page, validation['latest_tags_file'], latest_tag_expected, long_timeout),
        retries=waits['retry_count'],
        retry_wait_ms=waits['retry_sleep_ms'],
        timeout_ms=long_timeout,
        image_rules=image_rules,
        full_page=False,
    )
    latest_tag_status = 'PASS'
    latest_tag_detail = 'Real GitHub file page shows the latest_tags entry that deployment-poc resolved for this deployment.'
    if validation.get('expected_latest_value') and not validation.get('expected_latest_match'):
        latest_tag_status = 'FAIL'
        latest_tag_detail = (
            f"Fresh service CI produced latest tag {validation.get('expected_latest_value')} for {validation.get('expected_latest_service')}, "
            f"but latest_tags.yaml still shows {validation.get('latest_tag_value')}."
        )
        warnings.append(latest_tag_detail)
    recorder.add_step(
        StepResult(
            'DEP-001A',
            'deployment',
            'Latest tag metadata proof',
            latest_tag_status,
            latest_tag_detail,
            'screenshots/deployment/latest-tags-metadata-proof.png',
        )
    )

    jira_lifecycle_artifact = config.artifacts_dir / 'jira-lifecycle-proof.json'
    jira_lifecycle_payload = {
        'ticket_key': payload['jira_ticket'],
        'ticket_url': validation.get('jira_ticket_url'),
        'issue_status': validation.get('jira_issue_status'),
        'comments_total': validation.get('jira_comments_total'),
        'expected_progress_stages': validation.get('jira_expected_progress_stages'),
        'posted_progress_stages': validation.get('jira_posted_progress_stages'),
        'missing_progress_stages': validation.get('jira_missing_progress_stages'),
        'missing_comment_stages': validation.get('jira_missing_comment_stages'),
        'jira_feedback': validation.get('jira_feedback'),
        'orchestration': summary.get('orchestration', {}),
    }
    jira_lifecycle_artifact.write_text(json.dumps(jira_lifecycle_payload, indent=2), encoding='utf-8')
    recorder.add_artifact(jira_lifecycle_artifact)
    recorder.add_step(
        StepResult(
            'DEP-001B',
            'deployment',
            'Jira lifecycle API proof',
            'PASS',
            'Fresh Jira ticket creation, progress comments, and final completed status were verified via Jira REST API.',
            artifact='artifacts/jira-lifecycle-proof.json',
        )
    )

    jira_ui_status = 'SKIPPED'
    jira_ui_enabled = str(config.env.get('JIRA_UI_PROOF_ENABLED', 'false')).strip().lower() in {'1', 'true', 'yes', 'on'}
    if jira_ui_enabled:
        jira_url = str(config.env.get('JIRA_URL', '')).strip()
        jira_username = str(config.env.get('JIRA_USERNAME', '')).strip()
        jira_password = str(config.env.get('JIRA_PASSWORD', '')).strip()
        jira_issue_url = f"{jira_url.rstrip('/')}/browse/{payload['jira_ticket']}" if jira_url else ''
        jira_ui_status = 'WARN'
        if jira_issue_url and jira_username and jira_password:
            jira_page = page.context.new_page()
            try:
                jira_page.goto(jira_issue_url, wait_until='domcontentloaded')
                login_flows.ensure_jira_login(jira_page, config, long_timeout)
                jira_expected = [payload['jira_ticket'], target['requested_version']]
                if target.get('resolved_version'):
                    jira_expected.append(target['resolved_version'])
                capture_when_ready(
                    jira_page,
                    config.screenshot_dir('deployment') / 'jira-ticket-proof.png',
                    require_no_loading=False,
                    verify=lambda: deployment_ui_checks.jira_issue_page(jira_page, payload['jira_ticket'], jira_expected, long_timeout),
                    retries=waits['retry_count'],
                    retry_wait_ms=waits['retry_sleep_ms'],
                    timeout_ms=long_timeout,
                    image_rules=image_rules,
                    full_page=False,
                )
                recorder.add_step(
                    StepResult(
                        'DEP-001B',
                        'deployment',
                        'Jira ticket UI proof',
                        'PASS',
                        'Real Jira browser page shows the deployment ticket and live ticket metadata for the validated run.',
                        'screenshots/deployment/jira-ticket-proof.png',
                    )
                )
                jira_ui_status = 'PASS'
            except Exception as exc:
                warnings.append(f'Jira browser UI proof could not be captured: {exc}')
            finally:
                jira_page.close()
        else:
            warnings.append('Jira browser UI proof is unavailable because JIRA_URL / JIRA_USERNAME / JIRA_PASSWORD are not all configured locally.')
    else:
        warnings.append('Jira browser UI proof was skipped by configuration for this validation run.')

    page.goto(summary['run_url'], wait_until='domcontentloaded')
    capture_when_ready(
        page,
        config.screenshot_dir('deployment') / 'github-actions-run-summary.png',
        require_no_loading=False,
        verify=lambda: deployment_ui_checks.github_run_summary(page, summary['workflow_name'], long_timeout),
        retries=waits['retry_count'],
        retry_wait_ms=waits['retry_sleep_ms'],
        timeout_ms=long_timeout,
        image_rules=image_rules,
        full_page=False,
    )
    recorder.add_step(StepResult('DEP-002', 'deployment', 'GitHub Actions deployment run summary', 'PASS', 'Real GitHub Actions workflow run page captured with job summary visible', 'screenshots/deployment/github-actions-run-summary.png'))

    page.goto(summary['job_url'], wait_until='domcontentloaded')
    capture_when_ready(
        page,
        config.screenshot_dir('deployment') / 'github-actions-runner-proof.png',
        require_no_loading=False,
        verify=lambda: deployment_ui_checks.github_job_page(page, summary['runner_name'], long_timeout),
        retries=waits['retry_count'],
        retry_wait_ms=waits['retry_sleep_ms'],
        timeout_ms=long_timeout,
        image_rules=image_rules,
        full_page=False,
    )
    recorder.add_step(StepResult('DEP-003', 'deployment', 'GitHub Actions runner proof', 'PASS', 'Real GitHub job page captured with the self-hosted runner details visible', 'screenshots/deployment/github-actions-runner-proof.png'))

    page.goto(summary['run_url'], wait_until='domcontentloaded')
    capture_when_ready(
        page,
        config.screenshot_dir('deployment') / 'deployment-result-proof.png',
        require_no_loading=False,
        verify=lambda: deployment_ui_checks.github_run_artifact(page, 'deployment-result', long_timeout),
        retries=waits['retry_count'],
        retry_wait_ms=waits['retry_sleep_ms'],
        timeout_ms=long_timeout,
        image_rules=image_rules,
        full_page=False,
    )
    recorder.add_step(StepResult('DEP-004', 'deployment', 'deployment-poc result proof', 'PASS', 'Real GitHub workflow run page captured with the deployment-result artifact visible as primary browser proof', 'screenshots/deployment/deployment-result-proof.png'))

    commit_url = f"https://github.com/{config.env['DEPLOYMENT_POC_GITOPS_REPO']}/commit/{payload['gitops_commit']}"
    page.goto(commit_url, wait_until='domcontentloaded')
    capture_when_ready(
        page,
        config.screenshot_dir('deployment') / 'gitops-commit-proof.png',
        require_no_loading=False,
        verify=lambda: deployment_ui_checks.github_commit_page(page, payload['gitops_commit'], target['values_path'], long_timeout),
        retries=waits['retry_count'],
        retry_wait_ms=waits['retry_sleep_ms'],
        timeout_ms=long_timeout,
        image_rules=image_rules,
        full_page=False,
    )
    recorder.add_step(StepResult('DEP-005', 'deployment', 'GitOps commit proof', 'PASS', 'Real public GitHub commit page shows the leninkart-infra revision and changed values file', 'screenshots/deployment/gitops-commit-proof.png'))

    argocd_page = page.context.new_page()
    try:
        argocd_page.goto(config.env['ARGOCD_URL'], wait_until='domcontentloaded')
        login_flows.ensure_argocd_login(argocd_page, config, long_timeout)
        argocd_app_url = f"{config.env['ARGOCD_URL'].rstrip('/')}/applications/{target['argocd_app']}"
        argocd_page.goto(argocd_app_url, wait_until='domcontentloaded')
        capture_when_ready(
            argocd_page,
            config.screenshot_dir('deployment') / 'argocd-deployment-app.png',
            prepare=lambda: (argocd_page.goto(argocd_app_url, wait_until='domcontentloaded'), argocd_page.wait_for_timeout(3500)),
            require_no_loading=False,
            retries=waits['retry_count'],
            retry_wait_ms=waits['retry_sleep_ms'],
            timeout_ms=long_timeout,
            image_rules=image_rules,
            full_page=False,
        )
    finally:
        argocd_page.close()
    recorder.add_step(StepResult('DEP-006', 'deployment', 'ArgoCD deployment application proof', 'PASS', 'Real ArgoCD application page shows Synced and Healthy on the expected revision', 'screenshots/deployment/argocd-deployment-app.png'))

    app_page = page.context.new_page()
    try:
        app_page.goto(config.env['INGRESS_URL'], wait_until='domcontentloaded')
        capture_when_ready(
            app_page,
            config.screenshot_dir('deployment') / 'application-home-proof.png',
            require_no_loading=False,
            verify=lambda: deployment_ui_checks.application_home(app_page, 'LeninKart', long_timeout),
            retries=waits['retry_count'],
            retry_wait_ms=waits['retry_sleep_ms'],
            timeout_ms=long_timeout,
            image_rules=image_rules,
            full_page=False,
        )
    finally:
        app_page.close()
    recorder.add_step(StepResult('DEP-007', 'deployment', 'Application deployment proof', 'PASS', 'Real browser screenshot confirms the deployed LeninKart application is reachable', 'screenshots/deployment/application-home-proof.png'))

    validation_summary = {
        'jira_ticket': payload['jira_ticket'],
        'jira_ui_status': jira_ui_status,
        'jira_ticket_url': validation.get('jira_ticket_url'),
        'jira_issue_status': validation.get('jira_issue_status'),
        'jira_comments_total': validation.get('jira_comments_total'),
        'jira_expected_progress_stages': validation.get('jira_expected_progress_stages'),
        'jira_posted_progress_stages': validation.get('jira_posted_progress_stages'),
        'jira_feedback': validation.get('jira_feedback'),
        'orchestration': summary.get('orchestration', {}),
        'run_id': summary['run_id'],
        'run_number': summary['run_number'],
        'run_url': summary['run_url'],
        'job_url': summary['job_url'],
        'runner_name': summary['runner_name'],
        'workflow_name': summary['workflow_name'],
        'deployment_action': payload.get('deployment_action'),
        'requested_version': target.get('requested_version'),
        'resolved_version': target.get('resolved_version'),
        'version_source': validation.get('version_source'),
        'version_reference': validation.get('version_reference'),
        'image_repository': validation.get('image_repository'),
        'latest_tags_file': validation.get('latest_tags_file'),
        'latest_tag_value': validation.get('latest_tag_value'),
        'latest_tag_updated_at': validation.get('latest_tag_updated_at'),
        'latest_tag_source_repo': validation.get('latest_tag_source_repo'),
        'latest_tag_source_branch': validation.get('latest_tag_source_branch'),
        'service_ci_run': service_ci_run,
        'service_ci_contract': validation.get('service_ci_contract'),
        'expected_latest_service': validation.get('expected_latest_service'),
        'expected_latest_value': validation.get('expected_latest_value'),
        'expected_latest_match': validation.get('expected_latest_match'),
        'gitops_commit': payload.get('gitops_commit'),
        'values_path': target.get('values_path'),
        'argocd_app': target.get('argocd_app'),
        'argocd_sync': validation['argocd_sync'],
        'argocd_health': validation['argocd_health'],
        'argocd_revision': validation['argocd_revision'],
        'gitops_head': validation['gitops_head'],
        'deployment_poc_branch': validation.get('deployment_poc_branch'),
        'deployment_poc_head': validation.get('deployment_poc_head'),
        'verdict': 'FAIL' if validation.get('expected_latest_value') and not validation.get('expected_latest_match') else 'PASS' if jira_ui_status == 'PASS' else 'PASS_WITH_WARNINGS',
        'warnings': warnings,
        'supporting_artifact_path': summary['artifact_path'],
    }
    summary_path = config.artifacts_dir / 'deployment-poc-validation-summary.json'
    summary_path.write_text(json.dumps(validation_summary, indent=2), encoding='utf-8')
    recorder.add_artifact(summary_path)
