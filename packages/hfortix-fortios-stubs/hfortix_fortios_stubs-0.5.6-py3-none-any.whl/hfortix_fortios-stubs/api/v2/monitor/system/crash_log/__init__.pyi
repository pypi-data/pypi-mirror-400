"""Type stubs for CRASH_LOG category."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hfortix_core.http.interface import IHTTPClient
    from .clear import Clear
    from .download import Download


class CrashLog:
    """Type stub for CrashLog."""

    clear: Clear
    download: Download

    def __init__(self, client: IHTTPClient) -> None: ...
