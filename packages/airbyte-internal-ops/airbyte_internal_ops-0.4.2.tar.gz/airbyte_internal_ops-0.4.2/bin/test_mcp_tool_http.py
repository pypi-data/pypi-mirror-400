#!/usr/bin/env python3
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
"""One-step stateless test for airbyte-ops-mcp HTTP transport.

This script spawns the HTTP server on an ephemeral port, verifies it's working,
optionally calls a specific tool, then shuts down the server.

Usage:
    poe mcp-tool-test-http                           # Smoke test only
    poe mcp-tool-test-http <tool_name> '<json_args>' # Test specific tool

Examples:
    poe mcp-tool-test-http
    poe mcp-tool-test-http get_server_version '{}'
"""

import asyncio
import json
import os
import socket
import subprocess
import sys
from typing import Any

from fastmcp import Client

SERVER_STARTUP_TIMEOUT = 10.0
SERVER_SHUTDOWN_TIMEOUT = 5.0
POLL_INTERVAL = 0.2
MIN_ARGS_FOR_TOOL = 2


def find_free_port() -> int:
    """Find an available port on localhost."""
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


async def wait_for_server(url: str, timeout: float = SERVER_STARTUP_TIMEOUT) -> bool:
    """Wait for the MCP server to be ready by attempting to list tools."""
    deadline = asyncio.get_event_loop().time() + timeout
    while asyncio.get_event_loop().time() < deadline:
        try:
            async with Client(url) as client:
                await client.list_tools()
                return True
        except Exception:
            await asyncio.sleep(POLL_INTERVAL)
    return False


async def run_test() -> int:
    """Run the HTTP transport test."""
    port = find_free_port()
    url = f"http://127.0.0.1:{port}/mcp"

    env = os.environ.copy()
    env["MCP_HTTP_PORT"] = str(port)

    print(f"Starting HTTP server on port {port}...", file=sys.stderr)

    proc = subprocess.Popen(
        ["uv", "run", "airbyte-ops-mcp-http"],
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    try:
        if not await wait_for_server(url):
            print(f"Server failed to start on port {port}", file=sys.stderr)
            return 1

        async with Client(url) as client:
            tools = await client.list_tools()
            print(f"HTTP transport OK - {len(tools)} tools available")

            if len(sys.argv) >= MIN_ARGS_FOR_TOOL:
                tool_name = sys.argv[1]
                args: dict[str, Any] = {}
                if len(sys.argv) >= MIN_ARGS_FOR_TOOL + 1:
                    args = json.loads(sys.argv[2])

                print(f"Calling tool: {tool_name}", file=sys.stderr)
                result = await client.call_tool(tool_name, args)

                if hasattr(result, "text"):
                    print(result.text)
                else:
                    print(str(result))

        return 0

    finally:
        proc.terminate()
        try:
            proc.wait(timeout=SERVER_SHUTDOWN_TIMEOUT)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait()


def main() -> None:
    """Main entry point."""
    sys.exit(asyncio.run(run_test()))


if __name__ == "__main__":
    main()
