"""Type stubs for SCHEDULE category."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hfortix_core.http.interface import IHTTPClient
    from .group import Group
    from .onetime import Onetime
    from .recurring import Recurring


class Schedule:
    """Type stub for Schedule."""

    group: Group
    onetime: Onetime
    recurring: Recurring

    def __init__(self, client: IHTTPClient) -> None: ...
