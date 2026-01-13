"""Type stubs for OSPF category."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hfortix_core.http.interface import IHTTPClient
    from .neighbors import Neighbors


class Ospf:
    """Type stub for Ospf."""

    neighbors: Neighbors

    def __init__(self, client: IHTTPClient) -> None: ...
