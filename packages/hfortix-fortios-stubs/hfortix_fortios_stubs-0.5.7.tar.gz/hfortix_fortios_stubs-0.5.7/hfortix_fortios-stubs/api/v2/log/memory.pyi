"""Type stubs for LOG endpoint."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from hfortix_core.http.interface import IHTTPClient


class Memory:
    """Type stub for Memory."""

    anomaly: MemoryAnomaly
    app_ctrl: MemoryAppCtrl
    cifs: MemoryCifs
    dlp: MemoryDlp
    dns: MemoryDns
    emailfilter: MemoryEmailfilter
    event: MemoryEvent
    file_filter: MemoryFileFilter
    gtp: MemoryGtp
    ips: MemoryIps
    ssh: MemorySsh
    ssl: MemorySsl
    traffic: MemoryTraffic
    virus: MemoryVirus
    voip: MemoryVoip
    waf: MemoryWaf
    webfilter: MemoryWebfilter

    def __init__(self, client: IHTTPClient) -> None: ...

class MemoryAnomaly:
    """Type stub for MemoryAnomaly."""

    def __init__(self, client: IHTTPClient) -> None: ...
    def get(self, **kwargs: Any) -> dict[str, Any]: ...

class MemoryAppCtrl:
    """Type stub for MemoryAppCtrl."""

    archive: MemoryAppCtrlArchive
    archive_download: MemoryAppCtrlArchiveDownload

    def __init__(self, client: IHTTPClient) -> None: ...
    def get(self, **kwargs: Any) -> dict[str, Any]: ...

class MemoryAppCtrlArchive:
    """Type stub for MemoryAppCtrlArchive."""

    def __init__(self, client: IHTTPClient) -> None: ...
    def get(self, **kwargs: Any) -> dict[str, Any]: ...

class MemoryAppCtrlArchiveDownload:
    """Type stub for MemoryAppCtrlArchiveDownload."""

    def __init__(self, client: IHTTPClient) -> None: ...
    def get(self, **kwargs: Any) -> dict[str, Any]: ...

class MemoryCifs:
    """Type stub for MemoryCifs."""

    def __init__(self, client: IHTTPClient) -> None: ...
    def get(self, **kwargs: Any) -> dict[str, Any]: ...

class MemoryDlp:
    """Type stub for MemoryDlp."""

    def __init__(self, client: IHTTPClient) -> None: ...
    def get(self, **kwargs: Any) -> dict[str, Any]: ...

class MemoryDns:
    """Type stub for MemoryDns."""

    def __init__(self, client: IHTTPClient) -> None: ...
    def get(self, **kwargs: Any) -> dict[str, Any]: ...

class MemoryEmailfilter:
    """Type stub for MemoryEmailfilter."""

    def __init__(self, client: IHTTPClient) -> None: ...
    def get(self, **kwargs: Any) -> dict[str, Any]: ...

class MemoryEvent:
    """Type stub for MemoryEvent."""

    compliance_check: MemoryEventComplianceCheck
    connector: MemoryEventConnector
    endpoint: MemoryEventEndpoint
    fortiextender: MemoryEventFortiextender
    ha: MemoryEventHa
    router: MemoryEventRouter
    security_rating: MemoryEventSecurityRating
    system: MemoryEventSystem
    user: MemoryEventUser
    vpn: MemoryEventVpn
    wad: MemoryEventWad
    wireless: MemoryEventWireless

    def __init__(self, client: IHTTPClient) -> None: ...

class MemoryEventComplianceCheck:
    """Type stub for MemoryEventComplianceCheck."""

    def __init__(self, client: IHTTPClient) -> None: ...
    def get(self, **kwargs: Any) -> dict[str, Any]: ...

class MemoryEventConnector:
    """Type stub for MemoryEventConnector."""

    def __init__(self, client: IHTTPClient) -> None: ...
    def get(self, **kwargs: Any) -> dict[str, Any]: ...

class MemoryEventEndpoint:
    """Type stub for MemoryEventEndpoint."""

    def __init__(self, client: IHTTPClient) -> None: ...
    def get(self, **kwargs: Any) -> dict[str, Any]: ...

class MemoryEventFortiextender:
    """Type stub for MemoryEventFortiextender."""

    def __init__(self, client: IHTTPClient) -> None: ...
    def get(self, **kwargs: Any) -> dict[str, Any]: ...

class MemoryEventHa:
    """Type stub for MemoryEventHa."""

    def __init__(self, client: IHTTPClient) -> None: ...
    def get(self, **kwargs: Any) -> dict[str, Any]: ...

class MemoryEventRouter:
    """Type stub for MemoryEventRouter."""

    def __init__(self, client: IHTTPClient) -> None: ...
    def get(self, **kwargs: Any) -> dict[str, Any]: ...

class MemoryEventSecurityRating:
    """Type stub for MemoryEventSecurityRating."""

    def __init__(self, client: IHTTPClient) -> None: ...
    def get(self, **kwargs: Any) -> dict[str, Any]: ...

class MemoryEventSystem:
    """Type stub for MemoryEventSystem."""

    def __init__(self, client: IHTTPClient) -> None: ...
    def get(self, **kwargs: Any) -> dict[str, Any]: ...

class MemoryEventUser:
    """Type stub for MemoryEventUser."""

    def __init__(self, client: IHTTPClient) -> None: ...
    def get(self, **kwargs: Any) -> dict[str, Any]: ...

class MemoryEventVpn:
    """Type stub for MemoryEventVpn."""

    def __init__(self, client: IHTTPClient) -> None: ...
    def get(self, **kwargs: Any) -> dict[str, Any]: ...

class MemoryEventWad:
    """Type stub for MemoryEventWad."""

    def __init__(self, client: IHTTPClient) -> None: ...
    def get(self, **kwargs: Any) -> dict[str, Any]: ...

class MemoryEventWireless:
    """Type stub for MemoryEventWireless."""

    def __init__(self, client: IHTTPClient) -> None: ...
    def get(self, **kwargs: Any) -> dict[str, Any]: ...

class MemoryFileFilter:
    """Type stub for MemoryFileFilter."""

    def __init__(self, client: IHTTPClient) -> None: ...
    def get(self, **kwargs: Any) -> dict[str, Any]: ...

class MemoryGtp:
    """Type stub for MemoryGtp."""

    def __init__(self, client: IHTTPClient) -> None: ...
    def get(self, **kwargs: Any) -> dict[str, Any]: ...

class MemoryIps:
    """Type stub for MemoryIps."""

    archive: MemoryIpsArchive
    archive_download: MemoryIpsArchiveDownload

    def __init__(self, client: IHTTPClient) -> None: ...
    def get(self, **kwargs: Any) -> dict[str, Any]: ...

class MemoryIpsArchive:
    """Type stub for MemoryIpsArchive."""

    def __init__(self, client: IHTTPClient) -> None: ...
    def get(self, **kwargs: Any) -> dict[str, Any]: ...

class MemoryIpsArchiveDownload:
    """Type stub for MemoryIpsArchiveDownload."""

    def __init__(self, client: IHTTPClient) -> None: ...
    def get(self, **kwargs: Any) -> dict[str, Any]: ...

class MemorySsh:
    """Type stub for MemorySsh."""

    def __init__(self, client: IHTTPClient) -> None: ...
    def get(self, **kwargs: Any) -> dict[str, Any]: ...

class MemorySsl:
    """Type stub for MemorySsl."""

    def __init__(self, client: IHTTPClient) -> None: ...
    def get(self, **kwargs: Any) -> dict[str, Any]: ...

class MemoryTraffic:
    """Type stub for MemoryTraffic."""

    fortiview: MemoryTrafficFortiview
    forward: MemoryTrafficForward
    local: MemoryTrafficLocal
    multicast: MemoryTrafficMulticast
    sniffer: MemoryTrafficSniffer
    threat: MemoryTrafficThreat

    def __init__(self, client: IHTTPClient) -> None: ...

class MemoryTrafficFortiview:
    """Type stub for MemoryTrafficFortiview."""

    def __init__(self, client: IHTTPClient) -> None: ...
    def get(self, **kwargs: Any) -> dict[str, Any]: ...

class MemoryTrafficForward:
    """Type stub for MemoryTrafficForward."""

    def __init__(self, client: IHTTPClient) -> None: ...
    def get(self, **kwargs: Any) -> dict[str, Any]: ...

class MemoryTrafficLocal:
    """Type stub for MemoryTrafficLocal."""

    def __init__(self, client: IHTTPClient) -> None: ...
    def get(self, **kwargs: Any) -> dict[str, Any]: ...

class MemoryTrafficMulticast:
    """Type stub for MemoryTrafficMulticast."""

    def __init__(self, client: IHTTPClient) -> None: ...
    def get(self, **kwargs: Any) -> dict[str, Any]: ...

class MemoryTrafficSniffer:
    """Type stub for MemoryTrafficSniffer."""

    def __init__(self, client: IHTTPClient) -> None: ...
    def get(self, **kwargs: Any) -> dict[str, Any]: ...

class MemoryTrafficThreat:
    """Type stub for MemoryTrafficThreat."""

    def __init__(self, client: IHTTPClient) -> None: ...
    def get(self, **kwargs: Any) -> dict[str, Any]: ...

class MemoryVirus:
    """Type stub for MemoryVirus."""

    def __init__(self, client: IHTTPClient) -> None: ...
    def get(self, **kwargs: Any) -> dict[str, Any]: ...

class MemoryVoip:
    """Type stub for MemoryVoip."""

    def __init__(self, client: IHTTPClient) -> None: ...
    def get(self, **kwargs: Any) -> dict[str, Any]: ...

class MemoryWaf:
    """Type stub for MemoryWaf."""

    def __init__(self, client: IHTTPClient) -> None: ...
    def get(self, **kwargs: Any) -> dict[str, Any]: ...

class MemoryWebfilter:
    """Type stub for MemoryWebfilter."""

    def __init__(self, client: IHTTPClient) -> None: ...
    def get(self, **kwargs: Any) -> dict[str, Any]: ...
