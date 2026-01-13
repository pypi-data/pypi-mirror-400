"""Type stubs for LOG endpoint."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from hfortix_core.http.interface import IHTTPClient


class Search:
    """Type stub for Search."""

    status: SearchStatus

    def __init__(self, client: IHTTPClient) -> None: ...

class SearchStatus:
    """Type stub for SearchStatus."""

    def __init__(self, client: IHTTPClient) -> None: ...
