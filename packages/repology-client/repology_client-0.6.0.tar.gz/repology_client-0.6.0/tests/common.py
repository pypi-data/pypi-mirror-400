# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2024 Anna <cyber@sysrq.in>

from collections.abc import Set

from repology_client.types import Package


def check_firefox_project(packages: Set[Package]):
    """
    Check data returned by the ``/api/v1/project/firefox`` endpoint.
    """

    firefox_pkg: Package | None = None
    for pkg in packages:
        if pkg.repo == "gentoo" and pkg.visiblename == "www-client/firefox":
            firefox_pkg = pkg
            break

    assert firefox_pkg is not None
    assert firefox_pkg.srcname == "www-client/firefox"
    assert firefox_pkg.summary == "Firefox Web Browser"

    assert firefox_pkg.maintainers is not None
    assert "mozilla@gentoo.org" in firefox_pkg.maintainers

    assert firefox_pkg.licenses is not None
    assert "MPL-2.0" in firefox_pkg.licenses
