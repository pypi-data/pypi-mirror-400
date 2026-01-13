"""Type stubs for LOG endpoint."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from hfortix_core.http.interface import IHTTPClient


class Disk:
    """Type stub for Disk."""

    anomaly: DiskAnomaly
    app_ctrl: DiskAppCtrl
    cifs: DiskCifs
    dlp: DiskDlp
    dns: DiskDns
    emailfilter: DiskEmailfilter
    event: DiskEvent
    file_filter: DiskFileFilter
    gtp: DiskGtp
    ips: DiskIps
    ssh: DiskSsh
    ssl: DiskSsl
    traffic: DiskTraffic
    virus: DiskVirus
    voip: DiskVoip
    waf: DiskWaf
    webfilter: DiskWebfilter

    def __init__(self, client: IHTTPClient) -> None: ...

class DiskAnomaly:
    """Type stub for DiskAnomaly."""

    def __init__(self, client: IHTTPClient) -> None: ...
    def get(self, **kwargs: Any) -> dict[str, Any]: ...

class DiskAppCtrl:
    """Type stub for DiskAppCtrl."""

    archive: DiskAppCtrlArchive
    archive_download: DiskAppCtrlArchiveDownload

    def __init__(self, client: IHTTPClient) -> None: ...
    def get(self, **kwargs: Any) -> dict[str, Any]: ...

class DiskAppCtrlArchive:
    """Type stub for DiskAppCtrlArchive."""

    def __init__(self, client: IHTTPClient) -> None: ...
    def get(self, **kwargs: Any) -> dict[str, Any]: ...

class DiskAppCtrlArchiveDownload:
    """Type stub for DiskAppCtrlArchiveDownload."""

    def __init__(self, client: IHTTPClient) -> None: ...
    def get(self, **kwargs: Any) -> dict[str, Any]: ...

class DiskCifs:
    """Type stub for DiskCifs."""

    def __init__(self, client: IHTTPClient) -> None: ...
    def get(self, **kwargs: Any) -> dict[str, Any]: ...

class DiskDlp:
    """Type stub for DiskDlp."""

    def __init__(self, client: IHTTPClient) -> None: ...
    def get(self, **kwargs: Any) -> dict[str, Any]: ...

class DiskDns:
    """Type stub for DiskDns."""

    def __init__(self, client: IHTTPClient) -> None: ...
    def get(self, **kwargs: Any) -> dict[str, Any]: ...

class DiskEmailfilter:
    """Type stub for DiskEmailfilter."""

    def __init__(self, client: IHTTPClient) -> None: ...
    def get(self, **kwargs: Any) -> dict[str, Any]: ...

class DiskEvent:
    """Type stub for DiskEvent."""

    compliance_check: DiskEventComplianceCheck
    connector: DiskEventConnector
    endpoint: DiskEventEndpoint
    fortiextender: DiskEventFortiextender
    ha: DiskEventHa
    router: DiskEventRouter
    security_rating: DiskEventSecurityRating
    system: DiskEventSystem
    user: DiskEventUser
    vpn: DiskEventVpn
    wad: DiskEventWad
    wireless: DiskEventWireless

    def __init__(self, client: IHTTPClient) -> None: ...

class DiskEventComplianceCheck:
    """Type stub for DiskEventComplianceCheck."""

    def __init__(self, client: IHTTPClient) -> None: ...
    def get(self, **kwargs: Any) -> dict[str, Any]: ...

class DiskEventConnector:
    """Type stub for DiskEventConnector."""

    def __init__(self, client: IHTTPClient) -> None: ...
    def get(self, **kwargs: Any) -> dict[str, Any]: ...

class DiskEventEndpoint:
    """Type stub for DiskEventEndpoint."""

    def __init__(self, client: IHTTPClient) -> None: ...
    def get(self, **kwargs: Any) -> dict[str, Any]: ...

class DiskEventFortiextender:
    """Type stub for DiskEventFortiextender."""

    def __init__(self, client: IHTTPClient) -> None: ...
    def get(self, **kwargs: Any) -> dict[str, Any]: ...

class DiskEventHa:
    """Type stub for DiskEventHa."""

    def __init__(self, client: IHTTPClient) -> None: ...
    def get(self, **kwargs: Any) -> dict[str, Any]: ...

class DiskEventRouter:
    """Type stub for DiskEventRouter."""

    def __init__(self, client: IHTTPClient) -> None: ...
    def get(self, **kwargs: Any) -> dict[str, Any]: ...

class DiskEventSecurityRating:
    """Type stub for DiskEventSecurityRating."""

    def __init__(self, client: IHTTPClient) -> None: ...
    def get(self, **kwargs: Any) -> dict[str, Any]: ...

class DiskEventSystem:
    """Type stub for DiskEventSystem."""

    def __init__(self, client: IHTTPClient) -> None: ...
    def get(self, **kwargs: Any) -> dict[str, Any]: ...

class DiskEventUser:
    """Type stub for DiskEventUser."""

    def __init__(self, client: IHTTPClient) -> None: ...
    def get(self, **kwargs: Any) -> dict[str, Any]: ...

class DiskEventVpn:
    """Type stub for DiskEventVpn."""

    def __init__(self, client: IHTTPClient) -> None: ...
    def get(self, **kwargs: Any) -> dict[str, Any]: ...

class DiskEventWad:
    """Type stub for DiskEventWad."""

    def __init__(self, client: IHTTPClient) -> None: ...
    def get(self, **kwargs: Any) -> dict[str, Any]: ...

class DiskEventWireless:
    """Type stub for DiskEventWireless."""

    def __init__(self, client: IHTTPClient) -> None: ...
    def get(self, **kwargs: Any) -> dict[str, Any]: ...

class DiskFileFilter:
    """Type stub for DiskFileFilter."""

    def __init__(self, client: IHTTPClient) -> None: ...
    def get(self, **kwargs: Any) -> dict[str, Any]: ...

class DiskGtp:
    """Type stub for DiskGtp."""

    def __init__(self, client: IHTTPClient) -> None: ...
    def get(self, **kwargs: Any) -> dict[str, Any]: ...

class DiskIps:
    """Type stub for DiskIps."""

    archive: DiskIpsArchive
    archive_download: DiskIpsArchiveDownload

    def __init__(self, client: IHTTPClient) -> None: ...
    def get(self, **kwargs: Any) -> dict[str, Any]: ...

class DiskIpsArchive:
    """Type stub for DiskIpsArchive."""

    def __init__(self, client: IHTTPClient) -> None: ...
    def get(self, **kwargs: Any) -> dict[str, Any]: ...

class DiskIpsArchiveDownload:
    """Type stub for DiskIpsArchiveDownload."""

    def __init__(self, client: IHTTPClient) -> None: ...
    def get(self, **kwargs: Any) -> dict[str, Any]: ...

class DiskSsh:
    """Type stub for DiskSsh."""

    def __init__(self, client: IHTTPClient) -> None: ...
    def get(self, **kwargs: Any) -> dict[str, Any]: ...

class DiskSsl:
    """Type stub for DiskSsl."""

    def __init__(self, client: IHTTPClient) -> None: ...
    def get(self, **kwargs: Any) -> dict[str, Any]: ...

class DiskTraffic:
    """Type stub for DiskTraffic."""

    fortiview: DiskTrafficFortiview
    forward: DiskTrafficForward
    local: DiskTrafficLocal
    multicast: DiskTrafficMulticast
    sniffer: DiskTrafficSniffer
    threat: DiskTrafficThreat

    def __init__(self, client: IHTTPClient) -> None: ...

class DiskTrafficFortiview:
    """Type stub for DiskTrafficFortiview."""

    def __init__(self, client: IHTTPClient) -> None: ...
    def get(self, **kwargs: Any) -> dict[str, Any]: ...

class DiskTrafficForward:
    """Type stub for DiskTrafficForward."""

    def __init__(self, client: IHTTPClient) -> None: ...
    def get(self, **kwargs: Any) -> dict[str, Any]: ...

class DiskTrafficLocal:
    """Type stub for DiskTrafficLocal."""

    def __init__(self, client: IHTTPClient) -> None: ...
    def get(self, **kwargs: Any) -> dict[str, Any]: ...

class DiskTrafficMulticast:
    """Type stub for DiskTrafficMulticast."""

    def __init__(self, client: IHTTPClient) -> None: ...
    def get(self, **kwargs: Any) -> dict[str, Any]: ...

class DiskTrafficSniffer:
    """Type stub for DiskTrafficSniffer."""

    def __init__(self, client: IHTTPClient) -> None: ...
    def get(self, **kwargs: Any) -> dict[str, Any]: ...

class DiskTrafficThreat:
    """Type stub for DiskTrafficThreat."""

    def __init__(self, client: IHTTPClient) -> None: ...
    def get(self, **kwargs: Any) -> dict[str, Any]: ...

class DiskVirus:
    """Type stub for DiskVirus."""

    def __init__(self, client: IHTTPClient) -> None: ...
    def get(self, **kwargs: Any) -> dict[str, Any]: ...

class DiskVoip:
    """Type stub for DiskVoip."""

    def __init__(self, client: IHTTPClient) -> None: ...
    def get(self, **kwargs: Any) -> dict[str, Any]: ...

class DiskWaf:
    """Type stub for DiskWaf."""

    def __init__(self, client: IHTTPClient) -> None: ...
    def get(self, **kwargs: Any) -> dict[str, Any]: ...

class DiskWebfilter:
    """Type stub for DiskWebfilter."""

    def __init__(self, client: IHTTPClient) -> None: ...
    def get(self, **kwargs: Any) -> dict[str, Any]: ...
