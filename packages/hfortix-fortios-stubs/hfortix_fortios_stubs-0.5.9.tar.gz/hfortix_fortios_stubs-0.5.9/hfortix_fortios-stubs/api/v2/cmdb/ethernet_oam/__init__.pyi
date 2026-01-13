"""Type stubs for ETHERNET_OAM category."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hfortix_core.http.interface import IHTTPClient
    from .cfm import Cfm


class EthernetOam:
    """Type stub for EthernetOam."""

    cfm: Cfm

    def __init__(self, client: IHTTPClient) -> None: ...
