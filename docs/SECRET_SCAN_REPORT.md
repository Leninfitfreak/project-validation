# Secret Scan Report

## Tooling

- Tool: `Gitleaks`
- Integration mode: GitHub Actions
- Coverage target:
  - `leninkart-frontend`
  - `leninkart-product-service`
  - `leninkart-order-service`
  - `leninkart-infra`
  - `project-validation`
  - `kafka-platform`

## Why This Tool

`Gitleaks` is a practical baseline for public repositories:

- easy to integrate
- fast enough for routine CI
- readable pass/fail output in GitHub Actions
- appropriate for portfolio-visible secret scanning proof

## Policy

- Secret scanning is a blocking quality gate
- Repositories should fail CI on real leaks
- False positives should be handled by targeted allowlisting, not by disabling the scanner broadly

## Local Validation Notes

- The workflow integration was implemented, but local end-to-end execution of the GitHub Action itself is not reproduced on this workstation
- The absence of a local GitHub Actions runner is expected and not a project defect

## Expected Evidence

Final public CI proof should include:

- workflow run summary with `Gitleaks` job/step visible
- passing result where available
- any documented false-positive handling if needed later

## Known Limitations

- `Gitleaks` only proves repository content scanning, not runtime secret misuse
- Secret values must never be copied into public reports or screenshots
