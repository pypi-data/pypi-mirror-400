import logging

import requests

from .base import Notification


log = logging.getLogger(__name__)


class Speedcurve(Notification):
    def __call__(self, site_id, token, text='{project}_v{version}'):
        text = text.format(**self.__dict__)

        with requests.Session() as http:
            r = http.post(
                'https://api.speedcurve.com/v1/deploys',
                data={
                    'site_id': site_id,
                    'note': text,
                },
                auth=(token, 'any'),
            )
            log.info('%s returned %s: %s', r.url, r.status_code, r.text)
