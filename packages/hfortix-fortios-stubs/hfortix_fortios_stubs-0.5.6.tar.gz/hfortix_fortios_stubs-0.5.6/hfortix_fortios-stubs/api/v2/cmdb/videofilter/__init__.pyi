"""Type stubs for VIDEOFILTER category."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hfortix_core.http.interface import IHTTPClient
    from .keyword import Keyword
    from .profile import Profile
    from .youtube_key import YoutubeKey


class Videofilter:
    """Type stub for Videofilter."""

    keyword: Keyword
    profile: Profile
    youtube_key: YoutubeKey

    def __init__(self, client: IHTTPClient) -> None: ...
