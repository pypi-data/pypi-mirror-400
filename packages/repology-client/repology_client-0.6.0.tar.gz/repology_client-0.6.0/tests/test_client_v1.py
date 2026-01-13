# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2024 Anna <cyber@sysrq.in>

import uuid

import aiohttp
import pytest
from yarl import URL

import repology_client
from repology_client.constants import API_V1_URL
from repology_client.exceptions import (
    EmptyResponse,
    InvalidInput,
    RepoNotFound,
)

import tests.common


@pytest.mark.vcr
@pytest.mark.asyncio
async def test_raw_api(session: aiohttp.ClientSession):
    url = URL(API_V1_URL) / "repository/freebsd/problems"
    problems = await repology_client.api(url, session=session)
    assert isinstance(problems, list)
    assert len(problems) != 0


@pytest.mark.vcr
@pytest.mark.asyncio
async def test_get_packages_empty(session: aiohttp.ClientSession):
    with pytest.raises(InvalidInput):
        await repology_client.get_packages("", session=session)


@pytest.mark.vcr
@pytest.mark.asyncio
async def test_get_packages_notfound(session: aiohttp.ClientSession):
    with pytest.raises(EmptyResponse):
        project = uuid.uuid5(uuid.NAMESPACE_DNS, "repology.org").hex
        await repology_client.get_packages(project, session=session)


@pytest.mark.vcr
@pytest.mark.asyncio
async def test_get_packages(session: aiohttp.ClientSession):
    packages = await repology_client.get_packages("firefox", session=session)
    tests.common.check_firefox_project(packages)


@pytest.mark.vcr
@pytest.mark.asyncio
async def test_get_projects_simple(session: aiohttp.ClientSession):
    projects = await repology_client.get_projects(count=200, session=session)
    assert len(projects) == 200


@pytest.mark.vcr
@pytest.mark.asyncio
async def test_get_400_projects(session: aiohttp.ClientSession):
    projects = await repology_client.get_projects(count=400, session=session)
    assert len(projects) > 200


@pytest.mark.vcr
@pytest.mark.asyncio
async def test_get_projects_start_and_end(session: aiohttp.ClientSession):
    with pytest.warns(UserWarning):
        await repology_client.get_projects("a", "b", session=session)


@pytest.mark.vcr
@pytest.mark.asyncio
async def test_get_projects_search_failed(session: aiohttp.ClientSession):
    with pytest.raises(EmptyResponse):
        project = uuid.uuid5(uuid.NAMESPACE_DNS, "repology.org").hex
        await repology_client.get_projects(search=project, session=session)


@pytest.mark.vcr
@pytest.mark.asyncio
async def test_get_projects_search(session: aiohttp.ClientSession):
    projects = await repology_client.get_projects(search="firefox", session=session)
    assert "firefox" in projects


@pytest.mark.vcr
@pytest.mark.asyncio
async def test_get_problems_empty(session: aiohttp.ClientSession):
    with pytest.raises(InvalidInput):
        await repology_client.get_problems("", session=session)


@pytest.mark.vcr
@pytest.mark.skip(reason="vcrpy doesn't record a cassette")
@pytest.mark.asyncio
async def test_get_problems_notfound(session: aiohttp.ClientSession):
    repo = uuid.uuid5(uuid.NAMESPACE_DNS, "repology.org").hex
    with pytest.raises(RepoNotFound):
        await repology_client.get_problems(repo, session=session)


@pytest.mark.vcr
@pytest.mark.asyncio
async def test_get_problems_simple(session: aiohttp.ClientSession):
    problems = await repology_client.get_problems("freebsd", session=session)
    assert len(problems) == 200


@pytest.mark.vcr
@pytest.mark.asyncio
async def test_get_400_problems(session: aiohttp.ClientSession):
    problems = await repology_client.get_problems("freebsd", count=400, session=session)
    assert len(problems) > 200

    # Make sure there are no duplicates
    for item in problems:
        assert problems.count(item) == 1


@pytest.mark.vcr
@pytest.mark.asyncio
async def test_get_maintainer_problems(session: aiohttp.ClientSession):
    problems = await repology_client.get_problems("freebsd",
                                                  maintainer="ports@freebsd.org",
                                                  session=session)
    assert len(problems) == 200


@pytest.mark.vcr
@pytest.mark.asyncio
async def test_get_400_maintainer_problems(session: aiohttp.ClientSession):
    problems = await repology_client.get_problems("freebsd", count=400,
                                                  maintainer="ports@freebsd.org",
                                                  session=session)
    assert len(problems) > 200

    # Make sure there are no duplicates
    for item in problems:
        assert problems.count(item) == 1
