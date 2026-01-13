"""Type stubs for COM_LOG category."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hfortix_core.http.interface import IHTTPClient
    from .download import Download
    from .dump import Dump
    from .update import Update


class ComLog:
    """Type stub for ComLog."""

    download: Download
    dump: Dump
    update: Update

    def __init__(self, client: IHTTPClient) -> None: ...
