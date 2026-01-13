"""Type stubs for WEBPROXY category."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hfortix_core.http.interface import IHTTPClient
    from .pacfile import Pacfile


class Webproxy:
    """Type stub for Webproxy."""

    pacfile: Pacfile

    def __init__(self, client: IHTTPClient) -> None: ...
