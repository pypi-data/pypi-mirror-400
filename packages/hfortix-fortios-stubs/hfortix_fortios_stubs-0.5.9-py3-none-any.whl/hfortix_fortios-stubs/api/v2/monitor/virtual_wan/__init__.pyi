"""Type stubs for VIRTUAL_WAN category."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hfortix_core.http.interface import IHTTPClient
    from .health_check import HealthCheck
    from .interface_log import InterfaceLog
    from .members import Members
    from .sla_log import SlaLog
    from .sladb import Sladb


class VirtualWan:
    """Type stub for VirtualWan."""

    health_check: HealthCheck
    interface_log: InterfaceLog
    members: Members
    sla_log: SlaLog
    sladb: Sladb

    def __init__(self, client: IHTTPClient) -> None: ...
