# Sentry Configuration at Airbyte

This document describes how Sentry is configured and used at Airbyte for monitoring connector errors in production.

## Table of Contents

- [Overview](#overview)
- [How Sentry Works at Airbyte](#how-sentry-works-at-airbyte)
- [Configuration](#configuration)
  - [Environment Variables](#environment-variables)
  - [Cloud Deployment](#cloud-deployment)
- [Error Types and Filtering](#error-types-and-filtering)
- [Grouping Rules](#grouping-rules)
- [Ownership Rules](#ownership-rules)
- [Alerts](#alerts)
  - [P0 Alerts](#p0-alerts)
  - [Stack Trace Parsing Failure Alerts](#stack-trace-parsing-failure-alerts)
- [GitHub Integration](#github-integration)
- [Monitoring Systems](#monitoring-systems)
- [Related Notion Documentation](#related-notion-documentation)

## Overview

Sentry is used by Airbyte's connector team to monitor connector errors in production. It automatically captures and reports failures that originate from source and destination trace messages, helping identify issues before customers need to open support tickets.

**Key Points:**

- Only **system errors** (failures requiring bugfixes or on-call intervention) are reported to Sentry
- Errors are automatically captured from connectors using recent versions of the CDK or java-base
- All errors are reported to the [connector-incident-management](https://sentry.io/organizations/airbytehq/projects/connector-incident-management) Sentry project

For more details, see the [main Sentry documentation page](https://www.notion.so/Sentry-Configuration-at-Airbyte-9fdc95e5ed4d429e9fd889960bdb5b33) in Notion.

## How Sentry Works at Airbyte

Airbyte can be configured to report failures that originate from source and destination trace messages to Sentry. This includes unexpected errors encountered during:

- Spec operations
- Check connection operations
- Discover schema operations
- Reading source data
- Writing destination data
- Normalization

All connectors that use a recent version of the CDK or java-base emit these errors automatically by using `AirbyteTraceMessages` via uncaught exception handlers.

### Error Reporting Flow

```log
Connector Error → AirbyteErrorTraceMessage → Data Plane Worker → Platform Backend → Sentry
```

The platform sends error messages to Sentry for monitoring purposes. For detailed information about how errors flow through the system, see [Errors in Airbyte](https://www.notion.so/cefeae34698745a2aca9c3d967be81c5).

## Configuration

### Environment Variables

Connector error reporting functionality can be enabled by setting the following environment variables on the server and workers:

- `JOB_ERROR_REPORTING_STRATEGY`: Set to `sentry` (defaults to `logging`)
- `JOB_ERROR_REPORTING_SENTRY_DSN`: Set to the Sentry project's DSN (see [Sentry DSN documentation](https://docs.sentry.io/product/sentry-basics/dsn-explainer/))

### Cloud Deployment

For Airbyte Cloud environments, Sentry error reporting is configured as part of the [helm values template](https://github.com/airbytehq/airbyte-cloud/blob/4011324ade18bb95fc3efc7df3ab718d2ef1b9c0/tools/helm-values-builder/templates/gcp_helm_values.yaml.j2#L15-L16) to enable Sentry error reporting on production environments.

## Error Types and Filtering

Only errors with a `failureType` of **system_error** are reported to Sentry. These are errors that require either a bugfix or the intervention of on-call to be resolved.

Other failure types (`config_error` and `transient_error`) are not sent to Sentry as they don't indicate issues in the connector code itself.

For comprehensive information about error types and the error message flow, see [Errors in Airbyte](https://www.notion.so/cefeae34698745a2aca9c3d967be81c5).

## Grouping Rules

To improve the grouping behavior of errors reported to Sentry, custom [Stack Trace Rules](https://docs.sentry.io/product/data-management-settings/event-grouping/stack-trace-rules/) have been configured:

```plaintext
# java: mark everything from io.airbyte.* as in-app
stack.module:io.airbyte.* +app

# python: mark everything in a folder with airbyte in it as in-app (/airbyte/integration_code, */airbyte_cdk/*)
stack.abs_path:**/airbyte*/** +app
```

These rules ensure that Airbyte-specific code is properly identified as "in-app" frames, which helps Sentry group related errors together more accurately.

**Configuration Location:** [Sentry Issue Grouping Settings](https://sentry.io/settings/airbytehq/projects/connector-incident-management/issue-grouping/)

For more information about in-app frames, see [Sentry's stacktrace documentation](https://develop.sentry.dev/sdk/event-payloads/stacktrace/).

## Ownership Rules

[Issue ownership](https://docs.sentry.io/product/issues/issue-owners/) is used to determine which team should receive alerts for a given issue. Sentry automatically sets an issue's assigned team based on these rules:

```docker
# Auto assign issue owners in order to forward the alerts to the relevant teams
# in order to not miss anything, the alerts for api connectors should be set up as [NOT db-connectors]

# python issues should get auto assigned to api connectors team
tags.stacktrace_platform:python #api-connectors

# java and normalization failures should go to databases team
# order is important here, as python errors in normalization will be routed to dbs
tags.stacktrace_platform:java #db-connectors
tags.failure_origin:normalization #db-connectors
```

**Team Routing:**

- API connector issues → [#api-connectors](https://sentry.io/settings/airbytehq/teams/api-connectors/members/) team
- DB connector and normalization issues → [#db-connectors](https://sentry.io/settings/airbytehq/teams/db-connectors/members/) team

**Note:** These teams are only used for alert routing. Airbyte employees don't need to be direct members of these teams.

## Alerts

[Alerts](https://docs.sentry.io/product/alerts/) are configured through the Sentry UI and can be viewed on the [alerts rules page](https://sentry.io/organizations/airbytehq/alerts/rules).

### P0 Alerts

P0 alerts trigger both a PagerDuty alert and a message in the `#oncall` Slack channel when:

- A **Generally Available (GA) connector** issue is affecting more than 2 workspaces within 24h
- A **Beta connector** issue is affecting more than 5 workspaces within 24h

These alerts are split by connector type to ensure the right PagerDuty service is paged based on the assigned team (as determined by [Ownership Rules](#ownership-rules)).

For more information on handling PagerDuty incidents, see:

- [PagerDuty Incidents](https://www.notion.so/31b53468916541ebbbbed9d6a52b60a5)
- [All things PagerDuty](https://www.notion.so/018bb3ae8ef14fc2ba073f96c7e182fd)

### Stack Trace Parsing Failure Alerts

These alerts notify Connector Operations (via the `#dev-connectors-ops` Slack channel) when a stack trace wasn't able to be parsed correctly. This indicates that the parsing logic needs improvement.

## GitHub Integration

Sentry serves primarily as a system for discovering errors in production and alerting when things go wrong. The main entry point for communication about these errors is in the [OnCall GitHub repository](https://github.com/airbytehq/oncall).

### Sentry-GitHub Sync

A custom integration in the [workflow-actions](https://github.com/airbytehq/workflow-actions) repository syncs Sentry and GitHub issues together.

The [sentry.yml](https://github.com/airbytehq/workflow-actions/actions/workflows/sentry.yml) GitHub Action runs every hour to process all unresolved Sentry issues from the `connector-incident-management` project. For each unresolved Sentry Issue, it:

1. **If the Sentry Issue is NOT linked to a GitHub Issue:**
   - Creates a new GitHub issue

2. **If the Sentry Issue IS linked to a GitHub Issue:**
   - If the linked GitHub issue is closed and new events have NOT occurred: Resolves the Sentry Issue
   - If the linked GitHub Issue is closed and new events HAVE occurred: Creates a new GitHub Issue and replaces the link

3. **For all issues:**
   - Posts or updates a comment with the latest list of affected workspaces

This integration ensures that all production connector errors are tracked and managed through the oncall process. For more information about the oncall process, see [All Teams Oncall Issues Process](https://www.notion.so/42034cac09d5434e8ddb4cff1718742d).

## Monitoring Systems

Sentry is one of three monitoring systems that send alerts to on-call engineers via PagerDuty:

1. **Datadog** - [Datadog Monitors](https://app.datadoghq.com/monitors/manage)
2. **Sentry** - [Sentry Alert Rules](https://sentry.io/organizations/airbytehq/alerts/rules/)
3. **GCP Cloud Monitoring** - [GCP Alerting Policies](https://console.cloud.google.com/monitoring/alerting/policies?project=prod-ab-cloud-proj)

For more information, see [Pagerduty Incidents](https://www.notion.so/31b53468916541ebbbbed9d6a52b60a5).

## Infrastructure as Code (Pulumi)

Sentry configuration can be managed as Infrastructure as Code using Pulumi. The Pulumi project is located in this directory (`infra/sentry/`).

### What Can Be Managed via Pulumi

- **Projects** - Project settings including fingerprint rules and grouping enhancements
- **Issue Alerts** - Alert rules with conditions, filters, and actions
- **Metric Alerts** - Metric-based alert rules
- **Dashboards** - Custom dashboards
- **Keys** - DSN keys

### What Is Managed via Sentry UI

These are managed directly in the [Sentry UI](https://sentry.io/settings/airbytehq/):

- **Teams** - Team membership and permissions (referenced by slug in Pulumi, but managed in UI)
- **Ownership Rules** - Team assignment rules for alert routing
- **Inbound Filters** - Event filtering before ingestion

### Getting Started with Pulumi

To set up the Pulumi environment:

1. Install Pulumi CLI (>= 3.147.0): https://www.pulumi.com/docs/install/
2. Generate the Sentry SDK: `pulumi package add terraform-provider jianyuan/sentry`
3. Initialize the stack: `pulumi stack init prod`
4. Set the Sentry token: `pulumi config set sentry:token --secret <your-token>`
5. Preview changes: `pulumi preview`

For Sentry auth tokens, create an internal integration at https://airbytehq.sentry.io/settings/developer-settings/

### Known Spam Issues

See [GitHub Issue #150](https://github.com/airbytehq/airbyte-ops-mcp/issues/150) for analysis of recurring spam issues and recommended fingerprint fixes.

## Related Notion Documentation

### Primary Documentation

- [Sentry at Airbyte](https://www.notion.so/9fdc95e5ed4d429e9fd889960bdb5b33) - Main Sentry configuration and setup documentation
- [Errors in Airbyte](https://www.notion.so/cefeae34698745a2aca9c3d967be81c5) - Comprehensive guide to error handling and flow in Airbyte
- [Understanding a Sentry Issue](https://www.notion.so/c3596bf83b3c4372ab005495f89a9e5b) - Guide to interpreting Sentry issues

### Monitoring & Alerts

- [Monitoring (Parent Page)](https://www.notion.so/451234ea9bab451ca1922ce884eded7a) - Overview of monitoring at Airbyte
- [Pagerduty Incidents](https://www.notion.so/31b53468916541ebbbbed9d6a52b60a5) - How PagerDuty incidents work with Sentry
- [All things PagerDuty](https://www.notion.so/018bb3ae8ef14fc2ba073f96c7e182fd) - Complete PagerDuty documentation

### Oncall Process

- [All Teams Oncall Issues Process](https://www.notion.so/42034cac09d5434e8ddb4cff1718742d) - Complete oncall workflow and issue handling
- [OnCall GitHub Repository](https://github.com/airbytehq/oncall) - Where Sentry issues are tracked and managed

### Additional Resources

- [Datadog Monitoring](https://www.notion.so/e18111812b104719932c7206bb7b0ba5) - Complementary monitoring system
- [Internal Eng Wiki](https://www.notion.so/eff1eba446e74a048b7607d08513e411) - Parent wiki containing Sentry documentation
