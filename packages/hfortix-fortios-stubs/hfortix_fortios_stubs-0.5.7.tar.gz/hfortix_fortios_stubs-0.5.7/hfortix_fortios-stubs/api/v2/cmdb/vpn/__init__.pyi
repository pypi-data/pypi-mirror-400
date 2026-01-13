"""Type stubs for VPN category."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hfortix_core.http.interface import IHTTPClient
    from .kmip_server import KmipServer
    from .l2tp import L2tp
    from .pptp import Pptp
    from .qkd import Qkd
    from .certificate import Certificate
    from .ipsec import Ipsec


class Vpn:
    """Type stub for Vpn."""

    certificate: Certificate
    ipsec: Ipsec
    kmip_server: KmipServer
    l2tp: L2tp
    pptp: Pptp
    qkd: Qkd

    def __init__(self, client: IHTTPClient) -> None: ...
