# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
"""CLI commands for GitHub operations.

Commands:
    airbyte-ops gh workflow status - Check GitHub Actions workflow status
    airbyte-ops gh workflow trigger - Trigger a GitHub Actions CI workflow
"""

from __future__ import annotations

import json
import time
from typing import Annotated

from cyclopts import App, Parameter

from airbyte_ops_mcp.cli._base import app
from airbyte_ops_mcp.cli._shared import exit_with_error, print_json
from airbyte_ops_mcp.mcp.github_actions import (
    check_ci_workflow_status,
    trigger_ci_workflow,
)

# Create the gh sub-app
gh_app = App(name="gh", help="GitHub operations.")
app.command(gh_app)

# Create the workflow sub-app under gh
workflow_app = App(name="workflow", help="GitHub Actions workflow operations.")
gh_app.command(workflow_app)


@workflow_app.command(name="status")
def workflow_status(
    url: Annotated[
        str | None,
        Parameter(
            help="Full GitHub Actions workflow run URL "
            "(e.g., 'https://github.com/owner/repo/actions/runs/12345')."
        ),
    ] = None,
    owner: Annotated[
        str | None,
        Parameter(help="Repository owner (e.g., 'airbytehq')."),
    ] = None,
    repo: Annotated[
        str | None,
        Parameter(help="Repository name (e.g., 'airbyte')."),
    ] = None,
    run_id: Annotated[
        int | None,
        Parameter(help="Workflow run ID."),
    ] = None,
) -> None:
    """Check the status of a GitHub Actions workflow run.

    Provide either --url OR all of (--owner, --repo, --run-id).
    """
    # Validate input parameters
    if url:
        if owner or repo or run_id:
            exit_with_error(
                "Cannot specify --url together with --owner/--repo/--run-id. "
                "Use either --url OR the component parts."
            )
    elif not (owner and repo and run_id):
        exit_with_error(
            "Must provide either --url OR all of (--owner, --repo, --run-id)."
        )

    result = check_ci_workflow_status(
        workflow_url=url,
        owner=owner,
        repo=repo,
        run_id=run_id,
    )
    print_json(result.model_dump())


@workflow_app.command(name="trigger")
def workflow_trigger(
    owner: Annotated[
        str,
        Parameter(help="Repository owner (e.g., 'airbytehq')."),
    ],
    repo: Annotated[
        str,
        Parameter(help="Repository name (e.g., 'airbyte')."),
    ],
    workflow_file: Annotated[
        str,
        Parameter(help="Workflow file name (e.g., 'connector-regression-test.yml')."),
    ],
    workflow_definition_ref: Annotated[
        str | None,
        Parameter(
            help="Branch name or PR number for the workflow definition to use. "
            "If a PR number is provided, it resolves to the PR's head branch name. "
            "Defaults to 'main' if not specified."
        ),
    ] = None,
    inputs: Annotated[
        str | None,
        Parameter(
            help='Workflow inputs as a JSON string (e.g., \'{"key": "value"}\').'
        ),
    ] = None,
    wait: Annotated[
        bool,
        Parameter(help="Wait for the workflow to complete before returning."),
    ] = False,
    wait_seconds: Annotated[
        int,
        Parameter(
            help="Maximum seconds to wait for workflow completion (default: 600)."
        ),
    ] = 600,
) -> None:
    """Trigger a GitHub Actions CI workflow via workflow_dispatch.

    This command triggers a workflow in any GitHub repository that has workflow_dispatch
    enabled. It resolves PR numbers to branch names automatically.
    """
    # Parse inputs JSON if provided
    parsed_inputs: dict[str, str] | None = None
    if inputs:
        try:
            parsed_inputs = json.loads(inputs)
        except json.JSONDecodeError as e:
            exit_with_error(f"Invalid JSON for --inputs: {e}")

    # Trigger the workflow
    result = trigger_ci_workflow(
        owner=owner,
        repo=repo,
        workflow_file=workflow_file,
        workflow_definition_ref=workflow_definition_ref,
        inputs=parsed_inputs,
    )

    print_json(result.model_dump())

    # If wait is enabled and we have a run_id, poll for completion
    if wait and result.run_id:
        print(f"\nWaiting for workflow to complete (timeout: {wait_seconds}s)...")
        start_time = time.time()
        poll_interval = 10  # seconds

        while time.time() - start_time < wait_seconds:
            status_result = check_ci_workflow_status(
                owner=owner,
                repo=repo,
                run_id=result.run_id,
            )

            if status_result.status == "completed":
                print(
                    f"\nWorkflow completed with conclusion: {status_result.conclusion}"
                )
                print_json(status_result.model_dump())
                return

            elapsed = int(time.time() - start_time)
            print(f"  Status: {status_result.status} (elapsed: {elapsed}s)")
            time.sleep(poll_interval)

        print(f"\nTimeout reached after {wait_seconds}s. Workflow still running.")
        # Print final status
        final_status = check_ci_workflow_status(
            owner=owner,
            repo=repo,
            run_id=result.run_id,
        )
        print_json(final_status.model_dump())
