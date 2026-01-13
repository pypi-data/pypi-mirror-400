# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2024 Anna <cyber@sysrq.in>

from repology_client.exceptions.resolve import MultipleProjectsFound
from repology_client.types import (
    ResolvePackageType,
    _ResolvePkg,
)


def test_multiple_projects_exception():
    pkg = _ResolvePkg(repo="freedos", name="foo",
                      name_type=ResolvePackageType.BINARY)
    names = {
        "foo": "https://foo.example.com",
        "neofoo": "https://neofoo.example.org",
    }
    exc = MultipleProjectsFound(pkg, names.keys())

    assert exc.pkg == pkg
    assert sorted(exc.names) == ["foo", "neofoo"]
