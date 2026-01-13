from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class ServerPayload(TypedDict, total=False):
    """
    Type hints for icap/server payload fields.
    
    Configure ICAP servers.
    
    **Related Resources:**

    Dependencies (resources this endpoint references):
        - :class:`~.certificate.ca.CaEndpoint` (via: ssl-cert)

    **Usage:**
        payload: ServerPayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    name: NotRequired[str]  # Server name.
    addr_type: NotRequired[Literal[{"description": "Use an IPv4 address for the remote ICAP server", "help": "Use an IPv4 address for the remote ICAP server.", "label": "Ip4", "name": "ip4"}, {"description": "Use an IPv6 address for the remote ICAP server", "help": "Use an IPv6 address for the remote ICAP server.", "label": "Ip6", "name": "ip6"}, {"description": "Use the FQDN for the forwarding proxy server", "help": "Use the FQDN for the forwarding proxy server.", "label": "Fqdn", "name": "fqdn"}]]  # Address type of the remote ICAP server: IPv4, IPv6 or FQDN.
    ip_address: str  # IPv4 address of the ICAP server.
    ip6_address: str  # IPv6 address of the ICAP server.
    fqdn: NotRequired[str]  # ICAP remote server Fully Qualified Domain Name (FQDN).
    port: NotRequired[int]  # ICAP server port.
    max_connections: NotRequired[int]  # Maximum number of concurrent connections to ICAP server (unl
    secure: NotRequired[Literal[{"description": "Disable connection to secure ICAP server", "help": "Disable connection to secure ICAP server.", "label": "Disable", "name": "disable"}, {"description": "Enable connection to secure ICAP server", "help": "Enable connection to secure ICAP server.", "label": "Enable", "name": "enable"}]]  # Enable/disable secure connection to ICAP server.
    ssl_cert: NotRequired[str]  # CA certificate name.
    healthcheck: NotRequired[Literal[{"description": "Disable health checking", "help": "Disable health checking.", "label": "Disable", "name": "disable"}, {"description": "Enable health checking", "help": "Enable health checking.", "label": "Enable", "name": "enable"}]]  # Enable/disable ICAP remote server health checking. Attempts 
    healthcheck_service: str  # ICAP Service name to use for health checks.


class Server:
    """
    Configure ICAP servers.
    
    Path: icap/server
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
        payload_dict: ServerPayload | None = ...,
        name: str | None = ...,
        addr_type: Literal[{"description": "Use an IPv4 address for the remote ICAP server", "help": "Use an IPv4 address for the remote ICAP server.", "label": "Ip4", "name": "ip4"}, {"description": "Use an IPv6 address for the remote ICAP server", "help": "Use an IPv6 address for the remote ICAP server.", "label": "Ip6", "name": "ip6"}, {"description": "Use the FQDN for the forwarding proxy server", "help": "Use the FQDN for the forwarding proxy server.", "label": "Fqdn", "name": "fqdn"}] | None = ...,
        ip_address: str | None = ...,
        ip6_address: str | None = ...,
        fqdn: str | None = ...,
        port: int | None = ...,
        max_connections: int | None = ...,
        secure: Literal[{"description": "Disable connection to secure ICAP server", "help": "Disable connection to secure ICAP server.", "label": "Disable", "name": "disable"}, {"description": "Enable connection to secure ICAP server", "help": "Enable connection to secure ICAP server.", "label": "Enable", "name": "enable"}] | None = ...,
        ssl_cert: str | None = ...,
        healthcheck: Literal[{"description": "Disable health checking", "help": "Disable health checking.", "label": "Disable", "name": "disable"}, {"description": "Enable health checking", "help": "Enable health checking.", "label": "Enable", "name": "enable"}] | None = ...,
        healthcheck_service: str | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: ServerPayload | None = ...,
        name: str | None = ...,
        addr_type: Literal[{"description": "Use an IPv4 address for the remote ICAP server", "help": "Use an IPv4 address for the remote ICAP server.", "label": "Ip4", "name": "ip4"}, {"description": "Use an IPv6 address for the remote ICAP server", "help": "Use an IPv6 address for the remote ICAP server.", "label": "Ip6", "name": "ip6"}, {"description": "Use the FQDN for the forwarding proxy server", "help": "Use the FQDN for the forwarding proxy server.", "label": "Fqdn", "name": "fqdn"}] | None = ...,
        ip_address: str | None = ...,
        ip6_address: str | None = ...,
        fqdn: str | None = ...,
        port: int | None = ...,
        max_connections: int | None = ...,
        secure: Literal[{"description": "Disable connection to secure ICAP server", "help": "Disable connection to secure ICAP server.", "label": "Disable", "name": "disable"}, {"description": "Enable connection to secure ICAP server", "help": "Enable connection to secure ICAP server.", "label": "Enable", "name": "enable"}] | None = ...,
        ssl_cert: str | None = ...,
        healthcheck: Literal[{"description": "Disable health checking", "help": "Disable health checking.", "label": "Disable", "name": "disable"}, {"description": "Enable health checking", "help": "Enable health checking.", "label": "Enable", "name": "enable"}] | None = ...,
        healthcheck_service: str | None = ...,
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
        payload_dict: ServerPayload | None = ...,
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
    "Server",
    "ServerPayload",
]