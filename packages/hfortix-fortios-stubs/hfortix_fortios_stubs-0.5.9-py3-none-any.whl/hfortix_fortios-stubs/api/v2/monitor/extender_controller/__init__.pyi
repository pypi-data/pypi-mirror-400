"""Type stubs for EXTENDER_CONTROLLER category."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hfortix_core.http.interface import IHTTPClient
    from .extender import Extender


class ExtenderController:
    """Type stub for ExtenderController."""

    extender: Extender

    def __init__(self, client: IHTTPClient) -> None: ...
