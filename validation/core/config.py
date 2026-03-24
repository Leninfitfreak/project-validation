from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml
from dotenv import dotenv_values


@dataclass
class ValidationConfig:
    root: Path
    env: dict[str, str]
    settings: dict[str, Any]
    users: dict[str, Any]
    products: dict[str, Any]
    screenshot_targets: dict[str, Any]

    @property
    def docs_dir(self) -> Path:
        return self.root / self.settings["defaults"]["paths"]["docs"]

    @property
    def artifacts_dir(self) -> Path:
        return self.root / self.settings["defaults"]["paths"]["artifacts"]

    @property
    def validation_output_dir(self) -> Path:
        return self.root / self.settings["defaults"]["paths"]["validation_output"]

    def screenshot_dir(self, category: str) -> Path:
        relative = self.settings["defaults"]["paths"]["screenshots"][category]
        return self.root / relative


def load_config(root: Path) -> ValidationConfig:
    env = {key: value for key, value in dotenv_values(root / ".env").items() if value is not None}
    env.setdefault("INGRESS_URL", "http://127.0.0.1/")
    env.setdefault("ARGOCD_URL", "http://127.0.0.1:8085")
    env.setdefault("VAULT_URL", "http://127.0.0.1:8205")
    env.setdefault("GRAFANA_URL", "http://127.0.0.1:3000")
    env.setdefault("PROMETHEUS_URL", "http://127.0.0.1:9090")
    env.setdefault("LOKI_URL", "http://127.0.0.1:3100")
    env.setdefault("TEMPO_URL", "http://127.0.0.1:3200")
    settings = yaml.safe_load((root / "validation" / "data" / "validation_config.yaml").read_text(encoding="utf-8"))
    users = json.loads((root / "validation" / "data" / "test_users.json").read_text(encoding="utf-8"))
    products = json.loads((root / "validation" / "data" / "test_products.json").read_text(encoding="utf-8"))
    screenshot_targets = json.loads((root / "validation" / "data" / "screenshot_targets.json").read_text(encoding="utf-8"))
    return ValidationConfig(
        root=root,
        env=env,
        settings=settings,
        users=users,
        products=products,
        screenshot_targets=screenshot_targets,
    )
