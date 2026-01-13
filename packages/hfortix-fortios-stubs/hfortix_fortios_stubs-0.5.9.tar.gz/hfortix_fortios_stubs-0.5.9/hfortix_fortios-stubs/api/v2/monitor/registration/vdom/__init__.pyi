"""Type stubs for VDOM category."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hfortix_core.http.interface import IHTTPClient
    from .add_license import AddLicense


class Vdom:
    """Type stub for Vdom."""

    add_license: AddLicense

    def __init__(self, client: IHTTPClient) -> None: ...
