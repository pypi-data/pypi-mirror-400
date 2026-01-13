"""Type stubs for LOCAL_REPORT category."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hfortix_core.http.interface import IHTTPClient
    from .delete import Delete
    from .download import Download


class LocalReport:
    """Type stub for LocalReport."""

    delete: Delete
    download: Download

    def __init__(self, client: IHTTPClient) -> None: ...
