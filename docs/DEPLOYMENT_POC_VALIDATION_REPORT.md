# Deployment POC Validation Report

## Validated Scope

- Jira deployment ticket proof
- GitHub Actions workflow summary and self-hosted runner proof
- deployment-poc result/report evidence
- GitOps commit and target file proof
- ArgoCD final Sync and Health proof

## Latest Validated Deployment

- Jira ticket: `SCRUM-6`
- Workflow run: `#17`
- Workflow URL: `https://github.com/Leninfitfreak/deployment-poc/actions/runs/23612528816`
- Runner: `leninkart-runner`
- Deployment action: `already_deployed`
- Requested version: `v2`
- Resolved version: `23599512080`
- GitOps commit: `a5530ce5dccff30803b262516d8e66edc0022040`
- GitOps values path: `applications/frontend/helm/values-dev.yaml`
- ArgoCD app: `frontend-dev`
- Final sync: `Synced`
- Final health: `Healthy`
- Jira proof mode: `artifact_fallback`

## Screenshot Proof

### DEP-001 Jira ticket proof

- Detail: Deployment ticket proof captured from the live Jira page or an honest artifact-backed fallback
- Screenshot: [screenshots/deployment/jira-ticket-proof.png](screenshots/deployment/jira-ticket-proof.png)

![Jira ticket proof](screenshots/deployment/jira-ticket-proof.png)

### DEP-002 GitHub Actions deployment run summary

- Detail: Public workflow run summary loaded with successful deployment job visible
- Screenshot: [screenshots/deployment/github-actions-run-summary.png](screenshots/deployment/github-actions-run-summary.png)

![GitHub Actions deployment run summary](screenshots/deployment/github-actions-run-summary.png)

### DEP-003 GitHub Actions runner proof

- Detail: Readable runner proof confirms the validated deployment run used the expected self-hosted runner and labels
- Screenshot: [screenshots/deployment/github-actions-runner-proof.png](screenshots/deployment/github-actions-runner-proof.png)

![GitHub Actions runner proof](screenshots/deployment/github-actions-runner-proof.png)

### DEP-004 deployment-poc result proof

- Detail: Readable deployment result artifact rendered with ticket, action, commit, and ArgoCD details
- Screenshot: [screenshots/deployment/deployment-result-proof.png](screenshots/deployment/deployment-result-proof.png)

![deployment-poc result proof](screenshots/deployment/deployment-result-proof.png)

### DEP-005 GitOps commit proof

- Detail: Public GitHub commit page shows the relevant leninkart-infra revision and target values file path
- Screenshot: [screenshots/deployment/gitops-commit-proof.png](screenshots/deployment/gitops-commit-proof.png)

![GitOps commit proof](screenshots/deployment/gitops-commit-proof.png)

### DEP-006 ArgoCD deployment application proof

- Detail: ArgoCD application detail shows the validated app as Synced and Healthy on the expected revision
- Screenshot: [screenshots/deployment/argocd-deployment-app.png](screenshots/deployment/argocd-deployment-app.png)

![ArgoCD deployment application proof](screenshots/deployment/argocd-deployment-app.png)

## Final Verdict

`PASS`
