"""Type stubs for APPLICATION category."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hfortix_core.http.interface import IHTTPClient
    from .custom import Custom
    from .group import Group
    from .list import List
    from .name import Name
    from .rule_settings import RuleSettings


class Application:
    """Type stub for Application."""

    custom: Custom
    group: Group
    list: List
    name: Name
    rule_settings: RuleSettings

    def __init__(self, client: IHTTPClient) -> None: ...
