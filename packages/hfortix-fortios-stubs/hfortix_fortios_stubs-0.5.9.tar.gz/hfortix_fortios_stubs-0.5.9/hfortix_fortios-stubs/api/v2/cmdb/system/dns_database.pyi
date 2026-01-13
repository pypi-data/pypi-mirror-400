from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class DnsDatabasePayload(TypedDict, total=False):
    """
    Type hints for system/dns_database payload fields.
    
    Configure DNS databases.
    
    **Related Resources:**

    Dependencies (resources this endpoint references):
        - :class:`~.system.interface.InterfaceEndpoint` (via: interface, source-ip-interface)

    **Usage:**
        payload: DnsDatabasePayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    name: str  # Zone name.
    status: NotRequired[Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]]  # Enable/disable this DNS zone.
    domain: str  # Domain name.
    allow_transfer: NotRequired[list[dict[str, Any]]]  # DNS zone transfer IP address list.
    type: Literal[{"description": "Primary DNS zone, to manage entries directly", "help": "Primary DNS zone, to manage entries directly.", "label": "Primary", "name": "primary"}, {"description": "Secondary DNS zone, to import entries from other DNS zones", "help": "Secondary DNS zone, to import entries from other DNS zones.", "label": "Secondary", "name": "secondary"}]  # Zone type (primary to manage entries directly, secondary to 
    view: Literal[{"description": "Shadow DNS zone to serve internal clients", "help": "Shadow DNS zone to serve internal clients.", "label": "Shadow", "name": "shadow"}, {"description": "Public DNS zone to serve public clients", "help": "Public DNS zone to serve public clients.", "label": "Public", "name": "public"}, {"description": "implicit DNS zone for ztna dox tunnel", "help": "implicit DNS zone for ztna dox tunnel.", "label": "Shadow Ztna", "name": "shadow-ztna"}, {"description": "Shadow DNS zone for internal proxy", "help": "Shadow DNS zone for internal proxy.", "label": "Proxy", "name": "proxy"}]  # Zone view (public to serve public clients, shadow to serve i
    ip_primary: NotRequired[str]  # IP address of primary DNS server. Entries in this primary DN
    primary_name: NotRequired[str]  # Domain name of the default DNS server for this zone.
    contact: NotRequired[str]  # Email address of the administrator for this zone. You can sp
    ttl: int  # Default time-to-live value for the entries of this DNS zone 
    authoritative: Literal[{"description": "Enable authoritative zone", "help": "Enable authoritative zone.", "label": "Enable", "name": "enable"}, {"description": "Disable authoritative zone", "help": "Disable authoritative zone.", "label": "Disable", "name": "disable"}]  # Enable/disable authoritative zone.
    forwarder: NotRequired[list[dict[str, Any]]]  # DNS zone forwarder IP address list.
    forwarder6: NotRequired[str]  # Forwarder IPv6 address.
    source_ip: NotRequired[str]  # Source IP for forwarding to DNS server.
    source_ip6: NotRequired[str]  # IPv6 source IP address for forwarding to DNS server.
    source_ip_interface: NotRequired[str]  # IP address of the specified interface as the source IP addre
    rr_max: NotRequired[int]  # Maximum number of resource records (10 - 65536, 0 means infi
    dns_entry: list[dict[str, Any]]  # DNS entry.
    interface_select_method: NotRequired[Literal[{"description": "Set outgoing interface automatically", "help": "Set outgoing interface automatically.", "label": "Auto", "name": "auto"}, {"description": "Set outgoing interface by SD-WAN or policy routing rules", "help": "Set outgoing interface by SD-WAN or policy routing rules.", "label": "Sdwan", "name": "sdwan"}, {"description": "Set outgoing interface manually", "help": "Set outgoing interface manually.", "label": "Specify", "name": "specify"}]]  # Specify how to select outgoing interface to reach server.
    interface: str  # Specify outgoing interface to reach server.
    vrf_select: NotRequired[int]  # VRF ID used for connection to server.


class DnsDatabase:
    """
    Configure DNS databases.
    
    Path: system/dns_database
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
        payload_dict: DnsDatabasePayload | None = ...,
        name: str | None = ...,
        status: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        domain: str | None = ...,
        allow_transfer: list[dict[str, Any]] | None = ...,
        type: Literal[{"description": "Primary DNS zone, to manage entries directly", "help": "Primary DNS zone, to manage entries directly.", "label": "Primary", "name": "primary"}, {"description": "Secondary DNS zone, to import entries from other DNS zones", "help": "Secondary DNS zone, to import entries from other DNS zones.", "label": "Secondary", "name": "secondary"}] | None = ...,
        view: Literal[{"description": "Shadow DNS zone to serve internal clients", "help": "Shadow DNS zone to serve internal clients.", "label": "Shadow", "name": "shadow"}, {"description": "Public DNS zone to serve public clients", "help": "Public DNS zone to serve public clients.", "label": "Public", "name": "public"}, {"description": "implicit DNS zone for ztna dox tunnel", "help": "implicit DNS zone for ztna dox tunnel.", "label": "Shadow Ztna", "name": "shadow-ztna"}, {"description": "Shadow DNS zone for internal proxy", "help": "Shadow DNS zone for internal proxy.", "label": "Proxy", "name": "proxy"}] | None = ...,
        ip_primary: str | None = ...,
        primary_name: str | None = ...,
        contact: str | None = ...,
        ttl: int | None = ...,
        authoritative: Literal[{"description": "Enable authoritative zone", "help": "Enable authoritative zone.", "label": "Enable", "name": "enable"}, {"description": "Disable authoritative zone", "help": "Disable authoritative zone.", "label": "Disable", "name": "disable"}] | None = ...,
        forwarder: list[dict[str, Any]] | None = ...,
        forwarder6: str | None = ...,
        source_ip: str | None = ...,
        source_ip6: str | None = ...,
        source_ip_interface: str | None = ...,
        rr_max: int | None = ...,
        dns_entry: list[dict[str, Any]] | None = ...,
        interface_select_method: Literal[{"description": "Set outgoing interface automatically", "help": "Set outgoing interface automatically.", "label": "Auto", "name": "auto"}, {"description": "Set outgoing interface by SD-WAN or policy routing rules", "help": "Set outgoing interface by SD-WAN or policy routing rules.", "label": "Sdwan", "name": "sdwan"}, {"description": "Set outgoing interface manually", "help": "Set outgoing interface manually.", "label": "Specify", "name": "specify"}] | None = ...,
        interface: str | None = ...,
        vrf_select: int | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: DnsDatabasePayload | None = ...,
        name: str | None = ...,
        status: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        domain: str | None = ...,
        allow_transfer: list[dict[str, Any]] | None = ...,
        type: Literal[{"description": "Primary DNS zone, to manage entries directly", "help": "Primary DNS zone, to manage entries directly.", "label": "Primary", "name": "primary"}, {"description": "Secondary DNS zone, to import entries from other DNS zones", "help": "Secondary DNS zone, to import entries from other DNS zones.", "label": "Secondary", "name": "secondary"}] | None = ...,
        view: Literal[{"description": "Shadow DNS zone to serve internal clients", "help": "Shadow DNS zone to serve internal clients.", "label": "Shadow", "name": "shadow"}, {"description": "Public DNS zone to serve public clients", "help": "Public DNS zone to serve public clients.", "label": "Public", "name": "public"}, {"description": "implicit DNS zone for ztna dox tunnel", "help": "implicit DNS zone for ztna dox tunnel.", "label": "Shadow Ztna", "name": "shadow-ztna"}, {"description": "Shadow DNS zone for internal proxy", "help": "Shadow DNS zone for internal proxy.", "label": "Proxy", "name": "proxy"}] | None = ...,
        ip_primary: str | None = ...,
        primary_name: str | None = ...,
        contact: str | None = ...,
        ttl: int | None = ...,
        authoritative: Literal[{"description": "Enable authoritative zone", "help": "Enable authoritative zone.", "label": "Enable", "name": "enable"}, {"description": "Disable authoritative zone", "help": "Disable authoritative zone.", "label": "Disable", "name": "disable"}] | None = ...,
        forwarder: list[dict[str, Any]] | None = ...,
        forwarder6: str | None = ...,
        source_ip: str | None = ...,
        source_ip6: str | None = ...,
        source_ip_interface: str | None = ...,
        rr_max: int | None = ...,
        dns_entry: list[dict[str, Any]] | None = ...,
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
        payload_dict: DnsDatabasePayload | None = ...,
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
    "DnsDatabase",
    "DnsDatabasePayload",
]