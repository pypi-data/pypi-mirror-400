"""Type stubs for LINK_MONITOR_METRICS category."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hfortix_core.http.interface import IHTTPClient
    from .report import Report


class LinkMonitorMetrics:
    """Type stub for LinkMonitorMetrics."""

    report: Report

    def __init__(self, client: IHTTPClient) -> None: ...
