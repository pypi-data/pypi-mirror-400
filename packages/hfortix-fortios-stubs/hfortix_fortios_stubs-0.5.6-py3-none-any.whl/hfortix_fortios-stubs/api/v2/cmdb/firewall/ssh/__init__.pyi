"""Type stubs for SSH category."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hfortix_core.http.interface import IHTTPClient
    from .host_key import HostKey
    from .local_ca import LocalCa
    from .local_key import LocalKey
    from .setting import Setting


class Ssh:
    """Type stub for Ssh."""

    host_key: HostKey
    local_ca: LocalCa
    local_key: LocalKey
    setting: Setting

    def __init__(self, client: IHTTPClient) -> None: ...
