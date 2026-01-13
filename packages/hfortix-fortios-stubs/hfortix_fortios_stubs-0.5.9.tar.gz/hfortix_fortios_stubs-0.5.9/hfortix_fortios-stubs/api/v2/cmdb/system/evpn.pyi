from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class EvpnPayload(TypedDict, total=False):
    """
    Type hints for system/evpn payload fields.
    
    Configure EVPN instance.
    
    **Usage:**
        payload: EvpnPayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    id: NotRequired[int]  # ID.
    rd: NotRequired[str]  # Route Distinguisher: AA:NN|A.B.C.D:NN.
    import_rt: NotRequired[list[dict[str, Any]]]  # List of import route targets.
    export_rt: NotRequired[list[dict[str, Any]]]  # List of export route targets.
    ip_local_learning: NotRequired[Literal[{"description": "Enable IP address local learning", "help": "Enable IP address local learning.", "label": "Enable", "name": "enable"}, {"description": "Disable IP address local learning", "help": "Disable IP address local learning.", "label": "Disable", "name": "disable"}]]  # Enable/disable IP address local learning.
    arp_suppression: NotRequired[Literal[{"description": "Enable ARP suppression", "help": "Enable ARP suppression.", "label": "Enable", "name": "enable"}, {"description": "Disable ARP suppression", "help": "Disable ARP suppression.", "label": "Disable", "name": "disable"}]]  # Enable/disable ARP suppression.


class Evpn:
    """
    Configure EVPN instance.
    
    Path: system/evpn
    Category: cmdb
    Primary Key: id
    """
    
    # Overloads for get() with response_mode="object"
    @overload
    def get(
        self,
        id: int | None = ...,
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
        id: int,
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
        id: int | None = ...,
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
        id: int | None = ...,
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
        id: int | None = ...,
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
        payload_dict: EvpnPayload | None = ...,
        id: int | None = ...,
        rd: str | None = ...,
        import_rt: list[dict[str, Any]] | None = ...,
        export_rt: list[dict[str, Any]] | None = ...,
        ip_local_learning: Literal[{"description": "Enable IP address local learning", "help": "Enable IP address local learning.", "label": "Enable", "name": "enable"}, {"description": "Disable IP address local learning", "help": "Disable IP address local learning.", "label": "Disable", "name": "disable"}] | None = ...,
        arp_suppression: Literal[{"description": "Enable ARP suppression", "help": "Enable ARP suppression.", "label": "Enable", "name": "enable"}, {"description": "Disable ARP suppression", "help": "Disable ARP suppression.", "label": "Disable", "name": "disable"}] | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: EvpnPayload | None = ...,
        id: int | None = ...,
        rd: str | None = ...,
        import_rt: list[dict[str, Any]] | None = ...,
        export_rt: list[dict[str, Any]] | None = ...,
        ip_local_learning: Literal[{"description": "Enable IP address local learning", "help": "Enable IP address local learning.", "label": "Enable", "name": "enable"}, {"description": "Disable IP address local learning", "help": "Disable IP address local learning.", "label": "Disable", "name": "disable"}] | None = ...,
        arp_suppression: Literal[{"description": "Enable ARP suppression", "help": "Enable ARP suppression.", "label": "Enable", "name": "enable"}, {"description": "Disable ARP suppression", "help": "Disable ARP suppression.", "label": "Disable", "name": "disable"}] | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def delete(
        self,
        id: int | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def exists(
        self,
        id: int,
        vdom: str | bool | None = ...,
    ) -> Union[bool, Coroutine[Any, Any, bool]]: ...
    
    def set(
        self,
        payload_dict: EvpnPayload | None = ...,
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
    "Evpn",
    "EvpnPayload",
]