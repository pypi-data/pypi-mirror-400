"""Type stubs for MODEM3G category."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hfortix_core.http.interface import IHTTPClient
    from .custom import Custom


class Modem3g:
    """Type stub for Modem3g."""

    custom: Custom

    def __init__(self, client: IHTTPClient) -> None: ...
