# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2024-2026 Anna <cyber@sysrq.in>

"""
Asynchronous wrapper for Repology API tools.
"""

from collections.abc import Set

import aiohttp
from yarl import URL

from repology_client._client import api
from repology_client.constants import TOOL_PROJECT_BY_URL
from repology_client.exceptions.resolve import (
    MultipleProjectsFound,
    ProjectNotFound,
)
from repology_client.types import (
    Package,
    ResolvePackageType,
    _ResolvePkg,
)
from repology_client.utils import get_type_adapter, ensure_session


async def resolve_package(repo: str, name: str,
                          name_type: ResolvePackageType = ResolvePackageType.SOURCE,
                          *, autoresolve: bool = True,
                          session: aiohttp.ClientSession | None = None) -> Set[Package]:
    """
    If you don't know how a project is named on Repology and therefore cannot
    use the :py:func:`get_packages` function, use this instead.

    This function uses the ``/tools/project-by`` utility to resolve a package
    name into ``/api/v1/project/<project>`` project information.

    If you disable autoresolve, ambiguous package names will raise the
    :py:class:`repology_client.exceptions.resolve.MultipleProjectsFound`
    exception. It will however contain all matching project names, so you can
    continue.

    :param repo: repository name on Repology
    :param name: package name in the repository
    :param name_type: which name is used, "source" or "binary"
    :param autoresolve: enable automatic ambiguity resolution
    :param session: :external+aiohttp:py:mod:`aiohttp` client session

    :raises repology_client.exceptions.resolve.MultipleProjectsFound: on
        ambiguous package names when automatic resolution is disabled
    :raises repology_client.exceptions.resolve.ProjectNotFound: on failed
        resolve resulting in the "404 Not Found" HTTP error
    :raises aiohttp.ClientResponseError: on HTTP errors (except 404)
    :raises ValueError: on JSON decode failure

    :returns: set of packages
    """

    params = {
        "repo": repo,
        "name": name,
        "name_type": name_type,
        "target_page": "api_v1_project",
    }
    if not autoresolve:
        params["noautoresolve"] = "on"

    pkg = _ResolvePkg.model_validate(params)
    try:
        url = URL(TOOL_PROJECT_BY_URL).with_query(params)
        async with ensure_session(session) as aiohttp_session:
            data = await api(url, session=aiohttp_session)
    except aiohttp.ClientResponseError as err:
        if err.status == 404:
            raise ProjectNotFound(pkg) from err
        raise

    if (
        isinstance(data, dict)
        and isinstance(targets := data.get("targets"), dict)
    ):
        raise MultipleProjectsFound(pkg, targets.keys())

    return get_type_adapter(Set[Package]).validate_python(data)
