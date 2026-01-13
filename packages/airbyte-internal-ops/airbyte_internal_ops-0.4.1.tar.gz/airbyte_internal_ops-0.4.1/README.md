# airbyte-ops-mcp

MCP and API interfaces that let the agents do the admin work.

## Installing Ops MCP in your Client

This config example will help you add the MCP server to your client:

```json
{
  "mcpServers": {
    "airbyte-ops-mcp": {
      "type": "stdio",
      "command": "uv",
      "args": [
        "run",
        "--project=/Users/aj.steers/repos/airbyte-ops-mcp/",
        "airbyte-ops-mcp"
      ],
      "env": {
        "AIRBYTE_MCP_ENV_FILE": "/Users/{user-id}/.mcp/airbyte_mcp.env"
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

Your `.env` file should include the following values:

```ini
# Creds for Airbyte Cloud OAuth
AIRBYTE_CLOUD_CLIENT_ID="..."
AIRBYTE_CLOUD_CLIENT_SECRET="..."

# Required for elevated admin operations
AIRBYTE_INTERNAL_ADMIN_FLAG=airbyte.io
AIRBYTE_INTERNAL_ADMIN_USER={my-id}@airbyte.io

# Workspace ID for Testing
AIRBYTE_CLOUD_TEST_WORKSPACE_ID="..."
```

## Getting Started

Once configured, use the `test_my_tools` prompt by typing "/test" into your agent and selecting the auto-complete option for the `test_my_tools` prompt.

This prompt will step through all the tools, demoing their capabilities.

## Usage Examples

### Testing MCP Tools Locally

Use the `mcp-tool-test` poe task to test tools directly:

```bash
# List connectors in a repo
poe mcp-tool-test list_connectors_in_repo '{"repo_path": "/path/to/airbyte"}'

# Get cloud connector version
poe mcp-tool-test get_cloud_connector_version '{"workspace_id": "...", "actor_id": "..."}'
```

### Using Cloud SQL Proxy for Database Tools

Some tools (like `list_org_connections_by_source_type_db`) require access to the Airbyte Cloud Prod DB Replica. To test these locally:

1. Authenticate with GCP:
   ```bash
   gcloud auth login
   gcloud auth application-default login
   ```

2. Start Cloud SQL Proxy using one of the following methods:

   **Option A: Using the CLI (Recommended)**
   
   Pre-install the CLI tool:
   ```bash
   uv tool install airbyte-internal-ops
   airbyte-ops cloud db start-proxy --port=15432
   ```
   
   Or use as a single-step command:
   ```bash
   uvx --from=airbyte-internal-ops airbyte-ops cloud db start-proxy --port=15432
   ```

   **Option B: Manual startup**
   
   ```bash
   cloud-sql-proxy prod-ab-cloud-proj:us-west3:prod-pgsql-replica --port=15432
   ```

3. Run the tool with proxy environment variables:
   ```bash
   USE_CLOUD_SQL_PROXY=1 DB_PORT=15432 poe mcp-tool-test list_org_connections_by_source_type_db \
     '{"organization_id": "...", "connector_canonical_name": "source-youtube-analytics"}'
   ```

## Instructions for Agents

When working with a user to set up and use this MCP server, agents should follow these steps for authentication:

### GCP Authentication Flow

For tools that require GCP access (database queries, secret manager, etc.), guide the user through authentication:

1. **Check if gcloud is installed.** If not, install it:
   ```bash
   curl -sSL https://sdk.cloud.google.com | bash -s -- --disable-prompts
   ```

2. **Run gcloud auth login with `--no-launch-browser`** to get a verification URL:
   ```bash
   gcloud auth login --no-launch-browser
   ```
   Send the verification URL to the user and ask them to complete sign-in and provide the verification code.

3. **Set up Application Default Credentials (ADC)** for library access:
   ```bash
   gcloud auth application-default login --no-launch-browser
   ```
   Again, send the URL to the user and collect the verification code.

4. **For database tools**, start Cloud SQL Proxy on an available port and use the `USE_CLOUD_SQL_PROXY` and `DB_PORT` environment variables.

### Airbyte Cloud Authentication

For tools that interact with Airbyte Cloud API, ensure the user has configured:
- `AIRBYTE_CLOUD_CLIENT_ID` and `AIRBYTE_CLOUD_CLIENT_SECRET` in their `.env` file
- For admin operations: `AIRBYTE_INTERNAL_ADMIN_FLAG=airbyte.io` and `AIRBYTE_INTERNAL_ADMIN_USER`
