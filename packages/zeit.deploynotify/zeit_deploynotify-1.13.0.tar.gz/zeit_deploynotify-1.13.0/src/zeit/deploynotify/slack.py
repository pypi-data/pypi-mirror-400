import logging
import re

import requests

from . import changelog
from .base import Notification


log = logging.getLogger(__name__)


class SlackRelease(Notification):
    def __call__(self, channel_name, token, emoji, vcs_url=None, changelog_url=None):
        if not vcs_url:
            vcs_url = f'http://github.com/ZeitOnline/{self.project}/tree/{self.version}'
        if not changelog_url:
            changelog_url = f'http://github.com/ZeitOnline/{self.project}/blob/main/CHANGES.rst'

        with requests.Session() as http:
            r = http.post(
                f'http://hackbot.zon.zeit.de/{token}/deployment/{channel_name}',
                json={
                    'project': self.project,
                    'environment': self.environment,
                    'version': self.version,
                    'emoji': emoji,
                    'vcs_url': vcs_url,
                    'changelog_url': changelog_url,
                },
            )
            log.info('%s returned %s: %s', r.url, r.status_code, r.text)


class SlackVersionReminder(Notification):
    """Check given vivi version against the version seen in content storage api

    If versions differ, give friendly reminder to update content storage
    """

    def __call__(self, channel_id, slack_token):
        with requests.Session() as http:
            environment = self.environment if self.environment == 'staging' else 'prod'
            r = http.get(f'https://content-storage.{environment}.zon.zeit.de/public/-')
            storage_version = r.json()['data']['vivi-version']
            if storage_version == self.version:
                return
            r = http.post(
                'https://slack.com/api/chat.postMessage',
                json={
                    'channel': channel_id,
                    'text': (
                        f'Storage API vivi {storage_version} braucht ein '
                        f'Update auf vivi {self.version}'
                    ),
                },
                headers={'Authorization': f'Bearer {slack_token}'},
            )
            log.info('%s returned %s: %s', r.url, r.status_code, r.text)


class SlackChangelog(Notification):
    def __call__(
        self,
        channel_id,
        filename,
        slack_token,
        github_token,
        title='{project} {environment} changelog',
    ):
        t = changelog.download_changelog(github_token, self.project, self.version, filename)
        changes = changelog.extract_version(t, self.version, self.previous_version)
        if not changes:
            log.info(
                'No changelog found in %s %s for %s - %s',
                self.project,
                filename,
                self.previous_version,
                self.version,
            )
            return ''
        changes = re.sub('\n+', '\n', changes)  # Save some vertical space

        if not channel_id:
            return changes

        title = title.format(**self.__dict__)
        with requests.Session() as http:
            r = http.post(
                'https://slack.com/api/chat.postMessage',
                json={
                    'channel': channel_id,
                    'attachments': [
                        {
                            'title': title,
                            'mrkdwn_in': ['text'],
                            'text': f'```{changes}```',
                        }
                    ],
                },
                headers={'Authorization': f'Bearer {slack_token}'},
            )
            log.info('%s returned %s: %s', r.url, r.status_code, r.text)

        return changes


class SlackPostdeploy(Notification):
    def __call__(
        self, channel_id, filename, slack_token, github_token, title='{project} postdeploy'
    ):
        t = changelog.download_changelog(github_token, self.project, self.version, filename)
        postdeploy = changelog.extract_postdeploy(t)
        if not postdeploy:
            log.info(
                'No postdeploy entries found in %s %s for %s', self.project, filename, self.version
            )
            return
        if not channel_id:
            print(postdeploy)
            return

        with requests.Session() as http:
            r = http.post(
                'https://slack.com/api/chat.postMessage',
                json={
                    'channel': channel_id,
                    'attachments': [
                        {
                            'title': title.format(**self.__dict__),
                            'mrkdwn_in': ['text'],
                            'text': f'```{postdeploy}```',
                        }
                    ],
                },
                headers={'Authorization': f'Bearer {slack_token}'},
            )
            log.info('%s returned %s: %s', r.url, r.status_code, r.text)
