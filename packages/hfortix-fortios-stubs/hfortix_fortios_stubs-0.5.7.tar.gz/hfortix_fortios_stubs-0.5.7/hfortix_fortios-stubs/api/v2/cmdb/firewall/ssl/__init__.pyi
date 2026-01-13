"""Type stubs for SSL category."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hfortix_core.http.interface import IHTTPClient
    from .setting import Setting


class Ssl:
    """Type stub for Ssl."""

    setting: Setting

    def __init__(self, client: IHTTPClient) -> None: ...
