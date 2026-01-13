from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class FssoPollingPayload(TypedDict, total=False):
    """
    Type hints for user/fsso_polling payload fields.
    
    Configure FSSO active directory servers for polling mode.
    
    **Related Resources:**

    Dependencies (resources this endpoint references):
        - :class:`~.user.ldap.LdapEndpoint` (via: ldap-server)

    **Usage:**
        payload: FssoPollingPayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    id: NotRequired[int]  # Active Directory server ID.
    status: NotRequired[Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]]  # Enable/disable polling for the status of this Active Directo
    server: str  # Host name or IP address of the Active Directory server.
    default_domain: NotRequired[str]  # Default domain managed by this Active Directory server.
    port: NotRequired[int]  # Port to communicate with this Active Directory server.
    user: str  # User name required to log into this Active Directory server.
    password: NotRequired[str]  # Password required to log into this Active Directory server.
    ldap_server: str  # LDAP server name used in LDAP connection strings.
    logon_history: NotRequired[int]  # Number of hours of logon history to keep, 0 means keep all h
    polling_frequency: NotRequired[int]  # Polling frequency (every 1 to 30 seconds).
    adgrp: NotRequired[list[dict[str, Any]]]  # LDAP Group Info.
    smbv1: NotRequired[Literal[{"description": "Enable support of SMBv1 for Samba", "help": "Enable support of SMBv1 for Samba.", "label": "Enable", "name": "enable"}, {"description": "Disable support of SMBv1 for Samba", "help": "Disable support of SMBv1 for Samba.", "label": "Disable", "name": "disable"}]]  # Enable/disable support of SMBv1 for Samba.
    smb_ntlmv1_auth: NotRequired[Literal[{"description": "Enable support of NTLMv1 for Samba authentication", "help": "Enable support of NTLMv1 for Samba authentication.", "label": "Enable", "name": "enable"}, {"description": "Disable support of NTLMv1 for Samba authentication", "help": "Disable support of NTLMv1 for Samba authentication.", "label": "Disable", "name": "disable"}]]  # Enable/disable support of NTLMv1 for Samba authentication.


class FssoPolling:
    """
    Configure FSSO active directory servers for polling mode.
    
    Path: user/fsso_polling
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
        payload_dict: FssoPollingPayload | None = ...,
        id: int | None = ...,
        status: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        server: str | None = ...,
        default_domain: str | None = ...,
        port: int | None = ...,
        user: str | None = ...,
        password: str | None = ...,
        ldap_server: str | None = ...,
        logon_history: int | None = ...,
        polling_frequency: int | None = ...,
        adgrp: list[dict[str, Any]] | None = ...,
        smbv1: Literal[{"description": "Enable support of SMBv1 for Samba", "help": "Enable support of SMBv1 for Samba.", "label": "Enable", "name": "enable"}, {"description": "Disable support of SMBv1 for Samba", "help": "Disable support of SMBv1 for Samba.", "label": "Disable", "name": "disable"}] | None = ...,
        smb_ntlmv1_auth: Literal[{"description": "Enable support of NTLMv1 for Samba authentication", "help": "Enable support of NTLMv1 for Samba authentication.", "label": "Enable", "name": "enable"}, {"description": "Disable support of NTLMv1 for Samba authentication", "help": "Disable support of NTLMv1 for Samba authentication.", "label": "Disable", "name": "disable"}] | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: FssoPollingPayload | None = ...,
        id: int | None = ...,
        status: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        server: str | None = ...,
        default_domain: str | None = ...,
        port: int | None = ...,
        user: str | None = ...,
        password: str | None = ...,
        ldap_server: str | None = ...,
        logon_history: int | None = ...,
        polling_frequency: int | None = ...,
        adgrp: list[dict[str, Any]] | None = ...,
        smbv1: Literal[{"description": "Enable support of SMBv1 for Samba", "help": "Enable support of SMBv1 for Samba.", "label": "Enable", "name": "enable"}, {"description": "Disable support of SMBv1 for Samba", "help": "Disable support of SMBv1 for Samba.", "label": "Disable", "name": "disable"}] | None = ...,
        smb_ntlmv1_auth: Literal[{"description": "Enable support of NTLMv1 for Samba authentication", "help": "Enable support of NTLMv1 for Samba authentication.", "label": "Enable", "name": "enable"}, {"description": "Disable support of NTLMv1 for Samba authentication", "help": "Disable support of NTLMv1 for Samba authentication.", "label": "Disable", "name": "disable"}] | None = ...,
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
        payload_dict: FssoPollingPayload | None = ...,
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
    "FssoPolling",
    "FssoPollingPayload",
]