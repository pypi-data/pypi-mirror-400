"""Type stubs for CMDB category."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hfortix_core.http.interface import IHTTPClient
    from .firewall.address import Firewall.address

__all__ = [
    "Firewall.address",
]

class Cmdb:
    """CMDB API category."""
    
    firewall.address: Firewall.address

    def __init__(self, client: IHTTPClient, vdom: str | None = None) -> None:
        """Initialize cmdb category with HTTP client."""
        ...