"""Type stubs for LLDP category."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hfortix_core.http.interface import IHTTPClient
    from .neighbors import Neighbors
    from .ports import Ports


class Lldp:
    """Type stub for Lldp."""

    neighbors: Neighbors
    ports: Ports

    def __init__(self, client: IHTTPClient) -> None: ...
