"""Type stubs for SANDBOX category."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hfortix_core.http.interface import IHTTPClient
    from .cloud_regions import CloudRegions
    from .connection import Connection
    from .detect import Detect
    from .stats import Stats
    from .status import Status


class Sandbox:
    """Type stub for Sandbox."""

    cloud_regions: CloudRegions
    connection: Connection
    detect: Detect
    stats: Stats
    status: Status

    def __init__(self, client: IHTTPClient) -> None: ...
