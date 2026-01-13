"""Type stubs for DEVICE category."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hfortix_core.http.interface import IHTTPClient
    from .state import State


class Device:
    """Type stub for Device."""

    state: State

    def __init__(self, client: IHTTPClient) -> None: ...
