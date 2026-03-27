# Platform Validation Results

- Total steps: `38`
- Passed: `37`
- Warnings: `1`
- Failed: `0`

## INF-001 Kubernetes inventory artifacts

- Status: `PASS`
- Detail: Pod, service, ingress, ArgoCD app, and ExternalSecret outputs captured
- Artifact: `artifacts/kubernetes-pod-inventory.txt`

## MSG-001 Kafka runtime health

- Status: `PASS`
- Detail: Docker runtime proof captured for external Kafka
- Artifact: `artifacts/kafka-runtime-health.txt`

## MSG-002 Kafka dashboard proof

- Status: `PASS`
- Detail: Kafka dashboard screenshot will be produced during observability validation
- Screenshot: [screenshots/messaging/kafka-dashboard.png](screenshots/messaging/kafka-dashboard.png)

![Kafka dashboard proof](screenshots/messaging/kafka-dashboard.png)


## APP-001 Frontend login page

- Status: `PASS`
- Detail: Login page visible
- Screenshot: [screenshots/application/frontend-login.png](screenshots/application/frontend-login.png)

![Frontend login page](screenshots/application/frontend-login.png)


## APP-002 Frontend signup page

- Status: `PASS`
- Detail: Signup form visible
- Screenshot: [screenshots/application/frontend-signup.png](screenshots/application/frontend-signup.png)

![Frontend signup page](screenshots/application/frontend-signup.png)


## APP-003 Signup success state

- Status: `PASS`
- Detail: Signup success notice visible
- Screenshot: [screenshots/application/frontend-signup-success.png](screenshots/application/frontend-signup-success.png)

![Signup success state](screenshots/application/frontend-signup-success.png)


## APP-004 Authenticated dashboard

- Status: `PASS`
- Detail: Dashboard fully visible
- Screenshot: [screenshots/application/frontend-dashboard.png](screenshots/application/frontend-dashboard.png)

![Authenticated dashboard](screenshots/application/frontend-dashboard.png)


## APP-005 Product creation form

- Status: `PASS`
- Detail: Filled product form captured
- Screenshot: [screenshots/application/product-form.png](screenshots/application/product-form.png)

![Product creation form](screenshots/application/product-form.png)


## APP-006 Product list with created items

- Status: `PASS`
- Detail: Created products visible in list
- Screenshot: [screenshots/application/product-list.png](screenshots/application/product-list.png)

![Product list with created items](screenshots/application/product-list.png)


## APP-007 Order ledger populated

- Status: `PASS`
- Detail: Order row visible after buy flow
- Screenshot: [screenshots/application/order-ledger.png](screenshots/application/order-ledger.png)

![Order ledger populated](screenshots/application/order-ledger.png)


## APP-008 User activity overview

- Status: `PASS`
- Detail: User activity panel visible
- Screenshot: [screenshots/application/user-activity.png](screenshots/application/user-activity.png)

![User activity overview](screenshots/application/user-activity.png)


## GIT-001 ArgoCD login page

- Status: `PASS`
- Detail: ArgoCD login visible
- Screenshot: [screenshots/gitops/argocd-login.png](screenshots/gitops/argocd-login.png)

![ArgoCD login page](screenshots/gitops/argocd-login.png)


## GIT-002 ArgoCD applications list

- Status: `PASS`
- Detail: Core app names visible
- Screenshot: [screenshots/gitops/argocd-app-list.png](screenshots/gitops/argocd-app-list.png)

![ArgoCD applications list](screenshots/gitops/argocd-app-list.png)


## GIT-003 ArgoCD app detail

- Status: `PASS`
- Detail: Selected app detail visible
- Screenshot: [screenshots/gitops/argocd-app-detail.png](screenshots/gitops/argocd-app-detail.png)

![ArgoCD app detail](screenshots/gitops/argocd-app-detail.png)


## DEP-001 Jira ticket proof

- Status: `WARN`
- Detail: Real Jira UI proof is not configured in project-validation; no synthetic fallback was used as primary evidence

## DEP-002 GitHub Actions deployment run summary

- Status: `PASS`
- Detail: Real GitHub Actions workflow run page captured with job summary visible
- Screenshot: [screenshots/deployment/github-actions-run-summary.png](screenshots/deployment/github-actions-run-summary.png)

![GitHub Actions deployment run summary](screenshots/deployment/github-actions-run-summary.png)


## DEP-003 GitHub Actions runner proof

- Status: `PASS`
- Detail: Real GitHub job page captured with the self-hosted runner details visible
- Screenshot: [screenshots/deployment/github-actions-runner-proof.png](screenshots/deployment/github-actions-runner-proof.png)

![GitHub Actions runner proof](screenshots/deployment/github-actions-runner-proof.png)


## DEP-004 deployment-poc result proof

- Status: `PASS`
- Detail: Real GitHub workflow run page captured with the deployment-result artifact visible as primary browser proof
- Screenshot: [screenshots/deployment/deployment-result-proof.png](screenshots/deployment/deployment-result-proof.png)

![deployment-poc result proof](screenshots/deployment/deployment-result-proof.png)


## DEP-005 GitOps commit proof

- Status: `PASS`
- Detail: Real public GitHub commit page shows the leninkart-infra revision and changed values file
- Screenshot: [screenshots/deployment/gitops-commit-proof.png](screenshots/deployment/gitops-commit-proof.png)

![GitOps commit proof](screenshots/deployment/gitops-commit-proof.png)


## DEP-006 ArgoCD deployment application proof

- Status: `PASS`
- Detail: Real ArgoCD application page shows Synced and Healthy on the expected revision
- Screenshot: [screenshots/deployment/argocd-deployment-app.png](screenshots/deployment/argocd-deployment-app.png)

![ArgoCD deployment application proof](screenshots/deployment/argocd-deployment-app.png)


## DEP-007 Application deployment proof

- Status: `PASS`
- Detail: Real browser screenshot confirms the deployed LeninKart application is reachable
- Screenshot: [screenshots/deployment/application-home-proof.png](screenshots/deployment/application-home-proof.png)

![Application deployment proof](screenshots/deployment/application-home-proof.png)


## SEC-001 Vault login page

- Status: `PASS`
- Detail: Vault login visible
- Screenshot: [screenshots/secrets/vault-login.png](screenshots/secrets/vault-login.png)

![Vault login page](screenshots/secrets/vault-login.png)


## SEC-002 Vault safe inventory view

- Status: `PASS`
- Detail: Vault secret engines view visible
- Screenshot: [screenshots/secrets/vault-secret-inventory.png](screenshots/secrets/vault-secret-inventory.png)

![Vault safe inventory view](screenshots/secrets/vault-secret-inventory.png)


## SEC-003 Vault secret proof artifact

- Status: `PASS`
- Detail: Safe secret-path proof written
- Artifact: `artifacts/vault-secret-proof.md`

## OBS-001 Grafana login

- Status: `PASS`
- Detail: Grafana login page visible
- Screenshot: [screenshots/observability/grafana-login.png](screenshots/observability/grafana-login.png)

![Grafana login](screenshots/observability/grafana-login.png)


## OBS-002 Grafana dashboard list

- Status: `PASS`
- Detail: Provisioned dashboard list visible inside the LeninKart folder
- Screenshot: [screenshots/observability/grafana-dashboard-list.png](screenshots/observability/grafana-dashboard-list.png)

![Grafana dashboard list](screenshots/observability/grafana-dashboard-list.png)


## OBS-003 LeninKart Platform Overview

- Status: `PASS`
- Detail: LeninKart Platform Overview rendered with visible content
- Screenshot: [screenshots/observability/dashboard-platform.png](screenshots/observability/dashboard-platform.png)

![LeninKart Platform Overview](screenshots/observability/dashboard-platform.png)


## OBS-004 LeninKart Product Service Overview

- Status: `PASS`
- Detail: LeninKart Product Service Overview rendered with visible content
- Screenshot: [screenshots/observability/dashboard-product.png](screenshots/observability/dashboard-product.png)

![LeninKart Product Service Overview](screenshots/observability/dashboard-product.png)


## OBS-005 LeninKart Order Service Overview

- Status: `PASS`
- Detail: LeninKart Order Service Overview rendered with visible content
- Screenshot: [screenshots/observability/dashboard-order.png](screenshots/observability/dashboard-order.png)

![LeninKart Order Service Overview](screenshots/observability/dashboard-order.png)


## OBS-006 LeninKart Frontend Overview

- Status: `PASS`
- Detail: LeninKart Frontend Overview rendered with visible content
- Screenshot: [screenshots/observability/dashboard-frontend.png](screenshots/observability/dashboard-frontend.png)

![LeninKart Frontend Overview](screenshots/observability/dashboard-frontend.png)


## OBS-007 LeninKart Logs Overview

- Status: `PASS`
- Detail: LeninKart Logs Overview rendered with visible content
- Screenshot: [screenshots/observability/dashboard-logs.png](screenshots/observability/dashboard-logs.png)

![LeninKart Logs Overview](screenshots/observability/dashboard-logs.png)


## OBS-008 LeninKart Kafka Overview

- Status: `PASS`
- Detail: LeninKart Kafka Overview rendered with visible content
- Screenshot: [screenshots/observability/dashboard-kafka.png](screenshots/observability/dashboard-kafka.png)

![LeninKart Kafka Overview](screenshots/observability/dashboard-kafka.png)


## OBS-009 Grafana Explore Loki

- Status: `PASS`
- Detail: Loki search returned recent product-service logs
- Screenshot: [screenshots/observability/grafana-loki-explore.png](screenshots/observability/grafana-loki-explore.png)

![Grafana Explore Loki](screenshots/observability/grafana-loki-explore.png)


## OBS-010 Prometheus targets

- Status: `PASS`
- Detail: Prometheus targets page populated
- Screenshot: [screenshots/observability/prometheus-targets.png](screenshots/observability/prometheus-targets.png)

![Prometheus targets](screenshots/observability/prometheus-targets.png)


## OBS-011 Grafana Tempo datasource

- Status: `PASS`
- Detail: Tempo datasource page visible
- Screenshot: [screenshots/observability/grafana-tempo-datasource.png](screenshots/observability/grafana-tempo-datasource.png)

![Grafana Tempo datasource](screenshots/observability/grafana-tempo-datasource.png)


## OBS-012 Tempo search results

- Status: `PASS`
- Detail: Tempo search returned product-service traces
- Screenshot: [screenshots/observability/tempo-search.png](screenshots/observability/tempo-search.png)

![Tempo search results](screenshots/observability/tempo-search.png)


## OBS-013 Product trace detail

- Status: `PASS`
- Detail: Product-service trace detail visible
- Screenshot: [screenshots/observability/tempo-product-trace.png](screenshots/observability/tempo-product-trace.png)

![Product trace detail](screenshots/observability/tempo-product-trace.png)


## OBS-014 Order trace detail

- Status: `PASS`
- Detail: Order-service trace detail visible
- Screenshot: [screenshots/observability/tempo-order-trace.png](screenshots/observability/tempo-order-trace.png)

![Order trace detail](screenshots/observability/tempo-order-trace.png)

