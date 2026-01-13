"""Type stubs for CUSTOM_LANGUAGE category."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hfortix_core.http.interface import IHTTPClient
    from .create import Create
    from .download import Download
    from .update import Update


class CustomLanguage:
    """Type stub for CustomLanguage."""

    create: Create
    download: Download
    update: Update

    def __init__(self, client: IHTTPClient) -> None: ...
