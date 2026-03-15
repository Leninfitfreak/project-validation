# Secret Management

Vault is validated as the source of truth, `ClusterSecretStore/vault-backend` is checked for readiness, ExternalSecret sync state is captured during execution, and representative secret values are validated during the run.

- Verified secret keys: api_key, jwt_secret
- Detailed evidence: [vault-secret-management.md](vault-secret-management.md)
