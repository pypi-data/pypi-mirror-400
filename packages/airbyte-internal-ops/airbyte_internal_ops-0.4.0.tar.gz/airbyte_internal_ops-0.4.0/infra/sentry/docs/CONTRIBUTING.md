# Contributing to Sentry Configuration

This guide provides the minimal information needed to contribute to Airbyte's Sentry configuration.

## Quick Links

- [Sentry Project](https://sentry.io/organizations/airbytehq/projects/connector-incident-management) - Main connector-incident-management project
- [Alert Rules](https://sentry.io/organizations/airbytehq/alerts/rules) - Configure and view alert rules
- [Issue Grouping Settings](https://sentry.io/settings/airbytehq/projects/connector-incident-management/issue-grouping/) - Manage stack trace grouping rules
- [GitHub Integration](https://github.com/airbytehq/workflow-actions/actions/workflows/sentry.yml) - Sentry-GitHub sync workflow
- [Pulumi IAC](../) - Infrastructure as Code for Sentry configuration

## Configuration Areas

### 1. Environment Variables

**What:** Enable and configure Sentry error reporting in Airbyte deployments.

**Where to configure:**

- For Cloud: [Helm values template](https://github.com/airbytehq/airbyte-cloud/blob/4011324ade18bb95fc3efc7df3ab718d2ef1b9c0/tools/helm-values-builder/templates/gcp_helm_values.yaml.j2#L15-L16)
- For OSS/Self-hosted: Set environment variables on server and workers

**Required variables:**

```bash
JOB_ERROR_REPORTING_STRATEGY=sentry
JOB_ERROR_REPORTING_SENTRY_DSN=<sentry-project-dsn>
```

**Documentation:** [Sentry at Airbyte - Configuration](https://www.notion.so/9fdc95e5ed4d429e9fd889960bdb5b33#configuration)

### 2. Stack Trace Grouping Rules

**What:** Control how errors are grouped together in Sentry based on stack traces.

**Where to configure:** [Issue Grouping Settings](https://sentry.io/settings/airbytehq/projects/connector-incident-management/issue-grouping/)

**Current rules:**

```plaintext
# java: mark everything from io.airbyte.* as in-app
stack.module:io.airbyte.* +app

# python: mark everything in a folder with airbyte in it as in-app
stack.abs_path:**/airbyte*/** +app
```

**When to modify:** When errors from Airbyte code aren't being properly grouped or when adding support for new languages/frameworks.

**Documentation:**

- [Sentry Stack Trace Rules](https://docs.sentry.io/product/data-management-settings/event-grouping/stack-trace-rules/)
- [Airbyte Sentry Setup - Grouping Rules](https://www.notion.so/9fdc95e5ed4d429e9fd889960bdb5b33#grouping-rules)

### 3. Ownership Rules

**What:** Determine which team receives alerts for specific types of errors.

**Where to configure:** Sentry UI for the connector-incident-management project

**Current rules:**

```docker
# python issues → api connectors team
tags.stacktrace_platform:python #api-connectors

# java and normalization failures → databases team
tags.stacktrace_platform:java #db-connectors
tags.failure_origin:normalization #db-connectors
```

**When to modify:** When adding new connector teams or reorganizing team responsibilities.

**Documentation:**

- [Sentry Issue Ownership](https://docs.sentry.io/product/issues/issue-owners/)
- [Airbyte Sentry Setup - Ownership Rules](https://www.notion.so/9fdc95e5ed4d429e9fd889960bdb5b33#ownership-rules)

### 4. Alert Rules

**What:** Configure when and how teams are notified about Sentry issues.

**Where to configure:** [Sentry Alert Rules Page](https://sentry.io/organizations/airbytehq/alerts/rules)

**Current alert types:**

#### P0 Alerts

- Trigger PagerDuty + `#oncall` Slack channel
- GA connector: >2 workspaces affected in 24h
- Beta connector: >5 workspaces affected in 24h

#### Stack Trace Parsing Failure Alerts

- Notify `#dev-connectors-ops` Slack channel
- Indicates parsing logic needs improvement

**When to modify:** When changing alert thresholds, adding new alert types, or modifying notification channels.

**Documentation:**

- [Sentry Alerts](https://docs.sentry.io/product/alerts/)
- [Airbyte Sentry Setup - Alerts](https://www.notion.so/9fdc95e5ed4d429e9fd889960bdb5b33#alerts)

### 5. GitHub Integration

**What:** Automatically sync Sentry issues with GitHub issues in the [oncall repository](https://github.com/airbytehq/oncall).

**Where to configure:** [workflow-actions repository](https://github.com/airbytehq/workflow-actions)

**Main workflow:** [sentry.yml](https://github.com/airbytehq/workflow-actions/actions/workflows/sentry.yml)

**Functionality:**

- Runs hourly to process unresolved Sentry issues
- Creates GitHub issues for new Sentry issues
- Updates GitHub issues with affected workspace lists
- Resolves Sentry issues when GitHub issues are closed (if no new events)

**When to modify:** When changing sync behavior, updating issue templates, or modifying workspace tracking.

**Documentation:** [Airbyte Sentry Setup - GitHub Sync](https://www.notion.so/9fdc95e5ed4d429e9fd889960bdb5b33#github-sync)

### 6. Infrastructure as Code (Pulumi)

**What:** Manage Sentry teams, alerts, and dashboards as code using Pulumi.

**Where to configure:** This directory (`infra/sentry/`)

**Prerequisites:** Install the Pulumi CLI:

```bash
brew install pulumi
```

**What can be managed:**
- Projects (including fingerprint rules and grouping enhancements)
- Issue alerts (P0 alerts, parsing failure alerts)
- Metric alerts
- Dashboards

**What is managed via Sentry UI:**
- Teams (referenced by slug in Pulumi, but membership managed in UI)
- Ownership rules (team assignment rules)

**When to use:** When making changes to alert configurations that should be version-controlled and reviewed via PR.

**Documentation:** [Import Guide](./IMPORT_GUIDE.md)

## Common Contribution Scenarios

### Adding a New Connector Team

1. **Update Ownership Rules** in Sentry UI
   - Add new team identifier (e.g., `#new-team`)
   - Define rules for routing issues to the new team

2. **Create PagerDuty Service** for the new team
   - Follow [PagerDuty documentation](https://www.notion.so/018bb3ae8ef14fc2ba073f96c7e182fd)

3. **Create New P0 Alert** in Sentry
   - Clone existing P0 alert
   - Update team filter to match new ownership rules
   - Configure PagerDuty integration

4. **Test the Configuration**
   - Verify ownership assignment works
   - Test alert routing to correct team/PagerDuty service

### Adjusting Alert Thresholds

1. **Navigate to** [Alert Rules](https://sentry.io/organizations/airbytehq/alerts/rules)

2. **Edit the relevant alert** (P0 GA or P0 Beta)

3. **Modify the workspace count threshold**
   - GA connectors: Currently >2 workspaces
   - Beta connectors: Currently >5 workspaces

4. **Test and Monitor** impact of changes

### Improving Error Grouping

1. **Review** poorly grouped issues in Sentry

2. **Identify** common patterns in stack traces

3. **Update** [Stack Trace Rules](https://sentry.io/settings/airbytehq/projects/connector-incident-management/issue-grouping/)
   - Add new patterns to mark as in-app
   - Use `+app` to include frames in grouping

4. **Monitor** grouping behavior after changes

5. **Document** changes in [Notion](https://www.notion.so/9fdc95e5ed4d429e9fd889960bdb5b33#grouping-rules)

## Error Reporting Best Practices

When working on connector code, ensure proper error reporting:

### Use Correct Failure Types

Only **system_error** failures are sent to Sentry. Other failure types:

- `config_error`: User intervention required (NOT sent to Sentry)
- `transient_error`: Temporary errors that might resolve (NOT sent to Sentry)

**Documentation:** [Errors in Airbyte - Error Message Flow](https://www.notion.so/cefeae34698745a2aca9c3d967be81c5#error-message-flow-and-data-model)

### Emit AirbyteTraceMessages

Connectors using recent versions of CDK or java-base automatically emit trace messages via uncaught exception handlers.

**Documentation:** [Airbyte Protocol - AirbyteErrorTraceMessage](https://docs.airbyte.com/understanding-airbyte/airbyte-protocol#airbyteerrortracemessage)

## Getting Help

- **Sentry Configuration Questions:** Check [Sentry at Airbyte](https://www.notion.so/9fdc95e5ed4d429e9fd889960bdb5b33)
- **Error Handling Questions:** Check [Errors in Airbyte](https://www.notion.so/cefeae34698745a2aca9c3d967be81c5)
- **Oncall Process Questions:** Check [All Teams Oncall Issues Process](https://www.notion.so/42034cac09d5434e8ddb4cff1718742d)
- **PagerDuty Questions:** Check [All things PagerDuty](https://www.notion.so/018bb3ae8ef14fc2ba073f96c7e182fd)

## Related Documentation

- [Main Sentry README](../README.md) - Comprehensive Sentry setup documentation
- [Sentry at Airbyte (Notion)](https://www.notion.so/9fdc95e5ed4d429e9fd889960bdb5b33) - Primary configuration guide
- [Errors in Airbyte (Notion)](https://www.notion.so/cefeae34698745a2aca9c3d967be81c5) - Error handling architecture
- [workflow-actions Repository](https://github.com/airbytehq/workflow-actions) - GitHub integration code
- [oncall Repository](https://github.com/airbytehq/oncall) - Where Sentry issues are tracked
