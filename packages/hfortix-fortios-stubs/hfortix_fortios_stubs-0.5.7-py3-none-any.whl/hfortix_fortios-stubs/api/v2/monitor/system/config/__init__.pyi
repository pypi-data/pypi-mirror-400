"""Type stubs for CONFIG category."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hfortix_core.http.interface import IHTTPClient
    from .backup import Backup
    from .restore import Restore
    from .restore_status import RestoreStatus
    from .usb_filelist import UsbFilelist


class Config:
    """Type stub for Config."""

    backup: Backup
    restore: Restore
    restore_status: RestoreStatus
    usb_filelist: UsbFilelist

    def __init__(self, client: IHTTPClient) -> None: ...
