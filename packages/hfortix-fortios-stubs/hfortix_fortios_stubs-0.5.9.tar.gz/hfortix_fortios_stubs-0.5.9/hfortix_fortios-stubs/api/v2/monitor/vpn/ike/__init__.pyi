"""Type stubs for IKE category."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hfortix_core.http.interface import IHTTPClient
    from .clear import Clear


class Ike:
    """Type stub for Ike."""

    clear: Clear

    def __init__(self, client: IHTTPClient) -> None: ...
