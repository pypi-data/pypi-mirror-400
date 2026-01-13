"""Type stubs for REGISTRATION category."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hfortix_core.http.interface import IHTTPClient
    from .forticare import Forticare
    from .forticloud import Forticloud
    from .vdom import Vdom


class Registration:
    """Type stub for Registration."""

    forticare: Forticare
    forticloud: Forticloud
    vdom: Vdom

    def __init__(self, client: IHTTPClient) -> None: ...
