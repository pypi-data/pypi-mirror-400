# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2024-2026 Anna <cyber@sysrq.in>

"""
Type definitions for Repology API.
"""

from enum import ReprEnum, StrEnum

from pydantic import BaseModel, ConfigDict, JsonValue


class ResolvePackageType(StrEnum):
    """
    Package type enum for the "Project by package name" tool.

    .. seealso::

       :py:func:`repology_client.tools.resolve_package` function
          Implements ``/tools/project-by`` endpoint.
    """

    SOURCE = "srcname"
    BINARY = "binname"


class _ResolvePkg(BaseModel):
    """
    Internal object used in the :py:func:`repology_client.resolve_package`
    function to pass data into exceptions.
    """
    model_config = ConfigDict(defer_build=True, frozen=True)

    #: Repository name.
    repo: str

    #: Package name.
    name: str

    #: Package type (source or binary).
    name_type: ResolvePackageType

    def __str__(self) -> str:
        message_tmpl = "*{}* package '{}' in repository '{}'"
        return message_tmpl.format(
            "binary" if self.name_type == ResolvePackageType.BINARY else "source",
            self.name, self.repo
        )


class ProjectsRange(BaseModel):
    """
    Object for constructing a string representation of range.

    >>> str(ProjectsRange())
    ''
    >>> str(ProjectsRange(start="firefox"))
    'firefox'
    >>> str(ProjectsRange(end="firefox"))
    '..firefox'
    >>> str(ProjectsRange(start="firefox", end="firefoxpwa"))
    'firefox..firefoxpwa'
    """
    model_config = ConfigDict(defer_build=True, extra="forbid",
                              validate_assignment=True)

    #: First project to be included in range.
    start: str = ""

    #: Last project to be included in range.
    end: str = ""

    def __bool__(self) -> bool:
        return bool(self.start or self.end)

    def __str__(self) -> str:
        if self.end:
            return f"{self.start}..{self.end}"
        if self.start:
            return self.start
        return ""


class Package(BaseModel):
    """
    Package description type.

    .. seealso::

       :py:func:`repology_client.get_packages` function
          Implements ``/api/v1/project/<project>`` endpoint.
       :py:func:`repology_client.get_projects` function
          Implements ``/api/v1/projects/`` endpoint.
    """
    model_config = ConfigDict(defer_build=True, frozen=True)

    # Required fields

    #: Name of repository for this package.
    repo: str
    #: Package name as shown to the user by Repology.
    visiblename: str
    #: Package version (sanitized, as shown by Repology).
    version: str
    #: Package status ('newest', 'unique', 'outdated', etc.).
    status: str

    # Optional fields

    #: Name of subrepository (if applicable).
    subrepo: str | None = None
    #: Package name as used in repository - source package name.
    srcname: str | None = None
    #: Package name as used in repository - binary package name.
    binname: str | None = None
    #: Package version as in repository.
    origversion: str | None = None
    #: One-line description of the package.
    summary: str | None = None
    #: List of package categories.
    categories: frozenset[str] | None = None
    #: List of package licenses.
    licenses: frozenset[str] | None = None
    #: List of package maintainers.
    maintainers: frozenset[str] | None = None


class Problem(BaseModel):
    """
    Type for repository problem entries.

    .. seealso::

       :py:func:`repology_client.get_problems` function
          Implements ``/api/v1/repository/<repo>/problems`` and
          ``/api/v1/maintainer/<maint>/problems-for-repo/<repo>`` endpoints.

       :py:func:`repology_client.utils.format_link_status` function
    """
    model_config = ConfigDict(defer_build=True, frozen=True)

    # Required fields

    #: Problem type.
    type: str
    #: Additional details on the problem.
    data: dict[str, JsonValue]
    #: Repology project name.
    project_name: str
    #: Normalized version as used by Repology.
    version: str
    #: Repository package version.
    rawversion: str

    # Optional fields

    #: Repository (source) package name.
    srcname: str | None = None
    #: Repository (binary) package name.
    binname: str | None = None


class LinkStatus(int):
    """
    Status code object for repository problems API.

    >>> a = LinkStatus(-1, "custom error")
    >>> b = LinkStatus(404)
    >>> str(a), a
    ('custom error', LinkStatus(code=-1, message='custom error'))
    >>> str(b), b
    ('HTTP 404', LinkStatus(code=404, message=None))
    """

    _message: str | None

    def __new__(cls, code: int, message: str | None = None) -> "LinkStatus":
        obj = int.__new__(cls, code)
        obj._message = message
        return obj

    def __str__(self) -> str:
        if self > 0:
            return f"HTTP {int(self)}"
        return str(self._message)

    def __repr__(self) -> str:
        return f"LinkStatus(code={int(self)}, message={self._message!r})"


class _LinkStatusCodes(LinkStatus, ReprEnum):
    """
    Some pre-defined status codes for repository problems API.

    Source: https://github.com/repology/repology-rs/blob/master/repology-common/src/link_status.rs
    """

    NotYetProcessed = (0, "not yet processed by the link checker")
    Skipped = (-1, "host manually excluded from link checking")
    OutOfSample = (-2, "link is subject to sampling, and is excluded from the sample")
    SatisfiedWithIpv6Success = (-3, "not checked because IPv6 check succeeded")
    UnsupportedScheme = (-4, "unsupported scheme")
    ProtocolDisabled = (-5, "protocol checking manually disabled")
    ProtocolDisabledForHost = (-6, "protocol checking manually disabled for the host")

    Timeout = (-100, "connect timeout (60 seconds)")
    InvalidUrl = (-101, "invalid URL")
    Blacklisted = (-102, "host is manually blacklisted")
    UnknownError = (-103, "unknown error")
    Hijacked = (-104, "domain was manually marked as expired, hijacked, sold, "
                      "or otherwise not related to the project")

    DnsError = (-200, "DNS error")
    DnsDomainNotFound = (-201, "DNS error: domain name not found")
    DnsNoAddressRecord = (-202, "DNS error: no address record")
    DnsRefused = (-203, "DNS error: could not contact DNS servers")
    DnsTimeout = (-204, "DNS error: timeout while contacting DNS servers")
    DnsIpv4MappedInAaaa = (-205, "DNS error: IPv4-mapped address in AAAA")
    NonGlobalIpAddress = (-206, "DNS error: domain maps to non-global IP address")
    InvalidCharactersInHostname = (-207, "DNS error: invalid charactars in hostname")
    InvalidHostname = (-208, "DNS error: invalid hostname")

    ConnectionRefused = (-300, "connection refused")
    HostUnreachable = (-301, "no route to host")
    ConnectionResetByPeer = (-302, "connection reset by peer")
    NetworkUnreachable = (-303, "network is unreachable")
    ServerDisconnected = (-304, "server disconnected")
    ConnectionAborted = (-305, "connection aborted")
    AddressNotAvailable = (-306, "address not available")

    TooManyRedirects = (-400, "too many redirects (possibly, a redirect loop)")
    BadHttp = (-401, "HTTP protocol error")
    RedirectToNonHttp = (-402, "Redirect to non-HTTP url (such as ftp://)")

    SslError = (-500, "SSL error")
    SslCertificateHasExpired = (-501, "SSL error: certificate has expired")
    SslCertificateHostnameMismatch = (-502, "SSL error: certificate issued "
                                            "for different hostname")
    SslCertificateSelfSigned = (-503, "SSL error: self signed certificate")
    SslHandshakeFailure = (-504, "SSL handshake failure")
    CertificateUnknownIssuer = (-505, "SSL error: invalid certificate: unknown issuer")
    InvalidCertificate = (-506, "SSL error: invalid certificate")
