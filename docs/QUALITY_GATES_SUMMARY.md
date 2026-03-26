# Quality Gates Summary

## Blocking Gates

- Frontend test
- Frontend build
- Product service unit tests
- Product service package
- Order service unit tests
- Order service package
- Infra Helm lint
- Project-validation compile check
- Project-validation MkDocs build
- Kafka compose syntax validation
- Gitleaks secret scan

## Advisory Gates

- Trivy filesystem scans
- Trivy config scans
- Trivy image scans

## Rationale

This split keeps the CI baseline practical:

- real correctness checks fail fast
- security visibility is added immediately
- advisory vulnerability reporting avoids drowning the portfolio in noisy red pipelines before triage work is complete
