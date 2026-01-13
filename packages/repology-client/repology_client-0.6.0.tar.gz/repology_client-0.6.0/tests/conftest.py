# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2024 Anna <cyber@sysrq.in>

from collections.abc import AsyncGenerator

import aiohttp
import pytest_asyncio

from repology_client.constants import USER_AGENT


@pytest_asyncio.fixture(scope="session")
async def session() -> AsyncGenerator[aiohttp.ClientSession, None]:
    timeout = aiohttp.ClientTimeout(total=30)
    headers = {"user-agent": USER_AGENT}
    test_session = aiohttp.ClientSession(headers=headers, timeout=timeout)
    try:
        yield test_session
    finally:
        await test_session.close()
