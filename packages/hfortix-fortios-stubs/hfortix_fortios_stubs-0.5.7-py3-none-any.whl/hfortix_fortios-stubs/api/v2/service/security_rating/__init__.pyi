"""Type stubs for SECURITY_RATING category."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hfortix_core.http.interface import IHTTPClient
    from .recommendations import Recommendations
    from .report import Report


class SecurityRating:
    """Type stub for SecurityRating."""

    recommendations: Recommendations
    report: Report

    def __init__(self, client: IHTTPClient) -> None: ...
