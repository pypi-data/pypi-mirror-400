from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class ProfilePayload(TypedDict, total=False):
    """
    Type hints for switch_controller/ptp/profile payload fields.
    
    Global PTP profile.
    
    **Usage:**
        payload: ProfilePayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    name: str  # Profile name.
    description: NotRequired[str]  # Description.
    mode: NotRequired[Literal[{"description": "End-to-end transparent clock", "help": "End-to-end transparent clock.", "label": "Transparent E2E", "name": "transparent-e2e"}, {"description": "Peer-to-peer transparent clock", "help": "Peer-to-peer transparent clock.", "label": "Transparent P2P", "name": "transparent-p2p"}]]  # Select PTP mode.
    ptp_profile: NotRequired[Literal[{"help": "C37.238-2017 power profile.", "label": "C37.238 2017", "name": "C37.238-2017"}]]  # Configure PTP power profile.
    transport: NotRequired[Literal[{"description": "L2 multicast", "help": "L2 multicast.", "label": "L2 Mcast", "name": "l2-mcast"}]]  # Configure PTP transport mode.
    domain: NotRequired[int]  # Configure PTP domain value (0 - 255, default = 254).
    pdelay_req_interval: NotRequired[Literal[{"description": "1 sec", "help": "1 sec.", "label": "1Sec", "name": "1sec"}, {"description": "2 sec", "help": "2 sec.", "label": "2Sec", "name": "2sec"}, {"description": "4 sec", "help": "4 sec.", "label": "4Sec", "name": "4sec"}, {"description": "8 sec", "help": "8 sec.", "label": "8Sec", "name": "8sec"}, {"description": "16 sec", "help": "16 sec.", "label": "16Sec", "name": "16sec"}, {"description": "32 sec", "help": "32 sec.", "label": "32Sec", "name": "32sec"}]]  # Configure PTP peer delay request interval.


class Profile:
    """
    Global PTP profile.
    
    Path: switch_controller/ptp/profile
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
        payload_dict: ProfilePayload | None = ...,
        name: str | None = ...,
        description: str | None = ...,
        mode: Literal[{"description": "End-to-end transparent clock", "help": "End-to-end transparent clock.", "label": "Transparent E2E", "name": "transparent-e2e"}, {"description": "Peer-to-peer transparent clock", "help": "Peer-to-peer transparent clock.", "label": "Transparent P2P", "name": "transparent-p2p"}] | None = ...,
        ptp_profile: Literal[{"help": "C37.238-2017 power profile.", "label": "C37.238 2017", "name": "C37.238-2017"}] | None = ...,
        transport: Literal[{"description": "L2 multicast", "help": "L2 multicast.", "label": "L2 Mcast", "name": "l2-mcast"}] | None = ...,
        domain: int | None = ...,
        pdelay_req_interval: Literal[{"description": "1 sec", "help": "1 sec.", "label": "1Sec", "name": "1sec"}, {"description": "2 sec", "help": "2 sec.", "label": "2Sec", "name": "2sec"}, {"description": "4 sec", "help": "4 sec.", "label": "4Sec", "name": "4sec"}, {"description": "8 sec", "help": "8 sec.", "label": "8Sec", "name": "8sec"}, {"description": "16 sec", "help": "16 sec.", "label": "16Sec", "name": "16sec"}, {"description": "32 sec", "help": "32 sec.", "label": "32Sec", "name": "32sec"}] | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: ProfilePayload | None = ...,
        name: str | None = ...,
        description: str | None = ...,
        mode: Literal[{"description": "End-to-end transparent clock", "help": "End-to-end transparent clock.", "label": "Transparent E2E", "name": "transparent-e2e"}, {"description": "Peer-to-peer transparent clock", "help": "Peer-to-peer transparent clock.", "label": "Transparent P2P", "name": "transparent-p2p"}] | None = ...,
        ptp_profile: Literal[{"help": "C37.238-2017 power profile.", "label": "C37.238 2017", "name": "C37.238-2017"}] | None = ...,
        transport: Literal[{"description": "L2 multicast", "help": "L2 multicast.", "label": "L2 Mcast", "name": "l2-mcast"}] | None = ...,
        domain: int | None = ...,
        pdelay_req_interval: Literal[{"description": "1 sec", "help": "1 sec.", "label": "1Sec", "name": "1sec"}, {"description": "2 sec", "help": "2 sec.", "label": "2Sec", "name": "2sec"}, {"description": "4 sec", "help": "4 sec.", "label": "4Sec", "name": "4sec"}, {"description": "8 sec", "help": "8 sec.", "label": "8Sec", "name": "8sec"}, {"description": "16 sec", "help": "16 sec.", "label": "16Sec", "name": "16sec"}, {"description": "32 sec", "help": "32 sec.", "label": "32Sec", "name": "32sec"}] | None = ...,
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
        payload_dict: ProfilePayload | None = ...,
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
    "Profile",
    "ProfilePayload",
]