"""Type stubs for NETWORK category."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hfortix_core.http.interface import IHTTPClient
    from .arp import Arp
    from .reverse_ip_lookup import ReverseIpLookup
    from .ddns import Ddns
    from .debug_flow import DebugFlow
    from .dns import Dns
    from .fortiguard import Fortiguard
    from .lldp import Lldp


class Network:
    """Type stub for Network."""

    ddns: Ddns
    debug_flow: DebugFlow
    dns: Dns
    fortiguard: Fortiguard
    lldp: Lldp
    arp: Arp
    reverse_ip_lookup: ReverseIpLookup

    def __init__(self, client: IHTTPClient) -> None: ...
