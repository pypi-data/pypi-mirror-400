"""Type stubs for PROXY category."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hfortix_core.http.interface import IHTTPClient
    from .sessions import Sessions


class Proxy:
    """Type stub for Proxy."""

    sessions: Sessions

    def __init__(self, client: IHTTPClient) -> None: ...
