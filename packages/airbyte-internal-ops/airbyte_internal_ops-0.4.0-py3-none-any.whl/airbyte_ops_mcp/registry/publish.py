# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
"""Core logic for registry connector publish operations.

This module provides the core functionality for publishing connectors
to the Airbyte registry, including applying and rolling back version overrides.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import yaml
from google.cloud import storage
from google.oauth2 import service_account

from airbyte_ops_mcp.registry.models import (
    ConnectorMetadata,
    ConnectorPublishResult,
    PublishAction,
)

CONNECTOR_PATH_PREFIX = "airbyte-integrations/connectors"
METADATA_FILE_NAME = "metadata.yaml"
METADATA_FOLDER = "metadata"
LATEST_GCS_FOLDER_NAME = "latest"
RELEASE_CANDIDATE_GCS_FOLDER_NAME = "release_candidate"

# Bucket names for metadata service
PROD_METADATA_SERVICE_BUCKET_NAME = "prod-airbyte-cloud-connector-metadata-service"
DEV_METADATA_SERVICE_BUCKET_NAME = "dev-airbyte-cloud-connector-metadata-service-2"

# Default to dev bucket for safety - use --prod flag to target production
DEFAULT_METADATA_SERVICE_BUCKET_NAME = DEV_METADATA_SERVICE_BUCKET_NAME


def _get_gcs_client() -> storage.Client:
    """Get a GCS storage client using credentials from environment."""
    gcs_creds = os.environ.get("GCS_CREDENTIALS")
    if not gcs_creds:
        raise ValueError(
            "GCS_CREDENTIALS environment variable is required for registry operations"
        )
    service_account_info = json.loads(gcs_creds)
    credentials = service_account.Credentials.from_service_account_info(
        service_account_info
    )
    return storage.Client(credentials=credentials)


def _get_bucket_name(use_prod: bool = False) -> str:
    """Get the metadata service bucket name.

    Args:
        use_prod: If True, use the production bucket. Otherwise use dev bucket.
                  Can be overridden by METADATA_SERVICE_BUCKET_NAME env var.

    Returns:
        The bucket name to use for GCS operations.
    """
    # Environment variable takes precedence if set
    env_bucket = os.environ.get("METADATA_SERVICE_BUCKET_NAME")
    if env_bucket:
        return env_bucket

    # Otherwise use prod or dev based on flag
    if use_prod:
        return PROD_METADATA_SERVICE_BUCKET_NAME
    return DEV_METADATA_SERVICE_BUCKET_NAME


def get_connector_metadata(repo_path: Path, connector_name: str) -> ConnectorMetadata:
    """Read connector metadata from metadata.yaml.

    Args:
        repo_path: Path to the Airbyte monorepo.
        connector_name: The connector technical name (e.g., 'source-github').

    Returns:
        ConnectorMetadata object with the connector's metadata.

    Raises:
        FileNotFoundError: If the connector directory or metadata file doesn't exist.
    """
    connector_dir = repo_path / CONNECTOR_PATH_PREFIX / connector_name
    if not connector_dir.exists():
        raise FileNotFoundError(f"Connector directory not found: {connector_dir}")

    metadata_file = connector_dir / METADATA_FILE_NAME
    if not metadata_file.exists():
        raise FileNotFoundError(f"Metadata file not found: {metadata_file}")

    with open(metadata_file) as f:
        metadata = yaml.safe_load(f)

    data = metadata.get("data", {})
    return ConnectorMetadata(
        name=connector_name,
        docker_repository=data.get("dockerRepository", f"airbyte/{connector_name}"),
        docker_image_tag=data.get("dockerImageTag", "unknown"),
        support_level=data.get("supportLevel"),
        definition_id=data.get("definitionId"),
    )


def is_release_candidate(version: str) -> bool:
    """Check if a version string is a release candidate.

    Args:
        version: The version string to check.

    Returns:
        True if the version is a release candidate (format: X.Y.Z-rc.N), False otherwise.
    """
    return "-rc." in version


def strip_rc_suffix(version: str) -> str:
    """Strip the release candidate suffix from a version string.

    Args:
        version: The version string (e.g., '1.2.3-rc.1').

    Returns:
        The base version without RC suffix (e.g., '1.2.3').
        Returns the original version if no RC suffix is present.
    """
    if "-rc." in version:
        return version.split("-rc.")[0]
    return version


def publish_connector(
    repo_path: Path,
    connector_name: str,
    action: PublishAction,
    dry_run: bool = False,
    use_prod: bool = False,
) -> ConnectorPublishResult:
    """Publish a connector to the Airbyte registry.

    This function handles both applying version overrides (from RC to stable)
    and rolling back version overrides.

    Args:
        repo_path: Path to the Airbyte monorepo.
        connector_name: The connector technical name (e.g., 'source-github').
        action: The publish action to perform ('apply-version-override' or 'rollback-version-override').
        dry_run: If True, show what would be published without making changes.
        use_prod: If True, target the production GCS bucket. Otherwise use dev bucket (default).

    Returns:
        ConnectorPublishResult with the operation outcome.

    Raises:
        FileNotFoundError: If the connector or metadata file doesn't exist.
    """
    metadata = get_connector_metadata(repo_path, connector_name)

    if action == "apply-version-override":
        return _apply_version_override(metadata, dry_run, use_prod)
    else:
        return _rollback_version_override(metadata, dry_run, use_prod)


def _apply_version_override(
    metadata: ConnectorMetadata, dry_run: bool, use_prod: bool = False
) -> ConnectorPublishResult:
    """Apply a version override to promote an RC to stable.

    This copies the release candidate metadata to the 'latest' path in GCS,
    then deletes the release candidate metadata.

    Requires GCS_CREDENTIALS environment variable to be set.
    """
    version = metadata.docker_image_tag
    docker_repo = metadata.docker_repository

    if not is_release_candidate(version):
        return ConnectorPublishResult(
            connector=metadata.name,
            version=version,
            action="apply-version-override",
            status="failure",
            docker_image=f"{docker_repo}:{version}",
            registry_updated=False,
            message=f"Version '{version}' is not a release candidate. "
            "Expected format: X.Y.Z-rc.N",
        )

    target_version = strip_rc_suffix(version)

    if dry_run:
        return ConnectorPublishResult(
            connector=metadata.name,
            version=target_version,
            action="apply-version-override",
            status="dry-run",
            docker_image=f"{docker_repo}:{target_version}",
            registry_updated=False,
            message=f"Would apply version override for {metadata.name}: {version} -> {target_version}",
        )

    bucket_name = _get_bucket_name(use_prod)
    storage_client = _get_gcs_client()
    bucket = storage_client.bucket(bucket_name)

    gcp_connector_dir = f"{METADATA_FOLDER}/{docker_repo}"
    version_path = f"{gcp_connector_dir}/{version}/{METADATA_FILE_NAME}"
    rc_path = (
        f"{gcp_connector_dir}/{RELEASE_CANDIDATE_GCS_FOLDER_NAME}/{METADATA_FILE_NAME}"
    )
    latest_path = f"{gcp_connector_dir}/{LATEST_GCS_FOLDER_NAME}/{METADATA_FILE_NAME}"

    version_blob = bucket.blob(version_path)
    rc_blob = bucket.blob(rc_path)
    latest_blob = bucket.blob(latest_path)

    if not version_blob.exists():
        return ConnectorPublishResult(
            connector=metadata.name,
            version=version,
            action="apply-version-override",
            status="failure",
            docker_image=f"{docker_repo}:{version}",
            registry_updated=False,
            message=f"Version metadata file not found: {version_path}",
        )

    if not rc_blob.exists():
        return ConnectorPublishResult(
            connector=metadata.name,
            version=version,
            action="apply-version-override",
            status="failure",
            docker_image=f"{docker_repo}:{version}",
            registry_updated=False,
            message=f"Release candidate metadata file not found: {rc_path}",
        )

    version_blob.reload()
    rc_blob.reload()
    if rc_blob.md5_hash != version_blob.md5_hash:
        return ConnectorPublishResult(
            connector=metadata.name,
            version=version,
            action="apply-version-override",
            status="failure",
            docker_image=f"{docker_repo}:{version}",
            registry_updated=False,
            message=f"RC metadata hash does not match version metadata hash. "
            f"Unsafe to promote. RC: {rc_path}, Version: {version_path}",
        )

    bucket.copy_blob(rc_blob, bucket, latest_blob.name)
    rc_blob.delete()

    return ConnectorPublishResult(
        connector=metadata.name,
        version=target_version,
        action="apply-version-override",
        status="success",
        docker_image=f"{docker_repo}:{target_version}",
        registry_updated=True,
        message=f"Applied version override for {metadata.name}: {version} -> {target_version}. "
        f"Copied RC to latest and deleted RC metadata.",
    )


def _rollback_version_override(
    metadata: ConnectorMetadata, dry_run: bool, use_prod: bool = False
) -> ConnectorPublishResult:
    """Rollback a version override by deleting the RC metadata from GCS.

    This deletes both the release candidate metadata and the versioned metadata
    after verifying their hashes match.

    Requires GCS_CREDENTIALS environment variable to be set.
    """
    version = metadata.docker_image_tag
    docker_repo = metadata.docker_repository

    if not is_release_candidate(version):
        return ConnectorPublishResult(
            connector=metadata.name,
            version=version,
            action="rollback-version-override",
            status="failure",
            docker_image=f"{docker_repo}:{version}",
            registry_updated=False,
            message=f"Version '{version}' is not a release candidate. "
            "Expected format: X.Y.Z-rc.N",
        )

    if dry_run:
        return ConnectorPublishResult(
            connector=metadata.name,
            version=version,
            action="rollback-version-override",
            status="dry-run",
            docker_image=f"{docker_repo}:{version}",
            registry_updated=False,
            message=f"Would rollback version override for {metadata.name} (current: {version})",
        )

    bucket_name = _get_bucket_name(use_prod)
    storage_client = _get_gcs_client()
    bucket = storage_client.bucket(bucket_name)

    gcp_connector_dir = f"{METADATA_FOLDER}/{docker_repo}"
    version_path = f"{gcp_connector_dir}/{version}/{METADATA_FILE_NAME}"
    rc_path = (
        f"{gcp_connector_dir}/{RELEASE_CANDIDATE_GCS_FOLDER_NAME}/{METADATA_FILE_NAME}"
    )

    version_blob = bucket.blob(version_path)
    rc_blob = bucket.blob(rc_path)

    if not version_blob.exists():
        return ConnectorPublishResult(
            connector=metadata.name,
            version=version,
            action="rollback-version-override",
            status="failure",
            docker_image=f"{docker_repo}:{version}",
            registry_updated=False,
            message=f"Version metadata file not found: {version_path}",
        )

    if not rc_blob.exists():
        return ConnectorPublishResult(
            connector=metadata.name,
            version=version,
            action="rollback-version-override",
            status="failure",
            docker_image=f"{docker_repo}:{version}",
            registry_updated=False,
            message=f"Release candidate metadata file not found: {rc_path}",
        )

    version_blob.reload()
    rc_blob.reload()
    if rc_blob.md5_hash != version_blob.md5_hash:
        return ConnectorPublishResult(
            connector=metadata.name,
            version=version,
            action="rollback-version-override",
            status="failure",
            docker_image=f"{docker_repo}:{version}",
            registry_updated=False,
            message=f"RC metadata hash does not match version metadata hash. "
            f"Unsafe to delete. RC: {rc_path}, Version: {version_path}",
        )

    rc_blob.delete()
    version_blob.delete()

    return ConnectorPublishResult(
        connector=metadata.name,
        version=version,
        action="rollback-version-override",
        status="success",
        docker_image=f"{docker_repo}:{version}",
        registry_updated=True,
        message=f"Rolled back version override for {metadata.name}. "
        f"Deleted RC and version metadata from GCS.",
    )
