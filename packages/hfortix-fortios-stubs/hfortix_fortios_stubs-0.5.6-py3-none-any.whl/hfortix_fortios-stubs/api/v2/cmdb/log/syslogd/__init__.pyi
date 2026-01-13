"""Type stubs for SYSLOGD category."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hfortix_core.http.interface import IHTTPClient
    from .filter import Filter
    from .override_filter import OverrideFilter
    from .override_setting import OverrideSetting
    from .setting import Setting


class Syslogd:
    """Type stub for Syslogd."""

    filter: Filter
    override_filter: OverrideFilter
    override_setting: OverrideSetting
    setting: Setting

    def __init__(self, client: IHTTPClient) -> None: ...
