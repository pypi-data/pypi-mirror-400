# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2024-2026 Anna <cyber@sysrq.in>

"""
Asynchronous wrapper for Repology API v1.
"""

import warnings
from collections.abc import Mapping, Sequence, Set

import aiohttp
from yarl import URL

from repology_client._client import api
from repology_client.constants import (
    API_V1_URL,
    HARD_LIMIT,
    MAX_PROBLEMS,
    MAX_PROJECTS,
)
from repology_client.exceptions import (
    InvalidInput,
    RepoNotFound,
)
from repology_client.types import (
    Package,
    Problem,
    ProjectsRange,
)
from repology_client.utils import get_type_adapter, ensure_session


async def get_packages(project: str, *,
                       session: aiohttp.ClientSession | None = None) -> Set[Package]:
    """
    Access the ``/api/v1/project/<project>`` endpoint to list packages for a
    single project.

    :param project: project name on Repology
    :param session: :external+aiohttp:py:mod:`aiohttp` client session

    :raises repology_client.exceptions.EmptyResponse: on empty response
    :raises repology_client.exceptions.InvalidInput: if ``project`` is an empty
        string
    :raises aiohttp.ClientResponseError: on HTTP errors

    :returns: set of packages
    """

    if not project:
        raise InvalidInput(f"Not a valid project name: {project}")

    endpoint = URL(API_V1_URL) / "project" / project
    async with ensure_session(session) as aiohttp_session:
        data = await api(endpoint, session=aiohttp_session)
    return get_type_adapter(Set[Package]).validate_python(data)


async def get_projects(start: str = "", end: str = "", count: int = 200, *,
                       session: aiohttp.ClientSession | None = None,
                       **filters: str) -> Mapping[str, Set[Package]]:
    """
    Access the ``/api/v1/projects/`` endpoint to list projects.

    If both ``start`` and ``end`` are given, only ``start`` is used.

    :param start: name of the first project to start with
    :param end: name of the last project to end with
    :param count: maximum number of projects to fetch
    :param session: :external+aiohttp:py:mod:`aiohttp` client session

    :raises repology_client.exceptions.EmptyResponse: on empty response
    :raises aiohttp.ClientResponseError: on HTTP errors

    :returns: project to packages mapping
    """

    if count > HARD_LIMIT:
        warnings.warn(f"Resetting count to {HARD_LIMIT} to prevent API abuse")
        count = HARD_LIMIT

    proj_range = ProjectsRange(start=start, end=end)
    if start and end:
        warnings.warn("The 'start..end' range format is not supported by Repology API")
        proj_range.end = ""

    result: dict[str, Set[Package]] = {}
    async with ensure_session(session) as aiohttp_session:
        while True:
            endpoint = URL(API_V1_URL) / "projects"
            if proj_range:
                endpoint /= str(proj_range)
            endpoint /= ""

            batch = get_type_adapter(dict[str, Set[Package]]).validate_python(
                await api(endpoint.with_query(filters), session=aiohttp_session)
            )
            result.update(batch)

            if len(result) >= count:
                break
            if len(batch) == MAX_PROJECTS:
                # we probably hit API limits, so…
                # …choose lexicographically highest project as a new start
                proj_range.start = max(batch)
                # …make sure we haven't already hit the requested end
                if end and proj_range.start >= end:
                    break
                # …and drop end condition as unsupported
                proj_range.end = ""
            else:
                break

    return result


async def get_problems(repo: str, maintainer: str = "",
                       start: str = "", count: int = 200, *,
                       session: aiohttp.ClientSession | None = None) -> Sequence[Problem]:
    """
    Access the endpoints to get problems for specific repository or maintainer.

    .. seealso::

       :py:func:`repology_client.utils.format_link_status` function
          This helper function can be used to convert status codes (returned in
          data objects of ``homepage_dead`` and ``download_dead`` problem types)
          to human-readable messages.

    :param repo: repository name on Repology
    :param maintainer: maintainer e-mail address
    :param start: name of the first project to start with
    :param count: maximum number of projects to fetch
    :param session: :external+aiohttp:py:mod:`aiohttp` client session

    :raises repology_client.exceptions.InvalidInput: if ``repo`` is an empty
        string
    :raises repology_client.exceptions.EmptyResponse: on empty response
    :raises repology_client.exceptions.RepoNotFound: when there is no such repo
        on Repology
    :raises aiohttp.ClientResponseError: on HTTP errors (except 404)

    :returns: sequence of problems
    """

    if not repo:
        raise InvalidInput(f"Not a valid repository name: {repo}")

    if count > HARD_LIMIT:
        warnings.warn(f"Resetting count to {HARD_LIMIT} to prevent API abuse")
        count = HARD_LIMIT

    endpoint = URL(API_V1_URL) / "repository" / repo / "problems"
    if maintainer:
        endpoint = URL(API_V1_URL) / "maintainer" / maintainer / "problems-for-repo" / repo

    query = {}
    if start:
        query["start"] = start

    result: list[Problem] = []
    async with ensure_session(session) as aiohttp_session:
        while True:
            try:
                batch = get_type_adapter(Sequence[Problem]).validate_python(
                    await api(endpoint.with_query(query), session=aiohttp_session)
                )
            except aiohttp.ClientResponseError as err:
                if err.status == 404:
                    raise RepoNotFound(repo) from err
                raise

            # XXX: Remove duplicates to work around buggy paging.
            previous_page = result[-MAX_PROBLEMS:]
            for problem in batch:
                if problem not in previous_page:
                    result.append(problem)

            if len(result) >= count:
                break
            if len(batch) == MAX_PROBLEMS:
                # we probably hit API limits, so…
                # …choose lexicographically highest project as a new start
                query["start"] = max(item.project_name for item in batch)
            else:
                break

    return result
