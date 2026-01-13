"""Type stubs for UPGRADE_REPORT category."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hfortix_core.http.interface import IHTTPClient
    from .current import Current
    from .exists import Exists
    from .saved import Saved


class UpgradeReport:
    """Type stub for UpgradeReport."""

    current: Current
    exists: Exists
    saved: Saved

    def __init__(self, client: IHTTPClient) -> None: ...
