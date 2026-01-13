# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
"""Centralized GCP authentication utilities.

This module provides a single code path for GCP credential handling across
the airbyte-ops-mcp codebase. It supports both standard Application Default
Credentials (ADC) and the GCP_PROD_DB_ACCESS_CREDENTIALS environment variable
used internally at Airbyte.

Usage:
    from airbyte_ops_mcp.gcp_auth import get_secret_manager_client

    # Get a properly authenticated Secret Manager client
    client = get_secret_manager_client()
"""

from __future__ import annotations

import logging
import os
import tempfile
from pathlib import Path

from google.cloud import secretmanager

from airbyte_ops_mcp.constants import ENV_GCP_PROD_DB_ACCESS_CREDENTIALS

logger = logging.getLogger(__name__)

# Environment variable name (internal to GCP libraries)
ENV_GOOGLE_APPLICATION_CREDENTIALS = "GOOGLE_APPLICATION_CREDENTIALS"

# Module-level cache for the credentials file path
_credentials_file_path: str | None = None


def ensure_adc_credentials() -> str | None:
    """Ensure GCP Application Default Credentials are available.

    If GOOGLE_APPLICATION_CREDENTIALS is not set but GCP_PROD_DB_ACCESS_CREDENTIALS is,
    write the JSON credentials to a temp file and set GOOGLE_APPLICATION_CREDENTIALS
    to point to that file. This provides a fallback for internal employees who use
    GCP_PROD_DB_ACCESS_CREDENTIALS as their standard credential source.

    Note: GOOGLE_APPLICATION_CREDENTIALS must be a file path, not JSON content.
    The GCP_PROD_DB_ACCESS_CREDENTIALS env var contains the JSON content directly,
    so we write it to a temp file first.

    This function is idempotent and safe to call multiple times.

    Returns:
        The path to the credentials file if one was created, or None if
        GOOGLE_APPLICATION_CREDENTIALS was already set.
    """
    global _credentials_file_path

    # If GOOGLE_APPLICATION_CREDENTIALS is already set, nothing to do
    if ENV_GOOGLE_APPLICATION_CREDENTIALS in os.environ:
        return None

    # Check if we have the fallback credentials
    gsm_creds = os.getenv(ENV_GCP_PROD_DB_ACCESS_CREDENTIALS)
    if not gsm_creds:
        return None

    # Reuse the same file path if we've already written credentials and file still exists
    if _credentials_file_path is not None and Path(_credentials_file_path).exists():
        os.environ[ENV_GOOGLE_APPLICATION_CREDENTIALS] = _credentials_file_path
        return _credentials_file_path

    # Write credentials to a temp file
    # Use a unique filename based on PID to avoid collisions between processes
    creds_file = Path(tempfile.gettempdir()) / f"gcp_prod_db_creds_{os.getpid()}.json"
    creds_file.write_text(gsm_creds)

    # Set restrictive permissions (owner read/write only)
    creds_file.chmod(0o600)

    _credentials_file_path = str(creds_file)
    os.environ[ENV_GOOGLE_APPLICATION_CREDENTIALS] = _credentials_file_path

    logger.debug(
        f"Wrote {ENV_GCP_PROD_DB_ACCESS_CREDENTIALS} to {creds_file} and set "
        f"{ENV_GOOGLE_APPLICATION_CREDENTIALS}"
    )

    return _credentials_file_path


def get_secret_manager_client() -> secretmanager.SecretManagerServiceClient:
    """Get a Secret Manager client with proper credential handling.

    This function ensures GCP credentials are available (supporting the
    GCP_PROD_DB_ACCESS_CREDENTIALS fallback) before creating the client.

    Returns:
        A configured SecretManagerServiceClient instance.
    """
    ensure_adc_credentials()
    return secretmanager.SecretManagerServiceClient()
