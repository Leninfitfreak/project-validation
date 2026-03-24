from __future__ import annotations

import shutil
from pathlib import Path
from typing import Callable

from playwright.sync_api import Page

from .image_checks import ImageCheckResult, assert_meaningful_image
from .waits import wait_for_no_loading


def _debug_dir_for(path: Path) -> Path:
    root = path.parents[2]
    target = root / "artifacts" / "debug-retries" / path.parent.name
    target.mkdir(parents=True, exist_ok=True)
    return target


def capture_when_ready(
    page: Page,
    path: Path,
    *,
    prepare: Callable[[], None] | None = None,
    verify: Callable[[], None] | None = None,
    require_no_loading: bool = True,
    retries: int = 3,
    retry_wait_ms: int = 1500,
    timeout_ms: int = 20000,
    image_rules: dict[str, float | int] | None = None,
) -> ImageCheckResult:
    last_error: Exception | None = None
    debug_dir = _debug_dir_for(path)
    for attempt in range(1, retries + 1):
        temp_path = debug_dir / f"{path.stem}-attempt-{attempt}.png"
        try:
            if prepare:
                prepare()
            if require_no_loading:
                wait_for_no_loading(page, timeout_ms)
            if verify:
                verify()
            path.parent.mkdir(parents=True, exist_ok=True)
            page.screenshot(path=str(temp_path), full_page=True)
            result = assert_meaningful_image(temp_path, image_rules)
            shutil.move(str(temp_path), str(path))
            return result
        except Exception as exc:
            last_error = exc
            page.wait_for_timeout(retry_wait_ms * attempt)
    raise RuntimeError(f"failed to capture valid screenshot for {path.name}: {last_error}")
