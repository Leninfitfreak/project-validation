# Pre-SonarQube Baseline Report

This baseline was completed before SonarQube integration.

- Service under test: `product-service`
- Fresh service CI run: `23809444386`
- Jira ticket: `SCRUM-39`
- Deployment workflow run: `23809525823`
- Requested version: `latest-dev`
- Resolved version: `23809444386`
- Version source: `latest_tag_metadata`
- GitOps commit: `dc3909119774a7b9756fd4caf5d03822a1ae2265`
- GitOps values file: `applications/product-service/helm/values-dev.yaml`
- ArgoCD app: `dev-product-service`
- ArgoCD status: `Synced / Healthy`
- Application validation: `PASS`
- Observability validation: `PASS`
- Vault validation: `PASS`
- Jira lifecycle: `Done` with all expected progress stages posted
- Final verdict: `PASS`

## Notes

- Jira browser UI proof was intentionally skipped by local validation configuration.
- Jira lifecycle was verified through the live Jira API and deployment artifacts.
