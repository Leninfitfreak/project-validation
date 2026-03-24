from __future__ import annotations

import json
import shutil
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .config import ValidationConfig


@dataclass
class StepResult:
    id: str
    category: str
    title: str
    status: str
    detail: str
    screenshot: str | None = None
    artifact: str | None = None


@dataclass
class RunRecorder:
    config: ValidationConfig
    started_at: str = field(default_factory=lambda: time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
    steps: list[StepResult] = field(default_factory=list)
    artifacts: list[str] = field(default_factory=list)

    def ensure_dirs(self) -> None:
        self.config.docs_dir.mkdir(parents=True, exist_ok=True)
        self.config.artifacts_dir.mkdir(parents=True, exist_ok=True)
        self.config.validation_output_dir.mkdir(parents=True, exist_ok=True)
        for category in self.config.settings["defaults"]["paths"]["screenshots"]:
            target = self.config.screenshot_dir(category)
            target.mkdir(parents=True, exist_ok=True)

    def add_step(self, step: StepResult) -> None:
        self.steps.append(step)

    def add_artifact(self, path: Path) -> None:
        self.artifacts.append(str(path.relative_to(self.config.root)).replace("\\", "/"))

    def write_json_summary(self) -> Path:
        payload = {
            "generated_at": self.started_at,
            "steps": [step.__dict__ for step in self.steps],
            "artifacts": self.artifacts,
        }
        target = self.config.artifacts_dir / "execution-summary.json"
        target.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return target

    def write_screenshot_manifest(self) -> Path:
        payload = [
            {
                "id": step.id,
                "category": step.category,
                "title": step.title,
                "screenshot": step.screenshot,
                "status": step.status,
            }
            for step in self.steps
            if step.screenshot
        ]
        target = self.config.artifacts_dir / "screenshot-manifest.json"
        target.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return target

    def copy_outputs(self) -> None:
        for source in [self.config.docs_dir, self.config.artifacts_dir]:
            target = self.config.validation_output_dir / source.name
            if target.exists():
                shutil.rmtree(target)
            shutil.copytree(source, target)
        screenshots_target = self.config.validation_output_dir / "screenshots"
        if screenshots_target.exists():
            shutil.rmtree(screenshots_target)
        screenshots_target.mkdir(parents=True, exist_ok=True)
        for category in self.config.settings["defaults"]["paths"]["screenshots"]:
            source = self.config.screenshot_dir(category)
            if source.exists():
                shutil.copytree(source, screenshots_target / category)
