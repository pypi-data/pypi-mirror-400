"""Type stubs for LOG endpoint."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from hfortix_core.http.interface import IHTTPClient


class Fortianalyzer:
    """Type stub for Fortianalyzer."""

    anomaly: FortianalyzerAnomaly
    app_ctrl: FortianalyzerAppCtrl
    cifs: FortianalyzerCifs
    dlp: FortianalyzerDlp
    dns: FortianalyzerDns
    emailfilter: FortianalyzerEmailfilter
    event: FortianalyzerEvent
    file_filter: FortianalyzerFileFilter
    gtp: FortianalyzerGtp
    ips: FortianalyzerIps
    ssh: FortianalyzerSsh
    ssl: FortianalyzerSsl
    traffic: FortianalyzerTraffic
    virus: FortianalyzerVirus
    voip: FortianalyzerVoip
    waf: FortianalyzerWaf
    webfilter: FortianalyzerWebfilter

    def __init__(self, client: IHTTPClient) -> None: ...

class FortianalyzerAnomaly:
    """Type stub for FortianalyzerAnomaly."""

    def __init__(self, client: IHTTPClient) -> None: ...
    def get(self, **kwargs: Any) -> dict[str, Any]: ...

class FortianalyzerAppCtrl:
    """Type stub for FortianalyzerAppCtrl."""

    archive: FortianalyzerAppCtrlArchive
    archive_download: FortianalyzerAppCtrlArchiveDownload

    def __init__(self, client: IHTTPClient) -> None: ...
    def get(self, **kwargs: Any) -> dict[str, Any]: ...

class FortianalyzerAppCtrlArchive:
    """Type stub for FortianalyzerAppCtrlArchive."""

    def __init__(self, client: IHTTPClient) -> None: ...
    def get(self, **kwargs: Any) -> dict[str, Any]: ...

class FortianalyzerAppCtrlArchiveDownload:
    """Type stub for FortianalyzerAppCtrlArchiveDownload."""

    def __init__(self, client: IHTTPClient) -> None: ...
    def get(self, **kwargs: Any) -> dict[str, Any]: ...

class FortianalyzerCifs:
    """Type stub for FortianalyzerCifs."""

    def __init__(self, client: IHTTPClient) -> None: ...
    def get(self, **kwargs: Any) -> dict[str, Any]: ...

class FortianalyzerDlp:
    """Type stub for FortianalyzerDlp."""

    def __init__(self, client: IHTTPClient) -> None: ...
    def get(self, **kwargs: Any) -> dict[str, Any]: ...

class FortianalyzerDns:
    """Type stub for FortianalyzerDns."""

    def __init__(self, client: IHTTPClient) -> None: ...
    def get(self, **kwargs: Any) -> dict[str, Any]: ...

class FortianalyzerEmailfilter:
    """Type stub for FortianalyzerEmailfilter."""

    def __init__(self, client: IHTTPClient) -> None: ...
    def get(self, **kwargs: Any) -> dict[str, Any]: ...

class FortianalyzerEvent:
    """Type stub for FortianalyzerEvent."""

    compliance_check: FortianalyzerEventComplianceCheck
    connector: FortianalyzerEventConnector
    endpoint: FortianalyzerEventEndpoint
    fortiextender: FortianalyzerEventFortiextender
    ha: FortianalyzerEventHa
    router: FortianalyzerEventRouter
    security_rating: FortianalyzerEventSecurityRating
    system: FortianalyzerEventSystem
    user: FortianalyzerEventUser
    vpn: FortianalyzerEventVpn
    wad: FortianalyzerEventWad
    wireless: FortianalyzerEventWireless

    def __init__(self, client: IHTTPClient) -> None: ...

class FortianalyzerEventComplianceCheck:
    """Type stub for FortianalyzerEventComplianceCheck."""

    def __init__(self, client: IHTTPClient) -> None: ...
    def get(self, **kwargs: Any) -> dict[str, Any]: ...

class FortianalyzerEventConnector:
    """Type stub for FortianalyzerEventConnector."""

    def __init__(self, client: IHTTPClient) -> None: ...
    def get(self, **kwargs: Any) -> dict[str, Any]: ...

class FortianalyzerEventEndpoint:
    """Type stub for FortianalyzerEventEndpoint."""

    def __init__(self, client: IHTTPClient) -> None: ...
    def get(self, **kwargs: Any) -> dict[str, Any]: ...

class FortianalyzerEventFortiextender:
    """Type stub for FortianalyzerEventFortiextender."""

    def __init__(self, client: IHTTPClient) -> None: ...
    def get(self, **kwargs: Any) -> dict[str, Any]: ...

class FortianalyzerEventHa:
    """Type stub for FortianalyzerEventHa."""

    def __init__(self, client: IHTTPClient) -> None: ...
    def get(self, **kwargs: Any) -> dict[str, Any]: ...

class FortianalyzerEventRouter:
    """Type stub for FortianalyzerEventRouter."""

    def __init__(self, client: IHTTPClient) -> None: ...
    def get(self, **kwargs: Any) -> dict[str, Any]: ...

class FortianalyzerEventSecurityRating:
    """Type stub for FortianalyzerEventSecurityRating."""

    def __init__(self, client: IHTTPClient) -> None: ...
    def get(self, **kwargs: Any) -> dict[str, Any]: ...

class FortianalyzerEventSystem:
    """Type stub for FortianalyzerEventSystem."""

    def __init__(self, client: IHTTPClient) -> None: ...
    def get(self, **kwargs: Any) -> dict[str, Any]: ...

class FortianalyzerEventUser:
    """Type stub for FortianalyzerEventUser."""

    def __init__(self, client: IHTTPClient) -> None: ...
    def get(self, **kwargs: Any) -> dict[str, Any]: ...

class FortianalyzerEventVpn:
    """Type stub for FortianalyzerEventVpn."""

    def __init__(self, client: IHTTPClient) -> None: ...
    def get(self, **kwargs: Any) -> dict[str, Any]: ...

class FortianalyzerEventWad:
    """Type stub for FortianalyzerEventWad."""

    def __init__(self, client: IHTTPClient) -> None: ...
    def get(self, **kwargs: Any) -> dict[str, Any]: ...

class FortianalyzerEventWireless:
    """Type stub for FortianalyzerEventWireless."""

    def __init__(self, client: IHTTPClient) -> None: ...
    def get(self, **kwargs: Any) -> dict[str, Any]: ...

class FortianalyzerFileFilter:
    """Type stub for FortianalyzerFileFilter."""

    def __init__(self, client: IHTTPClient) -> None: ...
    def get(self, **kwargs: Any) -> dict[str, Any]: ...

class FortianalyzerGtp:
    """Type stub for FortianalyzerGtp."""

    def __init__(self, client: IHTTPClient) -> None: ...
    def get(self, **kwargs: Any) -> dict[str, Any]: ...

class FortianalyzerIps:
    """Type stub for FortianalyzerIps."""

    archive: FortianalyzerIpsArchive
    archive_download: FortianalyzerIpsArchiveDownload

    def __init__(self, client: IHTTPClient) -> None: ...
    def get(self, **kwargs: Any) -> dict[str, Any]: ...

class FortianalyzerIpsArchive:
    """Type stub for FortianalyzerIpsArchive."""

    def __init__(self, client: IHTTPClient) -> None: ...
    def get(self, **kwargs: Any) -> dict[str, Any]: ...

class FortianalyzerIpsArchiveDownload:
    """Type stub for FortianalyzerIpsArchiveDownload."""

    def __init__(self, client: IHTTPClient) -> None: ...
    def get(self, **kwargs: Any) -> dict[str, Any]: ...

class FortianalyzerSsh:
    """Type stub for FortianalyzerSsh."""

    def __init__(self, client: IHTTPClient) -> None: ...
    def get(self, **kwargs: Any) -> dict[str, Any]: ...

class FortianalyzerSsl:
    """Type stub for FortianalyzerSsl."""

    def __init__(self, client: IHTTPClient) -> None: ...
    def get(self, **kwargs: Any) -> dict[str, Any]: ...

class FortianalyzerTraffic:
    """Type stub for FortianalyzerTraffic."""

    fortiview: FortianalyzerTrafficFortiview
    forward: FortianalyzerTrafficForward
    local: FortianalyzerTrafficLocal
    multicast: FortianalyzerTrafficMulticast
    sniffer: FortianalyzerTrafficSniffer
    threat: FortianalyzerTrafficThreat

    def __init__(self, client: IHTTPClient) -> None: ...

class FortianalyzerTrafficFortiview:
    """Type stub for FortianalyzerTrafficFortiview."""

    def __init__(self, client: IHTTPClient) -> None: ...
    def get(self, **kwargs: Any) -> dict[str, Any]: ...

class FortianalyzerTrafficForward:
    """Type stub for FortianalyzerTrafficForward."""

    def __init__(self, client: IHTTPClient) -> None: ...
    def get(self, **kwargs: Any) -> dict[str, Any]: ...

class FortianalyzerTrafficLocal:
    """Type stub for FortianalyzerTrafficLocal."""

    def __init__(self, client: IHTTPClient) -> None: ...
    def get(self, **kwargs: Any) -> dict[str, Any]: ...

class FortianalyzerTrafficMulticast:
    """Type stub for FortianalyzerTrafficMulticast."""

    def __init__(self, client: IHTTPClient) -> None: ...
    def get(self, **kwargs: Any) -> dict[str, Any]: ...

class FortianalyzerTrafficSniffer:
    """Type stub for FortianalyzerTrafficSniffer."""

    def __init__(self, client: IHTTPClient) -> None: ...
    def get(self, **kwargs: Any) -> dict[str, Any]: ...

class FortianalyzerTrafficThreat:
    """Type stub for FortianalyzerTrafficThreat."""

    def __init__(self, client: IHTTPClient) -> None: ...
    def get(self, **kwargs: Any) -> dict[str, Any]: ...

class FortianalyzerVirus:
    """Type stub for FortianalyzerVirus."""

    def __init__(self, client: IHTTPClient) -> None: ...
    def get(self, **kwargs: Any) -> dict[str, Any]: ...

class FortianalyzerVoip:
    """Type stub for FortianalyzerVoip."""

    def __init__(self, client: IHTTPClient) -> None: ...
    def get(self, **kwargs: Any) -> dict[str, Any]: ...

class FortianalyzerWaf:
    """Type stub for FortianalyzerWaf."""

    def __init__(self, client: IHTTPClient) -> None: ...
    def get(self, **kwargs: Any) -> dict[str, Any]: ...

class FortianalyzerWebfilter:
    """Type stub for FortianalyzerWebfilter."""

    def __init__(self, client: IHTTPClient) -> None: ...
    def get(self, **kwargs: Any) -> dict[str, Any]: ...
