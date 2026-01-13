"""Type stubs for QUERY category."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hfortix_core.http.interface import IHTTPClient
    from .abort import Abort


class Query:
    """Type stub for Query."""

    abort: Abort

    def __init__(self, client: IHTTPClient) -> None: ...
