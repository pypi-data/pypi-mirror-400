"""Type stubs for CERTIFICATE category."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hfortix_core.http.interface import IHTTPClient
    from .download import Download
    from .read_info import ReadInfo


class Certificate:
    """Type stub for Certificate."""

    download: Download
    read_info: ReadInfo

    def __init__(self, client: IHTTPClient) -> None: ...
