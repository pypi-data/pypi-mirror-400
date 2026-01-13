"""Type stubs for UTM category."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hfortix_core.http.interface import IHTTPClient
    from .app_lookup import AppLookup
    from .application_categories import ApplicationCategories
    from .antivirus import Antivirus
    from .blacklisted_certificates import BlacklistedCertificates
    from .rating_lookup import RatingLookup


class Utm:
    """Type stub for Utm."""

    antivirus: Antivirus
    blacklisted_certificates: BlacklistedCertificates
    rating_lookup: RatingLookup
    app_lookup: AppLookup
    application_categories: ApplicationCategories

    def __init__(self, client: IHTTPClient) -> None: ...
