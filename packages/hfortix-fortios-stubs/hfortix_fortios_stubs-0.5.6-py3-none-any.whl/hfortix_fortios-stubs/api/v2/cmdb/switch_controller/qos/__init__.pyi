"""Type stubs for QOS category."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hfortix_core.http.interface import IHTTPClient
    from .dot1p_map import Dot1pMap
    from .ip_dscp_map import IpDscpMap
    from .qos_policy import QosPolicy
    from .queue_policy import QueuePolicy


class Qos:
    """Type stub for Qos."""

    dot1p_map: Dot1pMap
    ip_dscp_map: IpDscpMap
    qos_policy: QosPolicy
    queue_policy: QueuePolicy

    def __init__(self, client: IHTTPClient) -> None: ...
