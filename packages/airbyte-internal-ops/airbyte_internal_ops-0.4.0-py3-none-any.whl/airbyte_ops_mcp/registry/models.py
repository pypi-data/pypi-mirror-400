# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
"""Pydantic models for registry connector publish operations.

This module defines the data models used for connector publish operations
including applying and rolling back version overrides.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class ConnectorMetadata(BaseModel):
    """Connector metadata from metadata.yaml.

    This model represents the essential metadata about a connector
    read from its metadata.yaml file in the Airbyte monorepo.
    """

    name: str = Field(description="The connector technical name")
    docker_repository: str = Field(description="The Docker repository")
    docker_image_tag: str = Field(description="The Docker image tag/version")
    support_level: str | None = Field(
        default=None, description="The support level (certified, community, etc.)"
    )
    definition_id: str | None = Field(
        default=None, description="The connector definition ID"
    )


class ConnectorPublishResult(BaseModel):
    """Result of a connector publish operation.

    This model provides detailed information about the outcome of a
    connector publish operation (apply or rollback version override).
    """

    connector: str = Field(description="The connector technical name")
    version: str = Field(description="The connector version")
    action: Literal["apply-version-override", "rollback-version-override"] = Field(
        description="The action performed"
    )
    status: Literal["success", "failure", "dry-run"] = Field(
        description="The status of the operation"
    )
    docker_image: str | None = Field(
        default=None, description="The Docker image name if applicable"
    )
    registry_updated: bool = Field(
        default=False, description="Whether the registry was updated"
    )
    message: str | None = Field(default=None, description="Additional status message")

    def __str__(self) -> str:
        """Return a string representation of the publish result."""
        status_prefix = "dry-run" if self.status == "dry-run" else self.status
        return f"[{status_prefix}] {self.connector}:{self.version} - {self.action}"


# Type alias for publish actions
PublishAction = Literal["apply-version-override", "rollback-version-override"]
