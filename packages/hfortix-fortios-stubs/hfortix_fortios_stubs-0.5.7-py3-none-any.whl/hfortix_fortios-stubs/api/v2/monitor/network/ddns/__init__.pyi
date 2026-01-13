"""Type stubs for DDNS category."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hfortix_core.http.interface import IHTTPClient
    from .lookup import Lookup
    from .servers import Servers


class Ddns:
    """Type stub for Ddns."""

    lookup: Lookup
    servers: Servers

    def __init__(self, client: IHTTPClient) -> None: ...
