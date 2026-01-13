"""Type stubs for OBJECT category."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hfortix_core.http.interface import IHTTPClient
    from .usage import Usage


class Object:
    """Type stub for Object."""

    usage: Usage

    def __init__(self, client: IHTTPClient) -> None: ...
