"""Type stubs for MCLAG_ICL category."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hfortix_core.http.interface import IHTTPClient
    from .eligible_peer import EligiblePeer
    from .set_tier1 import SetTier1
    from .set_tier_plus import SetTierPlus
    from .tier_plus_candidates import TierPlusCandidates


class MclagIcl:
    """Type stub for MclagIcl."""

    eligible_peer: EligiblePeer
    set_tier1: SetTier1
    set_tier_plus: SetTierPlus
    tier_plus_candidates: TierPlusCandidates

    def __init__(self, client: IHTTPClient) -> None: ...
