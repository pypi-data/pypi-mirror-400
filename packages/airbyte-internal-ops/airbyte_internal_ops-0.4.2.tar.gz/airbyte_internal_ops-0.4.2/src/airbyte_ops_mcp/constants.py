# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
"""Constants for the Airbyte Admin MCP server."""

from __future__ import annotations

from enum import Enum, StrEnum

from airbyte.exceptions import PyAirbyteInputError

MCP_SERVER_NAME = "airbyte-internal-ops"
"""The name of the MCP server."""

USER_AGENT = "Airbyte-Internal-Ops Python client"
"""User-Agent string for HTTP requests to Airbyte Cloud APIs."""

# Environment variable names for internal admin authentication
ENV_AIRBYTE_INTERNAL_ADMIN_FLAG = "AIRBYTE_INTERNAL_ADMIN_FLAG"
ENV_AIRBYTE_INTERNAL_ADMIN_USER = "AIRBYTE_INTERNAL_ADMIN_USER"

# Environment variable for GCP credentials (JSON content, not file path)
ENV_GCP_PROD_DB_ACCESS_CREDENTIALS = "GCP_PROD_DB_ACCESS_CREDENTIALS"
"""Environment variable containing GCP service account JSON credentials for prod DB access."""

# Expected values for internal admin authentication
EXPECTED_ADMIN_FLAG_VALUE = "airbyte.io"
EXPECTED_ADMIN_EMAIL_DOMAIN = "@airbyte.io"

# =============================================================================
# HTTP Header Names for Airbyte Cloud Authentication
# =============================================================================
# These headers follow the PyAirbyte convention for passing credentials
# via HTTP when running as an MCP HTTP server.

HEADER_AIRBYTE_CLOUD_CLIENT_ID = "X-Airbyte-Cloud-Client-Id"
"""HTTP header for OAuth client ID."""

HEADER_AIRBYTE_CLOUD_CLIENT_SECRET = "X-Airbyte-Cloud-Client-Secret"
"""HTTP header for OAuth client secret."""

HEADER_AIRBYTE_CLOUD_WORKSPACE_ID = "X-Airbyte-Cloud-Workspace-Id"
"""HTTP header for default workspace ID."""

HEADER_AIRBYTE_CLOUD_API_URL = "X-Airbyte-Cloud-Api-Url"
"""HTTP header for API root URL override."""

# =============================================================================
# GCP and Prod DB Constants (from connection-retriever)
# =============================================================================

GCP_PROJECT_NAME = "prod-ab-cloud-proj"
"""The GCP project name for Airbyte Cloud production."""

CLOUD_SQL_INSTANCE = "prod-ab-cloud-proj:us-west3:prod-pgsql-replica"
"""The Cloud SQL instance connection name for the Prod DB Replica."""

DEFAULT_CLOUD_SQL_PROXY_PORT = 15432
"""Default port for Cloud SQL Proxy connections."""

CLOUD_SQL_PROXY_PID_FILE = "/tmp/airbyte-cloud-sql-proxy.pid"
"""PID file for tracking the Cloud SQL Proxy process."""

CLOUD_REGISTRY_URL = (
    "https://connectors.airbyte.com/files/registries/v0/cloud_registry.json"
)
"""URL for the Airbyte Cloud connector registry."""

# =============================================================================
# Organization ID Aliases
# =============================================================================


class OrganizationAliasEnum(StrEnum):
    """Organization ID aliases that can be used in place of UUIDs.

    Each member's name is the alias (e.g., "@airbyte-internal") and its value
    is the actual organization UUID. Use `OrganizationAliasEnum.resolve()` to
    resolve aliases to actual IDs.
    """

    AIRBYTE_INTERNAL = "664c690e-5263-49ba-b01f-4a6759b3330a"
    """The Airbyte internal organization for testing and internal operations.

    Alias: @airbyte-internal
    """

    @classmethod
    def resolve(cls, org_id: str | None) -> str | None:
        """Resolve an organization ID alias to its actual UUID.

        Accepts either an alias string (e.g., "@airbyte-internal") or an
        OrganizationAliasEnum enum member, and returns the actual UUID.

        Returns:
            The resolved organization ID (UUID), or None if input is None.
            If the input doesn't start with "@", it is returned unchanged.

        Raises:
            PyAirbyteInputError: If the input starts with "@" but is not a recognized alias.
        """
        if org_id is None:
            return None

        # Handle OrganizationAliasEnum enum members directly
        if isinstance(org_id, cls):
            return org_id.value

        # If it doesn't look like an alias, return as-is (assume it's a UUID)
        if not org_id.startswith("@"):
            return org_id

        # Handle alias strings or raise an error if invalid
        alias_mapping = {
            "@airbyte-internal": cls.AIRBYTE_INTERNAL.value,
        }
        if org_id not in alias_mapping:
            raise PyAirbyteInputError(
                message=f"Unknown organization alias: {org_id}",
                context={
                    "valid_aliases": list(alias_mapping.keys()),
                },
            )
        return alias_mapping[org_id]


CONNECTION_RETRIEVER_PG_CONNECTION_DETAILS_SECRET_ID = (
    "projects/587336813068/secrets/CONNECTION_RETRIEVER_PG_CONNECTION_DETAILS"
)
"""GCP Secret Manager ID for Prod DB connection details."""


class ConnectionObject(Enum):
    """Types of connection objects that can be retrieved."""

    CONNECTION = "connection"
    SOURCE_ID = "source-id"
    DESTINATION_ID = "destination-id"
    DESTINATION_CONFIG = "destination-config"
    SOURCE_CONFIG = "source-config"
    CATALOG = "catalog"
    CONFIGURED_CATALOG = "configured-catalog"
    STATE = "state"
    WORKSPACE_ID = "workspace-id"
    DESTINATION_DOCKER_IMAGE = "destination-docker-image"
    SOURCE_DOCKER_IMAGE = "source-docker-image"
