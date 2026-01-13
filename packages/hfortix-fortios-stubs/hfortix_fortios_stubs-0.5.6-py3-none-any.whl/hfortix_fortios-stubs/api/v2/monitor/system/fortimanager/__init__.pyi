"""Type stubs for FORTIMANAGER category."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hfortix_core.http.interface import IHTTPClient
    from .backup_action import BackupAction
    from .backup_details import BackupDetails
    from .backup_summary import BackupSummary


class Fortimanager:
    """Type stub for Fortimanager."""

    backup_action: BackupAction
    backup_details: BackupDetails
    backup_summary: BackupSummary

    def __init__(self, client: IHTTPClient) -> None: ...
