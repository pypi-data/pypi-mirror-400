# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
"""GitHub API utilities for user and comment operations.

This module provides utilities for interacting with GitHub's REST API
to retrieve user information and comment details. These utilities are
used by MCP tools for authorization and audit purposes.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from urllib.parse import urlparse

import requests

from airbyte_ops_mcp.github_actions import GITHUB_API_BASE, resolve_github_token


class GitHubCommentParseError(Exception):
    """Raised when a GitHub comment URL cannot be parsed."""


class GitHubUserEmailNotFoundError(Exception):
    """Raised when a GitHub user's public email cannot be found."""


class GitHubAPIError(Exception):
    """Raised when a GitHub API call fails."""


@dataclass(frozen=True)
class GitHubCommentInfo:
    """Information about a GitHub comment and its author."""

    comment_id: int
    """The numeric comment ID."""

    owner: str
    """Repository owner (e.g., 'airbytehq')."""

    repo: str
    """Repository name (e.g., 'oncall')."""

    author_login: str
    """GitHub username of the comment author."""

    author_association: str
    """Author's association with the repo (e.g., 'MEMBER', 'OWNER', 'CONTRIBUTOR')."""

    comment_type: str
    """Type of comment: 'issue_comment' or 'review_comment'."""


@dataclass(frozen=True)
class GitHubUserInfo:
    """Information about a GitHub user."""

    login: str
    """GitHub username."""

    email: str | None
    """Public email address, if set."""

    name: str | None
    """Display name, if set."""


def _parse_github_comment_url(url: str) -> tuple[str, str, int, str]:
    """Parse a GitHub comment URL to extract owner, repo, comment_id, and comment_type.

    Supports two URL formats:
    - Issue/PR timeline comments: https://github.com/{owner}/{repo}/issues/{num}#issuecomment-{id}
    - PR review comments: https://github.com/{owner}/{repo}/pull/{num}#discussion_r{id}

    Args:
        url: GitHub comment URL.

    Returns:
        Tuple of (owner, repo, comment_id, comment_type).
        comment_type is either 'issue_comment' or 'review_comment'.

    Raises:
        GitHubCommentParseError: If the URL cannot be parsed.
    """
    parsed = urlparse(url)

    if parsed.scheme != "https":
        raise GitHubCommentParseError(
            f"Invalid URL scheme: expected 'https', got '{parsed.scheme}'"
        )

    if parsed.netloc != "github.com":
        raise GitHubCommentParseError(
            f"Invalid URL host: expected 'github.com', got '{parsed.netloc}'"
        )

    path_parts = parsed.path.strip("/").split("/")
    if len(path_parts) < 2:
        raise GitHubCommentParseError(
            f"Invalid URL path: expected at least owner/repo, got '{parsed.path}'"
        )

    owner = path_parts[0]
    repo = path_parts[1]
    fragment = parsed.fragment

    issue_comment_match = re.match(r"^issuecomment-(\d+)$", fragment)
    if issue_comment_match:
        comment_id = int(issue_comment_match.group(1))
        return owner, repo, comment_id, "issue_comment"

    review_comment_match = re.match(r"^discussion_r(\d+)$", fragment)
    if review_comment_match:
        comment_id = int(review_comment_match.group(1))
        return owner, repo, comment_id, "review_comment"

    raise GitHubCommentParseError(
        f"Invalid URL fragment: expected '#issuecomment-<id>' or '#discussion_r<id>', "
        f"got '#{fragment}'"
    )


def get_github_comment_info(
    owner: str,
    repo: str,
    comment_id: int,
    comment_type: str,
    token: str | None = None,
) -> GitHubCommentInfo:
    """Fetch comment information from GitHub API.

    Args:
        owner: Repository owner.
        repo: Repository name.
        comment_id: Numeric comment ID.
        comment_type: Either 'issue_comment' or 'review_comment'.
        token: GitHub API token. If None, will be resolved from environment.

    Returns:
        GitHubCommentInfo with comment and author details.

    Raises:
        GitHubAPIError: If the API request fails.
        ValueError: If comment_type is invalid.
    """
    if token is None:
        token = resolve_github_token()

    if comment_type == "issue_comment":
        url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/issues/comments/{comment_id}"
    elif comment_type == "review_comment":
        url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/pulls/comments/{comment_id}"
    else:
        raise ValueError(f"Invalid comment_type: {comment_type}")

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    response = requests.get(url, headers=headers, timeout=30)
    if not response.ok:
        raise GitHubAPIError(
            f"Failed to fetch comment {comment_id} from {owner}/{repo}: "
            f"{response.status_code} {response.text}"
        )

    data = response.json()
    user = data.get("user", {})

    return GitHubCommentInfo(
        comment_id=comment_id,
        owner=owner,
        repo=repo,
        author_login=user.get("login", ""),
        author_association=data.get("author_association", "NONE"),
        comment_type=comment_type,
    )


def get_github_user_info(login: str, token: str | None = None) -> GitHubUserInfo:
    """Fetch user information from GitHub API.

    Args:
        login: GitHub username.
        token: GitHub API token. If None, will be resolved from environment.

    Returns:
        GitHubUserInfo with user details.

    Raises:
        GitHubAPIError: If the API request fails.
    """
    if token is None:
        token = resolve_github_token()

    url = f"{GITHUB_API_BASE}/users/{login}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    response = requests.get(url, headers=headers, timeout=30)
    if not response.ok:
        raise GitHubAPIError(
            f"Failed to fetch user {login}: {response.status_code} {response.text}"
        )

    data = response.json()

    return GitHubUserInfo(
        login=data.get("login", login),
        email=data.get("email"),
        name=data.get("name"),
    )


def get_admin_email_from_approval_comment(approval_comment_url: str) -> str:
    """Derive the admin email from a GitHub approval comment URL.

    This function:
    1. Parses the comment URL to extract owner, repo, and comment ID.
    2. Fetches the comment from GitHub API to get the author's username.
    3. Fetches the user's profile to get their public email.
    4. Validates the email is an @airbyte.io address.

    Args:
        approval_comment_url: GitHub comment URL where approval was given.

    Returns:
        The admin's @airbyte.io email address.

    Raises:
        GitHubCommentParseError: If the URL cannot be parsed.
        GitHubAPIError: If GitHub API calls fail.
        GitHubUserEmailNotFoundError: If the user has no public email or
            the email is not an @airbyte.io address.
    """
    owner, repo, comment_id, comment_type = _parse_github_comment_url(
        approval_comment_url
    )

    comment_info = get_github_comment_info(owner, repo, comment_id, comment_type)

    user_info = get_github_user_info(comment_info.author_login)

    if not user_info.email:
        raise GitHubUserEmailNotFoundError(
            f"GitHub user '{comment_info.author_login}' does not have a public email set. "
            f"To use this tool, the approver must have a public @airbyte.io email "
            f"configured on their GitHub profile (Settings > Public email)."
        )

    if not user_info.email.endswith("@airbyte.io"):
        raise GitHubUserEmailNotFoundError(
            f"GitHub user '{comment_info.author_login}' has public email '{user_info.email}' "
            f"which is not an @airbyte.io address. Only @airbyte.io emails are authorized "
            f"for admin operations."
        )

    return user_info.email
