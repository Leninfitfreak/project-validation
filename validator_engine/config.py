from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

ROOT = Path(r"C:\Projects\Services\project-validation")


@dataclass(frozen=True)
class RepoPaths:
    project_validation: Path = ROOT
    infra: Path = Path(r"C:\Projects\infra\leninkart-infra")
    observer_stack: Path = Path(r"C:\Projects\Services\observer-stack")
    kafka_platform: Path = Path(r"C:\Projects\Services\kafka-platform")
    frontend: Path = Path(r"C:\Projects\Services\leninkart-frontend")
    product_service: Path = Path(r"C:\Projects\Services\leninkart-product-service")
    order_service: Path = Path(r"C:\Projects\Services\leninkart-order-service")


@dataclass(frozen=True)
class Paths:
    root: Path = ROOT
    env_file: Path = ROOT / ".env"
    secrets_file: Path = ROOT / "local-secrets.txt.txt"
    logs_dir: Path = ROOT / "logs"
    artifacts_dir: Path = ROOT / "artifacts"
    screenshots_dir: Path = ROOT / "screenshots"
    docs_dir: Path = ROOT / "docs"
    diagrams_dir: Path = ROOT / "docs" / "diagrams"
    validation_results_dir: Path = ROOT / "docs" / "validation-results"


REPOS = RepoPaths()
PATHS = Paths()
