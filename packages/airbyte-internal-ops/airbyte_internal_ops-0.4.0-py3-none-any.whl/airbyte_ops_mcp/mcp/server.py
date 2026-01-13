# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
"""Airbyte Admin MCP server implementation.

This module provides the main MCP server for Airbyte admin operations.

The server can run in two modes:
- **stdio mode** (default): For direct MCP client connections via stdin/stdout
- **HTTP mode**: For HTTP-based MCP connections, useful for containerized deployments

Environment Variables:
    MCP_HTTP_HOST: Host to bind HTTP server to (default: 127.0.0.1)
    MCP_HTTP_PORT: Port for HTTP server (default: 8082)
"""

import asyncio
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from fastmcp import FastMCP

from airbyte_ops_mcp.constants import MCP_SERVER_NAME
from airbyte_ops_mcp.mcp.cloud_connector_versions import (
    register_cloud_connector_version_tools,
)
from airbyte_ops_mcp.mcp.gcp_logs import register_gcp_logs_tools
from airbyte_ops_mcp.mcp.github import register_github_tools
from airbyte_ops_mcp.mcp.github_repo_ops import register_github_repo_ops_tools
from airbyte_ops_mcp.mcp.prerelease import register_prerelease_tools
from airbyte_ops_mcp.mcp.prod_db_queries import register_prod_db_query_tools
from airbyte_ops_mcp.mcp.prompts import register_prompts
from airbyte_ops_mcp.mcp.regression_tests import register_regression_tests_tools
from airbyte_ops_mcp.mcp.server_info import register_server_info_resources

# Default HTTP server configuration
DEFAULT_HTTP_HOST = "127.0.0.1"
DEFAULT_HTTP_PORT = 8082

app: FastMCP = FastMCP(MCP_SERVER_NAME)


def register_server_assets(app: FastMCP) -> None:
    """Register all server assets (tools, prompts, resources) with the FastMCP app.

    This function registers assets for all domains:
    - SERVER_INFO: Server version and information resources
    - REPO: GitHub repository operations
    - CLOUD: Cloud connector version management
    - PROMPTS: Prompt templates for common workflows
    - REGRESSION_TESTS: Connector regression tests (single-version and comparison)
    - REGISTRY: Connector registry operations (future)
    - METADATA: Connector metadata operations (future)
    - QA: Connector quality assurance (future)
    - INSIGHTS: Connector analysis and insights (future)

    Args:
        app: FastMCP application instance
    """
    register_server_info_resources(app)
    register_github_repo_ops_tools(app)
    register_github_tools(app)
    register_prerelease_tools(app)
    register_cloud_connector_version_tools(app)
    register_prod_db_query_tools(app)
    register_gcp_logs_tools(app)
    register_prompts(app)
    register_regression_tests_tools(app)


register_server_assets(app)


def _load_env() -> None:
    """Load environment variables from .env file if present."""
    env_file = Path.cwd() / ".env"
    if env_file.exists():
        load_dotenv(env_file)
        print(f"Loaded environment from: {env_file}", flush=True, file=sys.stderr)


def main() -> None:
    """Main entry point for the Airbyte Admin MCP server (stdio mode).

    This is the default entry point that runs the server in stdio mode,
    suitable for direct MCP client connections.
    """
    _load_env()

    print("=" * 60, flush=True, file=sys.stderr)
    print("Starting Airbyte Admin MCP server (stdio mode).", file=sys.stderr)
    try:
        asyncio.run(app.run_stdio_async(show_banner=False))
    except KeyboardInterrupt:
        print("Airbyte Admin MCP server interrupted by user.", file=sys.stderr)

    print("Airbyte Admin MCP server stopped.", file=sys.stderr)
    print("=" * 60, flush=True, file=sys.stderr)


def _parse_port(port_str: str | None, default: int) -> int:
    """Parse and validate a port number from string.

    Args:
        port_str: Port string from environment variable, or None if not set
        default: Default port to use if port_str is None

    Returns:
        Validated port number

    Raises:
        ValueError: If port_str is not a valid integer or out of range
    """
    if port_str is None:
        return default

    port_str = port_str.strip()
    if not port_str.isdecimal():
        raise ValueError(f"MCP_HTTP_PORT must be a valid integer, got: {port_str!r}")

    port = int(port_str)
    if not 1 <= port <= 65535:
        raise ValueError(f"MCP_HTTP_PORT must be between 1 and 65535, got: {port}")

    return port


def main_http() -> None:
    """HTTP entry point for the Airbyte Admin MCP server.

    This entry point runs the server in HTTP mode, suitable for containerized
    deployments where the server needs to be accessible over HTTP.

    Environment Variables:
        MCP_HTTP_HOST: Host to bind to (default: 127.0.0.1)
        MCP_HTTP_PORT: Port to listen on (default: 8082)
    """
    _load_env()

    host = os.getenv("MCP_HTTP_HOST", DEFAULT_HTTP_HOST)
    port = _parse_port(os.getenv("MCP_HTTP_PORT"), DEFAULT_HTTP_PORT)

    print("=" * 60, flush=True, file=sys.stderr)
    print(
        f"Starting Airbyte Admin MCP server (HTTP mode) on {host}:{port}",
        file=sys.stderr,
    )
    try:
        app.run(transport="http", host=host, port=port)
    except KeyboardInterrupt:
        print("Airbyte Admin MCP server interrupted by user.", file=sys.stderr)

    print("Airbyte Admin MCP server stopped.", file=sys.stderr)
    print("=" * 60, flush=True, file=sys.stderr)


if __name__ == "__main__":
    main()
