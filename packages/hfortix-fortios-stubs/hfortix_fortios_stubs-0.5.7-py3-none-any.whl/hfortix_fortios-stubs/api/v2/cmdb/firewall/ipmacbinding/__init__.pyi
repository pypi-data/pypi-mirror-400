"""Type stubs for IPMACBINDING category."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hfortix_core.http.interface import IHTTPClient
    from .setting import Setting
    from .table import Table


class Ipmacbinding:
    """Type stub for Ipmacbinding."""

    setting: Setting
    table: Table

    def __init__(self, client: IHTTPClient) -> None: ...
