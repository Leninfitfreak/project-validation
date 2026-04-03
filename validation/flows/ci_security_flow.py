from __future__ import annotations

import json
from pathlib import Path

from validation.checks import deployment_poc_checks
from validation.core.reporting import RunRecorder, StepResult
from validation.core.screenshots import capture_when_ready
from validation.core.config import ValidationConfig


def _step_locator(page, step_name: str):
    return page.locator(f'check-step[data-name="{step_name}"]').first


def _find_step(run_details: dict, step_name: str) -> dict:
    for step in run_details.get('steps', []) or []:
        if str(step.get('name') or '').strip() == step_name:
            return step
    raise RuntimeError(f"Step '{step_name}' was not found in run {run_details.get('run_id')}")


def _ensure_step_success(run_details: dict, step_name: str) -> dict:
    step = _find_step(run_details, step_name)
    if str(step.get('conclusion') or '').lower() != 'success':
        raise RuntimeError(
            f"Step '{step_name}' did not succeed in run {run_details.get('run_id')}: {step.get('conclusion')}"
        )
    return step


def _open_job_step(page, run_details: dict, step_name: str, timeout_ms: int) -> None:
    page.goto(run_details['job_url'], wait_until='domcontentloaded', timeout=60000)
    page.wait_for_timeout(3000)
    page.evaluate(
        """
        (name) => {
          const details = document.querySelector(`check-step[data-name="${name}"] details`);
          if (details) {
            details.setAttribute('open', '');
          }
        }
        """,
        step_name,
    )
    locator = _step_locator(page, step_name)
    locator.wait_for(state='visible', timeout=timeout_ms)
    locator.scroll_into_view_if_needed(timeout=timeout_ms)
    page.wait_for_timeout(1500)


def _github_job_step_verify(page, step_name: str, timeout_ms: int) -> None:
    locator = _step_locator(page, step_name)
    locator.wait_for(state='visible', timeout=timeout_ms)


def run(page, config: ValidationConfig, recorder: RunRecorder) -> None:
    waits = config.settings['defaults']['waits']
    image_rules = config.settings['defaults']['screenshot_quality']
    ci_image_rules = dict(image_rules)
    ci_image_rules.update({'min_unique_colors': 8, 'min_stddev': 2.0, 'max_dominant_ratio': 0.9995})
    timeout_ms = waits['long_timeout_ms']
    app_key = str(config.env.get('VALIDATION_TARGET_APP') or 'product-service').strip()
    environment = str(config.env.get('VALIDATION_TARGET_ENV') or 'dev').strip()

    latest_tags = deployment_poc_checks.deployment_poc_latest_tags(config)
    latest_entry = (((latest_tags.get('services', {}) or {}).get(app_key, {}) or {}).get(environment, {}) or {})
    latest_value = str(latest_entry.get('latest', '')).strip()
    if not latest_value:
        raise RuntimeError(f'No latest_tags entry found for {app_key}/{environment}')

    service_run = deployment_poc_checks.service_ci_run_for_tag(config, app_key, latest_value)
    if not service_run:
        raise RuntimeError(f'Unable to resolve service CI run for {app_key} tag {latest_value}')
    if str(service_run.get('conclusion') or '').lower() != 'success':
        raise RuntimeError(f"Service CI run {service_run.get('run_id')} is not successful")
    service_run.update(deployment_poc_checks.run_job_details(config, service_run['repo'], int(service_run['run_id'])))

    sonar_step = _ensure_step_success(service_run, 'Run SonarQube scan')
    quality_gate_step = _ensure_step_success(service_run, 'Await SonarQube quality gate')

    quality_workflow = deployment_poc_checks.latest_successful_workflow_run(
        config,
        service_run['repo'],
        'quality-security.yml',
        branch=service_run.get('head_branch', '') or environment,
        per_page=20,
    )
    gitleaks_step = _ensure_step_success(quality_workflow, 'Run Gitleaks secret scan')

    ci_dir = config.root / 'screenshots' / 'ci'
    ci_dir.mkdir(parents=True, exist_ok=True)

    _open_job_step(page, service_run, 'Run SonarQube scan', timeout_ms)
    capture_when_ready(
        page,
        ci_dir / 'ci-sonarqube-scan.png',
        require_no_loading=False,
        verify=lambda: _github_job_step_verify(page, 'Run SonarQube scan', timeout_ms),
        retries=waits['retry_count'],
        retry_wait_ms=waits['retry_sleep_ms'],
        timeout_ms=timeout_ms,
        image_rules=ci_image_rules,
        full_page=False,
    )
    recorder.add_step(
        StepResult(
            'CI-001',
            'ci',
            'SonarQube scan proof',
            'PASS',
            f"Service CI run {service_run['run_id']} shows the SonarQube scan step completed successfully for {app_key}.",
            'screenshots/ci/ci-sonarqube-scan.png',
        )
    )

    _open_job_step(page, service_run, 'Await SonarQube quality gate', timeout_ms)
    capture_when_ready(
        page,
        ci_dir / 'ci-sonarqube-quality-gate.png',
        require_no_loading=False,
        verify=lambda: _github_job_step_verify(page, 'Await SonarQube quality gate', timeout_ms),
        retries=waits['retry_count'],
        retry_wait_ms=waits['retry_sleep_ms'],
        timeout_ms=timeout_ms,
        image_rules=ci_image_rules,
        full_page=False,
    )
    recorder.add_step(
        StepResult(
            'CI-002',
            'ci',
            'SonarQube quality gate proof',
            'PASS',
            f"Service CI run {service_run['run_id']} shows the SonarQube quality gate step completed successfully for {app_key}.",
            'screenshots/ci/ci-sonarqube-quality-gate.png',
        )
    )

    _open_job_step(page, quality_workflow, 'Run Gitleaks secret scan', timeout_ms)
    capture_when_ready(
        page,
        ci_dir / 'ci-gitleaks-scan.png',
        require_no_loading=False,
        verify=lambda: _github_job_step_verify(page, 'Run Gitleaks secret scan', timeout_ms),
        retries=waits['retry_count'],
        retry_wait_ms=waits['retry_sleep_ms'],
        timeout_ms=timeout_ms,
        image_rules=ci_image_rules,
        full_page=False,
    )
    recorder.add_step(
        StepResult(
            'CI-003',
            'ci',
            'Gitleaks scan proof',
            'PASS',
            f"Companion quality-security run {quality_workflow['run_id']} shows the Gitleaks scan step completed successfully for {app_key}.",
            'screenshots/ci/ci-gitleaks-scan.png',
        )
    )

    summary = {
        'service_name': app_key,
        'environment': environment,
        'ci_run_id': service_run['run_id'],
        'ci_run_url': service_run['run_url'],
        'quality_security_run_id': quality_workflow['run_id'],
        'quality_security_run_url': quality_workflow['run_url'],
        'latest_tag_value': latest_value,
        'sonarqube_scan': {
            'status': 'PASS',
            'step': sonar_step,
            'screenshot': 'screenshots/ci/ci-sonarqube-scan.png',
        },
        'quality_gate': {
            'status': 'PASS',
            'step': quality_gate_step,
            'screenshot': 'screenshots/ci/ci-sonarqube-quality-gate.png',
        },
        'gitleaks': {
            'status': 'PASS',
            'step': gitleaks_step,
            'run_id': quality_workflow['run_id'],
            'run_url': quality_workflow['run_url'],
            'screenshot': 'screenshots/ci/ci-gitleaks-scan.png',
        },
        'implementation_note': 'SonarQube proof is taken from the metadata-linked ci-cd run; Gitleaks proof is taken from the latest successful companion quality-security workflow for the same service and branch.',
    }
    target = config.artifacts_dir / 'ci-security-validation-summary.json'
    target.write_text(json.dumps(summary, indent=2), encoding='utf-8')
    recorder.add_artifact(target)
    config.env['VALIDATION_TRIGGER_SERVICE_CI'] = 'false'
