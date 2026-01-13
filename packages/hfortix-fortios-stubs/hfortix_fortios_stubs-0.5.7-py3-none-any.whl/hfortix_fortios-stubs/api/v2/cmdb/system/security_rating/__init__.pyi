"""Type stubs for SECURITY_RATING category."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hfortix_core.http.interface import IHTTPClient
    from .controls import Controls
    from .settings import Settings


class SecurityRating:
    """Type stub for SecurityRating."""

    controls: Controls
    settings: Settings

    def __init__(self, client: IHTTPClient) -> None: ...
