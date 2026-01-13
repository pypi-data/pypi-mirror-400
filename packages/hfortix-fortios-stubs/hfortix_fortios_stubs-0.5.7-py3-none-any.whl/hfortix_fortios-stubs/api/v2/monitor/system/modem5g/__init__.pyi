"""Type stubs for MODEM5G category."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hfortix_core.http.interface import IHTTPClient
    from .status import Status


class Modem5g:
    """Type stub for Modem5g."""

    status: Status

    def __init__(self, client: IHTTPClient) -> None: ...
