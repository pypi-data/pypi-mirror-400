import logging

import requests

from .base import Notification


log = logging.getLogger(__name__)


class GithubEvent(Notification):
    def __call__(self, repository, event_type, token, client_payload='{{}}'):
        client_payload = client_payload.format(**self.__dict__)

        with requests.Session() as http:
            r = http.post(
                f'https://api.github.com/repos/ZeitOnline/{repository}/dispatches',
                headers={
                    'Accept': 'application/vnd.github+json',
                    'Authorization': f'Bearer {token}',
                },
                data=f'{{"event_type": "{event_type}", "client_payload": {client_payload}}}',
            )
            log.info('%s returned %s: %s', r.url, r.status_code, r.text)
