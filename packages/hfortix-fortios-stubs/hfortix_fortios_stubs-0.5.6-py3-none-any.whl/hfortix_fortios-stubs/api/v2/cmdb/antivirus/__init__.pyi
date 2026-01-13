"""Type stubs for ANTIVIRUS category."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hfortix_core.http.interface import IHTTPClient
    from .exempt_list import ExemptList
    from .profile import Profile
    from .quarantine import Quarantine
    from .settings import Settings


class Antivirus:
    """Type stub for Antivirus."""

    exempt_list: ExemptList
    profile: Profile
    quarantine: Quarantine
    settings: Settings

    def __init__(self, client: IHTTPClient) -> None: ...
