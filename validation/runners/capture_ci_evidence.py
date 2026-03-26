from __future__ import annotations

import json
import shutil
from pathlib import Path

from playwright.sync_api import sync_playwright

from validation.core.image_checks import assert_meaningful_image


ROOT = Path(__file__).resolve().parents[2]
TARGETS_PATH = ROOT / "validation" / "data" / "ci_targets.json"
SCREENSHOT_DIR = ROOT / "screenshots" / "ci"
DOCS_SCREENSHOT_DIR = ROOT / "docs" / "screenshots" / "ci"
ARTIFACTS_DIR = ROOT / "artifacts"


def load_targets() -> list[dict[str, object]]:
    return json.loads(TARGETS_PATH.read_text(encoding="utf-8"))


def wait_for_page_content(page, target: dict[str, object]) -> None:
    page.goto(str(target["url"]), wait_until="domcontentloaded", timeout=60000)
    page.wait_for_load_state("networkidle", timeout=60000)
    for text in target["wait_texts"]:
        page.get_by_text(str(text), exact=False).first.wait_for(state="visible", timeout=60000)
    if target["type"] == "job":
        page.wait_for_timeout(3000)
    else:
        page.wait_for_timeout(2000)


def main() -> None:
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    DOCS_SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)

    manifest: list[dict[str, str]] = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(ignore_https_errors=True, viewport={"width": 1600, "height": 1200})
        page = context.new_page()

        for target in load_targets():
            output_path = SCREENSHOT_DIR / str(target["screenshot"])
            docs_output_path = DOCS_SCREENSHOT_DIR / str(target["screenshot"])
            wait_for_page_content(page, target)
            page.screenshot(path=str(output_path), full_page=True)
            assert_meaningful_image(output_path, None)
            shutil.copy2(output_path, docs_output_path)
            manifest.append(
                {
                    "name": str(target["name"]),
                    "url": str(target["url"]),
                    "screenshot": f"screenshots/ci/{target['screenshot']}",
                    "docs_screenshot": f"screenshots/ci/{target['screenshot']}",
                }
            )

        context.close()
        browser.close()

    (ARTIFACTS_DIR / "ci-screenshot-manifest.json").write_text(
        json.dumps(manifest, indent=2),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
