"""Type stubs for DEBUG category."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hfortix_core.http.interface import IHTTPClient
    from .download import Download


class Debug:
    """Type stub for Debug."""

    download: Download

    def __init__(self, client: IHTTPClient) -> None: ...
