"""Type stubs for SDWAN category."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hfortix_core.http.interface import IHTTPClient
    from .routes import Routes
    from .routes6 import Routes6
    from .routes_statistics import RoutesStatistics


class Sdwan:
    """Type stub for Sdwan."""

    routes: Routes
    routes6: Routes6
    routes_statistics: RoutesStatistics

    def __init__(self, client: IHTTPClient) -> None: ...
