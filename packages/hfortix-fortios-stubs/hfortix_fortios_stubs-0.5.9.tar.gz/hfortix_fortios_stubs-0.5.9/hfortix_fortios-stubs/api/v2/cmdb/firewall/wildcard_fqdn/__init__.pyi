"""Type stubs for WILDCARD_FQDN category."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hfortix_core.http.interface import IHTTPClient
    from .custom import Custom
    from .group import Group


class WildcardFqdn:
    """Type stub for WildcardFqdn."""

    custom: Custom
    group: Group

    def __init__(self, client: IHTTPClient) -> None: ...
