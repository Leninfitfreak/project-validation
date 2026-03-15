# Runtime Evidence

```json
{
  "secrets": {
    "OBSERVER_STACK_USER": "len***com",
    "OBSERVER_STACK_PASSWORD": "Len***345",
    "VAULT_ROOT_TOKEN": "hvs***BFo",
    "VAULT_UNSEAL_KEY": "1U8***Ss="
  },
  "repositories": {
    "ok": true,
    "repositories": {
      "project_validation": "C:\\Projects\\Services\\project-validation",
      "infra": "C:\\Projects\\infra\\leninkart-infra",
      "observer_stack": "C:\\Projects\\Services\\observer-stack",
      "kafka_platform": "C:\\Projects\\Services\\kafka-platform",
      "frontend": "C:\\Projects\\Services\\leninkart-frontend",
      "product_service": "C:\\Projects\\Services\\leninkart-product-service",
      "order_service": "C:\\Projects\\Services\\leninkart-order-service"
    },
    "attempt": 1
  },
  "infrastructure": {
    "ok": true,
    "namespaces": {
      "ok": true,
      "code": 0,
      "stdout": "namespace/argocd\nnamespace/default\nnamespace/dev\nnamespace/external-secrets-system\nnamespace/ingress-nginx\nnamespace/kube-node-lease\nnamespace/kube-public\nnamespace/kube-system\nnamespace/vault",
      "stderr": "",
      "duration_seconds": 0.45,
      "command": "kubectl get ns -o name"
    },
    "pods": {
      "ok": true,
      "code": 0,
      "stdout": "NAMESPACE                 NAME                                                READY   STATUS             RESTARTS        AGE\nargocd                    argocd-application-controller-0                     1/1     Running            22 (85m ago)    55d\nargocd                    argocd-applicationset-controller-7d97f7b47d-gshz2   1/1     Running            22 (85m ago)    55d\nargocd                    argocd-dex-server-657f5854c4-klmxb                  1/1     Running            21 (85m ago)    55d\nargocd                    argocd-notifications-controller-799d98bf9f-svpnf    1/1     Running            21 (85m ago)    55d\nargocd                    argocd-redis-5b69b8d789-zgsmz                       1/1     Running            21 (85m ago)    55d\nargocd                    argocd-repo-server-5bf6d445d7-jfbvf                 1/1     Running            12 (85m ago)    23d\nargocd                    argocd-server-57b47b59b6-4pj55                      1/1     Running            21 (85m ago)    55d\ndev                       ai-observer-5f7f7cc7c6-wx285                        0/1     CrashLoopBackOff   575 (14s ago)   13d\ndev                       ai-observer-central-collector-5548dc8576-k669f      0/1     ImagePullBackOff   0               14d\ndev                       ai-observer-central-collector-5f96957985-84h5v      0/1     ImagePullBackOff   0               14d\ndev                       ai-observer-central-otel-7bfd6d4969-l4jl2           1/1     Running            7 (85m ago)     14d\ndev                       ai-observer-d4cd47c8c-jdgsb                         1/1     Running            8 (84m ago)     14d\ndev                       dev-order-service-order-service-794b5b4554-6nwsh    1/1     Running            3 (84m ago)     2d2h\ndev                       frontend-54b69855dd-wtvwq                           1/1     Running            1 (85m ago)     178m\ndev                       grafana-b7b4f74fc-g8sl7                             1/1     Running            7 (85m ago)     14d\ndev                       jaeger-5b95988bb6-snd9v                             1/1     Running            7 (85m ago)     14d\ndev                       loadgen                                             0/1     Completed          0               9d\ndev                       loki-0                                              2/2     Running            14 (85m ago)    14d\ndev                       loki-canary-phm7x                                   1/1     Running            7 (85m ago)     14d\ndev                       loki-gateway-759f48dbd-xgxk8                        1/1     Running            17 (84m ago)    14d\ndev                       net-debug                                           0/1     Completed          0               13d\ndev                       observer-agent-847b9cffd8-75jmz                     1/1     Running            7 (85m ago)     13d\ndev                       observer-agent-local-test                           0/1     Completed          0               13d\ndev                       otel-collector-pcbdp                                1/1     Running            3 (85m ago)     6d11h\ndev                       postgres-v2-0                                       1/1     Running            7 (85m ago)     14d\ndev                       product-service-84b5998d57-x9f4l                    1/1     Running            2 (85m ago)     2d2h\ndev                       prometheus-744f9d4d98-26n9x                         1/1     Running            7 (85m ago)     14d\ndev                       traffic-gen                                         0/1     Completed          0               13d\ndev                       traffic-generator-7544d6db77-b62d8                  1/1     Running            3 (85m ago)     6d9h\ndev                       traffic-generator-7544d6db77-ldt27                  1/1     Running            3 (85m ago)     6d9h\ndev                       traffic-generator-7544d6db77-vcp4h                  1/1     Running            3 (85m ago)     6d9h\nexternal-secrets-system   external-secrets-56dcb8b89-whfcr                    1/1     Running            17 (85m ago)    41d\nexternal-secrets-system   external-secrets-cert-controller-8684b6cbf9-8798h   1/1     Running            17 (85m ago)    41d\nexternal-secrets-system   external-secrets-webhook-c8f559b76-kllfc            1/1     Running            17 (85m ago)    41d\ningress-nginx             ingress-nginx-admission-create-92gbv                0/1     Completed          0               55d\ningress-nginx             ingress-nginx-admission-patch-wrcsz                 0/1     Completed          0               55d\ningress-nginx             ingress-nginx-controller-55c775d56b-5dzr7           1/1     Running            20 (85m ago)    44d\nkube-system               coredns-66bc5c9577-9tl5v                            1/1     Running            24 (85m ago)    55d\nkube-system               etcd-minikube                                       1/1     Running            24 (85m ago)    55d\nkube-system               kube-apiserver-minikube                             1/1     Running            24 (85m ago)    55d\nkube-system               kube-controller-manager-minikube                    1/1     Running            27 (84m ago)    55d\nkube-system               kube-proxy-jvxdq                                    1/1     Running            23 (85m ago)    55d\nkube-system               kube-scheduler-minikube                             1/1     Running            24 (85m ago)    55d\nkube-system               storage-provisioner                                 1/1     Running            60 (85m ago)    55d\nvault                     vault-0                                             0/1     Running            11 (2m5s ago)   2d2h",
      "stderr": "",
      "duration_seconds": 0.96,
      "command": "kubectl get pods -A"
    },
    "ingress": {
      "ok": true,
      "code": 0,
      "stdout": "NAMESPACE   NAME                CLASS   HOSTS   ADDRESS        PORTS   AGE\ndev         leninkart-ingress   nginx   *       192.168.49.2   80      55d",
      "stderr": "",
      "duration_seconds": 0.52,
      "command": "kubectl get ingress -A"
    },
    "attempt": 1
  },
  "gitops": {
    "ok": true,
    "applications": {
      "ok": true,
      "code": 0,
      "stdout": "NAMESPACE   NAME                        SYNC STATUS   HEALTH STATUS\nargocd      dev-ingress                 Synced        Healthy\nargocd      dev-order-service           OutOfSync     Healthy\nargocd      dev-product-service         OutOfSync     Healthy\nargocd      external-secrets-operator   Synced        Healthy\nargocd      frontend-dev                Synced        Healthy\nargocd      leninkart-root              Synced        Healthy\nargocd      loadtest-dev                Synced        Healthy\nargocd      otel-collector-dev          Synced        Healthy\nargocd      postgres-dev                Synced        Healthy\nargocd      vault                       Synced        Progressing\nargocd      vault-externalsecrets       Synced        Degraded\nargocd      vault-secretstore           Synced        Healthy\nargocd      vault-secretstores-dev      OutOfSync     Healthy",
      "stderr": "",
      "duration_seconds": 0.67,
      "command": "kubectl get applications.argoproj.io -A"
    },
    "attempt": 1
  },
  "secret_management": {
    "ok": true,
    "vault_pod": {
      "ok": true,
      "code": 0,
      "stdout": "NAME      READY   STATUS    RESTARTS        AGE\nvault-0   0/1     Running   11 (2m7s ago)   2d2h",
      "stderr": "",
      "duration_seconds": 0.46,
      "command": "kubectl get pod -n vault vault-0"
    },
    "external_secrets": {
      "ok": true,
      "code": 0,
      "stdout": "NAMESPACE   NAME                       STORE           REFRESH INTERVAL   STATUS              READY\ndev         ai-observer-secrets        vault-backend   30m                SecretSyncedError   False\ndev         kafka-creds                vault-backend   1h                 SecretSyncedError   False\ndev         order-service-config       vault-backend   30m                SecretSyncedError   False\ndev         order-service-db-creds     vault-backend   1h                 SecretSyncedError   False\ndev         postgres-secret            vault-backend   1h                 SecretSyncedError   False\ndev         product-service-config     vault-backend   30m                SecretSyncedError   False\ndev         product-service-db-creds   vault-backend   1h                 SecretSyncedError   False",
      "stderr": "",
      "duration_seconds": 0.47,
      "command": "kubectl get externalsecret -A"
    },
    "secret_stores": {
      "ok": true,
      "code": 0,
      "stdout": "NAMESPACE   NAME                                                   AGE   STATUS   CAPABILITIES   READY\n            clustersecretstore.external-secrets.io/vault-backend   41d   Valid    ReadWrite      True",
      "stderr": "",
      "duration_seconds": 0.47,
      "command": "kubectl get secretstore,clustersecretstore -A"
    },
    "attempt": 1
  },
  "workflows": {
    "ok": true,
    "frontend_ingress": {
      "ok": true,
      "code": 0,
      "stdout": "HTTP/1.1 200 OK\nDate: Sat, 14 Mar 2026 19:59:27 GMT\nContent-Type: text/html\nContent-Length: 247\nConnection: keep-alive\nLast-Modified: Thu, 12 Mar 2026 18:43:09 GMT\nETag: \"69b3093d-f7\"\nAccept-Ranges: bytes",
      "stderr": "% Total    % Received % Xferd  Average Speed  Time    Time    Time   Current\n                                 Dload  Upload  Total   Spent   Left   Speed\n\n  0      0   0      0   0      0      0      0                              0\n  0    247   0      0   0      0      0      0                              0\n  0    247   0      0   0      0      0      0                              0\n  0    247   0      0   0      0      0      0                              0",
      "duration_seconds": 0.15,
      "command": "curl.exe --noproxy * -I --max-time 10 http://127.0.0.1/"
    },
    "product_service": {
      "ok": true,
      "code": 0,
      "stdout": "NAME                        TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)    AGE\nleninkart-product-service   ClusterIP   10.98.112.229   <none>        8081/TCP   55d",
      "stderr": "",
      "duration_seconds": 0.5,
      "command": "kubectl get svc -n dev leninkart-product-service"
    },
    "order_service": {
      "ok": true,
      "code": 0,
      "stdout": "NAME                      TYPE        CLUSTER-IP       EXTERNAL-IP   PORT(S)    AGE\nleninkart-order-service   ClusterIP   10.102.185.113   <none>        8080/TCP   55d",
      "stderr": "",
      "duration_seconds": 0.46,
      "command": "kubectl get svc -n dev leninkart-order-service"
    },
    "attempt": 1
  },
  "messaging": {
    "ok": true,
    "docker_ps": {
      "ok": true,
      "code": 0,
      "stdout": "NAMES                    STATUS\nsignoz                   Up 2 hours (healthy)\nsignoz-clickhouse        Up 2 hours (healthy)\ndeep-observer-frontend   Up 2 hours\ndeep-observer-ai-core    Up 2 hours\ndeep-observer-ai-brain   Up 2 hours\ndeep-observer-postgres   Up 2 hours (healthy)\nsignoz-otel-collector    Up 2 hours\nkafka-platform           Up 2 hours (unhealthy)\nsignoz-otlp-proxy        Up 2 hours\nsignoz-zookeeper-1       Up 2 hours (healthy)\nminikube                 Up 2 hours",
      "stderr": "",
      "duration_seconds": 0.45,
      "command": "docker ps --format \"table {{.Names}}\\t{{.Status}}\""
    },
    "kafka_hint": {
      "ok": true,
      "code": 0,
      "stdout": "kafka-platform",
      "stderr": "",
      "duration_seconds": 0.82,
      "command": "docker ps --format \"{{.Names}}\" | findstr /I kafka"
    },
    "attempt": 1
  },
  "observability": {
    "ok": true,
    "observer_stack": {
      "ok": true,
      "code": 0,
      "stdout": "HTTP/1.1 200 OK\nAccept-Ranges: bytes\nCache-Control: max-age=0,no-cache,private,must-revalidate\nContent-Length: 3066\nContent-Type: text/html; charset=utf-8\nLast-Modified: Sun, 08 Mar 2026 13:38:48 GMT\nVary: Accept-Encoding\nVary: Origin\nDate: Sat, 14 Mar 2026 19:59:29 GMT",
      "stderr": "% Total    % Received % Xferd  Average Speed  Time    Time    Time   Current\n                                 Dload  Upload  Total   Spent   Left   Speed\n\n  0      0   0      0   0      0      0      0                              0\n  0   3066   0      0   0      0      0      0                              0\n  0   3066   0      0   0      0      0      0                              0\n  0   3066   0      0   0      0      0      0                              0",
      "duration_seconds": 0.18,
      "command": "curl.exe --noproxy * -I --max-time 10 http://localhost:8080/"
    },
    "ai_api": {
      "ok": true,
      "code": 0,
      "stdout": "HTTP/1.1 200 OK\nAccess-Control-Allow-Headers: Content-Type\nAccess-Control-Allow-Methods: GET, OPTIONS\nAccess-Control-Allow-Origin: *\nContent-Type: application/json\nDate: Sat, 14 Mar 2026 19:59:30 GMT\nContent-Length: 16",
      "stderr": "% Total    % Received % Xferd  Average Speed  Time    Time    Time   Current\n                                 Dload  Upload  Total   Spent   Left   Speed\n\n  0      0   0      0   0      0      0      0                              0\n  0     16   0      0   0      0      0      0                              0\n  0     16   0      0   0      0      0      0                              0\n  0     16   0      0   0      0      0      0                              0",
      "duration_seconds": 0.13,
      "command": "curl.exe --noproxy * -I --max-time 10 http://localhost:8081/health"
    },
    "attempt": 1
  },
  "ai_observability": {
    "ok": true,
    "services": {
      "ok": true,
      "code": 0,
      "stdout": "NAME                        TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)    AGE\nai-observer                 ClusterIP   10.96.17.206    <none>        8080/TCP   21d\nobserver-backend-external   ClusterIP   10.107.103.67   <none>        8080/TCP   15d",
      "stderr": "",
      "duration_seconds": 0.49,
      "command": "kubectl get svc -n dev ai-observer observer-backend-external"
    },
    "attempt": 1
  },
  "summary": {
    "status": "success",
    "stages": {
      "repositories": true,
      "infrastructure": true,
      "gitops": true,
      "secret_management": true,
      "workflows": true,
      "messaging": true,
      "observability": true,
      "ai_observability": true
    }
  }
}
```