from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class EmailServerPayload(TypedDict, total=False):
    """
    Type hints for system/email_server payload fields.
    
    Configure the email server used by the FortiGate various things. For example, for sending email messages to users to support user authentication features.
    
    **Related Resources:**

    Dependencies (resources this endpoint references):
        - :class:`~.system.interface.InterfaceEndpoint` (via: interface)

    **Usage:**
        payload: EmailServerPayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    type: NotRequired[Literal[{"description": "Use custom email server", "help": "Use custom email server.", "label": "Custom", "name": "custom"}]]  # Use FortiGuard Message service or custom email server.
    server: NotRequired[str]  # SMTP server IP address or hostname.
    port: NotRequired[int]  # SMTP server port.
    source_ip: NotRequired[str]  # SMTP server IPv4 source IP.
    source_ip6: NotRequired[str]  # SMTP server IPv6 source IP.
    authenticate: NotRequired[Literal[{"description": "Enable authentication", "help": "Enable authentication.", "label": "Enable", "name": "enable"}, {"description": "Disable authentication", "help": "Disable authentication.", "label": "Disable", "name": "disable"}]]  # Enable/disable authentication.
    validate_server: NotRequired[Literal[{"description": "Enable validation of server certificate", "help": "Enable validation of server certificate.", "label": "Enable", "name": "enable"}, {"description": "Disable validation of server certificate", "help": "Disable validation of server certificate.", "label": "Disable", "name": "disable"}]]  # Enable/disable validation of server certificate.
    username: NotRequired[str]  # SMTP server user name for authentication.
    password: NotRequired[str]  # SMTP server user password for authentication.
    security: NotRequired[Literal[{"description": "None", "help": "None.", "label": "None", "name": "none"}, {"description": "STARTTLS", "help": "STARTTLS.", "label": "Starttls", "name": "starttls"}, {"description": "SSL/TLS", "help": "SSL/TLS.", "label": "Smtps", "name": "smtps"}]]  # Connection security used by the email server.
    ssl_min_proto_version: NotRequired[Literal[{"description": "Follow system global setting", "help": "Follow system global setting.", "label": "Default", "name": "default"}, {"description": "SSLv3", "help": "SSLv3.", "label": "Sslv3", "name": "SSLv3"}, {"description": "TLSv1", "help": "TLSv1.", "label": "Tlsv1", "name": "TLSv1"}, {"description": "TLSv1", "help": "TLSv1.1.", "label": "Tlsv1 1", "name": "TLSv1-1"}, {"description": "TLSv1", "help": "TLSv1.2.", "label": "Tlsv1 2", "name": "TLSv1-2"}, {"description": "TLSv1", "help": "TLSv1.3.", "label": "Tlsv1 3", "name": "TLSv1-3"}]]  # Minimum supported protocol version for SSL/TLS connections (
    interface_select_method: NotRequired[Literal[{"description": "Set outgoing interface automatically", "help": "Set outgoing interface automatically.", "label": "Auto", "name": "auto"}, {"description": "Set outgoing interface by SD-WAN or policy routing rules", "help": "Set outgoing interface by SD-WAN or policy routing rules.", "label": "Sdwan", "name": "sdwan"}, {"description": "Set outgoing interface manually", "help": "Set outgoing interface manually.", "label": "Specify", "name": "specify"}]]  # Specify how to select outgoing interface to reach server.
    interface: str  # Specify outgoing interface to reach server.
    vrf_select: NotRequired[int]  # VRF ID used for connection to server.


class EmailServer:
    """
    Configure the email server used by the FortiGate various things. For example, for sending email messages to users to support user authentication features.
    
    Path: system/email_server
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
        payload_dict: EmailServerPayload | None = ...,
        type: Literal[{"description": "Use custom email server", "help": "Use custom email server.", "label": "Custom", "name": "custom"}] | None = ...,
        server: str | None = ...,
        port: int | None = ...,
        source_ip: str | None = ...,
        source_ip6: str | None = ...,
        authenticate: Literal[{"description": "Enable authentication", "help": "Enable authentication.", "label": "Enable", "name": "enable"}, {"description": "Disable authentication", "help": "Disable authentication.", "label": "Disable", "name": "disable"}] | None = ...,
        validate_server: Literal[{"description": "Enable validation of server certificate", "help": "Enable validation of server certificate.", "label": "Enable", "name": "enable"}, {"description": "Disable validation of server certificate", "help": "Disable validation of server certificate.", "label": "Disable", "name": "disable"}] | None = ...,
        username: str | None = ...,
        password: str | None = ...,
        security: Literal[{"description": "None", "help": "None.", "label": "None", "name": "none"}, {"description": "STARTTLS", "help": "STARTTLS.", "label": "Starttls", "name": "starttls"}, {"description": "SSL/TLS", "help": "SSL/TLS.", "label": "Smtps", "name": "smtps"}] | None = ...,
        ssl_min_proto_version: Literal[{"description": "Follow system global setting", "help": "Follow system global setting.", "label": "Default", "name": "default"}, {"description": "SSLv3", "help": "SSLv3.", "label": "Sslv3", "name": "SSLv3"}, {"description": "TLSv1", "help": "TLSv1.", "label": "Tlsv1", "name": "TLSv1"}, {"description": "TLSv1", "help": "TLSv1.1.", "label": "Tlsv1 1", "name": "TLSv1-1"}, {"description": "TLSv1", "help": "TLSv1.2.", "label": "Tlsv1 2", "name": "TLSv1-2"}, {"description": "TLSv1", "help": "TLSv1.3.", "label": "Tlsv1 3", "name": "TLSv1-3"}] | None = ...,
        interface_select_method: Literal[{"description": "Set outgoing interface automatically", "help": "Set outgoing interface automatically.", "label": "Auto", "name": "auto"}, {"description": "Set outgoing interface by SD-WAN or policy routing rules", "help": "Set outgoing interface by SD-WAN or policy routing rules.", "label": "Sdwan", "name": "sdwan"}, {"description": "Set outgoing interface manually", "help": "Set outgoing interface manually.", "label": "Specify", "name": "specify"}] | None = ...,
        interface: str | None = ...,
        vrf_select: int | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: EmailServerPayload | None = ...,
        type: Literal[{"description": "Use custom email server", "help": "Use custom email server.", "label": "Custom", "name": "custom"}] | None = ...,
        server: str | None = ...,
        port: int | None = ...,
        source_ip: str | None = ...,
        source_ip6: str | None = ...,
        authenticate: Literal[{"description": "Enable authentication", "help": "Enable authentication.", "label": "Enable", "name": "enable"}, {"description": "Disable authentication", "help": "Disable authentication.", "label": "Disable", "name": "disable"}] | None = ...,
        validate_server: Literal[{"description": "Enable validation of server certificate", "help": "Enable validation of server certificate.", "label": "Enable", "name": "enable"}, {"description": "Disable validation of server certificate", "help": "Disable validation of server certificate.", "label": "Disable", "name": "disable"}] | None = ...,
        username: str | None = ...,
        password: str | None = ...,
        security: Literal[{"description": "None", "help": "None.", "label": "None", "name": "none"}, {"description": "STARTTLS", "help": "STARTTLS.", "label": "Starttls", "name": "starttls"}, {"description": "SSL/TLS", "help": "SSL/TLS.", "label": "Smtps", "name": "smtps"}] | None = ...,
        ssl_min_proto_version: Literal[{"description": "Follow system global setting", "help": "Follow system global setting.", "label": "Default", "name": "default"}, {"description": "SSLv3", "help": "SSLv3.", "label": "Sslv3", "name": "SSLv3"}, {"description": "TLSv1", "help": "TLSv1.", "label": "Tlsv1", "name": "TLSv1"}, {"description": "TLSv1", "help": "TLSv1.1.", "label": "Tlsv1 1", "name": "TLSv1-1"}, {"description": "TLSv1", "help": "TLSv1.2.", "label": "Tlsv1 2", "name": "TLSv1-2"}, {"description": "TLSv1", "help": "TLSv1.3.", "label": "Tlsv1 3", "name": "TLSv1-3"}] | None = ...,
        interface_select_method: Literal[{"description": "Set outgoing interface automatically", "help": "Set outgoing interface automatically.", "label": "Auto", "name": "auto"}, {"description": "Set outgoing interface by SD-WAN or policy routing rules", "help": "Set outgoing interface by SD-WAN or policy routing rules.", "label": "Sdwan", "name": "sdwan"}, {"description": "Set outgoing interface manually", "help": "Set outgoing interface manually.", "label": "Specify", "name": "specify"}] | None = ...,
        interface: str | None = ...,
        vrf_select: int | None = ...,
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
        payload_dict: EmailServerPayload | None = ...,
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
    "EmailServer",
    "EmailServerPayload",
]