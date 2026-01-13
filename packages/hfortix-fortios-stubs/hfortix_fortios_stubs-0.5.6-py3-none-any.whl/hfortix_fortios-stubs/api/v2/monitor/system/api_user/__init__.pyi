"""Type stubs for API_USER category."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hfortix_core.http.interface import IHTTPClient
    from .generate_key import GenerateKey


class ApiUser:
    """Type stub for ApiUser."""

    generate_key: GenerateKey

    def __init__(self, client: IHTTPClient) -> None: ...
