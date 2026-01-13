# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2024-2026 Anna <cyber@sysrq.in>

"""
Common code for Repology API clients.
"""

import aiohttp
from pydantic import JsonValue
from pydantic_core import from_json
from yarl import URL

from repology_client.exceptions import EmptyResponse
from repology_client.utils import ensure_session, limit


@limit(calls=1, period=1.25)
async def _call(url: URL, *,
                session: aiohttp.ClientSession | None = None) -> bytes:
    """
    Do a single rate-limited request.

    :param url: URL location
    :param session: :external+aiohttp:py:mod:`aiohttp` client session

    :raises repology_client.exceptions.EmptyResponse: on empty response
    :raises aiohttp.ClientResponseError: on HTTP errors

    :returns: raw response
    """

    async with ensure_session(session) as aiohttp_session:
        async with aiohttp_session.get(url, raise_for_status=True) as response:
            data = await response.read()
            if not data:
                raise EmptyResponse

    return data


async def api(url: URL, *,
              session: aiohttp.ClientSession | None = None) -> JsonValue:
    """
    Do a single API request.

    :param url: full URL (including a query string)
    :param session: :external+aiohttp:py:mod:`aiohttp` client session

    :raises repology_client.exceptions.EmptyResponse: on empty response
    :raises aiohttp.ClientResponseError: on HTTP errors
    :raises ValueError: on JSON decode failure

    :returns: decoded JSON response
    """

    raw_data = await _call(url, session=session)
    data = from_json(raw_data)
    if not data:
        raise EmptyResponse

    return data
