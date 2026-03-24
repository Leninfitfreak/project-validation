from __future__ import annotations

from pathlib import Path

from validation.core.image_checks import ImageCheckResult, analyze_image


def audit_screenshots(root: Path, rules: dict[str, float | int] | None = None) -> list[dict[str, str | int | float | bool]]:
    results: list[dict[str, str | int | float | bool]] = []
    for image_path in sorted(root.rglob("*.png")):
        check: ImageCheckResult = analyze_image(image_path, rules)
        results.append(
            {
                "path": str(image_path),
                "ok": check.ok,
                "width": check.width,
                "height": check.height,
                "unique_colors": check.unique_colors,
                "max_channel_stddev": round(check.max_channel_stddev, 2),
                "dominant_ratio": round(check.dominant_ratio, 4),
                "reason": check.reason,
            }
        )
    return results
