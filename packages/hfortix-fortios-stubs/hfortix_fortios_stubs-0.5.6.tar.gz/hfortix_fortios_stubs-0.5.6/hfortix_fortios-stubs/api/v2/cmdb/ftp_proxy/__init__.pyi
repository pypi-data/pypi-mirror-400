"""Type stubs for FTP_PROXY category."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hfortix_core.http.interface import IHTTPClient
    from .explicit import Explicit


class FtpProxy:
    """Type stub for FtpProxy."""

    explicit: Explicit

    def __init__(self, client: IHTTPClient) -> None: ...
