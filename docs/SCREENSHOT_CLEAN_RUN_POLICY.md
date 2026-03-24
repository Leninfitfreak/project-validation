# Screenshot Clean Run Policy

- Every validation run starts by deleting prior generated screenshots, reports, and validation-output bundles.
- Final evidence is written only to the canonical category folders under `screenshots/`.
- Retry attempts and failed captures are stored under `artifacts/debug-retries/`.
- Final evidence filenames are stable and do not use ad-hoc suffixes like `final-v2`.
- A screenshot is published only after UI readiness checks and image-quality checks pass.