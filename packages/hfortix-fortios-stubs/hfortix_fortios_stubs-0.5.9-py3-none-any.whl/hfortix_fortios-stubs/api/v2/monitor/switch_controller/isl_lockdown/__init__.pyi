"""Type stubs for ISL_LOCKDOWN category."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hfortix_core.http.interface import IHTTPClient
    from .status import Status
    from .update import Update


class IslLockdown:
    """Type stub for IslLockdown."""

    status: Status
    update: Update

    def __init__(self, client: IHTTPClient) -> None: ...
