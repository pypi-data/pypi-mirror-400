"""Type stubs for SAAS_APPLICATION category."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hfortix_core.http.interface import IHTTPClient
    from .details import Details


class SaasApplication:
    """Type stub for SaasApplication."""

    details: Details

    def __init__(self, client: IHTTPClient) -> None: ...
