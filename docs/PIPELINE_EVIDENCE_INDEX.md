# Pipeline Evidence Index

## Purpose

This page indexes the final CI/DevSecOps evidence captured from public GitHub Actions workflow pages.

## Final Evidence Targets

### Frontend

- workflow run summary for `Frontend Quality & Security`
  - [public run](https://github.com/Leninfitfreak/leninkart-frontend/actions/runs/23599512037)
  - screenshot: `screenshots/ci/frontend-quality-summary.png`
- job detail with step visibility for:
  - frontend tests
  - frontend build
  - Gitleaks
  - Trivy scans
  - screenshot: `screenshots/ci/frontend-quality-job.png`

### Product Service

- workflow run summary for `Product Service Quality & Security`
  - [public run](https://github.com/Leninfitfreak/leninkart-product-service/actions/runs/23599512416)
  - screenshot: `screenshots/ci/product-quality-summary.png`

### Order Service

- workflow run summary for `Order Service Quality & Security`
  - [public run](https://github.com/Leninfitfreak/leninkart-order-service/actions/runs/23599512566)
  - screenshot: `screenshots/ci/order-quality-summary.png`

### Infra

- workflow run summary for `Infra Quality & Security`
  - [public run](https://github.com/Leninfitfreak/leninkart-infra/actions/runs/23599611267)
  - screenshot: `screenshots/ci/infra-quality-summary.png`

### Project Validation

- workflow run summary for `Project Validation Quality & Security`
  - [public run](https://github.com/Leninfitfreak/project-validation/actions/runs/23599514246)
  - screenshot: `screenshots/ci/project-validation-quality-summary.png`

### Kafka Platform

- workflow run summary for `Kafka Platform Quality & Security`
  - [public run](https://github.com/Leninfitfreak/kafka-platform/actions/runs/23599513549)
  - screenshot: `screenshots/ci/kafka-quality-summary.png`

## Screenshot Storage Plan

Final CI screenshots should be stored under:

- `screenshots/ci/`
- mirrored into `docs/screenshots/ci/` for MkDocs rendering

## Status

- workflow definitions: implemented
- local command validation: completed as far as the current workstation toolchain allowed
- public GitHub Actions screenshots: captured from the latest corrected successful runs
