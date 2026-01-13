"""Type stubs for OS category."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hfortix_core.http.interface import IHTTPClient
    from .reboot import Reboot
    from .shutdown import Shutdown


class Os:
    """Type stub for Os."""

    reboot: Reboot
    shutdown: Shutdown

    def __init__(self, client: IHTTPClient) -> None: ...
