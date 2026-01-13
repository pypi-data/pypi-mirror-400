"""Type stubs for CSR category."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hfortix_core.http.interface import IHTTPClient
    from .generate import Generate


class Csr:
    """Type stub for Csr."""

    generate: Generate

    def __init__(self, client: IHTTPClient) -> None: ...
