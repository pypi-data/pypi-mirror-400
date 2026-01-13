"""Type stubs for GEOIP_QUERY category."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hfortix_core.http.interface import IHTTPClient
    from .select import Select


class GeoipQuery:
    """Type stub for GeoipQuery."""

    select: Select

    def __init__(self, client: IHTTPClient) -> None: ...
