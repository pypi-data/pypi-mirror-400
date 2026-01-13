"""Type stubs for TACACS_PLUSACCOUNTING2 category."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hfortix_core.http.interface import IHTTPClient
    from .filter import Filter
    from .setting import Setting


class TacacsPlusaccounting2:
    """Type stub for TacacsPlusaccounting2."""

    filter: Filter
    setting: Setting

    def __init__(self, client: IHTTPClient) -> None: ...
