"""Type stubs for IPS category."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hfortix_core.http.interface import IHTTPClient
    from .custom import Custom
    from .decoder import Decoder
    from .global_ import Global
    from .rule import Rule
    from .rule_settings import RuleSettings
    from .sensor import Sensor
    from .settings import Settings
    from .view_map import ViewMap


class Ips:
    """Type stub for Ips."""

    custom: Custom
    decoder: Decoder
    global_: Global
    rule: Rule
    rule_settings: RuleSettings
    sensor: Sensor
    settings: Settings
    view_map: ViewMap

    def __init__(self, client: IHTTPClient) -> None: ...
