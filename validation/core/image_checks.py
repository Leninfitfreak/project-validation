from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageStat


@dataclass
class ImageCheckResult:
    ok: bool
    width: int
    height: int
    unique_colors: int
    max_channel_stddev: float
    dominant_ratio: float
    reason: str


DEFAULT_RULES = {
    "min_width": 400,
    "min_height": 250,
    "min_unique_colors": 24,
    "min_stddev": 8.0,
    "max_dominant_ratio": 0.92,
}


def analyze_image(path: Path, rules: dict[str, float | int] | None = None) -> ImageCheckResult:
    active_rules = {**DEFAULT_RULES, **(rules or {})}
    with Image.open(path) as image:
        rgb = image.convert("RGB")
        width, height = rgb.size
        thumb = rgb.resize((64, 64))
        stat = ImageStat.Stat(thumb)
        stddev = max(stat.stddev)
        colors = thumb.getcolors(maxcolors=4096) or []
        unique_colors = len(colors)
        dominant = max((count for count, _ in colors), default=0)
        dominant_ratio = dominant / float(64 * 64)

    if width < int(active_rules["min_width"]) or height < int(active_rules["min_height"]):
        return ImageCheckResult(False, width, height, unique_colors, stddev, dominant_ratio, "image too small")
    if unique_colors < int(active_rules["min_unique_colors"]):
        return ImageCheckResult(False, width, height, unique_colors, stddev, dominant_ratio, "too few colors")
    if stddev < float(active_rules["min_stddev"]):
        return ImageCheckResult(False, width, height, unique_colors, stddev, dominant_ratio, "image too visually uniform")
    if dominant_ratio > float(active_rules["max_dominant_ratio"]):
        return ImageCheckResult(False, width, height, unique_colors, stddev, dominant_ratio, "single color dominates frame")
    return ImageCheckResult(True, width, height, unique_colors, stddev, dominant_ratio, "image looks populated")


def assert_meaningful_image(path: Path, rules: dict[str, float | int] | None = None) -> ImageCheckResult:
    result = analyze_image(path, rules)
    if not result.ok:
        raise RuntimeError(f"{path.name} rejected by image quality checks: {result.reason}")
    return result
