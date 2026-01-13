"""Type stubs for CLEARPASS_ADDRESS category."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hfortix_core.http.interface import IHTTPClient
    from .add import Add
    from .delete import Delete


class ClearpassAddress:
    """Type stub for ClearpassAddress."""

    add: Add
    delete: Delete

    def __init__(self, client: IHTTPClient) -> None: ...
