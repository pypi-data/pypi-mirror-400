# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2024 Anna <cyber@sysrq.in>

import uuid

import aiohttp
import pytest

import repology_client
from repology_client.exceptions.resolve import (
    MultipleProjectsFound,
    ProjectNotFound,
)
from repology_client.types import ResolvePackageType

import tests.common


@pytest.mark.vcr
@pytest.mark.skip(reason="vcrpy doesn't record a cassette")
@pytest.mark.asyncio
async def test_resolve_package_notfound(session: aiohttp.ClientSession):
    with pytest.raises(ProjectNotFound):
        repo = uuid.uuid5(uuid.NAMESPACE_DNS, "invalid.domain").hex
        await repology_client.resolve_package(repo, "firefox", session=session)

    with pytest.raises(ProjectNotFound):
        project = uuid.uuid5(uuid.NAMESPACE_DNS, "repology.org").hex
        await repology_client.resolve_package("freebsd", project, session=session)


@pytest.mark.vcr
@pytest.mark.asyncio
async def test_resolve_package_multiple(session: aiohttp.ClientSession):
    with pytest.raises(MultipleProjectsFound) as exc:
        # example from https://github.com/renovatebot/renovate/issues/11435
        await repology_client.resolve_package(
            "ubuntu_20_04", "gcc", ResolvePackageType.BINARY,
            autoresolve=False, session=session
        )
    assert sorted(exc.value.names) == ["gcc-defaults", "gcc-defaults-mipsen"]


@pytest.mark.vcr
@pytest.mark.asyncio
async def test_resolve_package(session: aiohttp.ClientSession):
    packages = await repology_client.resolve_package("freebsd", "www/firefox",
                                                     session=session)
    tests.common.check_firefox_project(packages)
