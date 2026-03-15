# AI Observability Analysis

This report captures the Deep Observer UI and the AI reasoning surfaces validated by the engine.

- Incident count observed: `100`
- First incident service: `product-service`
- Incident detail API OK: `True`

## Explored Pages

### Deep Observer dashboard
The Deep Observer dashboard is the AI observability landing page that correlates metrics, logs, traces, topology, and incidents.

![AI-002-deep-observer-home.png](screenshots/AI-002-deep-observer-home.png)

### AI topology graph
The topology graph shows how Deep Observer reconstructs service dependencies from telemetry, including the product-service to Kafka to order-service path.

![AI-003-deep-observer-topology.png](screenshots/AI-003-deep-observer-topology.png)

### Incident details panel
The incident details panel exposes the reasoning summary, detected signals, root cause hypothesis, and suggested remediation actions.

![AI-004-deep-observer-incident-panel.png](screenshots/AI-004-deep-observer-incident-panel.png)

### Incident detail route
The incident detail route is the drill-down surface for a specific incident and provides durable evidence of the AI reasoning and telemetry context for a selected root cause case.

![AI-004-deep-observer-incident-detail.png](screenshots/AI-004-deep-observer-incident-detail.png)
