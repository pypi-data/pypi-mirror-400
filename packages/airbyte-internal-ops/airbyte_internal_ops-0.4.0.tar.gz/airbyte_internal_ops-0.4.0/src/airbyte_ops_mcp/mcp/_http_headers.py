# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
"""HTTP header extraction for Airbyte Cloud credentials.

This module provides internal helper functions for extracting Airbyte Cloud
authentication credentials from HTTP headers when running as an MCP HTTP server.
This enables per-request credential passing from upstream services like coral-agents.

The resolution order for credentials is:
1. HTTP headers (when running as MCP HTTP server)
2. Environment variables (fallback)

Note: This module is prefixed with "_" to indicate it is internal helper logic
for the MCP module and should not be imported directly by external code.
"""

from __future__ import annotations

import os

from airbyte.cloud.auth import (
    resolve_cloud_api_url,
    resolve_cloud_client_id,
    resolve_cloud_client_secret,
    resolve_cloud_workspace_id,
)
from airbyte.secrets.base import SecretString
from fastmcp.server.dependencies import get_http_headers

from airbyte_ops_mcp.constants import (
    HEADER_AIRBYTE_CLOUD_API_URL,
    HEADER_AIRBYTE_CLOUD_CLIENT_ID,
    HEADER_AIRBYTE_CLOUD_CLIENT_SECRET,
    HEADER_AIRBYTE_CLOUD_WORKSPACE_ID,
)


def _get_header_value(headers: dict[str, str], header_name: str) -> str | None:
    """Get a header value from a headers dict, case-insensitively.

    Args:
        headers: Dictionary of HTTP headers.
        header_name: The header name to look for (case-insensitive).

    Returns:
        The header value if found, None otherwise.
    """
    header_name_lower = header_name.lower()
    for key, value in headers.items():
        if key.lower() == header_name_lower:
            return value
    return None


def get_bearer_token_from_headers() -> SecretString | None:
    """Extract bearer token from HTTP Authorization header.

    This function extracts the bearer token from the standard HTTP
    `Authorization: Bearer <token>` header when running as an MCP HTTP server.

    Returns:
        The bearer token as a SecretString, or None if not found or not in HTTP context.
    """
    headers = get_http_headers()
    if not headers:
        return None

    auth_header = _get_header_value(headers, "Authorization")
    if not auth_header:
        return None

    # Parse "Bearer <token>" format (case-insensitive prefix check)
    bearer_prefix = "bearer "
    if auth_header.lower().startswith(bearer_prefix):
        token = auth_header[len(bearer_prefix) :].strip()
        if token:
            return SecretString(token)

    return None


def get_client_id_from_headers() -> SecretString | None:
    """Extract client ID from HTTP headers.

    Returns:
        The client ID as a SecretString, or None if not found or not in HTTP context.
    """
    headers = get_http_headers()
    if not headers:
        return None

    value = _get_header_value(headers, HEADER_AIRBYTE_CLOUD_CLIENT_ID)
    if value:
        return SecretString(value)
    return None


def get_client_secret_from_headers() -> SecretString | None:
    """Extract client secret from HTTP headers.

    Returns:
        The client secret as a SecretString, or None if not found or not in HTTP context.
    """
    headers = get_http_headers()
    if not headers:
        return None

    value = _get_header_value(headers, HEADER_AIRBYTE_CLOUD_CLIENT_SECRET)
    if value:
        return SecretString(value)
    return None


def get_workspace_id_from_headers() -> str | None:
    """Extract workspace ID from HTTP headers.

    Returns:
        The workspace ID, or None if not found or not in HTTP context.
    """
    headers = get_http_headers()
    if not headers:
        return None

    return _get_header_value(headers, HEADER_AIRBYTE_CLOUD_WORKSPACE_ID)


def get_api_url_from_headers() -> str | None:
    """Extract API URL from HTTP headers.

    Returns:
        The API URL, or None if not found or not in HTTP context.
    """
    headers = get_http_headers()
    if not headers:
        return None

    return _get_header_value(headers, HEADER_AIRBYTE_CLOUD_API_URL)


def resolve_client_id() -> SecretString:
    """Resolve client ID from HTTP headers or environment variables.

    Resolution order:
    1. HTTP header X-Airbyte-Cloud-Client-Id
    2. Environment variable AIRBYTE_CLOUD_CLIENT_ID (via PyAirbyte)

    Returns:
        The resolved client ID as a SecretString.

    Raises:
        PyAirbyteSecretNotFoundError: If no client ID can be resolved.
    """
    header_value = get_client_id_from_headers()
    if header_value:
        return header_value

    return resolve_cloud_client_id()


def resolve_client_secret() -> SecretString:
    """Resolve client secret from HTTP headers or environment variables.

    Resolution order:
    1. HTTP header X-Airbyte-Cloud-Client-Secret
    2. Environment variable AIRBYTE_CLOUD_CLIENT_SECRET (via PyAirbyte)

    Returns:
        The resolved client secret as a SecretString.

    Raises:
        PyAirbyteSecretNotFoundError: If no client secret can be resolved.
    """
    header_value = get_client_secret_from_headers()
    if header_value:
        return header_value

    return resolve_cloud_client_secret()


def resolve_workspace_id(workspace_id: str | None = None) -> str:
    """Resolve workspace ID from multiple sources.

    Resolution order:
    1. Explicit workspace_id parameter (if provided)
    2. HTTP header X-Airbyte-Cloud-Workspace-Id
    3. Environment variable AIRBYTE_CLOUD_WORKSPACE_ID (via PyAirbyte)

    Args:
        workspace_id: Optional explicit workspace ID.

    Returns:
        The resolved workspace ID.

    Raises:
        PyAirbyteSecretNotFoundError: If no workspace ID can be resolved.
    """
    if workspace_id is not None:
        return workspace_id

    header_value = get_workspace_id_from_headers()
    if header_value:
        return header_value

    return resolve_cloud_workspace_id()


def resolve_api_url(api_url: str | None = None) -> str:
    """Resolve API URL from multiple sources.

    Resolution order:
    1. Explicit api_url parameter (if provided)
    2. HTTP header X-Airbyte-Cloud-Api-Url
    3. Environment variable / default (via PyAirbyte)

    Args:
        api_url: Optional explicit API URL.

    Returns:
        The resolved API URL.
    """
    if api_url is not None:
        return api_url

    header_value = get_api_url_from_headers()
    if header_value:
        return header_value

    return resolve_cloud_api_url()


def resolve_bearer_token() -> SecretString | None:
    """Resolve bearer token from HTTP headers or environment variables.

    Resolution order:
    1. HTTP Authorization header (Bearer <token>)
    2. Environment variable AIRBYTE_CLOUD_BEARER_TOKEN

    Returns:
        The resolved bearer token as a SecretString, or None if not found.

    Note:
        Unlike resolve_client_id/resolve_client_secret, this function returns
        None instead of raising an exception if no bearer token is found,
        since bearer token auth is optional (can fall back to client credentials).
    """
    header_value = get_bearer_token_from_headers()
    if header_value:
        return header_value

    # Try env var directly
    env_value = os.environ.get("AIRBYTE_CLOUD_BEARER_TOKEN")
    if env_value:
        return SecretString(env_value)

    return None
