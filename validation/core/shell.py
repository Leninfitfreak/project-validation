from __future__ import annotations

import subprocess
from pathlib import Path


def run(command: list[str], cwd: Path | None = None) -> dict[str, str | int]:
    result = subprocess.run(command, cwd=cwd, capture_output=True, text=True, check=False)
    return {
        "command": " ".join(command),
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }
