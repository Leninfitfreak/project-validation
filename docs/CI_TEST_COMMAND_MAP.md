# CI Test Command Map

## Purpose

This map records the intended GitHub Actions commands and the local verification path used on the current Windows workstation.

## Command Matrix

| Repo | CI Command | Intended Runner Toolchain | Local Verification Path | Status |
| --- | --- | --- | --- | --- |
| `leninkart-frontend` | `npm install` | GitHub Ubuntu + Node 20 | `npm.cmd install` | Passed |
| `leninkart-frontend` | `npm test -- --runInBand` | GitHub Ubuntu + Node 20 | `npm.cmd test -- --runInBand` | Passed |
| `leninkart-frontend` | `npm run build` | GitHub Ubuntu + Node 20 | `npm.cmd run build` | Passed |
| `leninkart-product-service` | `mvn -B test` | GitHub Ubuntu + Temurin 17 + Maven | Containerized Maven fallback intended | Blocked locally by stopped Docker daemon |
| `leninkart-product-service` | `mvn -B -DskipTests package` | GitHub Ubuntu + Temurin 17 + Maven | Not locally executed | Blocked locally by missing Maven and stopped Docker daemon |
| `leninkart-order-service` | `mvn -B test` | GitHub Ubuntu + Temurin 17 + Maven | Containerized Maven fallback intended | Blocked locally by stopped Docker daemon |
| `leninkart-order-service` | `mvn -B -DskipTests package` | GitHub Ubuntu + Temurin 17 + Maven | Not locally executed | Blocked locally by missing Maven and stopped Docker daemon |
| `leninkart-infra` | `helm lint applications/frontend/helm` | GitHub Ubuntu + Helm | `helm lint applications/frontend/helm` | Passed |
| `leninkart-infra` | `helm lint applications/product-service/helm --values applications/product-service/helm/values-dev.yaml` | GitHub Ubuntu + Helm | Same command | Passed |
| `leninkart-infra` | `helm lint applications/order-service/helm --values applications/order-service/helm/values-dev.yaml` | GitHub Ubuntu + Helm | Same command | Passed |
| `project-validation` | `python -m compileall validation run_validation.py` | GitHub Ubuntu + Python 3.13 | Same command | Passed |
| `project-validation` | `python -m mkdocs build` | GitHub Ubuntu + Python 3.13 | Same command | Passed |
| `kafka-platform` | `docker compose -f docker-compose.yml config` | GitHub Ubuntu + Docker | Same command | Passed |
| `kafka-platform` | `docker build -t leninkart/kafka-platform:ci .` | GitHub Ubuntu + Docker | Not locally executed | Blocked locally by stopped Docker daemon |

## Local Toolchain Notes

- Windows PowerShell attempted to route `npm` through `npm.ps1`, which is blocked by local execution policy.
- The correct local workaround is `npm.cmd`.
- Maven is not installed on this workstation.
- Docker daemon is currently unavailable, so containerized Maven and local image build validation could not run.

## Interpretation Guidance

- A blocked local command does not automatically mean the repository or workflow is broken.
- When the GitHub Actions runner already provisions the correct toolchain, the missing local tool should be classified as an environment limitation unless a repo-specific failure is separately proven.
