from __future__ import annotations

import shutil
from pathlib import Path

from .config import ValidationConfig


GENERATED_DOCS = [
    "index.md",
    "PLATFORM_TEST_CASE_MATRIX.md",
    "VALIDATION_EXECUTION_PLAN.md",
    "PLATFORM_EVIDENCE_INDEX.md",
    "PLATFORM_VALIDATION_RESULTS.md",
    "MKDOCS_NAVIGATION_PLAN.md",
    "SCREENSHOTS_GALLERY.md",
    "MKDOCS_IMAGE_FIX_REPORT.md",
    "VAULT_SECRET_INVENTORY_REPORT.md",
    "VALIDATION_CLEANUP_REPORT.md",
    "SCREENSHOT_CLEAN_RUN_POLICY.md",
    "SCREENSHOT_QUALITY_REPORT.md",
]


def clean_generated_outputs(config: ValidationConfig) -> None:
    debug_dir = config.artifacts_dir / "debug-retries"
    if debug_dir.exists():
        shutil.rmtree(debug_dir)
    debug_dir.mkdir(parents=True, exist_ok=True)

    for child in config.artifacts_dir.iterdir() if config.artifacts_dir.exists() else []:
        if child.name == "debug-retries":
            continue
        if child.is_dir():
            shutil.rmtree(child)
        else:
            child.unlink()
    for category in config.settings["defaults"]["paths"]["screenshots"]:
        target = config.screenshot_dir(category)
        if target.exists():
            shutil.rmtree(target)
        target.mkdir(parents=True, exist_ok=True)
    if config.validation_output_dir.exists():
        shutil.rmtree(config.validation_output_dir)
    config.validation_output_dir.mkdir(parents=True, exist_ok=True)
    config.docs_dir.mkdir(parents=True, exist_ok=True)
    docs_screenshots = config.docs_dir / "screenshots"
    if docs_screenshots.exists():
        shutil.rmtree(docs_screenshots)
    for doc_name in GENERATED_DOCS:
        path = config.docs_dir / doc_name
        if path.exists():
            path.unlink()


def collect_cleanup_candidates(root: Path) -> list[str]:
    return [
        "validator_engine/",
        "playwright_tests/",
        "scripts/",
        "docs/screenshots/",
        "docs/validation-results/",
        "legacy observer-stack markdown and screenshot assets",
    ]
