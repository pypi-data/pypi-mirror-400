"""Type stubs for ICAP category."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hfortix_core.http.interface import IHTTPClient
    from .profile import Profile
    from .server import Server
    from .server_group import ServerGroup


class Icap:
    """Type stub for Icap."""

    profile: Profile
    server: Server
    server_group: ServerGroup

    def __init__(self, client: IHTTPClient) -> None: ...
