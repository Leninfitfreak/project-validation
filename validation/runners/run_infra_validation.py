from __future__ import annotations

from pathlib import Path

from validation.core.browser import BrowserHarness
from validation.core.cleanup import clean_generated_outputs
from validation.core.config import load_config
from validation.core.reporting import RunRecorder
from validation.flows import gitops_flow, infra_flow, messaging_flow, vault_flow
from validation.runners.run_full_validation import (
    write_clean_run_policy,
    write_cleanup_report,
    write_docs,
    write_evidence_json,
    write_screenshot_quality_report,
)


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    config = load_config(root)
    clean_generated_outputs(config)
    recorder = RunRecorder(config)
    recorder.ensure_dirs()

    infra_flow.run(config, recorder)
    messaging_flow.run(config, recorder)

    with BrowserHarness(config) as browser:
        gitops_page = browser.new_page()
        gitops_flow.run(gitops_page, config, recorder)
        gitops_page.close()

        vault_page = browser.new_page()
        vault_flow.run(vault_page, config, recorder)
        vault_page.close()

    write_docs(config, recorder)
    recorder.add_artifact(write_cleanup_report(config, recorder))
    recorder.add_artifact(write_clean_run_policy(config))
    quality_report, quality_json = write_screenshot_quality_report(config)
    recorder.add_artifact(quality_report)
    recorder.add_artifact(quality_json)
    recorder.add_artifact(write_evidence_json(config, recorder))
    recorder.add_artifact(recorder.write_json_summary())
    recorder.add_artifact(recorder.write_screenshot_manifest())
    recorder.copy_outputs()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
