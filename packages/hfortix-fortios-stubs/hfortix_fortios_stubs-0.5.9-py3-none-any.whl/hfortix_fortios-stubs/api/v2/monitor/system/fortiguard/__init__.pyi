"""Type stubs for FORTIGUARD category."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hfortix_core.http.interface import IHTTPClient
    from .clear_statistics import ClearStatistics
    from .manual_update import ManualUpdate
    from .server_info import ServerInfo
    from .test_availability import TestAvailability
    from .update import Update


class Fortiguard:
    """Type stub for Fortiguard."""

    clear_statistics: ClearStatistics
    manual_update: ManualUpdate
    server_info: ServerInfo
    test_availability: TestAvailability
    update: Update

    def __init__(self, client: IHTTPClient) -> None: ...
