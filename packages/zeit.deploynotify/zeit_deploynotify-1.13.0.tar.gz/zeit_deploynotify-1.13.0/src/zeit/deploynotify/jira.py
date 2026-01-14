import logging

import jira

from . import changelog
from .base import Notification


log = logging.getLogger(__name__)


class Jira(Notification):
    def __call__(
        self,
        url,
        filename,
        issue_prefix,
        status_name,
        ignore_status_names,
        changelog_from_tag,
        jira_username,
        jira_token,
        github_token,
    ):
        t = changelog.download_changelog(
            github_token, self.project, self.version, filename, changelog_from_tag
        )
        issues = changelog.extract_issues(
            changelog.extract_version(t, self.version, self.previous_version), issue_prefix
        )

        api = jira.JIRA(server=url, basic_auth=(jira_username, jira_token))
        for issue in issues:
            issue = api.issue(issue)
            current = issue.fields.status.name
            if current in ignore_status_names:
                log.info('%s already has status %s', issue, current)
                continue
            log.info('Setting %s to %s', issue, status_name)
            try:
                api.transition_issue(issue, status_name)
            except jira.JIRAError:
                log.warn('Could not set %s to %s', issue, status_name, exc_info=True)
