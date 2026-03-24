# Project Validation

Clean, modular validation and evidence framework for the LeninKart platform.

## What It Covers

- Real application flow: signup, login, product creation, buy flow, and order history proof
- GitOps and infrastructure proof: ArgoCD, Kubernetes inventory, ExternalSecret evidence
- Secrets proof: Vault login, safe inventory page, and secret inventory report without values
- Observability proof: Grafana dashboards, Loki logs, Prometheus targets, and Tempo traces
- Messaging proof: external Kafka runtime health and Kafka dashboard evidence

## Framework Structure

- `validation/core/`: browser lifecycle, waits, retries, screenshot capture, cleanup, image checks, reporting
- `validation/flows/`: application, GitOps, Vault, messaging, and observability flows
- `validation/checks/`: reusable readiness checks for Grafana, ArgoCD, Vault, frontend, and screenshot audits
- `validation/data/`: config, demo users/products, and screenshot target metadata
- `validation/runners/`: full, app-only, infra-only, observability-only, and vault-only entry points

## Clean Run Policy

- Every run starts by deleting prior generated screenshots, reports, and output bundles
- Final screenshots are replaced in-place and never accumulate duplicate suffixes
- Retry attempts are stored separately under `artifacts/debug-retries/`
- Blank or weak screenshots are rejected automatically using image-quality checks

## Usage

Run the full validation suite:

```powershell
python run_validation.py
```

Run a focused suite:

```powershell
python -m validation.runners.run_app_validation
python -m validation.runners.run_infra_validation
python -m validation.runners.run_observability_validation
python -m validation.runners.run_vault_validation
```

## Configuration

- `.env`: runtime URLs and credentials
- `validation/data/validation_config.yaml`: waits, screenshot paths, screenshot quality thresholds, expected dashboards/apps
- `validation/data/test_users.json`: demo signup user template
- `validation/data/test_products.json`: demo product payloads
- `validation/data/screenshot_targets.json`: planned screenshot targets

## Outputs

- `docs/`: MkDocs-ready reports
- `screenshots/`: final evidence only
- `artifacts/`: execution summaries, manifests, CLI proof, and retry diagnostics
- `validation-output/`: packaged copy of the latest run
