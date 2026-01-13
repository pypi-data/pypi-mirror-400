# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
"""MCP tools for querying the Airbyte Cloud Prod DB Replica.

This module provides MCP tools that wrap the query functions from
airbyte_ops_mcp.prod_db_access.queries for use by AI agents.
"""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Annotated, Any

import requests
from airbyte.exceptions import PyAirbyteInputError
from fastmcp import FastMCP
from pydantic import BaseModel, Field

from airbyte_ops_mcp.constants import OrganizationAliasEnum
from airbyte_ops_mcp.mcp._mcp_utils import mcp_tool, register_mcp_tools
from airbyte_ops_mcp.prod_db_access.queries import (
    query_actors_pinned_to_version,
    query_connections_by_connector,
    query_connections_by_destination_connector,
    query_connector_versions,
    query_dataplanes_list,
    query_failed_sync_attempts_for_connector,
    query_new_connector_releases,
    query_recent_syncs_for_connector,
    query_syncs_for_version_pinned_connector,
    query_workspace_info,
    query_workspaces_by_email_domain,
)


class StatusFilter(StrEnum):
    """Filter for job status in sync queries."""

    ALL = "all"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


# Cloud UI base URL for building connection URLs
CLOUD_UI_BASE_URL = "https://cloud.airbyte.com"


# =============================================================================
# Pydantic Models for MCP Tool Responses
# =============================================================================


class WorkspaceInfo(BaseModel):
    """Information about a workspace found by email domain search."""

    organization_id: str = Field(description="The organization UUID")
    workspace_id: str = Field(description="The workspace UUID")
    workspace_name: str = Field(description="The name of the workspace")
    slug: str | None = Field(
        default=None, description="The workspace slug (URL-friendly identifier)"
    )
    email: str | None = Field(
        default=None, description="The email address associated with the workspace"
    )
    dataplane_group_id: str | None = Field(
        default=None, description="The dataplane group UUID (region)"
    )
    dataplane_name: str | None = Field(
        default=None, description="The name of the dataplane (e.g., 'US', 'EU')"
    )
    created_at: datetime | None = Field(
        default=None, description="When the workspace was created"
    )


class WorkspacesByEmailDomainResult(BaseModel):
    """Result of looking up workspaces by email domain."""

    email_domain: str = Field(
        description="The email domain that was searched for (e.g., 'motherduck.com')"
    )
    total_workspaces_found: int = Field(
        description="Total number of workspaces matching the email domain"
    )
    unique_organization_ids: list[str] = Field(
        description="List of unique organization IDs found"
    )
    workspaces: list[WorkspaceInfo] = Field(
        description="List of workspaces matching the email domain"
    )


# Cloud registry URL for resolving canonical names
CLOUD_REGISTRY_URL = (
    "https://connectors.airbyte.com/files/registries/v0/cloud_registry.json"
)


def _resolve_canonical_name_to_definition_id(canonical_name: str) -> str:
    """Resolve a canonical connector name to a definition ID.

    Auto-detects whether the connector is a source or destination based on the
    canonical name prefix ("source-" or "destination-"). If no prefix is present,
    searches both sources and destinations.

    Args:
        canonical_name: Canonical connector name (e.g., 'source-youtube-analytics',
            'destination-duckdb', 'YouTube Analytics', 'DuckDB').

    Returns:
        The connector definition ID (UUID).

    Raises:
        PyAirbyteInputError: If the canonical name cannot be resolved.
    """
    response = requests.get(CLOUD_REGISTRY_URL, timeout=60)

    if response.status_code != 200:
        raise PyAirbyteInputError(
            message=f"Failed to fetch connector registry: {response.status_code}",
            context={"response": response.text},
        )

    data = response.json()
    normalized_input = canonical_name.lower().strip()

    # Determine which registries to search based on prefix
    is_source = normalized_input.startswith("source-")
    is_destination = normalized_input.startswith("destination-")

    # Search sources if it looks like a source or has no prefix
    if is_source or not is_destination:
        sources = data.get("sources", [])
        for source in sources:
            source_name = source.get("name", "").lower()
            if source_name == normalized_input:
                return source["sourceDefinitionId"]
            slugified = source_name.replace(" ", "-")
            if (
                slugified == normalized_input
                or f"source-{slugified}" == normalized_input
            ):
                return source["sourceDefinitionId"]

    # Search destinations if it looks like a destination or has no prefix
    if is_destination or not is_source:
        destinations = data.get("destinations", [])
        for destination in destinations:
            destination_name = destination.get("name", "").lower()
            if destination_name == normalized_input:
                return destination["destinationDefinitionId"]
            slugified = destination_name.replace(" ", "-")
            if (
                slugified == normalized_input
                or f"destination-{slugified}" == normalized_input
            ):
                return destination["destinationDefinitionId"]

    # Build appropriate error message based on what was searched
    if is_source:
        connector_type = "source"
        hint = (
            "Use the exact canonical name (e.g., 'source-youtube-analytics') "
            "or display name (e.g., 'YouTube Analytics')."
        )
    elif is_destination:
        connector_type = "destination"
        hint = (
            "Use the exact canonical name (e.g., 'destination-duckdb') "
            "or display name (e.g., 'DuckDB')."
        )
    else:
        connector_type = "connector"
        hint = (
            "Use the exact canonical name (e.g., 'source-youtube-analytics', "
            "'destination-duckdb') or display name (e.g., 'YouTube Analytics', 'DuckDB')."
        )

    raise PyAirbyteInputError(
        message=f"Could not find {connector_type} definition for canonical name: {canonical_name}",
        context={
            "hint": hint
            + " You can list available connectors using the connector registry tools.",
            "searched_for": canonical_name,
        },
    )


@mcp_tool(
    read_only=True,
    idempotent=True,
)
def query_prod_dataplanes() -> list[dict[str, Any]]:
    """List all dataplane groups with workspace counts.

    Returns information about all active dataplane groups in Airbyte Cloud,
    including the number of workspaces in each. Useful for understanding
    the distribution of workspaces across regions (US, US-Central, EU).

    Returns list of dicts with keys: dataplane_group_id, dataplane_name,
    organization_id, enabled, tombstone, created_at, workspace_count
    """
    return query_dataplanes_list()


@mcp_tool(
    read_only=True,
    idempotent=True,
)
def query_prod_workspace_info(
    workspace_id: Annotated[
        str,
        Field(description="Workspace UUID to look up"),
    ],
) -> dict[str, Any] | None:
    """Get workspace information including dataplane group.

    Returns details about a specific workspace, including which dataplane
    (region) it belongs to. Useful for determining if a workspace is in
    the EU region for filtering purposes.

    Returns dict with keys: workspace_id, workspace_name, slug, organization_id,
    dataplane_group_id, dataplane_name, created_at, tombstone
    Or None if workspace not found.
    """
    return query_workspace_info(workspace_id)


@mcp_tool(
    read_only=True,
    idempotent=True,
)
def query_prod_connector_versions(
    connector_definition_id: Annotated[
        str,
        Field(description="Connector definition UUID to list versions for"),
    ],
) -> list[dict[str, Any]]:
    """List all versions for a connector definition.

    Returns all published versions of a connector, ordered by last_published
    date descending. Useful for understanding version history and finding
    specific version IDs for pinning or rollout monitoring.

    Returns list of dicts with keys: version_id, docker_image_tag, docker_repository,
    release_stage, support_level, cdk_version, language, last_published, release_date
    """
    return query_connector_versions(connector_definition_id)


@mcp_tool(
    read_only=True,
    idempotent=True,
)
def query_prod_new_connector_releases(
    days: Annotated[
        int,
        Field(description="Number of days to look back (default: 7)", default=7),
    ] = 7,
    limit: Annotated[
        int,
        Field(description="Maximum number of results (default: 100)", default=100),
    ] = 100,
) -> list[dict[str, Any]]:
    """List recently published connector versions.

    Returns connector versions published within the specified number of days.
    Uses last_published timestamp which reflects when the version was actually
    deployed to the registry (not the changelog date).

    Returns list of dicts with keys: version_id, connector_definition_id, docker_repository,
    docker_image_tag, last_published, release_date, release_stage, support_level,
    cdk_version, language, created_at
    """
    return query_new_connector_releases(days=days, limit=limit)


@mcp_tool(
    read_only=True,
    idempotent=True,
)
def query_prod_actors_by_connector_version(
    connector_version_id: Annotated[
        str,
        Field(description="Connector version UUID to find pinned instances for"),
    ],
) -> list[dict[str, Any]]:
    """List actors (sources/destinations) pinned to a specific connector version.

    Returns all actors that have been explicitly pinned to a specific
    connector version via scoped_configuration. Useful for monitoring
    rollouts and understanding which customers are affected by version pins.

    The actor_id field is the actor ID (superset of source_id/destination_id).

    Returns list of dicts with keys: actor_id, connector_definition_id, origin_type,
    origin, description, created_at, expires_at, actor_name, workspace_id,
    workspace_name, organization_id, dataplane_group_id, dataplane_name
    """
    return query_actors_pinned_to_version(connector_version_id)


@mcp_tool(
    read_only=True,
    idempotent=True,
)
def query_prod_recent_syncs_for_version_pinned_connector(
    connector_version_id: Annotated[
        str,
        Field(description="Connector version UUID to find sync results for"),
    ],
    days: Annotated[
        int,
        Field(description="Number of days to look back (default: 7)", default=7),
    ] = 7,
    limit: Annotated[
        int,
        Field(description="Maximum number of results (default: 100)", default=100),
    ] = 100,
    successful_only: Annotated[
        bool,
        Field(
            description="If True, only return successful syncs (default: False)",
            default=False,
        ),
    ] = False,
) -> list[dict[str, Any]]:
    """List sync job results for actors PINNED to a specific connector version.

    IMPORTANT: This tool ONLY returns results for actors that have been explicitly
    pinned to the specified version via scoped_configuration. Most connections run
    unpinned and will NOT appear in these results.

    Use this tool when you want to monitor rollout health for actors that have been
    explicitly pinned to a pre-release or specific version. For finding healthy
    connections across ALL actors using a connector type (regardless of pinning),
    use query_prod_recent_syncs_for_connector instead.

    The actor_id field is the actor ID (superset of source_id/destination_id).

    Returns list of dicts with keys: job_id, connection_id, job_status, started_at,
    job_updated_at, connection_name, actor_id, actor_name, connector_definition_id,
    pin_origin_type, pin_origin, workspace_id, workspace_name, organization_id,
    dataplane_group_id, dataplane_name
    """
    return query_syncs_for_version_pinned_connector(
        connector_version_id,
        days=days,
        limit=limit,
        successful_only=successful_only,
    )


@mcp_tool(
    read_only=True,
    idempotent=True,
    open_world=True,
)
def query_prod_recent_syncs_for_connector(
    source_definition_id: Annotated[
        str | None,
        Field(
            description=(
                "Source connector definition ID (UUID) to search for. "
                "Provide this OR source_canonical_name OR destination_definition_id "
                "OR destination_canonical_name (exactly one required). "
                "Example: 'afa734e4-3571-11ec-991a-1e0031268139' for YouTube Analytics."
            ),
            default=None,
        ),
    ],
    source_canonical_name: Annotated[
        str | None,
        Field(
            description=(
                "Canonical source connector name to search for. "
                "Provide this OR source_definition_id OR destination_definition_id "
                "OR destination_canonical_name (exactly one required). "
                "Examples: 'source-youtube-analytics', 'YouTube Analytics'."
            ),
            default=None,
        ),
    ],
    destination_definition_id: Annotated[
        str | None,
        Field(
            description=(
                "Destination connector definition ID (UUID) to search for. "
                "Provide this OR destination_canonical_name OR source_definition_id "
                "OR source_canonical_name (exactly one required). "
                "Example: '94bd199c-2ff0-4aa2-b98e-17f0acb72610' for DuckDB."
            ),
            default=None,
        ),
    ],
    destination_canonical_name: Annotated[
        str | None,
        Field(
            description=(
                "Canonical destination connector name to search for. "
                "Provide this OR destination_definition_id OR source_definition_id "
                "OR source_canonical_name (exactly one required). "
                "Examples: 'destination-duckdb', 'DuckDB'."
            ),
            default=None,
        ),
    ],
    status_filter: Annotated[
        StatusFilter,
        Field(
            description=(
                "Filter by job status: 'all' (default), 'succeeded', or 'failed'. "
                "Use 'succeeded' to find healthy connections with recent successful syncs. "
                "Use 'failed' to find connections with recent failures."
            ),
            default=StatusFilter.ALL,
        ),
    ],
    organization_id: Annotated[
        str | OrganizationAliasEnum | None,
        Field(
            description=(
                "Optional organization ID (UUID) or alias to filter results. "
                "If provided, only syncs from this organization will be returned. "
                "Accepts '@airbyte-internal' as an alias for the Airbyte internal org."
            ),
            default=None,
        ),
    ],
    lookback_days: Annotated[
        int,
        Field(description="Number of days to look back (default: 7)", default=7),
    ],
    limit: Annotated[
        int,
        Field(description="Maximum number of results (default: 100)", default=100),
    ],
) -> list[dict[str, Any]]:
    """List recent sync jobs for ALL actors using a connector type.

    This tool finds all actors with the given connector definition and returns their
    recent sync jobs, regardless of whether they have explicit version pins. It filters
    out deleted actors, deleted workspaces, and deprecated connections.

    Use this tool to:
    - Find healthy connections with recent successful syncs (status_filter='succeeded')
    - Investigate connector issues across all users (status_filter='failed')
    - Get an overview of all recent sync activity (status_filter='all')

    Supports both SOURCE and DESTINATION connectors. Provide exactly one of:
    source_definition_id, source_canonical_name, destination_definition_id,
    or destination_canonical_name.

    Key fields in results:
    - job_status: 'succeeded', 'failed', 'cancelled', etc.
    - connection_id, connection_name: The connection that ran the sync
    - actor_id, actor_name: The source or destination actor
    - pin_origin_type, pin_origin, pinned_version_id: Version pin context (NULL if not pinned)
    """
    # Validate that exactly one connector parameter is provided
    provided_params = [
        source_definition_id,
        source_canonical_name,
        destination_definition_id,
        destination_canonical_name,
    ]
    num_provided = sum(p is not None for p in provided_params)
    if num_provided != 1:
        raise PyAirbyteInputError(
            message=(
                "Exactly one of source_definition_id, source_canonical_name, "
                "destination_definition_id, or destination_canonical_name must be provided."
            ),
        )

    # Determine if this is a destination connector
    is_destination = (
        destination_definition_id is not None or destination_canonical_name is not None
    )

    # Resolve canonical name to definition ID if needed
    resolved_definition_id: str
    if source_canonical_name:
        resolved_definition_id = _resolve_canonical_name_to_definition_id(
            canonical_name=source_canonical_name,
        )
    elif destination_canonical_name:
        resolved_definition_id = _resolve_canonical_name_to_definition_id(
            canonical_name=destination_canonical_name,
        )
    elif source_definition_id:
        resolved_definition_id = source_definition_id
    else:
        # We've validated exactly one param is provided, so this must be set
        assert destination_definition_id is not None
        resolved_definition_id = destination_definition_id

    # Resolve organization ID alias
    resolved_organization_id = OrganizationAliasEnum.resolve(organization_id)

    return query_recent_syncs_for_connector(
        connector_definition_id=resolved_definition_id,
        is_destination=is_destination,
        status_filter=status_filter,
        organization_id=resolved_organization_id,
        days=lookback_days,
        limit=limit,
    )


@mcp_tool(
    read_only=True,
    idempotent=True,
    open_world=True,
)
def query_prod_failed_sync_attempts_for_connector(
    source_definition_id: Annotated[
        str | None,
        Field(
            description=(
                "Source connector definition ID (UUID) to search for. "
                "Exactly one of this or source_canonical_name is required. "
                "Example: 'afa734e4-3571-11ec-991a-1e0031268139' for YouTube Analytics."
            ),
            default=None,
        ),
    ] = None,
    source_canonical_name: Annotated[
        str | None,
        Field(
            description=(
                "Canonical source connector name to search for. "
                "Exactly one of this or source_definition_id is required. "
                "Examples: 'source-youtube-analytics', 'YouTube Analytics'."
            ),
            default=None,
        ),
    ] = None,
    organization_id: Annotated[
        str | OrganizationAliasEnum | None,
        Field(
            description=(
                "Optional organization ID (UUID) or alias to filter results. "
                "If provided, only failed attempts from this organization will be returned. "
                "Accepts '@airbyte-internal' as an alias for the Airbyte internal org."
            ),
            default=None,
        ),
    ] = None,
    days: Annotated[
        int,
        Field(description="Number of days to look back (default: 7)", default=7),
    ] = 7,
    limit: Annotated[
        int,
        Field(description="Maximum number of results (default: 100)", default=100),
    ] = 100,
) -> list[dict[str, Any]]:
    """List failed sync attempts for ALL actors using a source connector type.

    This tool finds all actors with the given connector definition and returns their
    failed sync attempts, regardless of whether they have explicit version pins.

    This is useful for investigating connector issues across all users. Use this when
    you want to find failures for a connector type regardless of which version users
    are on.

    Note: This tool only supports SOURCE connectors. For destination connectors,
    a separate tool would be needed.

    Key fields in results:
    - failure_summary: JSON containing failure details including failureType and messages
    - pin_origin_type, pin_origin, pinned_version_id: Version pin context (NULL if not pinned)
    """
    # Validate that exactly one of the two parameters is provided
    if (source_definition_id is None) == (source_canonical_name is None):
        raise PyAirbyteInputError(
            message=(
                "Exactly one of source_definition_id or source_canonical_name "
                "must be provided, but not both."
            ),
        )

    # Resolve canonical name to definition ID if needed
    resolved_definition_id: str
    if source_canonical_name:
        resolved_definition_id = _resolve_canonical_name_to_definition_id(
            canonical_name=source_canonical_name,
        )
    else:
        resolved_definition_id = source_definition_id  # type: ignore[assignment]

    # Resolve organization ID alias
    resolved_organization_id = OrganizationAliasEnum.resolve(organization_id)

    return query_failed_sync_attempts_for_connector(
        connector_definition_id=resolved_definition_id,
        organization_id=resolved_organization_id,
        days=days,
        limit=limit,
    )


@mcp_tool(
    read_only=True,
    idempotent=True,
    open_world=True,
)
def query_prod_connections_by_connector(
    source_definition_id: Annotated[
        str | None,
        Field(
            description=(
                "Source connector definition ID (UUID) to search for. "
                "Exactly one of source_definition_id, source_canonical_name, "
                "destination_definition_id, or destination_canonical_name is required. "
                "Example: 'afa734e4-3571-11ec-991a-1e0031268139' for YouTube Analytics."
            ),
            default=None,
        ),
    ] = None,
    source_canonical_name: Annotated[
        str | None,
        Field(
            description=(
                "Canonical source connector name to search for. "
                "Exactly one of source_definition_id, source_canonical_name, "
                "destination_definition_id, or destination_canonical_name is required. "
                "Examples: 'source-youtube-analytics', 'YouTube Analytics'."
            ),
            default=None,
        ),
    ] = None,
    destination_definition_id: Annotated[
        str | None,
        Field(
            description=(
                "Destination connector definition ID (UUID) to search for. "
                "Exactly one of source_definition_id, source_canonical_name, "
                "destination_definition_id, or destination_canonical_name is required. "
                "Example: 'e5c8e66c-a480-4a5e-9c0e-e8e5e4c5c5c5' for DuckDB."
            ),
            default=None,
        ),
    ] = None,
    destination_canonical_name: Annotated[
        str | None,
        Field(
            description=(
                "Canonical destination connector name to search for. "
                "Exactly one of source_definition_id, source_canonical_name, "
                "destination_definition_id, or destination_canonical_name is required. "
                "Examples: 'destination-duckdb', 'DuckDB'."
            ),
            default=None,
        ),
    ] = None,
    organization_id: Annotated[
        str | OrganizationAliasEnum | None,
        Field(
            description=(
                "Optional organization ID (UUID) or alias to filter results. "
                "If provided, only connections in this organization will be returned. "
                "Accepts '@airbyte-internal' as an alias for the Airbyte internal org."
            ),
            default=None,
        ),
    ] = None,
    limit: Annotated[
        int,
        Field(description="Maximum number of results (default: 1000)", default=1000),
    ] = 1000,
) -> list[dict[str, Any]]:
    """Search for all connections using a specific source or destination connector type.

    This tool queries the Airbyte Cloud Prod DB Replica directly for fast results.
    It finds all connections where the source or destination connector matches the
    specified type, regardless of how the connector is named by users.

    Optionally filter by organization_id to limit results to a specific organization.
    Use '@airbyte-internal' as an alias for the Airbyte internal organization.

    Returns a list of connection dicts with workspace context and clickable Cloud UI URLs.
    For source queries, returns: connection_id, connection_name, connection_url, source_id,
    source_name, source_definition_id, workspace_id, workspace_name, organization_id,
    dataplane_group_id, dataplane_name.
    For destination queries, returns: connection_id, connection_name, connection_url,
    destination_id, destination_name, destination_definition_id, workspace_id,
    workspace_name, organization_id, dataplane_group_id, dataplane_name.
    """
    # Validate that exactly one of the four connector parameters is provided
    provided_params = [
        source_definition_id,
        source_canonical_name,
        destination_definition_id,
        destination_canonical_name,
    ]
    num_provided = sum(p is not None for p in provided_params)
    if num_provided != 1:
        raise PyAirbyteInputError(
            message=(
                "Exactly one of source_definition_id, source_canonical_name, "
                "destination_definition_id, or destination_canonical_name must be provided."
            ),
        )

    # Determine if this is a source or destination query and resolve the definition ID
    is_source_query = (
        source_definition_id is not None or source_canonical_name is not None
    )
    resolved_definition_id: str

    if source_canonical_name:
        resolved_definition_id = _resolve_canonical_name_to_definition_id(
            canonical_name=source_canonical_name,
        )
    elif source_definition_id:
        resolved_definition_id = source_definition_id
    elif destination_canonical_name:
        resolved_definition_id = _resolve_canonical_name_to_definition_id(
            canonical_name=destination_canonical_name,
        )
    else:
        resolved_definition_id = destination_definition_id  # type: ignore[assignment]

    # Resolve organization ID alias
    resolved_organization_id = OrganizationAliasEnum.resolve(organization_id)

    # Query the database based on connector type
    if is_source_query:
        return [
            {
                "organization_id": str(row.get("organization_id", "")),
                "workspace_id": str(row["workspace_id"]),
                "workspace_name": row.get("workspace_name", ""),
                "connection_id": str(row["connection_id"]),
                "connection_name": row.get("connection_name", ""),
                "connection_url": (
                    f"{CLOUD_UI_BASE_URL}/workspaces/{row['workspace_id']}"
                    f"/connections/{row['connection_id']}/status"
                ),
                "source_id": str(row["source_id"]),
                "source_name": row.get("source_name", ""),
                "source_definition_id": str(row["source_definition_id"]),
                "dataplane_group_id": str(row.get("dataplane_group_id", "")),
                "dataplane_name": row.get("dataplane_name", ""),
            }
            for row in query_connections_by_connector(
                connector_definition_id=resolved_definition_id,
                organization_id=resolved_organization_id,
                limit=limit,
            )
        ]

    # Destination query
    return [
        {
            "organization_id": str(row.get("organization_id", "")),
            "workspace_id": str(row["workspace_id"]),
            "workspace_name": row.get("workspace_name", ""),
            "connection_id": str(row["connection_id"]),
            "connection_name": row.get("connection_name", ""),
            "connection_url": (
                f"{CLOUD_UI_BASE_URL}/workspaces/{row['workspace_id']}"
                f"/connections/{row['connection_id']}/status"
            ),
            "destination_id": str(row["destination_id"]),
            "destination_name": row.get("destination_name", ""),
            "destination_definition_id": str(row["destination_definition_id"]),
            "dataplane_group_id": str(row.get("dataplane_group_id", "")),
            "dataplane_name": row.get("dataplane_name", ""),
        }
        for row in query_connections_by_destination_connector(
            connector_definition_id=resolved_definition_id,
            organization_id=resolved_organization_id,
            limit=limit,
        )
    ]


@mcp_tool(
    read_only=True,
    idempotent=True,
)
def query_prod_workspaces_by_email_domain(
    email_domain: Annotated[
        str,
        Field(
            description=(
                "Email domain to search for (e.g., 'motherduck.com', 'fivetran.com'). "
                "Do not include the '@' symbol. This will find workspaces where users "
                "have email addresses with this domain."
            ),
        ),
    ],
    limit: Annotated[
        int,
        Field(
            description="Maximum number of workspaces to return (default: 100)",
            default=100,
        ),
    ] = 100,
) -> WorkspacesByEmailDomainResult:
    """Find workspaces by email domain.

    This tool searches for workspaces where users have email addresses matching
    the specified domain. This is useful for identifying workspaces belonging to
    specific companies - for example, searching for "motherduck.com" will find
    workspaces belonging to MotherDuck employees.

    Use cases:
    - Finding partner organization connections for testing connector fixes
    - Identifying internal test accounts for specific integrations
    - Locating workspaces belonging to technology partners

    The returned organization IDs can be used with other tools like
    `query_prod_connections_by_connector` to find connections within
    those organizations for safe testing.
    """
    # Strip leading @ if provided
    clean_domain = email_domain.lstrip("@")

    # Query the database
    rows = query_workspaces_by_email_domain(email_domain=clean_domain, limit=limit)

    # Convert rows to Pydantic models
    workspaces = [
        WorkspaceInfo(
            organization_id=str(row["organization_id"]),
            workspace_id=str(row["workspace_id"]),
            workspace_name=row.get("workspace_name", ""),
            slug=row.get("slug"),
            email=row.get("email"),
            dataplane_group_id=str(row["dataplane_group_id"])
            if row.get("dataplane_group_id")
            else None,
            dataplane_name=row.get("dataplane_name"),
            created_at=row.get("created_at"),
        )
        for row in rows
    ]

    # Extract unique organization IDs
    unique_org_ids = list(dict.fromkeys(w.organization_id for w in workspaces))

    return WorkspacesByEmailDomainResult(
        email_domain=clean_domain,
        total_workspaces_found=len(workspaces),
        unique_organization_ids=unique_org_ids,
        workspaces=workspaces,
    )


def register_prod_db_query_tools(app: FastMCP) -> None:
    """Register prod DB query tools with the FastMCP app."""
    register_mcp_tools(app, domain=__name__)
