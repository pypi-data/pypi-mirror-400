"""Type stubs for RULE category."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hfortix_core.http.interface import IHTTPClient
    from .fmwp import Fmwp
    from .iotd import Iotd
    from .otdt import Otdt
    from .otvp import Otvp


class Rule:
    """Type stub for Rule."""

    fmwp: Fmwp
    iotd: Iotd
    otdt: Otdt
    otvp: Otvp

    def __init__(self, client: IHTTPClient) -> None: ...
