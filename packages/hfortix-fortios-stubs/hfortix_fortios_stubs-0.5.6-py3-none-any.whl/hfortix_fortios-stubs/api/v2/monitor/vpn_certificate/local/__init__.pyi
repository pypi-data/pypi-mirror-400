"""Type stubs for LOCAL category."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hfortix_core.http.interface import IHTTPClient
    from .create import Create
    from .import_ import Import


class Local:
    """Type stub for Local."""

    create: Create
    import_: Import

    def __init__(self, client: IHTTPClient) -> None: ...
