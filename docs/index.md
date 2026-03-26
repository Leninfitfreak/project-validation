# LeninKart Validation Overview

This site contains the current end-to-end LeninKart platform evidence generated from the rebuilt `project-validation` framework.

## Covered Areas

- Application journey: signup, login, product creation, buy flow, order history
- GitOps proof: ArgoCD login, applications list, application detail
- Secrets proof: Vault access and safe secret-path artifact
- Messaging proof: external Kafka runtime artifact and Kafka dashboard
- Observability proof: Grafana dashboards, Loki logs, Prometheus targets, Tempo traces
- CI / DevSecOps proof: quality gates, secret scanning, vulnerability scanning, and pipeline evidence planning

## Validation Rules

- Every run starts clean and replaces the previous evidence set.
- Final screenshots are accepted only after selector checks, content checks, and non-blank image validation succeed.
- Retry attempts are stored separately under `artifacts/debug-retries/` and never mixed into the final evidence gallery.

## Category Summary

- `application`: 8 captured step(s)
- `gitops`: 3 captured step(s)
- `infra`: 1 captured step(s)
- `messaging`: 2 captured step(s)
- `observability`: 14 captured step(s)
- `secrets`: 3 captured step(s)

## CI / DevSecOps Documentation

This MkDocs site also carries the LeninKart CI baseline design and validation notes:

- repo-by-repo CI gap analysis
- local command verification and workaround map
- secret scanning and vulnerability scanning rationale
- workflow overview and planned public pipeline evidence index
