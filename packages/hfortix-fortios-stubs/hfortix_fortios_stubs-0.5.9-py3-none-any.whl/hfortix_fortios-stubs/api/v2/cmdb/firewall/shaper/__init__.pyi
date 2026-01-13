"""Type stubs for SHAPER category."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hfortix_core.http.interface import IHTTPClient
    from .per_ip_shaper import PerIpShaper
    from .traffic_shaper import TrafficShaper


class Shaper:
    """Type stub for Shaper."""

    per_ip_shaper: PerIpShaper
    traffic_shaper: TrafficShaper

    def __init__(self, client: IHTTPClient) -> None: ...
