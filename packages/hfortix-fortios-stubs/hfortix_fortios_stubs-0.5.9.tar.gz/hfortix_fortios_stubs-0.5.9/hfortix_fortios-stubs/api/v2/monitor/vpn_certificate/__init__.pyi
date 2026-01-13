"""Type stubs for VPN_CERTIFICATE category."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hfortix_core.http.interface import IHTTPClient
    from .cert_name_available import CertNameAvailable
    from .ca import Ca
    from .crl import Crl
    from .csr import Csr
    from .local import Local
    from .remote import Remote


class VpnCertificate:
    """Type stub for VpnCertificate."""

    ca: Ca
    crl: Crl
    csr: Csr
    local: Local
    remote: Remote
    cert_name_available: CertNameAvailable

    def __init__(self, client: IHTTPClient) -> None: ...
