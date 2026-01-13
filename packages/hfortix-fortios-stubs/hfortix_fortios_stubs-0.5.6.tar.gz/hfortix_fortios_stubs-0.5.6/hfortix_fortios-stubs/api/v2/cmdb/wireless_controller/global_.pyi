from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class GlobalPayload(TypedDict, total=False):
    """
    Type hints for wireless_controller/global_ payload fields.
    
    Configure wireless controller global settings.
    
    **Usage:**
        payload: GlobalPayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    name: NotRequired[str]  # Name of the wireless controller.
    location: NotRequired[str]  # Description of the location of the wireless controller.
    acd_process_count: NotRequired[int]  # Configure the number cw_acd daemons for multi-core CPU suppo
    wpad_process_count: NotRequired[int]  # Wpad daemon process count for multi-core CPU support.
    image_download: NotRequired[Literal[{"description": "Enable WTP image download at join time", "help": "Enable WTP image download at join time.", "label": "Enable", "name": "enable"}, {"description": "Disable WTP image download at join time", "help": "Disable WTP image download at join time.", "label": "Disable", "name": "disable"}]]  # Enable/disable WTP image download at join time.
    rolling_wtp_upgrade: NotRequired[Literal[{"description": "Enable rolling WTP upgrade", "help": "Enable rolling WTP upgrade.", "label": "Enable", "name": "enable"}, {"description": "Disable rolling WTP upgrade", "help": "Disable rolling WTP upgrade.", "label": "Disable", "name": "disable"}]]  # Enable/disable rolling WTP upgrade (default = disable).
    rolling_wtp_upgrade_threshold: NotRequired[str]  # Minimum signal level/threshold in dBm required for the manag
    max_retransmit: NotRequired[int]  # Maximum number of tunnel packet retransmissions (0 - 64, def
    control_message_offload: NotRequired[Literal[{"description": "Ekahau blink protocol (EBP) frames", "help": "Ekahau blink protocol (EBP) frames.", "label": "Ebp Frame", "name": "ebp-frame"}, {"description": "AeroScout tag", "help": "AeroScout tag.", "label": "Aeroscout Tag", "name": "aeroscout-tag"}, {"description": "Rogue AP list", "help": "Rogue AP list.", "label": "Ap List", "name": "ap-list"}, {"description": "Rogue STA list", "help": "Rogue STA list.", "label": "Sta List", "name": "sta-list"}, {"description": "STA capability list", "help": "STA capability list.", "label": "Sta Cap List", "name": "sta-cap-list"}, {"description": "WTP, radio, VAP, and STA statistics", "help": "WTP, radio, VAP, and STA statistics.", "label": "Stats", "name": "stats"}, {"description": "AeroScout Mobile Unit (MU) report", "help": "AeroScout Mobile Unit (MU) report.", "label": "Aeroscout Mu", "name": "aeroscout-mu"}, {"description": "STA health log", "help": "STA health log.", "label": "Sta Health", "name": "sta-health"}, {"description": "Spectral analysis report", "help": "Spectral analysis report.", "label": "Spectral Analysis", "name": "spectral-analysis"}]]  # Configure CAPWAP control message data channel offload.
    data_ethernet_II: NotRequired[Literal[{"description": "Use Ethernet II frames with 802", "help": "Use Ethernet II frames with 802.3 data tunnel mode.", "label": "Enable", "name": "enable"}, {"description": "Use 802", "help": "Use 802.3 Ethernet frames with 802.3 data tunnel mode.", "label": "Disable", "name": "disable"}]]  # Configure the wireless controller to use Ethernet II or 802.
    link_aggregation: NotRequired[Literal[{"description": "Enable calculating the CAPWAP transmit hash", "help": "Enable calculating the CAPWAP transmit hash.", "label": "Enable", "name": "enable"}, {"description": "Disable calculating the CAPWAP transmit hash", "help": "Disable calculating the CAPWAP transmit hash.", "label": "Disable", "name": "disable"}]]  # Enable/disable calculating the CAPWAP transmit hash to load 
    mesh_eth_type: NotRequired[int]  # Mesh Ethernet identifier included in backhaul packets (0 - 6
    fiapp_eth_type: NotRequired[int]  # Ethernet type for Fortinet Inter-Access Point Protocol (IAPP
    discovery_mc_addr: NotRequired[str]  # Multicast IP address for AP discovery (default = 244.0.1.140
    discovery_mc_addr6: NotRequired[str]  # Multicast IPv6 address for AP discovery (default = FF02::18C
    max_clients: NotRequired[int]  # Maximum number of clients that can connect simultaneously (d
    rogue_scan_mac_adjacency: NotRequired[int]  # Maximum numerical difference between an AP's Ethernet and wi
    ipsec_base_ip: NotRequired[str]  # Base IP address for IPsec VPN tunnels between the access poi
    wtp_share: NotRequired[Literal[{"description": "WTP can be shared between all VDOMs", "help": "WTP can be shared between all VDOMs.", "label": "Enable", "name": "enable"}, {"description": "WTP can be used only in its own VDOM", "help": "WTP can be used only in its own VDOM.", "label": "Disable", "name": "disable"}]]  # Enable/disable sharing of WTPs between VDOMs.
    tunnel_mode: NotRequired[Literal[{"description": "Allow for backward compatible ciphers(3DES+SHA1+Strong list)", "help": "Allow for backward compatible ciphers(3DES+SHA1+Strong list).", "label": "Compatible", "name": "compatible"}, {"description": "Follow system level strong-crypto ciphers", "help": "Follow system level strong-crypto ciphers.", "label": "Strict", "name": "strict"}]]  # Compatible/strict tunnel mode.
    nac_interval: NotRequired[int]  # Interval in seconds between two WiFi network access control 
    ap_log_server: NotRequired[Literal[{"description": "Enable AP log server", "help": "Enable AP log server.", "label": "Enable", "name": "enable"}, {"description": "Disable AP log server", "help": "Disable AP log server.", "label": "Disable", "name": "disable"}]]  # Enable/disable configuring FortiGate to redirect wireless ev
    ap_log_server_ip: NotRequired[str]  # IP address that FortiGate or FortiAPs send log messages to.
    ap_log_server_port: NotRequired[int]  # Port that FortiGate or FortiAPs send log messages to.
    max_sta_offline: NotRequired[int]  # Maximum number of station offline stored on the controller (
    max_sta_offline_ip2mac: NotRequired[int]  # Maximum number of station offline ip2mac stored on the contr
    max_sta_cap: NotRequired[int]  # Maximum number of station cap stored on the controller (defa
    max_sta_cap_wtp: NotRequired[int]  # Maximum number of station cap's wtp info stored on the contr
    max_rogue_ap: NotRequired[int]  # Maximum number of rogue APs stored on the controller (defaul
    max_rogue_ap_wtp: NotRequired[int]  # Maximum number of rogue AP's wtp info stored on the controll
    max_rogue_sta: NotRequired[int]  # Maximum number of rogue stations stored on the controller (d
    max_wids_entry: NotRequired[int]  # Maximum number of wids entries stored on the controller (def
    max_ble_device: NotRequired[int]  # Maximum number of BLE devices stored on the controller (defa


class Global:
    """
    Configure wireless controller global settings.
    
    Path: wireless_controller/global_
    Category: cmdb
    """
    
    # Overloads for get() with response_mode="object"
    @overload
    def get(
        self,
        name: str | None = ...,
        filter: list[str] | None = ...,
        count: int | None = ...,
        start: int | None = ...,
        payload_dict: dict[str, Any] | None = ...,
        range: list[int] | None = ...,
        sort: str | None = ...,
        format: str | None = ...,
        action: str | None = ...,
        vdom: str | bool | None = ...,
        raw_json: Literal[False] = ...,
        response_mode: Literal["object"] = ...,
        **kwargs: Any,
    ) -> list[FortiObject]: ...
    
    @overload
    def get(
        self,
        name: str,
        filter: list[str] | None = ...,
        count: int | None = ...,
        start: int | None = ...,
        payload_dict: dict[str, Any] | None = ...,
        range: list[int] | None = ...,
        sort: str | None = ...,
        format: str | None = ...,
        action: str | None = ...,
        vdom: str | bool | None = ...,
        raw_json: Literal[False] = ...,
        response_mode: Literal["object"] = ...,
        **kwargs: Any,
    ) -> FortiObject: ...
    
    @overload
    def get(
        self,
        name: str | None = ...,
        filter: list[str] | None = ...,
        count: int | None = ...,
        start: int | None = ...,
        payload_dict: dict[str, Any] | None = ...,
        range: list[int] | None = ...,
        sort: str | None = ...,
        format: str | None = ...,
        action: str | None = ...,
        vdom: str | bool | None = ...,
        raw_json: Literal[True] = ...,
        response_mode: Literal["object"] = ...,
        **kwargs: Any,
    ) -> dict[str, Any]: ...
    
    # Default overload for dict mode
    @overload
    def get(
        self,
        name: str | None = ...,
        filter: list[str] | None = ...,
        count: int | None = ...,
        start: int | None = ...,
        payload_dict: dict[str, Any] | None = ...,
        range: list[int] | None = ...,
        sort: str | None = ...,
        format: str | None = ...,
        action: str | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        response_mode: Literal["dict"] | None = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], list[dict[str, Any]]]: ...
    
    def get(
        self,
        name: str | None = ...,
        filter: list[str] | None = ...,
        count: int | None = ...,
        start: int | None = ...,
        payload_dict: dict[str, Any] | None = ...,
        range: list[int] | None = ...,
        sort: str | None = ...,
        format: str | None = ...,
        action: str | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        response_mode: str | None = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], list[dict[str, Any]], FortiObject, list[FortiObject]]: ...
    
    def get_schema(
        self,
        vdom: str | None = ...,
        format: str = ...,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def post(
        self,
        payload_dict: GlobalPayload | None = ...,
        name: str | None = ...,
        location: str | None = ...,
        acd_process_count: int | None = ...,
        wpad_process_count: int | None = ...,
        image_download: Literal[{"description": "Enable WTP image download at join time", "help": "Enable WTP image download at join time.", "label": "Enable", "name": "enable"}, {"description": "Disable WTP image download at join time", "help": "Disable WTP image download at join time.", "label": "Disable", "name": "disable"}] | None = ...,
        rolling_wtp_upgrade: Literal[{"description": "Enable rolling WTP upgrade", "help": "Enable rolling WTP upgrade.", "label": "Enable", "name": "enable"}, {"description": "Disable rolling WTP upgrade", "help": "Disable rolling WTP upgrade.", "label": "Disable", "name": "disable"}] | None = ...,
        rolling_wtp_upgrade_threshold: str | None = ...,
        max_retransmit: int | None = ...,
        control_message_offload: Literal[{"description": "Ekahau blink protocol (EBP) frames", "help": "Ekahau blink protocol (EBP) frames.", "label": "Ebp Frame", "name": "ebp-frame"}, {"description": "AeroScout tag", "help": "AeroScout tag.", "label": "Aeroscout Tag", "name": "aeroscout-tag"}, {"description": "Rogue AP list", "help": "Rogue AP list.", "label": "Ap List", "name": "ap-list"}, {"description": "Rogue STA list", "help": "Rogue STA list.", "label": "Sta List", "name": "sta-list"}, {"description": "STA capability list", "help": "STA capability list.", "label": "Sta Cap List", "name": "sta-cap-list"}, {"description": "WTP, radio, VAP, and STA statistics", "help": "WTP, radio, VAP, and STA statistics.", "label": "Stats", "name": "stats"}, {"description": "AeroScout Mobile Unit (MU) report", "help": "AeroScout Mobile Unit (MU) report.", "label": "Aeroscout Mu", "name": "aeroscout-mu"}, {"description": "STA health log", "help": "STA health log.", "label": "Sta Health", "name": "sta-health"}, {"description": "Spectral analysis report", "help": "Spectral analysis report.", "label": "Spectral Analysis", "name": "spectral-analysis"}] | None = ...,
        data_ethernet_II: Literal[{"description": "Use Ethernet II frames with 802", "help": "Use Ethernet II frames with 802.3 data tunnel mode.", "label": "Enable", "name": "enable"}, {"description": "Use 802", "help": "Use 802.3 Ethernet frames with 802.3 data tunnel mode.", "label": "Disable", "name": "disable"}] | None = ...,
        link_aggregation: Literal[{"description": "Enable calculating the CAPWAP transmit hash", "help": "Enable calculating the CAPWAP transmit hash.", "label": "Enable", "name": "enable"}, {"description": "Disable calculating the CAPWAP transmit hash", "help": "Disable calculating the CAPWAP transmit hash.", "label": "Disable", "name": "disable"}] | None = ...,
        mesh_eth_type: int | None = ...,
        fiapp_eth_type: int | None = ...,
        discovery_mc_addr: str | None = ...,
        discovery_mc_addr6: str | None = ...,
        max_clients: int | None = ...,
        rogue_scan_mac_adjacency: int | None = ...,
        ipsec_base_ip: str | None = ...,
        wtp_share: Literal[{"description": "WTP can be shared between all VDOMs", "help": "WTP can be shared between all VDOMs.", "label": "Enable", "name": "enable"}, {"description": "WTP can be used only in its own VDOM", "help": "WTP can be used only in its own VDOM.", "label": "Disable", "name": "disable"}] | None = ...,
        tunnel_mode: Literal[{"description": "Allow for backward compatible ciphers(3DES+SHA1+Strong list)", "help": "Allow for backward compatible ciphers(3DES+SHA1+Strong list).", "label": "Compatible", "name": "compatible"}, {"description": "Follow system level strong-crypto ciphers", "help": "Follow system level strong-crypto ciphers.", "label": "Strict", "name": "strict"}] | None = ...,
        nac_interval: int | None = ...,
        ap_log_server: Literal[{"description": "Enable AP log server", "help": "Enable AP log server.", "label": "Enable", "name": "enable"}, {"description": "Disable AP log server", "help": "Disable AP log server.", "label": "Disable", "name": "disable"}] | None = ...,
        ap_log_server_ip: str | None = ...,
        ap_log_server_port: int | None = ...,
        max_sta_offline: int | None = ...,
        max_sta_offline_ip2mac: int | None = ...,
        max_sta_cap: int | None = ...,
        max_sta_cap_wtp: int | None = ...,
        max_rogue_ap: int | None = ...,
        max_rogue_ap_wtp: int | None = ...,
        max_rogue_sta: int | None = ...,
        max_wids_entry: int | None = ...,
        max_ble_device: int | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: GlobalPayload | None = ...,
        name: str | None = ...,
        location: str | None = ...,
        acd_process_count: int | None = ...,
        wpad_process_count: int | None = ...,
        image_download: Literal[{"description": "Enable WTP image download at join time", "help": "Enable WTP image download at join time.", "label": "Enable", "name": "enable"}, {"description": "Disable WTP image download at join time", "help": "Disable WTP image download at join time.", "label": "Disable", "name": "disable"}] | None = ...,
        rolling_wtp_upgrade: Literal[{"description": "Enable rolling WTP upgrade", "help": "Enable rolling WTP upgrade.", "label": "Enable", "name": "enable"}, {"description": "Disable rolling WTP upgrade", "help": "Disable rolling WTP upgrade.", "label": "Disable", "name": "disable"}] | None = ...,
        rolling_wtp_upgrade_threshold: str | None = ...,
        max_retransmit: int | None = ...,
        control_message_offload: Literal[{"description": "Ekahau blink protocol (EBP) frames", "help": "Ekahau blink protocol (EBP) frames.", "label": "Ebp Frame", "name": "ebp-frame"}, {"description": "AeroScout tag", "help": "AeroScout tag.", "label": "Aeroscout Tag", "name": "aeroscout-tag"}, {"description": "Rogue AP list", "help": "Rogue AP list.", "label": "Ap List", "name": "ap-list"}, {"description": "Rogue STA list", "help": "Rogue STA list.", "label": "Sta List", "name": "sta-list"}, {"description": "STA capability list", "help": "STA capability list.", "label": "Sta Cap List", "name": "sta-cap-list"}, {"description": "WTP, radio, VAP, and STA statistics", "help": "WTP, radio, VAP, and STA statistics.", "label": "Stats", "name": "stats"}, {"description": "AeroScout Mobile Unit (MU) report", "help": "AeroScout Mobile Unit (MU) report.", "label": "Aeroscout Mu", "name": "aeroscout-mu"}, {"description": "STA health log", "help": "STA health log.", "label": "Sta Health", "name": "sta-health"}, {"description": "Spectral analysis report", "help": "Spectral analysis report.", "label": "Spectral Analysis", "name": "spectral-analysis"}] | None = ...,
        data_ethernet_II: Literal[{"description": "Use Ethernet II frames with 802", "help": "Use Ethernet II frames with 802.3 data tunnel mode.", "label": "Enable", "name": "enable"}, {"description": "Use 802", "help": "Use 802.3 Ethernet frames with 802.3 data tunnel mode.", "label": "Disable", "name": "disable"}] | None = ...,
        link_aggregation: Literal[{"description": "Enable calculating the CAPWAP transmit hash", "help": "Enable calculating the CAPWAP transmit hash.", "label": "Enable", "name": "enable"}, {"description": "Disable calculating the CAPWAP transmit hash", "help": "Disable calculating the CAPWAP transmit hash.", "label": "Disable", "name": "disable"}] | None = ...,
        mesh_eth_type: int | None = ...,
        fiapp_eth_type: int | None = ...,
        discovery_mc_addr: str | None = ...,
        discovery_mc_addr6: str | None = ...,
        max_clients: int | None = ...,
        rogue_scan_mac_adjacency: int | None = ...,
        ipsec_base_ip: str | None = ...,
        wtp_share: Literal[{"description": "WTP can be shared between all VDOMs", "help": "WTP can be shared between all VDOMs.", "label": "Enable", "name": "enable"}, {"description": "WTP can be used only in its own VDOM", "help": "WTP can be used only in its own VDOM.", "label": "Disable", "name": "disable"}] | None = ...,
        tunnel_mode: Literal[{"description": "Allow for backward compatible ciphers(3DES+SHA1+Strong list)", "help": "Allow for backward compatible ciphers(3DES+SHA1+Strong list).", "label": "Compatible", "name": "compatible"}, {"description": "Follow system level strong-crypto ciphers", "help": "Follow system level strong-crypto ciphers.", "label": "Strict", "name": "strict"}] | None = ...,
        nac_interval: int | None = ...,
        ap_log_server: Literal[{"description": "Enable AP log server", "help": "Enable AP log server.", "label": "Enable", "name": "enable"}, {"description": "Disable AP log server", "help": "Disable AP log server.", "label": "Disable", "name": "disable"}] | None = ...,
        ap_log_server_ip: str | None = ...,
        ap_log_server_port: int | None = ...,
        max_sta_offline: int | None = ...,
        max_sta_offline_ip2mac: int | None = ...,
        max_sta_cap: int | None = ...,
        max_sta_cap_wtp: int | None = ...,
        max_rogue_ap: int | None = ...,
        max_rogue_ap_wtp: int | None = ...,
        max_rogue_sta: int | None = ...,
        max_wids_entry: int | None = ...,
        max_ble_device: int | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def delete(
        self,
        name: str | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def exists(
        self,
        name: str,
        vdom: str | bool | None = ...,
    ) -> Union[bool, Coroutine[Any, Any, bool]]: ...
    
    def set(
        self,
        payload_dict: GlobalPayload | None = ...,
        vdom: str | bool | None = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    # Helper methods
    @staticmethod
    def help(field_name: str | None = ...) -> str: ...
    
    @staticmethod
    def fields(detailed: bool = ...) -> Union[list[str], list[dict[str, Any]]]: ...
    
    @staticmethod
    def field_info(field_name: str) -> dict[str, Any]: ...
    
    @staticmethod
    def validate_field(name: str, value: Any) -> bool: ...
    
    @staticmethod
    def required_fields() -> list[str]: ...
    
    @staticmethod
    def defaults() -> dict[str, Any]: ...
    
    @staticmethod
    def schema() -> dict[str, Any]: ...


__all__ = [
    "Global",
    "GlobalPayload",
]