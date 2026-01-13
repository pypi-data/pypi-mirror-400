# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
"""Low-level API client for Airbyte Cloud operations.

This module provides direct HTTP access to Airbyte Cloud APIs that are not
yet available in PyAirbyte. This is vendored functionality from PyAirbyte PR #838.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Literal

import requests
from airbyte import constants
from airbyte.exceptions import PyAirbyteInputError

from airbyte_ops_mcp import constants as ops_constants

# Internal enums for scoped configuration API "magic strings"
# These values caused issues during development and are now centralized here


class _ScopedConfigKey(str, Enum):
    """Configuration keys used in scoped configuration API.

    Valid values from airbyte-platform-internal:
    oss/airbyte-data/src/main/kotlin/io/airbyte/data/services/shared/ScopedConfigurationKey.kt
    """

    CONNECTOR_VERSION = "connector_version"
    NETWORK_SECURITY_TOKEN = "network_security_token"
    PRODUCT_LIMITS = "product_limits"


class _ResourceType(str, Enum):
    """Resource types for scoped configuration.

    Valid values from airbyte-platform-internal:
    oss/airbyte-config/config-models/src/generated/java/io/airbyte/config/ConfigResourceType.java
    """

    ACTOR_DEFINITION = "actor_definition"
    USER = "user"
    WORKSPACE = "workspace"
    ORGANIZATION = "organization"
    CONNECTION = "connection"
    SOURCE = "source"
    DESTINATION = "destination"


class _ScopeType(str, Enum):
    """Scope types for scoped configuration.

    Valid values from airbyte-platform-internal:
    oss/airbyte-config/config-models/src/generated/java/io/airbyte/config/ConfigScopeType.java
    """

    ORGANIZATION = "organization"
    WORKSPACE = "workspace"
    ACTOR = "actor"


class _OriginType(str, Enum):
    """Origin types for scoped configuration.

    Valid values from airbyte-platform-internal:
    oss/airbyte-config/config-models/src/generated/java/io/airbyte/config/ConfigOriginType.java
    """

    USER = "user"
    BREAKING_CHANGE = "breaking_change"
    CONNECTOR_ROLLOUT = "connector_rollout"


def _get_access_token(
    client_id: str | None = None,
    client_secret: str | None = None,
    bearer_token: str | None = None,
) -> str:
    """Get an access token for Airbyte Cloud API.

    If a bearer_token is provided, it is returned directly (already an access token).
    Otherwise, exchanges client_id/client_secret for an access token.

    Args:
        client_id: The Airbyte Cloud client ID (required if no bearer_token)
        client_secret: The Airbyte Cloud client secret (required if no bearer_token)
        bearer_token: Pre-existing bearer token (takes precedence over client credentials)

    Returns:
        Access token string

    Raises:
        PyAirbyteInputError: If authentication fails or no valid credentials provided
    """
    # If bearer token provided, use it directly
    if bearer_token:
        return bearer_token

    # Otherwise, exchange client credentials for access token
    if not client_id or not client_secret:
        raise PyAirbyteInputError(
            message="Either bearer_token or both client_id and client_secret must be provided",
        )

    # Always authenticate via the public API endpoint
    auth_url = f"{constants.CLOUD_API_ROOT}/applications/token"
    response = requests.post(
        auth_url,
        json={
            "client_id": client_id,
            "client_secret": client_secret,
        },
        timeout=30,
    )

    if response.status_code != 200:
        raise PyAirbyteInputError(
            message=f"Failed to authenticate with Airbyte Cloud: {response.status_code} {response.text}",
            context={
                "status_code": response.status_code,
                "response": response.text,
            },
        )

    data = response.json()
    return data["access_token"]


def get_user_id_by_email(
    email: str,
    api_root: str,
    client_id: str | None = None,
    client_secret: str | None = None,
    bearer_token: str | None = None,
) -> str:
    """Get user ID from email address.

    Args:
        email: The user's email address
        api_root: The API root URL
        client_id: The Airbyte Cloud client ID (required if no bearer_token)
        client_secret: The Airbyte Cloud client secret (required if no bearer_token)
        bearer_token: Pre-existing bearer token (takes precedence over client credentials)

    Returns:
        User ID (UUID string)

    Raises:
        PyAirbyteInputError: If user not found or API request fails
    """
    access_token = _get_access_token(client_id, client_secret, bearer_token)

    endpoint = f"{api_root}/users/list_instance_admin"
    response = requests.post(
        endpoint,
        json={},
        headers={
            "Authorization": f"Bearer {access_token}",
            "User-Agent": ops_constants.USER_AGENT,
            "Content-Type": "application/json",
        },
        timeout=30,
    )

    if response.status_code != 200:
        raise PyAirbyteInputError(
            message=f"Failed to list users: {response.status_code} {response.text}",
            context={
                "endpoint": endpoint,
                "status_code": response.status_code,
                "response": response.text,
            },
        )

    data = response.json()
    users = data.get("users", [])

    for user in users:
        if user.get("email") == email:
            return user["userId"]

    raise PyAirbyteInputError(
        message=f"No user found with email: {email}",
        context={
            "email": email,
            "available_users": len(users),
        },
    )


def resolve_connector_version_id(
    actor_definition_id: str,
    connector_type: Literal["source", "destination"],
    version: str,
    api_root: str,
    client_id: str | None = None,
    client_secret: str | None = None,
    bearer_token: str | None = None,
) -> str:
    """Resolve a version string to an actor_definition_version_id.

    Args:
        actor_definition_id: The actor definition ID
        connector_type: Either "source" or "destination"
        version: The version string (e.g., "0.1.47-preview.abe7cb4")
        api_root: The API root URL
        client_id: The Airbyte Cloud client ID (required if no bearer_token)
        client_secret: The Airbyte Cloud client secret (required if no bearer_token)
        bearer_token: Pre-existing bearer token (takes precedence over client credentials)

    Returns:
        Version ID (UUID string)

    Raises:
        PyAirbyteInputError: If version cannot be resolved or API request fails
    """
    access_token = _get_access_token(client_id, client_secret, bearer_token)

    endpoint = f"{api_root}/actor_definition_versions/resolve"
    payload = {
        "actorDefinitionId": actor_definition_id,
        "actorType": connector_type,
        "dockerImageTag": version,
    }

    response = requests.post(
        endpoint,
        json=payload,
        headers={
            "Authorization": f"Bearer {access_token}",
            "User-Agent": ops_constants.USER_AGENT,
            "Content-Type": "application/json",
        },
        timeout=30,
    )

    if response.status_code != 200:
        raise PyAirbyteInputError(
            message=f"Failed to resolve version: {response.status_code} {response.text}",
            context={
                "endpoint": endpoint,
                "payload": payload,
                "status_code": response.status_code,
                "response": response.text,
            },
        )

    data = response.json()
    version_id = data.get("versionId")

    if not version_id:
        raise PyAirbyteInputError(
            message=f"Could not resolve version '{version}' for connector",
            context={
                "actor_definition_id": actor_definition_id,
                "connector_type": connector_type,
                "version": version,
                "response": data,
            },
        )

    return version_id


def _get_scoped_configuration_context(
    actor_definition_id: str,
    scope_type: _ScopeType,
    scope_id: str,
    api_root: str,
    access_token: str,
) -> dict[str, Any] | None:
    """Get the active scoped configuration for a single scope level.

    This is the canonical way to query /scoped_configuration/get_context.
    Used by both the unset path and the multi-scope checking in the set path.

    Args:
        actor_definition_id: The actor definition ID for the connector
        scope_type: The scope type enum (ACTOR, WORKSPACE, or ORGANIZATION)
        scope_id: The ID for the scope (connector_id, workspace_id, or organization_id)
        api_root: The API root URL
        access_token: Pre-authenticated access token

    Returns:
        The active configuration dict if an override exists at this scope, or None.

    Raises:
        PyAirbyteInputError: If the API request fails
    """
    endpoint = f"{api_root}/scoped_configuration/get_context"
    context_payload = {
        "config_key": _ScopedConfigKey.CONNECTOR_VERSION.value,
        "resource_type": _ResourceType.ACTOR_DEFINITION.value,
        "resource_id": actor_definition_id,
        "scope_type": scope_type.value,
        "scope_id": scope_id,
    }

    response = requests.post(
        endpoint,
        json=context_payload,
        headers={
            "Authorization": f"Bearer {access_token}",
            "User-Agent": ops_constants.USER_AGENT,
            "Content-Type": "application/json",
        },
        timeout=30,
    )

    if response.status_code != 200:
        raise PyAirbyteInputError(
            message=f"Failed to get scoped configuration context for {scope_type.value} scope: "
            f"{response.status_code} {response.text}",
            context={
                "endpoint": endpoint,
                "payload": context_payload,
                "scope_type": scope_type.value,
                "status_code": response.status_code,
                "response": response.text,
            },
        )

    context_data = response.json()
    return context_data.get("activeConfiguration")


def get_all_scoped_configuration_contexts(
    connector_id: str,
    actor_definition_id: str,
    workspace_id: str,
    organization_id: str,
    api_root: str,
    client_id: str | None = None,
    client_secret: str | None = None,
    bearer_token: str | None = None,
) -> dict[str, dict[str, Any]]:
    """Get version override configurations at all scope levels (actor, workspace, organization).

    This ALWAYS checks all three scope levels to provide a complete picture of any version
    overrides that may affect the connector. All scope IDs are required to ensure comprehensive
    checking - this function will not silently skip any scope.

    Args:
        connector_id: The ID of the deployed connector (source or destination)
        actor_definition_id: The actor definition ID for the connector
        workspace_id: The workspace ID (required - must always check workspace scope)
        organization_id: The organization ID (required - must always check org scope)
        api_root: The API root URL
        client_id: The Airbyte Cloud client ID (required if no bearer_token)
        client_secret: The Airbyte Cloud client secret (required if no bearer_token)
        bearer_token: Pre-existing bearer token (takes precedence over client credentials)

    Returns:
        Dictionary containing only the scopes that have active configurations.
        Empty dict if no overrides exist (falsy). Keys are 'actor', 'workspace',
        'organization' - only present if an override exists at that scope.

    Raises:
        PyAirbyteInputError: If any API request fails
    """
    access_token = _get_access_token(client_id, client_secret, bearer_token)

    # Start with empty dict - only add entries for scopes that have active configs
    # This ensures the result is falsy if nothing is set
    results: dict[str, dict[str, Any]] = {}

    # Always check all three scopes - no optional skipping
    # Using enum values consistently to avoid magic strings
    scopes_to_check: list[tuple[_ScopeType, str]] = [
        (_ScopeType.ACTOR, connector_id),
        (_ScopeType.WORKSPACE, workspace_id),
        (_ScopeType.ORGANIZATION, organization_id),
    ]

    for scope_type_enum, scope_id in scopes_to_check:
        active_config = _get_scoped_configuration_context(
            actor_definition_id=actor_definition_id,
            scope_type=scope_type_enum,
            scope_id=scope_id,
            api_root=api_root,
            access_token=access_token,
        )
        if active_config:
            results[scope_type_enum.value] = active_config

    return results


def get_connector_version(
    connector_id: str,
    connector_type: Literal["source", "destination"],
    api_root: str,
    client_id: str | None = None,
    client_secret: str | None = None,
    bearer_token: str | None = None,
    workspace_id: str | None = None,
) -> dict[str, Any]:
    """Get version information for a deployed connector.

    This function retrieves the current version and override status. If workspace_id is provided,
    it also fetches detailed scoped configuration context at all scope levels (actor, workspace,
    organization) to provide a complete picture of any version pins.

    Args:
        connector_id: The ID of the deployed connector (source or destination)
        connector_type: Either "source" or "destination"
        api_root: The API root URL
        client_id: The Airbyte Cloud client ID (required if no bearer_token)
        client_secret: The Airbyte Cloud client secret (required if no bearer_token)
        bearer_token: Pre-existing bearer token (takes precedence over client credentials)
        workspace_id: Optional workspace ID to enable detailed scope checking

    Returns:
        Dictionary containing:
        - dockerImageTag: The current version string
        - isVersionOverrideApplied: Boolean indicating if override is active
        - scopedConfigs: (if workspace_id provided) Dict with 'actor', 'workspace', 'organization'
          keys containing the active configuration at each scope level, or None

    Raises:
        PyAirbyteInputError: If the API request fails
    """
    access_token = _get_access_token(client_id, client_secret, bearer_token)

    # Determine endpoint based on connector type
    # api_root already includes /v1
    if connector_type == "source":
        endpoint = f"{api_root}/actor_definition_versions/get_for_source"
        payload = {"sourceId": connector_id}
        definition_id_key = "sourceDefinitionId"
    else:
        endpoint = f"{api_root}/actor_definition_versions/get_for_destination"
        payload = {"destinationId": connector_id}
        definition_id_key = "destinationDefinitionId"

    response = requests.post(
        endpoint,
        json=payload,
        headers={
            "Authorization": f"Bearer {access_token}",
            "User-Agent": ops_constants.USER_AGENT,
            "Content-Type": "application/json",
        },
        timeout=30,
    )

    if response.status_code != 200:
        raise PyAirbyteInputError(
            message=f"Failed to get connector version: {response.status_code} {response.text}",
            context={
                "connector_id": connector_id,
                "connector_type": connector_type,
                "endpoint": endpoint,
                "payload": payload,
                "api_root": api_root,
                "status_code": response.status_code,
                "response": response.text,
            },
        )

    data = response.json()

    result: dict[str, Any] = {
        "dockerImageTag": data.get("dockerImageTag", "unknown"),
        "isVersionOverrideApplied": data.get(
            "isVersionOverrideApplied", data.get("isOverrideApplied", False)
        ),
    }

    # If workspace_id is provided, also get detailed scoped configuration context
    if workspace_id:
        # Get actor_definition_id from the connector info
        get_endpoint = f"{api_root}/{connector_type}s/get"
        get_payload: dict[str, str] = {f"{connector_type}Id": connector_id}

        get_response = requests.post(
            get_endpoint,
            json=get_payload,
            headers={
                "Authorization": f"Bearer {access_token}",
                "User-Agent": ops_constants.USER_AGENT,
                "Content-Type": "application/json",
            },
            timeout=30,
        )

        if get_response.status_code == 200:
            connector_info = get_response.json()
            actor_definition_id = connector_info.get(definition_id_key)

            if actor_definition_id:
                # Get organization_id from workspace
                workspace_endpoint = f"{api_root}/workspaces/get"
                workspace_response = requests.post(
                    workspace_endpoint,
                    json={"workspaceId": workspace_id},
                    headers={
                        "Authorization": f"Bearer {access_token}",
                        "User-Agent": ops_constants.USER_AGENT,
                        "Content-Type": "application/json",
                    },
                    timeout=30,
                )

                organization_id = None
                if workspace_response.status_code == 200:
                    workspace_data = workspace_response.json()
                    organization_id = workspace_data.get("organizationId")

                if organization_id:
                    result["scopedConfigs"] = get_all_scoped_configuration_contexts(
                        connector_id=connector_id,
                        actor_definition_id=actor_definition_id,
                        workspace_id=workspace_id,
                        organization_id=organization_id,
                        api_root=api_root,
                        bearer_token=access_token,
                    )

    return result


def set_connector_version_override(
    connector_id: str,
    connector_type: Literal["source", "destination"],
    api_root: str,
    client_id: str | None = None,
    client_secret: str | None = None,
    workspace_id: str | None = None,
    version: str | None = None,
    unset: bool = False,
    override_reason: str | None = None,
    override_reason_reference_url: str | None = None,
    user_email: str | None = None,
    bearer_token: str | None = None,
) -> bool:
    """Set or clear a version override for a deployed connector.

    This function checks all three scope levels (actor, workspace, organization) before
    creating a new override to prevent duplicate key constraint violations. If an override
    already exists at the actor scope with a different version, it will be deleted first
    before creating the new one.

    Note:
        Race condition caveat: The check-then-delete-then-create sequence is not atomic.
        If two concurrent requests attempt to set version overrides for the same connector,
        both could pass the existence check and one could still fail with a duplicate key
        error. The improved 500 error message provides guidance in this case.

    Args:
        connector_id: The ID of the deployed connector
        connector_type: Either "source" or "destination"
        api_root: The API root URL
        client_id: The Airbyte Cloud client ID (required if no bearer_token)
        client_secret: The Airbyte Cloud client secret (required if no bearer_token)
        workspace_id: The workspace ID
        version: The version to pin to (e.g., "0.1.0"), or None to unset
        unset: If True, removes any existing override
        override_reason: Required when setting. Explanation for the override
        override_reason_reference_url: Optional URL with more context
        user_email: Email of user creating the override
        bearer_token: Pre-existing bearer token (takes precedence over client credentials)

    Returns:
        True if operation succeeded, False if no override existed (unset only)

    Raises:
        PyAirbyteInputError: If the API request fails or parameters are invalid
    """
    # Input validation
    if (version is None) == (not unset):
        raise PyAirbyteInputError(
            message="Must specify EXACTLY ONE of version (to set) OR unset=True (to clear), but not both",
        )

    if not unset and (not override_reason or len(override_reason.strip()) < 10):
        raise PyAirbyteInputError(
            message="override_reason is required when setting a version and must be at least 10 characters",
        )

    access_token = _get_access_token(client_id, client_secret, bearer_token)

    # Build the scoped configuration
    scope_type = _ScopeType.ACTOR

    if unset:
        # To unset, we need to delete the scoped configuration
        # First, get the actor_definition_id for the connector
        get_endpoint: str = f"{api_root}/{connector_type}s/get"
        get_payload: dict[str, str] = {f"{connector_type}Id": connector_id}
        definition_id_key = f"{connector_type}DefinitionId"

        get_response = requests.post(
            get_endpoint,
            json=get_payload,
            headers={
                "Authorization": f"Bearer {access_token}",
                "User-Agent": ops_constants.USER_AGENT,
                "Content-Type": "application/json",
            },
            timeout=30,
        )

        if get_response.status_code != 200:
            raise PyAirbyteInputError(
                message=f"Failed to get {connector_type} info: {get_response.status_code} {get_response.text}",
            )

        connector_info = get_response.json()
        actor_definition_id = connector_info.get(definition_id_key)

        if not actor_definition_id:
            raise PyAirbyteInputError(
                message=f"Could not find {definition_id_key} in {connector_type} info",
            )

        # Use the shared helper to get the scoped configuration context at actor scope
        active_config = _get_scoped_configuration_context(
            actor_definition_id=actor_definition_id,
            scope_type=_ScopeType.ACTOR,
            scope_id=connector_id,
            api_root=api_root,
            access_token=access_token,
        )

        if not active_config:
            # No override exists, nothing to do
            return False

        # Delete the active configuration
        delete_endpoint = f"{api_root}/scoped_configuration/delete"
        delete_payload = {"scopedConfigurationId": active_config["id"]}

        response = requests.post(
            delete_endpoint,
            json=delete_payload,
            headers={
                "Authorization": f"Bearer {access_token}",
                "User-Agent": ops_constants.USER_AGENT,
                "Content-Type": "application/json",
            },
            timeout=30,
        )

        if response.status_code not in (200, 204):
            raise PyAirbyteInputError(
                message=f"Failed to delete version override: {response.status_code} {response.text}",
                context={
                    "delete_endpoint": delete_endpoint,
                    "config_id": active_config["id"],
                    "status_code": response.status_code,
                    "response": response.text,
                },
            )

        return True

    else:
        # Set a new override
        # First, get the actor_definition_id for the connector
        get_endpoint = f"{api_root}/{connector_type}s/get"
        get_payload: dict[str, str] = {f"{connector_type}Id": connector_id}
        definition_id_key = f"{connector_type}DefinitionId"

        get_response = requests.post(
            get_endpoint,
            json=get_payload,
            headers={
                "Authorization": f"Bearer {access_token}",
                "User-Agent": ops_constants.USER_AGENT,
                "Content-Type": "application/json",
            },
            timeout=30,
        )

        if get_response.status_code != 200:
            raise PyAirbyteInputError(
                message=f"Failed to get {connector_type} info: {get_response.status_code} {get_response.text}",
            )

        connector_info = get_response.json()
        actor_definition_id = connector_info.get(definition_id_key)

        if not actor_definition_id:
            raise PyAirbyteInputError(
                message=f"Could not find {definition_id_key} in {connector_type} info",
            )

        # Resolve version string to version ID
        version_id = resolve_connector_version_id(
            actor_definition_id=actor_definition_id,
            connector_type=connector_type,
            version=version,
            api_root=api_root,
            client_id=client_id,
            client_secret=client_secret,
            bearer_token=bearer_token,
        )

        # Get organization_id from workspace info for comprehensive scope checking
        # This is REQUIRED - we must always check all three scopes
        workspace_endpoint = f"{api_root}/workspaces/get"
        workspace_payload = {"workspaceId": workspace_id}
        workspace_response = requests.post(
            workspace_endpoint,
            json=workspace_payload,
            headers={
                "Authorization": f"Bearer {access_token}",
                "User-Agent": ops_constants.USER_AGENT,
                "Content-Type": "application/json",
            },
            timeout=30,
        )
        if workspace_response.status_code != 200:
            raise PyAirbyteInputError(
                message=f"Failed to get workspace info: {workspace_response.status_code} {workspace_response.text}. "
                "Workspace info is required to determine organization_id for comprehensive scope checking.",
                context={
                    "workspace_id": workspace_id,
                    "status_code": workspace_response.status_code,
                    "response": workspace_response.text,
                },
            )
        workspace_info = workspace_response.json()
        organization_id = workspace_info.get("organizationId")
        if not organization_id:
            raise PyAirbyteInputError(
                message="Workspace does not have an organization_id. "
                "Organization ID is required for comprehensive scope checking.",
                context={
                    "workspace_id": workspace_id,
                    "workspace_info": workspace_info,
                },
            )

        # Check for existing scoped configuration at ALL scope levels BEFORE creating
        # This prevents duplicate key constraint violations (500 errors) and provides
        # clear messaging about where existing pins are set
        all_configs = get_all_scoped_configuration_contexts(
            connector_id=connector_id,
            actor_definition_id=actor_definition_id,
            workspace_id=workspace_id,
            organization_id=organization_id,
            api_root=api_root,
            client_id=client_id,
            client_secret=client_secret,
            bearer_token=bearer_token,
        )

        # Check actor-level config first (most specific)
        actor_config = all_configs.get(_ScopeType.ACTOR.value)
        if actor_config:
            existing_version_id = actor_config.get("value")
            # API returns snake_case field names
            existing_version_name = actor_config.get("value_name", "unknown")

            # If already pinned to the same version at actor level, no action needed
            if existing_version_id == version_id:
                # Build detailed message with full context about the existing pin
                # API returns snake_case field names
                existing_description = actor_config.get(
                    "description", "No description provided"
                )
                existing_reference_url = actor_config.get(
                    "reference_url", "No reference URL"
                )
                existing_origin = actor_config.get("origin", "unknown")
                existing_origin_type = actor_config.get("origin_type", "unknown")
                existing_created_at = actor_config.get("created_at", "unknown")
                existing_updated_at = actor_config.get("updated_at", "unknown")
                existing_scope_name = actor_config.get("scope_name", "unknown")
                existing_resource_name = actor_config.get("resource_name", "unknown")

                detailed_message = (
                    f"Connector is already pinned to version {existing_version_name} "
                    f"(version_id: {existing_version_id}) at actor scope.\n\n"
                    f"EXISTING PIN DETAILS:\n"
                    f"  - Config ID: {actor_config.get('id')}\n"
                    f"  - Pinned Version: {existing_version_name}\n"
                    f"  - Connector Name: {existing_scope_name}\n"
                    f"  - Connector Definition: {existing_resource_name}\n"
                    f"  - Description: {existing_description}\n"
                    f"  - Reference URL: {existing_reference_url}\n"
                    f"  - Origin Type: {existing_origin_type}\n"
                    f"  - Origin: {existing_origin}\n"
                    f"  - Created At: {existing_created_at}\n"
                    f"  - Updated At: {existing_updated_at}\n\n"
                    f"No action needed. Use unset=True first if you want to re-pin to a different version."
                )

                raise PyAirbyteInputError(
                    message=detailed_message,
                    context={
                        "connector_id": connector_id,
                        "connector_type": connector_type,
                        "existing_version": existing_version_name,
                        "existing_version_id": existing_version_id,
                        "requested_version": version,
                        "requested_version_id": version_id,
                        "existing_config_id": actor_config.get("id"),
                        "existing_description": existing_description,
                        "existing_reference_url": existing_reference_url,
                        "existing_origin": existing_origin,
                        "existing_origin_type": existing_origin_type,
                        "existing_created_at": existing_created_at,
                        "existing_updated_at": existing_updated_at,
                        "scope_level": _ScopeType.ACTOR.value,
                        "scope_type_from_api": actor_config.get("scope_type"),
                        "scope_id_from_api": actor_config.get("scope_id"),
                        "full_existing_config": actor_config,
                    },
                )

            # If pinned to a different version at actor level, delete it first
            # SAFETY GUARD: Only delete if the returned config is truly actor-scoped
            # (not an inherited workspace/org config returned by the API)
            api_scope_type = actor_config.get("scope_type", "").lower()
            api_scope_id = actor_config.get("scope_id", "")
            if api_scope_type != _ScopeType.ACTOR.value or api_scope_id != connector_id:
                raise PyAirbyteInputError(
                    message=f"Cannot delete existing config: API returned a config that is not actor-scoped. "
                    f"Expected scope_type='{_ScopeType.ACTOR.value}' and scope_id='{connector_id}', "
                    f"but got scope_type='{api_scope_type}' and scope_id='{api_scope_id}'. "
                    f"This may be an inherited config from workspace/organization level.",
                    context={
                        "connector_id": connector_id,
                        "expected_scope_type": _ScopeType.ACTOR.value,
                        "expected_scope_id": connector_id,
                        "actual_scope_type": api_scope_type,
                        "actual_scope_id": api_scope_id,
                        "full_config": actor_config,
                    },
                )

            delete_endpoint = f"{api_root}/scoped_configuration/delete"
            delete_payload = {"scopedConfigurationId": actor_config["id"]}

            delete_response = requests.post(
                delete_endpoint,
                json=delete_payload,
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "User-Agent": ops_constants.USER_AGENT,
                    "Content-Type": "application/json",
                },
                timeout=30,
            )

            if delete_response.status_code not in (200, 204):
                raise PyAirbyteInputError(
                    message=f"Failed to delete existing actor-level version override before setting new one: "
                    f"{delete_response.status_code} {delete_response.text}. "
                    f"Connector is currently pinned to {existing_version_name} at actor scope.",
                    context={
                        "delete_endpoint": delete_endpoint,
                        "config_id": actor_config["id"],
                        "existing_version": existing_version_name,
                        "requested_version": version,
                        "status_code": delete_response.status_code,
                        "response": delete_response.text,
                        "scope_level": _ScopeType.ACTOR.value,
                    },
                )

        # Report if there are pins at workspace or organization level (informational)
        # These won't cause duplicate key errors but users should be aware of them
        workspace_config = all_configs.get(_ScopeType.WORKSPACE.value)
        org_config = all_configs.get(_ScopeType.ORGANIZATION.value)
        inherited_pins: list[str] = []
        if workspace_config:
            ws_version = workspace_config.get("valueName", "unknown")
            inherited_pins.append(f"workspace (version: {ws_version})")
        if org_config:
            org_version = org_config.get("valueName", "unknown")
            inherited_pins.append(f"organization (version: {org_version})")

        # Get user ID from email - required by API spec
        if not user_email:
            raise PyAirbyteInputError(
                message="user_email is required to set a version override",
                context={
                    "connector_id": connector_id,
                    "connector_type": connector_type,
                },
            )
        origin = get_user_id_by_email(
            email=user_email,
            api_root=api_root,
            client_id=client_id,
            client_secret=client_secret,
            bearer_token=bearer_token,
        )

        # Create the override with correct schema
        endpoint = f"{api_root}/scoped_configuration/create"

        # Build payload with explicit string values for auditability
        # (enum.value ensures we log exactly what we send)
        payload: dict[str, Any] = {
            "config_key": _ScopedConfigKey.CONNECTOR_VERSION.value,
            "resource_type": _ResourceType.ACTOR_DEFINITION.value,
            "resource_id": actor_definition_id,
            "scope_type": scope_type.value,
            "scope_id": connector_id,
            "value": version_id,  # Use version ID, not version string
            "description": override_reason,
            "origin_type": _OriginType.USER.value,
            "origin": origin,
        }

        if override_reason_reference_url:
            payload["reference_url"] = override_reason_reference_url

        response = requests.post(
            endpoint,
            json=payload,
            headers={
                "Authorization": f"Bearer {access_token}",
                "User-Agent": ops_constants.USER_AGENT,
                "Content-Type": "application/json",
            },
            timeout=30,
        )

        if response.status_code not in (200, 201):
            # Provide helpful guidance for 500 errors which often indicate duplicates
            error_message = f"Failed to set version override: {response.status_code} {response.text}"
            if response.status_code == 500:
                error_message += (
                    " A 500 error often indicates a duplicate key constraint violation - "
                    "the connector may already be pinned. Try using unset=True first, "
                    "or use the error lookup tool to get more details on the error ID."
                )
                if inherited_pins:
                    error_message += (
                        f" Note: Version pins were found at other scope levels: {', '.join(inherited_pins)}. "
                        "These inherited pins won't cause duplicate key errors but may affect the connector."
                    )
            raise PyAirbyteInputError(
                message=error_message,
                context={
                    "connector_id": connector_id,
                    "connector_type": connector_type,
                    "version": version,
                    "version_id": version_id,
                    "endpoint": endpoint,
                    "payload": payload,
                    "actor_definition_id": actor_definition_id,
                    "status_code": response.status_code,
                    "response": response.text,
                    "inherited_pins": inherited_pins if inherited_pins else None,
                    "all_scope_configs": {
                        k: {"id": v.get("id"), "valueName": v.get("valueName")}
                        for k, v in all_configs.items()
                        if v
                    },
                },
            )

        return True
