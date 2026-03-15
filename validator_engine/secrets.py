from __future__ import annotations

from pathlib import Path

from .config import PATHS
from .utils import mask_value, write_text


def parse_local_secrets(secrets_file: Path) -> dict[str, str]:
    raw = secrets_file.read_text(encoding="utf-8")
    result: dict[str, str] = {}
    current = None
    for line in raw.splitlines():
        stripped = line.strip()
        lower = stripped.lower()
        if not stripped:
            continue
        if lower.startswith("observer stack login"):
            current = "observer"
            continue
        if lower == "vault":
            current = "vault"
            continue
        if current == "observer" and lower.startswith("username"):
            result["OBSERVER_STACK_USER"] = stripped.split(":", 1)[1].strip()
        elif current == "observer" and lower.startswith("password"):
            result["OBSERVER_STACK_PASSWORD"] = stripped.split(":", 1)[1].strip()
        elif lower.startswith("initial root token"):
            current = "vault_token"
        elif current == "vault_token" and stripped.startswith("hvs."):
            result["VAULT_ROOT_TOKEN"] = stripped
            current = "vault"
        elif lower.startswith("key 1"):
            current = "vault_key"
        elif current == "vault_key":
            result["VAULT_UNSEAL_KEY"] = stripped
            current = "vault"
    return result


def generate_env_file() -> dict[str, str]:
    secrets = parse_local_secrets(PATHS.secrets_file)
    lines = [
        "PLATFORM_ENV=local",
        "KUBE_NAMESPACE=dev",
        "INGRESS_URL=http://127.0.0.1/",
        "OBSERVER_STACK_URL=http://localhost:8080",
        "ARGOCD_URL=http://localhost:8085",
        "VAULT_URL=http://localhost:8205",
    ]
    for key in ["OBSERVER_STACK_USER", "OBSERVER_STACK_PASSWORD", "VAULT_ROOT_TOKEN", "VAULT_UNSEAL_KEY"]:
        if key in secrets:
            lines.append(f"{key}={secrets[key]}")
    write_text(PATHS.env_file, "\n".join(lines) + "\n")
    return secrets


def masked_secret_report(secrets: dict[str, str]) -> dict[str, str]:
    return {key: mask_value(value) for key, value in secrets.items()}
