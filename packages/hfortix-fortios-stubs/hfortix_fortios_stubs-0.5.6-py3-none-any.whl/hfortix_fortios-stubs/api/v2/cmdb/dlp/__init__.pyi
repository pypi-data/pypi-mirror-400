"""Type stubs for DLP category."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hfortix_core.http.interface import IHTTPClient
    from .data_type import DataType
    from .dictionary import Dictionary
    from .exact_data_match import ExactDataMatch
    from .filepattern import Filepattern
    from .label import Label
    from .profile import Profile
    from .sensor import Sensor
    from .settings import Settings


class Dlp:
    """Type stub for Dlp."""

    data_type: DataType
    dictionary: Dictionary
    exact_data_match: ExactDataMatch
    filepattern: Filepattern
    label: Label
    profile: Profile
    sensor: Sensor
    settings: Settings

    def __init__(self, client: IHTTPClient) -> None: ...
