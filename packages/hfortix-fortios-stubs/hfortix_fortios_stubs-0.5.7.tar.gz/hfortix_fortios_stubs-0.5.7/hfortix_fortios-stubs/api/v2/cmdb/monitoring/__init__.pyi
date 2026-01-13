"""Type stubs for MONITORING category."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hfortix_core.http.interface import IHTTPClient
    from .npu_hpe import NpuHpe


class Monitoring:
    """Type stub for Monitoring."""

    npu_hpe: NpuHpe

    def __init__(self, client: IHTTPClient) -> None: ...
