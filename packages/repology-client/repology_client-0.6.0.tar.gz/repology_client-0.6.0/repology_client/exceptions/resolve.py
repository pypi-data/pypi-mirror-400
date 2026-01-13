# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2024 Anna <cyber@sysrq.in>

"""
Exceptions that can be raised by the "Project by package name" tool.
"""

from collections.abc import Iterable

from repology_client.exceptions import RepologyException
from repology_client.types import _ResolvePkg


class PackageResolveException(RepologyException):
    """
    Base class for all exceptions related to the "Project by package name" tool.
    """

    def __init__(self, pkg: _ResolvePkg, message: str | None = None):
        if message is None:
            message = f"Exception occured while resolving {pkg!s}"
        super().__init__(message)
        self._pkg = pkg

    @property
    def pkg(self) -> _ResolvePkg:
        """
        Underlying :py:class:`repology_client.types._ResolvePkg` object.
        """
        return self._pkg


class ProjectNotFound(PackageResolveException):
    """
    Raised if Repology was requested to get project by package name but
    responded with the "404 Not Found" HTTP code.
    """

    def __init__(self, pkg: _ResolvePkg):
        message = f"No projects found for {pkg!s}"
        super().__init__(pkg, message)


class MultipleProjectsFound(PackageResolveException):
    """
    Raised if Repology was requested to get project by package name without
    automatic ambiguity resolution and responded with multiple results.

    Instances of this exception contain all project names returned by Repology.
    """

    def __init__(self, pkg: _ResolvePkg, names: Iterable[str]):
        message = f"Multiple projects found for {pkg!s}"
        super().__init__(pkg, message)

        self._names = tuple(names)

    @property
    def names(self) -> tuple[str, ...]:
        """
        Project names returned by Repology.
        """
        return self._names
