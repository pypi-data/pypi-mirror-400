"""Type stubs for WAF category."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hfortix_core.http.interface import IHTTPClient
    from .main_class import MainClass
    from .profile import Profile
    from .signature import Signature


class Waf:
    """Type stub for Waf."""

    main_class: MainClass
    profile: Profile
    signature: Signature

    def __init__(self, client: IHTTPClient) -> None: ...
