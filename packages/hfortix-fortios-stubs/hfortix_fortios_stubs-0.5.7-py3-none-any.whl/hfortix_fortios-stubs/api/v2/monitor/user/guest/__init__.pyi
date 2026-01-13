"""Type stubs for GUEST category."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hfortix_core.http.interface import IHTTPClient
    from .email import Email
    from .sms import Sms


class Guest:
    """Type stub for Guest."""

    email: Email
    sms: Sms

    def __init__(self, client: IHTTPClient) -> None: ...
