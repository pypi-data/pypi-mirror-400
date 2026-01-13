"""Type stubs for AUTHENTICATION category."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hfortix_core.http.interface import IHTTPClient
    from .rule import Rule
    from .scheme import Scheme
    from .setting import Setting


class Authentication:
    """Type stub for Authentication."""

    rule: Rule
    scheme: Scheme
    setting: Setting

    def __init__(self, client: IHTTPClient) -> None: ...
