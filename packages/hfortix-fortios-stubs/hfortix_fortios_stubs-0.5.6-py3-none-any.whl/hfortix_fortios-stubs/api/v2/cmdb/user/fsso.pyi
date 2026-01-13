from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class FssoPayload(TypedDict, total=False):
    """
    Type hints for user/fsso payload fields.
    
    Configure Fortinet Single Sign On (FSSO) agents.
    
    **Related Resources:**

    Dependencies (resources this endpoint references):
        - :class:`~.system.interface.InterfaceEndpoint` (via: interface)
        - :class:`~.user.ldap.LdapEndpoint` (via: ldap-server, user-info-server)
        - :class:`~.vpn.certificate.ca.CaEndpoint` (via: ssl-trusted-cert)
        - :class:`~.vpn.certificate.remote.RemoteEndpoint` (via: ssl-trusted-cert)

    **Usage:**
        payload: FssoPayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    name: str  # Name.
    type: NotRequired[Literal[{"description": "All other unspecified types of servers", "help": "All other unspecified types of servers.", "label": "Default", "name": "default"}, {"description": "FortiNAC server", "help": "FortiNAC server.", "label": "Fortinac", "name": "fortinac"}]]  # Server type.
    server: str  # Domain name or IP address of the first FSSO collector agent.
    port: int  # Port of the first FSSO collector agent.
    password: NotRequired[str]  # Password of the first FSSO collector agent.
    server2: NotRequired[str]  # Domain name or IP address of the second FSSO collector agent
    port2: NotRequired[int]  # Port of the second FSSO collector agent.
    password2: NotRequired[str]  # Password of the second FSSO collector agent.
    server3: NotRequired[str]  # Domain name or IP address of the third FSSO collector agent.
    port3: NotRequired[int]  # Port of the third FSSO collector agent.
    password3: NotRequired[str]  # Password of the third FSSO collector agent.
    server4: NotRequired[str]  # Domain name or IP address of the fourth FSSO collector agent
    port4: NotRequired[int]  # Port of the fourth FSSO collector agent.
    password4: NotRequired[str]  # Password of the fourth FSSO collector agent.
    server5: NotRequired[str]  # Domain name or IP address of the fifth FSSO collector agent.
    port5: NotRequired[int]  # Port of the fifth FSSO collector agent.
    password5: NotRequired[str]  # Password of the fifth FSSO collector agent.
    logon_timeout: NotRequired[int]  # Interval in minutes to keep logons after FSSO server down.
    ldap_server: NotRequired[str]  # LDAP server to get group information.
    group_poll_interval: NotRequired[int]  # Interval in minutes within to fetch groups from FSSO server,
    ldap_poll: NotRequired[Literal[{"description": "Enable automatic fetching of groups from LDAP server", "help": "Enable automatic fetching of groups from LDAP server.", "label": "Enable", "name": "enable"}, {"description": "Disable automatic fetching of groups from LDAP server", "help": "Disable automatic fetching of groups from LDAP server.", "label": "Disable", "name": "disable"}]]  # Enable/disable automatic fetching of groups from LDAP server
    ldap_poll_interval: NotRequired[int]  # Interval in minutes within to fetch groups from LDAP server.
    ldap_poll_filter: NotRequired[str]  # Filter used to fetch groups.
    user_info_server: NotRequired[str]  # LDAP server to get user information.
    ssl: NotRequired[Literal[{"description": "Enable use of SSL", "help": "Enable use of SSL.", "label": "Enable", "name": "enable"}, {"description": "Disable use of SSL", "help": "Disable use of SSL.", "label": "Disable", "name": "disable"}]]  # Enable/disable use of SSL.
    sni: NotRequired[str]  # Server Name Indication.
    ssl_server_host_ip_check: NotRequired[Literal[{"description": "Enable server host/IP verification", "help": "Enable server host/IP verification.", "label": "Enable", "name": "enable"}, {"description": "Disable server host/IP verification", "help": "Disable server host/IP verification.", "label": "Disable", "name": "disable"}]]  # Enable/disable server host/IP verification.
    ssl_trusted_cert: NotRequired[str]  # Trusted server certificate or CA certificate.
    source_ip: NotRequired[str]  # Source IP for communications to FSSO agent.
    source_ip6: NotRequired[str]  # IPv6 source for communications to FSSO agent.
    interface_select_method: NotRequired[Literal[{"description": "Set outgoing interface automatically", "help": "Set outgoing interface automatically.", "label": "Auto", "name": "auto"}, {"description": "Set outgoing interface by SD-WAN or policy routing rules", "help": "Set outgoing interface by SD-WAN or policy routing rules.", "label": "Sdwan", "name": "sdwan"}, {"description": "Set outgoing interface manually", "help": "Set outgoing interface manually.", "label": "Specify", "name": "specify"}]]  # Specify how to select outgoing interface to reach server.
    interface: str  # Specify outgoing interface to reach server.
    vrf_select: NotRequired[int]  # VRF ID used for connection to server.


class Fsso:
    """
    Configure Fortinet Single Sign On (FSSO) agents.
    
    Path: user/fsso
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
        payload_dict: FssoPayload | None = ...,
        name: str | None = ...,
        type: Literal[{"description": "All other unspecified types of servers", "help": "All other unspecified types of servers.", "label": "Default", "name": "default"}, {"description": "FortiNAC server", "help": "FortiNAC server.", "label": "Fortinac", "name": "fortinac"}] | None = ...,
        server: str | None = ...,
        port: int | None = ...,
        password: str | None = ...,
        server2: str | None = ...,
        port2: int | None = ...,
        password2: str | None = ...,
        server3: str | None = ...,
        port3: int | None = ...,
        password3: str | None = ...,
        server4: str | None = ...,
        port4: int | None = ...,
        password4: str | None = ...,
        server5: str | None = ...,
        port5: int | None = ...,
        password5: str | None = ...,
        logon_timeout: int | None = ...,
        ldap_server: str | None = ...,
        group_poll_interval: int | None = ...,
        ldap_poll: Literal[{"description": "Enable automatic fetching of groups from LDAP server", "help": "Enable automatic fetching of groups from LDAP server.", "label": "Enable", "name": "enable"}, {"description": "Disable automatic fetching of groups from LDAP server", "help": "Disable automatic fetching of groups from LDAP server.", "label": "Disable", "name": "disable"}] | None = ...,
        ldap_poll_interval: int | None = ...,
        ldap_poll_filter: str | None = ...,
        user_info_server: str | None = ...,
        ssl: Literal[{"description": "Enable use of SSL", "help": "Enable use of SSL.", "label": "Enable", "name": "enable"}, {"description": "Disable use of SSL", "help": "Disable use of SSL.", "label": "Disable", "name": "disable"}] | None = ...,
        sni: str | None = ...,
        ssl_server_host_ip_check: Literal[{"description": "Enable server host/IP verification", "help": "Enable server host/IP verification.", "label": "Enable", "name": "enable"}, {"description": "Disable server host/IP verification", "help": "Disable server host/IP verification.", "label": "Disable", "name": "disable"}] | None = ...,
        ssl_trusted_cert: str | None = ...,
        source_ip: str | None = ...,
        source_ip6: str | None = ...,
        interface_select_method: Literal[{"description": "Set outgoing interface automatically", "help": "Set outgoing interface automatically.", "label": "Auto", "name": "auto"}, {"description": "Set outgoing interface by SD-WAN or policy routing rules", "help": "Set outgoing interface by SD-WAN or policy routing rules.", "label": "Sdwan", "name": "sdwan"}, {"description": "Set outgoing interface manually", "help": "Set outgoing interface manually.", "label": "Specify", "name": "specify"}] | None = ...,
        interface: str | None = ...,
        vrf_select: int | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: FssoPayload | None = ...,
        name: str | None = ...,
        type: Literal[{"description": "All other unspecified types of servers", "help": "All other unspecified types of servers.", "label": "Default", "name": "default"}, {"description": "FortiNAC server", "help": "FortiNAC server.", "label": "Fortinac", "name": "fortinac"}] | None = ...,
        server: str | None = ...,
        port: int | None = ...,
        password: str | None = ...,
        server2: str | None = ...,
        port2: int | None = ...,
        password2: str | None = ...,
        server3: str | None = ...,
        port3: int | None = ...,
        password3: str | None = ...,
        server4: str | None = ...,
        port4: int | None = ...,
        password4: str | None = ...,
        server5: str | None = ...,
        port5: int | None = ...,
        password5: str | None = ...,
        logon_timeout: int | None = ...,
        ldap_server: str | None = ...,
        group_poll_interval: int | None = ...,
        ldap_poll: Literal[{"description": "Enable automatic fetching of groups from LDAP server", "help": "Enable automatic fetching of groups from LDAP server.", "label": "Enable", "name": "enable"}, {"description": "Disable automatic fetching of groups from LDAP server", "help": "Disable automatic fetching of groups from LDAP server.", "label": "Disable", "name": "disable"}] | None = ...,
        ldap_poll_interval: int | None = ...,
        ldap_poll_filter: str | None = ...,
        user_info_server: str | None = ...,
        ssl: Literal[{"description": "Enable use of SSL", "help": "Enable use of SSL.", "label": "Enable", "name": "enable"}, {"description": "Disable use of SSL", "help": "Disable use of SSL.", "label": "Disable", "name": "disable"}] | None = ...,
        sni: str | None = ...,
        ssl_server_host_ip_check: Literal[{"description": "Enable server host/IP verification", "help": "Enable server host/IP verification.", "label": "Enable", "name": "enable"}, {"description": "Disable server host/IP verification", "help": "Disable server host/IP verification.", "label": "Disable", "name": "disable"}] | None = ...,
        ssl_trusted_cert: str | None = ...,
        source_ip: str | None = ...,
        source_ip6: str | None = ...,
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
        payload_dict: FssoPayload | None = ...,
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
    "Fsso",
    "FssoPayload",
]