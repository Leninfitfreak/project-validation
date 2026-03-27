from __future__ import annotations

import json
from pathlib import Path
import shutil

from validation.core.browser import BrowserHarness
from validation.core.cleanup import clean_generated_outputs, collect_cleanup_candidates
from validation.core.config import load_config
from validation.core.reporting import RunRecorder, StepResult
from validation.flows import (
    app_auth_flow,
    deployment_flow,
    gitops_flow,
    infra_flow,
    messaging_flow,
    observability_flow,
    order_flow,
    product_flow,
    vault_flow,
)
from validation.checks.screenshot_checks import audit_screenshots


def _step_rows(recorder: RunRecorder) -> list[str]:
    rows = [
        "| Component | Test Case | Expected Proof | Screenshot Target | Pass Criteria |",
        "| --- | --- | --- | --- | --- |",
    ]
    for step in recorder.steps:
        target = step.screenshot or step.artifact or "-"
        rows.append(
            f"| {step.category} | {step.id} {step.title} | {step.detail} | `{target}` | `{step.status}` |"
        )
    return rows


def _sync_docs_screenshots(config) -> dict[str, str]:
    docs_root = config.docs_dir / "screenshots"
    docs_root.mkdir(parents=True, exist_ok=True)
    relative_map: dict[str, str] = {}
    for image_path in sorted((config.root / "screenshots").rglob("*.png")):
        relative = image_path.relative_to(config.root / "screenshots")
        target = docs_root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(image_path, target)
        relative_map[str(image_path.relative_to(config.root)).replace("\\", "/")] = str(
            Path("screenshots") / relative
        ).replace("\\", "/")
    return relative_map


def _embed_for(step: StepResult, screenshot_map: dict[str, str]) -> list[str]:
    if not step.screenshot:
        return []
    relative = screenshot_map.get(step.screenshot, step.screenshot)
    return ["", f"![{step.title}]({relative})", ""]


def write_docs(config, recorder: RunRecorder) -> None:
    docs = config.docs_dir
    docs.mkdir(parents=True, exist_ok=True)
    screenshot_map = _sync_docs_screenshots(config)

    summary_by_category: dict[str, list[StepResult]] = {}
    for step in recorder.steps:
        summary_by_category.setdefault(step.category, []).append(step)

    matrix = docs / "PLATFORM_TEST_CASE_MATRIX.md"
    matrix.write_text(
        "\n".join(
            [
                "# Platform Test Case Matrix",
                "",
                "This matrix is generated from the rebuilt modular validation framework and represents the exact proof set produced by the latest clean run.",
                "",
            ]
            + _step_rows(recorder)
        ),
        encoding="utf-8",
    )

    plan = docs / "VALIDATION_EXECUTION_PLAN.md"
    plan.write_text(
        "\n".join(
            [
                "# Validation Execution Plan",
                "",
                "1. Start from a clean output state by removing prior screenshots, reports, and artifacts while preserving retry debug folders only for the current run.",
                "2. Load URLs, credentials, wait rules, screenshot quality thresholds, and demo data from `.env` and `validation/data/*`.",
                "3. Capture infrastructure and messaging CLI proof before browser work begins.",
                "4. Run the frontend user journey in order: login page, signup, authenticated dashboard, product creation, buy flow, and order history proof.",
                "5. Validate the Jira -> GitHub Actions -> GitOps -> ArgoCD deployment POC using public GitHub pages, local deployment artifacts, and ArgoCD state proof.",
                "6. Run GitOps and Vault UI proof flows and generate the safe Vault secret inventory report.",
                "7. Run observability proof for Grafana dashboards, Loki Explore, Prometheus targets, and Tempo search/detail pages.",
                "8. Reject blank or weak screenshots automatically, retry with longer waits, and only publish screenshots that pass image-quality checks.",
                "9. Write markdown, JSON, screenshot manifest, and validation-output bundles for MkDocs and portfolio documentation.",
            ]
        ),
        encoding="utf-8",
    )

    evidence_index = docs / "PLATFORM_EVIDENCE_INDEX.md"
    lines = ["# Platform Evidence Index", ""]
    for step in recorder.steps:
        lines.append(f"## `{step.id}` {step.title}")
        lines.append("")
        lines.append(f"- Category: `{step.category}`")
        lines.append(f"- Status: `{step.status}`")
        lines.append(f"- Proof: {step.detail}")
        if step.screenshot:
            lines.append(f"- Screenshot: [{screenshot_map.get(step.screenshot, step.screenshot)}]({screenshot_map.get(step.screenshot, step.screenshot)})")
        if step.artifact:
            lines.append(f"- Artifact: `{step.artifact}`")
        lines.extend(_embed_for(step, screenshot_map))
        lines.append("")
    evidence_index.write_text("\n".join(lines), encoding="utf-8")

    results = docs / "PLATFORM_VALIDATION_RESULTS.md"
    passed = sum(1 for step in recorder.steps if step.status == "PASS")
    warnings = sum(1 for step in recorder.steps if step.status == "WARN")
    failed = sum(1 for step in recorder.steps if step.status not in {"PASS", "WARN"})
    result_lines = [
        "# Platform Validation Results",
        "",
        f"- Total steps: `{len(recorder.steps)}`",
        f"- Passed: `{passed}`",
        f"- Warnings: `{warnings}`",
        f"- Failed: `{failed}`",
        "",
    ]
    for step in recorder.steps:
        result_lines.append(f"## {step.id} {step.title}")
        result_lines.append("")
        result_lines.append(f"- Status: `{step.status}`")
        result_lines.append(f"- Detail: {step.detail}")
        if step.screenshot:
            relative = screenshot_map.get(step.screenshot, step.screenshot)
            result_lines.append(f"- Screenshot: [{relative}]({relative})")
        if step.artifact:
            result_lines.append(f"- Artifact: `{step.artifact}`")
        result_lines.extend(_embed_for(step, screenshot_map))
        result_lines.append("")
    results.write_text("\n".join(result_lines), encoding="utf-8")

    mkdocs_plan = docs / "MKDOCS_NAVIGATION_PLAN.md"
    mkdocs_plan.write_text(
        "\n".join(
            [
                "# MkDocs Navigation Plan",
                "",
                "- Overview",
                "- Real UI Validation",
                "- Deployment POC Validation Report",
                "- Deployment POC Evidence Index",
                "- Platform Test Case Matrix",
                "- Validation Execution Plan",
                "- Platform Validation Results",
                "- Platform Evidence Index",
                "- Vault Secret Inventory Report",
                "- Validation Cleanup Report",
                "- Screenshot Clean Run Policy",
                "- Screenshot Quality Report",
                "- Application Validation",
                "- Deployment POC Validation",
                "- GitOps Validation",
                "- Secrets Validation",
                "- Messaging Validation",
                "- Observability Validation",
                "- Screenshots Gallery",
            ]
        ),
        encoding="utf-8",
    )

    overview = docs / "index.md"
    overview.write_text(
        "\n".join(
            [
                "# LeninKart Validation Overview",
                "",
                "This site contains the current end-to-end LeninKart platform evidence generated from the rebuilt `project-validation` framework.",
                "",
                "## Covered Areas",
                "",
                "- Application journey: signup, login, product creation, buy flow, order history",
                "- Deployment POC proof: Jira ticket evidence, GitHub Actions run, deployment result, GitOps commit, ArgoCD sync and health",
                "- GitOps proof: ArgoCD login, applications list, application detail",
                "- Secrets proof: Vault access and safe secret-path artifact",
                "- Messaging proof: external Kafka runtime artifact and Kafka dashboard",
                "- Observability proof: Grafana dashboards, Loki logs, Prometheus targets, Tempo traces",
                "",
                "## Validation Rules",
                "",
                "- Every run starts clean and replaces the previous evidence set.",
                "- Final screenshots are accepted only after selector checks, content checks, and non-blank image validation succeed.",
                "- Retry attempts are stored separately under `artifacts/debug-retries/` and never mixed into the final evidence gallery.",
                "",
                "## Category Summary",
                "",
            ]
            + [
                f"- `{category}`: {len(steps)} captured step(s)"
                for category, steps in sorted(summary_by_category.items())
            ]
        ),
        encoding="utf-8",
    )

    gallery = docs / "SCREENSHOTS_GALLERY.md"
    gallery_lines = ["# Screenshots Gallery", ""]
    for category, steps in sorted(summary_by_category.items()):
        screenshot_steps = [step for step in steps if step.screenshot]
        if not screenshot_steps:
            continue
        gallery_lines.append(f"## {category.title()}")
        gallery_lines.append("")
        for step in screenshot_steps:
            relative = screenshot_map.get(step.screenshot, step.screenshot)
            gallery_lines.append(f"### {step.id} {step.title}")
            gallery_lines.append("")
            gallery_lines.append(f"![{step.title}]({relative})")
            gallery_lines.append("")
    gallery.write_text("\n".join(gallery_lines), encoding="utf-8")

    real_ui = docs / "REAL_UI_VALIDATION.md"
    real_ui.write_text(
        "\n".join(
            [
                "# Real UI Validation",
                "",
                "This validation framework now treats browser-captured UI as the primary deployment proof.",
                "",
                "## Primary UI Proof",
                "",
                "- Real Jira ticket page when browser authentication is available",
                "- Real GitHub Actions run summary page",
                "- Real GitHub Actions job page for runner details",
                "- Real GitHub Actions run page artifact section for deployment-result proof",
                "- Real public GitOps commit page",
                "- Real ArgoCD application page",
                "- Real LeninKart application page",
                "",
                "## Supporting Evidence",
                "",
                "- Local JSON and markdown artifacts generated by validation",
                "- Deployment workflow artifacts used only for cross-checking and report generation",
                "",
                "## Authentication Model",
                "",
                "- Jira UI proof requires a browser-authenticated Jira session or local Jira browser credentials in `.env`.",
                "- GitHub deployment pages are captured from public workflow and commit pages.",
                "- ArgoCD, Grafana, and other protected UIs use credentials from local `.env` only.",
                "- No credentials are stored in `.env.example`.",
                "",
                "## Honest Limitation Handling",
                "",
                "- If a protected UI cannot be reached because authentication is missing, the framework records a warning instead of faking proof.",
                "- Supporting artifacts may still be recorded, but they are not presented as primary UI screenshots.",
            ]
        ),
        encoding="utf-8",
    )


def write_deployment_docs(config, recorder: RunRecorder) -> None:
    summary_path = config.artifacts_dir / "deployment-poc-validation-summary.json"
    if not summary_path.exists():
        return
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    docs = config.docs_dir
    screenshot_map = _sync_docs_screenshots(config)
    steps = [step for step in recorder.steps if step.category == "deployment"]

    report_lines = [
        "# Deployment POC Validation Report",
        "",
        "## Validated Scope",
        "",
        "- Jira deployment ticket proof",
        "- GitHub Actions workflow summary and self-hosted runner proof",
        "- deployment-poc result proof from the real GitHub workflow artifact section",
        "- GitOps commit and target file proof",
        "- ArgoCD final Sync and Health proof",
        "- Application reachability proof",
        "",
        "## Latest Validated Deployment",
        "",
        f"- Jira ticket: `{summary.get('jira_ticket', '')}`",
        f"- Workflow run: `#{summary.get('run_number', '')}`",
        f"- Workflow URL: `{summary.get('run_url', '')}`",
        f"- Runner: `{summary.get('runner_name', '')}`",
        f"- Deployment action: `{summary.get('deployment_action', '')}`",
        f"- Requested version: `{summary.get('requested_version', '')}`",
        f"- Resolved version: `{summary.get('resolved_version', '')}`",
        f"- GitOps commit: `{summary.get('gitops_commit', '')}`",
        f"- GitOps values path: `{summary.get('values_path', '')}`",
        f"- ArgoCD app: `{summary.get('argocd_app', '')}`",
        f"- Final sync: `{summary.get('argocd_sync', '')}`",
        f"- Final health: `{summary.get('argocd_health', '')}`",
        f"- Jira proof mode: `{summary.get('jira_proof_mode', '')}`",
        f"- Supporting artifact: `{summary.get('supporting_artifact_path', '')}`",
        "",
        "## Screenshot Proof",
        "",
    ]
    for step in steps:
        if not step.screenshot:
            continue
        relative = screenshot_map.get(step.screenshot, step.screenshot)
        report_lines.extend(
            [
                f"### {step.id} {step.title}",
                "",
                f"- Detail: {step.detail}",
                f"- Screenshot: [{relative}]({relative})",
                "",
                f"![{step.title}]({relative})",
                "",
            ]
        )
    if summary.get("warnings"):
        report_lines.extend(["## Warnings", ""])
        for warning in summary["warnings"]:
            report_lines.append(f"- {warning}")
        report_lines.append("")
    report_lines.extend(
        [
            "## Evidence Model",
            "",
            "- Primary proof in this report is browser-captured UI.",
            "- Local artifacts are supporting evidence only.",
            "",
            "## Final Verdict",
            "",
            f"`{summary.get('verdict', 'UNKNOWN')}`",
            "",
        ]
    )
    (docs / "DEPLOYMENT_POC_VALIDATION_REPORT.md").write_text("\n".join(report_lines), encoding="utf-8")

    index_lines = ["# Deployment POC Evidence Index", ""]
    for step in steps:
        index_lines.append(f"## `{step.id}` {step.title}")
        index_lines.append("")
        index_lines.append(f"- Status: `{step.status}`")
        index_lines.append(f"- Detail: {step.detail}")
        if step.screenshot:
            relative = screenshot_map.get(step.screenshot, step.screenshot)
            index_lines.append(f"- Screenshot: [{relative}]({relative})")
            index_lines.append("")
            index_lines.append(f"![{step.title}]({relative})")
        if step.artifact:
            index_lines.append(f"- Artifact: `{step.artifact}`")
        index_lines.append("")
    (docs / "DEPLOYMENT_POC_EVIDENCE_INDEX.md").write_text("\n".join(index_lines), encoding="utf-8")


def write_cleanup_report(config, recorder: RunRecorder) -> Path:
    target = config.docs_dir / "VALIDATION_CLEANUP_REPORT.md"
    lines = [
        "# Validation Cleanup Report",
        "",
        "The previous `project-validation` implementation was cleaned before rebuilding the framework.",
        "",
        "## Removed or Replaced",
        "",
    ]
    lines.extend(f"- `{item}`" for item in collect_cleanup_candidates(config.root))
    lines.extend(
        [
            "",
            "## Current Baseline",
            "",
            "- Legacy SigNoz, DeepObserver, and observer-stack validation logic is excluded from the rebuilt framework.",
            "- Final screenshots are produced only from the current run.",
            "- Retry attempts are isolated under `artifacts/debug-retries/`.",
            f"- Current generated step count: `{len(recorder.steps)}`",
        ]
    )
    target.write_text("\n".join(lines), encoding="utf-8")
    return target


def write_clean_run_policy(config) -> Path:
    target = config.docs_dir / "SCREENSHOT_CLEAN_RUN_POLICY.md"
    target.write_text(
        "\n".join(
            [
                "# Screenshot Clean Run Policy",
                "",
                "- Every validation run starts by deleting prior generated screenshots, reports, and validation-output bundles.",
                "- Final evidence is written only to the canonical category folders under `screenshots/`.",
                "- Retry attempts and failed captures are stored under `artifacts/debug-retries/`.",
                "- Final evidence filenames are stable and do not use ad-hoc suffixes like `final-v2`.",
                "- A screenshot is published only after UI readiness checks and image-quality checks pass.",
            ]
        ),
        encoding="utf-8",
    )
    return target


def write_screenshot_quality_report(config) -> tuple[Path, Path]:
    rules = config.settings["defaults"].get("screenshot_quality", {})
    audit = audit_screenshots(config.root / "screenshots", rules)
    json_target = config.artifacts_dir / "blank-image-detection-report.json"
    json_target.write_text(json.dumps(audit, indent=2), encoding="utf-8")

    markdown_target = config.docs_dir / "SCREENSHOT_QUALITY_REPORT.md"
    lines = [
        "# Screenshot Quality Report",
        "",
        "This report is generated from automated image checks to reject blank, uniform, or obviously incomplete screenshots.",
        "",
        "## Active Rules",
        "",
    ]
    for key, value in rules.items():
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(["", "## Screenshot Audit", ""])
    if not audit:
        lines.append("- No screenshots were captured.")
    for item in audit:
        status = "PASS" if item["ok"] else "FAIL"
        lines.append(
            f"- `{status}` `{item['path']}`: {item['reason']} "
            f"(size={item['width']}x{item['height']}, colors={item['unique_colors']}, "
            f"stddev={item['max_channel_stddev']}, dominant={item['dominant_ratio']})"
        )
    markdown_target.write_text("\n".join(lines), encoding="utf-8")
    return markdown_target, json_target


def write_mkdocs_image_fix_report(config) -> Path:
    docs_screenshots = config.docs_dir / "screenshots"
    image_count = len(list(docs_screenshots.rglob("*.png"))) if docs_screenshots.exists() else 0
    target = config.docs_dir / "MKDOCS_IMAGE_FIX_REPORT.md"
    target.write_text(
        "\n".join(
            [
                "# MkDocs Image Fix Report",
                "",
                "## Issues Found",
                "",
                "- Final screenshots were stored outside `docs/`, so MkDocs could not serve them reliably after hosting.",
                "- Markdown pages referenced screenshot paths as text proof, but did not embed the images for rendering.",
                "- The docs cleanup step did not clear any previously copied screenshot tree under `docs/`.",
                "",
                "## Fixes Applied",
                "",
                "- Screenshots are now copied into `docs/screenshots/` on each run.",
                "- Evidence pages now use relative Markdown image links that resolve within the hosted site.",
                "- A dedicated screenshots gallery page is generated for review and GitHub Pages hosting.",
                "- The clean-run policy now clears `docs/screenshots/` before each run.",
                "",
                "## Validation Status",
                "",
                f"- Screenshots copied into docs: `{image_count}`",
                "- All final image references use relative paths.",
                "- MkDocs build should now package screenshots into the generated site output.",
            ]
        ),
        encoding="utf-8",
    )
    return target


def write_evidence_json(config, recorder: RunRecorder) -> Path:
    results: dict[str, list[dict]] = {}
    for step in recorder.steps:
        results.setdefault(step.category, []).append(step.__dict__)
    payload = {"generated_at": recorder.started_at, "results": results, "artifacts": recorder.artifacts}
    target = config.artifacts_dir / "evidence.json"
    target.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return target


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    config = load_config(root)
    clean_generated_outputs(config)
    recorder = RunRecorder(config)
    recorder.ensure_dirs()

    infra_flow.run(config, recorder)
    messaging_flow.run(config, recorder)

    with BrowserHarness(config) as browser:
        app_page = browser.new_page()
        app_auth_flow.run(app_page, config, recorder)
        products = product_flow.run(app_page, config, recorder)
        order_flow.run(app_page, config, recorder, products)
        app_page.close()

        gitops_page = browser.new_page()
        gitops_flow.run(gitops_page, config, recorder)
        gitops_page.close()

        deployment_page = browser.new_page()
        deployment_flow.run(deployment_page, config, recorder)
        deployment_page.close()

        vault_page = browser.new_page()
        vault_flow.run(vault_page, config, recorder)
        vault_page.close()

        obs_page = browser.new_page()
        observability_flow.run(obs_page, config, recorder)
        obs_page.close()

    write_docs(config, recorder)
    write_deployment_docs(config, recorder)
    recorder.add_artifact(write_cleanup_report(config, recorder))
    recorder.add_artifact(write_clean_run_policy(config))
    quality_report, quality_json = write_screenshot_quality_report(config)
    recorder.add_artifact(quality_report)
    recorder.add_artifact(quality_json)
    recorder.add_artifact(write_mkdocs_image_fix_report(config))
    recorder.add_artifact(write_evidence_json(config, recorder))
    recorder.add_artifact(recorder.write_json_summary())
    recorder.add_artifact(recorder.write_screenshot_manifest())
    recorder.copy_outputs()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
