from functools import partial
from unittest.mock import patch

import click.testing
import pytest
import requests

import zeit.deploynotify.cli


@pytest.fixture(scope='session')
def cli():
    runner = click.testing.CliRunner()
    return partial(runner.invoke, zeit.deploynotify.cli.cli)


def test_cli_imports_all_modules(cli):
    assert cli(['--help']).exit_code == 0


@patch.object(requests.Session, 'get')
def test_cli_slack_reminder(mock_get, monkeypatch, cli):
    mock_get.return_value.json.return_value = {'data': {'vivi-version': '1.0.0'}}
    monkeypatch.setenv('SLACK_BOT_TOKEN', 'test-slack-hook-token')
    result = cli(
        [
            '--environment',
            'production',
            '--project',
            'vivi',
            '--version',
            '1.0.0',
            '--previous-version',
            '0.9.0',
            'slack-reminder',
            '--channel-id',
            'C12345678',
        ]
    )
    mock_get.assert_called_once_with('https://content-storage.prod.zon.zeit.de/public/-')
    assert result.exit_code == 0
