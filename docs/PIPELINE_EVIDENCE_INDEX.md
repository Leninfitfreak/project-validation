# Pipeline Evidence Index

## Purpose

This page indexes the CI/DevSecOps evidence set that should be captured from public GitHub Actions workflow pages.

## Planned Evidence Targets

### Frontend

- workflow run summary for `Frontend Quality & Security`
- step visibility for:
  - frontend tests
  - frontend build
  - Gitleaks
  - Trivy scans

### Product Service

- workflow run summary for `Product Service Quality & Security`
- step visibility for:
  - unit tests
  - package
  - Gitleaks
  - Trivy scans

### Order Service

- workflow run summary for `Order Service Quality & Security`
- step visibility for:
  - unit tests
  - package
  - Gitleaks
  - Trivy scans

### Infra

- workflow run summary for `Infra Quality & Security`
- step visibility for:
  - Helm lint
  - Gitleaks
  - Trivy config scan

### Project Validation

- workflow run summary for `Project Validation Quality & Security`
- step visibility for:
  - compile check
  - MkDocs build
  - Gitleaks
  - Trivy scan

### Kafka Platform

- workflow run summary for `Kafka Platform Quality & Security`
- step visibility for:
  - compose validation
  - image build
  - Gitleaks
  - Trivy scans

## Screenshot Storage Plan

Final CI screenshots should be stored under:

- `screenshots/ci/`
- mirrored into `docs/screenshots/ci/` for MkDocs rendering

## Status

- workflow definitions: implemented
- local command validation: partially completed
- public GitHub Actions screenshots: pending push + workflow execution
