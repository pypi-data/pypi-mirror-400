"""Type stubs for VIDEOFILTER category."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hfortix_core.http.interface import IHTTPClient
    from .fortiguard_categories import FortiguardCategories


class Videofilter:
    """Type stub for Videofilter."""

    fortiguard_categories: FortiguardCategories

    def __init__(self, client: IHTTPClient) -> None: ...
