# CI Gap Analysis

## Scope

This report captures the practical CI/DevSecOps baseline across the active LeninKart repositories:

- `leninkart-frontend`
- `leninkart-product-service`
- `leninkart-order-service`
- `leninkart-infra`
- `project-validation`
- `kafka-platform`

Legacy `observer-stack` / SigNoz validation was intentionally excluded because it is no longer part of the supported platform.

## Initial State

Before this CI pass:

- `leninkart-frontend` had a deployment workflow but no unit test, secret scan, or vulnerability scan workflow.
- `leninkart-product-service` had a build/push/deploy workflow but no unit test, secret scan, or vulnerability scan workflow.
- `leninkart-order-service` had a build/push/deploy workflow but no unit test, secret scan, or vulnerability scan workflow.
- `leninkart-infra` had no GitHub Actions workflow for linting, secret scanning, or config scanning.
- `project-validation` had no GitHub Actions workflow for framework compilation, docs build, or security scanning.
- `kafka-platform` had no GitHub Actions workflow for compose validation, image build validation, or security scanning.

## Implemented Baseline

The new baseline adds practical CI quality gates with lightweight security coverage:

- Unit/basic tests where the repo has a realistic test surface
- Build validation where the repo already has a build path
- `Gitleaks` secret scanning
- `Trivy` vulnerability/config scanning
- Docker image build validation where practical

## Repo-by-Repo Findings

### `leninkart-frontend`

Current CI additions:

- `npm install`
- `npm test -- --runInBand`
- `npm run build`
- `Gitleaks`
- `Trivy` filesystem scan
- `Docker build`
- `Trivy` image scan

Gap that was fixed during local verification:

- The repo had no stable test entry point.
- A small public-shell test was added for the anonymous login experience.
- The app mount was made test-safe by guarding `createRoot` behind a real DOM root check.
- `axios` had to be mocked in the test because the current CRA/Jest setup does not like the package’s ESM entry directly in this environment.

Local verification result:

- `npm.cmd install` passed
- `npm.cmd test -- --runInBand` passed
- `npm.cmd run build` passed

Classification:

- Real CI issue found and fixed: missing test-safe frontend entry + axios/Jest incompatibility in the new test path

### `leninkart-product-service`

Current CI additions:

- `mvn -B test`
- `mvn -B -DskipTests package`
- `Gitleaks`
- `Trivy` filesystem scan
- `Docker build`
- `Trivy` image scan

Test surface added:

- `JwtServiceTest` for token generation and parsing

Local verification result:

- Workflow commands are valid for GitHub Actions Ubuntu runners
- Local execution could not be completed on this machine because:
  - `mvn` is not installed locally
  - Docker daemon is currently unavailable, so the containerized Maven fallback could not run

Classification:

- No repo-level breakage proven locally
- Local blocker only: missing Maven toolchain and stopped Docker daemon

### `leninkart-order-service`

Current CI additions:

- `mvn -B test`
- `mvn -B -DskipTests package`
- `Gitleaks`
- `Trivy` filesystem scan
- `Docker build`
- `Trivy` image scan

Test surface added:

- `JwtServiceTest` for token generation and parsing

Local verification result:

- Workflow commands are valid for GitHub Actions Ubuntu runners
- Local execution could not be completed on this machine because:
  - `mvn` is not installed locally
  - Docker daemon is currently unavailable, so the containerized Maven fallback could not run

Classification:

- No repo-level breakage proven locally
- Local blocker only: missing Maven toolchain and stopped Docker daemon

### `leninkart-infra`

Current CI additions:

- `helm lint` for active application charts
- `Gitleaks`
- `Trivy` config scan

Gap that was fixed during local verification:

- `helm lint` initially failed for `product-service` and `order-service` when run without env values.
- The workflow was corrected to lint those charts with `values-dev.yaml`.

Local verification result:

- `helm lint applications/frontend/helm` passed
- `helm lint applications/product-service/helm --values applications/product-service/helm/values-dev.yaml` passed
- `helm lint applications/order-service/helm --values applications/order-service/helm/values-dev.yaml` passed

Classification:

- Real CI issue found and fixed: chart lint command needed env-specific values

### `project-validation`

Current CI additions:

- `python -m compileall validation run_validation.py`
- `python -m mkdocs build`
- `Gitleaks`
- `Trivy` filesystem scan

Local verification result:

- `python -m compileall validation run_validation.py` passed
- `python -m mkdocs build` passed

Classification:

- CI baseline verified locally

### `kafka-platform`

Current CI additions:

- `docker compose -f docker-compose.yml config`
- `Docker build`
- `Gitleaks`
- `Trivy` config scan
- `Trivy` image scan

Local verification result:

- `docker compose -f docker-compose.yml config` passed
- Docker image build was not verified locally because Docker daemon is currently unavailable

Classification:

- Partial local validation only
- Remaining blocker is local Docker availability, not compose syntax

## True Project / CI Issues vs Local Toolchain Limitations

### True Project / CI Issues

- Frontend had no stable test entry and needed a small test-safe mount adjustment
- Frontend test path needed an `axios` mock to work with the current CRA/Jest dependency behavior
- Infra Helm lint needed env values for service charts instead of bare chart linting
- The initial workflow draft pinned `aquasecurity/trivy-action@0.30.0`, and the first fix still missed the required `v` prefix. The working form is `aquasecurity/trivy-action@v0.33.1`

### Local Machine / Toolchain Limitations

- PowerShell `npm.ps1` policy issue on Windows
  - Workaround used: `npm.cmd`
- Maven is not installed locally
  - Intended workaround: containerized Maven
- Docker daemon is currently unavailable
  - This prevented:
    - containerized Maven fallback
    - local image-build verification

These local limitations should not be treated as repository or CI design failures because GitHub Actions runners provide the required toolchains directly.

## Recommended Quality Gate Posture

- Blocking:
  - frontend tests/build
  - backend unit tests/package
  - Helm lint
  - project-validation compile/docs build
  - Gitleaks
- Advisory for now:
  - Trivy vulnerability/config/image scans

The vulnerability scans are intentionally non-blocking in the first baseline so the public pipelines stay practical and readable while still surfacing security findings.
