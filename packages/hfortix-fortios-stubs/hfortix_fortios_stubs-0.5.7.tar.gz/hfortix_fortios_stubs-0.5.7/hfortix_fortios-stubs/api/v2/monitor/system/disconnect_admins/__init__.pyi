"""Type stubs for DISCONNECT_ADMINS category."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hfortix_core.http.interface import IHTTPClient
    from .select import Select


class DisconnectAdmins:
    """Type stub for DisconnectAdmins."""

    select: Select

    def __init__(self, client: IHTTPClient) -> None: ...
