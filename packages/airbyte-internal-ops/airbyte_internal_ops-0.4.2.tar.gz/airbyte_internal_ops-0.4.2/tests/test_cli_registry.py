# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
"""Unit tests for the CLI registry connector publish command."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

from airbyte_ops_mcp.registry import (
    ConnectorMetadata,
    ConnectorPublishResult,
    is_release_candidate,
    strip_rc_suffix,
)


@pytest.mark.unit
@pytest.mark.parametrize(
    "version,expected",
    [
        pytest.param("1.2.3-rc.1", True, id="valid_rc_version"),
        pytest.param("1.2.3-rc.10", True, id="valid_rc_version_double_digit"),
        pytest.param("0.0.1-rc.1", True, id="valid_rc_version_zero"),
        pytest.param("1.2.3", False, id="stable_version"),
        pytest.param("1.2.3-preview.abc123", False, id="preview_version"),
        pytest.param("1.2.3-alpha.1", False, id="alpha_version"),
        pytest.param("1.2.3-beta.1", False, id="beta_version"),
    ],
)
def test_is_release_candidate(version: str, expected: bool) -> None:
    """Test release candidate version detection."""
    assert is_release_candidate(version) == expected


@pytest.mark.unit
@pytest.mark.parametrize(
    "version,expected",
    [
        pytest.param("1.2.3-rc.1", "1.2.3", id="rc_version"),
        pytest.param("1.2.3-rc.10", "1.2.3", id="rc_version_double_digit"),
        pytest.param("0.0.1-rc.1", "0.0.1", id="rc_version_zero"),
        pytest.param("1.2.3", "1.2.3", id="stable_version_unchanged"),
    ],
)
def test_strip_rc_suffix(version: str, expected: str) -> None:
    """Test stripping release candidate suffix from version."""
    assert strip_rc_suffix(version) == expected


@pytest.mark.unit
def test_connector_metadata_model() -> None:
    """Test ConnectorMetadata Pydantic model."""
    metadata = ConnectorMetadata(
        name="source-github",
        docker_repository="airbyte/source-github",
        docker_image_tag="1.2.3-rc.1",
        support_level="certified",
        definition_id="abc123",
    )
    assert metadata.name == "source-github"
    assert metadata.docker_repository == "airbyte/source-github"
    assert metadata.docker_image_tag == "1.2.3-rc.1"
    assert metadata.support_level == "certified"
    assert metadata.definition_id == "abc123"


@pytest.mark.unit
def test_connector_publish_result_model() -> None:
    """Test ConnectorPublishResult Pydantic model."""
    result = ConnectorPublishResult(
        connector="source-github",
        version="1.2.3",
        action="apply-version-override",
        status="success",
        docker_image="airbyte/source-github:1.2.3",
        registry_updated=True,
        message="Applied version override",
    )
    assert result.connector == "source-github"
    assert result.version == "1.2.3"
    assert result.action == "apply-version-override"
    assert result.status == "success"
    assert result.docker_image == "airbyte/source-github:1.2.3"
    assert result.registry_updated is True
    assert result.message == "Applied version override"


def run_cli(
    *args: str, cwd: str | Path | None = None
) -> subprocess.CompletedProcess[str]:
    """Run the airbyte-ops CLI with the given arguments."""
    cmd = [sys.executable, "-m", "airbyte_ops_mcp.cli.app", *args]
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=cwd,
        env={**os.environ, "PYTHONPATH": str(Path(__file__).parent.parent / "src")},
    )


@pytest.mark.unit
def test_cli_help() -> None:
    """Test CLI help output."""
    result = run_cli("--help")
    assert result.returncode == 0
    assert "airbyte-ops" in result.stdout.lower()
    assert "registry" in result.stdout


@pytest.mark.unit
@pytest.mark.parametrize(
    "base_version,sha,expected",
    [
        pytest.param(
            "1.2.3", "abcdef1234567890", "1.2.3-preview.abcdef1", id="standard"
        ),
        pytest.param("0.1.0", "1234567", "0.1.0-preview.1234567", id="short_sha"),
        pytest.param("0.6.0", "a6370d9275", "0.6.0-preview.a6370d9", id="real_world"),
    ],
)
def test_registry_connector_compute_prerelease_tag_with_base_version(
    base_version: str, sha: str, expected: str
) -> None:
    """Test compute-prerelease-tag CLI command with explicit base-version."""
    result = run_cli(
        "registry",
        "connector",
        "compute-prerelease-tag",
        "--connector-name",
        "source-test",  # Connector name is required but not used when base-version is provided
        "--sha",
        sha,
        "--base-version",
        base_version,
    )
    assert result.returncode == 0
    assert result.stdout.strip() == expected


@pytest.mark.unit
def test_registry_connector_compute_prerelease_tag_help() -> None:
    """Test compute-prerelease-tag help output."""
    result = run_cli("registry", "connector", "compute-prerelease-tag", "--help")
    assert result.returncode == 0
    assert "connector-name" in result.stdout
    assert "sha" in result.stdout
    assert "base-version" in result.stdout


@pytest.mark.unit
def test_registry_connector_compute_prerelease_tag_missing_connector_name() -> None:
    """Test compute-prerelease-tag fails without connector-name."""
    result = run_cli(
        "registry",
        "connector",
        "compute-prerelease-tag",
        "--sha",
        "abcdef1",
    )
    assert result.returncode != 0


@pytest.mark.unit
def test_registry_help() -> None:
    """Test registry subcommand help output."""
    result = run_cli("registry", "--help")
    assert result.returncode == 0
    assert "connector" in result.stdout


@pytest.mark.unit
def test_registry_connector_publish_help() -> None:
    """Test registry connector publish help output."""
    result = run_cli("registry", "connector", "publish", "--help")
    assert result.returncode == 0
    assert "repo-path" in result.stdout.lower()
    assert "name" in result.stdout.lower()
    assert "apply-override" in result.stdout.lower()
    assert "rollback-override" in result.stdout.lower()
    assert "dry-run" in result.stdout


@pytest.mark.unit
def test_registry_connector_publish_missing_required_options() -> None:
    """Test that missing required options causes an error."""
    result = run_cli("registry", "connector", "publish")
    assert result.returncode != 0


@pytest.mark.unit
def test_registry_connector_publish_missing_action(tmp_path: Path) -> None:
    """Test that missing action flag causes an error."""
    connector_dir = tmp_path / "airbyte-integrations" / "connectors" / "source-test"
    connector_dir.mkdir(parents=True)
    (connector_dir / "metadata.yaml").write_text(
        "data:\n  dockerRepository: airbyte/source-test\n  dockerImageTag: 1.0.0\n"
    )
    result = run_cli(
        "registry",
        "connector",
        "publish",
        "source-test",
        "--repo-path",
        str(tmp_path),
        cwd=tmp_path,
    )
    assert result.returncode != 0
    assert (
        "Must specify either" in result.stderr or "Must specify either" in result.stdout
    )


@pytest.mark.unit
def test_registry_connector_publish_both_actions_error(tmp_path: Path) -> None:
    """Test that specifying both action flags causes an error."""
    connector_dir = tmp_path / "airbyte-integrations" / "connectors" / "source-test"
    connector_dir.mkdir(parents=True)
    (connector_dir / "metadata.yaml").write_text(
        "data:\n  dockerRepository: airbyte/source-test\n  dockerImageTag: 1.0.0\n"
    )
    result = run_cli(
        "registry",
        "connector",
        "publish",
        "source-test",
        "--repo-path",
        str(tmp_path),
        "--apply-override",
        "--rollback-override",
        cwd=tmp_path,
    )
    assert result.returncode != 0
    assert "Cannot use both" in result.stderr or "Cannot use both" in result.stdout


@pytest.mark.unit
def test_registry_connector_publish_apply_override_dry_run(tmp_path: Path) -> None:
    """Test apply version override with dry-run."""
    connector_dir = tmp_path / "airbyte-integrations" / "connectors" / "source-test"
    connector_dir.mkdir(parents=True)
    (connector_dir / "metadata.yaml").write_text(
        "data:\n  dockerRepository: airbyte/source-test\n  dockerImageTag: 1.0.0-rc.1\n"
    )
    result = run_cli(
        "registry",
        "connector",
        "publish",
        "source-test",
        "--repo-path",
        str(tmp_path),
        "--apply-override",
        "--dry-run",
        cwd=tmp_path,
    )
    assert result.returncode == 0
    assert "dry-run" in result.stdout
    assert "source-test" in result.stdout
    assert "1.0.0" in result.stdout


@pytest.mark.unit
def test_registry_connector_publish_apply_override_non_rc_version(
    tmp_path: Path,
) -> None:
    """Test apply override fails for non-RC version."""
    connector_dir = tmp_path / "airbyte-integrations" / "connectors" / "source-test"
    connector_dir.mkdir(parents=True)
    (connector_dir / "metadata.yaml").write_text(
        "data:\n  dockerRepository: airbyte/source-test\n  dockerImageTag: 1.0.0\n"
    )
    result = run_cli(
        "registry",
        "connector",
        "publish",
        "source-test",
        "--repo-path",
        str(tmp_path),
        "--apply-override",
        cwd=tmp_path,
    )
    assert result.returncode == 1
    assert "failure" in result.stdout
    assert "not a release candidate" in result.stdout


@pytest.mark.unit
def test_registry_connector_publish_rollback_override_dry_run(tmp_path: Path) -> None:
    """Test rollback version override with dry-run."""
    connector_dir = tmp_path / "airbyte-integrations" / "connectors" / "source-test"
    connector_dir.mkdir(parents=True)
    (connector_dir / "metadata.yaml").write_text(
        "data:\n  dockerRepository: airbyte/source-test\n  dockerImageTag: 1.0.0-rc.1\n"
    )
    result = run_cli(
        "registry",
        "connector",
        "publish",
        "source-test",
        "--repo-path",
        str(tmp_path),
        "--rollback-override",
        "--dry-run",
        cwd=tmp_path,
    )
    assert result.returncode == 0
    assert "dry-run" in result.stdout
    assert "source-test" in result.stdout


@pytest.mark.unit
def test_registry_connector_publish_rollback_override_non_rc_version(
    tmp_path: Path,
) -> None:
    """Test rollback override fails for non-RC version."""
    connector_dir = tmp_path / "airbyte-integrations" / "connectors" / "source-test"
    connector_dir.mkdir(parents=True)
    (connector_dir / "metadata.yaml").write_text(
        "data:\n  dockerRepository: airbyte/source-test\n  dockerImageTag: 1.0.0\n"
    )
    result = run_cli(
        "registry",
        "connector",
        "publish",
        "source-test",
        "--repo-path",
        str(tmp_path),
        "--rollback-override",
        cwd=tmp_path,
    )
    assert result.returncode == 1
    assert "failure" in result.stdout
    assert "not a release candidate" in result.stdout


@pytest.mark.unit
def test_registry_connector_publish_connector_not_found(tmp_path: Path) -> None:
    """Test error when connector directory doesn't exist."""
    connectors_dir = tmp_path / "airbyte-integrations" / "connectors"
    connectors_dir.mkdir(parents=True)
    result = run_cli(
        "registry",
        "connector",
        "publish",
        "source-nonexistent",
        "--repo-path",
        str(tmp_path),
        "--apply-override",
        cwd=tmp_path,
    )
    assert result.returncode != 0
    assert "not found" in result.stdout.lower() or "not found" in result.stderr.lower()
