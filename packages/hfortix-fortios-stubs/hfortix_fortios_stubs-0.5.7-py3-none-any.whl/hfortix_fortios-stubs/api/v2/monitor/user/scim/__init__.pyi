"""Type stubs for SCIM category."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hfortix_core.http.interface import IHTTPClient
    from .groups import Groups
    from .users import Users


class Scim:
    """Type stub for Scim."""

    groups: Groups
    users: Users

    def __init__(self, client: IHTTPClient) -> None: ...
