# Vault Secret Management

This report captures the Vault UI evidence and KV verification performed by the validator.

- Vault ready: `True`
- Vault sealed: `False`
- ClusterSecretStore ready: `True`
- KV paths: agent_token, ai-observer, db, kafka, order-service, postgres, product-service

## Explored Pages

### Vault login page
The Vault login page confirms that the secrets management UI is reachable.

![SEC-001-vault-login.png](screenshots/SEC-001-vault-login.png)

### Vault home
The Vault home view confirms successful authentication and exposes the operational workspace for secrets engines and quick actions.

![SEC-003-vault-home.png](screenshots/SEC-003-vault-home.png)

### Secrets engine list
The secrets engine list shows the mounted secret backends, including the KV engine used by LeninKart.

![SEC-003-vault-secret-engines.png](screenshots/SEC-003-vault-secret-engines.png)

### KV secret paths
The Vault path view provides evidence that the LeninKart KV hierarchy is present under the mounted secret engine.

![SEC-005-vault-secret-paths.png](screenshots/SEC-005-vault-secret-paths.png)

### Secret key and value evidence
This evidence view renders the extracted KV secret data for the product-service configuration so the validator can prove real key presence without navigating brittle Vault UI internals for each value.

![SEC-006-vault-secret-values.png](screenshots/SEC-006-vault-secret-values.png)
