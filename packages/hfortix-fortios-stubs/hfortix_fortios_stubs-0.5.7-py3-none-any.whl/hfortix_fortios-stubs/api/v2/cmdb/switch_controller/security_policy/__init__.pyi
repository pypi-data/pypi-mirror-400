"""Type stubs for SECURITY_POLICY category."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hfortix_core.http.interface import IHTTPClient
    from .local_access import LocalAccess
    from .x802_1x import X8021x


class SecurityPolicy:
    """Type stub for SecurityPolicy."""

    local_access: LocalAccess
    x802_1x: X8021x

    def __init__(self, client: IHTTPClient) -> None: ...
