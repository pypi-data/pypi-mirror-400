"""Type stubs for SDWAN category."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hfortix_core.http.interface import IHTTPClient
    from .link_monitor_metrics import LinkMonitorMetrics


class Sdwan:
    """Type stub for Sdwan."""

    link_monitor_metrics: LinkMonitorMetrics

    def __init__(self, client: IHTTPClient) -> None: ...
