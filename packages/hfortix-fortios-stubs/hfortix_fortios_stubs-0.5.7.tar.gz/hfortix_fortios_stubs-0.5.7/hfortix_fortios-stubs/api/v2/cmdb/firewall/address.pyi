from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class AddressPayload(TypedDict, total=False):
    """
    Type hints for firewall/address payload fields.
    
    Configure IPv4 addresses.
    
    **Related Resources:**

    Dependencies (resources this endpoint references):
        - :class:`~.system.interface.InterfaceEndpoint` (via: associated-interface, interface)
        - :class:`~.system.sdn-connector.SdnConnectorEndpoint` (via: sdn)
        - :class:`~.system.zone.ZoneEndpoint` (via: associated-interface)

    **Usage:**
        payload: AddressPayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    name: NotRequired[str]  # Address name.
    uuid: NotRequired[str]  # Universally Unique Identifier (UUID; automatically assigned 
    subnet: NotRequired[str]  # IP address and subnet mask of address.
    type: NotRequired[Literal[{"description": "Standard IPv4 address with subnet mask", "help": "Standard IPv4 address with subnet mask.", "label": "Ipmask", "name": "ipmask"}, {"description": "Range of IPv4 addresses between two specified addresses (inclusive)", "help": "Range of IPv4 addresses between two specified addresses (inclusive).", "label": "Iprange", "name": "iprange"}, {"description": "Fully Qualified Domain Name address", "help": "Fully Qualified Domain Name address.", "label": "Fqdn", "name": "fqdn"}, {"description": "IP addresses from a specified country", "help": "IP addresses from a specified country.", "label": "Geography", "name": "geography"}, {"description": "Standard IPv4 using a wildcard subnet mask", "help": "Standard IPv4 using a wildcard subnet mask.", "label": "Wildcard", "name": "wildcard"}, {"description": "Dynamic address object", "help": "Dynamic address object.", "label": "Dynamic", "name": "dynamic"}, {"description": "IP and subnet of interface", "help": "IP and subnet of interface.", "label": "Interface Subnet", "name": "interface-subnet"}, {"description": "Range of MAC addresses", "help": "Range of MAC addresses.", "label": "Mac", "name": "mac"}, {"description": "route-tag addresses", "help": "route-tag addresses.", "label": "Route Tag", "name": "route-tag"}]]  # Type of address.
    route_tag: NotRequired[int]  # route-tag address.
    sub_type: NotRequired[Literal[{"description": "SDN address", "help": "SDN address.", "label": "Sdn", "name": "sdn"}, {"description": "ClearPass SPT (System Posture Token) address", "help": "ClearPass SPT (System Posture Token) address.", "label": "Clearpass Spt", "name": "clearpass-spt"}, {"description": "FSSO address", "help": "FSSO address.", "label": "Fsso", "name": "fsso"}, {"description": "RSSO address", "help": "RSSO address.", "label": "Rsso", "name": "rsso"}, {"description": "FortiClient EMS tag", "help": "FortiClient EMS tag.", "label": "Ems Tag", "name": "ems-tag"}, {"description": "FortiVoice tag", "help": "FortiVoice tag.", "label": "Fortivoice Tag", "name": "fortivoice-tag"}, {"description": "FortiNAC tag", "help": "FortiNAC tag.", "label": "Fortinac Tag", "name": "fortinac-tag"}, {"description": "Switch Controller NAC policy tag", "help": "Switch Controller NAC policy tag.", "label": "Swc Tag", "name": "swc-tag"}, {"description": "Device address", "help": "Device address.", "label": "Device Identification", "name": "device-identification"}, {"description": "External resource", "help": "External resource.", "label": "External Resource", "name": "external-resource"}, {"description": "Tag from EOL product", "help": "Tag from EOL product.", "label": "Obsolete", "name": "obsolete"}]]  # Sub-type of address.
    clearpass_spt: NotRequired[Literal[{"description": "UNKNOWN", "help": "UNKNOWN.", "label": "Unknown", "name": "unknown"}, {"description": "HEALTHY", "help": "HEALTHY.", "label": "Healthy", "name": "healthy"}, {"description": "QUARANTINE", "help": "QUARANTINE.", "label": "Quarantine", "name": "quarantine"}, {"description": "CHECKUP", "help": "CHECKUP.", "label": "Checkup", "name": "checkup"}, {"description": "TRANSIENT", "help": "TRANSIENT.", "label": "Transient", "name": "transient"}, {"description": "INFECTED", "help": "INFECTED.", "label": "Infected", "name": "infected"}]]  # SPT (System Posture Token) value.
    macaddr: NotRequired[list[dict[str, Any]]]  # Multiple MAC address ranges.
    start_ip: NotRequired[str]  # First IP address (inclusive) in the range for the address.
    end_ip: NotRequired[str]  # Final IP address (inclusive) in the range for the address.
    fqdn: NotRequired[str]  # Fully Qualified Domain Name address.
    country: NotRequired[str]  # IP addresses associated to a specific country.
    wildcard_fqdn: NotRequired[str]  # Fully Qualified Domain Name with wildcard characters.
    cache_ttl: NotRequired[int]  # Defines the minimal TTL of individual IP addresses in FQDN c
    wildcard: NotRequired[str]  # IP address and wildcard netmask.
    sdn: NotRequired[str]  # SDN.
    fsso_group: NotRequired[list[dict[str, Any]]]  # FSSO group(s).
    sso_attribute_value: NotRequired[list[dict[str, Any]]]  # RADIUS attributes value.
    interface: str  # Name of interface whose IP address is to be used.
    tenant: NotRequired[str]  # Tenant.
    organization: NotRequired[str]  # Organization domain name (Syntax: organization/domain).
    epg_name: NotRequired[str]  # Endpoint group name.
    subnet_name: NotRequired[str]  # Subnet name.
    sdn_tag: NotRequired[str]  # SDN Tag.
    policy_group: NotRequired[str]  # Policy group name.
    obj_tag: NotRequired[str]  # Tag of dynamic address object.
    obj_type: NotRequired[Literal[{"description": "IP address", "help": "IP address.", "label": "Ip", "name": "ip"}, {"description": "MAC address", "help": "MAC address", "label": "Mac", "name": "mac"}]]  # Object type.
    tag_detection_level: NotRequired[str]  # Tag detection level of dynamic address object.
    tag_type: NotRequired[str]  # Tag type of dynamic address object.
    hw_vendor: NotRequired[str]  # Dynamic address matching hardware vendor.
    hw_model: NotRequired[str]  # Dynamic address matching hardware model.
    os: NotRequired[str]  # Dynamic address matching operating system.
    sw_version: NotRequired[str]  # Dynamic address matching software version.
    comment: NotRequired[str]  # Comment.
    associated_interface: NotRequired[str]  # Network interface associated with address.
    color: NotRequired[int]  # Color of icon on the GUI.
    filter: str  # Match criteria filter.
    sdn_addr_type: NotRequired[Literal[{"description": "Collect private addresses only", "help": "Collect private addresses only.", "label": "Private", "name": "private"}, {"description": "Collect public addresses only", "help": "Collect public addresses only.", "label": "Public", "name": "public"}, {"description": "Collect both public and private addresses", "help": "Collect both public and private addresses.", "label": "All", "name": "all"}]]  # Type of addresses to collect.
    node_ip_only: NotRequired[Literal[{"description": "Enable collection of node addresses only in Kubernetes", "help": "Enable collection of node addresses only in Kubernetes.", "label": "Enable", "name": "enable"}, {"description": "Disable collection of node addresses only in Kubernetes", "help": "Disable collection of node addresses only in Kubernetes.", "label": "Disable", "name": "disable"}]]  # Enable/disable collection of node addresses only in Kubernet
    obj_id: NotRequired[str]  # Object ID for NSX.
    list: NotRequired[list[dict[str, Any]]]  # IP address list.
    tagging: NotRequired[list[dict[str, Any]]]  # Config object tagging.
    allow_routing: NotRequired[Literal[{"description": "Enable use of this address in routing configurations", "help": "Enable use of this address in routing configurations.", "label": "Enable", "name": "enable"}, {"description": "Disable use of this address in routing configurations", "help": "Disable use of this address in routing configurations.", "label": "Disable", "name": "disable"}]]  # Enable/disable use of this address in routing configurations
    passive_fqdn_learning: NotRequired[Literal[{"description": "Disable passive learning of FQDNs", "help": "Disable passive learning of FQDNs.", "label": "Disable", "name": "disable"}, {"description": "Enable passive learning of FQDNs", "help": "Enable passive learning of FQDNs.", "label": "Enable", "name": "enable"}]]  # Enable/disable passive learning of FQDNs.  When enabled, the
    fabric_object: NotRequired[Literal[{"description": "Object is set as a security fabric-wide global object", "help": "Object is set as a security fabric-wide global object.", "label": "Enable", "name": "enable"}, {"description": "Object is local to this security fabric member", "help": "Object is local to this security fabric member.", "label": "Disable", "name": "disable"}]]  # Security Fabric global object setting.


class Address:
    """
    Configure IPv4 addresses.
    
    Path: firewall/address
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
        payload_dict: AddressPayload | None = ...,
        name: str | None = ...,
        uuid: str | None = ...,
        subnet: str | None = ...,
        type: Literal[{"description": "Standard IPv4 address with subnet mask", "help": "Standard IPv4 address with subnet mask.", "label": "Ipmask", "name": "ipmask"}, {"description": "Range of IPv4 addresses between two specified addresses (inclusive)", "help": "Range of IPv4 addresses between two specified addresses (inclusive).", "label": "Iprange", "name": "iprange"}, {"description": "Fully Qualified Domain Name address", "help": "Fully Qualified Domain Name address.", "label": "Fqdn", "name": "fqdn"}, {"description": "IP addresses from a specified country", "help": "IP addresses from a specified country.", "label": "Geography", "name": "geography"}, {"description": "Standard IPv4 using a wildcard subnet mask", "help": "Standard IPv4 using a wildcard subnet mask.", "label": "Wildcard", "name": "wildcard"}, {"description": "Dynamic address object", "help": "Dynamic address object.", "label": "Dynamic", "name": "dynamic"}, {"description": "IP and subnet of interface", "help": "IP and subnet of interface.", "label": "Interface Subnet", "name": "interface-subnet"}, {"description": "Range of MAC addresses", "help": "Range of MAC addresses.", "label": "Mac", "name": "mac"}, {"description": "route-tag addresses", "help": "route-tag addresses.", "label": "Route Tag", "name": "route-tag"}] | None = ...,
        route_tag: int | None = ...,
        sub_type: Literal[{"description": "SDN address", "help": "SDN address.", "label": "Sdn", "name": "sdn"}, {"description": "ClearPass SPT (System Posture Token) address", "help": "ClearPass SPT (System Posture Token) address.", "label": "Clearpass Spt", "name": "clearpass-spt"}, {"description": "FSSO address", "help": "FSSO address.", "label": "Fsso", "name": "fsso"}, {"description": "RSSO address", "help": "RSSO address.", "label": "Rsso", "name": "rsso"}, {"description": "FortiClient EMS tag", "help": "FortiClient EMS tag.", "label": "Ems Tag", "name": "ems-tag"}, {"description": "FortiVoice tag", "help": "FortiVoice tag.", "label": "Fortivoice Tag", "name": "fortivoice-tag"}, {"description": "FortiNAC tag", "help": "FortiNAC tag.", "label": "Fortinac Tag", "name": "fortinac-tag"}, {"description": "Switch Controller NAC policy tag", "help": "Switch Controller NAC policy tag.", "label": "Swc Tag", "name": "swc-tag"}, {"description": "Device address", "help": "Device address.", "label": "Device Identification", "name": "device-identification"}, {"description": "External resource", "help": "External resource.", "label": "External Resource", "name": "external-resource"}, {"description": "Tag from EOL product", "help": "Tag from EOL product.", "label": "Obsolete", "name": "obsolete"}] | None = ...,
        clearpass_spt: Literal[{"description": "UNKNOWN", "help": "UNKNOWN.", "label": "Unknown", "name": "unknown"}, {"description": "HEALTHY", "help": "HEALTHY.", "label": "Healthy", "name": "healthy"}, {"description": "QUARANTINE", "help": "QUARANTINE.", "label": "Quarantine", "name": "quarantine"}, {"description": "CHECKUP", "help": "CHECKUP.", "label": "Checkup", "name": "checkup"}, {"description": "TRANSIENT", "help": "TRANSIENT.", "label": "Transient", "name": "transient"}, {"description": "INFECTED", "help": "INFECTED.", "label": "Infected", "name": "infected"}] | None = ...,
        macaddr: list[dict[str, Any]] | None = ...,
        start_ip: str | None = ...,
        end_ip: str | None = ...,
        fqdn: str | None = ...,
        country: str | None = ...,
        wildcard_fqdn: str | None = ...,
        cache_ttl: int | None = ...,
        wildcard: str | None = ...,
        sdn: str | None = ...,
        fsso_group: list[dict[str, Any]] | None = ...,
        sso_attribute_value: list[dict[str, Any]] | None = ...,
        interface: str | None = ...,
        tenant: str | None = ...,
        organization: str | None = ...,
        epg_name: str | None = ...,
        subnet_name: str | None = ...,
        sdn_tag: str | None = ...,
        policy_group: str | None = ...,
        obj_tag: str | None = ...,
        obj_type: Literal[{"description": "IP address", "help": "IP address.", "label": "Ip", "name": "ip"}, {"description": "MAC address", "help": "MAC address", "label": "Mac", "name": "mac"}] | None = ...,
        tag_detection_level: str | None = ...,
        tag_type: str | None = ...,
        hw_vendor: str | None = ...,
        hw_model: str | None = ...,
        os: str | None = ...,
        sw_version: str | None = ...,
        comment: str | None = ...,
        associated_interface: str | None = ...,
        color: int | None = ...,
        filter: str | None = ...,
        sdn_addr_type: Literal[{"description": "Collect private addresses only", "help": "Collect private addresses only.", "label": "Private", "name": "private"}, {"description": "Collect public addresses only", "help": "Collect public addresses only.", "label": "Public", "name": "public"}, {"description": "Collect both public and private addresses", "help": "Collect both public and private addresses.", "label": "All", "name": "all"}] | None = ...,
        node_ip_only: Literal[{"description": "Enable collection of node addresses only in Kubernetes", "help": "Enable collection of node addresses only in Kubernetes.", "label": "Enable", "name": "enable"}, {"description": "Disable collection of node addresses only in Kubernetes", "help": "Disable collection of node addresses only in Kubernetes.", "label": "Disable", "name": "disable"}] | None = ...,
        obj_id: str | None = ...,
        list: list[dict[str, Any]] | None = ...,
        tagging: list[dict[str, Any]] | None = ...,
        allow_routing: Literal[{"description": "Enable use of this address in routing configurations", "help": "Enable use of this address in routing configurations.", "label": "Enable", "name": "enable"}, {"description": "Disable use of this address in routing configurations", "help": "Disable use of this address in routing configurations.", "label": "Disable", "name": "disable"}] | None = ...,
        passive_fqdn_learning: Literal[{"description": "Disable passive learning of FQDNs", "help": "Disable passive learning of FQDNs.", "label": "Disable", "name": "disable"}, {"description": "Enable passive learning of FQDNs", "help": "Enable passive learning of FQDNs.", "label": "Enable", "name": "enable"}] | None = ...,
        fabric_object: Literal[{"description": "Object is set as a security fabric-wide global object", "help": "Object is set as a security fabric-wide global object.", "label": "Enable", "name": "enable"}, {"description": "Object is local to this security fabric member", "help": "Object is local to this security fabric member.", "label": "Disable", "name": "disable"}] | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: AddressPayload | None = ...,
        name: str | None = ...,
        uuid: str | None = ...,
        subnet: str | None = ...,
        type: Literal[{"description": "Standard IPv4 address with subnet mask", "help": "Standard IPv4 address with subnet mask.", "label": "Ipmask", "name": "ipmask"}, {"description": "Range of IPv4 addresses between two specified addresses (inclusive)", "help": "Range of IPv4 addresses between two specified addresses (inclusive).", "label": "Iprange", "name": "iprange"}, {"description": "Fully Qualified Domain Name address", "help": "Fully Qualified Domain Name address.", "label": "Fqdn", "name": "fqdn"}, {"description": "IP addresses from a specified country", "help": "IP addresses from a specified country.", "label": "Geography", "name": "geography"}, {"description": "Standard IPv4 using a wildcard subnet mask", "help": "Standard IPv4 using a wildcard subnet mask.", "label": "Wildcard", "name": "wildcard"}, {"description": "Dynamic address object", "help": "Dynamic address object.", "label": "Dynamic", "name": "dynamic"}, {"description": "IP and subnet of interface", "help": "IP and subnet of interface.", "label": "Interface Subnet", "name": "interface-subnet"}, {"description": "Range of MAC addresses", "help": "Range of MAC addresses.", "label": "Mac", "name": "mac"}, {"description": "route-tag addresses", "help": "route-tag addresses.", "label": "Route Tag", "name": "route-tag"}] | None = ...,
        route_tag: int | None = ...,
        sub_type: Literal[{"description": "SDN address", "help": "SDN address.", "label": "Sdn", "name": "sdn"}, {"description": "ClearPass SPT (System Posture Token) address", "help": "ClearPass SPT (System Posture Token) address.", "label": "Clearpass Spt", "name": "clearpass-spt"}, {"description": "FSSO address", "help": "FSSO address.", "label": "Fsso", "name": "fsso"}, {"description": "RSSO address", "help": "RSSO address.", "label": "Rsso", "name": "rsso"}, {"description": "FortiClient EMS tag", "help": "FortiClient EMS tag.", "label": "Ems Tag", "name": "ems-tag"}, {"description": "FortiVoice tag", "help": "FortiVoice tag.", "label": "Fortivoice Tag", "name": "fortivoice-tag"}, {"description": "FortiNAC tag", "help": "FortiNAC tag.", "label": "Fortinac Tag", "name": "fortinac-tag"}, {"description": "Switch Controller NAC policy tag", "help": "Switch Controller NAC policy tag.", "label": "Swc Tag", "name": "swc-tag"}, {"description": "Device address", "help": "Device address.", "label": "Device Identification", "name": "device-identification"}, {"description": "External resource", "help": "External resource.", "label": "External Resource", "name": "external-resource"}, {"description": "Tag from EOL product", "help": "Tag from EOL product.", "label": "Obsolete", "name": "obsolete"}] | None = ...,
        clearpass_spt: Literal[{"description": "UNKNOWN", "help": "UNKNOWN.", "label": "Unknown", "name": "unknown"}, {"description": "HEALTHY", "help": "HEALTHY.", "label": "Healthy", "name": "healthy"}, {"description": "QUARANTINE", "help": "QUARANTINE.", "label": "Quarantine", "name": "quarantine"}, {"description": "CHECKUP", "help": "CHECKUP.", "label": "Checkup", "name": "checkup"}, {"description": "TRANSIENT", "help": "TRANSIENT.", "label": "Transient", "name": "transient"}, {"description": "INFECTED", "help": "INFECTED.", "label": "Infected", "name": "infected"}] | None = ...,
        macaddr: list[dict[str, Any]] | None = ...,
        start_ip: str | None = ...,
        end_ip: str | None = ...,
        fqdn: str | None = ...,
        country: str | None = ...,
        wildcard_fqdn: str | None = ...,
        cache_ttl: int | None = ...,
        wildcard: str | None = ...,
        sdn: str | None = ...,
        fsso_group: list[dict[str, Any]] | None = ...,
        sso_attribute_value: list[dict[str, Any]] | None = ...,
        interface: str | None = ...,
        tenant: str | None = ...,
        organization: str | None = ...,
        epg_name: str | None = ...,
        subnet_name: str | None = ...,
        sdn_tag: str | None = ...,
        policy_group: str | None = ...,
        obj_tag: str | None = ...,
        obj_type: Literal[{"description": "IP address", "help": "IP address.", "label": "Ip", "name": "ip"}, {"description": "MAC address", "help": "MAC address", "label": "Mac", "name": "mac"}] | None = ...,
        tag_detection_level: str | None = ...,
        tag_type: str | None = ...,
        hw_vendor: str | None = ...,
        hw_model: str | None = ...,
        os: str | None = ...,
        sw_version: str | None = ...,
        comment: str | None = ...,
        associated_interface: str | None = ...,
        color: int | None = ...,
        filter: str | None = ...,
        sdn_addr_type: Literal[{"description": "Collect private addresses only", "help": "Collect private addresses only.", "label": "Private", "name": "private"}, {"description": "Collect public addresses only", "help": "Collect public addresses only.", "label": "Public", "name": "public"}, {"description": "Collect both public and private addresses", "help": "Collect both public and private addresses.", "label": "All", "name": "all"}] | None = ...,
        node_ip_only: Literal[{"description": "Enable collection of node addresses only in Kubernetes", "help": "Enable collection of node addresses only in Kubernetes.", "label": "Enable", "name": "enable"}, {"description": "Disable collection of node addresses only in Kubernetes", "help": "Disable collection of node addresses only in Kubernetes.", "label": "Disable", "name": "disable"}] | None = ...,
        obj_id: str | None = ...,
        list: list[dict[str, Any]] | None = ...,
        tagging: list[dict[str, Any]] | None = ...,
        allow_routing: Literal[{"description": "Enable use of this address in routing configurations", "help": "Enable use of this address in routing configurations.", "label": "Enable", "name": "enable"}, {"description": "Disable use of this address in routing configurations", "help": "Disable use of this address in routing configurations.", "label": "Disable", "name": "disable"}] | None = ...,
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
        payload_dict: AddressPayload | None = ...,
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
    "Address",
    "AddressPayload",
]