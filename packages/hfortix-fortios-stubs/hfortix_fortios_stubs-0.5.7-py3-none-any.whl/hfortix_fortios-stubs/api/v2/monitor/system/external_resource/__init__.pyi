"""Type stubs for EXTERNAL_RESOURCE category."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hfortix_core.http.interface import IHTTPClient
    from .dynamic import Dynamic
    from .entry_list import EntryList
    from .generic_address import GenericAddress
    from .refresh import Refresh
    from .validate_jsonpath import ValidateJsonpath


class ExternalResource:
    """Type stub for ExternalResource."""

    dynamic: Dynamic
    entry_list: EntryList
    generic_address: GenericAddress
    refresh: Refresh
    validate_jsonpath: ValidateJsonpath

    def __init__(self, client: IHTTPClient) -> None: ...
