"""Type stubs for LLDP category."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hfortix_core.http.interface import IHTTPClient
    from .network_policy import NetworkPolicy


class Lldp:
    """Type stub for Lldp."""

    network_policy: NetworkPolicy

    def __init__(self, client: IHTTPClient) -> None: ...
