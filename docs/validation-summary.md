# Validation Summary

- `infra`: PASS - Infrastructure validation passed
- `gitops`: PASS - GitOps validation passed
- `vault`: PASS - Vault validation passed
- `kafka`: PASS - Kafka validation passed
- `frontend`: PASS - Frontend workflow validation passed
- `api`: PASS - API validation passed
- `database`: PASS - Database validation passed
- `otel_pipeline`: PASS - OTEL pipeline validation passed
- `clickhouse`: PASS - ClickHouse validation passed
- `observability`: PASS - Observability validation passed
- `ai`: PASS - AI validation passed
- `performance`: PASS - Performance validation passed

## Evidence Summary

- Screenshot count: 36
- Kafka topics verified: __consumer_offsets, order-created, order-events, product-events, product-orders, validation-probe
- Vault secret keys verified: api_key, jwt_secret
- Observability sections explored: 18
- AI incident count observed: 100

## Screenshot References

- [screenshots/AI-002-deep-observer-home.png](screenshots/AI-002-deep-observer-home.png)
- [screenshots/AI-003-deep-observer-topology.png](screenshots/AI-003-deep-observer-topology.png)
- [screenshots/AI-004-deep-observer-incident-detail.png](screenshots/AI-004-deep-observer-incident-detail.png)
- [screenshots/AI-004-deep-observer-incident-panel.png](screenshots/AI-004-deep-observer-incident-panel.png)
- [screenshots/FE-001-auth-page.png](screenshots/FE-001-auth-page.png)
- [screenshots/FE-002-signup-success.png](screenshots/FE-002-signup-success.png)
- [screenshots/FE-004-dashboard.png](screenshots/FE-004-dashboard.png)
- [screenshots/FE-008-product-form.png](screenshots/FE-008-product-form.png)
- [screenshots/FE-008-product-list.png](screenshots/FE-008-product-list.png)
- [screenshots/FE-009-order-ledger.png](screenshots/FE-009-order-ledger.png)
- [screenshots/GIT-001-argocd-dashboard.png](screenshots/GIT-001-argocd-dashboard.png)
- [screenshots/GIT-001-argocd-login.png](screenshots/GIT-001-argocd-login.png)
- [screenshots/GIT-003-argocd-product-service.png](screenshots/GIT-003-argocd-product-service.png)
- [screenshots/GIT-005-argocd-history.png](screenshots/GIT-005-argocd-history.png)
- [screenshots/KTEL-004-observer-kafka-detail.png](screenshots/KTEL-004-observer-kafka-detail.png)
- [screenshots/KTEL-004-observer-messaging-overview.png](screenshots/KTEL-004-observer-messaging-overview.png)
- [screenshots/OBS-001-observer-home.png](screenshots/OBS-001-observer-home.png)
- [screenshots/OBS-004-observer-order-service.png](screenshots/OBS-004-observer-order-service.png)
- [screenshots/OBS-004-observer-product-service.png](screenshots/OBS-004-observer-product-service.png)
- [screenshots/OBS-004-observer-service-map.png](screenshots/OBS-004-observer-service-map.png)
- [screenshots/OBS-004-observer-services.png](screenshots/OBS-004-observer-services.png)
- [screenshots/OBS-005-observer-traces.png](screenshots/OBS-005-observer-traces.png)
- [screenshots/OBS-006-observer-logs.png](screenshots/OBS-006-observer-logs.png)
- [screenshots/OBS-007-observer-dashboard-detail.png](screenshots/OBS-007-observer-dashboard-detail.png)
- [screenshots/OBS-007-observer-dashboard-list.png](screenshots/OBS-007-observer-dashboard-list.png)
- [screenshots/OBS-007-observer-infra-hosts.png](screenshots/OBS-007-observer-infra-hosts.png)
- [screenshots/OBS-007-observer-infra-kubernetes.png](screenshots/OBS-007-observer-infra-kubernetes.png)
- [screenshots/OBS-009-observer-alerts.png](screenshots/OBS-009-observer-alerts.png)
- [screenshots/OBS-009-observer-api-monitoring.png](screenshots/OBS-009-observer-api-monitoring.png)
- [screenshots/OBS-009-observer-exceptions.png](screenshots/OBS-009-observer-exceptions.png)
- [screenshots/OBS-011-observer-ai-observer.png](screenshots/OBS-011-observer-ai-observer.png)
- [screenshots/SEC-001-vault-login.png](screenshots/SEC-001-vault-login.png)
- [screenshots/SEC-003-vault-home.png](screenshots/SEC-003-vault-home.png)
- [screenshots/SEC-003-vault-secret-engines.png](screenshots/SEC-003-vault-secret-engines.png)
- [screenshots/SEC-005-vault-secret-paths.png](screenshots/SEC-005-vault-secret-paths.png)
- [screenshots/SEC-006-vault-secret-values.png](screenshots/SEC-006-vault-secret-values.png)

See [validation-results.md](validation-results.md) for the full payload.