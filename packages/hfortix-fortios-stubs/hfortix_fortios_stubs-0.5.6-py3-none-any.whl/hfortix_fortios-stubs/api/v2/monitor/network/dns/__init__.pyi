"""Type stubs for DNS category."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hfortix_core.http.interface import IHTTPClient
    from .latency import Latency


class Dns:
    """Type stub for Dns."""

    latency: Latency

    def __init__(self, client: IHTTPClient) -> None: ...
