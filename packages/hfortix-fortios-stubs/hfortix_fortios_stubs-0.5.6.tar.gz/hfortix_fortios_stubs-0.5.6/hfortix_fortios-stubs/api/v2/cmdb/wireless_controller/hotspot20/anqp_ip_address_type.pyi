from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class AnqpIpAddressTypePayload(TypedDict, total=False):
    """
    Type hints for wireless_controller/hotspot20/anqp_ip_address_type payload fields.
    
    Configure IP address type availability.
    
    **Usage:**
        payload: AnqpIpAddressTypePayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    name: NotRequired[str]  # IP type name.
    ipv6_address_type: NotRequired[Literal[{"description": "Address type not available", "help": "Address type not available.", "label": "Not Available", "name": "not-available"}, {"description": "Address type available", "help": "Address type available.", "label": "Available", "name": "available"}, {"description": "Availability of the address type not known", "help": "Availability of the address type not known.", "label": "Not Known", "name": "not-known"}]]  # IPv6 address type.
    ipv4_address_type: NotRequired[Literal[{"description": "Address type not available", "help": "Address type not available.", "label": "Not Available", "name": "not-available"}, {"description": "Public IPv4 address available", "help": "Public IPv4 address available.", "label": "Public", "name": "public"}, {"description": "Port-restricted IPv4 address available", "help": "Port-restricted IPv4 address available.", "label": "Port Restricted", "name": "port-restricted"}, {"description": "Single NATed private IPv4 address available", "help": "Single NATed private IPv4 address available.", "label": "Single Nated Private", "name": "single-NATed-private"}, {"description": "Double NATed private IPv4 address available", "help": "Double NATed private IPv4 address available.", "label": "Double Nated Private", "name": "double-NATed-private"}, {"description": "Port-restricted IPv4 address and single NATed IPv4 address available", "help": "Port-restricted IPv4 address and single NATed IPv4 address available.", "label": "Port Restricted And Single Nated", "name": "port-restricted-and-single-NATed"}, {"description": "Port-restricted IPv4 address and double NATed IPv4 address available", "help": "Port-restricted IPv4 address and double NATed IPv4 address available.", "label": "Port Restricted And Double Nated", "name": "port-restricted-and-double-NATed"}, {"description": "Availability of the address type is not known", "help": "Availability of the address type is not known.", "label": "Not Known", "name": "not-known"}]]  # IPv4 address type.


class AnqpIpAddressType:
    """
    Configure IP address type availability.
    
    Path: wireless_controller/hotspot20/anqp_ip_address_type
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
        payload_dict: AnqpIpAddressTypePayload | None = ...,
        name: str | None = ...,
        ipv6_address_type: Literal[{"description": "Address type not available", "help": "Address type not available.", "label": "Not Available", "name": "not-available"}, {"description": "Address type available", "help": "Address type available.", "label": "Available", "name": "available"}, {"description": "Availability of the address type not known", "help": "Availability of the address type not known.", "label": "Not Known", "name": "not-known"}] | None = ...,
        ipv4_address_type: Literal[{"description": "Address type not available", "help": "Address type not available.", "label": "Not Available", "name": "not-available"}, {"description": "Public IPv4 address available", "help": "Public IPv4 address available.", "label": "Public", "name": "public"}, {"description": "Port-restricted IPv4 address available", "help": "Port-restricted IPv4 address available.", "label": "Port Restricted", "name": "port-restricted"}, {"description": "Single NATed private IPv4 address available", "help": "Single NATed private IPv4 address available.", "label": "Single Nated Private", "name": "single-NATed-private"}, {"description": "Double NATed private IPv4 address available", "help": "Double NATed private IPv4 address available.", "label": "Double Nated Private", "name": "double-NATed-private"}, {"description": "Port-restricted IPv4 address and single NATed IPv4 address available", "help": "Port-restricted IPv4 address and single NATed IPv4 address available.", "label": "Port Restricted And Single Nated", "name": "port-restricted-and-single-NATed"}, {"description": "Port-restricted IPv4 address and double NATed IPv4 address available", "help": "Port-restricted IPv4 address and double NATed IPv4 address available.", "label": "Port Restricted And Double Nated", "name": "port-restricted-and-double-NATed"}, {"description": "Availability of the address type is not known", "help": "Availability of the address type is not known.", "label": "Not Known", "name": "not-known"}] | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: AnqpIpAddressTypePayload | None = ...,
        name: str | None = ...,
        ipv6_address_type: Literal[{"description": "Address type not available", "help": "Address type not available.", "label": "Not Available", "name": "not-available"}, {"description": "Address type available", "help": "Address type available.", "label": "Available", "name": "available"}, {"description": "Availability of the address type not known", "help": "Availability of the address type not known.", "label": "Not Known", "name": "not-known"}] | None = ...,
        ipv4_address_type: Literal[{"description": "Address type not available", "help": "Address type not available.", "label": "Not Available", "name": "not-available"}, {"description": "Public IPv4 address available", "help": "Public IPv4 address available.", "label": "Public", "name": "public"}, {"description": "Port-restricted IPv4 address available", "help": "Port-restricted IPv4 address available.", "label": "Port Restricted", "name": "port-restricted"}, {"description": "Single NATed private IPv4 address available", "help": "Single NATed private IPv4 address available.", "label": "Single Nated Private", "name": "single-NATed-private"}, {"description": "Double NATed private IPv4 address available", "help": "Double NATed private IPv4 address available.", "label": "Double Nated Private", "name": "double-NATed-private"}, {"description": "Port-restricted IPv4 address and single NATed IPv4 address available", "help": "Port-restricted IPv4 address and single NATed IPv4 address available.", "label": "Port Restricted And Single Nated", "name": "port-restricted-and-single-NATed"}, {"description": "Port-restricted IPv4 address and double NATed IPv4 address available", "help": "Port-restricted IPv4 address and double NATed IPv4 address available.", "label": "Port Restricted And Double Nated", "name": "port-restricted-and-double-NATed"}, {"description": "Availability of the address type is not known", "help": "Availability of the address type is not known.", "label": "Not Known", "name": "not-known"}] | None = ...,
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
        payload_dict: AnqpIpAddressTypePayload | None = ...,
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
    "AnqpIpAddressType",
    "AnqpIpAddressTypePayload",
]