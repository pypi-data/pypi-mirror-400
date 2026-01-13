"""Type stubs for CASB category."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hfortix_core.http.interface import IHTTPClient
    from .saas_application import SaasApplication


class Casb:
    """Type stub for Casb."""

    saas_application: SaasApplication

    def __init__(self, client: IHTTPClient) -> None: ...
