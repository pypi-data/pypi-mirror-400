"""Type stubs for EXTENSION_CONTROLLER category."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hfortix_core.http.interface import IHTTPClient
    from .fortigate import Fortigate
    from .lan_extension_vdom_status import LanExtensionVdomStatus


class ExtensionController:
    """Type stub for ExtensionController."""

    fortigate: Fortigate
    lan_extension_vdom_status: LanExtensionVdomStatus

    def __init__(self, client: IHTTPClient) -> None: ...
