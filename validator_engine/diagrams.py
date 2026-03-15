from __future__ import annotations

from .config import PATHS
from .utils import ensure_dirs, write_text

SYSTEM_ARCH_MMD = """flowchart LR
  Browser[User Browser] --> Frontend[LeninKart Frontend]
  Frontend --> Product[Product Service]
  Frontend --> OrderApi[Order Service API]
  Product --> Postgres[(PostgreSQL)]
  Product --> Kafka[Kafka Broker]
  Kafka --> OrderConsumer[Order Service Consumer]
  OrderConsumer --> Postgres
  Product --> OTelCluster[In-cluster OTEL Collector]
  OrderConsumer --> OTelCluster
  Kafka --> OTelHost[Host OTEL Collector]
  OTelCluster --> OTelHost
  OTelHost --> ClickHouse[(ClickHouse)]
  ClickHouse --> Observer[Observer Stack]
  ClickHouse --> DeepObserver[Deep Observer]
"""

K8S_TOPOLOGY_MMD = """flowchart TB
  subgraph Minikube[Minikube Cluster]
    Ingress[Ingress NGINX]
    FrontendPod[frontend]
    ProductPod[product-service]
    OrderPod[order-service]
    PostgresPod[postgres-v2-0]
    Vault[Vault]
    ESO[External Secrets]
    Argo[Argo CD]
    OTel[otel-collector]
  end
  Ingress --> FrontendPod
  Ingress --> ProductPod
  Ingress --> OrderPod
  ProductPod --> PostgresPod
  OrderPod --> PostgresPod
  ProductPod --> OTel
  OrderPod --> OTel
  Vault --> ESO
  Argo --> FrontendPod
  Argo --> ProductPod
  Argo --> OrderPod
"""


def generate_diagrams() -> None:
    ensure_dirs(PATHS.diagrams_dir)
    write_text(PATHS.diagrams_dir / "system-architecture.mmd", SYSTEM_ARCH_MMD)
    write_text(PATHS.diagrams_dir / "kubernetes-topology.mmd", K8S_TOPOLOGY_MMD)
