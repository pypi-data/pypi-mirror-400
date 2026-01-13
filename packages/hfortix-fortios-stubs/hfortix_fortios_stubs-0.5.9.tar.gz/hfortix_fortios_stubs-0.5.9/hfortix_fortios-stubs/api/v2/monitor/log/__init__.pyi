"""Type stubs for LOG category."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hfortix_core.http.interface import IHTTPClient
    from .current_disk_usage import CurrentDiskUsage
    from .feature_set import FeatureSet
    from .fortianalyzer import Fortianalyzer
    from .fortianalyzer_queue import FortianalyzerQueue
    from .forticloud_report_list import ForticloudReportList
    from .historic_daily_remote_logs import HistoricDailyRemoteLogs
    from .hourly_disk_usage import HourlyDiskUsage
    from .local_report_list import LocalReportList
    from .av_archive import AvArchive
    from .device import Device
    from .forticloud import Forticloud
    from .forticloud_report import ForticloudReport
    from .local_report import LocalReport
    from .policy_archive import PolicyArchive
    from .stats import Stats


class Log:
    """Type stub for Log."""

    av_archive: AvArchive
    device: Device
    forticloud: Forticloud
    forticloud_report: ForticloudReport
    local_report: LocalReport
    policy_archive: PolicyArchive
    stats: Stats
    current_disk_usage: CurrentDiskUsage
    feature_set: FeatureSet
    fortianalyzer: Fortianalyzer
    fortianalyzer_queue: FortianalyzerQueue
    forticloud_report_list: ForticloudReportList
    historic_daily_remote_logs: HistoricDailyRemoteLogs
    hourly_disk_usage: HourlyDiskUsage
    local_report_list: LocalReportList

    def __init__(self, client: IHTTPClient) -> None: ...
