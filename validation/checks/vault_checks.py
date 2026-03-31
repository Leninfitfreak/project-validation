from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

from validation.core.assertions import assert_text


def login_page(page, timeout_ms: int) -> None:
    assert_text(page, "Sign in", timeout_ms)


def resolve_root_token(env: dict[str, str]) -> str:
    if env.get("VAULT_ROOT_TOKEN"):
        return env["VAULT_ROOT_TOKEN"]
    result = subprocess.run(
        ["kubectl", "exec", "-n", "vault", "vault-0", "--", "cat", "/vault/data/bootstrap-keys.json"],
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(result.stdout)["root_token"]


def list_secret_inventory(token: str) -> dict[str, list[str]]:
    script = r"""
import json
import os
import subprocess
from collections import defaultdict

token = os.environ["VAULT_TOKEN"]
queue = ["secret/leninkart/"]
inventory = defaultdict(list)
while queue:
    current = queue.pop(0)
    result = subprocess.run(
        ["kubectl", "exec", "-n", "vault", "vault-0", "--", "sh", "-lc", f'VAULT_TOKEN="{token}" vault kv list -format=json {current}'],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0 or not result.stdout.strip():
        continue
    for item in json.loads(result.stdout):
        if item.endswith("/"):
            queue.append(current + item)
        else:
            inventory[current].append(item)
print(json.dumps(inventory))
"""
    env = os.environ.copy()
    env["VAULT_TOKEN"] = token
    result = subprocess.run(["python", "-c", script], capture_output=True, text=True, check=True, env=env)
    return json.loads(result.stdout)


def top_level_inventory_entries(inventory: dict[str, list[str]]) -> list[str]:
    entries = inventory.get("secret/leninkart/", [])
    return sorted(str(item).strip() for item in entries if str(item).strip())


def write_inventory_report(target: Path, inventory: dict[str, list[str]]) -> None:
    total = sum(len(values) for values in inventory.values())
    lines = [
        "# Vault Secret Inventory Report",
        "",
        f"- Secret count: `{total}`",
        "",
        "## Paths",
        "",
    ]
    for path, keys in sorted(inventory.items()):
        lines.append(f"### `{path}`")
        lines.append("")
        for key in sorted(keys):
            lines.append(f"- `{key}`")
        lines.append("")
    lines.extend(
        [
            "## Usage Mapping",
            "",
            "- `secret/leninkart/observability/*`: observability admin and provisioning secrets",
            "- `secret/leninkart/product-service/*`: product-service runtime configuration",
            "- `secret/leninkart/order-service/*`: order-service runtime configuration",
            "- `secret/leninkart/postgres/*`: shared database credentials and connection data",
        ]
    )
    target.write_text("\n".join(lines), encoding="utf-8")
