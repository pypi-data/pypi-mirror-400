# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2024-2026 Anna <cyber@sysrq.in>

"""
Asynchronous wrapper for Repology API.
"""

from repology_client._client import api
from repology_client._client.v1 import (
    get_packages,
    get_problems,
    get_projects,
)
from repology_client._client.tools import (
    resolve_package,
)

__all__ = [
    "api",
    "get_packages",
    "get_problems",
    "get_projects",
    "resolve_package",
]
