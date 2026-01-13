"""Type stubs for CMDB category."""

from __future__ import annotations

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from hfortix_core.http.interface import IHTTPClient
    from . import alertemail
    from . import antivirus
    from . import application
    from . import authentication
    from . import automation
    from . import casb
    from . import certificate
    from . import diameter_filter
    from . import dlp
    from . import dnsfilter
    from . import emailfilter
    from . import endpoint_control
    from . import ethernet_oam
    from . import extension_controller
    from . import file_filter
    from . import firewall
    from . import ftp_proxy
    from . import icap
    from . import ips
    from . import log
    from . import monitoring
    from . import report
    from . import router
    from . import rule
    from . import sctp_filter
    from . import switch_controller
    from . import system
    from . import user
    from . import videofilter
    from . import virtual_patch
    from . import voip
    from . import vpn
    from . import waf
    from . import web_proxy
    from . import webfilter
    from . import wireless_controller
    from . import ztna


class CMDB:
    """Type stub for CMDB."""


    def __init__(self, client: IHTTPClient) -> None: ...
