"""Type stubs for PROCESS category."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hfortix_core.http.interface import IHTTPClient
    from .kill import Kill


class Process:
    """Type stub for Process."""

    kill: Kill

    def __init__(self, client: IHTTPClient) -> None: ...
