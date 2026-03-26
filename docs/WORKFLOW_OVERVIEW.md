# Workflow Overview

## Repositories and Quality Workflows

- `leninkart-frontend`
  - workflow: `Frontend Quality & Security`
- `leninkart-product-service`
  - workflow: `Product Service Quality & Security`
- `leninkart-order-service`
  - workflow: `Order Service Quality & Security`
- `leninkart-infra`
  - workflow: `Infra Quality & Security`
- `project-validation`
  - workflow: `Project Validation Quality & Security`
- `kafka-platform`
  - workflow: `Kafka Platform Quality & Security`

## Shared Pattern

Each workflow follows the same portfolio-friendly structure:

1. checkout
2. language/build validation
3. secret scan
4. vulnerability/config/image scan

## Deliberate Design Choices

- keep tests/builds blocking where the repo has a stable execution path
- keep vulnerability scans advisory in the first baseline
- keep workflow names explicit so public Actions pages are easy to understand in screenshots
