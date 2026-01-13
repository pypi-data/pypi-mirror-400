"""Type stubs for PTP category."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hfortix_core.http.interface import IHTTPClient
    from .interface_policy import InterfacePolicy
    from .profile import Profile


class Ptp:
    """Type stub for Ptp."""

    interface_policy: InterfacePolicy
    profile: Profile

    def __init__(self, client: IHTTPClient) -> None: ...
