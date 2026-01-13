from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class DdnsPayload(TypedDict, total=False):
    """
    Type hints for system/ddns payload fields.
    
    Configure DDNS.
    
    **Related Resources:**

    Dependencies (resources this endpoint references):
        - :class:`~.certificate.local.LocalEndpoint` (via: ssl-certificate)

    **Usage:**
        payload: DdnsPayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    ddnsid: NotRequired[int]  # DDNS ID.
    ddns_server: Literal[{"help": "members.dyndns.org and dnsalias.com", "label": "Dyndns.Org", "name": "dyndns.org"}, {"help": "www.dyns.net", "label": "Dyns.Net", "name": "dyns.net"}, {"help": "rh.tzo.com", "label": "Tzo.Com", "name": "tzo.com"}, {"help": "Peanut Hull", "label": "Vavic.Com", "name": "vavic.com"}, {"help": "dipdnsserver.dipdns.com", "label": "Dipdns.Net", "name": "dipdns.net"}, {"help": "ip.todayisp.com", "label": "Now.Net.Cn", "name": "now.net.cn"}, {"help": "members.dhs.org", "label": "Dhs.Org", "name": "dhs.org"}, {"help": "members.easydns.com", "label": "Easydns.Com", "name": "easydns.com"}, {"help": "Generic DDNS based on RFC2136.", "label": "Genericddns", "name": "genericDDNS"}, {"description": "FortiGuard DDNS service", "help": "FortiGuard DDNS service.", "label": "Fortiguardddns", "name": "FortiGuardDDNS"}, {"help": "dynupdate.no-ip.com", "label": "Noip.Com", "name": "noip.com"}]  # Select a DDNS service provider.
    addr_type: NotRequired[Literal[{"description": "Use IPv4 address of the interface", "help": "Use IPv4 address of the interface.", "label": "Ipv4", "name": "ipv4"}, {"description": "Use IPv6 address of the interface", "help": "Use IPv6 address of the interface.", "label": "Ipv6", "name": "ipv6"}]]  # Address type of interface address in DDNS update.
    server_type: NotRequired[Literal[{"description": "Use IPv4 addressing", "help": "Use IPv4 addressing.", "label": "Ipv4", "name": "ipv4"}, {"description": "Use IPv6 addressing", "help": "Use IPv6 addressing.", "label": "Ipv6", "name": "ipv6"}]]  # Address type of the DDNS server.
    ddns_server_addr: NotRequired[list[dict[str, Any]]]  # Generic DDNS server IP/FQDN list.
    ddns_zone: NotRequired[str]  # Zone of your domain name (for example, DDNS.com).
    ddns_ttl: NotRequired[int]  # Time-to-live for DDNS packets.
    ddns_auth: NotRequired[Literal[{"description": "Disable DDNS authentication", "help": "Disable DDNS authentication.", "label": "Disable", "name": "disable"}, {"description": "Enable TSIG authentication based on RFC2845", "help": "Enable TSIG authentication based on RFC2845.", "label": "Tsig", "name": "tsig"}]]  # Enable/disable TSIG authentication for your DDNS server.
    ddns_keyname: NotRequired[str]  # DDNS update key name.
    ddns_key: NotRequired[str]  # DDNS update key (base 64 encoding).
    ddns_domain: NotRequired[str]  # Your fully qualified domain name. For example, yourname.ddns
    ddns_username: NotRequired[str]  # DDNS user name.
    ddns_sn: NotRequired[str]  # DDNS Serial Number.
    ddns_password: NotRequired[str]  # DDNS password.
    use_public_ip: NotRequired[Literal[{"description": "Disable use of public IP address", "help": "Disable use of public IP address.", "label": "Disable", "name": "disable"}, {"description": "Enable use of public IP address", "help": "Enable use of public IP address.", "label": "Enable", "name": "enable"}]]  # Enable/disable use of public IP address.
    update_interval: NotRequired[int]  # DDNS update interval (60 - 2592000 sec, 0 means default).
    clear_text: NotRequired[Literal[{"description": "Disable use of clear text connections", "help": "Disable use of clear text connections.", "label": "Disable", "name": "disable"}, {"description": "Enable use of clear text connections", "help": "Enable use of clear text connections.", "label": "Enable", "name": "enable"}]]  # Enable/disable use of clear text connections.
    ssl_certificate: NotRequired[str]  # Name of local certificate for SSL connections.
    bound_ip: NotRequired[str]  # Bound IP address.
    monitor_interface: list[dict[str, Any]]  # Monitored interface.


class Ddns:
    """
    Configure DDNS.
    
    Path: system/ddns
    Category: cmdb
    Primary Key: ddnsid
    """
    
    # Overloads for get() with response_mode="object"
    @overload
    def get(
        self,
        ddnsid: int | None = ...,
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
        ddnsid: int,
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
        ddnsid: int | None = ...,
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
        ddnsid: int | None = ...,
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
        ddnsid: int | None = ...,
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
        payload_dict: DdnsPayload | None = ...,
        ddnsid: int | None = ...,
        ddns_server: Literal[{"help": "members.dyndns.org and dnsalias.com", "label": "Dyndns.Org", "name": "dyndns.org"}, {"help": "www.dyns.net", "label": "Dyns.Net", "name": "dyns.net"}, {"help": "rh.tzo.com", "label": "Tzo.Com", "name": "tzo.com"}, {"help": "Peanut Hull", "label": "Vavic.Com", "name": "vavic.com"}, {"help": "dipdnsserver.dipdns.com", "label": "Dipdns.Net", "name": "dipdns.net"}, {"help": "ip.todayisp.com", "label": "Now.Net.Cn", "name": "now.net.cn"}, {"help": "members.dhs.org", "label": "Dhs.Org", "name": "dhs.org"}, {"help": "members.easydns.com", "label": "Easydns.Com", "name": "easydns.com"}, {"help": "Generic DDNS based on RFC2136.", "label": "Genericddns", "name": "genericDDNS"}, {"description": "FortiGuard DDNS service", "help": "FortiGuard DDNS service.", "label": "Fortiguardddns", "name": "FortiGuardDDNS"}, {"help": "dynupdate.no-ip.com", "label": "Noip.Com", "name": "noip.com"}] | None = ...,
        addr_type: Literal[{"description": "Use IPv4 address of the interface", "help": "Use IPv4 address of the interface.", "label": "Ipv4", "name": "ipv4"}, {"description": "Use IPv6 address of the interface", "help": "Use IPv6 address of the interface.", "label": "Ipv6", "name": "ipv6"}] | None = ...,
        server_type: Literal[{"description": "Use IPv4 addressing", "help": "Use IPv4 addressing.", "label": "Ipv4", "name": "ipv4"}, {"description": "Use IPv6 addressing", "help": "Use IPv6 addressing.", "label": "Ipv6", "name": "ipv6"}] | None = ...,
        ddns_server_addr: list[dict[str, Any]] | None = ...,
        ddns_zone: str | None = ...,
        ddns_ttl: int | None = ...,
        ddns_auth: Literal[{"description": "Disable DDNS authentication", "help": "Disable DDNS authentication.", "label": "Disable", "name": "disable"}, {"description": "Enable TSIG authentication based on RFC2845", "help": "Enable TSIG authentication based on RFC2845.", "label": "Tsig", "name": "tsig"}] | None = ...,
        ddns_keyname: str | None = ...,
        ddns_key: str | None = ...,
        ddns_domain: str | None = ...,
        ddns_username: str | None = ...,
        ddns_sn: str | None = ...,
        ddns_password: str | None = ...,
        use_public_ip: Literal[{"description": "Disable use of public IP address", "help": "Disable use of public IP address.", "label": "Disable", "name": "disable"}, {"description": "Enable use of public IP address", "help": "Enable use of public IP address.", "label": "Enable", "name": "enable"}] | None = ...,
        update_interval: int | None = ...,
        clear_text: Literal[{"description": "Disable use of clear text connections", "help": "Disable use of clear text connections.", "label": "Disable", "name": "disable"}, {"description": "Enable use of clear text connections", "help": "Enable use of clear text connections.", "label": "Enable", "name": "enable"}] | None = ...,
        ssl_certificate: str | None = ...,
        bound_ip: str | None = ...,
        monitor_interface: list[dict[str, Any]] | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: DdnsPayload | None = ...,
        ddnsid: int | None = ...,
        ddns_server: Literal[{"help": "members.dyndns.org and dnsalias.com", "label": "Dyndns.Org", "name": "dyndns.org"}, {"help": "www.dyns.net", "label": "Dyns.Net", "name": "dyns.net"}, {"help": "rh.tzo.com", "label": "Tzo.Com", "name": "tzo.com"}, {"help": "Peanut Hull", "label": "Vavic.Com", "name": "vavic.com"}, {"help": "dipdnsserver.dipdns.com", "label": "Dipdns.Net", "name": "dipdns.net"}, {"help": "ip.todayisp.com", "label": "Now.Net.Cn", "name": "now.net.cn"}, {"help": "members.dhs.org", "label": "Dhs.Org", "name": "dhs.org"}, {"help": "members.easydns.com", "label": "Easydns.Com", "name": "easydns.com"}, {"help": "Generic DDNS based on RFC2136.", "label": "Genericddns", "name": "genericDDNS"}, {"description": "FortiGuard DDNS service", "help": "FortiGuard DDNS service.", "label": "Fortiguardddns", "name": "FortiGuardDDNS"}, {"help": "dynupdate.no-ip.com", "label": "Noip.Com", "name": "noip.com"}] | None = ...,
        addr_type: Literal[{"description": "Use IPv4 address of the interface", "help": "Use IPv4 address of the interface.", "label": "Ipv4", "name": "ipv4"}, {"description": "Use IPv6 address of the interface", "help": "Use IPv6 address of the interface.", "label": "Ipv6", "name": "ipv6"}] | None = ...,
        server_type: Literal[{"description": "Use IPv4 addressing", "help": "Use IPv4 addressing.", "label": "Ipv4", "name": "ipv4"}, {"description": "Use IPv6 addressing", "help": "Use IPv6 addressing.", "label": "Ipv6", "name": "ipv6"}] | None = ...,
        ddns_server_addr: list[dict[str, Any]] | None = ...,
        ddns_zone: str | None = ...,
        ddns_ttl: int | None = ...,
        ddns_auth: Literal[{"description": "Disable DDNS authentication", "help": "Disable DDNS authentication.", "label": "Disable", "name": "disable"}, {"description": "Enable TSIG authentication based on RFC2845", "help": "Enable TSIG authentication based on RFC2845.", "label": "Tsig", "name": "tsig"}] | None = ...,
        ddns_keyname: str | None = ...,
        ddns_key: str | None = ...,
        ddns_domain: str | None = ...,
        ddns_username: str | None = ...,
        ddns_sn: str | None = ...,
        ddns_password: str | None = ...,
        use_public_ip: Literal[{"description": "Disable use of public IP address", "help": "Disable use of public IP address.", "label": "Disable", "name": "disable"}, {"description": "Enable use of public IP address", "help": "Enable use of public IP address.", "label": "Enable", "name": "enable"}] | None = ...,
        update_interval: int | None = ...,
        clear_text: Literal[{"description": "Disable use of clear text connections", "help": "Disable use of clear text connections.", "label": "Disable", "name": "disable"}, {"description": "Enable use of clear text connections", "help": "Enable use of clear text connections.", "label": "Enable", "name": "enable"}] | None = ...,
        ssl_certificate: str | None = ...,
        bound_ip: str | None = ...,
        monitor_interface: list[dict[str, Any]] | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def delete(
        self,
        ddnsid: int | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def exists(
        self,
        ddnsid: int,
        vdom: str | bool | None = ...,
    ) -> Union[bool, Coroutine[Any, Any, bool]]: ...
    
    def set(
        self,
        payload_dict: DdnsPayload | None = ...,
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
    "Ddns",
    "DdnsPayload",
]