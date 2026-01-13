"""Type stubs for ADMIN category."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hfortix_core.http.interface import IHTTPClient
    from .change_vdom_mode import ChangeVdomMode


class Admin:
    """Type stub for Admin."""

    change_vdom_mode: ChangeVdomMode

    def __init__(self, client: IHTTPClient) -> None: ...
