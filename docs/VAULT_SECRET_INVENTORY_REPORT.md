# Vault Secret Inventory Report

- Secret count: `8`

## Paths

### `secret/leninkart/`

- `auth`

### `secret/leninkart/kafka/`

- `credentials`

### `secret/leninkart/observability/`

- `grafana`

### `secret/leninkart/order-service/`

- `config`
- `database`

### `secret/leninkart/postgres/`

- `admin`

### `secret/leninkart/product-service/`

- `config`
- `database`

## Usage Mapping

- `secret/leninkart/observability/*`: observability admin and provisioning secrets
- `secret/leninkart/product-service/*`: product-service runtime configuration
- `secret/leninkart/order-service/*`: order-service runtime configuration
- `secret/leninkart/postgres/*`: shared database credentials and connection data