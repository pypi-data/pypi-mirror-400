# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
"""Deferred MCP capability registration for tools, prompts, and resources.

This module provides a decorator to tag tool functions with MCP annotations
for deferred registration. The domain for each tool is automatically derived
from the file stem of the module where the tool is defined.
"""

from __future__ import annotations

import inspect
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, TypeVar

from fastmcp import FastMCP

from airbyte_ops_mcp._annotations import (
    DESTRUCTIVE_HINT,
    IDEMPOTENT_HINT,
    OPEN_WORLD_HINT,
    READ_ONLY_HINT,
)

F = TypeVar("F", bound=Callable[..., Any])


@dataclass
class PromptDef:
    """Definition of a deferred MCP prompt."""

    name: str
    description: str
    func: Callable[..., list[dict[str, str]]]


@dataclass
class ResourceDef:
    """Definition of a deferred MCP resource."""

    uri: str
    description: str
    mime_type: str
    func: Callable[..., Any]


class ToolDomain(str, Enum):
    """Tool domain categories for the Airbyte Admin MCP server.

    These domains correspond to the main functional areas of the server.
    """

    REGISTRY = "registry"
    """Registry tools for connector registry operations"""

    METADATA = "metadata"
    """Metadata tools for connector metadata operations"""

    QA = "qa"
    """QA tools for connector quality assurance"""

    INSIGHTS = "insights"
    """Insights tools for connector analysis and insights"""

    REPO = "repo"
    """Repository tools for GitHub repository operations"""

    CLOUD_ADMIN = "cloud_admin"
    """Cloud admin tools for Airbyte Cloud operations"""

    SERVER_INFO = "server_info"
    """Server information and version resources"""

    PROMPTS = "prompts"
    """Prompt templates for common workflows"""

    REGRESSION_TESTS = "regression_tests"
    """Regression tests for connector validation and comparison testing"""


_REGISTERED_TOOLS: list[tuple[Callable[..., Any], dict[str, Any]]] = []
_REGISTERED_RESOURCES: list[tuple[Callable[..., Any], dict[str, Any]]] = []
_REGISTERED_PROMPTS: list[tuple[Callable[..., Any], dict[str, Any]]] = []


def should_register_tool(annotations: dict[str, Any]) -> bool:
    """Check if a tool should be registered.

    Args:
        annotations: Tool annotations dict

    Returns:
        Always returns True (no filtering applied)
    """
    return True


def _get_caller_file_stem() -> str:
    """Get the file stem of the caller's module.

    Walks up the call stack to find the first frame outside this module,
    then returns the stem of that file (e.g., "github" for "github.py").

    Returns:
        The file stem of the calling module.
    """
    for frame_info in inspect.stack():
        # Skip frames from this module
        if frame_info.filename != __file__:
            return Path(frame_info.filename).stem
    return "unknown"


def _normalize_domain(domain: str) -> str:
    """Normalize a domain string to its simple form.

    Handles both file stems (e.g., "github") and module names
    (e.g., "airbyte_ops_mcp.mcp.github") by extracting the last segment.

    Args:
        domain: A domain string, either a simple name or a dotted module path.

    Returns:
        The normalized domain (last segment of a dotted path, or the input if no dots).
    """
    return domain.rsplit(".", 1)[-1]


def mcp_tool(
    domain: ToolDomain | str | None = None,
    *,
    read_only: bool = False,
    destructive: bool = False,
    idempotent: bool = False,
    open_world: bool = False,
    extra_help_text: str | None = None,
) -> Callable[[F], F]:
    """Decorator to tag an MCP tool function with annotations for deferred registration.

    This decorator stores the annotations on the function for later use during
    deferred registration. It does not register the tool immediately.

    The domain is automatically derived from the file stem of the module where
    the tool is defined (e.g., tools in "github.py" get domain "github").

    Args:
        domain: Optional explicit domain override. If not provided, the domain
            is automatically derived from the caller's file stem.
        read_only: If True, tool only reads without making changes (default: False)
        destructive: If True, tool modifies/deletes existing data (default: False)
        idempotent: If True, repeated calls have same effect (default: False)
        open_world: If True, tool interacts with external systems (default: False)
        extra_help_text: Optional text to append to the function's docstring
            with a newline delimiter

    Returns:
        Decorator function that tags the tool with annotations

    Example:
        @mcp_tool(read_only=True, idempotent=True)
        def list_connectors_in_repo():
            ...
    """
    # Auto-derive domain from caller's file stem if not provided
    if domain is None:
        domain_str = _get_caller_file_stem()
    elif isinstance(domain, ToolDomain):
        domain_str = domain.value
    else:
        domain_str = domain

    annotations: dict[str, Any] = {
        "domain": domain_str,
        READ_ONLY_HINT: read_only,
        DESTRUCTIVE_HINT: destructive,
        IDEMPOTENT_HINT: idempotent,
        OPEN_WORLD_HINT: open_world,
    }

    def decorator(func: F) -> F:
        if extra_help_text:
            func.__doc__ = (
                (func.__doc__ or "") + "\n\n" + (extra_help_text or "")
            ).rstrip()

        _REGISTERED_TOOLS.append((func, annotations))
        return func

    return decorator


def mcp_prompt(
    name: str,
    description: str,
    domain: ToolDomain | str | None = None,
):
    """Decorator for deferred MCP prompt registration.

    Args:
        name: Unique name for the prompt
        description: Human-readable description of the prompt
        domain: Optional domain for filtering. If not provided, automatically
            derived from the caller's file stem.

    Returns:
        Decorator function that registers the prompt

    Raises:
        ValueError: If a prompt with the same name is already registered
    """
    # Auto-derive domain from caller's file stem if not provided
    if domain is None:
        domain_str = _get_caller_file_stem()
    elif isinstance(domain, ToolDomain):
        domain_str = domain.value
    else:
        domain_str = domain

    def decorator(func: Callable[..., list[dict[str, str]]]):
        annotations = {
            "name": name,
            "description": description,
            "domain": domain_str,
        }
        _REGISTERED_PROMPTS.append((func, annotations))
        return func

    return decorator


def mcp_resource(
    uri: str,
    description: str,
    mime_type: str,
    domain: ToolDomain | str | None = None,
):
    """Decorator for deferred MCP resource registration.

    Args:
        uri: Unique URI for the resource
        description: Human-readable description of the resource
        mime_type: MIME type of the resource content
        domain: Optional domain for filtering. If not provided, automatically
            derived from the caller's file stem.

    Returns:
        Decorator function that registers the resource

    Raises:
        ValueError: If a resource with the same URI is already registered
    """
    # Auto-derive domain from caller's file stem if not provided
    if domain is None:
        domain_str = _get_caller_file_stem()
    elif isinstance(domain, ToolDomain):
        domain_str = domain.value
    else:
        domain_str = domain

    def decorator(func: Callable[..., Any]):
        annotations = {
            "uri": uri,
            "description": description,
            "mime_type": mime_type,
            "domain": domain_str,
        }
        _REGISTERED_RESOURCES.append((func, annotations))
        return func

    return decorator


def _register_mcp_callables(
    *,
    app: FastMCP,
    domain: ToolDomain | str,
    resource_list: list[tuple[Callable, dict]],
    register_fn: Callable,
) -> None:
    """Register resources and tools with the FastMCP app, filtered by domain.

    Args:
        app: The FastMCP app instance
        domain: The domain to register tools for. Can be a simple name (e.g., "github")
            or a full module path (e.g., "airbyte_ops_mcp.mcp.github" from __name__).
        resource_list: List of (callable, annotations) tuples to register
        register_fn: Function to call for each registration
    """
    domain_str = domain.value if isinstance(domain, ToolDomain) else domain
    # Normalize to handle both file stems and __name__ module paths
    domain_str = _normalize_domain(domain_str)

    filtered_callables = [
        (func, ann) for func, ann in resource_list if ann.get("domain") == domain_str
    ]

    for callable_fn, callable_annotations in filtered_callables:
        register_fn(app, callable_fn, callable_annotations)


def register_mcp_tools(
    app: FastMCP,
    domain: ToolDomain | str | None = None,
) -> None:
    """Register tools with the FastMCP app, filtered by domain.

    Args:
        app: The FastMCP app instance
        domain: The domain to register for. If not provided, automatically
            derived from the caller's file stem.
    """
    if domain is None:
        domain = _get_caller_file_stem()

    def _register_fn(
        app: FastMCP,
        callable_fn: Callable,
        annotations: dict[str, Any],
    ):
        app.tool(
            callable_fn,
            annotations=annotations,
        )

    _register_mcp_callables(
        app=app,
        domain=domain,
        resource_list=_REGISTERED_TOOLS,
        register_fn=_register_fn,
    )


def register_mcp_prompts(
    app: FastMCP,
    domain: ToolDomain | str | None = None,
) -> None:
    """Register prompt callables with the FastMCP app, filtered by domain.

    Args:
        app: The FastMCP app instance
        domain: The domain to register for. If not provided, automatically
            derived from the caller's file stem.
    """
    if domain is None:
        domain = _get_caller_file_stem()

    def _register_fn(
        app: FastMCP,
        callable_fn: Callable,
        annotations: dict[str, Any],
    ):
        app.prompt(
            name=annotations["name"],
            description=annotations["description"],
        )(callable_fn)

    _register_mcp_callables(
        app=app,
        domain=domain,
        resource_list=_REGISTERED_PROMPTS,
        register_fn=_register_fn,
    )


def register_mcp_resources(
    app: FastMCP,
    domain: ToolDomain | str | None = None,
) -> None:
    """Register resource callables with the FastMCP app, filtered by domain.

    Args:
        app: The FastMCP app instance
        domain: The domain to register for. If not provided, automatically
            derived from the caller's file stem.
    """
    if domain is None:
        domain = _get_caller_file_stem()

    def _register_fn(
        app: FastMCP,
        callable_fn: Callable,
        annotations: dict[str, Any],
    ):
        _ = annotations
        app.resource(
            annotations["uri"],
            description=annotations["description"],
            mime_type=annotations["mime_type"],
        )(callable_fn)

    _register_mcp_callables(
        app=app,
        domain=domain,
        resource_list=_REGISTERED_RESOURCES,
        register_fn=_register_fn,
    )
