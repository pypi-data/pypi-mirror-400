from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class TimersPayload(TypedDict, total=False):
    """
    Type hints for wireless_controller/timers payload fields.
    
    Configure CAPWAP timers.
    
    **Usage:**
        payload: TimersPayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    echo_interval: NotRequired[int]  # Time between echo requests sent by the managed WTP, AP, or F
    nat_session_keep_alive: NotRequired[int]  # Maximal time in seconds between control requests sent by the
    discovery_interval: NotRequired[int]  # Time between discovery requests (2 - 180 sec, default = 5).
    client_idle_timeout: NotRequired[int]  # Time after which a client is considered idle and times out (
    client_idle_rehome_timeout: NotRequired[int]  # Time after which a client is considered idle and disconnecte
    auth_timeout: NotRequired[int]  # Time after which a client is considered failed in RADIUS aut
    rogue_ap_log: NotRequired[int]  # Time between logging rogue AP messages if periodic rogue AP 
    fake_ap_log: NotRequired[int]  # Time between recording logs about fake APs if periodic fake 
    sta_offline_cleanup: NotRequired[int]  # Time period in seconds to keep station offline data after it
    sta_offline_ip2mac_cleanup: NotRequired[int]  # Time period in seconds to keep station offline Ip2mac data a
    sta_cap_cleanup: NotRequired[int]  # Time period in minutes to keep station capability data after
    rogue_ap_cleanup: NotRequired[int]  # Time period in minutes to keep rogue AP after it is gone (de
    rogue_sta_cleanup: NotRequired[int]  # Time period in minutes to keep rogue station after it is gon
    wids_entry_cleanup: NotRequired[int]  # Time period in minutes to keep wids entry after it is gone (
    ble_device_cleanup: NotRequired[int]  # Time period in minutes to keep BLE device after it is gone (
    sta_stats_interval: NotRequired[int]  # Time between running client (station) reports (1 - 255 sec, 
    vap_stats_interval: NotRequired[int]  # Time between running Virtual Access Point (VAP) reports (1 -
    radio_stats_interval: NotRequired[int]  # Time between running radio reports (1 - 255 sec, default = 1
    sta_capability_interval: NotRequired[int]  # Time between running station capability reports (1 - 255 sec
    sta_locate_timer: NotRequired[int]  # Time between running client presence flushes to remove clien
    ipsec_intf_cleanup: NotRequired[int]  # Time period to keep IPsec VPN interfaces up after WTP sessio
    ble_scan_report_intv: NotRequired[int]  # Time between running Bluetooth Low Energy (BLE) reports (10 
    drma_interval: NotRequired[int]  # Dynamic radio mode assignment (DRMA) schedule interval in mi
    ap_reboot_wait_interval1: NotRequired[int]  # Time in minutes to wait before AP reboots when there is no c
    ap_reboot_wait_time: NotRequired[str]  # Time to reboot the AP when there is no controller detected a
    ap_reboot_wait_interval2: NotRequired[int]  # Time in minutes to wait before AP reboots when there is no c


class Timers:
    """
    Configure CAPWAP timers.
    
    Path: wireless_controller/timers
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
        payload_dict: TimersPayload | None = ...,
        echo_interval: int | None = ...,
        nat_session_keep_alive: int | None = ...,
        discovery_interval: int | None = ...,
        client_idle_timeout: int | None = ...,
        client_idle_rehome_timeout: int | None = ...,
        auth_timeout: int | None = ...,
        rogue_ap_log: int | None = ...,
        fake_ap_log: int | None = ...,
        sta_offline_cleanup: int | None = ...,
        sta_offline_ip2mac_cleanup: int | None = ...,
        sta_cap_cleanup: int | None = ...,
        rogue_ap_cleanup: int | None = ...,
        rogue_sta_cleanup: int | None = ...,
        wids_entry_cleanup: int | None = ...,
        ble_device_cleanup: int | None = ...,
        sta_stats_interval: int | None = ...,
        vap_stats_interval: int | None = ...,
        radio_stats_interval: int | None = ...,
        sta_capability_interval: int | None = ...,
        sta_locate_timer: int | None = ...,
        ipsec_intf_cleanup: int | None = ...,
        ble_scan_report_intv: int | None = ...,
        drma_interval: int | None = ...,
        ap_reboot_wait_interval1: int | None = ...,
        ap_reboot_wait_time: str | None = ...,
        ap_reboot_wait_interval2: int | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: TimersPayload | None = ...,
        echo_interval: int | None = ...,
        nat_session_keep_alive: int | None = ...,
        discovery_interval: int | None = ...,
        client_idle_timeout: int | None = ...,
        client_idle_rehome_timeout: int | None = ...,
        auth_timeout: int | None = ...,
        rogue_ap_log: int | None = ...,
        fake_ap_log: int | None = ...,
        sta_offline_cleanup: int | None = ...,
        sta_offline_ip2mac_cleanup: int | None = ...,
        sta_cap_cleanup: int | None = ...,
        rogue_ap_cleanup: int | None = ...,
        rogue_sta_cleanup: int | None = ...,
        wids_entry_cleanup: int | None = ...,
        ble_device_cleanup: int | None = ...,
        sta_stats_interval: int | None = ...,
        vap_stats_interval: int | None = ...,
        radio_stats_interval: int | None = ...,
        sta_capability_interval: int | None = ...,
        sta_locate_timer: int | None = ...,
        ipsec_intf_cleanup: int | None = ...,
        ble_scan_report_intv: int | None = ...,
        drma_interval: int | None = ...,
        ap_reboot_wait_interval1: int | None = ...,
        ap_reboot_wait_time: str | None = ...,
        ap_reboot_wait_interval2: int | None = ...,
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
        payload_dict: TimersPayload | None = ...,
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
    "Timers",
    "TimersPayload",
]