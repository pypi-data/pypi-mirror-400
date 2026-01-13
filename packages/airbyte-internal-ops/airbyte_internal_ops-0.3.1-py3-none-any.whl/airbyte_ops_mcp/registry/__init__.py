# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
"""Registry operations for Airbyte connectors.

This package provides functionality for publishing connectors to the Airbyte
registry, including promoting and rolling back release candidates.
"""

from __future__ import annotations

from airbyte_ops_mcp.registry.models import (
    ConnectorMetadata,
    ConnectorPublishResult,
    PublishAction,
)
from airbyte_ops_mcp.registry.publish import (
    CONNECTOR_PATH_PREFIX,
    METADATA_FILE_NAME,
    get_connector_metadata,
    is_release_candidate,
    publish_connector,
    strip_rc_suffix,
)

__all__ = [
    "CONNECTOR_PATH_PREFIX",
    "METADATA_FILE_NAME",
    "ConnectorMetadata",
    "ConnectorPublishResult",
    "PublishAction",
    "get_connector_metadata",
    "is_release_candidate",
    "publish_connector",
    "strip_rc_suffix",
]
