"""Type stubs for EMAILFILTER category."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hfortix_core.http.interface import IHTTPClient
    from .block_allow_list import BlockAllowList
    from .bword import Bword
    from .dnsbl import Dnsbl
    from .fortishield import Fortishield
    from .iptrust import Iptrust
    from .mheader import Mheader
    from .options import Options
    from .profile import Profile


class Emailfilter:
    """Type stub for Emailfilter."""

    block_allow_list: BlockAllowList
    bword: Bword
    dnsbl: Dnsbl
    fortishield: Fortishield
    iptrust: Iptrust
    mheader: Mheader
    options: Options
    profile: Profile

    def __init__(self, client: IHTTPClient) -> None: ...
