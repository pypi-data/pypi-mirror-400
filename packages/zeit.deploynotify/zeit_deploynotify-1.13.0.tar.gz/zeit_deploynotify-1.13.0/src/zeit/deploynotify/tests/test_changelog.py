from .. import changelog


def test_extract_postdeploy():
    postdeploy = changelog.extract_postdeploy("""\
Changelog
=========

something else

POSTDEPLOY
- one
- two

.. towncrier release notes start

1.0.0 (2023-01-01)
------------------

- Initial release""")
    assert (
        postdeploy
        == """\
- one
- two"""
    )


def test_postdeploy_only_nothing_returns_empty():
    postdeploy = changelog.extract_postdeploy("""\
- nothing

.. towncrier release notes start""")
    assert postdeploy is None


VERSIONS = """\
Changelog
=========

.. towncrier release notes start

1.3.0 (2023-04-03)
------------------

- Entry 1.3.0 A

- Entry 1.3.0 B


1.2.0 (2023-04-02)
------------------

- Entry 1.2.0 A

- Entry 1.2.0 B


1.0.0 (2023-04-01)
------------------

- Entry 1.0.0 A

- Entry 1.0.0 B
"""


def test_extract_first_version():
    assert (
        changelog.extract_version(VERSIONS)
        == """\
1.3.0 (2023-04-03)
------------------

- Entry 1.3.0 A

- Entry 1.3.0 B"""
    )


def test_extract_specified_version():
    assert (
        changelog.extract_version(VERSIONS, '1.2.0')
        == """\
1.2.0 (2023-04-02)
------------------

- Entry 1.2.0 A

- Entry 1.2.0 B"""
    )


def test_extract_to_previous_version():
    assert (
        changelog.extract_version(VERSIONS, '1.3.0', '1.0.0')
        == """\
1.3.0 (2023-04-03)
------------------

- Entry 1.3.0 A

- Entry 1.3.0 B


1.2.0 (2023-04-02)
------------------

- Entry 1.2.0 A

- Entry 1.2.0 B"""
    )


def test_extract_nothing_if_previous_version_is_same():
    assert changelog.extract_version(VERSIONS, '1.3.0', '1.3.0') == ''


def test_extract_issues():
    issues = changelog.extract_issues(
        """\
1.3.0 (2023-04-03)
------------------

- ZO-123: Issue A

- WCM-789: Issue C

FIX:
- Fix something

- MAINT: Maintenance

- ZO-456: Issue B
""",
        'ZO|WCM',
    )
    assert issues == ['ZO-123', 'WCM-789', 'ZO-456']
