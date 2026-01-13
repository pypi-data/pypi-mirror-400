"""Type stubs for TACACS_PLUS category."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hfortix_core.http.interface import IHTTPClient
    from .test import Test


class TacacsPlus:
    """Type stub for TacacsPlus."""

    test: Test

    def __init__(self, client: IHTTPClient) -> None: ...
