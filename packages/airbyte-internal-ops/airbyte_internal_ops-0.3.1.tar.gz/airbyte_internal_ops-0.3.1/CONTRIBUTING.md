# Contributing

First clone the repo, then use something like the following MCP config.

```json
{
  "mcpServers": {
    "airbyte-ops-mcp": {
      "type": "stdio",
      "command": "uv",
      "args": [
        "run",
        "--project=/Users/{my-user-id}/repos/airbyte-ops-mcp/",
        "airbyte-ops-mcp"
      ],
      "env": {
        "AIRBYTE_MCP_ENV_FILE": "/path/to/airbyte-ops-mcp/.env"
      }
    },
    "airbyte-coral-mcp": {
      "type": "stdio",
      "command": "uvx",
      "args": [
        "--python=3.11",
        "--from=airbyte@latest",
        "airbyte-mcp"
      ],
      "env": {
        "AIRBYTE_MCP_ENV_FILE": "/Users/{user-id}/.mcp/airbyte_mcp.env"
      }
    }
  }
}
```

## Internal Secrets for Live Tests

The live tests feature can retrieve unmasked connection secrets from Airbyte Cloud's internal database. This requires:

- **GCP_PROD_DB_ACCESS_CREDENTIALS** - Access to prod Cloud SQL and Google Secret Manager for DB connection details

To test locally:

1. Set up GCP Application Default Credentials: `gcloud auth application-default login`
2. Ensure you have access to the `prod-ab-cloud-proj` project
3. Connect to Tailscale (required for private network access)

In CI, these secrets are available at the org level and a Cloud SQL Auth Proxy handles connectivity.

## Authorizing Service Accounts

To grant a service account access to the prod database query tools, you need to grant permissions on the `CONNECTION_RETRIEVER_PG_CONNECTION_DETAILS` secret in Google Secret Manager (see `CONNECTION_RETRIEVER_PG_CONNECTION_DETAILS_SECRET_ID` in `src/airbyte_ops_mcp/constants.py`). The service account needs both `secretAccessor` (to read the secret value) and `viewer` (to list secret versions) roles.

### Required Permissions

#### Secret Manager Permissions

Grant both roles scoped to the specific secret:

```bash
# Grant secretAccessor role (for reading secret values)
gcloud secrets add-iam-policy-binding projects/587336813068/secrets/CONNECTION_RETRIEVER_PG_CONNECTION_DETAILS \
  --member="serviceAccount:YOUR_SERVICE_ACCOUNT@prod-ab-cloud-proj.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

# Grant viewer role (for listing secret versions)
gcloud secrets add-iam-policy-binding projects/587336813068/secrets/CONNECTION_RETRIEVER_PG_CONNECTION_DETAILS \
  --member="serviceAccount:YOUR_SERVICE_ACCOUNT@prod-ab-cloud-proj.iam.gserviceaccount.com" \
  --role="roles/secretmanager.viewer"
```

#### Cloud SQL Permissions

Grant Cloud SQL access at the project level:

```bash
# Grant Cloud SQL Client role (required for connecting via Cloud SQL Proxy or Python Connector)
gcloud projects add-iam-policy-binding prod-ab-cloud-proj \
  --member="serviceAccount:YOUR_SERVICE_ACCOUNT@prod-ab-cloud-proj.iam.gserviceaccount.com" \
  --role="roles/cloudsql.client"

# Grant Cloud SQL Instance User role (may be required depending on org policies)
gcloud projects add-iam-policy-binding prod-ab-cloud-proj \
  --member="serviceAccount:YOUR_SERVICE_ACCOUNT@prod-ab-cloud-proj.iam.gserviceaccount.com" \
  --role="roles/cloudsql.instanceUser"
```

Note: `roles/cloudsql.client` is required for the Cloud SQL Python Connector and Cloud SQL Auth Proxy to establish connections. `roles/cloudsql.instanceUser` is typically needed for IAM database authentication; it may be redundant when using username/password authentication (as this codebase does), but some environments may still require it.

#### Cloud Logging Permissions

For tools that query GCP Cloud Logging (e.g., `lookup_cloud_backend_error`), grant the Logs Viewer role at the project level:

```bash
# Grant Logs Viewer role (for reading log entries)
# Note: --condition=None is required to avoid interactive prompts when the project has conditional bindings
gcloud projects add-iam-policy-binding prod-ab-cloud-proj \
  --member="serviceAccount:YOUR_SERVICE_ACCOUNT@prod-ab-cloud-proj.iam.gserviceaccount.com" \
  --role="roles/logging.viewer" \
  --condition=None
```

For tools that retrieve connection secrets with audit logging (e.g., `fetch-connection-config --with-secrets`), also grant the Logs Writer role:

```bash
# Grant Logs Writer role (for writing audit log entries when retrieving secrets)
gcloud projects add-iam-policy-binding prod-ab-cloud-proj \
  --member="serviceAccount:YOUR_SERVICE_ACCOUNT@prod-ab-cloud-proj.iam.gserviceaccount.com" \
  --role="roles/logging.logWriter" \
  --condition=None
```

To check if the permission is already granted:

```bash
# List all IAM bindings for the project and filter for the service account
gcloud projects get-iam-policy prod-ab-cloud-proj \
  --flatten="bindings[].members" \
  --filter="bindings.members:YOUR_SERVICE_ACCOUNT@prod-ab-cloud-proj.iam.gserviceaccount.com" \
  --format="table(bindings.role)"
```

### Verifying Permissions

To check existing permissions on the secret:

```bash
gcloud secrets get-iam-policy projects/587336813068/secrets/CONNECTION_RETRIEVER_PG_CONNECTION_DETAILS
```

### Using Cloud SQL Proxy

When running outside of the VPC (without Tailscale), use the Cloud SQL Auth Proxy:

**Option A: Using the CLI (Recommended)**

Pre-install the CLI tool:
```bash
uv tool install airbyte-internal-ops
airbyte-ops cloud db start-proxy --port=5433
```

Or use as a single-step command:
```bash
uvx --from=airbyte-internal-ops airbyte-ops cloud db start-proxy --port=5433
```

**Option B: Manual startup**

```bash
# Start the proxy on port 5433 (avoids conflicts with default PostgreSQL port 5432)
cloud-sql-proxy prod-ab-cloud-proj:us-west3:prod-pgsql-replica --port=5433
```

Then set environment variables for your application:
```bash
export USE_CLOUD_SQL_PROXY=1
export DB_PORT=5433
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json
```
