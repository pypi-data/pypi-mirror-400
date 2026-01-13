"""Type stubs for VPN category."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hfortix_core.http.interface import IHTTPClient
    from .ike import Ike
    from .ipsec import Ipsec
    from .ssl import Ssl


class Vpn:
    """Type stub for Vpn."""

    ike: Ike
    ipsec: Ipsec
    ssl: Ssl

    def __init__(self, client: IHTTPClient) -> None: ...
