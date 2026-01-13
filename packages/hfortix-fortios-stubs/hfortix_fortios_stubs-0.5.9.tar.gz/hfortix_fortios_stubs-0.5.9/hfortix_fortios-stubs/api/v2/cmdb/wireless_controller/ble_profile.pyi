from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class BleProfilePayload(TypedDict, total=False):
    """
    Type hints for wireless_controller/ble_profile payload fields.
    
    Configure Bluetooth Low Energy profile.
    
    **Usage:**
        payload: BleProfilePayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    name: NotRequired[str]  # Bluetooth Low Energy profile name.
    comment: NotRequired[str]  # Comment.
    advertising: NotRequired[Literal[{"description": "iBeacon advertising", "help": "iBeacon advertising.", "label": "Ibeacon", "name": "ibeacon"}, {"description": "Eddystone UID advertising", "help": "Eddystone UID advertising.", "label": "Eddystone Uid", "name": "eddystone-uid"}, {"description": "Eddystone URL advertising", "help": "Eddystone URL advertising.", "label": "Eddystone Url", "name": "eddystone-url"}]]  # Advertising type.
    ibeacon_uuid: NotRequired[str]  # Universally Unique Identifier (UUID; automatically assigned 
    major_id: NotRequired[int]  # Major ID.
    minor_id: NotRequired[int]  # Minor ID.
    eddystone_namespace: NotRequired[str]  # Eddystone namespace ID.
    eddystone_instance: NotRequired[str]  # Eddystone instance ID.
    eddystone_url: NotRequired[str]  # Eddystone URL.
    txpower: NotRequired[Literal[{"description": "Transmit power level 0 (-21 dBm)    1:Transmit power level 1 (-18 dBm)    2:Transmit power level 2 (-15 dBm)    3:Transmit power level 3 (-12 dBm)    4:Transmit power level 4 (-9 dBm)    5:Transmit power level 5 (-6 dBm)    6:Transmit power level 6 (-3 dBm)    7:Transmit power level 7 (0 dBm)    8:Transmit power level 8 (1 dBm)    9:Transmit power level 9 (2 dBm)    10:Transmit power level 10 (3 dBm)    11:Transmit power level 11 (4 dBm)    12:Transmit power level 12 (5 dBm)    13:Transmit power level 13 (8 dBm)    14:Transmit power level 14 (11 dBm)    15:Transmit power level 15 (14 dBm)    16:Transmit power level 16 (17 dBm)    17:Transmit power level 17 (20 dBm)", "help": "Transmit power level 0 (-21 dBm)", "label": "0", "name": "0"}, {"help": "Transmit power level 1 (-18 dBm)", "label": "1", "name": "1"}, {"help": "Transmit power level 2 (-15 dBm)", "label": "2", "name": "2"}, {"help": "Transmit power level 3 (-12 dBm)", "label": "3", "name": "3"}, {"help": "Transmit power level 4 (-9 dBm)", "label": "4", "name": "4"}, {"help": "Transmit power level 5 (-6 dBm)", "label": "5", "name": "5"}, {"help": "Transmit power level 6 (-3 dBm)", "label": "6", "name": "6"}, {"help": "Transmit power level 7 (0 dBm)", "label": "7", "name": "7"}, {"help": "Transmit power level 8 (1 dBm)", "label": "8", "name": "8"}, {"help": "Transmit power level 9 (2 dBm)", "label": "9", "name": "9"}, {"help": "Transmit power level 10 (3 dBm)", "label": "10", "name": "10"}, {"help": "Transmit power level 11 (4 dBm)", "label": "11", "name": "11"}, {"help": "Transmit power level 12 (5 dBm)", "label": "12", "name": "12"}, {"help": "Transmit power level 13 (8 dBm)", "label": "13", "name": "13"}, {"help": "Transmit power level 14 (11 dBm)", "label": "14", "name": "14"}, {"help": "Transmit power level 15 (14 dBm)", "label": "15", "name": "15"}, {"help": "Transmit power level 16 (17 dBm)", "label": "16", "name": "16"}, {"help": "Transmit power level 17 (20 dBm)", "label": "17", "name": "17"}]]  # Transmit power level (default = 0).
    beacon_interval: NotRequired[int]  # Beacon interval (default = 100 msec).
    ble_scanning: NotRequired[Literal[{"description": "Enable BLE scanning", "help": "Enable BLE scanning.", "label": "Enable", "name": "enable"}, {"description": "Disable BLE scanning", "help": "Disable BLE scanning.", "label": "Disable", "name": "disable"}]]  # Enable/disable Bluetooth Low Energy (BLE) scanning.
    scan_type: NotRequired[Literal[{"description": "Active BLE scanning", "help": "Active BLE scanning.", "label": "Active", "name": "active"}, {"description": "Passive BLE scanning", "help": "Passive BLE scanning.", "label": "Passive", "name": "passive"}]]  # Scan Type (default = active).
    scan_threshold: NotRequired[str]  # Minimum signal level/threshold in dBm required for the AP to
    scan_period: NotRequired[int]  # Scan Period (default = 4000 msec).
    scan_time: NotRequired[int]  # Scan Time (default = 1000 msec).
    scan_interval: NotRequired[int]  # Scan Interval (default = 50 msec).
    scan_window: NotRequired[int]  # Scan Windows (default = 50 msec).


class BleProfile:
    """
    Configure Bluetooth Low Energy profile.
    
    Path: wireless_controller/ble_profile
    Category: cmdb
    Primary Key: name
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
        payload_dict: BleProfilePayload | None = ...,
        name: str | None = ...,
        comment: str | None = ...,
        advertising: Literal[{"description": "iBeacon advertising", "help": "iBeacon advertising.", "label": "Ibeacon", "name": "ibeacon"}, {"description": "Eddystone UID advertising", "help": "Eddystone UID advertising.", "label": "Eddystone Uid", "name": "eddystone-uid"}, {"description": "Eddystone URL advertising", "help": "Eddystone URL advertising.", "label": "Eddystone Url", "name": "eddystone-url"}] | None = ...,
        ibeacon_uuid: str | None = ...,
        major_id: int | None = ...,
        minor_id: int | None = ...,
        eddystone_namespace: str | None = ...,
        eddystone_instance: str | None = ...,
        eddystone_url: str | None = ...,
        txpower: Literal[{"description": "Transmit power level 0 (-21 dBm)    1:Transmit power level 1 (-18 dBm)    2:Transmit power level 2 (-15 dBm)    3:Transmit power level 3 (-12 dBm)    4:Transmit power level 4 (-9 dBm)    5:Transmit power level 5 (-6 dBm)    6:Transmit power level 6 (-3 dBm)    7:Transmit power level 7 (0 dBm)    8:Transmit power level 8 (1 dBm)    9:Transmit power level 9 (2 dBm)    10:Transmit power level 10 (3 dBm)    11:Transmit power level 11 (4 dBm)    12:Transmit power level 12 (5 dBm)    13:Transmit power level 13 (8 dBm)    14:Transmit power level 14 (11 dBm)    15:Transmit power level 15 (14 dBm)    16:Transmit power level 16 (17 dBm)    17:Transmit power level 17 (20 dBm)", "help": "Transmit power level 0 (-21 dBm)", "label": "0", "name": "0"}, {"help": "Transmit power level 1 (-18 dBm)", "label": "1", "name": "1"}, {"help": "Transmit power level 2 (-15 dBm)", "label": "2", "name": "2"}, {"help": "Transmit power level 3 (-12 dBm)", "label": "3", "name": "3"}, {"help": "Transmit power level 4 (-9 dBm)", "label": "4", "name": "4"}, {"help": "Transmit power level 5 (-6 dBm)", "label": "5", "name": "5"}, {"help": "Transmit power level 6 (-3 dBm)", "label": "6", "name": "6"}, {"help": "Transmit power level 7 (0 dBm)", "label": "7", "name": "7"}, {"help": "Transmit power level 8 (1 dBm)", "label": "8", "name": "8"}, {"help": "Transmit power level 9 (2 dBm)", "label": "9", "name": "9"}, {"help": "Transmit power level 10 (3 dBm)", "label": "10", "name": "10"}, {"help": "Transmit power level 11 (4 dBm)", "label": "11", "name": "11"}, {"help": "Transmit power level 12 (5 dBm)", "label": "12", "name": "12"}, {"help": "Transmit power level 13 (8 dBm)", "label": "13", "name": "13"}, {"help": "Transmit power level 14 (11 dBm)", "label": "14", "name": "14"}, {"help": "Transmit power level 15 (14 dBm)", "label": "15", "name": "15"}, {"help": "Transmit power level 16 (17 dBm)", "label": "16", "name": "16"}, {"help": "Transmit power level 17 (20 dBm)", "label": "17", "name": "17"}] | None = ...,
        beacon_interval: int | None = ...,
        ble_scanning: Literal[{"description": "Enable BLE scanning", "help": "Enable BLE scanning.", "label": "Enable", "name": "enable"}, {"description": "Disable BLE scanning", "help": "Disable BLE scanning.", "label": "Disable", "name": "disable"}] | None = ...,
        scan_type: Literal[{"description": "Active BLE scanning", "help": "Active BLE scanning.", "label": "Active", "name": "active"}, {"description": "Passive BLE scanning", "help": "Passive BLE scanning.", "label": "Passive", "name": "passive"}] | None = ...,
        scan_threshold: str | None = ...,
        scan_period: int | None = ...,
        scan_time: int | None = ...,
        scan_interval: int | None = ...,
        scan_window: int | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: BleProfilePayload | None = ...,
        name: str | None = ...,
        comment: str | None = ...,
        advertising: Literal[{"description": "iBeacon advertising", "help": "iBeacon advertising.", "label": "Ibeacon", "name": "ibeacon"}, {"description": "Eddystone UID advertising", "help": "Eddystone UID advertising.", "label": "Eddystone Uid", "name": "eddystone-uid"}, {"description": "Eddystone URL advertising", "help": "Eddystone URL advertising.", "label": "Eddystone Url", "name": "eddystone-url"}] | None = ...,
        ibeacon_uuid: str | None = ...,
        major_id: int | None = ...,
        minor_id: int | None = ...,
        eddystone_namespace: str | None = ...,
        eddystone_instance: str | None = ...,
        eddystone_url: str | None = ...,
        txpower: Literal[{"description": "Transmit power level 0 (-21 dBm)    1:Transmit power level 1 (-18 dBm)    2:Transmit power level 2 (-15 dBm)    3:Transmit power level 3 (-12 dBm)    4:Transmit power level 4 (-9 dBm)    5:Transmit power level 5 (-6 dBm)    6:Transmit power level 6 (-3 dBm)    7:Transmit power level 7 (0 dBm)    8:Transmit power level 8 (1 dBm)    9:Transmit power level 9 (2 dBm)    10:Transmit power level 10 (3 dBm)    11:Transmit power level 11 (4 dBm)    12:Transmit power level 12 (5 dBm)    13:Transmit power level 13 (8 dBm)    14:Transmit power level 14 (11 dBm)    15:Transmit power level 15 (14 dBm)    16:Transmit power level 16 (17 dBm)    17:Transmit power level 17 (20 dBm)", "help": "Transmit power level 0 (-21 dBm)", "label": "0", "name": "0"}, {"help": "Transmit power level 1 (-18 dBm)", "label": "1", "name": "1"}, {"help": "Transmit power level 2 (-15 dBm)", "label": "2", "name": "2"}, {"help": "Transmit power level 3 (-12 dBm)", "label": "3", "name": "3"}, {"help": "Transmit power level 4 (-9 dBm)", "label": "4", "name": "4"}, {"help": "Transmit power level 5 (-6 dBm)", "label": "5", "name": "5"}, {"help": "Transmit power level 6 (-3 dBm)", "label": "6", "name": "6"}, {"help": "Transmit power level 7 (0 dBm)", "label": "7", "name": "7"}, {"help": "Transmit power level 8 (1 dBm)", "label": "8", "name": "8"}, {"help": "Transmit power level 9 (2 dBm)", "label": "9", "name": "9"}, {"help": "Transmit power level 10 (3 dBm)", "label": "10", "name": "10"}, {"help": "Transmit power level 11 (4 dBm)", "label": "11", "name": "11"}, {"help": "Transmit power level 12 (5 dBm)", "label": "12", "name": "12"}, {"help": "Transmit power level 13 (8 dBm)", "label": "13", "name": "13"}, {"help": "Transmit power level 14 (11 dBm)", "label": "14", "name": "14"}, {"help": "Transmit power level 15 (14 dBm)", "label": "15", "name": "15"}, {"help": "Transmit power level 16 (17 dBm)", "label": "16", "name": "16"}, {"help": "Transmit power level 17 (20 dBm)", "label": "17", "name": "17"}] | None = ...,
        beacon_interval: int | None = ...,
        ble_scanning: Literal[{"description": "Enable BLE scanning", "help": "Enable BLE scanning.", "label": "Enable", "name": "enable"}, {"description": "Disable BLE scanning", "help": "Disable BLE scanning.", "label": "Disable", "name": "disable"}] | None = ...,
        scan_type: Literal[{"description": "Active BLE scanning", "help": "Active BLE scanning.", "label": "Active", "name": "active"}, {"description": "Passive BLE scanning", "help": "Passive BLE scanning.", "label": "Passive", "name": "passive"}] | None = ...,
        scan_threshold: str | None = ...,
        scan_period: int | None = ...,
        scan_time: int | None = ...,
        scan_interval: int | None = ...,
        scan_window: int | None = ...,
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
        payload_dict: BleProfilePayload | None = ...,
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
    "BleProfile",
    "BleProfilePayload",
]