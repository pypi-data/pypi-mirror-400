"""Type stubs for SERVICE category."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hfortix_core.http.interface import IHTTPClient
    from .category import Category
    from .custom import Custom
    from .group import Group


class Service:
    """Type stub for Service."""

    category: Category
    custom: Custom
    group: Group

    def __init__(self, client: IHTTPClient) -> None: ...
