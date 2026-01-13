from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class IpamPayload(TypedDict, total=False):
    """
    Type hints for system/ipam payload fields.
    
    Configure IP address management services.
    
    **Usage:**
        payload: IpamPayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    status: NotRequired[Literal[{"description": "Enable integration with IP address management services", "help": "Enable integration with IP address management services.", "label": "Enable", "name": "enable"}, {"description": "Disable integration with IP address management services", "help": "Disable integration with IP address management services.", "label": "Disable", "name": "disable"}]]  # Enable/disable IP address management services.
    server_type: NotRequired[Literal[{"description": "Use the IPAM server running on the Security Fabric root", "help": "Use the IPAM server running on the Security Fabric root.", "label": "Fabric Root", "name": "fabric-root"}]]  # Configure the type of IPAM server to use.
    automatic_conflict_resolution: NotRequired[Literal[{"description": "Disable automatic conflict resolution", "help": "Disable automatic conflict resolution.", "label": "Disable", "name": "disable"}, {"description": "Enable automatic conflict resolution", "help": "Enable automatic conflict resolution.", "label": "Enable", "name": "enable"}]]  # Enable/disable automatic conflict resolution.
    require_subnet_size_match: NotRequired[Literal[{"description": "Disable requiring subnet sizes to match", "help": "Disable requiring subnet sizes to match.", "label": "Disable", "name": "disable"}, {"description": "Enable requiring subnet sizes to match", "help": "Enable requiring subnet sizes to match.", "label": "Enable", "name": "enable"}]]  # Enable/disable reassignment of subnets to make requested and
    manage_lan_addresses: NotRequired[Literal[{"description": "Disable LAN interface address management by default", "help": "Disable LAN interface address management by default.", "label": "Disable", "name": "disable"}, {"description": "Enable LAN interface address management by default", "help": "Enable LAN interface address management by default.", "label": "Enable", "name": "enable"}]]  # Enable/disable default management of LAN interface addresses
    manage_lan_extension_addresses: NotRequired[Literal[{"description": "Disable FortiExtender LAN extension interface address management by default", "help": "Disable FortiExtender LAN extension interface address management by default.", "label": "Disable", "name": "disable"}, {"description": "Enable FortiExtender LAN extension interface address management by default", "help": "Enable FortiExtender LAN extension interface address management by default.", "label": "Enable", "name": "enable"}]]  # Enable/disable default management of FortiExtender LAN exten
    manage_ssid_addresses: NotRequired[Literal[{"description": "Disable FortiAP SSID address management by default", "help": "Disable FortiAP SSID address management by default.", "label": "Disable", "name": "disable"}, {"description": "Enable FortiAP SSID address management by default", "help": "Enable FortiAP SSID address management by default.", "label": "Enable", "name": "enable"}]]  # Enable/disable default management of FortiAP SSID addresses.
    pools: NotRequired[list[dict[str, Any]]]  # Configure IPAM pools.
    rules: NotRequired[list[dict[str, Any]]]  # Configure IPAM allocation rules.


class Ipam:
    """
    Configure IP address management services.
    
    Path: system/ipam
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
        payload_dict: IpamPayload | None = ...,
        status: Literal[{"description": "Enable integration with IP address management services", "help": "Enable integration with IP address management services.", "label": "Enable", "name": "enable"}, {"description": "Disable integration with IP address management services", "help": "Disable integration with IP address management services.", "label": "Disable", "name": "disable"}] | None = ...,
        server_type: Literal[{"description": "Use the IPAM server running on the Security Fabric root", "help": "Use the IPAM server running on the Security Fabric root.", "label": "Fabric Root", "name": "fabric-root"}] | None = ...,
        automatic_conflict_resolution: Literal[{"description": "Disable automatic conflict resolution", "help": "Disable automatic conflict resolution.", "label": "Disable", "name": "disable"}, {"description": "Enable automatic conflict resolution", "help": "Enable automatic conflict resolution.", "label": "Enable", "name": "enable"}] | None = ...,
        require_subnet_size_match: Literal[{"description": "Disable requiring subnet sizes to match", "help": "Disable requiring subnet sizes to match.", "label": "Disable", "name": "disable"}, {"description": "Enable requiring subnet sizes to match", "help": "Enable requiring subnet sizes to match.", "label": "Enable", "name": "enable"}] | None = ...,
        manage_lan_addresses: Literal[{"description": "Disable LAN interface address management by default", "help": "Disable LAN interface address management by default.", "label": "Disable", "name": "disable"}, {"description": "Enable LAN interface address management by default", "help": "Enable LAN interface address management by default.", "label": "Enable", "name": "enable"}] | None = ...,
        manage_lan_extension_addresses: Literal[{"description": "Disable FortiExtender LAN extension interface address management by default", "help": "Disable FortiExtender LAN extension interface address management by default.", "label": "Disable", "name": "disable"}, {"description": "Enable FortiExtender LAN extension interface address management by default", "help": "Enable FortiExtender LAN extension interface address management by default.", "label": "Enable", "name": "enable"}] | None = ...,
        manage_ssid_addresses: Literal[{"description": "Disable FortiAP SSID address management by default", "help": "Disable FortiAP SSID address management by default.", "label": "Disable", "name": "disable"}, {"description": "Enable FortiAP SSID address management by default", "help": "Enable FortiAP SSID address management by default.", "label": "Enable", "name": "enable"}] | None = ...,
        pools: list[dict[str, Any]] | None = ...,
        rules: list[dict[str, Any]] | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: IpamPayload | None = ...,
        status: Literal[{"description": "Enable integration with IP address management services", "help": "Enable integration with IP address management services.", "label": "Enable", "name": "enable"}, {"description": "Disable integration with IP address management services", "help": "Disable integration with IP address management services.", "label": "Disable", "name": "disable"}] | None = ...,
        server_type: Literal[{"description": "Use the IPAM server running on the Security Fabric root", "help": "Use the IPAM server running on the Security Fabric root.", "label": "Fabric Root", "name": "fabric-root"}] | None = ...,
        automatic_conflict_resolution: Literal[{"description": "Disable automatic conflict resolution", "help": "Disable automatic conflict resolution.", "label": "Disable", "name": "disable"}, {"description": "Enable automatic conflict resolution", "help": "Enable automatic conflict resolution.", "label": "Enable", "name": "enable"}] | None = ...,
        require_subnet_size_match: Literal[{"description": "Disable requiring subnet sizes to match", "help": "Disable requiring subnet sizes to match.", "label": "Disable", "name": "disable"}, {"description": "Enable requiring subnet sizes to match", "help": "Enable requiring subnet sizes to match.", "label": "Enable", "name": "enable"}] | None = ...,
        manage_lan_addresses: Literal[{"description": "Disable LAN interface address management by default", "help": "Disable LAN interface address management by default.", "label": "Disable", "name": "disable"}, {"description": "Enable LAN interface address management by default", "help": "Enable LAN interface address management by default.", "label": "Enable", "name": "enable"}] | None = ...,
        manage_lan_extension_addresses: Literal[{"description": "Disable FortiExtender LAN extension interface address management by default", "help": "Disable FortiExtender LAN extension interface address management by default.", "label": "Disable", "name": "disable"}, {"description": "Enable FortiExtender LAN extension interface address management by default", "help": "Enable FortiExtender LAN extension interface address management by default.", "label": "Enable", "name": "enable"}] | None = ...,
        manage_ssid_addresses: Literal[{"description": "Disable FortiAP SSID address management by default", "help": "Disable FortiAP SSID address management by default.", "label": "Disable", "name": "disable"}, {"description": "Enable FortiAP SSID address management by default", "help": "Enable FortiAP SSID address management by default.", "label": "Enable", "name": "enable"}] | None = ...,
        pools: list[dict[str, Any]] | None = ...,
        rules: list[dict[str, Any]] | None = ...,
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
        payload_dict: IpamPayload | None = ...,
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
    "Ipam",
    "IpamPayload",
]