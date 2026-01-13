"""Type stubs for WEBFILTER category."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hfortix_core.http.interface import IHTTPClient
    from .content import Content
    from .content_header import ContentHeader
    from .fortiguard import Fortiguard
    from .ftgd_local_cat import FtgdLocalCat
    from .ftgd_local_rating import FtgdLocalRating
    from .ftgd_local_risk import FtgdLocalRisk
    from .ftgd_risk_level import FtgdRiskLevel
    from .ips_urlfilter_cache_setting import IpsUrlfilterCacheSetting
    from .ips_urlfilter_setting import IpsUrlfilterSetting
    from .ips_urlfilter_setting6 import IpsUrlfilterSetting6
    from .override import Override
    from .profile import Profile
    from .search_engine import SearchEngine
    from .urlfilter import Urlfilter


class Webfilter:
    """Type stub for Webfilter."""

    content: Content
    content_header: ContentHeader
    fortiguard: Fortiguard
    ftgd_local_cat: FtgdLocalCat
    ftgd_local_rating: FtgdLocalRating
    ftgd_local_risk: FtgdLocalRisk
    ftgd_risk_level: FtgdRiskLevel
    ips_urlfilter_cache_setting: IpsUrlfilterCacheSetting
    ips_urlfilter_setting: IpsUrlfilterSetting
    ips_urlfilter_setting6: IpsUrlfilterSetting6
    override: Override
    profile: Profile
    search_engine: SearchEngine
    urlfilter: Urlfilter

    def __init__(self, client: IHTTPClient) -> None: ...
