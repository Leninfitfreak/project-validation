# Project Validation

Clean, modular validation and evidence framework for the LeninKart platform.

## What It Covers

- Real application flow: signup, login, product creation, buy flow, and order history proof
- Real deployment proof: Jira-driven deployment validation, GitHub Actions run proof, GitOps commit proof, ArgoCD sync and health proof, and application reachability proof
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

## Real UI Proof

Deployment and platform presentation proof now prioritizes real browser UI over synthetic artifacts.

- screenshots are captured at high resolution with a 1920x1080 viewport and device scale factor 2 for sharper evidence
- Jira proof supports authenticated browser login and stage-aware capture for overview, details, comments, progress, and final state when Jira URL and credentials are available in `.env`
- the framework reviews Jira ticket professionalism and flags weak summary/metadata patterns with a preferred template for future tickets
- GitHub Actions workflow proof is captured from the real public workflow and job pages
- GitOps proof is captured from the real GitHub commit UI
- ArgoCD proof is captured from the real application page
- application proof is captured from the live LeninKart UI
- observability proof is captured from real Grafana, Prometheus, Loki, and Tempo pages

If an authenticated UI cannot be reached safely, the framework records an honest warning instead of faking a screenshot.
