# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2024-2025 Anna <cyber@sysrq.in>

"""
Hardcoded constants for Repology API.
"""

#: Library package name.
PACKAGE = "repology-client"

#: Library version.
VERSION = "0.6.0"

#: Library homepage.
HOMEPAGE = "https://repology-client.sysrq.in"

#: Library's User-agent header
USER_AGENT = f"Mozilla/5.0 (compatible; {PACKAGE}/{VERSION}; +{HOMEPAGE})"

#: Base URL for API v1 requests.
API_V1_URL = "https://repology.org/api/v1"

#: Base URL for the "Project by package name" tool.
TOOL_PROJECT_BY_URL = "https://repology.org/tools/project-by"

#: Maximum number of projects API can return.
MAX_PROJECTS = 200

#: Maximum number of problems API can return.
MAX_PROBLEMS = 200

#: Number of projects, starting from which you should use bulk export instead.
HARD_LIMIT = 5_000
