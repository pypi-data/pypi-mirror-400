"""Type stubs for INITIAL_CONFIG category."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hfortix_core.http.interface import IHTTPClient
    from .template import Template
    from .vlans import Vlans


class InitialConfig:
    """Type stub for InitialConfig."""

    template: Template
    vlans: Vlans

    def __init__(self, client: IHTTPClient) -> None: ...
