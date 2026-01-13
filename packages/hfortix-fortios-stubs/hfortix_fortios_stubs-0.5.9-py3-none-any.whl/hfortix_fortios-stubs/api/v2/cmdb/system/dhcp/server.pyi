from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class ServerPayload(TypedDict, total=False):
    """
    Type hints for system/dhcp/server payload fields.
    
    Configure DHCP servers.
    
    **Related Resources:**

    Dependencies (resources this endpoint references):
        - :class:`~.system.interface.InterfaceEndpoint` (via: interface)
        - :class:`~.system.timezone.TimezoneEndpoint` (via: timezone)

    **Usage:**
        payload: ServerPayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    id: int  # ID.
    status: NotRequired[Literal[{"description": "Do not use this DHCP server configuration", "help": "Do not use this DHCP server configuration.", "label": "Disable", "name": "disable"}, {"description": "Use this DHCP server configuration", "help": "Use this DHCP server configuration.", "label": "Enable", "name": "enable"}]]  # Enable/disable this DHCP configuration.
    lease_time: NotRequired[int]  # Lease time in seconds, 0 means unlimited.
    mac_acl_default_action: NotRequired[Literal[{"description": "Allow the DHCP server to assign IP settings to clients on the MAC access control list", "help": "Allow the DHCP server to assign IP settings to clients on the MAC access control list.", "label": "Assign", "name": "assign"}, {"description": "Block the DHCP server from assigning IP settings to clients on the MAC access control list", "help": "Block the DHCP server from assigning IP settings to clients on the MAC access control list.", "label": "Block", "name": "block"}]]  # MAC access control default action (allow or block assigning 
    forticlient_on_net_status: NotRequired[Literal[{"description": "Disable FortiClient On-Net Status", "help": "Disable FortiClient On-Net Status.", "label": "Disable", "name": "disable"}, {"description": "Enable FortiClient On-Net Status", "help": "Enable FortiClient On-Net Status.", "label": "Enable", "name": "enable"}]]  # Enable/disable FortiClient-On-Net service for this DHCP serv
    dns_service: NotRequired[Literal[{"description": "IP address of the interface the DHCP server is added to becomes the client\u0027s DNS server IP address", "help": "IP address of the interface the DHCP server is added to becomes the client\u0027s DNS server IP address.", "label": "Local", "name": "local"}, {"description": "Clients are assigned the FortiGate\u0027s configured DNS servers", "help": "Clients are assigned the FortiGate\u0027s configured DNS servers.", "label": "Default", "name": "default"}, {"description": "Specify up to 3 DNS servers in the DHCP server configuration", "help": "Specify up to 3 DNS servers in the DHCP server configuration.", "label": "Specify", "name": "specify"}]]  # Options for assigning DNS servers to DHCP clients.
    dns_server1: NotRequired[str]  # DNS server 1.
    dns_server2: NotRequired[str]  # DNS server 2.
    dns_server3: NotRequired[str]  # DNS server 3.
    dns_server4: NotRequired[str]  # DNS server 4.
    wifi_ac_service: NotRequired[Literal[{"description": "Specify up to 3 WiFi Access Controllers in the DHCP server configuration", "help": "Specify up to 3 WiFi Access Controllers in the DHCP server configuration.", "label": "Specify", "name": "specify"}, {"description": "IP address of the interface the DHCP server is added to becomes the client\u0027s WiFi Access Controller IP address", "help": "IP address of the interface the DHCP server is added to becomes the client\u0027s WiFi Access Controller IP address.", "label": "Local", "name": "local"}]]  # Options for assigning WiFi access controllers to DHCP client
    wifi_ac1: NotRequired[str]  # WiFi Access Controller 1 IP address (DHCP option 138, RFC 54
    wifi_ac2: NotRequired[str]  # WiFi Access Controller 2 IP address (DHCP option 138, RFC 54
    wifi_ac3: NotRequired[str]  # WiFi Access Controller 3 IP address (DHCP option 138, RFC 54
    ntp_service: NotRequired[Literal[{"description": "IP address of the interface the DHCP server is added to becomes the client\u0027s NTP server IP address", "help": "IP address of the interface the DHCP server is added to becomes the client\u0027s NTP server IP address.", "label": "Local", "name": "local"}, {"description": "Clients are assigned the FortiGate\u0027s configured NTP servers", "help": "Clients are assigned the FortiGate\u0027s configured NTP servers.", "label": "Default", "name": "default"}, {"description": "Specify up to 3 NTP servers in the DHCP server configuration", "help": "Specify up to 3 NTP servers in the DHCP server configuration.", "label": "Specify", "name": "specify"}]]  # Options for assigning Network Time Protocol (NTP) servers to
    ntp_server1: NotRequired[str]  # NTP server 1.
    ntp_server2: NotRequired[str]  # NTP server 2.
    ntp_server3: NotRequired[str]  # NTP server 3.
    domain: NotRequired[str]  # Domain name suffix for the IP addresses that the DHCP server
    wins_server1: NotRequired[str]  # WINS server 1.
    wins_server2: NotRequired[str]  # WINS server 2.
    default_gateway: NotRequired[str]  # Default gateway IP address assigned by the DHCP server.
    next_server: NotRequired[str]  # IP address of a server (for example, a TFTP sever) that DHCP
    netmask: str  # Netmask assigned by the DHCP server.
    interface: str  # DHCP server can assign IP configurations to clients connecte
    ip_range: NotRequired[list[dict[str, Any]]]  # DHCP IP range configuration.
    timezone_option: NotRequired[Literal[{"description": "Do not set the client\u0027s time zone", "help": "Do not set the client\u0027s time zone.", "label": "Disable", "name": "disable"}, {"description": "Clients are assigned the FortiGate\u0027s configured time zone", "help": "Clients are assigned the FortiGate\u0027s configured time zone.", "label": "Default", "name": "default"}, {"description": "Specify the time zone to be assigned to DHCP clients", "help": "Specify the time zone to be assigned to DHCP clients.", "label": "Specify", "name": "specify"}]]  # Options for the DHCP server to set the client's time zone.
    timezone: str  # Select the time zone to be assigned to DHCP clients.
    tftp_server: NotRequired[list[dict[str, Any]]]  # One or more hostnames or IP addresses of the TFTP servers in
    filename: NotRequired[str]  # Name of the boot file on the TFTP server.
    options: NotRequired[list[dict[str, Any]]]  # DHCP options.
    server_type: NotRequired[Literal[{"description": "Regular DHCP service", "help": "Regular DHCP service.", "label": "Regular", "name": "regular"}, {"description": "DHCP over IPsec service", "help": "DHCP over IPsec service.", "label": "Ipsec", "name": "ipsec"}]]  # DHCP server can be a normal DHCP server or an IPsec DHCP ser
    ip_mode: NotRequired[Literal[{"description": "Use range defined by start-ip/end-ip to assign client IP", "help": "Use range defined by start-ip/end-ip to assign client IP.", "label": "Range", "name": "range"}, {"description": "Use user-group defined method to assign client IP", "help": "Use user-group defined method to assign client IP.", "label": "Usrgrp", "name": "usrgrp"}]]  # Method used to assign client IP.
    conflicted_ip_timeout: NotRequired[int]  # Time in seconds to wait after a conflicted IP address is rem
    ipsec_lease_hold: NotRequired[int]  # DHCP over IPsec leases expire this many seconds after tunnel
    auto_configuration: NotRequired[Literal[{"description": "Disable auto configuration", "help": "Disable auto configuration.", "label": "Disable", "name": "disable"}, {"description": "Enable auto configuration", "help": "Enable auto configuration.", "label": "Enable", "name": "enable"}]]  # Enable/disable auto configuration.
    dhcp_settings_from_fortiipam: NotRequired[Literal[{"description": "Disable populating of DHCP server settings from FortiIPAM", "help": "Disable populating of DHCP server settings from FortiIPAM.", "label": "Disable", "name": "disable"}, {"description": "Enable populating of DHCP server settings from FortiIPAM", "help": "Enable populating of DHCP server settings from FortiIPAM.", "label": "Enable", "name": "enable"}]]  # Enable/disable populating of DHCP server settings from Forti
    auto_managed_status: NotRequired[Literal[{"description": "Disable use of this DHCP server once this interface has been assigned an IP address from FortiIPAM", "help": "Disable use of this DHCP server once this interface has been assigned an IP address from FortiIPAM.", "label": "Disable", "name": "disable"}, {"description": "Enable use of this DHCP server once this interface has been assigned an IP address from FortiIPAM", "help": "Enable use of this DHCP server once this interface has been assigned an IP address from FortiIPAM.", "label": "Enable", "name": "enable"}]]  # Enable/disable use of this DHCP server once this interface h
    ddns_update: NotRequired[Literal[{"description": "Disable DDNS update for DHCP", "help": "Disable DDNS update for DHCP.", "label": "Disable", "name": "disable"}, {"description": "Enable DDNS update for DHCP", "help": "Enable DDNS update for DHCP.", "label": "Enable", "name": "enable"}]]  # Enable/disable DDNS update for DHCP.
    ddns_update_override: NotRequired[Literal[{"description": "Disable DDNS update override for DHCP", "help": "Disable DDNS update override for DHCP.", "label": "Disable", "name": "disable"}, {"description": "Enable DDNS update override for DHCP", "help": "Enable DDNS update override for DHCP.", "label": "Enable", "name": "enable"}]]  # Enable/disable DDNS update override for DHCP.
    ddns_server_ip: NotRequired[str]  # DDNS server IP.
    ddns_zone: NotRequired[str]  # Zone of your domain name (ex. DDNS.com).
    ddns_auth: NotRequired[Literal[{"description": "Disable DDNS authentication", "help": "Disable DDNS authentication.", "label": "Disable", "name": "disable"}, {"description": "TSIG based on RFC2845", "help": "TSIG based on RFC2845.", "label": "Tsig", "name": "tsig"}]]  # DDNS authentication mode.
    ddns_keyname: NotRequired[str]  # DDNS update key name.
    ddns_key: NotRequired[str]  # DDNS update key (base 64 encoding).
    ddns_ttl: NotRequired[int]  # TTL.
    vci_match: NotRequired[Literal[{"description": "Disable VCI matching", "help": "Disable VCI matching.", "label": "Disable", "name": "disable"}, {"description": "Enable VCI matching", "help": "Enable VCI matching.", "label": "Enable", "name": "enable"}]]  # Enable/disable vendor class identifier (VCI) matching. When 
    vci_string: NotRequired[list[dict[str, Any]]]  # One or more VCI strings in quotes separated by spaces.
    exclude_range: NotRequired[list[dict[str, Any]]]  # Exclude one or more ranges of IP addresses from being assign
    shared_subnet: NotRequired[Literal[{"description": "Disable shared subnet", "help": "Disable shared subnet.", "label": "Disable", "name": "disable"}, {"description": "Enable shared subnet", "help": "Enable shared subnet.", "label": "Enable", "name": "enable"}]]  # Enable/disable shared subnet.
    relay_agent: NotRequired[str]  # Relay agent IP.
    reserved_address: NotRequired[list[dict[str, Any]]]  # Options for the DHCP server to assign IP settings to specifi


class Server:
    """
    Configure DHCP servers.
    
    Path: system/dhcp/server
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
        payload_dict: ServerPayload | None = ...,
        id: int | None = ...,
        status: Literal[{"description": "Do not use this DHCP server configuration", "help": "Do not use this DHCP server configuration.", "label": "Disable", "name": "disable"}, {"description": "Use this DHCP server configuration", "help": "Use this DHCP server configuration.", "label": "Enable", "name": "enable"}] | None = ...,
        lease_time: int | None = ...,
        mac_acl_default_action: Literal[{"description": "Allow the DHCP server to assign IP settings to clients on the MAC access control list", "help": "Allow the DHCP server to assign IP settings to clients on the MAC access control list.", "label": "Assign", "name": "assign"}, {"description": "Block the DHCP server from assigning IP settings to clients on the MAC access control list", "help": "Block the DHCP server from assigning IP settings to clients on the MAC access control list.", "label": "Block", "name": "block"}] | None = ...,
        forticlient_on_net_status: Literal[{"description": "Disable FortiClient On-Net Status", "help": "Disable FortiClient On-Net Status.", "label": "Disable", "name": "disable"}, {"description": "Enable FortiClient On-Net Status", "help": "Enable FortiClient On-Net Status.", "label": "Enable", "name": "enable"}] | None = ...,
        dns_service: Literal[{"description": "IP address of the interface the DHCP server is added to becomes the client\u0027s DNS server IP address", "help": "IP address of the interface the DHCP server is added to becomes the client\u0027s DNS server IP address.", "label": "Local", "name": "local"}, {"description": "Clients are assigned the FortiGate\u0027s configured DNS servers", "help": "Clients are assigned the FortiGate\u0027s configured DNS servers.", "label": "Default", "name": "default"}, {"description": "Specify up to 3 DNS servers in the DHCP server configuration", "help": "Specify up to 3 DNS servers in the DHCP server configuration.", "label": "Specify", "name": "specify"}] | None = ...,
        dns_server1: str | None = ...,
        dns_server2: str | None = ...,
        dns_server3: str | None = ...,
        dns_server4: str | None = ...,
        wifi_ac_service: Literal[{"description": "Specify up to 3 WiFi Access Controllers in the DHCP server configuration", "help": "Specify up to 3 WiFi Access Controllers in the DHCP server configuration.", "label": "Specify", "name": "specify"}, {"description": "IP address of the interface the DHCP server is added to becomes the client\u0027s WiFi Access Controller IP address", "help": "IP address of the interface the DHCP server is added to becomes the client\u0027s WiFi Access Controller IP address.", "label": "Local", "name": "local"}] | None = ...,
        wifi_ac1: str | None = ...,
        wifi_ac2: str | None = ...,
        wifi_ac3: str | None = ...,
        ntp_service: Literal[{"description": "IP address of the interface the DHCP server is added to becomes the client\u0027s NTP server IP address", "help": "IP address of the interface the DHCP server is added to becomes the client\u0027s NTP server IP address.", "label": "Local", "name": "local"}, {"description": "Clients are assigned the FortiGate\u0027s configured NTP servers", "help": "Clients are assigned the FortiGate\u0027s configured NTP servers.", "label": "Default", "name": "default"}, {"description": "Specify up to 3 NTP servers in the DHCP server configuration", "help": "Specify up to 3 NTP servers in the DHCP server configuration.", "label": "Specify", "name": "specify"}] | None = ...,
        ntp_server1: str | None = ...,
        ntp_server2: str | None = ...,
        ntp_server3: str | None = ...,
        domain: str | None = ...,
        wins_server1: str | None = ...,
        wins_server2: str | None = ...,
        default_gateway: str | None = ...,
        next_server: str | None = ...,
        netmask: str | None = ...,
        interface: str | None = ...,
        ip_range: list[dict[str, Any]] | None = ...,
        timezone_option: Literal[{"description": "Do not set the client\u0027s time zone", "help": "Do not set the client\u0027s time zone.", "label": "Disable", "name": "disable"}, {"description": "Clients are assigned the FortiGate\u0027s configured time zone", "help": "Clients are assigned the FortiGate\u0027s configured time zone.", "label": "Default", "name": "default"}, {"description": "Specify the time zone to be assigned to DHCP clients", "help": "Specify the time zone to be assigned to DHCP clients.", "label": "Specify", "name": "specify"}] | None = ...,
        timezone: str | None = ...,
        tftp_server: list[dict[str, Any]] | None = ...,
        filename: str | None = ...,
        options: list[dict[str, Any]] | None = ...,
        server_type: Literal[{"description": "Regular DHCP service", "help": "Regular DHCP service.", "label": "Regular", "name": "regular"}, {"description": "DHCP over IPsec service", "help": "DHCP over IPsec service.", "label": "Ipsec", "name": "ipsec"}] | None = ...,
        ip_mode: Literal[{"description": "Use range defined by start-ip/end-ip to assign client IP", "help": "Use range defined by start-ip/end-ip to assign client IP.", "label": "Range", "name": "range"}, {"description": "Use user-group defined method to assign client IP", "help": "Use user-group defined method to assign client IP.", "label": "Usrgrp", "name": "usrgrp"}] | None = ...,
        conflicted_ip_timeout: int | None = ...,
        ipsec_lease_hold: int | None = ...,
        auto_configuration: Literal[{"description": "Disable auto configuration", "help": "Disable auto configuration.", "label": "Disable", "name": "disable"}, {"description": "Enable auto configuration", "help": "Enable auto configuration.", "label": "Enable", "name": "enable"}] | None = ...,
        dhcp_settings_from_fortiipam: Literal[{"description": "Disable populating of DHCP server settings from FortiIPAM", "help": "Disable populating of DHCP server settings from FortiIPAM.", "label": "Disable", "name": "disable"}, {"description": "Enable populating of DHCP server settings from FortiIPAM", "help": "Enable populating of DHCP server settings from FortiIPAM.", "label": "Enable", "name": "enable"}] | None = ...,
        auto_managed_status: Literal[{"description": "Disable use of this DHCP server once this interface has been assigned an IP address from FortiIPAM", "help": "Disable use of this DHCP server once this interface has been assigned an IP address from FortiIPAM.", "label": "Disable", "name": "disable"}, {"description": "Enable use of this DHCP server once this interface has been assigned an IP address from FortiIPAM", "help": "Enable use of this DHCP server once this interface has been assigned an IP address from FortiIPAM.", "label": "Enable", "name": "enable"}] | None = ...,
        ddns_update: Literal[{"description": "Disable DDNS update for DHCP", "help": "Disable DDNS update for DHCP.", "label": "Disable", "name": "disable"}, {"description": "Enable DDNS update for DHCP", "help": "Enable DDNS update for DHCP.", "label": "Enable", "name": "enable"}] | None = ...,
        ddns_update_override: Literal[{"description": "Disable DDNS update override for DHCP", "help": "Disable DDNS update override for DHCP.", "label": "Disable", "name": "disable"}, {"description": "Enable DDNS update override for DHCP", "help": "Enable DDNS update override for DHCP.", "label": "Enable", "name": "enable"}] | None = ...,
        ddns_server_ip: str | None = ...,
        ddns_zone: str | None = ...,
        ddns_auth: Literal[{"description": "Disable DDNS authentication", "help": "Disable DDNS authentication.", "label": "Disable", "name": "disable"}, {"description": "TSIG based on RFC2845", "help": "TSIG based on RFC2845.", "label": "Tsig", "name": "tsig"}] | None = ...,
        ddns_keyname: str | None = ...,
        ddns_key: str | None = ...,
        ddns_ttl: int | None = ...,
        vci_match: Literal[{"description": "Disable VCI matching", "help": "Disable VCI matching.", "label": "Disable", "name": "disable"}, {"description": "Enable VCI matching", "help": "Enable VCI matching.", "label": "Enable", "name": "enable"}] | None = ...,
        vci_string: list[dict[str, Any]] | None = ...,
        exclude_range: list[dict[str, Any]] | None = ...,
        shared_subnet: Literal[{"description": "Disable shared subnet", "help": "Disable shared subnet.", "label": "Disable", "name": "disable"}, {"description": "Enable shared subnet", "help": "Enable shared subnet.", "label": "Enable", "name": "enable"}] | None = ...,
        relay_agent: str | None = ...,
        reserved_address: list[dict[str, Any]] | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: ServerPayload | None = ...,
        id: int | None = ...,
        status: Literal[{"description": "Do not use this DHCP server configuration", "help": "Do not use this DHCP server configuration.", "label": "Disable", "name": "disable"}, {"description": "Use this DHCP server configuration", "help": "Use this DHCP server configuration.", "label": "Enable", "name": "enable"}] | None = ...,
        lease_time: int | None = ...,
        mac_acl_default_action: Literal[{"description": "Allow the DHCP server to assign IP settings to clients on the MAC access control list", "help": "Allow the DHCP server to assign IP settings to clients on the MAC access control list.", "label": "Assign", "name": "assign"}, {"description": "Block the DHCP server from assigning IP settings to clients on the MAC access control list", "help": "Block the DHCP server from assigning IP settings to clients on the MAC access control list.", "label": "Block", "name": "block"}] | None = ...,
        forticlient_on_net_status: Literal[{"description": "Disable FortiClient On-Net Status", "help": "Disable FortiClient On-Net Status.", "label": "Disable", "name": "disable"}, {"description": "Enable FortiClient On-Net Status", "help": "Enable FortiClient On-Net Status.", "label": "Enable", "name": "enable"}] | None = ...,
        dns_service: Literal[{"description": "IP address of the interface the DHCP server is added to becomes the client\u0027s DNS server IP address", "help": "IP address of the interface the DHCP server is added to becomes the client\u0027s DNS server IP address.", "label": "Local", "name": "local"}, {"description": "Clients are assigned the FortiGate\u0027s configured DNS servers", "help": "Clients are assigned the FortiGate\u0027s configured DNS servers.", "label": "Default", "name": "default"}, {"description": "Specify up to 3 DNS servers in the DHCP server configuration", "help": "Specify up to 3 DNS servers in the DHCP server configuration.", "label": "Specify", "name": "specify"}] | None = ...,
        dns_server1: str | None = ...,
        dns_server2: str | None = ...,
        dns_server3: str | None = ...,
        dns_server4: str | None = ...,
        wifi_ac_service: Literal[{"description": "Specify up to 3 WiFi Access Controllers in the DHCP server configuration", "help": "Specify up to 3 WiFi Access Controllers in the DHCP server configuration.", "label": "Specify", "name": "specify"}, {"description": "IP address of the interface the DHCP server is added to becomes the client\u0027s WiFi Access Controller IP address", "help": "IP address of the interface the DHCP server is added to becomes the client\u0027s WiFi Access Controller IP address.", "label": "Local", "name": "local"}] | None = ...,
        wifi_ac1: str | None = ...,
        wifi_ac2: str | None = ...,
        wifi_ac3: str | None = ...,
        ntp_service: Literal[{"description": "IP address of the interface the DHCP server is added to becomes the client\u0027s NTP server IP address", "help": "IP address of the interface the DHCP server is added to becomes the client\u0027s NTP server IP address.", "label": "Local", "name": "local"}, {"description": "Clients are assigned the FortiGate\u0027s configured NTP servers", "help": "Clients are assigned the FortiGate\u0027s configured NTP servers.", "label": "Default", "name": "default"}, {"description": "Specify up to 3 NTP servers in the DHCP server configuration", "help": "Specify up to 3 NTP servers in the DHCP server configuration.", "label": "Specify", "name": "specify"}] | None = ...,
        ntp_server1: str | None = ...,
        ntp_server2: str | None = ...,
        ntp_server3: str | None = ...,
        domain: str | None = ...,
        wins_server1: str | None = ...,
        wins_server2: str | None = ...,
        default_gateway: str | None = ...,
        next_server: str | None = ...,
        netmask: str | None = ...,
        interface: str | None = ...,
        ip_range: list[dict[str, Any]] | None = ...,
        timezone_option: Literal[{"description": "Do not set the client\u0027s time zone", "help": "Do not set the client\u0027s time zone.", "label": "Disable", "name": "disable"}, {"description": "Clients are assigned the FortiGate\u0027s configured time zone", "help": "Clients are assigned the FortiGate\u0027s configured time zone.", "label": "Default", "name": "default"}, {"description": "Specify the time zone to be assigned to DHCP clients", "help": "Specify the time zone to be assigned to DHCP clients.", "label": "Specify", "name": "specify"}] | None = ...,
        timezone: str | None = ...,
        tftp_server: list[dict[str, Any]] | None = ...,
        filename: str | None = ...,
        options: list[dict[str, Any]] | None = ...,
        server_type: Literal[{"description": "Regular DHCP service", "help": "Regular DHCP service.", "label": "Regular", "name": "regular"}, {"description": "DHCP over IPsec service", "help": "DHCP over IPsec service.", "label": "Ipsec", "name": "ipsec"}] | None = ...,
        ip_mode: Literal[{"description": "Use range defined by start-ip/end-ip to assign client IP", "help": "Use range defined by start-ip/end-ip to assign client IP.", "label": "Range", "name": "range"}, {"description": "Use user-group defined method to assign client IP", "help": "Use user-group defined method to assign client IP.", "label": "Usrgrp", "name": "usrgrp"}] | None = ...,
        conflicted_ip_timeout: int | None = ...,
        ipsec_lease_hold: int | None = ...,
        auto_configuration: Literal[{"description": "Disable auto configuration", "help": "Disable auto configuration.", "label": "Disable", "name": "disable"}, {"description": "Enable auto configuration", "help": "Enable auto configuration.", "label": "Enable", "name": "enable"}] | None = ...,
        dhcp_settings_from_fortiipam: Literal[{"description": "Disable populating of DHCP server settings from FortiIPAM", "help": "Disable populating of DHCP server settings from FortiIPAM.", "label": "Disable", "name": "disable"}, {"description": "Enable populating of DHCP server settings from FortiIPAM", "help": "Enable populating of DHCP server settings from FortiIPAM.", "label": "Enable", "name": "enable"}] | None = ...,
        auto_managed_status: Literal[{"description": "Disable use of this DHCP server once this interface has been assigned an IP address from FortiIPAM", "help": "Disable use of this DHCP server once this interface has been assigned an IP address from FortiIPAM.", "label": "Disable", "name": "disable"}, {"description": "Enable use of this DHCP server once this interface has been assigned an IP address from FortiIPAM", "help": "Enable use of this DHCP server once this interface has been assigned an IP address from FortiIPAM.", "label": "Enable", "name": "enable"}] | None = ...,
        ddns_update: Literal[{"description": "Disable DDNS update for DHCP", "help": "Disable DDNS update for DHCP.", "label": "Disable", "name": "disable"}, {"description": "Enable DDNS update for DHCP", "help": "Enable DDNS update for DHCP.", "label": "Enable", "name": "enable"}] | None = ...,
        ddns_update_override: Literal[{"description": "Disable DDNS update override for DHCP", "help": "Disable DDNS update override for DHCP.", "label": "Disable", "name": "disable"}, {"description": "Enable DDNS update override for DHCP", "help": "Enable DDNS update override for DHCP.", "label": "Enable", "name": "enable"}] | None = ...,
        ddns_server_ip: str | None = ...,
        ddns_zone: str | None = ...,
        ddns_auth: Literal[{"description": "Disable DDNS authentication", "help": "Disable DDNS authentication.", "label": "Disable", "name": "disable"}, {"description": "TSIG based on RFC2845", "help": "TSIG based on RFC2845.", "label": "Tsig", "name": "tsig"}] | None = ...,
        ddns_keyname: str | None = ...,
        ddns_key: str | None = ...,
        ddns_ttl: int | None = ...,
        vci_match: Literal[{"description": "Disable VCI matching", "help": "Disable VCI matching.", "label": "Disable", "name": "disable"}, {"description": "Enable VCI matching", "help": "Enable VCI matching.", "label": "Enable", "name": "enable"}] | None = ...,
        vci_string: list[dict[str, Any]] | None = ...,
        exclude_range: list[dict[str, Any]] | None = ...,
        shared_subnet: Literal[{"description": "Disable shared subnet", "help": "Disable shared subnet.", "label": "Disable", "name": "disable"}, {"description": "Enable shared subnet", "help": "Enable shared subnet.", "label": "Enable", "name": "enable"}] | None = ...,
        relay_agent: str | None = ...,
        reserved_address: list[dict[str, Any]] | None = ...,
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