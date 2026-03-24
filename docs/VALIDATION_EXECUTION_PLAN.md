# Validation Execution Plan

1. Start from a clean output state by removing prior screenshots, reports, and artifacts while preserving retry debug folders only for the current run.
2. Load URLs, credentials, wait rules, screenshot quality thresholds, and demo data from `.env` and `validation/data/*`.
3. Capture infrastructure and messaging CLI proof before browser work begins.
4. Run the frontend user journey in order: login page, signup, authenticated dashboard, product creation, buy flow, and order history proof.
5. Run GitOps and Vault UI proof flows and generate the safe Vault secret inventory report.
6. Run observability proof for Grafana dashboards, Loki Explore, Prometheus targets, and Tempo search/detail pages.
7. Reject blank or weak screenshots automatically, retry with longer waits, and only publish screenshots that pass image-quality checks.
8. Write markdown, JSON, screenshot manifest, and validation-output bundles for MkDocs and portfolio documentation.