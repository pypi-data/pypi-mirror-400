"""Type stubs for PACFILE category."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hfortix_core.http.interface import IHTTPClient
    from .download import Download
    from .upload import Upload


class Pacfile:
    """Type stub for Pacfile."""

    download: Download
    upload: Upload

    def __init__(self, client: IHTTPClient) -> None: ...
