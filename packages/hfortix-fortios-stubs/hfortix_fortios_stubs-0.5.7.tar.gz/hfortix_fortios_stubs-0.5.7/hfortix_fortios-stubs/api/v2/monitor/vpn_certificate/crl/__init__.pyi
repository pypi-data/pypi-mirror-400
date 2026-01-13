"""Type stubs for CRL category."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hfortix_core.http.interface import IHTTPClient
    from .import_ import Import


class Crl:
    """Type stub for Crl."""

    import_: Import

    def __init__(self, client: IHTTPClient) -> None: ...
