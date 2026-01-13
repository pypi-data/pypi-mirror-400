"""Type stubs for CERTIFICATE category."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hfortix_core.http.interface import IHTTPClient
    from .ca import Ca
    from .crl import Crl
    from .hsm_local import HsmLocal
    from .local import Local
    from .ocsp_server import OcspServer
    from .remote import Remote
    from .setting import Setting


class Certificate:
    """Type stub for Certificate."""

    ca: Ca
    crl: Crl
    hsm_local: HsmLocal
    local: Local
    ocsp_server: OcspServer
    remote: Remote
    setting: Setting

    def __init__(self, client: IHTTPClient) -> None: ...
