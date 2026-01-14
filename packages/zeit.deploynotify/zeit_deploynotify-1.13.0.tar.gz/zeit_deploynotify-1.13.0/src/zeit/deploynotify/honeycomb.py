import logging

import requests

from .base import Notification


log = logging.getLogger(__name__)


class Honeycomb(Notification):
    def __call__(
        self,
        token,
        dataset='__all__',
        text='{project} {version}',
        vcs_url=None,
        staging_dataset_auto=True,
    ):
        text = text.format(**self.__dict__)
        if dataset != '__all__' and staging_dataset_auto and self.environment != 'production':
            dataset = f'staging-{dataset}'
        if not vcs_url:
            vcs_url = f'http://github.com/ZeitOnline/{self.project}/tree/{self.version}'

        with requests.Session() as http:
            r = http.post(
                f'https://api.honeycomb.io/1/markers/{dataset}',
                json={
                    'message': text,
                    'type': 'deploy',
                    'url': vcs_url,
                },
                headers={'x-honeycomb-team': token},
            )
            log.info('%s returned %s: %s', r.url, r.status_code, r.text)
