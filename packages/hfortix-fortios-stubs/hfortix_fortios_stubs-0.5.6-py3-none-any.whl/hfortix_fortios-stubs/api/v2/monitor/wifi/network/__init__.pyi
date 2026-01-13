"""Type stubs for NETWORK category."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hfortix_core.http.interface import IHTTPClient
    from .connect import Connect
    from .list import List
    from .scan import Scan
    from .status import Status


class Network:
    """Type stub for Network."""

    connect: Connect
    list: List
    scan: Scan
    status: Status

    def __init__(self, client: IHTTPClient) -> None: ...
