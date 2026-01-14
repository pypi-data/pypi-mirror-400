========================
Deployment Notifications
========================

This package collects the mechanics for sending notifications "version x of project y was just deployed to environment z",
for example to set markers in observability systems like Grafana,
post a message to a slack channel,
transition issues in jira to the corresponding status, etc.


Usage
=====

The package provides a "multi subcommand" CLI interface::

    python -m zeit.deploynotify
        --environment=staging --project=example --version=1.2.3 \
        slack --channel=example --emoji=palm_tree

Typically this will be integrated as a `Keptn Deployment Task <https://lifecycle.keptn.sh/docs/implementing/tasks/>`_, like this::

    apiVersion: external-secrets.io/v1
    kind: ExternalSecret
    metadata:
      name: deployment-notify
    spec:
      refreshInterval: 1h
      secretStoreRef:
        name: baseproject-vault
        kind: SecretStore
      data:
      - secretKey: SLACK_HOOK_TOKEN
        remoteRef:
          key: zon/v1/slack/hackbot
          property: HOOK_TOKEN
    ---
    apiVersion: lifecycle.keptn.sh/v1alpha3
    kind: KeptnTaskDefinition
    metadata:
      name: notify
    spec:
      container:
        name: task
        image: europe-west3-docker.pkg.dev/zeitonline-engineering/docker-zon/deploynotify:1.0.0
        envFrom:
          - secretRef:
              name: deployment-notify
        args:
          - "--environment=staging"
          - "slack"
          - "--channel=example"
          - "--emoji=palm_tree"
