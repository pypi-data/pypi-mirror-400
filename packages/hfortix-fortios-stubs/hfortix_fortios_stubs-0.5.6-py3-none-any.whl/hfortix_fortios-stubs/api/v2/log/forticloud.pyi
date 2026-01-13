"""Type stubs for LOG endpoint."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from hfortix_core.http.interface import IHTTPClient


class Forticloud:
    """Type stub for Forticloud."""

    anomaly: ForticloudAnomaly
    app_ctrl: ForticloudAppCtrl
    cifs: ForticloudCifs
    dlp: ForticloudDlp
    dns: ForticloudDns
    emailfilter: ForticloudEmailfilter
    event: ForticloudEvent
    file_filter: ForticloudFileFilter
    gtp: ForticloudGtp
    ips: ForticloudIps
    ssh: ForticloudSsh
    ssl: ForticloudSsl
    traffic: ForticloudTraffic
    virus: ForticloudVirus
    voip: ForticloudVoip
    waf: ForticloudWaf
    webfilter: ForticloudWebfilter

    def __init__(self, client: IHTTPClient) -> None: ...

class ForticloudAnomaly:
    """Type stub for ForticloudAnomaly."""

    def __init__(self, client: IHTTPClient) -> None: ...
    def get(self, **kwargs: Any) -> dict[str, Any]: ...

class ForticloudAppCtrl:
    """Type stub for ForticloudAppCtrl."""

    archive: ForticloudAppCtrlArchive
    archive_download: ForticloudAppCtrlArchiveDownload

    def __init__(self, client: IHTTPClient) -> None: ...
    def get(self, **kwargs: Any) -> dict[str, Any]: ...

class ForticloudAppCtrlArchive:
    """Type stub for ForticloudAppCtrlArchive."""

    def __init__(self, client: IHTTPClient) -> None: ...
    def get(self, **kwargs: Any) -> dict[str, Any]: ...

class ForticloudAppCtrlArchiveDownload:
    """Type stub for ForticloudAppCtrlArchiveDownload."""

    def __init__(self, client: IHTTPClient) -> None: ...
    def get(self, **kwargs: Any) -> dict[str, Any]: ...

class ForticloudCifs:
    """Type stub for ForticloudCifs."""

    def __init__(self, client: IHTTPClient) -> None: ...
    def get(self, **kwargs: Any) -> dict[str, Any]: ...

class ForticloudDlp:
    """Type stub for ForticloudDlp."""

    def __init__(self, client: IHTTPClient) -> None: ...
    def get(self, **kwargs: Any) -> dict[str, Any]: ...

class ForticloudDns:
    """Type stub for ForticloudDns."""

    def __init__(self, client: IHTTPClient) -> None: ...
    def get(self, **kwargs: Any) -> dict[str, Any]: ...

class ForticloudEmailfilter:
    """Type stub for ForticloudEmailfilter."""

    def __init__(self, client: IHTTPClient) -> None: ...
    def get(self, **kwargs: Any) -> dict[str, Any]: ...

class ForticloudEvent:
    """Type stub for ForticloudEvent."""

    compliance_check: ForticloudEventComplianceCheck
    connector: ForticloudEventConnector
    endpoint: ForticloudEventEndpoint
    fortiextender: ForticloudEventFortiextender
    ha: ForticloudEventHa
    router: ForticloudEventRouter
    security_rating: ForticloudEventSecurityRating
    system: ForticloudEventSystem
    user: ForticloudEventUser
    vpn: ForticloudEventVpn
    wad: ForticloudEventWad
    wireless: ForticloudEventWireless

    def __init__(self, client: IHTTPClient) -> None: ...

class ForticloudEventComplianceCheck:
    """Type stub for ForticloudEventComplianceCheck."""

    def __init__(self, client: IHTTPClient) -> None: ...
    def get(self, **kwargs: Any) -> dict[str, Any]: ...

class ForticloudEventConnector:
    """Type stub for ForticloudEventConnector."""

    def __init__(self, client: IHTTPClient) -> None: ...
    def get(self, **kwargs: Any) -> dict[str, Any]: ...

class ForticloudEventEndpoint:
    """Type stub for ForticloudEventEndpoint."""

    def __init__(self, client: IHTTPClient) -> None: ...
    def get(self, **kwargs: Any) -> dict[str, Any]: ...

class ForticloudEventFortiextender:
    """Type stub for ForticloudEventFortiextender."""

    def __init__(self, client: IHTTPClient) -> None: ...
    def get(self, **kwargs: Any) -> dict[str, Any]: ...

class ForticloudEventHa:
    """Type stub for ForticloudEventHa."""

    def __init__(self, client: IHTTPClient) -> None: ...
    def get(self, **kwargs: Any) -> dict[str, Any]: ...

class ForticloudEventRouter:
    """Type stub for ForticloudEventRouter."""

    def __init__(self, client: IHTTPClient) -> None: ...
    def get(self, **kwargs: Any) -> dict[str, Any]: ...

class ForticloudEventSecurityRating:
    """Type stub for ForticloudEventSecurityRating."""

    def __init__(self, client: IHTTPClient) -> None: ...
    def get(self, **kwargs: Any) -> dict[str, Any]: ...

class ForticloudEventSystem:
    """Type stub for ForticloudEventSystem."""

    def __init__(self, client: IHTTPClient) -> None: ...
    def get(self, **kwargs: Any) -> dict[str, Any]: ...

class ForticloudEventUser:
    """Type stub for ForticloudEventUser."""

    def __init__(self, client: IHTTPClient) -> None: ...
    def get(self, **kwargs: Any) -> dict[str, Any]: ...

class ForticloudEventVpn:
    """Type stub for ForticloudEventVpn."""

    def __init__(self, client: IHTTPClient) -> None: ...
    def get(self, **kwargs: Any) -> dict[str, Any]: ...

class ForticloudEventWad:
    """Type stub for ForticloudEventWad."""

    def __init__(self, client: IHTTPClient) -> None: ...
    def get(self, **kwargs: Any) -> dict[str, Any]: ...

class ForticloudEventWireless:
    """Type stub for ForticloudEventWireless."""

    def __init__(self, client: IHTTPClient) -> None: ...
    def get(self, **kwargs: Any) -> dict[str, Any]: ...

class ForticloudFileFilter:
    """Type stub for ForticloudFileFilter."""

    def __init__(self, client: IHTTPClient) -> None: ...
    def get(self, **kwargs: Any) -> dict[str, Any]: ...

class ForticloudGtp:
    """Type stub for ForticloudGtp."""

    def __init__(self, client: IHTTPClient) -> None: ...
    def get(self, **kwargs: Any) -> dict[str, Any]: ...

class ForticloudIps:
    """Type stub for ForticloudIps."""

    archive: ForticloudIpsArchive
    archive_download: ForticloudIpsArchiveDownload

    def __init__(self, client: IHTTPClient) -> None: ...
    def get(self, **kwargs: Any) -> dict[str, Any]: ...

class ForticloudIpsArchive:
    """Type stub for ForticloudIpsArchive."""

    def __init__(self, client: IHTTPClient) -> None: ...
    def get(self, **kwargs: Any) -> dict[str, Any]: ...

class ForticloudIpsArchiveDownload:
    """Type stub for ForticloudIpsArchiveDownload."""

    def __init__(self, client: IHTTPClient) -> None: ...
    def get(self, **kwargs: Any) -> dict[str, Any]: ...

class ForticloudSsh:
    """Type stub for ForticloudSsh."""

    def __init__(self, client: IHTTPClient) -> None: ...
    def get(self, **kwargs: Any) -> dict[str, Any]: ...

class ForticloudSsl:
    """Type stub for ForticloudSsl."""

    def __init__(self, client: IHTTPClient) -> None: ...
    def get(self, **kwargs: Any) -> dict[str, Any]: ...

class ForticloudTraffic:
    """Type stub for ForticloudTraffic."""

    fortiview: ForticloudTrafficFortiview
    forward: ForticloudTrafficForward
    local: ForticloudTrafficLocal
    multicast: ForticloudTrafficMulticast
    sniffer: ForticloudTrafficSniffer
    threat: ForticloudTrafficThreat

    def __init__(self, client: IHTTPClient) -> None: ...

class ForticloudTrafficFortiview:
    """Type stub for ForticloudTrafficFortiview."""

    def __init__(self, client: IHTTPClient) -> None: ...
    def get(self, **kwargs: Any) -> dict[str, Any]: ...

class ForticloudTrafficForward:
    """Type stub for ForticloudTrafficForward."""

    def __init__(self, client: IHTTPClient) -> None: ...
    def get(self, **kwargs: Any) -> dict[str, Any]: ...

class ForticloudTrafficLocal:
    """Type stub for ForticloudTrafficLocal."""

    def __init__(self, client: IHTTPClient) -> None: ...
    def get(self, **kwargs: Any) -> dict[str, Any]: ...

class ForticloudTrafficMulticast:
    """Type stub for ForticloudTrafficMulticast."""

    def __init__(self, client: IHTTPClient) -> None: ...
    def get(self, **kwargs: Any) -> dict[str, Any]: ...

class ForticloudTrafficSniffer:
    """Type stub for ForticloudTrafficSniffer."""

    def __init__(self, client: IHTTPClient) -> None: ...
    def get(self, **kwargs: Any) -> dict[str, Any]: ...

class ForticloudTrafficThreat:
    """Type stub for ForticloudTrafficThreat."""

    def __init__(self, client: IHTTPClient) -> None: ...
    def get(self, **kwargs: Any) -> dict[str, Any]: ...

class ForticloudVirus:
    """Type stub for ForticloudVirus."""

    def __init__(self, client: IHTTPClient) -> None: ...
    def get(self, **kwargs: Any) -> dict[str, Any]: ...

class ForticloudVoip:
    """Type stub for ForticloudVoip."""

    def __init__(self, client: IHTTPClient) -> None: ...
    def get(self, **kwargs: Any) -> dict[str, Any]: ...

class ForticloudWaf:
    """Type stub for ForticloudWaf."""

    def __init__(self, client: IHTTPClient) -> None: ...
    def get(self, **kwargs: Any) -> dict[str, Any]: ...

class ForticloudWebfilter:
    """Type stub for ForticloudWebfilter."""

    def __init__(self, client: IHTTPClient) -> None: ...
    def get(self, **kwargs: Any) -> dict[str, Any]: ...
