# Validation Execution Plan

1. Start from a clean output state by removing prior screenshots, reports, and artifacts while preserving retry debug folders only for the current run.
2. Load URLs, credentials, wait rules, screenshot quality thresholds, and demo data from `.env` and `validation/data/*`.
3. Capture infrastructure and messaging CLI proof before browser work begins.
4. Validate CI security proof from the service pipeline: SonarQube scan, SonarQube quality gate, and Gitleaks evidence.
5. Validate the latest-tag deployment path: service CI metadata publish, Jira -> deployment-poc resolution, GitOps commit, ArgoCD state, and application reachability proof.
6. Run the frontend user journey in order: login page, signup, authenticated dashboard, product creation, buy flow, and order history proof.
7. Run GitOps and Vault UI proof flows and generate the safe Vault secret inventory report.
8. Run observability proof for Grafana dashboards, Loki Explore, Prometheus targets, and Tempo search/detail pages.
9. Reject blank or weak screenshots automatically, retry with longer waits, and only publish screenshots that pass image-quality checks.
10. Write markdown, JSON, screenshot manifest, and validation-output bundles for MkDocs and portfolio documentation.