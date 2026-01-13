# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
"""Tests for the prerelease module."""

import pytest

from airbyte_ops_mcp.mcp.prerelease import (
    PRERELEASE_SHA_LENGTH,
    PRERELEASE_TAG_PREFIX,
    compute_prerelease_docker_image_tag,
)


@pytest.mark.parametrize(
    "base_version,sha,expected",
    [
        pytest.param(
            "1.2.3",
            "abcdef1234567890",
            "1.2.3-preview.abcdef1",
            id="standard_version_long_sha",
        ),
        pytest.param(
            "0.1.0",
            "1234567",
            "0.1.0-preview.1234567",
            id="short_version_exact_sha_length",
        ),
        pytest.param(
            "10.20.30",
            "abc1234",
            "10.20.30-preview.abc1234",
            id="large_version_numbers",
        ),
        pytest.param(
            "0.0.1",
            "deadbeef12345678901234567890",
            "0.0.1-preview.deadbee",
            id="very_long_sha_truncated",
        ),
        pytest.param(
            "2.0.0",
            "a6370d9275abc123",
            "2.0.0-preview.a6370d9",
            id="real_world_sha_example",
        ),
    ],
)
def test_compute_prerelease_docker_image_tag(
    base_version: str, sha: str, expected: str
) -> None:
    """Test that compute_prerelease_docker_image_tag produces correct version tags."""
    result = compute_prerelease_docker_image_tag(base_version, sha)
    assert result == expected


def test_prerelease_constants() -> None:
    """Test that prerelease constants have expected values."""
    assert PRERELEASE_TAG_PREFIX == "preview"
    assert PRERELEASE_SHA_LENGTH == 7


def test_compute_prerelease_docker_image_tag_uses_constants() -> None:
    """Test that the function uses the defined constants for consistency."""
    base_version = "1.0.0"
    sha = "abcdefghijklmnop"

    result = compute_prerelease_docker_image_tag(base_version, sha)

    assert f"-{PRERELEASE_TAG_PREFIX}." in result
    assert result.endswith(sha[:PRERELEASE_SHA_LENGTH])
