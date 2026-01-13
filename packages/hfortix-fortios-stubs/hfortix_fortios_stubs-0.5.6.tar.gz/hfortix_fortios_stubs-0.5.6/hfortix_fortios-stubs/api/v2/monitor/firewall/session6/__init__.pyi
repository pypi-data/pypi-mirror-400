"""Type stubs for SESSION6 category."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hfortix_core.http.interface import IHTTPClient
    from .close_multiple import CloseMultiple


class Session6:
    """Type stub for Session6."""

    close_multiple: CloseMultiple

    def __init__(self, client: IHTTPClient) -> None: ...
