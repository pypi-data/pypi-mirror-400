from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class MobileTunnelPayload(TypedDict, total=False):
    """
    Type hints for system/mobile_tunnel payload fields.
    
    Configure Mobile tunnels, an implementation of Network Mobility (NEMO) extensions for Mobile IPv4 RFC5177.
    
    **Related Resources:**

    Dependencies (resources this endpoint references):
        - :class:`~.system.interface.InterfaceEndpoint` (via: roaming-interface)

    **Usage:**
        payload: MobileTunnelPayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    name: NotRequired[str]  # Tunnel name.
    status: NotRequired[Literal[{"description": "Disable this mobile tunnel", "help": "Disable this mobile tunnel.", "label": "Disable", "name": "disable"}, {"description": "Enable this mobile tunnel", "help": "Enable this mobile tunnel.", "label": "Enable", "name": "enable"}]]  # Enable/disable this mobile tunnel.
    roaming_interface: str  # Select the associated interface name from available options.
    home_agent: str  # IPv4 address of the NEMO HA (Format: xxx.xxx.xxx.xxx).
    home_address: NotRequired[str]  # Home IP address (Format: xxx.xxx.xxx.xxx).
    renew_interval: int  # Time before lifetime expiration to send NMMO HA re-registrat
    lifetime: int  # NMMO HA registration request lifetime (180 - 65535 sec, defa
    reg_interval: int  # NMMO HA registration interval (5 - 300, default = 5).
    reg_retry: int  # Maximum number of NMMO HA registration retries (1 to 30, def
    n_mhae_spi: int  # NEMO authentication SPI (default: 256).
    n_mhae_key_type: Literal[{"description": "The authentication key is an ASCII string", "help": "The authentication key is an ASCII string.", "label": "Ascii", "name": "ascii"}, {"description": "The authentication key is Base64 encoded", "help": "The authentication key is Base64 encoded.", "label": "Base64", "name": "base64"}]  # NEMO authentication key type (ASCII or base64).
    n_mhae_key: NotRequired[str]  # NEMO authentication key.
    hash_algorithm: Literal[{"description": "Keyed MD5", "help": "Keyed MD5.", "label": "Hmac Md5", "name": "hmac-md5"}]  # Hash Algorithm (Keyed MD5).
    tunnel_mode: Literal[{"description": "GRE tunnel", "help": "GRE tunnel.", "label": "Gre", "name": "gre"}]  # NEMO tunnel mode (GRE tunnel).
    network: NotRequired[list[dict[str, Any]]]  # NEMO network configuration.


class MobileTunnel:
    """
    Configure Mobile tunnels, an implementation of Network Mobility (NEMO) extensions for Mobile IPv4 RFC5177.
    
    Path: system/mobile_tunnel
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
        payload_dict: MobileTunnelPayload | None = ...,
        name: str | None = ...,
        status: Literal[{"description": "Disable this mobile tunnel", "help": "Disable this mobile tunnel.", "label": "Disable", "name": "disable"}, {"description": "Enable this mobile tunnel", "help": "Enable this mobile tunnel.", "label": "Enable", "name": "enable"}] | None = ...,
        roaming_interface: str | None = ...,
        home_agent: str | None = ...,
        home_address: str | None = ...,
        renew_interval: int | None = ...,
        lifetime: int | None = ...,
        reg_interval: int | None = ...,
        reg_retry: int | None = ...,
        n_mhae_spi: int | None = ...,
        n_mhae_key_type: Literal[{"description": "The authentication key is an ASCII string", "help": "The authentication key is an ASCII string.", "label": "Ascii", "name": "ascii"}, {"description": "The authentication key is Base64 encoded", "help": "The authentication key is Base64 encoded.", "label": "Base64", "name": "base64"}] | None = ...,
        n_mhae_key: str | None = ...,
        hash_algorithm: Literal[{"description": "Keyed MD5", "help": "Keyed MD5.", "label": "Hmac Md5", "name": "hmac-md5"}] | None = ...,
        tunnel_mode: Literal[{"description": "GRE tunnel", "help": "GRE tunnel.", "label": "Gre", "name": "gre"}] | None = ...,
        network: list[dict[str, Any]] | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: MobileTunnelPayload | None = ...,
        name: str | None = ...,
        status: Literal[{"description": "Disable this mobile tunnel", "help": "Disable this mobile tunnel.", "label": "Disable", "name": "disable"}, {"description": "Enable this mobile tunnel", "help": "Enable this mobile tunnel.", "label": "Enable", "name": "enable"}] | None = ...,
        roaming_interface: str | None = ...,
        home_agent: str | None = ...,
        home_address: str | None = ...,
        renew_interval: int | None = ...,
        lifetime: int | None = ...,
        reg_interval: int | None = ...,
        reg_retry: int | None = ...,
        n_mhae_spi: int | None = ...,
        n_mhae_key_type: Literal[{"description": "The authentication key is an ASCII string", "help": "The authentication key is an ASCII string.", "label": "Ascii", "name": "ascii"}, {"description": "The authentication key is Base64 encoded", "help": "The authentication key is Base64 encoded.", "label": "Base64", "name": "base64"}] | None = ...,
        n_mhae_key: str | None = ...,
        hash_algorithm: Literal[{"description": "Keyed MD5", "help": "Keyed MD5.", "label": "Hmac Md5", "name": "hmac-md5"}] | None = ...,
        tunnel_mode: Literal[{"description": "GRE tunnel", "help": "GRE tunnel.", "label": "Gre", "name": "gre"}] | None = ...,
        network: list[dict[str, Any]] | None = ...,
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
        payload_dict: MobileTunnelPayload | None = ...,
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
    "MobileTunnel",
    "MobileTunnelPayload",
]