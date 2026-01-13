"""Type stubs for AP_PROFILE category."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hfortix_core.http.interface import IHTTPClient
    from .create_default import CreateDefault


class ApProfile:
    """Type stub for ApProfile."""

    create_default: CreateDefault

    def __init__(self, client: IHTTPClient) -> None: ...
