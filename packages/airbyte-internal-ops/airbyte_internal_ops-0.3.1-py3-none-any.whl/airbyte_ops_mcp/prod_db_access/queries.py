# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
"""Query execution functions for Airbyte Cloud Prod DB Replica.

This module provides functions that execute SQL queries against the Prod DB Replica
and return structured results. Each function wraps a SQL template from sql.py.
"""

from __future__ import annotations

import logging
from collections.abc import Mapping
from datetime import datetime, timedelta, timezone
from time import perf_counter
from typing import Any

import sqlalchemy
from google.cloud import secretmanager

from airbyte_ops_mcp.gcp_auth import get_secret_manager_client
from airbyte_ops_mcp.prod_db_access.db_engine import get_pool
from airbyte_ops_mcp.prod_db_access.sql import (
    SELECT_ACTORS_PINNED_TO_VERSION,
    SELECT_CONNECTIONS_BY_CONNECTOR,
    SELECT_CONNECTIONS_BY_CONNECTOR_AND_ORG,
    SELECT_CONNECTIONS_BY_DESTINATION_CONNECTOR,
    SELECT_CONNECTIONS_BY_DESTINATION_CONNECTOR_AND_ORG,
    SELECT_CONNECTOR_VERSIONS,
    SELECT_DATAPLANES_LIST,
    SELECT_FAILED_SYNC_ATTEMPTS_FOR_CONNECTOR,
    SELECT_NEW_CONNECTOR_RELEASES,
    SELECT_ORG_WORKSPACES,
    SELECT_RECENT_FAILED_SYNCS_FOR_DESTINATION_CONNECTOR,
    SELECT_RECENT_FAILED_SYNCS_FOR_SOURCE_CONNECTOR,
    SELECT_RECENT_SUCCESSFUL_SYNCS_FOR_DESTINATION_CONNECTOR,
    SELECT_RECENT_SUCCESSFUL_SYNCS_FOR_SOURCE_CONNECTOR,
    SELECT_RECENT_SYNCS_FOR_DESTINATION_CONNECTOR,
    SELECT_RECENT_SYNCS_FOR_SOURCE_CONNECTOR,
    SELECT_SUCCESSFUL_SYNCS_FOR_VERSION,
    SELECT_SYNC_RESULTS_FOR_VERSION,
    SELECT_WORKSPACE_INFO,
    SELECT_WORKSPACES_BY_EMAIL_DOMAIN,
)

logger = logging.getLogger(__name__)


def _run_sql_query(
    statement: sqlalchemy.sql.elements.TextClause,
    parameters: Mapping[str, Any] | None = None,
    *,
    query_name: str | None = None,
    gsm_client: secretmanager.SecretManagerServiceClient | None = None,
) -> list[dict[str, Any]]:
    """Execute a SQL text statement and return rows as list[dict], logging elapsed time.

    Args:
        statement: SQLAlchemy text clause to execute
        parameters: Query parameters to bind
        query_name: Optional name for logging (defaults to first line of SQL)
        gsm_client: GCP Secret Manager client for retrieving credentials.
            If None, a new client will be instantiated.

    Returns:
        List of row dicts from the query result
    """
    if gsm_client is None:
        gsm_client = get_secret_manager_client()
    pool = get_pool(gsm_client)
    start = perf_counter()
    with pool.connect() as conn:
        result = conn.execute(statement, parameters or {})
        rows = [dict(row._mapping) for row in result]
    elapsed = perf_counter() - start

    name = query_name or "SQL query"
    logger.info("Prod DB query %s returned %d rows in %.3f s", name, len(rows), elapsed)

    return rows


def query_connections_by_connector(
    connector_definition_id: str,
    organization_id: str | None = None,
    limit: int = 1000,
    *,
    gsm_client: secretmanager.SecretManagerServiceClient | None = None,
) -> list[dict[str, Any]]:
    """Query connections by source connector type, optionally filtered by organization.

    Args:
        connector_definition_id: Connector definition UUID to filter by
        organization_id: Optional organization UUID to search within
        limit: Maximum number of results (default: 1000)
        gsm_client: GCP Secret Manager client. If None, a new client will be instantiated.

    Returns:
        List of connection records with workspace and dataplane info
    """
    # Use separate queries to avoid pg8000 NULL parameter type issues
    # pg8000 cannot determine the type of NULL parameters in patterns like
    # "(:param IS NULL OR column = :param)"
    if organization_id is None:
        return _run_sql_query(
            SELECT_CONNECTIONS_BY_CONNECTOR,
            parameters={
                "connector_definition_id": connector_definition_id,
                "limit": limit,
            },
            query_name="SELECT_CONNECTIONS_BY_CONNECTOR",
            gsm_client=gsm_client,
        )

    return _run_sql_query(
        SELECT_CONNECTIONS_BY_CONNECTOR_AND_ORG,
        parameters={
            "connector_definition_id": connector_definition_id,
            "organization_id": organization_id,
            "limit": limit,
        },
        query_name="SELECT_CONNECTIONS_BY_CONNECTOR_AND_ORG",
        gsm_client=gsm_client,
    )


def query_connections_by_destination_connector(
    connector_definition_id: str,
    organization_id: str | None = None,
    limit: int = 1000,
    *,
    gsm_client: secretmanager.SecretManagerServiceClient | None = None,
) -> list[dict[str, Any]]:
    """Query connections by destination connector type, optionally filtered by organization.

    Args:
        connector_definition_id: Destination connector definition UUID to filter by
        organization_id: Optional organization UUID to search within
        limit: Maximum number of results (default: 1000)
        gsm_client: GCP Secret Manager client. If None, a new client will be instantiated.

    Returns:
        List of connection records with workspace and dataplane info
    """
    # Use separate queries to avoid pg8000 NULL parameter type issues
    if organization_id is None:
        return _run_sql_query(
            SELECT_CONNECTIONS_BY_DESTINATION_CONNECTOR,
            parameters={
                "connector_definition_id": connector_definition_id,
                "limit": limit,
            },
            query_name="SELECT_CONNECTIONS_BY_DESTINATION_CONNECTOR",
            gsm_client=gsm_client,
        )

    return _run_sql_query(
        SELECT_CONNECTIONS_BY_DESTINATION_CONNECTOR_AND_ORG,
        parameters={
            "connector_definition_id": connector_definition_id,
            "organization_id": organization_id,
            "limit": limit,
        },
        query_name="SELECT_CONNECTIONS_BY_DESTINATION_CONNECTOR_AND_ORG",
        gsm_client=gsm_client,
    )


def query_connector_versions(
    connector_definition_id: str,
    *,
    gsm_client: secretmanager.SecretManagerServiceClient | None = None,
) -> list[dict[str, Any]]:
    """Query all versions for a connector definition.

    Args:
        connector_definition_id: Connector definition UUID
        gsm_client: GCP Secret Manager client. If None, a new client will be instantiated.

    Returns:
        List of version records ordered by last_published DESC
    """
    return _run_sql_query(
        SELECT_CONNECTOR_VERSIONS,
        parameters={"actor_definition_id": connector_definition_id},
        query_name="SELECT_CONNECTOR_VERSIONS",
        gsm_client=gsm_client,
    )


def query_new_connector_releases(
    days: int = 7,
    limit: int = 100,
    *,
    gsm_client: secretmanager.SecretManagerServiceClient | None = None,
) -> list[dict[str, Any]]:
    """Query recently published connector versions.

    Args:
        days: Number of days to look back (default: 7)
        limit: Maximum number of results (default: 100)
        gsm_client: GCP Secret Manager client. If None, a new client will be instantiated.

    Returns:
        List of recently published connector versions
    """
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
    return _run_sql_query(
        SELECT_NEW_CONNECTOR_RELEASES,
        parameters={"cutoff_date": cutoff_date, "limit": limit},
        query_name="SELECT_NEW_CONNECTOR_RELEASES",
        gsm_client=gsm_client,
    )


def query_actors_pinned_to_version(
    connector_version_id: str,
    *,
    gsm_client: secretmanager.SecretManagerServiceClient | None = None,
) -> list[dict[str, Any]]:
    """Query actors (sources/destinations) pinned to a specific connector version.

    Args:
        connector_version_id: Connector version UUID to search for
        gsm_client: GCP Secret Manager client. If None, a new client will be instantiated.

    Returns:
        List of actors pinned to the specified version
    """
    return _run_sql_query(
        SELECT_ACTORS_PINNED_TO_VERSION,
        parameters={"actor_definition_version_id": connector_version_id},
        query_name="SELECT_ACTORS_PINNED_TO_VERSION",
        gsm_client=gsm_client,
    )


def query_syncs_for_version_pinned_connector(
    connector_version_id: str,
    days: int = 7,
    limit: int = 100,
    successful_only: bool = False,
    *,
    gsm_client: secretmanager.SecretManagerServiceClient | None = None,
) -> list[dict[str, Any]]:
    """Query sync job results for actors pinned to a specific connector version.

    Args:
        connector_version_id: Connector version UUID to filter by
        days: Number of days to look back (default: 7)
        limit: Maximum number of results (default: 100)
        successful_only: If True, only return successful syncs (default: False)
        gsm_client: GCP Secret Manager client. If None, a new client will be instantiated.

    Returns:
        List of sync job results
    """
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
    query = (
        SELECT_SUCCESSFUL_SYNCS_FOR_VERSION
        if successful_only
        else SELECT_SYNC_RESULTS_FOR_VERSION
    )
    query_name = (
        "SELECT_SUCCESSFUL_SYNCS_FOR_VERSION"
        if successful_only
        else "SELECT_SYNC_RESULTS_FOR_VERSION"
    )
    return _run_sql_query(
        query,
        parameters={
            "actor_definition_version_id": connector_version_id,
            "cutoff_date": cutoff_date,
            "limit": limit,
        },
        query_name=query_name,
        gsm_client=gsm_client,
    )


def query_failed_sync_attempts_for_connector(
    connector_definition_id: str,
    organization_id: str | None = None,
    days: int = 7,
    limit: int = 100,
    *,
    gsm_client: secretmanager.SecretManagerServiceClient | None = None,
) -> list[dict[str, Any]]:
    """Query failed sync attempts for ALL actors using a connector definition.

    Finds all actors with the given actor_definition_id and returns their failed
    sync attempts, regardless of whether they have explicit version pins.

    This is useful for investigating connector issues across all users.

    Note: This query only supports SOURCE connectors (joins via connection.source_id).
    For destination connectors, a separate query would be needed.

    Args:
        connector_definition_id: Connector definition UUID to filter by
        organization_id: Optional organization UUID to filter results by (post-query filter)
        days: Number of days to look back (default: 7)
        limit: Maximum number of results (default: 100)
        gsm_client: GCP Secret Manager client. If None, a new client will be instantiated.

    Returns:
        List of failed sync attempt records with failure_summary and workspace info
    """
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)

    results = _run_sql_query(
        SELECT_FAILED_SYNC_ATTEMPTS_FOR_CONNECTOR,
        parameters={
            "connector_definition_id": connector_definition_id,
            "cutoff_date": cutoff_date,
            "limit": limit,
        },
        query_name="SELECT_FAILED_SYNC_ATTEMPTS_FOR_CONNECTOR",
        gsm_client=gsm_client,
    )

    # Post-query filter by organization_id if provided
    if organization_id is not None:
        results = [
            r for r in results if str(r.get("organization_id")) == organization_id
        ]

    return results


def query_recent_syncs_for_connector(
    connector_definition_id: str,
    is_destination: bool = False,
    status_filter: str = "all",
    organization_id: str | None = None,
    days: int = 7,
    limit: int = 100,
    *,
    gsm_client: secretmanager.SecretManagerServiceClient | None = None,
) -> list[dict[str, Any]]:
    """Query recent sync jobs for ALL actors using a connector definition.

    Finds all actors with the given actor_definition_id and returns their sync jobs,
    regardless of whether they have explicit version pins. Filters out deleted actors,
    deleted workspaces, and deprecated connections.

    This is useful for finding healthy connections with recent successful syncs,
    or for investigating connector issues across all users.

    Args:
        connector_definition_id: Connector definition UUID to filter by
        is_destination: If True, query destination connectors; if False, query sources
        status_filter: Filter by job status - "all", "succeeded", or "failed"
        organization_id: Optional organization UUID to filter results by (post-query filter)
        days: Number of days to look back (default: 7)
        limit: Maximum number of results (default: 100)
        gsm_client: GCP Secret Manager client. If None, a new client will be instantiated.

    Returns:
        List of sync job records with workspace info and optional pin context
    """
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)

    # Select the appropriate query based on connector type and status filter
    if is_destination:
        if status_filter == "succeeded":
            query = SELECT_RECENT_SUCCESSFUL_SYNCS_FOR_DESTINATION_CONNECTOR
            query_name = "SELECT_RECENT_SUCCESSFUL_SYNCS_FOR_DESTINATION_CONNECTOR"
        elif status_filter == "failed":
            query = SELECT_RECENT_FAILED_SYNCS_FOR_DESTINATION_CONNECTOR
            query_name = "SELECT_RECENT_FAILED_SYNCS_FOR_DESTINATION_CONNECTOR"
        else:
            query = SELECT_RECENT_SYNCS_FOR_DESTINATION_CONNECTOR
            query_name = "SELECT_RECENT_SYNCS_FOR_DESTINATION_CONNECTOR"
    else:
        if status_filter == "succeeded":
            query = SELECT_RECENT_SUCCESSFUL_SYNCS_FOR_SOURCE_CONNECTOR
            query_name = "SELECT_RECENT_SUCCESSFUL_SYNCS_FOR_SOURCE_CONNECTOR"
        elif status_filter == "failed":
            query = SELECT_RECENT_FAILED_SYNCS_FOR_SOURCE_CONNECTOR
            query_name = "SELECT_RECENT_FAILED_SYNCS_FOR_SOURCE_CONNECTOR"
        else:
            query = SELECT_RECENT_SYNCS_FOR_SOURCE_CONNECTOR
            query_name = "SELECT_RECENT_SYNCS_FOR_SOURCE_CONNECTOR"

    results = _run_sql_query(
        query,
        parameters={
            "connector_definition_id": connector_definition_id,
            "cutoff_date": cutoff_date,
            "limit": limit,
        },
        query_name=query_name,
        gsm_client=gsm_client,
    )

    # Post-query filter by organization_id if provided
    if organization_id is not None:
        results = [
            r for r in results if str(r.get("organization_id")) == organization_id
        ]

    return results


def query_dataplanes_list(
    *,
    gsm_client: secretmanager.SecretManagerServiceClient | None = None,
) -> list[dict[str, Any]]:
    """Query all dataplane groups with workspace counts.

    Args:
        gsm_client: GCP Secret Manager client. If None, a new client will be instantiated.

    Returns:
        List of dataplane groups ordered by workspace count DESC
    """
    return _run_sql_query(
        SELECT_DATAPLANES_LIST,
        query_name="SELECT_DATAPLANES_LIST",
        gsm_client=gsm_client,
    )


def query_workspace_info(
    workspace_id: str,
    *,
    gsm_client: secretmanager.SecretManagerServiceClient | None = None,
) -> dict[str, Any] | None:
    """Query workspace info including dataplane group.

    Args:
        workspace_id: Workspace UUID
        gsm_client: GCP Secret Manager client. If None, a new client will be instantiated.

    Returns:
        Workspace info dict, or None if not found
    """
    rows = _run_sql_query(
        SELECT_WORKSPACE_INFO,
        parameters={"workspace_id": workspace_id},
        query_name="SELECT_WORKSPACE_INFO",
        gsm_client=gsm_client,
    )
    return rows[0] if rows else None


def query_org_workspaces(
    organization_id: str,
    *,
    gsm_client: secretmanager.SecretManagerServiceClient | None = None,
) -> list[dict[str, Any]]:
    """Query all workspaces in an organization with dataplane info.

    Args:
        organization_id: Organization UUID
        gsm_client: GCP Secret Manager client. If None, a new client will be instantiated.

    Returns:
        List of workspaces in the organization
    """
    return _run_sql_query(
        SELECT_ORG_WORKSPACES,
        parameters={"organization_id": organization_id},
        query_name="SELECT_ORG_WORKSPACES",
        gsm_client=gsm_client,
    )


def query_workspaces_by_email_domain(
    email_domain: str,
    limit: int = 100,
    *,
    gsm_client: secretmanager.SecretManagerServiceClient | None = None,
) -> list[dict[str, Any]]:
    """Query workspaces by email domain.

    This is useful for identifying workspaces based on user email domains.
    For example, searching for "motherduck.com" will find workspaces where users have
    @motherduck.com email addresses, which may belong to partner accounts.

    Args:
        email_domain: Email domain to search for (e.g., "motherduck.com", "fivetran.com").
            Do not include the "@" symbol.
        limit: Maximum number of results (default: 100)
        gsm_client: GCP Secret Manager client. If None, a new client will be instantiated.

    Returns:
        List of workspace records with organization_id, workspace_id, workspace_name,
        slug, email, dataplane_group_id, dataplane_name, and created_at.
        Results are ordered by organization_id and workspace_name.
    """
    # Strip leading @ if provided
    clean_domain = email_domain.lstrip("@")

    return _run_sql_query(
        SELECT_WORKSPACES_BY_EMAIL_DOMAIN,
        parameters={"email_domain": clean_domain, "limit": limit},
        query_name="SELECT_WORKSPACES_BY_EMAIL_DOMAIN",
        gsm_client=gsm_client,
    )
