"""Type stubs for CENTRAL_MANAGEMENT category."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hfortix_core.http.interface import IHTTPClient
    from .status import Status


class CentralManagement:
    """Type stub for CentralManagement."""

    status: Status

    def __init__(self, client: IHTTPClient) -> None: ...
