from __future__ import annotations

from .config import PATHS
from .utils import ensure_dirs, json_code_block, write_text


def generate_docs(results: dict) -> None:
    ensure_dirs(PATHS.docs_dir, PATHS.validation_results_dir)
    write_text(
        PATHS.docs_dir / "index.md",
        "# LeninKart Validation Engine\n\n"
        "This site is generated from the autonomous validation engine.\n\n"
        f"Latest run status: **{results['summary']['status']}**\n",
    )
    write_text(
        PATHS.docs_dir / "system-architecture.md",
        "# System Architecture\n\n"
        "Architecture is discovered from platform repositories and runtime validation.\n\n"
        "## Repositories\n"
        "- `C:\\Projects\\infra\\leninkart-infra`\n"
        "- `C:\\Projects\\Services\\observer-stack`\n"
        "- `C:\\Projects\\Services\\kafka-platform`\n"
        "- `C:\\Projects\\Services\\leninkart-frontend`\n"
        "- `C:\\Projects\\Services\\leninkart-product-service`\n"
        "- `C:\\Projects\\Services\\leninkart-order-service`\n\n"
        "## Diagram\n"
        "See [Diagrams](diagrams.md).\n",
    )
    write_text(PATHS.docs_dir / "infrastructure-topology.md", "# Infrastructure Topology\n\n" + json_code_block(results.get("infrastructure", {})))
    write_text(PATHS.docs_dir / "messaging-architecture.md", "# Messaging Architecture\n\n" + json_code_block(results.get("messaging", {})))
    write_text(PATHS.docs_dir / "observability-architecture.md", "# Observability Architecture\n\n" + json_code_block(results.get("observability", {})))
    write_text(PATHS.docs_dir / "secret-management.md", "# Secret Management\n\n" + json_code_block(results.get("secret_management", {})))
    write_text(PATHS.docs_dir / "validation-summary.md", "# Validation Summary\n\n" + json_code_block(results.get("summary", {})))
    write_text(PATHS.validation_results_dir / "runtime-evidence.md", "# Runtime Evidence\n\n" + json_code_block(results))
    screenshots = sorted(p.name for p in PATHS.screenshots_dir.glob("*.svg"))
    write_text(PATHS.docs_dir / "screenshots.md", "# Screenshots\n\n" + "\n".join(f"![{name}](screenshots/{name})" for name in screenshots))
    diagrams = sorted(p.name for p in PATHS.diagrams_dir.glob("*"))
    write_text(PATHS.docs_dir / "diagrams.md", "# Diagrams\n\n" + "\n".join(f"- `{name}`" for name in diagrams))
