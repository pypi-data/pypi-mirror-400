"""Type stubs for LICENSE category."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hfortix_core.http.interface import IHTTPClient
    from .fortianalyzer_status import FortianalyzerStatus
    from .forticare_org_list import ForticareOrgList
    from .forticare_resellers import ForticareResellers
    from .status import Status
    from .database import Database


class License:
    """Type stub for License."""

    database: Database
    fortianalyzer_status: FortianalyzerStatus
    forticare_org_list: ForticareOrgList
    forticare_resellers: ForticareResellers
    status: Status

    def __init__(self, client: IHTTPClient) -> None: ...
