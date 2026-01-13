"""Type stubs for ACL category."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hfortix_core.http.interface import IHTTPClient
    from .group import Group
    from .ingress import Ingress


class Acl:
    """Type stub for Acl."""

    group: Group
    ingress: Ingress

    def __init__(self, client: IHTTPClient) -> None: ...
