"""Type stubs for TACACS_PLUSACCOUNTING category."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hfortix_core.http.interface import IHTTPClient
    from .filter import Filter
    from .setting import Setting


class TacacsPlusaccounting:
    """Type stub for TacacsPlusaccounting."""

    filter: Filter
    setting: Setting

    def __init__(self, client: IHTTPClient) -> None: ...
