"""Type stubs for SESSION category."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hfortix_core.http.interface import IHTTPClient
    from .close import Close
    from .close_all import CloseAll
    from .close_multiple import CloseMultiple


class Session:
    """Type stub for Session."""

    close: Close
    close_all: CloseAll
    close_multiple: CloseMultiple

    def __init__(self, client: IHTTPClient) -> None: ...
