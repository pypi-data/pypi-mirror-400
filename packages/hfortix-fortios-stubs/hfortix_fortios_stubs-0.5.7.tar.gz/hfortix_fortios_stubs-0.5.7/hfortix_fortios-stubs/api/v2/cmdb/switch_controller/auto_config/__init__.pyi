"""Type stubs for AUTO_CONFIG category."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hfortix_core.http.interface import IHTTPClient
    from .custom import Custom
    from .default import Default
    from .policy import Policy


class AutoConfig:
    """Type stub for AutoConfig."""

    custom: Custom
    default: Default
    policy: Policy

    def __init__(self, client: IHTTPClient) -> None: ...
