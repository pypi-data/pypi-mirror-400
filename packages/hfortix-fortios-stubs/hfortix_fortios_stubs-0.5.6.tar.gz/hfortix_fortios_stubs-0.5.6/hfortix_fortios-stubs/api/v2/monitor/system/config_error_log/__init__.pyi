"""Type stubs for CONFIG_ERROR_LOG category."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hfortix_core.http.interface import IHTTPClient
    from .download import Download


class ConfigErrorLog:
    """Type stub for ConfigErrorLog."""

    download: Download

    def __init__(self, client: IHTTPClient) -> None: ...
