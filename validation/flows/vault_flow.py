from __future__ import annotations

from playwright.sync_api import Page

from validation.checks import vault_checks
from validation.core.config import ValidationConfig
from validation.core.reporting import RunRecorder, StepResult
from validation.core.screenshots import capture_when_ready
from validation.core.waits import wait_for_condition, wait_for_text


def run(page: Page, config: ValidationConfig, recorder: RunRecorder) -> None:
    waits = config.settings["defaults"]["waits"]
    image_rules = config.settings["defaults"]["screenshot_quality"]
    timeout = waits["timeout_ms"]
    long_timeout = waits["long_timeout_ms"]

    page.goto(config.env["VAULT_URL"], wait_until="domcontentloaded")
    capture_when_ready(
        page,
        config.screenshot_dir("secrets") / "vault-login.png",
        require_no_loading=False,
        verify=lambda: vault_checks.login_page(page, timeout),
        retries=waits["retry_count"],
        retry_wait_ms=waits["retry_sleep_ms"],
        timeout_ms=timeout,
        image_rules=image_rules,
    )
    recorder.add_step(StepResult("SEC-001", "secrets", "Vault login page", "PASS", "Vault login visible", "screenshots/secrets/vault-login.png"))

    token = vault_checks.resolve_root_token(config.env)
    inventory = vault_checks.list_secret_inventory(token)
    expected_entries = vault_checks.top_level_inventory_entries(inventory)

    page.locator('input[name="token"]').fill(token)
    page.get_by_role("button", name="Sign In").click()
    page.set_viewport_size({"width": 1720, "height": 1280})
    wait_for_text(page, "Dashboard", long_timeout)
    page.get_by_text("Secrets Engines", exact=False).first.click()
    wait_for_text(page, "secret/", long_timeout)
    page.get_by_text("secret/", exact=False).first.click()
    wait_for_text(page, "leninkart/", long_timeout)
    page.get_by_text("leninkart/", exact=False).first.click()

    def verify_inventory_view() -> None:
        wait_for_text(page, "secret", long_timeout)
        wait_for_text(page, "leninkart", long_timeout)
        wait_for_condition(
            page,
            "vault top-level entries visible",
            lambda: sum(1 for item in expected_entries if item in (page.text_content("body") or "")) >= min(3, len(expected_entries)),
            long_timeout,
        )

    capture_when_ready(
        page,
        config.screenshot_dir("secrets") / "vault-secret-inventory.png",
        require_no_loading=False,
        verify=verify_inventory_view,
        retries=waits["retry_count"],
        retry_wait_ms=waits["retry_sleep_ms"],
        timeout_ms=long_timeout,
        image_rules=image_rules,
        full_page=True,
    )
    recorder.add_step(StepResult("SEC-002", "secrets", "Vault safe inventory view", "PASS", "Vault leninkart secret path inventory visible without exposing secret values", "screenshots/secrets/vault-secret-inventory.png"))

    proof_artifact = config.artifacts_dir / "vault-secret-proof.md"
    proof_artifact.write_text(
        "\n".join(
            [
                "# Vault Secret Proof",
                "",
                "- Representative platform path: `secret/leninkart/observability/grafana`",
                f"- Inventory paths discovered: `{len(inventory)}`",
                f"- Root token resolved at runtime: `{'yes' if token else 'no'}`",
                "- Secret values were intentionally excluded from all artifacts.",
            ]
        ),
        encoding="utf-8",
    )
    recorder.add_artifact(proof_artifact)
    recorder.add_step(StepResult("SEC-003", "secrets", "Vault secret proof artifact", "PASS", "Safe secret-path proof written", artifact="artifacts/vault-secret-proof.md"))

    report = config.docs_dir / "VAULT_SECRET_INVENTORY_REPORT.md"
    vault_checks.write_inventory_report(report, inventory)
