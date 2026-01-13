"""Type stubs for USB_DEVICE category."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hfortix_core.http.interface import IHTTPClient
    from .eject import Eject


class UsbDevice:
    """Type stub for UsbDevice."""

    eject: Eject

    def __init__(self, client: IHTTPClient) -> None: ...
