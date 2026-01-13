"""Type stubs for FORTIGUARD category."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hfortix_core.http.interface import IHTTPClient
    from .answers import Answers
    from .redirect_portal import RedirectPortal
    from .service_communication_stats import ServiceCommunicationStats


class Fortiguard:
    """Type stub for Fortiguard."""

    answers: Answers
    redirect_portal: RedirectPortal
    service_communication_stats: ServiceCommunicationStats

    def __init__(self, client: IHTTPClient) -> None: ...
