"""Type stubs for WEBFILTER category."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hfortix_core.http.interface import IHTTPClient
    from .fortiguard_categories import FortiguardCategories
    from .trusted_urls import TrustedUrls
    from .category_quota import CategoryQuota
    from .malicious_urls import MaliciousUrls
    from .override import Override


class Webfilter:
    """Type stub for Webfilter."""

    category_quota: CategoryQuota
    malicious_urls: MaliciousUrls
    override: Override
    fortiguard_categories: FortiguardCategories
    trusted_urls: TrustedUrls

    def __init__(self, client: IHTTPClient) -> None: ...
