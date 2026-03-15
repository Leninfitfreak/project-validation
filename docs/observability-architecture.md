# Observability Architecture

This report explains the observability surfaces explored by the validator and what each page represents operationally.

- Observer health endpoint OK: `True`
- Kafka telemetry detected: `True`
- Required service detection OK: `True`

## Explored Pages

### Observer Stack home dashboard
The home dashboard is the landing surface for the observability workspace and confirms that the main telemetry navigation is available to the operator.

![OBS-001-observer-home.png](screenshots/OBS-001-observer-home.png)

- Route: `/home`
- Data present: `True`
- Matched telemetry markers: services, alerts, dashboards

### Services overview
The services overview shows discovered application services and their top-level health signals such as throughput, latency, and error context.

![OBS-004-observer-services.png](screenshots/OBS-004-observer-services.png)

- Route: `/services`
- Data present: `True`
- Matched telemetry markers: product-service, order-service

### Product service metrics page
The product-service detail page exposes service-specific latency, throughput, and error panels for the product and auth workflow.

![OBS-004-observer-product-service.png](screenshots/OBS-004-observer-product-service.png)

- Route: `/services`
- Data present: `True`
- Matched telemetry markers: error, latency

### Order service metrics page
The order-service detail page validates that downstream Kafka consumption and PostgreSQL-backed order reads are represented in the service view.

![OBS-004-observer-order-service.png](screenshots/OBS-004-observer-order-service.png)

- Route: `/services`
- Data present: `True`
- Matched telemetry markers: error, latency

### Dashboard inventory
The dashboard inventory shows the available curated observability boards, including the LeninKart-specific dashboard set.

![OBS-007-observer-dashboard-list.png](screenshots/OBS-007-observer-dashboard-list.png)

- Route: `/dashboard`
- Data present: `True`
- Matched telemetry markers: leninkart, dashboard

### LeninKart dashboard detail
The LeninKart dashboard detail correlates application latency, database wait, and Kafka throughput in one operational view.

![OBS-007-observer-dashboard-detail.png](screenshots/OBS-007-observer-dashboard-detail.png)

- Route: `/dashboard`
- Data present: `True`
- Matched telemetry markers: kafka throughput, database wait time

### Traces explorer
The traces explorer confirms distributed request traces from the frontend-driven product and order flow are ingested and queryable.

![OBS-005-observer-traces.png](screenshots/OBS-005-observer-traces.png)

- Route: `/traces-explorer`
- Data present: `True`
- Matched telemetry markers: product-service

### Logs explorer
The logs explorer validates that application logs from the Spring services are visible in the observability stack and can be correlated with traces.

![OBS-006-observer-logs.png](screenshots/OBS-006-observer-logs.png)

- Route: `/logs/logs-explorer`
- Data present: `True`
- Matched telemetry markers: product-service, order-service

### Messaging queues overview
The messaging overview shows queue-level telemetry derived from Kafka spans and broker metrics for the application event pipeline.

![KTEL-004-observer-messaging-overview.png](screenshots/KTEL-004-observer-messaging-overview.png)

- Route: `/messaging-queues/overview`
- Data present: `True`
- Matched telemetry markers: kafka, product-orders

### Kafka telemetry detail
The Kafka detail page focuses specifically on topic-level telemetry and verifies that the product-orders topic is visible from the observability UI.

![KTEL-004-observer-kafka-detail.png](screenshots/KTEL-004-observer-kafka-detail.png)

- Route: `/messaging-queues/kafka`
- Data present: `False`

### Service dependency map
The service map visualizes inter-service dependencies, including the Kafka edge between product-service and order-service.

![OBS-004-observer-service-map.png](screenshots/OBS-004-observer-service-map.png)

- Route: `/service-map`
- Data present: `False`

### Infrastructure hosts monitoring
The hosts view represents infrastructure-level metrics for the monitored environment.

![OBS-007-observer-infra-hosts.png](screenshots/OBS-007-observer-infra-hosts.png)

- Route: `/infrastructure-monitoring/hosts`
- Data present: `True`
- Matched telemetry markers: host, cpu, memory

### Kubernetes infrastructure monitoring
The Kubernetes infrastructure view shows cluster-level telemetry such as node and pod health surfaces.

![OBS-007-observer-infra-kubernetes.png](screenshots/OBS-007-observer-infra-kubernetes.png)

- Route: `/infrastructure-monitoring/kubernetes`
- Data present: `True`
- Matched telemetry markers: node, pod, cluster

### Exception tracking
The exceptions section is used to inspect aggregated application exceptions when exception telemetry is available.

![OBS-009-observer-exceptions.png](screenshots/OBS-009-observer-exceptions.png)

- Route: `/exceptions`
- Data present: `True`
- Matched telemetry markers: exception, error

### External API monitoring
The API monitoring explorer is intended for upstream and downstream API observation when external API traffic is instrumented.

![OBS-009-observer-api-monitoring.png](screenshots/OBS-009-observer-api-monitoring.png)

- Route: `/api-monitoring/explorer`
- Data present: `False`

### Telemetry cost and usage analytics
The usage explorer provides telemetry volume and cost analytics for the observability platform itself.

- Route: `/usage-explorer`
- Data present: `False`

### Alerts overview
The alerts overview confirms that the alerting subsystem is available and exposes rules, triggered alerts, and configuration surfaces.

![OBS-009-observer-alerts.png](screenshots/OBS-009-observer-alerts.png)

- Route: `/alerts/overview`
- Data present: `True`
- Matched telemetry markers: triggered alerts, alert rules, configuration

### Embedded AI Observer dashboard
The embedded AI Observer route connects the core observability workspace to the Deep Observer analysis experience.

![OBS-011-observer-ai-observer.png](screenshots/OBS-011-observer-ai-observer.png)

- Route: `/ai-observer`
- Data present: `True`
- Matched telemetry markers: root cause, incident
