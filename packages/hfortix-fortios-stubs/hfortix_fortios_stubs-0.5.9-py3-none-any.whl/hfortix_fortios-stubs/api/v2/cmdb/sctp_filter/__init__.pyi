"""Type stubs for SCTP_FILTER category."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hfortix_core.http.interface import IHTTPClient
    from .profile import Profile


class SctpFilter:
    """Type stub for SctpFilter."""

    profile: Profile

    def __init__(self, client: IHTTPClient) -> None: ...
