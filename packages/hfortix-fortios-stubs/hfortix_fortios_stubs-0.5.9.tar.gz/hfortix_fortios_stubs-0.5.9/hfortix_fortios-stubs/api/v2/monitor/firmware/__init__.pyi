"""Type stubs for FIRMWARE category."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hfortix_core.http.interface import IHTTPClient
    from .extension_device import ExtensionDevice


class Firmware:
    """Type stub for Firmware."""

    extension_device: ExtensionDevice

    def __init__(self, client: IHTTPClient) -> None: ...
