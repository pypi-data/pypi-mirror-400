"""Type stubs for CA category."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hfortix_core.http.interface import IHTTPClient
    from .import_ import Import


class Ca:
    """Type stub for Ca."""

    import_: Import

    def __init__(self, client: IHTTPClient) -> None: ...
