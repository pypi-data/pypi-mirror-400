"""Type stubs for DEVICE category."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hfortix_core.http.interface import IHTTPClient
    from .iot_query import IotQuery
    from .purdue_level import PurdueLevel
    from .query import Query
    from .stats import Stats


class Device:
    """Type stub for Device."""

    iot_query: IotQuery
    purdue_level: PurdueLevel
    query: Query
    stats: Stats

    def __init__(self, client: IHTTPClient) -> None: ...
