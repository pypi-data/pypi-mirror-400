# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2024-2025 Anna <cyber@sysrq.in>

"""
Exceptions this library can raise.
"""


class RepologyException(Exception):
    """
    Base class for all our exceptions. Pinkie promise.
    """


class InvalidInput(RepologyException):
    """
    A function was given invalid parameters.
    """


class EmptyResponse(RepologyException):
    """
    Raised if API returned empty object. Is it an error or everything's correct,
    just nothing matched your search criteria? Who knows.
    """


class RepoNotFound(RepologyException):
    """
    Raised if Repology could not find the requested repository and returned
    "404 Not Found" HTTP code.
    """

    def __init__(self, repo: str):
        super().__init__(f"Repository not found: {repo}")
