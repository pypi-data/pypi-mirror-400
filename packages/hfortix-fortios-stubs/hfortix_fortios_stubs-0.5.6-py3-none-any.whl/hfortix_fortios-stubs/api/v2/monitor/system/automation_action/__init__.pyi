"""Type stubs for AUTOMATION_ACTION category."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hfortix_core.http.interface import IHTTPClient
    from .stats import Stats


class AutomationAction:
    """Type stub for AutomationAction."""

    stats: Stats

    def __init__(self, client: IHTTPClient) -> None: ...
