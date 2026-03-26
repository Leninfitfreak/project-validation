# CI Validation Report

## Summary

The LeninKart platform now has a practical CI/DevSecOps baseline across the active repositories.

Implemented areas:

- build/test validation
- secret scanning
- vulnerability/config/image scanning
- documentation-ready public workflow structure

## Locally Verified Commands

- `leninkart-frontend`
  - `npm.cmd install`
  - `npm.cmd test -- --runInBand`
  - `npm.cmd run build`
- `leninkart-infra`
  - `helm lint applications/frontend/helm`
  - `helm lint applications/product-service/helm --values applications/product-service/helm/values-dev.yaml`
  - `helm lint applications/order-service/helm --values applications/order-service/helm/values-dev.yaml`
- `project-validation`
  - `python -m compileall validation run_validation.py`
  - `python -m mkdocs build`
- `kafka-platform`
  - `docker compose -f docker-compose.yml config`

## Locally Blocked By Toolchain, Not Repo Defects

- `leninkart-product-service`
  - blocked by missing local Maven and stopped Docker daemon
- `leninkart-order-service`
  - blocked by missing local Maven and stopped Docker daemon
- image build verification in Docker-backed repos
  - blocked by stopped Docker daemon

## Fixes Applied During Validation

- frontend test path made stable for CRA/Jest by:
  - guarding the runtime root mount in tests
  - mocking `axios` for the shell-level test
- infra Helm lint workflow updated to use env values files for service charts

## Next Validation Step

After pushing these workflow changes:

1. let GitHub Actions run on the public repos
2. capture workflow summary/job screenshots
3. add those screenshots to the CI evidence set
