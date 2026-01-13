"""Type stubs for INFO category."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hfortix_core.http.interface import IHTTPClient
    from .query import Query
    from .thumbnail import Thumbnail
    from .thumbnail_file import ThumbnailFile


class Info:
    """Type stub for Info."""

    query: Query
    thumbnail: Thumbnail
    thumbnail_file: ThumbnailFile

    def __init__(self, client: IHTTPClient) -> None: ...
