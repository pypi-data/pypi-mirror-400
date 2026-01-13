"""Type stubs for RATING_LOOKUP category."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hfortix_core.http.interface import IHTTPClient
    from .select import Select


class RatingLookup:
    """Type stub for RatingLookup."""

    select: Select

    def __init__(self, client: IHTTPClient) -> None: ...
