"""Type stubs for IPAM category."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hfortix_core.http.interface import IHTTPClient
    from .list import List
    from .status import Status
    from .utilization import Utilization


class Ipam:
    """Type stub for Ipam."""

    list: List
    status: Status
    utilization: Utilization

    def __init__(self, client: IHTTPClient) -> None: ...
