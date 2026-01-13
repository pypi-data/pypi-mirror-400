"""Type stubs for FORTIGUARD category."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hfortix_core.http.interface import IHTTPClient
    from .live_services_latency import LiveServicesLatency


class Fortiguard:
    """Type stub for Fortiguard."""

    live_services_latency: LiveServicesLatency

    def __init__(self, client: IHTTPClient) -> None: ...
