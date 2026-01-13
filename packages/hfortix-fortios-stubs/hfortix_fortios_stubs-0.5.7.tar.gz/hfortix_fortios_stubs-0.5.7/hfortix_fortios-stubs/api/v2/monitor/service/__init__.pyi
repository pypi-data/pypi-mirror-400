"""Type stubs for SERVICE category."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hfortix_core.http.interface import IHTTPClient
    from .ldap import Ldap


class Service:
    """Type stub for Service."""

    ldap: Ldap

    def __init__(self, client: IHTTPClient) -> None: ...
