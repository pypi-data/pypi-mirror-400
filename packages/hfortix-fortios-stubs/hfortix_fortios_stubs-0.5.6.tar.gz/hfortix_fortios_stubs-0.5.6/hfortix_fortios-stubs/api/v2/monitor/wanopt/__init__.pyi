"""Type stubs for WANOPT category."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hfortix_core.http.interface import IHTTPClient
    from .history import History
    from .peer_stats import PeerStats
    from .webcache import Webcache


class Wanopt:
    """Type stub for Wanopt."""

    history: History
    peer_stats: PeerStats
    webcache: Webcache

    def __init__(self, client: IHTTPClient) -> None: ...
