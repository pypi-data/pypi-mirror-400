"""Type stubs for MEMORY category."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hfortix_core.http.interface import IHTTPClient
    from .filter import Filter
    from .global_setting import GlobalSetting
    from .setting import Setting


class Memory:
    """Type stub for Memory."""

    filter: Filter
    global_setting: GlobalSetting
    setting: Setting

    def __init__(self, client: IHTTPClient) -> None: ...
