from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class Address6Payload(TypedDict, total=False):
    """
    Type hints for firewall/address6 payload fields.
    
    Configure IPv6 firewall addresses.
    
    **Related Resources:**

    Dependencies (resources this endpoint references):
        - :class:`~.firewall.address6-template.Address6TemplateEndpoint` (via: template)
        - :class:`~.system.sdn-connector.SdnConnectorEndpoint` (via: sdn)

    **Usage:**
        payload: Address6Payload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    name: NotRequired[str]  # Address name.
    uuid: NotRequired[str]  # Universally Unique Identifier (UUID; automatically assigned 
    type: NotRequired[Literal[{"description": "Uses the IP prefix to define a range of IPv6 addresses", "help": "Uses the IP prefix to define a range of IPv6 addresses.", "label": "Ipprefix", "name": "ipprefix"}, {"description": "Range of IPv6 addresses between two specified addresses (inclusive)", "help": "Range of IPv6 addresses between two specified addresses (inclusive).", "label": "Iprange", "name": "iprange"}, {"description": "Fully qualified domain name", "help": "Fully qualified domain name.", "label": "Fqdn", "name": "fqdn"}, {"description": "IPv6 addresses from a specified country", "help": "IPv6 addresses from a specified country.", "label": "Geography", "name": "geography"}, {"description": "Dynamic address object for SDN", "help": "Dynamic address object for SDN.", "label": "Dynamic", "name": "dynamic"}, {"description": "Template", "help": "Template.", "label": "Template", "name": "template"}, {"description": "Range of MAC addresses", "help": "Range of MAC addresses.", "label": "Mac", "name": "mac"}, {"description": "route-tag addresses", "help": "route-tag addresses.", "label": "Route Tag", "name": "route-tag"}, {"description": "Standard IPv6 using a wildcard subnet mask", "help": "Standard IPv6 using a wildcard subnet mask.", "label": "Wildcard", "name": "wildcard"}]]  # Type of IPv6 address object (default = ipprefix).
    route_tag: NotRequired[int]  # route-tag address.
    macaddr: NotRequired[list[dict[str, Any]]]  # Multiple MAC address ranges.
    sdn: NotRequired[str]  # SDN.
    ip6: NotRequired[str]  # IPv6 address prefix (format: xxxx:xxxx:xxxx:xxxx:xxxx:xxxx:x
    wildcard: NotRequired[str]  # IPv6 address and wildcard netmask.
    start_ip: NotRequired[str]  # First IP address (inclusive) in the range for the address (f
    end_ip: NotRequired[str]  # Final IP address (inclusive) in the range for the address (f
    fqdn: NotRequired[str]  # Fully qualified domain name.
    country: NotRequired[str]  # IPv6 addresses associated to a specific country.
    cache_ttl: NotRequired[int]  # Minimal TTL of individual IPv6 addresses in FQDN cache.
    color: NotRequired[int]  # Integer value to determine the color of the icon in the GUI 
    obj_id: NotRequired[str]  # Object ID for NSX.
    tagging: NotRequired[list[dict[str, Any]]]  # Config object tagging.
    comment: NotRequired[str]  # Comment.
    template: str  # IPv6 address template.
    subnet_segment: NotRequired[list[dict[str, Any]]]  # IPv6 subnet segments.
    host_type: NotRequired[Literal[{"description": "Wildcard", "help": "Wildcard.", "label": "Any", "name": "any"}, {"description": "Specific host address", "help": "Specific host address.", "label": "Specific", "name": "specific"}]]  # Host type.
    host: NotRequired[str]  # Host Address.
    tenant: NotRequired[str]  # Tenant.
    epg_name: NotRequired[str]  # Endpoint group name.
    sdn_tag: NotRequired[str]  # SDN Tag.
    filter: str  # Match criteria filter.
    list: NotRequired[list[dict[str, Any]]]  # IP address list.
    sdn_addr_type: NotRequired[Literal[{"description": "Collect private addresses only", "help": "Collect private addresses only.", "label": "Private", "name": "private"}, {"description": "Collect public addresses only", "help": "Collect public addresses only.", "label": "Public", "name": "public"}, {"description": "Collect both public and private addresses", "help": "Collect both public and private addresses.", "label": "All", "name": "all"}]]  # Type of addresses to collect.
    passive_fqdn_learning: NotRequired[Literal[{"description": "Disable passive learning of FQDNs", "help": "Disable passive learning of FQDNs.", "label": "Disable", "name": "disable"}, {"description": "Enable passive learning of FQDNs", "help": "Enable passive learning of FQDNs.", "label": "Enable", "name": "enable"}]]  # Enable/disable passive learning of FQDNs.  When enabled, the
    fabric_object: NotRequired[Literal[{"description": "Object is set as a security fabric-wide global object", "help": "Object is set as a security fabric-wide global object.", "label": "Enable", "name": "enable"}, {"description": "Object is local to this security fabric member", "help": "Object is local to this security fabric member.", "label": "Disable", "name": "disable"}]]  # Security Fabric global object setting.


class Address6:
    """
    Configure IPv6 firewall addresses.
    
    Path: firewall/address6
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
        payload_dict: Address6Payload | None = ...,
        name: str | None = ...,
        uuid: str | None = ...,
        type: Literal[{"description": "Uses the IP prefix to define a range of IPv6 addresses", "help": "Uses the IP prefix to define a range of IPv6 addresses.", "label": "Ipprefix", "name": "ipprefix"}, {"description": "Range of IPv6 addresses between two specified addresses (inclusive)", "help": "Range of IPv6 addresses between two specified addresses (inclusive).", "label": "Iprange", "name": "iprange"}, {"description": "Fully qualified domain name", "help": "Fully qualified domain name.", "label": "Fqdn", "name": "fqdn"}, {"description": "IPv6 addresses from a specified country", "help": "IPv6 addresses from a specified country.", "label": "Geography", "name": "geography"}, {"description": "Dynamic address object for SDN", "help": "Dynamic address object for SDN.", "label": "Dynamic", "name": "dynamic"}, {"description": "Template", "help": "Template.", "label": "Template", "name": "template"}, {"description": "Range of MAC addresses", "help": "Range of MAC addresses.", "label": "Mac", "name": "mac"}, {"description": "route-tag addresses", "help": "route-tag addresses.", "label": "Route Tag", "name": "route-tag"}, {"description": "Standard IPv6 using a wildcard subnet mask", "help": "Standard IPv6 using a wildcard subnet mask.", "label": "Wildcard", "name": "wildcard"}] | None = ...,
        route_tag: int | None = ...,
        macaddr: list[dict[str, Any]] | None = ...,
        sdn: str | None = ...,
        ip6: str | None = ...,
        wildcard: str | None = ...,
        start_ip: str | None = ...,
        end_ip: str | None = ...,
        fqdn: str | None = ...,
        country: str | None = ...,
        cache_ttl: int | None = ...,
        color: int | None = ...,
        obj_id: str | None = ...,
        tagging: list[dict[str, Any]] | None = ...,
        comment: str | None = ...,
        template: str | None = ...,
        subnet_segment: list[dict[str, Any]] | None = ...,
        host_type: Literal[{"description": "Wildcard", "help": "Wildcard.", "label": "Any", "name": "any"}, {"description": "Specific host address", "help": "Specific host address.", "label": "Specific", "name": "specific"}] | None = ...,
        host: str | None = ...,
        tenant: str | None = ...,
        epg_name: str | None = ...,
        sdn_tag: str | None = ...,
        filter: str | None = ...,
        list: list[dict[str, Any]] | None = ...,
        sdn_addr_type: Literal[{"description": "Collect private addresses only", "help": "Collect private addresses only.", "label": "Private", "name": "private"}, {"description": "Collect public addresses only", "help": "Collect public addresses only.", "label": "Public", "name": "public"}, {"description": "Collect both public and private addresses", "help": "Collect both public and private addresses.", "label": "All", "name": "all"}] | None = ...,
        passive_fqdn_learning: Literal[{"description": "Disable passive learning of FQDNs", "help": "Disable passive learning of FQDNs.", "label": "Disable", "name": "disable"}, {"description": "Enable passive learning of FQDNs", "help": "Enable passive learning of FQDNs.", "label": "Enable", "name": "enable"}] | None = ...,
        fabric_object: Literal[{"description": "Object is set as a security fabric-wide global object", "help": "Object is set as a security fabric-wide global object.", "label": "Enable", "name": "enable"}, {"description": "Object is local to this security fabric member", "help": "Object is local to this security fabric member.", "label": "Disable", "name": "disable"}] | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: Address6Payload | None = ...,
        name: str | None = ...,
        uuid: str | None = ...,
        type: Literal[{"description": "Uses the IP prefix to define a range of IPv6 addresses", "help": "Uses the IP prefix to define a range of IPv6 addresses.", "label": "Ipprefix", "name": "ipprefix"}, {"description": "Range of IPv6 addresses between two specified addresses (inclusive)", "help": "Range of IPv6 addresses between two specified addresses (inclusive).", "label": "Iprange", "name": "iprange"}, {"description": "Fully qualified domain name", "help": "Fully qualified domain name.", "label": "Fqdn", "name": "fqdn"}, {"description": "IPv6 addresses from a specified country", "help": "IPv6 addresses from a specified country.", "label": "Geography", "name": "geography"}, {"description": "Dynamic address object for SDN", "help": "Dynamic address object for SDN.", "label": "Dynamic", "name": "dynamic"}, {"description": "Template", "help": "Template.", "label": "Template", "name": "template"}, {"description": "Range of MAC addresses", "help": "Range of MAC addresses.", "label": "Mac", "name": "mac"}, {"description": "route-tag addresses", "help": "route-tag addresses.", "label": "Route Tag", "name": "route-tag"}, {"description": "Standard IPv6 using a wildcard subnet mask", "help": "Standard IPv6 using a wildcard subnet mask.", "label": "Wildcard", "name": "wildcard"}] | None = ...,
        route_tag: int | None = ...,
        macaddr: list[dict[str, Any]] | None = ...,
        sdn: str | None = ...,
        ip6: str | None = ...,
        wildcard: str | None = ...,
        start_ip: str | None = ...,
        end_ip: str | None = ...,
        fqdn: str | None = ...,
        country: str | None = ...,
        cache_ttl: int | None = ...,
        color: int | None = ...,
        obj_id: str | None = ...,
        tagging: list[dict[str, Any]] | None = ...,
        comment: str | None = ...,
        template: str | None = ...,
        subnet_segment: list[dict[str, Any]] | None = ...,
        host_type: Literal[{"description": "Wildcard", "help": "Wildcard.", "label": "Any", "name": "any"}, {"description": "Specific host address", "help": "Specific host address.", "label": "Specific", "name": "specific"}] | None = ...,
        host: str | None = ...,
        tenant: str | None = ...,
        epg_name: str | None = ...,
        sdn_tag: str | None = ...,
        filter: str | None = ...,
        list: list[dict[str, Any]] | None = ...,
        sdn_addr_type: Literal[{"description": "Collect private addresses only", "help": "Collect private addresses only.", "label": "Private", "name": "private"}, {"description": "Collect public addresses only", "help": "Collect public addresses only.", "label": "Public", "name": "public"}, {"description": "Collect both public and private addresses", "help": "Collect both public and private addresses.", "label": "All", "name": "all"}] | None = ...,
        passive_fqdn_learning: Literal[{"description": "Disable passive learning of FQDNs", "help": "Disable passive learning of FQDNs.", "label": "Disable", "name": "disable"}, {"description": "Enable passive learning of FQDNs", "help": "Enable passive learning of FQDNs.", "label": "Enable", "name": "enable"}] | None = ...,
        fabric_object: Literal[{"description": "Object is set as a security fabric-wide global object", "help": "Object is set as a security fabric-wide global object.", "label": "Enable", "name": "enable"}, {"description": "Object is local to this security fabric member", "help": "Object is local to this security fabric member.", "label": "Disable", "name": "disable"}] | None = ...,
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
        payload_dict: Address6Payload | None = ...,
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
    "Address6",
    "Address6Payload",
]