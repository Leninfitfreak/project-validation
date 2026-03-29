# Deployment POC Evidence Index

## `DEP-001` Service CI latest tag publish proof

- Status: `PASS`
- Detail: Real GitHub Actions run page shows the service CI workflow that published the latest tag metadata used by deployment-poc.
- Screenshot: [screenshots/deployment/service-ci-latest-tag-publish.png](screenshots/deployment/service-ci-latest-tag-publish.png)

![Service CI latest tag publish proof](screenshots/deployment/service-ci-latest-tag-publish.png)

## `DEP-001A` Latest tag metadata proof

- Status: `PASS`
- Detail: Real GitHub file page shows the latest_tags entry that deployment-poc resolved for this deployment.
- Screenshot: [screenshots/deployment/latest-tags-metadata-proof.png](screenshots/deployment/latest-tags-metadata-proof.png)

![Latest tag metadata proof](screenshots/deployment/latest-tags-metadata-proof.png)

## `DEP-001B` Jira lifecycle API proof

- Status: `PASS`
- Detail: Fresh Jira ticket creation, progress comments, and final completed status were verified via Jira REST API.
- Artifact: `artifacts/jira-lifecycle-proof.json`

## `DEP-002` GitHub Actions deployment run summary

- Status: `PASS`
- Detail: Real GitHub Actions workflow run page captured with job summary visible
- Screenshot: [screenshots/deployment/github-actions-run-summary.png](screenshots/deployment/github-actions-run-summary.png)

![GitHub Actions deployment run summary](screenshots/deployment/github-actions-run-summary.png)

## `DEP-003` GitHub Actions runner proof

- Status: `PASS`
- Detail: Real GitHub job page captured with the self-hosted runner details visible
- Screenshot: [screenshots/deployment/github-actions-runner-proof.png](screenshots/deployment/github-actions-runner-proof.png)

![GitHub Actions runner proof](screenshots/deployment/github-actions-runner-proof.png)

## `DEP-004` deployment-poc result proof

- Status: `PASS`
- Detail: Real GitHub workflow run page captured with the deployment-result artifact visible as primary browser proof
- Screenshot: [screenshots/deployment/deployment-result-proof.png](screenshots/deployment/deployment-result-proof.png)

![deployment-poc result proof](screenshots/deployment/deployment-result-proof.png)

## `DEP-005` GitOps commit proof

- Status: `PASS`
- Detail: Real public GitHub commit page shows the leninkart-infra revision and changed values file
- Screenshot: [screenshots/deployment/gitops-commit-proof.png](screenshots/deployment/gitops-commit-proof.png)

![GitOps commit proof](screenshots/deployment/gitops-commit-proof.png)

## `DEP-006` ArgoCD deployment application proof

- Status: `PASS`
- Detail: Real ArgoCD application page shows Synced and Healthy on the expected revision
- Screenshot: [screenshots/deployment/argocd-deployment-app.png](screenshots/deployment/argocd-deployment-app.png)

![ArgoCD deployment application proof](screenshots/deployment/argocd-deployment-app.png)

## `DEP-007` Application deployment proof

- Status: `PASS`
- Detail: Real browser screenshot confirms the deployed LeninKart application is reachable
- Screenshot: [screenshots/deployment/application-home-proof.png](screenshots/deployment/application-home-proof.png)

![Application deployment proof](screenshots/deployment/application-home-proof.png)
