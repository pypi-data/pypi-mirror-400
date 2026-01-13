"""Type stubs for FORTITOKEN_CLOUD category."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hfortix_core.http.interface import IHTTPClient
    from .status import Status
    from .trial import Trial


class FortitokenCloud:
    """Type stub for FortitokenCloud."""

    status: Status
    trial: Trial

    def __init__(self, client: IHTTPClient) -> None: ...
