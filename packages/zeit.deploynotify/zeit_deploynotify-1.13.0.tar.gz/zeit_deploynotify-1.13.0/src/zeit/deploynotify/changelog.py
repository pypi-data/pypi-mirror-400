import re

import requests


def download_changelog(token, package, version, filename, from_tag=True):
    params = {}
    if from_tag:
        params['ref'] = version
    with requests.Session() as http:
        r = http.get(
            f'https://api.github.com/repos/ZeitOnline/{package}/contents/{filename}',
            params=params,
            headers={
                'Accept': 'application/vnd.github.3.raw',
                'Authorization': f'Bearer {token}',
            },
        )
        r.raise_for_status()
        return r.text


def extract_postdeploy(changelog):
    lines = changelog.split('\n')
    start = 0
    end = -1
    for i, line in enumerate(lines):
        if line == 'POSTDEPLOY':
            start = i + 1
        if '.. towncrier' in line:
            end = i - 1
            break

    result = lines[start:end]
    if result[-1] == '- nothing':
        return None
    return '\n'.join(result)


def extract_version(changelog, version=None, previous_version=None):
    if version and previous_version and version == previous_version:
        return ''

    _version = re.compile(r'(.+) \(\d{4}-\d{2}-\d{2}\)\W*$')
    lines = changelog.split('\n')
    start = 0
    end = -1
    for i, line in enumerate(lines):
        match = _version.search(line)
        if not match:
            continue

        if not version:
            if not start:
                start = i
                continue
            else:
                end = i
                break

        if not previous_version and start:
            end = i
            break

        current = match.group(1).strip()
        if current == version:
            start = i
        elif start and current == previous_version:
            end = i
            break

    return '\n'.join(lines[start:end]).strip()


def extract_issues(changelog, prefix):
    _issue = re.compile(rf'\s*-\s+(({prefix})-\d+):')
    result = []
    for line in changelog.split('\n'):
        issue = _issue.search(line)
        if issue:
            result.append(issue.group(1))
    return result
