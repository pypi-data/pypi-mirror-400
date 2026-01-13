"""
Pulumi Infrastructure as Code for Airbyte's Sentry Configuration.

This module manages multiple Sentry projects for Airbyte, including teams, alerts,
integrations, and fingerprint rules.

SETUP:
------
Before running `pulumi up`, generate the Sentry provider SDK:
    pulumi package add terraform-provider jianyuan/sentry

This uses the Terraform Sentry provider directly (v0.14.5) which supports
fingerprinting_rules and grouping_enhancements on SentryProject resources.

CONFIGURATION:
--------------
Business logic configuration is stored in Pulumi.{stack}.yaml:
- Per-project configuration:
  - Teams list
  - Fingerprint rules
  - Grouping enhancements

Static values (organization, project slugs) are Python constants in this file.
See Pulumi.prod.yaml for the production configuration.

IMPORTANT NOTES:
----------------
1. Fingerprint rules ARE managed by this configuration via the fingerprinting_rules
   property on SentryProject. Changes to Pulumi.prod.yaml will be applied to Sentry.

2. Ownership rules are configured in the Sentry UI and determine alert routing.

3. The GitHub integration (sentry.yml workflow) is managed separately in:
   https://github.com/airbytehq/workflow-actions

4. Teams are managed separately in Sentry UI and referenced by slug in projects.

IMPORTING EXISTING RESOURCES:
-----------------------------
To import existing Sentry resources into Pulumi state, use the `pulumi import` command.

Import a team:
    pulumi import sentry:index/team:Team <resource_name> airbytehq/<team-slug>

Import a project:
    pulumi import sentry:index/project:Project <alias> airbytehq/<slug>

Import an alert rule:
    pulumi import sentry:index/issueAlert:IssueAlert <name> airbytehq/<project-slug>/<rule-id>
"""

from typing import Any

import pulumi

# Note: The sentry module is generated locally by running:
#   pulumi package add terraform-provider jianyuan/sentry
# This creates sdks/sentry/ with full support for fingerprinting_rules
import pulumi_sentry as sentry
from pulumi import Config

# Type alias for output variables map
OutputVarsMap = dict[str, Any]

# =============================================================================
# CONFIGURATION - All values loaded from Pulumi.{stack}.yaml
# =============================================================================
CONFIG = Config("airbyte-sentry")

# Organization (constant - unlikely to change)
ORGANIZATION = "airbytehq"

# Project constants (aliases for Pulumi URN, IDs are the actual Sentry project slugs)
CONNECTOR_INCIDENTS_PROJECT_ALIAS = "connector-incidents"
CONNECTOR_INCIDENTS_PROJECT_ID = "connector-incident-management"
CONNECTOR_CI_PROJECT_ALIAS = "connector-ci"
CONNECTOR_CI_PROJECT_ID = "connectors-ci"

# Projects configuration (each project has its own settings)
# Structure: { "alias": { "teams": [...], "fingerprinting_rules": "...", ... }, ... }
PROJECTS_CONFIG = CONFIG.require_object("projects")


# =============================================================================
# PROJECTS - Explicitly defined for each Sentry project
# =============================================================================
# Each project is defined in Pulumi.{stack}.yaml with an alias (key) and config.
# See GitHub issue #150 for fingerprint rule improvement suggestions.


def define_connector_incidents_project() -> tuple[sentry.Project, OutputVarsMap]:
    """Define the connector-incidents project for connector error monitoring.

    Returns:
        Tuple of (project resource, output variables map)

    Raises:
        KeyError: If a required config key is missing from Pulumi.{stack}.yaml.
    """
    if CONNECTOR_INCIDENTS_PROJECT_ALIAS not in PROJECTS_CONFIG:
        raise KeyError(
            f"Missing project config for '{CONNECTOR_INCIDENTS_PROJECT_ALIAS}'. "
            f"Add 'airbyte-sentry:projects:{CONNECTOR_INCIDENTS_PROJECT_ALIAS}:' section to Pulumi.{{stack}}.yaml"
        )
    cfg = PROJECTS_CONFIG[CONNECTOR_INCIDENTS_PROJECT_ALIAS]
    required_keys = [
        "platform",
        "teams",
        "fingerprinting_rules",
        "grouping_enhancements",
    ]
    missing = [k for k in required_keys if k not in cfg]
    if missing:
        raise KeyError(
            f"Missing required config key(s) for '{CONNECTOR_INCIDENTS_PROJECT_ALIAS}': {missing}. "
            f"Add under 'airbyte-sentry:projects:{CONNECTOR_INCIDENTS_PROJECT_ALIAS}:' in Pulumi.{{stack}}.yaml"
        )
    project = sentry.Project(
        CONNECTOR_INCIDENTS_PROJECT_ALIAS,  # Resource name (Pulumi URN)
        organization=ORGANIZATION,
        name=CONNECTOR_INCIDENTS_PROJECT_ID,
        slug=CONNECTOR_INCIDENTS_PROJECT_ID,
        platform=cfg["platform"],
        teams=cfg["teams"],
        # Note: digests_max_delay and digests_min_delay are not set here because
        # the provider doesn't read them during import, causing spurious diffs.
        # These settings are managed via Sentry UI instead.
        fingerprinting_rules=cfg["fingerprinting_rules"],
        grouping_enhancements=cfg["grouping_enhancements"],
        opts=pulumi.ResourceOptions(
            protect=True,  # Prevent accidental deletion
            import_=f"{ORGANIZATION}/{CONNECTOR_INCIDENTS_PROJECT_ID}",  # Import existing project
        ),
    )
    outputs: OutputVarsMap = {
        "projects.connector-incidents.slug": project.slug,
        "projects.connector-incidents.url": project.slug.apply(
            lambda s: f"https://{ORGANIZATION}.sentry.io/projects/{s}/"
        ),
        "projects.connector-incidents.issue_grouping_url": project.slug.apply(
            lambda s: f"https://{ORGANIZATION}.sentry.io/settings/projects/{s}/issue-grouping/"
        ),
    }
    return project, outputs


def define_connector_ci_project() -> tuple[sentry.Project, OutputVarsMap]:
    """Define the connector-ci project for CI/CD pipeline monitoring.

    Returns:
        Tuple of (project resource, output variables map)

    Raises:
        KeyError: If a required config key is missing from Pulumi.{stack}.yaml.
    """
    if CONNECTOR_CI_PROJECT_ALIAS not in PROJECTS_CONFIG:
        raise KeyError(
            f"Missing project config for '{CONNECTOR_CI_PROJECT_ALIAS}'. "
            f"Add 'airbyte-sentry:projects:{CONNECTOR_CI_PROJECT_ALIAS}:' section to Pulumi.{{stack}}.yaml"
        )
    cfg = PROJECTS_CONFIG[CONNECTOR_CI_PROJECT_ALIAS]
    required_keys = [
        "platform",
        "teams",
        "fingerprinting_rules",
        "grouping_enhancements",
    ]
    missing = [k for k in required_keys if k not in cfg]
    if missing:
        raise KeyError(
            f"Missing required config key(s) for '{CONNECTOR_CI_PROJECT_ALIAS}': {missing}. "
            f"Add under 'airbyte-sentry:projects:{CONNECTOR_CI_PROJECT_ALIAS}:' in Pulumi.{{stack}}.yaml"
        )
    project = sentry.Project(
        CONNECTOR_CI_PROJECT_ALIAS,  # Resource name (Pulumi URN)
        organization=ORGANIZATION,
        name=CONNECTOR_CI_PROJECT_ID,
        slug=CONNECTOR_CI_PROJECT_ID,
        platform=cfg["platform"],
        teams=cfg["teams"],
        # Note: digests_max_delay and digests_min_delay are not set here because
        # the provider doesn't read them during import, causing spurious diffs.
        # These settings are managed via Sentry UI instead.
        fingerprinting_rules=cfg["fingerprinting_rules"],
        grouping_enhancements=cfg["grouping_enhancements"],
        opts=pulumi.ResourceOptions(
            protect=True,  # Prevent accidental deletion
            import_=f"{ORGANIZATION}/{CONNECTOR_CI_PROJECT_ID}",  # Import existing project
        ),
    )
    outputs: OutputVarsMap = {
        "projects.connector-ci.slug": project.slug,
        "projects.connector-ci.url": project.slug.apply(
            lambda s: f"https://{ORGANIZATION}.sentry.io/projects/{s}/"
        ),
        "projects.connector-ci.issue_grouping_url": project.slug.apply(
            lambda s: f"https://{ORGANIZATION}.sentry.io/settings/projects/{s}/issue-grouping/"
        ),
    }
    return project, outputs


# =============================================================================
# ALERT RULES - Issue alert rules for connector-incident-management project
# =============================================================================
# Alert rules are defined in Python code (not YAML) as they contain complex
# conditions, filters, and actions that are better expressed programmatically.


def define_connector_incidents_alert_rules(
    project: sentry.Project,
) -> list[sentry.IssueAlert]:
    """Define alert rules for the connector-incidents project.

    These rules were imported from Sentry on 2025-12-22 and match the existing
    production configuration. Uses v2 API fields (structured objects) for better
    readability and type safety.

    Args:
        project: The connector-incidents project resource.

    Returns:
        List of IssueAlert resources.
    """
    return [
        # Alert: API Connectors P0 (SDM, 10+ workspaces affected) (ID: 15976921)
        sentry.IssueAlert(
            "alert-api-connectors-p0-sdm",
            organization=ORGANIZATION,
            project=CONNECTOR_INCIDENTS_PROJECT_ID,
            name="API Connectors P0 (SDM, 10+ workspaces affected)",
            action_match="any",
            filter_match="all",
            frequency=1440,
            owner="team:1838478",
            conditions_v2s=[
                sentry.IssueAlertConditionsV2Args(
                    event_unique_user_frequency=sentry.IssueAlertConditionsV2EventUniqueUserFrequencyArgs(
                        comparison_type="count",
                        interval="1d",
                        value=9,
                    ),
                ),
            ],
            filters_v2s=[
                sentry.IssueAlertFiltersV2Args(
                    tagged_event=sentry.IssueAlertFiltersV2TaggedEventArgs(
                        key="failure_origin",
                        match="EQUAL",
                        value="source",
                    ),
                ),
                sentry.IssueAlertFiltersV2Args(
                    tagged_event=sentry.IssueAlertFiltersV2TaggedEventArgs(
                        key="connector_repository",
                        match="CONTAINS",
                        value="source-declarative-manifest",
                    ),
                ),
            ],
            actions_v2s=[
                sentry.IssueAlertActionsV2Args(
                    pagerduty_notify_service=sentry.IssueAlertActionsV2PagerdutyNotifyServiceArgs(
                        account="139284",
                        service="10250",
                        severity="default",
                    ),
                ),
                sentry.IssueAlertActionsV2Args(
                    slack_notify_service=sentry.IssueAlertActionsV2SlackNotifyServiceArgs(
                        channel="#oncall-bots",
                        workspace="139867",
                    ),
                ),
            ],
            opts=pulumi.ResourceOptions(
                protect=True,
                import_=f"{ORGANIZATION}/{CONNECTOR_INCIDENTS_PROJECT_ID}/15976921",
            ),
        ),
        # Alert: DB Source Connectors P0 (Beta, affecting more than 5 workspaces) (ID: 14868739)
        sentry.IssueAlert(
            "alert-db-source-connectors-p0-beta",
            organization=ORGANIZATION,
            project=CONNECTOR_INCIDENTS_PROJECT_ID,
            name="DB Source Connectors P0 (Beta, affecting more than 5 workspaces)",
            action_match="any",
            filter_match="all",
            frequency=1440,
            owner="team:1199001",
            conditions_v2s=[
                sentry.IssueAlertConditionsV2Args(
                    event_unique_user_frequency=sentry.IssueAlertConditionsV2EventUniqueUserFrequencyArgs(
                        comparison_type="count",
                        interval="1d",
                        value=5,
                    ),
                ),
            ],
            filters_v2s=[
                sentry.IssueAlertFiltersV2Args(
                    tagged_event=sentry.IssueAlertFiltersV2TaggedEventArgs(
                        key="connector_release_stage",
                        match="NOT_IN",
                        value="alpha,generally_available,custom",
                    ),
                ),
                sentry.IssueAlertFiltersV2Args(
                    assigned_to=sentry.IssueAlertFiltersV2AssignedToArgs(
                        target_type="Team",
                        target_identifier="4509563160690689",
                    ),
                ),
                sentry.IssueAlertFiltersV2Args(
                    tagged_event=sentry.IssueAlertFiltersV2TaggedEventArgs(
                        key="failure_origin",
                        match="EQUAL",
                        value="source",
                    ),
                ),
            ],
            actions_v2s=[
                sentry.IssueAlertActionsV2Args(
                    pagerduty_notify_service=sentry.IssueAlertActionsV2PagerdutyNotifyServiceArgs(
                        account="139284",
                        service="238987",
                        severity="default",
                    ),
                ),
                sentry.IssueAlertActionsV2Args(
                    slack_notify_service=sentry.IssueAlertActionsV2SlackNotifyServiceArgs(
                        channel="#oncall-bots",
                        workspace="139867",
                    ),
                ),
            ],
            opts=pulumi.ResourceOptions(
                protect=True,
                import_=f"{ORGANIZATION}/{CONNECTOR_INCIDENTS_PROJECT_ID}/14868739",
            ),
        ),
        # Alert: DB Source Connectors P0 (GA, affecting more than 5 workspaces) (ID: 14868697)
        sentry.IssueAlert(
            "alert-db-source-connectors-p0-ga",
            organization=ORGANIZATION,
            project=CONNECTOR_INCIDENTS_PROJECT_ID,
            name="DB Source Connectors P0 (GA, affecting more than 5 workspaces)",
            action_match="any",
            filter_match="all",
            frequency=1440,
            owner="team:1199001",
            conditions_v2s=[
                sentry.IssueAlertConditionsV2Args(
                    event_unique_user_frequency=sentry.IssueAlertConditionsV2EventUniqueUserFrequencyArgs(
                        comparison_type="count",
                        interval="1d",
                        value=5,
                    ),
                ),
            ],
            filters_v2s=[
                sentry.IssueAlertFiltersV2Args(
                    tagged_event=sentry.IssueAlertFiltersV2TaggedEventArgs(
                        key="connector_release_stage",
                        match="NOT_IN",
                        value="alpha,beta,custom",
                    ),
                ),
                sentry.IssueAlertFiltersV2Args(
                    assigned_to=sentry.IssueAlertFiltersV2AssignedToArgs(
                        target_type="Team",
                        target_identifier="4509563160690689",
                    ),
                ),
                sentry.IssueAlertFiltersV2Args(
                    tagged_event=sentry.IssueAlertFiltersV2TaggedEventArgs(
                        key="failure_origin",
                        match="EQUAL",
                        value="source",
                    ),
                ),
            ],
            actions_v2s=[
                sentry.IssueAlertActionsV2Args(
                    pagerduty_notify_service=sentry.IssueAlertActionsV2PagerdutyNotifyServiceArgs(
                        account="139284",
                        service="238987",
                        severity="default",
                    ),
                ),
                sentry.IssueAlertActionsV2Args(
                    slack_notify_service=sentry.IssueAlertActionsV2SlackNotifyServiceArgs(
                        channel="#oncall-bots",
                        workspace="139867",
                    ),
                ),
            ],
            opts=pulumi.ResourceOptions(
                protect=True,
                import_=f"{ORGANIZATION}/{CONNECTOR_INCIDENTS_PROJECT_ID}/14868697",
            ),
        ),
        # Alert: Destination Connectors P0 (GA, affecting more than 5 workspaces) (ID: 14866113)
        sentry.IssueAlert(
            "alert-destination-connectors-p0-ga",
            organization=ORGANIZATION,
            project=CONNECTOR_INCIDENTS_PROJECT_ID,
            name="Destination Connectors P0 (GA, affecting more than 5 workspaces)",
            action_match="any",
            filter_match="all",
            frequency=1440,
            owner="team:1199001",
            conditions_v2s=[
                sentry.IssueAlertConditionsV2Args(
                    event_unique_user_frequency=sentry.IssueAlertConditionsV2EventUniqueUserFrequencyArgs(
                        comparison_type="count",
                        interval="1d",
                        value=5,
                    ),
                ),
            ],
            filters_v2s=[
                sentry.IssueAlertFiltersV2Args(
                    tagged_event=sentry.IssueAlertFiltersV2TaggedEventArgs(
                        key="connector_release_stage",
                        match="NOT_IN",
                        value="alpha,beta,custom",
                    ),
                ),
                sentry.IssueAlertFiltersV2Args(
                    assigned_to=sentry.IssueAlertFiltersV2AssignedToArgs(
                        target_type="Team",
                        target_identifier="1838479",
                    ),
                ),
                sentry.IssueAlertFiltersV2Args(
                    tagged_event=sentry.IssueAlertFiltersV2TaggedEventArgs(
                        key="failure_origin",
                        match="NOT_EQUAL",
                        value="source",
                    ),
                ),
                sentry.IssueAlertFiltersV2Args(
                    tagged_event=sentry.IssueAlertFiltersV2TaggedEventArgs(
                        key="stacktrace_platform",
                        match="NOT_EQUAL",
                        value="python",
                    ),
                ),
            ],
            actions_v2s=[
                sentry.IssueAlertActionsV2Args(
                    pagerduty_notify_service=sentry.IssueAlertActionsV2PagerdutyNotifyServiceArgs(
                        account="139284",
                        service="238752",
                        severity="default",
                    ),
                ),
                sentry.IssueAlertActionsV2Args(
                    slack_notify_service=sentry.IssueAlertActionsV2SlackNotifyServiceArgs(
                        channel="#move-sentry-alerts",
                        workspace="139867",
                    ),
                ),
                sentry.IssueAlertActionsV2Args(
                    slack_notify_service=sentry.IssueAlertActionsV2SlackNotifyServiceArgs(
                        channel="#dev-platform-move-alerts",
                        workspace="139867",
                    ),
                ),
            ],
            opts=pulumi.ResourceOptions(
                protect=True,
                import_=f"{ORGANIZATION}/{CONNECTOR_INCIDENTS_PROJECT_ID}/14866113",
            ),
        ),
        # Alert: API Connectors P0 (10+ workspaces affected) (ID: 11478402)
        sentry.IssueAlert(
            "alert-api-connectors-p0",
            organization=ORGANIZATION,
            project=CONNECTOR_INCIDENTS_PROJECT_ID,
            name="API Connectors P0 (10+ workspaces affected)",
            action_match="any",
            filter_match="none",
            frequency=1440,
            owner="team:1838478",
            conditions_v2s=[
                sentry.IssueAlertConditionsV2Args(
                    event_unique_user_frequency=sentry.IssueAlertConditionsV2EventUniqueUserFrequencyArgs(
                        comparison_type="count",
                        interval="1d",
                        value=9,
                    ),
                ),
            ],
            filters_v2s=[
                sentry.IssueAlertFiltersV2Args(
                    assigned_to=sentry.IssueAlertFiltersV2AssignedToArgs(
                        target_type="Team",
                        target_identifier="1838479",
                    ),
                ),
                sentry.IssueAlertFiltersV2Args(
                    tagged_event=sentry.IssueAlertFiltersV2TaggedEventArgs(
                        key="connector_internal_support_level",
                        match="EQUAL",
                        value="100",
                    ),
                ),
                sentry.IssueAlertFiltersV2Args(
                    tagged_event=sentry.IssueAlertFiltersV2TaggedEventArgs(
                        key="connector_internal_support_level",
                        match="NOT_SET",
                        value="custom",
                    ),
                ),
                sentry.IssueAlertFiltersV2Args(
                    tagged_event=sentry.IssueAlertFiltersV2TaggedEventArgs(
                        key="connector_internal_support_level",
                        match="EQUAL",
                        value="200",
                    ),
                ),
            ],
            actions_v2s=[
                sentry.IssueAlertActionsV2Args(
                    pagerduty_notify_service=sentry.IssueAlertActionsV2PagerdutyNotifyServiceArgs(
                        account="139284",
                        service="10250",
                        severity="default",
                    ),
                ),
                sentry.IssueAlertActionsV2Args(
                    slack_notify_service=sentry.IssueAlertActionsV2SlackNotifyServiceArgs(
                        channel="#oncall-bots",
                        workspace="139867",
                    ),
                ),
            ],
            opts=pulumi.ResourceOptions(
                protect=True,
                import_=f"{ORGANIZATION}/{CONNECTOR_INCIDENTS_PROJECT_ID}/11478402",
            ),
        ),
    ]


# =============================================================================
# MAIN - Entry point for Pulumi
# =============================================================================


def main() -> None:
    """Main entry point for Pulumi configuration."""
    # Create projects and collect outputs
    connector_incidents_project, connector_incidents_outputs = (
        define_connector_incidents_project()
    )
    _, connector_ci_outputs = define_connector_ci_project()

    # Create alert rules for connector-incidents project
    # Note: Alert resources are created for side effects; return value not needed
    define_connector_incidents_alert_rules(connector_incidents_project)

    # Export organization-level outputs
    pulumi.export("organization", ORGANIZATION)
    pulumi.export("alert_rules_url", f"https://{ORGANIZATION}.sentry.io/alerts/rules/")

    # Export combined project outputs
    all_outputs: OutputVarsMap = {**connector_incidents_outputs, **connector_ci_outputs}
    for key, value in all_outputs.items():
        pulumi.export(key, value)


# Run main when executed by Pulumi
main()
