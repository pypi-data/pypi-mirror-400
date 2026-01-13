"""Type stubs for DIAMETER_FILTER category."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hfortix_core.http.interface import IHTTPClient
    from .profile import Profile


class DiameterFilter:
    """Type stub for DiameterFilter."""

    profile: Profile

    def __init__(self, client: IHTTPClient) -> None: ...
