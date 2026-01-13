"""Type stubs for GEOIP category."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hfortix_core.http.interface import IHTTPClient
    from .geoip_query import GeoipQuery


class Geoip:
    """Type stub for Geoip."""

    geoip_query: GeoipQuery

    def __init__(self, client: IHTTPClient) -> None: ...
