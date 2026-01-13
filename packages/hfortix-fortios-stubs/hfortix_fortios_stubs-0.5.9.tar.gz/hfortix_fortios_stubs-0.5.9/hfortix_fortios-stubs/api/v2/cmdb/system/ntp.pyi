from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class NtpPayload(TypedDict, total=False):
    """
    Type hints for system/ntp payload fields.
    
    Configure system NTP information.
    
    **Usage:**
        payload: NtpPayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    ntpsync: NotRequired[Literal[{"description": "Enable synchronization with NTP Server", "help": "Enable synchronization with NTP Server.", "label": "Enable", "name": "enable"}, {"description": "Disable synchronization with NTP Server", "help": "Disable synchronization with NTP Server.", "label": "Disable", "name": "disable"}]]  # Enable/disable setting the FortiGate system time by synchron
    type: NotRequired[Literal[{"description": "Use the FortiGuard NTP server", "help": "Use the FortiGuard NTP server.", "label": "Fortiguard", "name": "fortiguard"}, {"description": "Use any other available NTP server", "help": "Use any other available NTP server.", "label": "Custom", "name": "custom"}]]  # Use the FortiGuard NTP server or any other available NTP Ser
    syncinterval: NotRequired[int]  # NTP synchronization interval (1 - 1440 min).
    ntpserver: NotRequired[list[dict[str, Any]]]  # Configure the FortiGate to connect to any available third-pa
    source_ip: NotRequired[str]  # Source IP address for communication to the NTP server.
    source_ip6: NotRequired[str]  # Source IPv6 address for communication to the NTP server.
    server_mode: NotRequired[Literal[{"description": "Enable FortiGate NTP Server Mode", "help": "Enable FortiGate NTP Server Mode.", "label": "Enable", "name": "enable"}, {"description": "Disable FortiGate NTP Server Mode", "help": "Disable FortiGate NTP Server Mode.", "label": "Disable", "name": "disable"}]]  # Enable/disable FortiGate NTP Server Mode. Your FortiGate bec
    authentication: NotRequired[Literal[{"description": "Enable authentication", "help": "Enable authentication.", "label": "Enable", "name": "enable"}, {"description": "Disable authentication", "help": "Disable authentication.", "label": "Disable", "name": "disable"}]]  # Enable/disable authentication.
    key_type: NotRequired[Literal[{"description": "Use MD5 to authenticate the message", "help": "Use MD5 to authenticate the message.", "label": "Md5", "name": "MD5"}, {"description": "Use SHA1 to authenticate the message", "help": "Use SHA1 to authenticate the message.", "label": "Sha1", "name": "SHA1"}, {"description": "Use SHA256 to authenticate the message", "help": "Use SHA256 to authenticate the message.", "label": "Sha256", "name": "SHA256"}]]  # Key type for authentication (MD5, SHA1, SHA256).
    key: str  # Key for authentication.
    key_id: int  # Key ID for authentication.
    interface: NotRequired[list[dict[str, Any]]]  # FortiGate interface(s) with NTP server mode enabled. Devices


class Ntp:
    """
    Configure system NTP information.
    
    Path: system/ntp
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
        payload_dict: NtpPayload | None = ...,
        ntpsync: Literal[{"description": "Enable synchronization with NTP Server", "help": "Enable synchronization with NTP Server.", "label": "Enable", "name": "enable"}, {"description": "Disable synchronization with NTP Server", "help": "Disable synchronization with NTP Server.", "label": "Disable", "name": "disable"}] | None = ...,
        type: Literal[{"description": "Use the FortiGuard NTP server", "help": "Use the FortiGuard NTP server.", "label": "Fortiguard", "name": "fortiguard"}, {"description": "Use any other available NTP server", "help": "Use any other available NTP server.", "label": "Custom", "name": "custom"}] | None = ...,
        syncinterval: int | None = ...,
        ntpserver: list[dict[str, Any]] | None = ...,
        source_ip: str | None = ...,
        source_ip6: str | None = ...,
        server_mode: Literal[{"description": "Enable FortiGate NTP Server Mode", "help": "Enable FortiGate NTP Server Mode.", "label": "Enable", "name": "enable"}, {"description": "Disable FortiGate NTP Server Mode", "help": "Disable FortiGate NTP Server Mode.", "label": "Disable", "name": "disable"}] | None = ...,
        authentication: Literal[{"description": "Enable authentication", "help": "Enable authentication.", "label": "Enable", "name": "enable"}, {"description": "Disable authentication", "help": "Disable authentication.", "label": "Disable", "name": "disable"}] | None = ...,
        key_type: Literal[{"description": "Use MD5 to authenticate the message", "help": "Use MD5 to authenticate the message.", "label": "Md5", "name": "MD5"}, {"description": "Use SHA1 to authenticate the message", "help": "Use SHA1 to authenticate the message.", "label": "Sha1", "name": "SHA1"}, {"description": "Use SHA256 to authenticate the message", "help": "Use SHA256 to authenticate the message.", "label": "Sha256", "name": "SHA256"}] | None = ...,
        key: str | None = ...,
        key_id: int | None = ...,
        interface: list[dict[str, Any]] | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: NtpPayload | None = ...,
        ntpsync: Literal[{"description": "Enable synchronization with NTP Server", "help": "Enable synchronization with NTP Server.", "label": "Enable", "name": "enable"}, {"description": "Disable synchronization with NTP Server", "help": "Disable synchronization with NTP Server.", "label": "Disable", "name": "disable"}] | None = ...,
        type: Literal[{"description": "Use the FortiGuard NTP server", "help": "Use the FortiGuard NTP server.", "label": "Fortiguard", "name": "fortiguard"}, {"description": "Use any other available NTP server", "help": "Use any other available NTP server.", "label": "Custom", "name": "custom"}] | None = ...,
        syncinterval: int | None = ...,
        ntpserver: list[dict[str, Any]] | None = ...,
        source_ip: str | None = ...,
        source_ip6: str | None = ...,
        server_mode: Literal[{"description": "Enable FortiGate NTP Server Mode", "help": "Enable FortiGate NTP Server Mode.", "label": "Enable", "name": "enable"}, {"description": "Disable FortiGate NTP Server Mode", "help": "Disable FortiGate NTP Server Mode.", "label": "Disable", "name": "disable"}] | None = ...,
        authentication: Literal[{"description": "Enable authentication", "help": "Enable authentication.", "label": "Enable", "name": "enable"}, {"description": "Disable authentication", "help": "Disable authentication.", "label": "Disable", "name": "disable"}] | None = ...,
        key_type: Literal[{"description": "Use MD5 to authenticate the message", "help": "Use MD5 to authenticate the message.", "label": "Md5", "name": "MD5"}, {"description": "Use SHA1 to authenticate the message", "help": "Use SHA1 to authenticate the message.", "label": "Sha1", "name": "SHA1"}, {"description": "Use SHA256 to authenticate the message", "help": "Use SHA256 to authenticate the message.", "label": "Sha256", "name": "SHA256"}] | None = ...,
        key: str | None = ...,
        key_id: int | None = ...,
        interface: list[dict[str, Any]] | None = ...,
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
        payload_dict: NtpPayload | None = ...,
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
    "Ntp",
    "NtpPayload",
]