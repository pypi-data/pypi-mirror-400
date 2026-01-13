"""Type stubs for LDAP category."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hfortix_core.http.interface import IHTTPClient
    from .query import Query


class Ldap:
    """Type stub for Ldap."""

    query: Query

    def __init__(self, client: IHTTPClient) -> None: ...
