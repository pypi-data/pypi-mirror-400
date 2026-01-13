"""Type stubs for AUTOMATION_STITCH category."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hfortix_core.http.interface import IHTTPClient
    from .stats import Stats
    from .test import Test
    from .webhook import Webhook


class AutomationStitch:
    """Type stub for AutomationStitch."""

    stats: Stats
    test: Test
    webhook: Webhook

    def __init__(self, client: IHTTPClient) -> None: ...
