# Platform Test Case Matrix

This matrix is generated from the rebuilt modular validation framework and represents the exact proof set produced by the latest clean run.

| Component | Test Case | Expected Proof | Screenshot Target | Pass Criteria |
| --- | --- | --- | --- | --- |
| infra | INF-001 Kubernetes inventory artifacts | Pod, service, ingress, ArgoCD app, and ExternalSecret outputs captured | `artifacts/kubernetes-pod-inventory.txt` | `PASS` |
| messaging | MSG-001 Kafka runtime health | Docker runtime proof captured for external Kafka | `artifacts/kafka-runtime-health.txt` | `PASS` |
| messaging | MSG-002 Kafka dashboard proof | Kafka dashboard screenshot will be produced during observability validation | `screenshots/messaging/kafka-dashboard.png` | `PASS` |
| application | APP-001 Frontend login page | Login page visible | `screenshots/application/frontend-login.png` | `PASS` |
| application | APP-002 Frontend signup page | Signup form visible | `screenshots/application/frontend-signup.png` | `PASS` |
| application | APP-003 Signup success state | Signup success notice visible | `screenshots/application/frontend-signup-success.png` | `PASS` |
| application | APP-004 Authenticated dashboard | Dashboard fully visible | `screenshots/application/frontend-dashboard.png` | `PASS` |
| application | APP-005 Product creation form | Filled product form captured | `screenshots/application/product-form.png` | `PASS` |
| application | APP-006 Product list with created items | Created products visible in list | `screenshots/application/product-list.png` | `PASS` |
| application | APP-007 Order ledger populated | Order row visible after buy flow | `screenshots/application/order-ledger.png` | `PASS` |
| application | APP-008 User activity overview | User activity panel visible | `screenshots/application/user-activity.png` | `PASS` |
| gitops | GIT-001 ArgoCD login page | ArgoCD login visible | `screenshots/gitops/argocd-login.png` | `PASS` |
| gitops | GIT-002 ArgoCD applications list | Core app names visible | `screenshots/gitops/argocd-app-list.png` | `PASS` |
| gitops | GIT-003 ArgoCD app detail | Selected app detail visible | `screenshots/gitops/argocd-app-detail.png` | `PASS` |
| secrets | SEC-001 Vault login page | Vault login visible | `screenshots/secrets/vault-login.png` | `PASS` |
| secrets | SEC-002 Vault safe inventory view | Vault secret engines view visible | `screenshots/secrets/vault-secret-inventory.png` | `PASS` |
| secrets | SEC-003 Vault secret proof artifact | Safe secret-path proof written | `artifacts/vault-secret-proof.md` | `PASS` |
| observability | OBS-001 Grafana login | Grafana login page visible | `screenshots/observability/grafana-login.png` | `PASS` |
| observability | OBS-002 Grafana dashboard list | Provisioned dashboard list visible inside the LeninKart folder | `screenshots/observability/grafana-dashboard-list.png` | `PASS` |
| observability | OBS-003 LeninKart Platform Overview | LeninKart Platform Overview rendered with visible content | `screenshots/observability/dashboard-platform.png` | `PASS` |
| observability | OBS-004 LeninKart Product Service Overview | LeninKart Product Service Overview rendered with visible content | `screenshots/observability/dashboard-product.png` | `PASS` |
| observability | OBS-005 LeninKart Order Service Overview | LeninKart Order Service Overview rendered with visible content | `screenshots/observability/dashboard-order.png` | `PASS` |
| observability | OBS-006 LeninKart Frontend Overview | LeninKart Frontend Overview rendered with visible content | `screenshots/observability/dashboard-frontend.png` | `PASS` |
| observability | OBS-007 LeninKart Logs Overview | LeninKart Logs Overview rendered with visible content | `screenshots/observability/dashboard-logs.png` | `PASS` |
| observability | OBS-008 LeninKart Kafka Overview | LeninKart Kafka Overview rendered with visible content | `screenshots/observability/dashboard-kafka.png` | `PASS` |
| observability | OBS-009 Grafana Explore Loki | Loki search returned recent product-service logs | `screenshots/observability/grafana-loki-explore.png` | `PASS` |
| observability | OBS-010 Prometheus targets | Prometheus targets page populated | `screenshots/observability/prometheus-targets.png` | `PASS` |
| observability | OBS-011 Grafana Tempo datasource | Tempo datasource page visible | `screenshots/observability/grafana-tempo-datasource.png` | `PASS` |
| observability | OBS-012 Tempo search results | Tempo search returned product-service traces | `screenshots/observability/tempo-search.png` | `PASS` |
| observability | OBS-013 Product trace detail | Product-service trace detail visible | `screenshots/observability/tempo-product-trace.png` | `PASS` |
| observability | OBS-014 Order trace detail | Order-service trace detail visible | `screenshots/observability/tempo-order-trace.png` | `PASS` |