"""Type stubs for CASB category."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hfortix_core.http.interface import IHTTPClient
    from .attribute_match import AttributeMatch
    from .profile import Profile
    from .saas_application import SaasApplication
    from .user_activity import UserActivity


class Casb:
    """Type stub for Casb."""

    attribute_match: AttributeMatch
    profile: Profile
    saas_application: SaasApplication
    user_activity: UserActivity

    def __init__(self, client: IHTTPClient) -> None: ...
