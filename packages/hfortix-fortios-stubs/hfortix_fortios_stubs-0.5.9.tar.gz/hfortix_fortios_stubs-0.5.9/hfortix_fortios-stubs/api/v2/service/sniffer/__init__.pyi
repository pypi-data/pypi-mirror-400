"""Type stubs for SNIFFER category."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hfortix_core.http.interface import IHTTPClient
    from .delete import Delete
    from .download import Download
    from .list import List
    from .meta import Meta
    from .start import Start
    from .stop import Stop


class Sniffer:
    """Type stub for Sniffer."""

    delete: Delete
    download: Download
    list: List
    meta: Meta
    start: Start
    stop: Stop

    def __init__(self, client: IHTTPClient) -> None: ...
