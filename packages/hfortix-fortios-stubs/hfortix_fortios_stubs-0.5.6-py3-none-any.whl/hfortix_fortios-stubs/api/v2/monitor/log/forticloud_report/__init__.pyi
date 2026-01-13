"""Type stubs for FORTICLOUD_REPORT category."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hfortix_core.http.interface import IHTTPClient
    from .download import Download


class ForticloudReport:
    """Type stub for ForticloudReport."""

    download: Download

    def __init__(self, client: IHTTPClient) -> None: ...
