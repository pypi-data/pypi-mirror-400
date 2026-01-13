from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class CustomPayload(TypedDict, total=False):
    """
    Type hints for firewall/service/custom payload fields.
    
    Configure custom services.
    
    **Related Resources:**

    Dependencies (resources this endpoint references):
        - :class:`~.firewall.service.category.CategoryEndpoint` (via: category)

    **Usage:**
        payload: CustomPayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    name: NotRequired[str]  # Custom service name.
    uuid: NotRequired[str]  # Universally Unique Identifier (UUID; automatically assigned 
    proxy: NotRequired[Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]]  # Enable/disable web proxy service.
    category: NotRequired[str]  # Service category.
    protocol: NotRequired[Literal[{"description": "TCP, UDP, UDP-Lite and SCTP", "help": "TCP, UDP, UDP-Lite and SCTP.", "label": "Tcp/Udp/Udp Lite/Sctp", "name": "TCP/UDP/UDP-Lite/SCTP"}, {"description": "ICMP", "help": "ICMP.", "label": "Icmp", "name": "ICMP"}, {"description": "ICMP6", "help": "ICMP6.", "label": "Icmp6", "name": "ICMP6"}, {"description": "IP", "help": "IP.", "label": "Ip", "name": "IP"}, {"description": "HTTP - for web proxy", "help": "HTTP - for web proxy.", "label": "Http", "name": "HTTP"}, {"description": "FTP - for web proxy", "help": "FTP - for web proxy.", "label": "Ftp", "name": "FTP"}, {"description": "Connect - for web proxy", "help": "Connect - for web proxy.", "label": "Connect", "name": "CONNECT"}, {"description": "Socks TCP - for web proxy", "help": "Socks TCP - for web proxy.", "label": "Socks Tcp", "name": "SOCKS-TCP"}, {"description": "Socks UDP - for web proxy", "help": "Socks UDP - for web proxy.", "label": "Socks Udp", "name": "SOCKS-UDP"}, {"description": "All - for web proxy", "help": "All - for web proxy.", "label": "All", "name": "ALL"}]]  # Protocol type based on IANA numbers.
    helper: NotRequired[Literal[{"description": "Automatically select helper based on protocol and port", "help": "Automatically select helper based on protocol and port.", "label": "Auto", "name": "auto"}, {"description": "Disable helper", "help": "Disable helper.", "label": "Disable", "name": "disable"}, {"description": "FTP", "help": "FTP.", "label": "Ftp", "name": "ftp"}, {"description": "TFTP", "help": "TFTP.", "label": "Tftp", "name": "tftp"}, {"description": "RAS", "help": "RAS.", "label": "Ras", "name": "ras"}, {"description": "H323", "help": "H323.", "label": "H323", "name": "h323"}, {"description": "TNS", "help": "TNS.", "label": "Tns", "name": "tns"}, {"description": "MMS", "help": "MMS.", "label": "Mms", "name": "mms"}, {"description": "SIP", "help": "SIP.", "label": "Sip", "name": "sip"}, {"description": "PPTP", "help": "PPTP.", "label": "Pptp", "name": "pptp"}, {"description": "RTSP", "help": "RTSP.", "label": "Rtsp", "name": "rtsp"}, {"description": "DNS UDP", "help": "DNS UDP.", "label": "Dns Udp", "name": "dns-udp"}, {"description": "DNS TCP", "help": "DNS TCP.", "label": "Dns Tcp", "name": "dns-tcp"}, {"description": "PMAP", "help": "PMAP.", "label": "Pmap", "name": "pmap"}, {"description": "RSH", "help": "RSH.", "label": "Rsh", "name": "rsh"}, {"description": "DCERPC", "help": "DCERPC.", "label": "Dcerpc", "name": "dcerpc"}, {"description": "MGCP", "help": "MGCP.", "label": "Mgcp", "name": "mgcp"}]]  # Helper name.
    iprange: NotRequired[str]  # Start and end of the IP range associated with service.
    fqdn: NotRequired[str]  # Fully qualified domain name.
    protocol_number: NotRequired[int]  # IP protocol number.
    icmptype: NotRequired[int]  # ICMP type.
    icmpcode: NotRequired[int]  # ICMP code.
    tcp_portrange: NotRequired[str]  # Multiple TCP port ranges.
    udp_portrange: NotRequired[str]  # Multiple UDP port ranges.
    udplite_portrange: NotRequired[str]  # Multiple UDP-Lite port ranges.
    sctp_portrange: NotRequired[str]  # Multiple SCTP port ranges.
    tcp_halfclose_timer: NotRequired[int]  # Wait time to close a TCP session waiting for an unanswered F
    tcp_halfopen_timer: NotRequired[int]  # Wait time to close a TCP session waiting for an unanswered o
    tcp_timewait_timer: NotRequired[int]  # Set the length of the TCP TIME-WAIT state in seconds (1 - 30
    tcp_rst_timer: NotRequired[int]  # Set the length of the TCP CLOSE state in seconds (5 - 300 se
    udp_idle_timer: NotRequired[int]  # Number of seconds before an idle UDP/UDP-Lite connection tim
    session_ttl: NotRequired[str]  # Session TTL (300 - 2764800, 0 = default).
    check_reset_range: NotRequired[Literal[{"description": "Disable RST range check", "help": "Disable RST range check.", "label": "Disable", "name": "disable"}, {"description": "Check RST range strictly", "help": "Check RST range strictly.", "label": "Strict", "name": "strict"}, {"description": "Using system default setting", "help": "Using system default setting.", "label": "Default", "name": "default"}]]  # Configure the type of ICMP error message verification.
    comment: NotRequired[str]  # Comment.
    color: NotRequired[int]  # Color of icon on the GUI.
    app_service_type: NotRequired[Literal[{"description": "Disable application type", "help": "Disable application type.", "label": "Disable", "name": "disable"}, {"description": "Application ID", "help": "Application ID.", "label": "App Id", "name": "app-id"}, {"description": "Applicatin category", "help": "Applicatin category.", "label": "App Category", "name": "app-category"}]]  # Application service type.
    app_category: NotRequired[list[dict[str, Any]]]  # Application category ID.
    application: NotRequired[list[dict[str, Any]]]  # Application ID.
    fabric_object: NotRequired[Literal[{"description": "Object is set as a security fabric-wide global object", "help": "Object is set as a security fabric-wide global object.", "label": "Enable", "name": "enable"}, {"description": "Object is local to this security fabric member", "help": "Object is local to this security fabric member.", "label": "Disable", "name": "disable"}]]  # Security Fabric global object setting.


class Custom:
    """
    Configure custom services.
    
    Path: firewall/service/custom
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
        payload_dict: CustomPayload | None = ...,
        name: str | None = ...,
        uuid: str | None = ...,
        proxy: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        category: str | None = ...,
        protocol: Literal[{"description": "TCP, UDP, UDP-Lite and SCTP", "help": "TCP, UDP, UDP-Lite and SCTP.", "label": "Tcp/Udp/Udp Lite/Sctp", "name": "TCP/UDP/UDP-Lite/SCTP"}, {"description": "ICMP", "help": "ICMP.", "label": "Icmp", "name": "ICMP"}, {"description": "ICMP6", "help": "ICMP6.", "label": "Icmp6", "name": "ICMP6"}, {"description": "IP", "help": "IP.", "label": "Ip", "name": "IP"}, {"description": "HTTP - for web proxy", "help": "HTTP - for web proxy.", "label": "Http", "name": "HTTP"}, {"description": "FTP - for web proxy", "help": "FTP - for web proxy.", "label": "Ftp", "name": "FTP"}, {"description": "Connect - for web proxy", "help": "Connect - for web proxy.", "label": "Connect", "name": "CONNECT"}, {"description": "Socks TCP - for web proxy", "help": "Socks TCP - for web proxy.", "label": "Socks Tcp", "name": "SOCKS-TCP"}, {"description": "Socks UDP - for web proxy", "help": "Socks UDP - for web proxy.", "label": "Socks Udp", "name": "SOCKS-UDP"}, {"description": "All - for web proxy", "help": "All - for web proxy.", "label": "All", "name": "ALL"}] | None = ...,
        helper: Literal[{"description": "Automatically select helper based on protocol and port", "help": "Automatically select helper based on protocol and port.", "label": "Auto", "name": "auto"}, {"description": "Disable helper", "help": "Disable helper.", "label": "Disable", "name": "disable"}, {"description": "FTP", "help": "FTP.", "label": "Ftp", "name": "ftp"}, {"description": "TFTP", "help": "TFTP.", "label": "Tftp", "name": "tftp"}, {"description": "RAS", "help": "RAS.", "label": "Ras", "name": "ras"}, {"description": "H323", "help": "H323.", "label": "H323", "name": "h323"}, {"description": "TNS", "help": "TNS.", "label": "Tns", "name": "tns"}, {"description": "MMS", "help": "MMS.", "label": "Mms", "name": "mms"}, {"description": "SIP", "help": "SIP.", "label": "Sip", "name": "sip"}, {"description": "PPTP", "help": "PPTP.", "label": "Pptp", "name": "pptp"}, {"description": "RTSP", "help": "RTSP.", "label": "Rtsp", "name": "rtsp"}, {"description": "DNS UDP", "help": "DNS UDP.", "label": "Dns Udp", "name": "dns-udp"}, {"description": "DNS TCP", "help": "DNS TCP.", "label": "Dns Tcp", "name": "dns-tcp"}, {"description": "PMAP", "help": "PMAP.", "label": "Pmap", "name": "pmap"}, {"description": "RSH", "help": "RSH.", "label": "Rsh", "name": "rsh"}, {"description": "DCERPC", "help": "DCERPC.", "label": "Dcerpc", "name": "dcerpc"}, {"description": "MGCP", "help": "MGCP.", "label": "Mgcp", "name": "mgcp"}] | None = ...,
        iprange: str | None = ...,
        fqdn: str | None = ...,
        protocol_number: int | None = ...,
        icmptype: int | None = ...,
        icmpcode: int | None = ...,
        tcp_portrange: str | None = ...,
        udp_portrange: str | None = ...,
        udplite_portrange: str | None = ...,
        sctp_portrange: str | None = ...,
        tcp_halfclose_timer: int | None = ...,
        tcp_halfopen_timer: int | None = ...,
        tcp_timewait_timer: int | None = ...,
        tcp_rst_timer: int | None = ...,
        udp_idle_timer: int | None = ...,
        session_ttl: str | None = ...,
        check_reset_range: Literal[{"description": "Disable RST range check", "help": "Disable RST range check.", "label": "Disable", "name": "disable"}, {"description": "Check RST range strictly", "help": "Check RST range strictly.", "label": "Strict", "name": "strict"}, {"description": "Using system default setting", "help": "Using system default setting.", "label": "Default", "name": "default"}] | None = ...,
        comment: str | None = ...,
        color: int | None = ...,
        app_service_type: Literal[{"description": "Disable application type", "help": "Disable application type.", "label": "Disable", "name": "disable"}, {"description": "Application ID", "help": "Application ID.", "label": "App Id", "name": "app-id"}, {"description": "Applicatin category", "help": "Applicatin category.", "label": "App Category", "name": "app-category"}] | None = ...,
        app_category: list[dict[str, Any]] | None = ...,
        application: list[dict[str, Any]] | None = ...,
        fabric_object: Literal[{"description": "Object is set as a security fabric-wide global object", "help": "Object is set as a security fabric-wide global object.", "label": "Enable", "name": "enable"}, {"description": "Object is local to this security fabric member", "help": "Object is local to this security fabric member.", "label": "Disable", "name": "disable"}] | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: CustomPayload | None = ...,
        name: str | None = ...,
        uuid: str | None = ...,
        proxy: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        category: str | None = ...,
        protocol: Literal[{"description": "TCP, UDP, UDP-Lite and SCTP", "help": "TCP, UDP, UDP-Lite and SCTP.", "label": "Tcp/Udp/Udp Lite/Sctp", "name": "TCP/UDP/UDP-Lite/SCTP"}, {"description": "ICMP", "help": "ICMP.", "label": "Icmp", "name": "ICMP"}, {"description": "ICMP6", "help": "ICMP6.", "label": "Icmp6", "name": "ICMP6"}, {"description": "IP", "help": "IP.", "label": "Ip", "name": "IP"}, {"description": "HTTP - for web proxy", "help": "HTTP - for web proxy.", "label": "Http", "name": "HTTP"}, {"description": "FTP - for web proxy", "help": "FTP - for web proxy.", "label": "Ftp", "name": "FTP"}, {"description": "Connect - for web proxy", "help": "Connect - for web proxy.", "label": "Connect", "name": "CONNECT"}, {"description": "Socks TCP - for web proxy", "help": "Socks TCP - for web proxy.", "label": "Socks Tcp", "name": "SOCKS-TCP"}, {"description": "Socks UDP - for web proxy", "help": "Socks UDP - for web proxy.", "label": "Socks Udp", "name": "SOCKS-UDP"}, {"description": "All - for web proxy", "help": "All - for web proxy.", "label": "All", "name": "ALL"}] | None = ...,
        helper: Literal[{"description": "Automatically select helper based on protocol and port", "help": "Automatically select helper based on protocol and port.", "label": "Auto", "name": "auto"}, {"description": "Disable helper", "help": "Disable helper.", "label": "Disable", "name": "disable"}, {"description": "FTP", "help": "FTP.", "label": "Ftp", "name": "ftp"}, {"description": "TFTP", "help": "TFTP.", "label": "Tftp", "name": "tftp"}, {"description": "RAS", "help": "RAS.", "label": "Ras", "name": "ras"}, {"description": "H323", "help": "H323.", "label": "H323", "name": "h323"}, {"description": "TNS", "help": "TNS.", "label": "Tns", "name": "tns"}, {"description": "MMS", "help": "MMS.", "label": "Mms", "name": "mms"}, {"description": "SIP", "help": "SIP.", "label": "Sip", "name": "sip"}, {"description": "PPTP", "help": "PPTP.", "label": "Pptp", "name": "pptp"}, {"description": "RTSP", "help": "RTSP.", "label": "Rtsp", "name": "rtsp"}, {"description": "DNS UDP", "help": "DNS UDP.", "label": "Dns Udp", "name": "dns-udp"}, {"description": "DNS TCP", "help": "DNS TCP.", "label": "Dns Tcp", "name": "dns-tcp"}, {"description": "PMAP", "help": "PMAP.", "label": "Pmap", "name": "pmap"}, {"description": "RSH", "help": "RSH.", "label": "Rsh", "name": "rsh"}, {"description": "DCERPC", "help": "DCERPC.", "label": "Dcerpc", "name": "dcerpc"}, {"description": "MGCP", "help": "MGCP.", "label": "Mgcp", "name": "mgcp"}] | None = ...,
        iprange: str | None = ...,
        fqdn: str | None = ...,
        protocol_number: int | None = ...,
        icmptype: int | None = ...,
        icmpcode: int | None = ...,
        tcp_portrange: str | None = ...,
        udp_portrange: str | None = ...,
        udplite_portrange: str | None = ...,
        sctp_portrange: str | None = ...,
        tcp_halfclose_timer: int | None = ...,
        tcp_halfopen_timer: int | None = ...,
        tcp_timewait_timer: int | None = ...,
        tcp_rst_timer: int | None = ...,
        udp_idle_timer: int | None = ...,
        session_ttl: str | None = ...,
        check_reset_range: Literal[{"description": "Disable RST range check", "help": "Disable RST range check.", "label": "Disable", "name": "disable"}, {"description": "Check RST range strictly", "help": "Check RST range strictly.", "label": "Strict", "name": "strict"}, {"description": "Using system default setting", "help": "Using system default setting.", "label": "Default", "name": "default"}] | None = ...,
        comment: str | None = ...,
        color: int | None = ...,
        app_service_type: Literal[{"description": "Disable application type", "help": "Disable application type.", "label": "Disable", "name": "disable"}, {"description": "Application ID", "help": "Application ID.", "label": "App Id", "name": "app-id"}, {"description": "Applicatin category", "help": "Applicatin category.", "label": "App Category", "name": "app-category"}] | None = ...,
        app_category: list[dict[str, Any]] | None = ...,
        application: list[dict[str, Any]] | None = ...,
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
        payload_dict: CustomPayload | None = ...,
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
    "Custom",
    "CustomPayload",
]