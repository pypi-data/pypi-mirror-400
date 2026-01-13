from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class DomainControllerPayload(TypedDict, total=False):
    """
    Type hints for user/domain_controller payload fields.
    
    Configure domain controller entries.
    
    **Related Resources:**

    Dependencies (resources this endpoint references):
        - :class:`~.system.interface.InterfaceEndpoint` (via: interface)

    **Usage:**
        payload: DomainControllerPayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    name: NotRequired[str]  # Domain controller entry name.
    ad_mode: NotRequired[Literal[{"description": "The server is not configured as an Active Directory Domain Server (AD DS)", "help": "The server is not configured as an Active Directory Domain Server (AD DS).", "label": "None", "name": "none"}, {"description": "The server is configured as an Active Directory Domain Server (AD DS)", "help": "The server is configured as an Active Directory Domain Server (AD DS).", "label": "Ds", "name": "ds"}, {"description": "The server is an Active Directory Lightweight Domain Server (AD LDS)", "help": "The server is an Active Directory Lightweight Domain Server (AD LDS).", "label": "Lds", "name": "lds"}]]  # Set Active Directory mode.
    hostname: str  # Hostname of the server to connect to.
    username: str  # User name to sign in with. Must have proper permissions for 
    password: str  # Password for specified username.
    ip_address: NotRequired[str]  # Domain controller IPv4 address.
    ip6: NotRequired[str]  # Domain controller IPv6 address.
    port: NotRequired[int]  # Port to be used for communication with the domain controller
    source_ip_address: NotRequired[str]  # FortiGate IPv4 address to be used for communication with the
    source_ip6: NotRequired[str]  # FortiGate IPv6 address to be used for communication with the
    source_port: NotRequired[int]  # Source port to be used for communication with the domain con
    interface_select_method: NotRequired[Literal[{"description": "Set outgoing interface automatically", "help": "Set outgoing interface automatically.", "label": "Auto", "name": "auto"}, {"description": "Set outgoing interface by SD-WAN or policy routing rules", "help": "Set outgoing interface by SD-WAN or policy routing rules.", "label": "Sdwan", "name": "sdwan"}, {"description": "Set outgoing interface manually", "help": "Set outgoing interface manually.", "label": "Specify", "name": "specify"}]]  # Specify how to select outgoing interface to reach server.
    interface: str  # Specify outgoing interface to reach server.
    extra_server: NotRequired[list[dict[str, Any]]]  # Extra servers.
    domain_name: NotRequired[str]  # Domain DNS name.
    replication_port: NotRequired[int]  # Port to be used for communication with the domain controller
    ldap_server: NotRequired[list[dict[str, Any]]]  # LDAP server name(s).
    change_detection: NotRequired[Literal[{"description": "Enable detection of a configuration change in the Active Directory server", "help": "Enable detection of a configuration change in the Active Directory server.", "label": "Enable", "name": "enable"}, {"description": "Disable detection of a configuration change in the Active Directory server", "help": "Disable detection of a configuration change in the Active Directory server.", "label": "Disable", "name": "disable"}]]  # Enable/disable detection of a configuration change in the Ac
    change_detection_period: NotRequired[int]  # Minutes to detect a configuration change in the Active Direc
    dns_srv_lookup: NotRequired[Literal[{"description": "Enable DNS service lookup", "help": "Enable DNS service lookup.", "label": "Enable", "name": "enable"}, {"description": "Disable DNS service lookup", "help": "Disable DNS service lookup.", "label": "Disable", "name": "disable"}]]  # Enable/disable DNS service lookup.
    adlds_dn: str  # AD LDS distinguished name.
    adlds_ip_address: NotRequired[str]  # AD LDS IPv4 address.
    adlds_ip6: NotRequired[str]  # AD LDS IPv6 address.
    adlds_port: NotRequired[int]  # Port number of AD LDS service (default = 389).


class DomainController:
    """
    Configure domain controller entries.
    
    Path: user/domain_controller
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
        payload_dict: DomainControllerPayload | None = ...,
        name: str | None = ...,
        ad_mode: Literal[{"description": "The server is not configured as an Active Directory Domain Server (AD DS)", "help": "The server is not configured as an Active Directory Domain Server (AD DS).", "label": "None", "name": "none"}, {"description": "The server is configured as an Active Directory Domain Server (AD DS)", "help": "The server is configured as an Active Directory Domain Server (AD DS).", "label": "Ds", "name": "ds"}, {"description": "The server is an Active Directory Lightweight Domain Server (AD LDS)", "help": "The server is an Active Directory Lightweight Domain Server (AD LDS).", "label": "Lds", "name": "lds"}] | None = ...,
        hostname: str | None = ...,
        username: str | None = ...,
        password: str | None = ...,
        ip_address: str | None = ...,
        ip6: str | None = ...,
        port: int | None = ...,
        source_ip_address: str | None = ...,
        source_ip6: str | None = ...,
        source_port: int | None = ...,
        interface_select_method: Literal[{"description": "Set outgoing interface automatically", "help": "Set outgoing interface automatically.", "label": "Auto", "name": "auto"}, {"description": "Set outgoing interface by SD-WAN or policy routing rules", "help": "Set outgoing interface by SD-WAN or policy routing rules.", "label": "Sdwan", "name": "sdwan"}, {"description": "Set outgoing interface manually", "help": "Set outgoing interface manually.", "label": "Specify", "name": "specify"}] | None = ...,
        interface: str | None = ...,
        extra_server: list[dict[str, Any]] | None = ...,
        domain_name: str | None = ...,
        replication_port: int | None = ...,
        ldap_server: list[dict[str, Any]] | None = ...,
        change_detection: Literal[{"description": "Enable detection of a configuration change in the Active Directory server", "help": "Enable detection of a configuration change in the Active Directory server.", "label": "Enable", "name": "enable"}, {"description": "Disable detection of a configuration change in the Active Directory server", "help": "Disable detection of a configuration change in the Active Directory server.", "label": "Disable", "name": "disable"}] | None = ...,
        change_detection_period: int | None = ...,
        dns_srv_lookup: Literal[{"description": "Enable DNS service lookup", "help": "Enable DNS service lookup.", "label": "Enable", "name": "enable"}, {"description": "Disable DNS service lookup", "help": "Disable DNS service lookup.", "label": "Disable", "name": "disable"}] | None = ...,
        adlds_dn: str | None = ...,
        adlds_ip_address: str | None = ...,
        adlds_ip6: str | None = ...,
        adlds_port: int | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: DomainControllerPayload | None = ...,
        name: str | None = ...,
        ad_mode: Literal[{"description": "The server is not configured as an Active Directory Domain Server (AD DS)", "help": "The server is not configured as an Active Directory Domain Server (AD DS).", "label": "None", "name": "none"}, {"description": "The server is configured as an Active Directory Domain Server (AD DS)", "help": "The server is configured as an Active Directory Domain Server (AD DS).", "label": "Ds", "name": "ds"}, {"description": "The server is an Active Directory Lightweight Domain Server (AD LDS)", "help": "The server is an Active Directory Lightweight Domain Server (AD LDS).", "label": "Lds", "name": "lds"}] | None = ...,
        hostname: str | None = ...,
        username: str | None = ...,
        password: str | None = ...,
        ip_address: str | None = ...,
        ip6: str | None = ...,
        port: int | None = ...,
        source_ip_address: str | None = ...,
        source_ip6: str | None = ...,
        source_port: int | None = ...,
        interface_select_method: Literal[{"description": "Set outgoing interface automatically", "help": "Set outgoing interface automatically.", "label": "Auto", "name": "auto"}, {"description": "Set outgoing interface by SD-WAN or policy routing rules", "help": "Set outgoing interface by SD-WAN or policy routing rules.", "label": "Sdwan", "name": "sdwan"}, {"description": "Set outgoing interface manually", "help": "Set outgoing interface manually.", "label": "Specify", "name": "specify"}] | None = ...,
        interface: str | None = ...,
        extra_server: list[dict[str, Any]] | None = ...,
        domain_name: str | None = ...,
        replication_port: int | None = ...,
        ldap_server: list[dict[str, Any]] | None = ...,
        change_detection: Literal[{"description": "Enable detection of a configuration change in the Active Directory server", "help": "Enable detection of a configuration change in the Active Directory server.", "label": "Enable", "name": "enable"}, {"description": "Disable detection of a configuration change in the Active Directory server", "help": "Disable detection of a configuration change in the Active Directory server.", "label": "Disable", "name": "disable"}] | None = ...,
        change_detection_period: int | None = ...,
        dns_srv_lookup: Literal[{"description": "Enable DNS service lookup", "help": "Enable DNS service lookup.", "label": "Enable", "name": "enable"}, {"description": "Disable DNS service lookup", "help": "Disable DNS service lookup.", "label": "Disable", "name": "disable"}] | None = ...,
        adlds_dn: str | None = ...,
        adlds_ip_address: str | None = ...,
        adlds_ip6: str | None = ...,
        adlds_port: int | None = ...,
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
        payload_dict: DomainControllerPayload | None = ...,
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
    "DomainController",
    "DomainControllerPayload",
]