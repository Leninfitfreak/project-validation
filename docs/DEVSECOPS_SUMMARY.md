# DevSecOps Summary

## Outcome

The LeninKart platform now includes a practical CI/DevSecOps layer designed for:

- portfolio proof
- GitHub visibility
- interview discussion
- day-to-day repository hygiene

## Included Controls

- automated build/test validation
- secret scanning with `Gitleaks`
- vulnerability/config/image scanning with `Trivy`
- infra linting with `Helm`
- docs build verification for `project-validation`
- compose syntax validation for `kafka-platform`

## Why This Is Practical

- small enough to maintain
- strong enough to demonstrate real engineering discipline
- avoids heavy enterprise-only complexity
- produces clean public workflow pages that can be used as evidence

## Current Limitations

- local workstation lacks Maven
- local Docker daemon is currently unavailable
- final GitHub Actions screenshot evidence depends on pushing the workflow files and capturing the public runs afterward
