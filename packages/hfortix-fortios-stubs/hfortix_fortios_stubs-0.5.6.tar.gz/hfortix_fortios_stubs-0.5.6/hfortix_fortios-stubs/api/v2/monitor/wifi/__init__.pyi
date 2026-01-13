"""Type stubs for WIFI category."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hfortix_core.http.interface import IHTTPClient
    from .ap_channels import ApChannels
    from .ap_names import ApNames
    from .ap_status import ApStatus
    from .interfering_ap import InterferingAp
    from .matched_devices import MatchedDevices
    from .meta import Meta
    from .station_capability import StationCapability
    from .statistics import Statistics
    from .unassociated_devices import UnassociatedDevices
    from .ap_profile import ApProfile
    from .client import Client
    from .euclid import Euclid
    from .firmware import Firmware
    from .managed_ap import ManagedAp
    from .nac_device import NacDevice
    from .network import Network
    from .region_image import RegionImage
    from .rogue_ap import RogueAp
    from .spectrum import Spectrum
    from .ssid import Ssid
    from .vlan_probe import VlanProbe


class Wifi:
    """Type stub for Wifi."""

    ap_profile: ApProfile
    client: Client
    euclid: Euclid
    firmware: Firmware
    managed_ap: ManagedAp
    nac_device: NacDevice
    network: Network
    region_image: RegionImage
    rogue_ap: RogueAp
    spectrum: Spectrum
    ssid: Ssid
    vlan_probe: VlanProbe
    ap_channels: ApChannels
    ap_names: ApNames
    ap_status: ApStatus
    interfering_ap: InterferingAp
    matched_devices: MatchedDevices
    meta: Meta
    station_capability: StationCapability
    statistics: Statistics
    unassociated_devices: UnassociatedDevices

    def __init__(self, client: IHTTPClient) -> None: ...
