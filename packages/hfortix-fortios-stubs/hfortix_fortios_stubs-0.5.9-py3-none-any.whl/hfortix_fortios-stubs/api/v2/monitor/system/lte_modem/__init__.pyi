"""Type stubs for LTE_MODEM category."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hfortix_core.http.interface import IHTTPClient
    from .status import Status
    from .upgrade import Upgrade
    from .upload import Upload


class LteModem:
    """Type stub for LteModem."""

    status: Status
    upgrade: Upgrade
    upload: Upload

    def __init__(self, client: IHTTPClient) -> None: ...
