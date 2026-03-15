from __future__ import annotations

from pathlib import Path


class DiagramGenerator:
    def __init__(self, docs: Path, diagrams: Path) -> None:
        self.docs = docs
        self.diagrams = diagrams

    def generate(self, model: dict) -> list[str]:
        outputs = {
            'system-architecture.mmd': '''flowchart LR
  Browser --> Frontend
  Frontend --> ProductService
  Frontend --> OrderService
  ProductService --> Postgres
  ProductService --> Kafka
  Kafka --> OrderService
  ProductService --> OTelCollector
  OrderService --> OTelCollector
  OTelCollector --> ObserverStack
  ObserverStack --> ClickHouse
  ObserverStack --> DeepObserver
''',
            'kubernetes-topology.mmd': '''flowchart TD
  subgraph Minikube
    Ingress --> FrontendPod
    Ingress --> ProductPod
    Ingress --> OrderPod
    ProductPod --> PostgresSvc
    OrderPod --> PostgresSvc
    ProductPod --> OTelCollector
    OrderPod --> OTelCollector
  end
  OTelCollector --> HostCollector
  HostCollector --> ClickHouse
''',
            'kafka-event-flow.mmd': '''sequenceDiagram
  participant U as User
  participant F as Frontend
  participant P as Product Service
  participant K as Kafka
  participant O as Order Service
  U->>F: Buy product
  F->>P: POST /api/products/{id}/order
  P->>K: publish product-orders
  K->>O: consume product-orders
  O->>O: persist order
''',
            'vault-secret-flow.mmd': '''flowchart LR
  Vault --> ClusterSecretStore
  ClusterSecretStore --> ExternalSecrets
  ExternalSecrets --> K8sSecrets
  K8sSecrets --> ProductService
  K8sSecrets --> OrderService
''',
            'observability-pipeline.mmd': '''flowchart LR
  Services --> ClusterOTel
  ClusterOTel --> HostOTel
  KafkaJMX --> HostOTel
  HostOTel --> ClickHouse
  ClickHouse --> ObserverStack
  ClickHouse --> DeepObserver
''',
        }
        for name, content in outputs.items():
            (self.diagrams / name).write_text(content, encoding='utf-8')
        return sorted(outputs)
