"""Type stubs for DNSFILTER category."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hfortix_core.http.interface import IHTTPClient
    from .domain_filter import DomainFilter
    from .profile import Profile


class Dnsfilter:
    """Type stub for Dnsfilter."""

    domain_filter: DomainFilter
    profile: Profile

    def __init__(self, client: IHTTPClient) -> None: ...
