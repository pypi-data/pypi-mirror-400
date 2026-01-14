import json
import logging
import os

import click

from .github import GithubEvent
from .grafana import Grafana
from .honeycomb import Honeycomb
from .jira import Jira
from .slack import SlackChangelog, SlackPostdeploy, SlackRelease, SlackVersionReminder
from .speedcurve import Speedcurve


@click.group(chain=True)
@click.pass_context
@click.option('--environment', required=True)
@click.option('--project')
@click.option('--version')
@click.option('--previous-version')
def cli(ctx, environment, project, version, previous_version):
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')
    ctx.ensure_object(dict)

    ctx.obj['environment'] = environment

    # https://keptn.sh/stable/docs/guides/tasks/#context
    if 'KEPTN_CONTEXT' in os.environ:
        keptn = json.loads(os.environ['KEPTN_CONTEXT'])
        ctx.obj['project'] = keptn['appName']
        ctx.obj['version'] = keptn['workloadVersion']

    if project:
        ctx.obj['project'] = project
    if version:
        ctx.obj['version'] = version
    ctx.obj['previous_version'] = previous_version


@cli.command()
@click.pass_context
@click.option('--url', default='https://grafana.ops.zeit.de')
@click.option('--text', default='{project} {version}')
@click.option('--tags', default='deployment')
def grafana(ctx, url, text, tags):
    notify = Grafana(**ctx.obj)
    notify(url, os.environ['GRAFANA_TOKEN'], text, tags.split(','))


@cli.command()
@click.pass_context
@click.option('--dataset', default='__all__')
@click.option('--text', default='{project} {version}')
@click.option('--vcs-url')
def honeycomb(ctx, dataset, text, vcs_url):
    notify = Honeycomb(**ctx.obj)
    notify(os.environ['HONEYCOMB_TOKEN'], dataset, text, vcs_url)


@cli.command()
@click.pass_context
@click.option('--url', default='https://zeit-online.atlassian.net')
@click.option('--issue-prefix', default='ZO|WCM|ES')
@click.option('--status-name', default='Testing')
@click.option('--ignore-status', default='Backlog,Testing,Approved,Closed')
@click.option('--changelog', default='CHANGES.rst')
@click.option('--changelog-from-tag/--no-changelog-from-tag', default=True)
def jira(ctx, url, issue_prefix, status_name, ignore_status, changelog, changelog_from_tag):
    notify = Jira(**ctx.obj)
    notify(
        url,
        changelog,
        issue_prefix,
        status_name,
        ignore_status.split(','),
        changelog_from_tag,
        os.environ['JIRA_USERNAME'],
        os.environ['JIRA_TOKEN'],
        os.environ['GITHUB_TOKEN'],
    )


@cli.command()
@click.pass_context
@click.option('--channel-name', default='releases')
@click.option('--emoji')
@click.option('--vcs-url')
@click.option('--changelog-url')
def slack(ctx, channel_name, emoji, vcs_url, changelog_url):
    notify = SlackRelease(**ctx.obj)
    notify(channel_name, os.environ['SLACK_HOOK_TOKEN'], emoji, vcs_url, changelog_url)


@cli.command()
@click.pass_context
@click.option('--channel-id')
@click.option('--title', default='{project} {environment} changelog')
@click.option('--changelog', default='CHANGES.rst')
def slack_changelog(ctx, channel_id, title, changelog):
    notify = SlackChangelog(**ctx.obj)
    diff = notify(
        channel_id, changelog, os.environ['SLACK_BOT_TOKEN'], os.environ['GITHUB_TOKEN'], title
    )
    print(diff)


@cli.command()
@click.pass_context
@click.option('--channel-id')
def slack_reminder(ctx, channel_id):
    notify = SlackVersionReminder(**ctx.obj)
    notify(channel_id, os.environ['SLACK_BOT_TOKEN'])


@cli.command()
@click.pass_context
@click.option('--channel-id')
@click.option('--changelog', default='CHANGES.rst')
def slack_postdeploy(ctx, channel_id, changelog):
    notify = SlackPostdeploy(**ctx.obj)
    notify(channel_id, changelog, os.environ['SLACK_BOT_TOKEN'], os.environ['GITHUB_TOKEN'])


@cli.command()
@click.pass_context
@click.option('--site-id', required=True)
@click.option('--text', default='{project}_v{version}')
def speedcurve(ctx, site_id, text):
    notify = Speedcurve(**ctx.obj)
    notify(site_id, os.environ['SPEEDCURVE_TOKEN'], text)


@cli.command()
@click.pass_context
@click.option('--repository', required=True)
@click.option('--event-type', required=True)
@click.option('--client-payload')
def gha_workflow(ctx, repository, event_type, client_payload):
    notify = GithubEvent(**ctx.obj)
    notify(repository, event_type, os.environ['GITHUB_TOKEN'], client_payload)
