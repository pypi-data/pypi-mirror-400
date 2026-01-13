"""Type stubs for MONITOR category."""

from __future__ import annotations

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from hfortix_core.http.interface import IHTTPClient
    from . import azure
    from . import casb
    from . import endpoint_control
    from . import extender_controller
    from . import extension_controller
    from . import firewall
    from . import firmware
    from . import fortiguard
    from . import fortiview
    from . import geoip
    from . import ips
    from . import license
    from . import log
    from . import network
    from . import registration
    from . import router
    from . import sdwan
    from . import service
    from . import switch_controller
    from . import system
    from . import user
    from . import utm
    from . import videofilter
    from . import virtual_wan
    from . import vpn
    from . import vpn_certificate
    from . import wanopt
    from . import web_ui
    from . import webcache
    from . import webfilter
    from . import webproxy
    from . import wifi


class Monitor:
    """Type stub for Monitor."""


    def __init__(self, client: IHTTPClient) -> None: ...
