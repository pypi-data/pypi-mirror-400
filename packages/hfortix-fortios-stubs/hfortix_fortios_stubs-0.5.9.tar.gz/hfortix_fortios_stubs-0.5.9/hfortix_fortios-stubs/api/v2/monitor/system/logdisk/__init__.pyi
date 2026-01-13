"""Type stubs for LOGDISK category."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hfortix_core.http.interface import IHTTPClient
    from .format import Format


class Logdisk:
    """Type stub for Logdisk."""

    format: Format

    def __init__(self, client: IHTTPClient) -> None: ...
