"""Type stubs for RESOURCE category."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hfortix_core.http.interface import IHTTPClient
    from .usage import Usage


class Resource:
    """Type stub for Resource."""

    usage: Usage

    def __init__(self, client: IHTTPClient) -> None: ...
