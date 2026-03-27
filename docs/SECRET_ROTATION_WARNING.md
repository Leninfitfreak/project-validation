# Secret Rotation Warning

## Immediate Action

If any real Jira, GitHub, Grafana, ArgoCD, Vault, or other credentials were ever committed to example files such as:

- `.env.example`
- template files
- sample config files

those secrets must be treated as exposed and rotated immediately.

## Required Practice

Example and template files must contain placeholders only.

Real values must come only from:

- local `.env`
- GitHub Actions secrets
- other secure runtime secret stores

## Current Cleanup

The example environment file in this repo has been scrubbed so it now contains placeholders only.
