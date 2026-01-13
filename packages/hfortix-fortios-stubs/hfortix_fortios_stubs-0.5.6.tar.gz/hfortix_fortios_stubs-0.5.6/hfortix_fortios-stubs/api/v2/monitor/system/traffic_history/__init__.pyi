"""Type stubs for TRAFFIC_HISTORY category."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hfortix_core.http.interface import IHTTPClient
    from .enable_app_bandwidth_tracking import EnableAppBandwidthTracking
    from .interface import Interface
    from .top_applications import TopApplications


class TrafficHistory:
    """Type stub for TrafficHistory."""

    enable_app_bandwidth_tracking: EnableAppBandwidthTracking
    interface: Interface
    top_applications: TopApplications

    def __init__(self, client: IHTTPClient) -> None: ...
