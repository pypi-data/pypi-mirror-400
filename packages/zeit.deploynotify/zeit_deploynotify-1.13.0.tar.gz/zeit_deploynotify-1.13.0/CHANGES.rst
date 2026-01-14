Changelog
=========

.. towncrier release notes start

zeit.deploynotify 1.13.0 (2026-01-08)
-------------------------------------

Changes
+++++++

- Implement gha-workflow command to send repository_dispatch event to GHA (gha)


zeit.deploynotify 1.12.0 (2025-09-10)
-------------------------------------

Changes
+++++++

- jira: Ignore issues that cannot be transitioned (jira)


1.11.0 (2025-05-06)
-------------------

Changes
+++++++

- MAINT: Consider ES project when updating Jira tickets (jira-project)


1.10.2 (2025-04-25)
-------------------

Changes
+++++++

- Correctly return empty changelog diff (empty)


1.10.1 (2025-04-23)
-------------------

Changes
+++++++

- Return empty changelog diff if previous version equals current version (previous)


1.10.0 (2025-02-27)
-------------------

Changes
+++++++

- Specify separate title for postdeploy message (postdeploy)


1.9.1 (2025-02-25)
------------------

Changes
+++++++

- Ignore status Backlog by default (jira)


1.9.0 (2025-02-20)
------------------

Changes
+++++++

- Move printing of changelog diff to CLI for reusability (printdiff)


1.8.1 (2024-12-11)
------------------

Changes
+++++++

- Retrieve workloadVersion, not appVersion from keptn context (keptn)


1.7.0 (2024-12-10)
------------------

Changes
+++++++

- Make retrieving the changelog from tag configurable (jira)


1.6.0 (2024-10-18)
------------------

Changes
+++++++

- WCM-457: new custom command slack-reminder (reminder)


Changes
+++++++

- WCM-457: new custom command slack-reminder (reminder)


1.5.0 (2024-08-07)
------------------

Changes
+++++++

- issues: Support multiple issue prefixes (issues)
- jira: Select jira status by name insead of id (jira)


1.4.1 (2024-07-30)
------------------

Changes
+++++++

- ZO-5636: Set all hny dataset as default (ZO-5636)


1.4.0 (2024-07-30)
------------------

Changes
+++++++

- ZO-5636: Support honeycomb environments marker (ZO-5636)


1.3.0 (2024-02-22)
------------------

Changes
+++++++

- Update to keptn-0.10 context API (keptn)


1.2.3 (2024-01-17)
------------------

Changes
+++++++

- Fix jira status change (jira)


1.2.2 (2024-01-16)
------------------

Changes
+++++++

- Don't set jira status if status is already 'more done' (jira)


1.2.1 (2024-01-11)
------------------

Changes
+++++++

- Detect empty postdeploy properly (postdeploy)


1.1.1 (2024-01-08)
------------------

Changes
+++++++

- Quote changelog text correctly for slack (changelog)


1.1.0 (2024-01-08)
------------------

Changes
+++++++

- ZO-4171: Implement posting the changelog diff to slack (changelog)


1.0.4 (2024-01-08)
------------------

Changes
+++++++

- postdeploy: Retrieve changelog of the deployed version (postdeploy)


1.0.3 (2023-12-18)
------------------

Changes
+++++++

- Fix jira changelog parsing (jira)


1.0.2 (2023-12-18)
------------------

Changes
+++++++

- Fix bugsnag cli parsing (bugsnag)


1.0.1 (2023-12-18)
------------------

Changes
+++++++

- Allow calling multiple tasks in a single invocation (chain)


1.0.0 (2023-12-13)
------------------

Changes
+++++++

- Initial release (initial)
