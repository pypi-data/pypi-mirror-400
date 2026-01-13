from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class MulticastAddressPayload(TypedDict, total=False):
    """
    Type hints for firewall/multicast_address payload fields.
    
    Configure multicast addresses.
    
    **Related Resources:**

    Dependencies (resources this endpoint references):
        - :class:`~.system.interface.InterfaceEndpoint` (via: associated-interface)

    **Usage:**
        payload: MulticastAddressPayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    name: NotRequired[str]  # Multicast address name.
    type: NotRequired[Literal[{"description": "Multicast range", "help": "Multicast range.", "label": "Multicastrange", "name": "multicastrange"}, {"description": "Broadcast IP/mask", "help": "Broadcast IP/mask.", "label": "Broadcastmask", "name": "broadcastmask"}]]  # Type of address object: multicast IP address range or broadc
    subnet: NotRequired[str]  # Broadcast address and subnet.
    start_ip: str  # First IPv4 address (inclusive) in the range for the address.
    end_ip: str  # Final IPv4 address (inclusive) in the range for the address.
    comment: NotRequired[str]  # Comment.
    associated_interface: NotRequired[str]  # Interface associated with the address object. When setting u
    color: NotRequired[int]  # Integer value to determine the color of the icon in the GUI 
    tagging: NotRequired[list[dict[str, Any]]]  # Config object tagging.


class MulticastAddress:
    """
    Configure multicast addresses.
    
    Path: firewall/multicast_address
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
        payload_dict: MulticastAddressPayload | None = ...,
        name: str | None = ...,
        type: Literal[{"description": "Multicast range", "help": "Multicast range.", "label": "Multicastrange", "name": "multicastrange"}, {"description": "Broadcast IP/mask", "help": "Broadcast IP/mask.", "label": "Broadcastmask", "name": "broadcastmask"}] | None = ...,
        subnet: str | None = ...,
        start_ip: str | None = ...,
        end_ip: str | None = ...,
        comment: str | None = ...,
        associated_interface: str | None = ...,
        color: int | None = ...,
        tagging: list[dict[str, Any]] | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: MulticastAddressPayload | None = ...,
        name: str | None = ...,
        type: Literal[{"description": "Multicast range", "help": "Multicast range.", "label": "Multicastrange", "name": "multicastrange"}, {"description": "Broadcast IP/mask", "help": "Broadcast IP/mask.", "label": "Broadcastmask", "name": "broadcastmask"}] | None = ...,
        subnet: str | None = ...,
        start_ip: str | None = ...,
        end_ip: str | None = ...,
        comment: str | None = ...,
        associated_interface: str | None = ...,
        color: int | None = ...,
        tagging: list[dict[str, Any]] | None = ...,
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
        payload_dict: MulticastAddressPayload | None = ...,
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
    "MulticastAddress",
    "MulticastAddressPayload",
]