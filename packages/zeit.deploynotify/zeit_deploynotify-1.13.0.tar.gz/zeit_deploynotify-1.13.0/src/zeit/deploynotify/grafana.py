import logging

import requests

from .base import Notification


log = logging.getLogger(__name__)


class Grafana(Notification):
    def __call__(self, url, token, text='{project} {version}', tags=None):
        text = text.format(**self.__dict__)
        if not tags:
            tags = []

        with requests.Session() as http:
            r = http.post(
                f'{url}/api/annotations',
                json={
                    'text': text,
                    'tags': tags,
                },
                headers={'Authorization': f'Bearer {token}'},
            )
            log.info('%s returned %s: %s', r.url, r.status_code, r.text)
