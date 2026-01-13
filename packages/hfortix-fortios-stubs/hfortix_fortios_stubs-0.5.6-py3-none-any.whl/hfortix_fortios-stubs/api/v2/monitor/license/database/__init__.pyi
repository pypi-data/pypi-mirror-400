"""Type stubs for DATABASE category."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hfortix_core.http.interface import IHTTPClient
    from .upgrade import Upgrade


class Database:
    """Type stub for Database."""

    upgrade: Upgrade

    def __init__(self, client: IHTTPClient) -> None: ...
