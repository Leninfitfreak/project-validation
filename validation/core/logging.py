from __future__ import annotations

import logging
from pathlib import Path


def get_logger(name: str, root: Path) -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)
    debug_dir = root / "artifacts" / "debug-retries"
    debug_dir.mkdir(parents=True, exist_ok=True)
    handler = logging.FileHandler(debug_dir / "validation.log", encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s"))
    logger.addHandler(handler)
    logger.propagate = False
    return logger
