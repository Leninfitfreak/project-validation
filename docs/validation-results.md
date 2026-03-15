# Validation Results

```json
[
  {
    "name": "infra",
    "success": true,
    "summary": "Infrastructure validation passed",
    "details": {
      "nodes": [
        "minikube"
      ],
      "namespaces": [
        "argocd",
        "default",
        "dev",
        "external-secrets-system",
        "ingress-nginx",
        "kube-node-lease",
        "kube-public",
        "kube-system",
        "vault"
      ],
      "core_workloads": {
        "frontend": true,
        "product-service": true,
        "order-service": true,
        "postgres": true,
        "otel-collector": true
      },
      "service_count": 33,
      "ingress_paths": [
        "/",
        "/api/orders",
        "/api/products",
        "/auth"
      ],
      "bad_core_pods": []
    },
    "repairs": [],
    "test_ids": [
      "INF-001",
      "INF-002",
      "INF-003",
      "INF-004",
      "INF-005",
      "INF-006"
    ]
  },
  {
    "name": "gitops",
    "success": true,
    "summary": "GitOps validation passed",
    "details": {
      "applications": [
        {
          "name": "dev-ingress",
          "sync": "Synced",
          "health": "Healthy"
        },
        {
          "name": "dev-order-service",
          "sync": "Synced",
          "health": "Healthy"
        },
        {
          "name": "dev-product-service",
          "sync": "Synced",
          "health": "Healthy"
        },
        {
          "name": "external-secrets-operator",
          "sync": "Synced",
          "health": "Healthy"
        },
        {
          "name": "frontend-dev",
          "sync": "Synced",
          "health": "Healthy"
        },
        {
          "name": "leninkart-root",
          "sync": "Synced",
          "health": "Healthy"
        },
        {
          "name": "loadtest-dev",
          "sync": "Synced",
          "health": "Healthy"
        },
        {
          "name": "otel-collector-dev",
          "sync": "Synced",
          "health": "Healthy"
        },
        {
          "name": "postgres-dev",
          "sync": "Synced",
          "health": "Healthy"
        },
        {
          "name": "vault",
          "sync": "Synced",
          "health": "Healthy"
        },
        {
          "name": "vault-externalsecrets",
          "sync": "Synced",
          "health": "Healthy"
        },
        {
          "name": "vault-secretstore",
          "sync": "Synced",
          "health": "Healthy"
        },
        {
          "name": "vault-secretstores-dev",
          "sync": "OutOfSync",
          "health": "Healthy"
        }
      ],
      "failing": [],
      "screenshots": [
        "GIT-001-argocd-login.png",
        "GIT-001-argocd-dashboard.png",
        "GIT-003-argocd-product-service.png",
        "GIT-005-argocd-history.png"
      ],
      "sections": [
        {
          "title": "ArgoCD login page",
          "screenshot": "GIT-001-argocd-login.png",
          "explanation": "The ArgoCD login page verifies that the GitOps dashboard is reachable and ready for operator access."
        },
        {
          "title": "Applications dashboard",
          "screenshot": "GIT-001-argocd-dashboard.png",
          "explanation": "The applications dashboard is the GitOps inventory view and shows sync and health state for each managed application."
        },
        {
          "title": "Product-service application detail",
          "screenshot": "GIT-003-argocd-product-service.png",
          "explanation": "The product-service application detail page exposes sync state, resource tree, and deployment health for the product API workload."
        },
        {
          "title": "Deployment history",
          "screenshot": "GIT-005-argocd-history.png",
          "explanation": "The deployment history confirms that GitOps revisions are tracked and rollback-capable through ArgoCD."
        }
      ]
    },
    "repairs": [],
    "test_ids": [
      "GIT-001",
      "GIT-002",
      "GIT-003",
      "GIT-004",
      "GIT-005",
      "UI-002"
    ]
  },
  {
    "name": "vault",
    "success": true,
    "summary": "Vault validation passed",
    "details": {
      "vault_ready": true,
      "sealed": false,
      "store_ready": true,
      "external_secrets": {
        "ai-observer-secrets": true,
        "kafka-creds": true,
        "order-service-config": true,
        "order-service-db-creds": true,
        "postgres-secret": true,
        "product-service-config": true,
        "product-service-db-creds": true
      },
      "kv_paths": [
        "agent_token",
        "ai-observer",
        "db",
        "kafka",
        "order-service",
        "postgres",
        "product-service"
      ],
      "secret_value_keys": [
        "api_key",
        "jwt_secret"
      ],
      "screenshots": [
        "SEC-001-vault-login.png",
        "SEC-003-vault-home.png",
        "SEC-003-vault-secret-engines.png",
        "SEC-005-vault-secret-paths.png",
        "SEC-006-vault-secret-values.png"
      ],
      "sections": [
        {
          "title": "Vault login page",
          "screenshot": "SEC-001-vault-login.png",
          "explanation": "The Vault login page confirms that the secrets management UI is reachable."
        },
        {
          "title": "Vault home",
          "screenshot": "SEC-003-vault-home.png",
          "explanation": "The Vault home view confirms successful authentication and exposes the operational workspace for secrets engines and quick actions."
        },
        {
          "title": "Secrets engine list",
          "screenshot": "SEC-003-vault-secret-engines.png",
          "explanation": "The secrets engine list shows the mounted secret backends, including the KV engine used by LeninKart."
        },
        {
          "title": "KV secret paths",
          "screenshot": "SEC-005-vault-secret-paths.png",
          "explanation": "The Vault path view provides evidence that the LeninKart KV hierarchy is present under the mounted secret engine."
        },
        {
          "title": "Secret key and value evidence",
          "screenshot": "SEC-006-vault-secret-values.png",
          "explanation": "This evidence view renders the extracted KV secret data for the product-service configuration so the validator can prove real key presence without navigating brittle Vault UI internals for each value."
        }
      ]
    },
    "repairs": [],
    "test_ids": [
      "SEC-001",
      "SEC-002",
      "SEC-003",
      "SEC-004",
      "SEC-005",
      "SEC-006",
      "SEC-007",
      "UI-003"
    ]
  },
  {
    "name": "kafka",
    "success": true,
    "summary": "Kafka validation passed",
    "details": {
      "topics": [
        "__consumer_offsets",
        "order-created",
        "order-events",
        "product-events",
        "product-orders",
        "validation-probe"
      ],
      "probe_output": "validation-probe-message\nvalidation-probe-message\nvalidation-probe-message\nvalidation-probe-message\nvalidation-probe-message\nvalidation-probe-message\nvalidation-probe-message\nvalidation-probe-message\nvalidation-probe-message\nvalidation-probe-message",
      "jmx_metrics_present": true,
      "minikube_gateway": "192.168.49.1",
      "kafka_minikube_ip": "192.168.49.3"
    },
    "repairs": [],
    "test_ids": [
      "MQ-001",
      "MQ-002",
      "MQ-003",
      "MQ-004",
      "MQ-005",
      "MQ-006",
      "MQ-007"
    ]
  },
  {
    "name": "frontend",
    "success": true,
    "summary": "Frontend workflow validation passed",
    "details": {
      "user_email": "validator-tjtrmswyzd@example.com",
      "product_name": "Validation Product xkxwve",
      "product_visible": true,
      "order_ledger_visible": true,
      "screenshots": [
        "FE-001-auth-page.png",
        "FE-002-signup-success.png",
        "FE-004-dashboard.png",
        "FE-008-product-form.png",
        "FE-008-product-list.png",
        "FE-009-order-ledger.png"
      ],
      "timings": {
        "auth_page_seconds": 0.35,
        "dashboard_seconds": 0.95,
        "product_create_seconds": 0.33,
        "order_ledger_seconds": 33.19
      },
      "orders_requested": 20
    },
    "repairs": [],
    "test_ids": [
      "FE-001",
      "FE-002",
      "FE-004",
      "FE-008",
      "FE-009",
      "FE-010",
      "UI-001",
      "UI-006"
    ]
  },
  {
    "name": "api",
    "success": true,
    "summary": "API validation passed",
    "details": {
      "signup_status": "200",
      "duplicate_signup_status": "409",
      "login_status": "200",
      "bad_login_status": "401",
      "create_product_status": "200",
      "order_status": "200",
      "missing_order_status": "404",
      "orders_status": "200",
      "user_scope_ok": true
    },
    "repairs": [],
    "test_ids": [
      "API-001",
      "API-002",
      "API-003",
      "API-004",
      "API-006",
      "API-007",
      "API-008",
      "API-009",
      "API-010"
    ]
  },
  {
    "name": "database",
    "success": true,
    "summary": "Database validation passed",
    "details": {
      "user_count": 1,
      "product_count": 1,
      "order_count": 20,
      "ordering_check": "1"
    },
    "repairs": [],
    "test_ids": [
      "DB-001",
      "DB-002",
      "DB-003",
      "DB-004"
    ]
  },
  {
    "name": "otel_pipeline",
    "success": true,
    "summary": "OTEL pipeline validation passed",
    "details": {
      "cluster_collector_ready": true,
      "host_collector_running": true,
      "service_dockerfiles_configured_for_otel": true,
      "traffic_generated": true
    },
    "repairs": [],
    "test_ids": [
      "OTEL-001",
      "OTEL-002",
      "OTEL-003",
      "OTEL-004",
      "OTEL-005"
    ]
  },
  {
    "name": "clickhouse",
    "success": true,
    "summary": "ClickHouse validation passed",
    "details": {
      "running": true,
      "databases": [
        "INFORMATION_SCHEMA",
        "default",
        "information_schema",
        "signoz_analytics",
        "signoz_logs",
        "signoz_metadata",
        "signoz_meter",
        "signoz_metrics",
        "signoz_traces",
        "system"
      ],
      "trace_rows": 3938726,
      "metric_rows": 191038,
      "log_rows": 24001
    },
    "repairs": [],
    "test_ids": [
      "CH-001",
      "CH-002",
      "CH-003",
      "CH-004",
      "CH-005",
      "CH-006"
    ]
  },
  {
    "name": "observability",
    "success": true,
    "summary": "Observability validation passed",
    "details": {
      "screenshots": [
        "OBS-001-observer-home.png",
        "OBS-004-observer-services.png",
        "OBS-004-observer-product-service.png",
        "OBS-004-observer-order-service.png",
        "OBS-007-observer-dashboard-list.png",
        "OBS-007-observer-dashboard-detail.png",
        "OBS-005-observer-traces.png",
        "OBS-006-observer-logs.png",
        "KTEL-004-observer-messaging-overview.png",
        "KTEL-004-observer-kafka-detail.png",
        "OBS-004-observer-service-map.png",
        "OBS-007-observer-infra-hosts.png",
        "OBS-007-observer-infra-kubernetes.png",
        "OBS-009-observer-exceptions.png",
        "OBS-009-observer-api-monitoring.png",
        "OBS-009-observer-alerts.png",
        "OBS-011-observer-ai-observer.png"
      ],
      "sections": [
        {
          "title": "Observer Stack home dashboard",
          "path": "/home",
          "url": "http://127.0.0.1:8080/home",
          "screenshot": "OBS-001-observer-home.png",
          "explanation": "The home dashboard is the landing surface for the observability workspace and confirms that the main telemetry navigation is available to the operator.",
          "data_present": true,
          "required_data": false,
          "critical": true,
          "matched_terms": [
            "services",
            "alerts",
            "dashboards"
          ],
          "status": "ok"
        },
        {
          "title": "Services overview",
          "path": "/services",
          "url": "http://127.0.0.1:8080/services?relativeTime=30m",
          "screenshot": "OBS-004-observer-services.png",
          "explanation": "The services overview shows discovered application services and their top-level health signals such as throughput, latency, and error context.",
          "data_present": true,
          "required_data": true,
          "critical": true,
          "matched_terms": [
            "product-service",
            "order-service"
          ],
          "status": "ok"
        },
        {
          "title": "Product service metrics page",
          "path": "/services",
          "url": "http://127.0.0.1:8080/services/product-service?relativeTime=30m",
          "screenshot": "OBS-004-observer-product-service.png",
          "explanation": "The product-service detail page exposes service-specific latency, throughput, and error panels for the product and auth workflow.",
          "data_present": true,
          "required_data": true,
          "critical": true,
          "matched_terms": [
            "error",
            "latency"
          ],
          "status": "ok"
        },
        {
          "title": "Order service metrics page",
          "path": "/services",
          "url": "http://127.0.0.1:8080/services/order-service?relativeTime=30m",
          "screenshot": "OBS-004-observer-order-service.png",
          "explanation": "The order-service detail page validates that downstream Kafka consumption and PostgreSQL-backed order reads are represented in the service view.",
          "data_present": true,
          "required_data": true,
          "critical": true,
          "matched_terms": [
            "error",
            "latency"
          ],
          "status": "ok"
        },
        {
          "title": "Dashboard inventory",
          "path": "/dashboard",
          "url": "http://127.0.0.1:8080/dashboard",
          "screenshot": "OBS-007-observer-dashboard-list.png",
          "explanation": "The dashboard inventory shows the available curated observability boards, including the LeninKart-specific dashboard set.",
          "data_present": true,
          "required_data": false,
          "critical": false,
          "matched_terms": [
            "leninkart",
            "dashboard"
          ],
          "status": "ok"
        },
        {
          "title": "LeninKart dashboard detail",
          "path": "/dashboard",
          "url": "http://127.0.0.1:8080/dashboard/019cc98c-149b-7103-91fc-730c61b1447b?relativeTime=30m",
          "screenshot": "OBS-007-observer-dashboard-detail.png",
          "explanation": "The LeninKart dashboard detail correlates application latency, database wait, and Kafka throughput in one operational view.",
          "data_present": true,
          "required_data": true,
          "critical": true,
          "matched_terms": [
            "kafka throughput",
            "database wait time"
          ],
          "status": "ok"
        },
        {
          "title": "Traces explorer",
          "path": "/traces-explorer",
          "url": "http://127.0.0.1:8080/traces-explorer?compositeQuery=%257B%2522queryType%2522%253A%2522builder%2522%252C%2522builder%2522%253A%257B%2522queryData%2522%253A%255B%257B%2522dataSource%2522%253A%2522traces%2522%252C%2522queryName%2522%253A%2522A%2522%252C%2522aggregateAttribute%2522%253A%257B%2522id%2522%253A%2522----%2522%252C%2522dataType%2522%253A%2522%2522%252C%2522key%2522%253A%2522%2522%252C%2522type%2522%253A%2522%2522%257D%252C%2522timeAggregation%2522%253A%2522rate%2522%252C%2522spaceAggregation%2522%253A%2522sum%2522%252C%2522filter%2522%253A%257B%2522expression%2522%253A%2522%2522%257D%252C%2522aggregations%2522%253A%255B%257B%2522expression%2522%253A%2522count%28%29%2520%2522%257D%255D%252C%2522functions%2522%253A%255B%255D%252C%2522filters%2522%253A%257B%2522items%2522%253A%255B%255D%252C%2522op%2522%253A%2522AND%2522%257D%252C%2522expression%2522%253A%2522A%2522%252C%2522disabled%2522%253Afalse%252C%2522stepInterval%2522%253Anull%252C%2522having%2522%253A%255B%255D%252C%2522limit%2522%253Anull%252C%2522orderBy%2522%253A%255B%255D%252C%2522groupBy%2522%253A%255B%255D%252C%2522legend%2522%253A%2522%2522%252C%2522reduceTo%2522%253A%2522avg%2522%257D%255D%252C%2522queryFormulas%2522%253A%255B%255D%252C%2522queryTraceOperator%2522%253A%255B%255D%257D%252C%2522promql%2522%253A%255B%257B%2522name%2522%253A%2522A%2522%252C%2522query%2522%253A%2522%2522%252C%2522legend%2522%253A%2522%2522%252C%2522disabled%2522%253Afalse%257D%255D%252C%2522clickhouse_sql%2522%253A%255B%257B%2522name%2522%253A%2522A%2522%252C%2522legend%2522%253A%2522%2522%252C%2522disabled%2522%253Afalse%252C%2522query%2522%253A%2522%2522%257D%255D%252C%2522id%2522%253A%252279d5d926-c4f3-4011-b33c-39a8f44cea1f%2522%252C%2522unit%2522%253A%2522%2522%257D&options=%7B%22selectColumns%22%3A%5B%7B%22name%22%3A%22service.name%22%2C%22signal%22%3A%22traces%22%2C%22fieldContext%22%3A%22resource%22%2C%22fieldDataType%22%3A%22string%22%7D%2C%7B%22name%22%3A%22name%22%2C%22signal%22%3A%22traces%22%2C%22fieldContext%22%3A%22span%22%2C%22fieldDataType%22%3A%22string%22%7D%2C%7B%22name%22%3A%22duration_nano%22%2C%22signal%22%3A%22traces%22%2C%22fieldContext%22%3A%22span%22%2C%22fieldDataType%22%3A%22%22%7D%2C%7B%22name%22%3A%22http_method%22%2C%22signal%22%3A%22traces%22%2C%22fieldContext%22%3A%22span%22%2C%22fieldDataType%22%3A%22%22%7D%2C%7B%22name%22%3A%22response_status_code%22%2C%22signal%22%3A%22traces%22%2C%22fieldContext%22%3A%22span%22%2C%22fieldDataType%22%3A%22%22%7D%5D%2C%22maxLines%22%3A1%2C%22format%22%3A%22raw%22%2C%22fontSize%22%3A%22small%22%7D&pagination=%7B%22offset%22%3A0%2C%22limit%22%3A10%7D",
          "screenshot": "OBS-005-observer-traces.png",
          "explanation": "The traces explorer confirms distributed request traces from the frontend-driven product and order flow are ingested and queryable.",
          "data_present": true,
          "required_data": true,
          "critical": true,
          "matched_terms": [
            "product-service"
          ],
          "status": "ok"
        },
        {
          "title": "Logs explorer",
          "path": "/logs/logs-explorer",
          "url": "http://127.0.0.1:8080/logs/logs-explorer?compositeQuery=%257B%2522queryType%2522%253A%2522builder%2522%252C%2522builder%2522%253A%257B%2522queryData%2522%253A%255B%257B%2522dataSource%2522%253A%2522logs%2522%252C%2522queryName%2522%253A%2522A%2522%252C%2522aggregateAttribute%2522%253A%257B%2522id%2522%253A%2522----%2522%252C%2522dataType%2522%253A%2522%2522%252C%2522key%2522%253A%2522%2522%252C%2522type%2522%253A%2522%2522%257D%252C%2522timeAggregation%2522%253A%2522rate%2522%252C%2522spaceAggregation%2522%253A%2522sum%2522%252C%2522filter%2522%253A%257B%2522expression%2522%253A%2522%2522%257D%252C%2522aggregations%2522%253A%255B%257B%2522expression%2522%253A%2522count%28%29%2520%2522%257D%255D%252C%2522functions%2522%253A%255B%255D%252C%2522filters%2522%253A%257B%2522items%2522%253A%255B%255D%252C%2522op%2522%253A%2522AND%2522%257D%252C%2522expression%2522%253A%2522A%2522%252C%2522disabled%2522%253Afalse%252C%2522stepInterval%2522%253Anull%252C%2522having%2522%253A%255B%255D%252C%2522limit%2522%253Anull%252C%2522orderBy%2522%253A%255B%255D%252C%2522groupBy%2522%253A%255B%255D%252C%2522legend%2522%253A%2522%2522%252C%2522reduceTo%2522%253A%2522avg%2522%257D%255D%252C%2522queryFormulas%2522%253A%255B%255D%252C%2522queryTraceOperator%2522%253A%255B%255D%257D%252C%2522promql%2522%253A%255B%257B%2522name%2522%253A%2522A%2522%252C%2522query%2522%253A%2522%2522%252C%2522legend%2522%253A%2522%2522%252C%2522disabled%2522%253Afalse%257D%255D%252C%2522clickhouse_sql%2522%253A%255B%257B%2522name%2522%253A%2522A%2522%252C%2522legend%2522%253A%2522%2522%252C%2522disabled%2522%253Afalse%252C%2522query%2522%253A%2522%2522%257D%255D%252C%2522id%2522%253A%252299dd6a74-ed65-4fc6-9df5-49385b267148%2522%252C%2522unit%2522%253A%2522%2522%257D&options=%7B%22selectColumns%22%3A%5B%7B%22name%22%3A%22timestamp%22%2C%22signal%22%3A%22logs%22%2C%22fieldContext%22%3A%22log%22%2C%22fieldDataType%22%3A%22%22%2C%22isIndexed%22%3Afalse%7D%2C%7B%22name%22%3A%22body%22%2C%22signal%22%3A%22logs%22%2C%22fieldContext%22%3A%22log%22%2C%22fieldDataType%22%3A%22%22%2C%22isIndexed%22%3Afalse%7D%5D%2C%22maxLines%22%3A1%2C%22format%22%3A%22raw%22%2C%22fontSize%22%3A%22small%22%7D",
          "screenshot": "OBS-006-observer-logs.png",
          "explanation": "The logs explorer validates that application logs from the Spring services are visible in the observability stack and can be correlated with traces.",
          "data_present": true,
          "required_data": true,
          "critical": true,
          "matched_terms": [
            "product-service",
            "order-service"
          ],
          "status": "ok"
        },
        {
          "title": "Messaging queues overview",
          "path": "/messaging-queues/overview",
          "url": "http://127.0.0.1:8080/messaging-queues/overview?relativeTime=30m",
          "screenshot": "KTEL-004-observer-messaging-overview.png",
          "explanation": "The messaging overview shows queue-level telemetry derived from Kafka spans and broker metrics for the application event pipeline.",
          "data_present": true,
          "required_data": true,
          "critical": true,
          "matched_terms": [
            "kafka",
            "product-orders"
          ],
          "status": "ok"
        },
        {
          "title": "Kafka telemetry detail",
          "path": "/messaging-queues/kafka",
          "url": "http://127.0.0.1:8080/messaging-queues/kafka?relativeTime=30m",
          "screenshot": "KTEL-004-observer-kafka-detail.png",
          "explanation": "The Kafka detail page focuses specifically on topic-level telemetry and verifies that the product-orders topic is visible from the observability UI.",
          "data_present": false,
          "required_data": false,
          "critical": false,
          "matched_terms": [],
          "status": "ok"
        },
        {
          "title": "Service dependency map",
          "path": "/service-map",
          "url": "http://127.0.0.1:8080/service-map?relativeTime=30m",
          "screenshot": "OBS-004-observer-service-map.png",
          "explanation": "The service map visualizes inter-service dependencies, including the Kafka edge between product-service and order-service.",
          "data_present": false,
          "required_data": false,
          "critical": false,
          "matched_terms": [],
          "status": "ok"
        },
        {
          "title": "Infrastructure hosts monitoring",
          "path": "/infrastructure-monitoring/hosts",
          "url": "http://127.0.0.1:8080/infrastructure-monitoring/hosts?relativeTime=30m&filters=%7B%22items%22%3A%5B%5D%2C%22op%22%3A%22AND%22%7D",
          "screenshot": "OBS-007-observer-infra-hosts.png",
          "explanation": "The hosts view represents infrastructure-level metrics for the monitored environment.",
          "data_present": true,
          "required_data": false,
          "critical": false,
          "matched_terms": [
            "host",
            "cpu",
            "memory"
          ],
          "status": "ok"
        },
        {
          "title": "Kubernetes infrastructure monitoring",
          "path": "/infrastructure-monitoring/kubernetes",
          "url": "http://127.0.0.1:8080/infrastructure-monitoring/kubernetes?currentPage=1&filters=%7B%22items%22%3A%5B%5D%2C%22op%22%3A%22AND%22%7D",
          "screenshot": "OBS-007-observer-infra-kubernetes.png",
          "explanation": "The Kubernetes infrastructure view shows cluster-level telemetry such as node and pod health surfaces.",
          "data_present": true,
          "required_data": false,
          "critical": false,
          "matched_terms": [
            "node",
            "pod",
            "cluster"
          ],
          "status": "ok"
        },
        {
          "title": "Exception tracking",
          "path": "/exceptions",
          "url": "http://127.0.0.1:8080/exceptions?compositeQuery=%257B%2522queryType%2522%253A%2522builder%2522%252C%2522builder%2522%253A%257B%2522queryData%2522%253A%255B%257B%2522dataSource%2522%253A%2522traces%2522%252C%2522queryName%2522%253A%2522%2522%252C%2522aggregateOperator%2522%253A%2522noop%2522%252C%2522aggregateAttribute%2522%253A%257B%2522id%2522%253A%2522----%2522%252C%2522dataType%2522%253A%2522%2522%252C%2522key%2522%253A%2522%2522%252C%2522type%2522%253A%2522resource%2522%257D%252C%2522timeAggregation%2522%253A%2522rate%2522%252C%2522spaceAggregation%2522%253A%2522sum%2522%252C%2522filter%2522%253A%257B%2522expression%2522%253A%2522%2522%257D%252C%2522aggregations%2522%253A%255B%257B%2522expression%2522%253A%2522count%28%29%2520%2522%257D%255D%252C%2522functions%2522%253A%255B%255D%252C%2522filters%2522%253A%257B%2522items%2522%253A%255B%255D%252C%2522op%2522%253A%2522AND%2522%257D%252C%2522expression%2522%253A%2522A%2522%252C%2522disabled%2522%253Afalse%252C%2522stepInterval%2522%253Anull%252C%2522having%2522%253A%255B%255D%252C%2522limit%2522%253Anull%252C%2522orderBy%2522%253A%255B%255D%252C%2522groupBy%2522%253A%255B%255D%252C%2522legend%2522%253A%2522%2522%252C%2522reduceTo%2522%253A%2522avg%2522%252C%2522source%2522%253A%2522%2522%257D%255D%252C%2522queryFormulas%2522%253A%255B%255D%252C%2522queryTraceOperator%2522%253A%255B%255D%257D%252C%2522promql%2522%253A%255B%257B%2522name%2522%253A%2522A%2522%252C%2522query%2522%253A%2522%2522%252C%2522legend%2522%253A%2522%2522%252C%2522disabled%2522%253Afalse%257D%255D%252C%2522clickhouse_sql%2522%253A%255B%257B%2522name%2522%253A%2522A%2522%252C%2522legend%2522%253A%2522%2522%252C%2522disabled%2522%253Afalse%252C%2522query%2522%253A%2522%2522%257D%255D%252C%2522id%2522%253A%25229c76687b-8f3c-40df-8567-4777dba219be%2522%252C%2522unit%2522%253A%2522%2522%257D",
          "screenshot": "OBS-009-observer-exceptions.png",
          "explanation": "The exceptions section is used to inspect aggregated application exceptions when exception telemetry is available.",
          "data_present": true,
          "required_data": false,
          "critical": false,
          "matched_terms": [
            "exception",
            "error"
          ],
          "status": "ok"
        },
        {
          "title": "External API monitoring",
          "path": "/api-monitoring/explorer",
          "url": "http://127.0.0.1:8080/api-monitoring/explorer?compositeQuery=%257B%2522queryType%2522%253A%2522builder%2522%252C%2522builder%2522%253A%257B%2522queryData%2522%253A%255B%257B%2522dataSource%2522%253A%2522traces%2522%252C%2522queryName%2522%253A%2522A%2522%252C%2522aggregateOperator%2522%253A%2522noop%2522%252C%2522aggregateAttribute%2522%253A%257B%2522id%2522%253A%2522----%2522%252C%2522dataType%2522%253A%2522%2522%252C%2522key%2522%253A%2522%2522%252C%2522type%2522%253A%2522%2522%257D%252C%2522timeAggregation%2522%253A%2522rate%2522%252C%2522spaceAggregation%2522%253A%2522sum%2522%252C%2522filter%2522%253A%257B%2522expression%2522%253A%2522%2522%257D%252C%2522aggregations%2522%253A%255B%257B%2522expression%2522%253A%2522count%28%29%2520%2522%257D%255D%252C%2522functions%2522%253A%255B%255D%252C%2522filters%2522%253A%257B%2522items%2522%253A%255B%255D%252C%2522op%2522%253A%2522AND%2522%257D%252C%2522expression%2522%253A%2522A%2522%252C%2522disabled%2522%253Afalse%252C%2522stepInterval%2522%253Anull%252C%2522having%2522%253A%255B%255D%252C%2522limit%2522%253Anull%252C%2522orderBy%2522%253A%255B%255D%252C%2522groupBy%2522%253A%255B%255D%252C%2522legend%2522%253A%2522%2522%252C%2522reduceTo%2522%253A%2522avg%2522%252C%2522source%2522%253A%2522%2522%257D%255D%252C%2522queryFormulas%2522%253A%255B%255D%252C%2522queryTraceOperator%2522%253A%255B%255D%257D%252C%2522promql%2522%253A%255B%257B%2522name%2522%253A%2522A%2522%252C%2522query%2522%253A%2522%2522%252C%2522legend%2522%253A%2522%2522%252C%2522disabled%2522%253Afalse%257D%255D%252C%2522clickhouse_sql%2522%253A%255B%257B%2522name%2522%253A%2522A%2522%252C%2522legend%2522%253A%2522%2522%252C%2522disabled%2522%253Afalse%252C%2522query%2522%253A%2522%2522%257D%255D%252C%2522id%2522%253A%2522becddec6-18dd-4903-82e4-32ce2887c6c0%2522%252C%2522unit%2522%253A%2522%2522%257D",
          "screenshot": "OBS-009-observer-api-monitoring.png",
          "explanation": "The API monitoring explorer is intended for upstream and downstream API observation when external API traffic is instrumented.",
          "data_present": false,
          "required_data": false,
          "critical": false,
          "matched_terms": [],
          "status": "ok"
        },
        {
          "title": "Telemetry cost and usage analytics",
          "path": "/usage-explorer",
          "url": "http://127.0.0.1:8080/usage-explorer",
          "screenshot": "",
          "explanation": "The usage explorer provides telemetry volume and cost analytics for the observability platform itself.",
          "data_present": false,
          "required_data": false,
          "critical": false,
          "matched_terms": [],
          "status": "not-captured: missing required text: usage"
        },
        {
          "title": "Alerts overview",
          "path": "/alerts/overview",
          "url": "http://127.0.0.1:8080/alerts/overview",
          "screenshot": "OBS-009-observer-alerts.png",
          "explanation": "The alerts overview confirms that the alerting subsystem is available and exposes rules, triggered alerts, and configuration surfaces.",
          "data_present": true,
          "required_data": false,
          "critical": false,
          "matched_terms": [
            "triggered alerts",
            "alert rules",
            "configuration"
          ],
          "status": "ok"
        },
        {
          "title": "Embedded AI Observer dashboard",
          "path": "/ai-observer",
          "url": "http://127.0.0.1:8080/ai-observer?relativeTime=30m",
          "screenshot": "OBS-011-observer-ai-observer.png",
          "explanation": "The embedded AI Observer route connects the core observability workspace to the Deep Observer analysis experience.",
          "data_present": true,
          "required_data": true,
          "critical": true,
          "matched_terms": [
            "root cause",
            "incident"
          ],
          "status": "ok"
        }
      ],
      "observer_health": true,
      "kafka_metrics": true,
      "detected_services": {
        "frontend": false,
        "product-service": false,
        "order-service": false
      },
      "fallback_detected_services": {
        "frontend": false,
        "product-service": true,
        "order-service": true
      },
      "topology_nodes": [
        "kafka",
        "order-service",
        "postgres",
        "product-service"
      ],
      "frontend_service_detected": false,
      "required_service_detection_ok": true,
      "critical_sections_ok": true
    },
    "repairs": [],
    "test_ids": [
      "OBS-001",
      "OBS-004",
      "OBS-005",
      "OBS-006",
      "OBS-007",
      "OBS-008",
      "OBS-009",
      "OBS-011",
      "KTEL-001",
      "KTEL-004",
      "UI-004"
    ]
  },
  {
    "name": "ai",
    "success": true,
    "summary": "AI validation passed",
    "details": {
      "screenshots": [
        "AI-002-deep-observer-home.png",
        "AI-003-deep-observer-topology.png",
        "AI-004-deep-observer-incident-panel.png",
        "AI-004-deep-observer-incident-detail.png"
      ],
      "sections": [
        {
          "title": "Deep Observer dashboard",
          "screenshot": "AI-002-deep-observer-home.png",
          "explanation": "The Deep Observer dashboard is the AI observability landing page that correlates metrics, logs, traces, topology, and incidents."
        },
        {
          "title": "AI topology graph",
          "screenshot": "AI-003-deep-observer-topology.png",
          "explanation": "The topology graph shows how Deep Observer reconstructs service dependencies from telemetry, including the product-service to Kafka to order-service path."
        },
        {
          "title": "Incident details panel",
          "screenshot": "AI-004-deep-observer-incident-panel.png",
          "explanation": "The incident details panel exposes the reasoning summary, detected signals, root cause hypothesis, and suggested remediation actions."
        },
        {
          "title": "Incident detail route",
          "screenshot": "AI-004-deep-observer-incident-detail.png",
          "explanation": "The incident detail route is the drill-down surface for a specific incident and provides durable evidence of the AI reasoning and telemetry context for a selected root cause case."
        }
      ],
      "incident_count": 100,
      "topology_status": 200,
      "first_incident_id": "d3e40640-5ba9-42ea-b2d3-f31c96379085",
      "first_service": "product-service",
      "incident_detail_ok": true
    },
    "repairs": [],
    "test_ids": [
      "AI-001",
      "AI-002",
      "AI-003",
      "AI-004",
      "AI-005",
      "UI-005"
    ]
  },
  {
    "name": "performance",
    "success": true,
    "summary": "Performance validation passed",
    "details": {
      "timings": {
        "auth_page_seconds": 0.35,
        "dashboard_seconds": 0.95,
        "product_create_seconds": 0.33,
        "order_ledger_seconds": 33.19
      },
      "thresholds": {
        "auth_page_seconds": 12,
        "dashboard_seconds": 15,
        "product_create_seconds": 15,
        "order_ledger_seconds": 180
      },
      "failures": {}
    },
    "repairs": [],
    "test_ids": [
      "PERF-001",
      "PERF-002",
      "PERF-003",
      "PERF-004"
    ]
  }
]
```
