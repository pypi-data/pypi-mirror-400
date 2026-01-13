"""Type stubs for RADIUS category."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hfortix_core.http.interface import IHTTPClient
    from .get_test_connect import GetTestConnect
    from .test_connect import TestConnect


class Radius:
    """Type stub for Radius."""

    get_test_connect: GetTestConnect
    test_connect: TestConnect

    def __init__(self, client: IHTTPClient) -> None: ...
