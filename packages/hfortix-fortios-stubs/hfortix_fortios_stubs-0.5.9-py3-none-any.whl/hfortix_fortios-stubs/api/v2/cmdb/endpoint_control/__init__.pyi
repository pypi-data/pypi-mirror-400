"""Type stubs for ENDPOINT_CONTROL category."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hfortix_core.http.interface import IHTTPClient
    from .fctems import Fctems
    from .fctems_override import FctemsOverride
    from .settings import Settings


class EndpointControl:
    """Type stub for EndpointControl."""

    fctems: Fctems
    fctems_override: FctemsOverride
    settings: Settings

    def __init__(self, client: IHTTPClient) -> None: ...
