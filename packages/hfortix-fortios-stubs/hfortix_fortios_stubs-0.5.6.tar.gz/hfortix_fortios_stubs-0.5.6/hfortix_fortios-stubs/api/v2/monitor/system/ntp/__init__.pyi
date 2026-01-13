"""Type stubs for NTP category."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hfortix_core.http.interface import IHTTPClient
    from .status import Status


class Ntp:
    """Type stub for Ntp."""

    status: Status

    def __init__(self, client: IHTTPClient) -> None: ...
