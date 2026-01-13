# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
"""SQL query templates and schema documentation for Airbyte Cloud Prod DB Replica.

Prod DB Replica Schema Reference
================================

Database: prod-configapi
Instance: prod-ab-cloud-proj:us-west3:prod-pgsql-replica

connection
----------
id, namespace_definition, namespace_format, prefix, source_id, destination_id, name,
catalog, status, schedule, manual, resource_requirements, created_at, updated_at,
source_catalog_id, schedule_type, schedule_data, non_breaking_change_preference,
breaking_change, field_selection_data, destination_catalog_id, status_reason

actor
-----
id, workspace_id, actor_definition_id, name, configuration, actor_type, tombstone,
created_at, updated_at, resource_requirements

workspace
---------
id, customer_id, name, slug, email, initial_setup_complete, anonymous_data_collection,
send_newsletter, send_security_updates, display_setup_wizard, tombstone, notifications,
first_sync_complete, feedback_complete, created_at, updated_at, webhook_operation_configs,
notification_settings, organization_id, dataplane_group_id

dataplane_group
---------------
id, organization_id, name, enabled, created_at, updated_at, tombstone

Note: Main dataplane groups are:
- 645a183f-b12b-4c6e-8ad3-99e165603450 = US (default, ~133K workspaces)
- 153996d3-208e-4887-b8b1-e5fe48104450 = US-Central (~12K workspaces)
- b9e48d61-f082-4a14-a8d0-799a907938cb = EU (~3K workspaces)

actor_definition_version
------------------------
id, actor_definition_id, created_at, updated_at, documentation_url, docker_repository,
docker_image_tag, spec, protocol_version, release_date, normalization_repository,
normalization_tag, supports_dbt, normalization_integration_type, allowed_hosts,
suggested_streams, release_stage, support_state, support_level, supports_refreshes,
cdk_version, last_published, internal_support_level, language, supports_file_transfer,
supports_data_activation, connector_ipc_options

scoped_configuration
--------------------
id, key, resource_type, resource_id, scope_type, scope_id, value, description,
reference_url, origin_type, origin, expires_at, created_at, updated_at

Note: Version overrides are stored with key='connector_version', resource_type='actor_definition',
scope_type='actor', and value=actor_definition_version.id (UUID).

jobs
----
id, config_type, scope (connection_id), config, status, started_at, created_at,
updated_at, metadata, is_scheduled

Note: status values: 'succeeded', 'failed', 'cancelled', 'running', 'incomplete'
      config_type values: 'sync', 'reset_connection', 'refresh'

attempts
--------
id, job_id, attempt_number, log_path, output, status, created_at, updated_at,
ended_at, failure_summary, processing_task_queue, attempt_sync_config
"""

from __future__ import annotations

import sqlalchemy

# =============================================================================
# Connection Queries
# =============================================================================

# Query connections by connector type (no organization filter)
# Note: pg8000 cannot determine the type of NULL parameters in patterns like
# "(:param IS NULL OR column = :param)", so we use separate queries instead
SELECT_CONNECTIONS_BY_CONNECTOR = sqlalchemy.text(
    """
    SELECT
         connection.id AS connection_id,
         connection.name AS connection_name,
         connection.source_id,
         workspace.id AS workspace_id,
         workspace.name AS workspace_name,
         workspace.organization_id,
         workspace.dataplane_group_id,
         dataplane_group.name AS dataplane_name,
         source_actor.actor_definition_id AS source_definition_id,
         source_actor.name AS source_name
    FROM connection
    JOIN actor AS source_actor
      ON connection.source_id = source_actor.id
    JOIN workspace
      ON source_actor.workspace_id = workspace.id
    LEFT JOIN dataplane_group
      ON workspace.dataplane_group_id = dataplane_group.id
    WHERE
         source_actor.actor_definition_id = :connector_definition_id
    LIMIT :limit
    """
)

# Query connections by connector type, filtered by organization
SELECT_CONNECTIONS_BY_CONNECTOR_AND_ORG = sqlalchemy.text(
    """
    SELECT
         connection.id AS connection_id,
         connection.name AS connection_name,
         connection.source_id,
         workspace.id AS workspace_id,
         workspace.name AS workspace_name,
         workspace.organization_id,
         workspace.dataplane_group_id,
         dataplane_group.name AS dataplane_name,
         source_actor.actor_definition_id AS source_definition_id,
         source_actor.name AS source_name
    FROM connection
    JOIN actor AS source_actor
      ON connection.source_id = source_actor.id
    JOIN workspace
      ON source_actor.workspace_id = workspace.id
    LEFT JOIN dataplane_group
      ON workspace.dataplane_group_id = dataplane_group.id
    WHERE
         source_actor.actor_definition_id = :connector_definition_id
     AND workspace.organization_id = :organization_id
    LIMIT :limit
    """
)

# Query connections by DESTINATION connector type (no organization filter)
SELECT_CONNECTIONS_BY_DESTINATION_CONNECTOR = sqlalchemy.text(
    """
    SELECT
         connection.id AS connection_id,
         connection.name AS connection_name,
         connection.destination_id,
         workspace.id AS workspace_id,
         workspace.name AS workspace_name,
         workspace.organization_id,
         workspace.dataplane_group_id,
         dataplane_group.name AS dataplane_name,
         destination_actor.actor_definition_id AS destination_definition_id,
         destination_actor.name AS destination_name
    FROM connection
    JOIN actor AS destination_actor
      ON connection.destination_id = destination_actor.id
    JOIN workspace
      ON destination_actor.workspace_id = workspace.id
    LEFT JOIN dataplane_group
      ON workspace.dataplane_group_id = dataplane_group.id
    WHERE
         destination_actor.actor_definition_id = :connector_definition_id
    LIMIT :limit
    """
)

# Query connections by DESTINATION connector type, filtered by organization
SELECT_CONNECTIONS_BY_DESTINATION_CONNECTOR_AND_ORG = sqlalchemy.text(
    """
    SELECT
         connection.id AS connection_id,
         connection.name AS connection_name,
         connection.destination_id,
         workspace.id AS workspace_id,
         workspace.name AS workspace_name,
         workspace.organization_id,
         workspace.dataplane_group_id,
         dataplane_group.name AS dataplane_name,
         destination_actor.actor_definition_id AS destination_definition_id,
         destination_actor.name AS destination_name
    FROM connection
    JOIN actor AS destination_actor
      ON connection.destination_id = destination_actor.id
    JOIN workspace
      ON destination_actor.workspace_id = workspace.id
    LEFT JOIN dataplane_group
      ON workspace.dataplane_group_id = dataplane_group.id
    WHERE
         destination_actor.actor_definition_id = :connector_definition_id
     AND workspace.organization_id = :organization_id
    LIMIT :limit
    """
)

# =============================================================================
# Connector Version Queries
# =============================================================================

SELECT_CONNECTOR_VERSIONS = sqlalchemy.text(
    """
    SELECT
         actor_definition_version.id AS version_id,
         actor_definition_version.docker_image_tag,
         actor_definition_version.docker_repository,
         actor_definition_version.release_stage,
         actor_definition_version.support_level,
         actor_definition_version.cdk_version,
         actor_definition_version.language,
         actor_definition_version.last_published,
         actor_definition_version.release_date
    FROM actor_definition_version
    WHERE
         actor_definition_version.actor_definition_id = :actor_definition_id
    ORDER BY
         actor_definition_version.last_published DESC NULLS LAST,
         actor_definition_version.created_at DESC
    """
)

# List new connector releases within the last N days
# Uses last_published (timestamp) rather than release_date (date only, often NULL)
# Note: No index on last_published, but table is small (~39K rows)
SELECT_NEW_CONNECTOR_RELEASES = sqlalchemy.text(
    """
    SELECT
         actor_definition_version.id AS version_id,
         actor_definition_version.actor_definition_id,
         actor_definition_version.docker_repository,
         actor_definition_version.docker_image_tag,
         actor_definition_version.last_published,
         actor_definition_version.release_date,
         actor_definition_version.release_stage,
         actor_definition_version.support_level,
         actor_definition_version.cdk_version,
         actor_definition_version.language,
         actor_definition_version.created_at
    FROM actor_definition_version
    WHERE
         actor_definition_version.last_published >= :cutoff_date
    ORDER BY
         actor_definition_version.last_published DESC
    LIMIT :limit
    """
)

SELECT_ACTORS_PINNED_TO_VERSION = sqlalchemy.text(
    """
    SELECT
         scoped_configuration.scope_id AS actor_id,
         scoped_configuration.resource_id AS actor_definition_id,
         scoped_configuration.origin_type,
         scoped_configuration.origin,
         scoped_configuration.description,
         scoped_configuration.created_at,
         scoped_configuration.expires_at,
         actor.name AS actor_name,
         actor.workspace_id,
         workspace.name AS workspace_name,
         workspace.organization_id,
         workspace.dataplane_group_id,
         dataplane_group.name AS dataplane_name
    FROM scoped_configuration
    JOIN actor
      ON scoped_configuration.scope_id = actor.id
    JOIN workspace
      ON actor.workspace_id = workspace.id
    LEFT JOIN dataplane_group
      ON workspace.dataplane_group_id = dataplane_group.id
    WHERE
         scoped_configuration.key = 'connector_version'
     AND scoped_configuration.scope_type = 'actor'
     AND scoped_configuration.value = :actor_definition_version_id
    ORDER BY
         scoped_configuration.created_at DESC
    """
)

# =============================================================================
# Sync Results Queries
# =============================================================================

# Get sync results for actors pinned to a specific connector definition VERSION ID
# This joins through scoped_configuration to find actors with version overrides
SELECT_SYNC_RESULTS_FOR_VERSION = sqlalchemy.text(
    """
    SELECT
         jobs.id AS job_id,
         jobs.scope AS connection_id,
         jobs.status AS job_status,
         jobs.started_at,
         jobs.updated_at AS job_updated_at,
         connection.name AS connection_name,
         actor.id AS actor_id,
         actor.name AS actor_name,
         actor.actor_definition_id,
         scoped_configuration.origin_type AS pin_origin_type,
         scoped_configuration.origin AS pin_origin,
         workspace.id AS workspace_id,
         workspace.name AS workspace_name,
         workspace.organization_id,
         workspace.dataplane_group_id,
         dataplane_group.name AS dataplane_name
    FROM jobs
    JOIN connection
      ON jobs.scope = connection.id::text
    JOIN actor
      ON connection.source_id = actor.id
    JOIN scoped_configuration
      ON scoped_configuration.scope_id = actor.id
     AND scoped_configuration.key = 'connector_version'
     AND scoped_configuration.scope_type = 'actor'
    JOIN workspace
      ON actor.workspace_id = workspace.id
    LEFT JOIN dataplane_group
      ON workspace.dataplane_group_id = dataplane_group.id
    WHERE
         jobs.config_type = 'sync'
     AND scoped_configuration.value = :actor_definition_version_id
     AND jobs.updated_at >= :cutoff_date
    ORDER BY
         jobs.updated_at DESC
    LIMIT :limit
    """
)

# Get successful sync results for actors pinned to a specific connector definition VERSION ID
SELECT_SUCCESSFUL_SYNCS_FOR_VERSION = sqlalchemy.text(
    """
    SELECT
         jobs.id AS job_id,
         jobs.scope AS connection_id,
         jobs.started_at,
         jobs.updated_at AS job_updated_at,
         connection.name AS connection_name,
         actor.id AS actor_id,
         actor.name AS actor_name,
         actor.actor_definition_id,
         scoped_configuration.origin_type AS pin_origin_type,
         scoped_configuration.origin AS pin_origin,
         workspace.id AS workspace_id,
         workspace.name AS workspace_name,
         workspace.organization_id,
         workspace.dataplane_group_id,
         dataplane_group.name AS dataplane_name
    FROM jobs
    JOIN connection
      ON jobs.scope = connection.id::text
    JOIN actor
      ON connection.source_id = actor.id
    JOIN scoped_configuration
      ON scoped_configuration.scope_id = actor.id
     AND scoped_configuration.key = 'connector_version'
     AND scoped_configuration.scope_type = 'actor'
    JOIN workspace
      ON actor.workspace_id = workspace.id
    LEFT JOIN dataplane_group
      ON workspace.dataplane_group_id = dataplane_group.id
    WHERE
         jobs.config_type = 'sync'
     AND jobs.status = 'succeeded'
     AND scoped_configuration.value = :actor_definition_version_id
     AND jobs.updated_at >= :cutoff_date
    ORDER BY
         jobs.updated_at DESC
    LIMIT :limit
    """
)

# Get recent sync results for ALL actors using a SOURCE connector definition.
# Finds all actors with the given actor_definition_id and returns their sync attempts,
# regardless of whether they have explicit version pins.
# Query starts from jobs table to leverage indexed columns.
# The LEFT JOIN to scoped_configuration provides pin context when available (pin_origin_type,
# pin_origin, pinned_version_id will be NULL for unpinned actors).
# Status filtering ('all', 'succeeded', 'failed') is handled at the application layer by
# selecting among different SQL query constants; this query returns all statuses.
SELECT_RECENT_SYNCS_FOR_SOURCE_CONNECTOR = sqlalchemy.text(
    """
    SELECT
         jobs.id AS job_id,
         jobs.scope AS connection_id,
         jobs.status AS job_status,
         jobs.started_at AS job_started_at,
         jobs.updated_at AS job_updated_at,
         connection.name AS connection_name,
         actor.id AS actor_id,
         actor.name AS actor_name,
         actor.actor_definition_id,
         actor.tombstone AS actor_tombstone,
         workspace.id AS workspace_id,
         workspace.name AS workspace_name,
         workspace.organization_id,
         workspace.dataplane_group_id,
         dataplane_group.name AS dataplane_name,
         scoped_configuration.origin_type AS pin_origin_type,
         scoped_configuration.origin AS pin_origin,
         scoped_configuration.value AS pinned_version_id
    FROM jobs
    JOIN connection
      ON jobs.scope = connection.id::text
     AND connection.status != 'deprecated'
    JOIN actor
      ON connection.source_id = actor.id
     AND actor.actor_definition_id = :connector_definition_id
     AND actor.tombstone = false
    JOIN workspace
      ON actor.workspace_id = workspace.id
     AND workspace.tombstone = false
    LEFT JOIN dataplane_group
      ON workspace.dataplane_group_id = dataplane_group.id
    LEFT JOIN scoped_configuration
      ON scoped_configuration.scope_id = actor.id
     AND scoped_configuration.key = 'connector_version'
     AND scoped_configuration.scope_type = 'actor'
    WHERE
         jobs.config_type = 'sync'
     AND jobs.updated_at >= :cutoff_date
    ORDER BY
         jobs.updated_at DESC
    LIMIT :limit
    """
)

# Same as above but filtered to only successful syncs
SELECT_RECENT_SUCCESSFUL_SYNCS_FOR_SOURCE_CONNECTOR = sqlalchemy.text(
    """
    SELECT
         jobs.id AS job_id,
         jobs.scope AS connection_id,
         jobs.status AS job_status,
         jobs.started_at AS job_started_at,
         jobs.updated_at AS job_updated_at,
         connection.name AS connection_name,
         actor.id AS actor_id,
         actor.name AS actor_name,
         actor.actor_definition_id,
         actor.tombstone AS actor_tombstone,
         workspace.id AS workspace_id,
         workspace.name AS workspace_name,
         workspace.organization_id,
         workspace.dataplane_group_id,
         dataplane_group.name AS dataplane_name,
         scoped_configuration.origin_type AS pin_origin_type,
         scoped_configuration.origin AS pin_origin,
         scoped_configuration.value AS pinned_version_id
    FROM jobs
    JOIN connection
      ON jobs.scope = connection.id::text
     AND connection.status != 'deprecated'
    JOIN actor
      ON connection.source_id = actor.id
     AND actor.actor_definition_id = :connector_definition_id
     AND actor.tombstone = false
    JOIN workspace
      ON actor.workspace_id = workspace.id
     AND workspace.tombstone = false
    LEFT JOIN dataplane_group
      ON workspace.dataplane_group_id = dataplane_group.id
    LEFT JOIN scoped_configuration
      ON scoped_configuration.scope_id = actor.id
     AND scoped_configuration.key = 'connector_version'
     AND scoped_configuration.scope_type = 'actor'
    WHERE
         jobs.config_type = 'sync'
     AND jobs.status = 'succeeded'
     AND jobs.updated_at >= :cutoff_date
    ORDER BY
         jobs.updated_at DESC
    LIMIT :limit
    """
)

# Same as above but filtered to only failed syncs
SELECT_RECENT_FAILED_SYNCS_FOR_SOURCE_CONNECTOR = sqlalchemy.text(
    """
    SELECT
         jobs.id AS job_id,
         jobs.scope AS connection_id,
         jobs.status AS job_status,
         jobs.started_at AS job_started_at,
         jobs.updated_at AS job_updated_at,
         connection.name AS connection_name,
         actor.id AS actor_id,
         actor.name AS actor_name,
         actor.actor_definition_id,
         actor.tombstone AS actor_tombstone,
         workspace.id AS workspace_id,
         workspace.name AS workspace_name,
         workspace.organization_id,
         workspace.dataplane_group_id,
         dataplane_group.name AS dataplane_name,
         scoped_configuration.origin_type AS pin_origin_type,
         scoped_configuration.origin AS pin_origin,
         scoped_configuration.value AS pinned_version_id
    FROM jobs
    JOIN connection
      ON jobs.scope = connection.id::text
     AND connection.status != 'deprecated'
    JOIN actor
      ON connection.source_id = actor.id
     AND actor.actor_definition_id = :connector_definition_id
     AND actor.tombstone = false
    JOIN workspace
      ON actor.workspace_id = workspace.id
     AND workspace.tombstone = false
    LEFT JOIN dataplane_group
      ON workspace.dataplane_group_id = dataplane_group.id
    LEFT JOIN scoped_configuration
      ON scoped_configuration.scope_id = actor.id
     AND scoped_configuration.key = 'connector_version'
     AND scoped_configuration.scope_type = 'actor'
    WHERE
         jobs.config_type = 'sync'
     AND jobs.status = 'failed'
     AND jobs.updated_at >= :cutoff_date
    ORDER BY
         jobs.updated_at DESC
    LIMIT :limit
    """
)

# Get recent sync results for ALL actors using a DESTINATION connector definition.
SELECT_RECENT_SYNCS_FOR_DESTINATION_CONNECTOR = sqlalchemy.text(
    """
    SELECT
         jobs.id AS job_id,
         jobs.scope AS connection_id,
         jobs.status AS job_status,
         jobs.started_at AS job_started_at,
         jobs.updated_at AS job_updated_at,
         connection.name AS connection_name,
         actor.id AS actor_id,
         actor.name AS actor_name,
         actor.actor_definition_id,
         actor.tombstone AS actor_tombstone,
         workspace.id AS workspace_id,
         workspace.name AS workspace_name,
         workspace.organization_id,
         workspace.dataplane_group_id,
         dataplane_group.name AS dataplane_name,
         scoped_configuration.origin_type AS pin_origin_type,
         scoped_configuration.origin AS pin_origin,
         scoped_configuration.value AS pinned_version_id
    FROM jobs
    JOIN connection
      ON jobs.scope = connection.id::text
     AND connection.status != 'deprecated'
    JOIN actor
      ON connection.destination_id = actor.id
     AND actor.actor_definition_id = :connector_definition_id
     AND actor.tombstone = false
    JOIN workspace
      ON actor.workspace_id = workspace.id
     AND workspace.tombstone = false
    LEFT JOIN dataplane_group
      ON workspace.dataplane_group_id = dataplane_group.id
    LEFT JOIN scoped_configuration
      ON scoped_configuration.scope_id = actor.id
     AND scoped_configuration.key = 'connector_version'
     AND scoped_configuration.scope_type = 'actor'
    WHERE
         jobs.config_type = 'sync'
     AND jobs.updated_at >= :cutoff_date
    ORDER BY
         jobs.updated_at DESC
    LIMIT :limit
    """
)

# Same as above but filtered to only successful syncs
SELECT_RECENT_SUCCESSFUL_SYNCS_FOR_DESTINATION_CONNECTOR = sqlalchemy.text(
    """
    SELECT
         jobs.id AS job_id,
         jobs.scope AS connection_id,
         jobs.status AS job_status,
         jobs.started_at AS job_started_at,
         jobs.updated_at AS job_updated_at,
         connection.name AS connection_name,
         actor.id AS actor_id,
         actor.name AS actor_name,
         actor.actor_definition_id,
         actor.tombstone AS actor_tombstone,
         workspace.id AS workspace_id,
         workspace.name AS workspace_name,
         workspace.organization_id,
         workspace.dataplane_group_id,
         dataplane_group.name AS dataplane_name,
         scoped_configuration.origin_type AS pin_origin_type,
         scoped_configuration.origin AS pin_origin,
         scoped_configuration.value AS pinned_version_id
    FROM jobs
    JOIN connection
      ON jobs.scope = connection.id::text
     AND connection.status != 'deprecated'
    JOIN actor
      ON connection.destination_id = actor.id
     AND actor.actor_definition_id = :connector_definition_id
     AND actor.tombstone = false
    JOIN workspace
      ON actor.workspace_id = workspace.id
     AND workspace.tombstone = false
    LEFT JOIN dataplane_group
      ON workspace.dataplane_group_id = dataplane_group.id
    LEFT JOIN scoped_configuration
      ON scoped_configuration.scope_id = actor.id
     AND scoped_configuration.key = 'connector_version'
     AND scoped_configuration.scope_type = 'actor'
    WHERE
         jobs.config_type = 'sync'
     AND jobs.status = 'succeeded'
     AND jobs.updated_at >= :cutoff_date
    ORDER BY
         jobs.updated_at DESC
    LIMIT :limit
    """
)

# Same as above but filtered to only failed syncs
SELECT_RECENT_FAILED_SYNCS_FOR_DESTINATION_CONNECTOR = sqlalchemy.text(
    """
    SELECT
         jobs.id AS job_id,
         jobs.scope AS connection_id,
         jobs.status AS job_status,
         jobs.started_at AS job_started_at,
         jobs.updated_at AS job_updated_at,
         connection.name AS connection_name,
         actor.id AS actor_id,
         actor.name AS actor_name,
         actor.actor_definition_id,
         actor.tombstone AS actor_tombstone,
         workspace.id AS workspace_id,
         workspace.name AS workspace_name,
         workspace.organization_id,
         workspace.dataplane_group_id,
         dataplane_group.name AS dataplane_name,
         scoped_configuration.origin_type AS pin_origin_type,
         scoped_configuration.origin AS pin_origin,
         scoped_configuration.value AS pinned_version_id
    FROM jobs
    JOIN connection
      ON jobs.scope = connection.id::text
     AND connection.status != 'deprecated'
    JOIN actor
      ON connection.destination_id = actor.id
     AND actor.actor_definition_id = :connector_definition_id
     AND actor.tombstone = false
    JOIN workspace
      ON actor.workspace_id = workspace.id
     AND workspace.tombstone = false
    LEFT JOIN dataplane_group
      ON workspace.dataplane_group_id = dataplane_group.id
    LEFT JOIN scoped_configuration
      ON scoped_configuration.scope_id = actor.id
     AND scoped_configuration.key = 'connector_version'
     AND scoped_configuration.scope_type = 'actor'
    WHERE
         jobs.config_type = 'sync'
     AND jobs.status = 'failed'
     AND jobs.updated_at >= :cutoff_date
    ORDER BY
         jobs.updated_at DESC
    LIMIT :limit
    """
)

# Get failed attempt results for ALL actors using a connector definition.
# Finds all actors with the given actor_definition_id and returns their failed sync attempts,
# regardless of whether they have explicit version pins.
# Query starts from attempts table to leverage indexed columns (ended_at, status).
# Note: This query only supports SOURCE connectors (joins via connection.source_id).
# The LEFT JOIN to scoped_configuration provides pin context when available (pin_origin_type,
# pin_origin, pinned_version_id will be NULL for unpinned actors).
SELECT_FAILED_SYNC_ATTEMPTS_FOR_CONNECTOR = sqlalchemy.text(
    """
    SELECT
         jobs.id AS job_id,
         jobs.scope AS connection_id,
         jobs.status AS latest_job_status,
         jobs.started_at AS job_started_at,
         jobs.updated_at AS job_updated_at,
         connection.name AS connection_name,
         actor.id AS actor_id,
         actor.name AS actor_name,
         actor.actor_definition_id,
         workspace.id AS workspace_id,
         workspace.name AS workspace_name,
         workspace.organization_id,
         workspace.dataplane_group_id,
         dataplane_group.name AS dataplane_name,
         scoped_configuration.origin_type AS pin_origin_type,
         scoped_configuration.origin AS pin_origin,
         scoped_configuration.value AS pinned_version_id,
         attempts.id AS failed_attempt_id,
         attempts.attempt_number AS failed_attempt_number,
         attempts.status AS failed_attempt_status,
         attempts.created_at AS failed_attempt_created_at,
         attempts.ended_at AS failed_attempt_ended_at,
         attempts.failure_summary,
         attempts.processing_task_queue
    FROM attempts
    JOIN jobs
      ON jobs.id = attempts.job_id
     AND jobs.config_type = 'sync'
     AND jobs.updated_at >= :cutoff_date
    JOIN connection
      ON jobs.scope = connection.id::text
    JOIN actor
      ON connection.source_id = actor.id
     AND actor.actor_definition_id = :connector_definition_id
    JOIN workspace
      ON actor.workspace_id = workspace.id
    LEFT JOIN dataplane_group
      ON workspace.dataplane_group_id = dataplane_group.id
    LEFT JOIN scoped_configuration
      ON scoped_configuration.scope_id = actor.id
     AND scoped_configuration.key = 'connector_version'
     AND scoped_configuration.scope_type = 'actor'
    WHERE
         attempts.ended_at >= :cutoff_date
     AND attempts.status = 'failed'
    ORDER BY
         attempts.ended_at DESC
    LIMIT :limit
    """
)

# =============================================================================
# Dataplane and Workspace Queries
# =============================================================================

# List all dataplane groups with workspace counts
SELECT_DATAPLANES_LIST = sqlalchemy.text(
    """
    SELECT
         dataplane_group.id AS dataplane_group_id,
         dataplane_group.name AS dataplane_name,
         dataplane_group.organization_id,
         dataplane_group.enabled,
         dataplane_group.tombstone,
         dataplane_group.created_at,
         COUNT(workspace.id) AS workspace_count
    FROM dataplane_group
    LEFT JOIN workspace
      ON workspace.dataplane_group_id = dataplane_group.id
     AND workspace.tombstone = false
    WHERE
         dataplane_group.tombstone = false
    GROUP BY
         dataplane_group.id,
         dataplane_group.name,
         dataplane_group.organization_id,
         dataplane_group.enabled,
         dataplane_group.tombstone,
         dataplane_group.created_at
    ORDER BY
         workspace_count DESC
    """
)

# Get workspace info including dataplane group for EU filtering
SELECT_WORKSPACE_INFO = sqlalchemy.text(
    """
    SELECT
         workspace.id AS workspace_id,
         workspace.name AS workspace_name,
         workspace.slug,
         workspace.organization_id,
         workspace.dataplane_group_id,
         dataplane_group.name AS dataplane_name,
         workspace.created_at,
         workspace.tombstone
    FROM workspace
    LEFT JOIN dataplane_group
      ON workspace.dataplane_group_id = dataplane_group.id
    WHERE
         workspace.id = :workspace_id
    """
)

# Get all workspaces in an organization with dataplane info
SELECT_ORG_WORKSPACES = sqlalchemy.text(
    """
    SELECT
         workspace.id AS workspace_id,
         workspace.name AS workspace_name,
         workspace.slug,
         workspace.organization_id,
         workspace.dataplane_group_id,
         dataplane_group.name AS dataplane_name,
         workspace.created_at,
         workspace.tombstone
    FROM workspace
    LEFT JOIN dataplane_group
      ON workspace.dataplane_group_id = dataplane_group.id
    WHERE
         workspace.organization_id = :organization_id
     AND workspace.tombstone = false
    ORDER BY
         workspace.name
    """
)

# =============================================================================
# Workspace Lookup by Email Domain
# =============================================================================

# Find workspaces by email domain
# This is useful for identifying workspaces based on user email domains
# (e.g., finding partner accounts like MotherDuck by searching for "motherduck.com")
SELECT_WORKSPACES_BY_EMAIL_DOMAIN = sqlalchemy.text(
    """
    SELECT DISTINCT
         workspace.organization_id,
         workspace.id AS workspace_id,
         workspace.name AS workspace_name,
         workspace.slug,
         workspace.email,
         workspace.dataplane_group_id,
         dataplane_group.name AS dataplane_name,
         workspace.created_at
    FROM workspace
    LEFT JOIN dataplane_group
      ON workspace.dataplane_group_id = dataplane_group.id
    WHERE
         workspace.email LIKE '%@' || :email_domain
     AND workspace.tombstone = false
    ORDER BY
         workspace.organization_id,
         workspace.name
    LIMIT :limit
    """
)
