# SPDX-License-Identifier: EUPL-1.2 AND CC-BY-SA-3.0
# SPDX-FileCopyrightText: 2024-2026 Anna <cyber@sysrq.in>
# SPDX-FileCopyrightText: 2017 Mark Amery <markrobertamery@gmail.com>

"""
Utility functions and classes.
"""

import asyncio
import functools
import time
from collections.abc import AsyncGenerator, Awaitable, Callable
from contextlib import asynccontextmanager

import aiohttp
from pydantic import TypeAdapter, validate_call

from repology_client.constants import USER_AGENT
from repology_client.types import LinkStatus, _LinkStatusCodes


@functools.cache
def get_type_adapter[T](t: type[T]) -> TypeAdapter[T]:
    """
    Get a cached :class:`TypeAdapter` instance.

    :param t: type
    """

    return TypeAdapter(t)


class limit():
    """
    Decorator to set a limit on requests per second.

    Based on `this StackOverflow answer`__.

    __ https://stackoverflow.com/a/62503115/4257264
    """

    def __init__(self, calls: int, period: float):
        """
        :param calls: number of calls
        :param period: time period in seconds
        """
        self.calls: int = calls
        self.period: float = period
        self.clock: Callable[[], float] = time.monotonic
        self.last_reset: float = 0.0
        self.num_calls: int = 0

    def __call__[**P, T](
        self, func: Callable[P, Awaitable[T]]
    ) -> Callable[P, Awaitable[T]]:
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            if self.num_calls >= self.calls:
                await asyncio.sleep(self.__period_remaining())

            period_remaining = self.__period_remaining()

            if period_remaining <= 0:
                self.num_calls = 0
                self.last_reset = self.clock()

            self.num_calls += 1

            return await func(*args, **kwargs)

        return wrapper

    def __period_remaining(self) -> float:
        elapsed = self.clock() - self.last_reset
        return self.period - elapsed


@asynccontextmanager
async def ensure_session(
    session: aiohttp.ClientSession | None = None
) -> AsyncGenerator[aiohttp.ClientSession, None]:
    """
    Create a new client session, if necessary, and close it on exit.

    :param session: :external+aiohttp:py:mod:`aiohttp` client session
    """

    keep_session = True
    if session is None:
        timeout = aiohttp.ClientTimeout(total=30)
        headers = {"user-agent": USER_AGENT}
        session = aiohttp.ClientSession(headers=headers, timeout=timeout)
        keep_session = False

    try:
        yield session
    finally:
        if not keep_session:
            await session.close()


@validate_call
def format_link_status(code: int) -> str:
    """
    Convert status codes to human-readable messages.

    .. seealso::

       :py:func:`repology_client.get_problems` function
          Implements ``/api/v1/repository/<repo>/problems`` and
          ``/api/v1/maintainer/<maint>/problems-for-repo/<repo>`` endpoints.

       :py:class:`repology_client.types.Problem` class

    >>> format_link_status(404)
    'HTTP 404'
    >>> format_link_status(-100)
    'connect timeout (60 seconds)'
    >>> format_link_status(-999)
    'unknown status code -999, please report a bug to repology-client'
    """

    result: LinkStatus

    # HTTP status codes
    if code > 0:
        result = LinkStatus(code)
    else:
        try:
            result = _LinkStatusCodes(code).value
        except ValueError:
            result = LinkStatus(code, f"unknown status code {code}, please "
                                      "report a bug to repology-client")

    return str(result)
