from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class ExchangePayload(TypedDict, total=False):
    """
    Type hints for user/exchange payload fields.
    
    Configure MS Exchange server entries.
    
    **Usage:**
        payload: ExchangePayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    name: NotRequired[str]  # MS Exchange server entry name.
    server_name: str  # MS Exchange server hostname.
    domain_name: str  # MS Exchange server fully qualified domain name.
    username: str  # User name used to sign in to the server. Must have proper pe
    password: str  # Password for the specified username.
    ip: NotRequired[str]  # Server IPv4 address.
    connect_protocol: NotRequired[Literal[{"description": "Connect using RPC-over-TCP", "help": "Connect using RPC-over-TCP. Use for MS Exchange 2010 and earlier versions. Supported in MS Exchange 2013.", "label": "Rpc Over Tcp", "name": "rpc-over-tcp"}, {"description": "Connect using RPC-over-HTTP", "help": "Connect using RPC-over-HTTP. Use for MS Exchange 2016 and later versions. Supported in MS Exchange 2013.", "label": "Rpc Over Http", "name": "rpc-over-http"}, {"description": "Connect using RPC-over-HTTPS", "help": "Connect using RPC-over-HTTPS. Use for MS Exchange 2016 and later versions. Supported in MS Exchange 2013.", "label": "Rpc Over Https", "name": "rpc-over-https"}]]  # Connection protocol used to connect to MS Exchange service.
    validate_server_certificate: NotRequired[Literal[{"description": "Disable validation of server certificate", "help": "Disable validation of server certificate.", "label": "Disable", "name": "disable"}, {"description": "Enable validation of server certificate", "help": "Enable validation of server certificate.", "label": "Enable", "name": "enable"}]]  # Enable/disable exchange server certificate validation.
    auth_type: NotRequired[Literal[{"description": "Negotiate authentication", "help": "Negotiate authentication.", "label": "Spnego", "name": "spnego"}, {"description": "NTLM authentication", "help": "NTLM authentication.", "label": "Ntlm", "name": "ntlm"}, {"description": "Kerberos authentication", "help": "Kerberos authentication.", "label": "Kerberos", "name": "kerberos"}]]  # Authentication security type used for the RPC protocol layer
    auth_level: NotRequired[Literal[{"description": "RPC authentication level \u0027connect\u0027", "help": "RPC authentication level \u0027connect\u0027.", "label": "Connect", "name": "connect"}, {"description": "RPC authentication level \u0027call\u0027", "help": "RPC authentication level \u0027call\u0027.", "label": "Call", "name": "call"}, {"description": "RPC authentication level \u0027packet\u0027", "help": "RPC authentication level \u0027packet\u0027.", "label": "Packet", "name": "packet"}, {"description": "RPC authentication level \u0027integrity\u0027", "help": "RPC authentication level \u0027integrity\u0027.", "label": "Integrity", "name": "integrity"}, {"description": "RPC authentication level \u0027privacy\u0027", "help": "RPC authentication level \u0027privacy\u0027.", "label": "Privacy", "name": "privacy"}]]  # Authentication security level used for the RPC protocol laye
    http_auth_type: NotRequired[Literal[{"description": "Basic HTTP authentication", "help": "Basic HTTP authentication.", "label": "Basic", "name": "basic"}, {"description": "NTLM HTTP authentication", "help": "NTLM HTTP authentication.", "label": "Ntlm", "name": "ntlm"}]]  # Authentication security type used for the HTTP transport.
    ssl_min_proto_version: NotRequired[Literal[{"description": "Follow system global setting", "help": "Follow system global setting.", "label": "Default", "name": "default"}, {"description": "SSLv3", "help": "SSLv3.", "label": "Sslv3", "name": "SSLv3"}, {"description": "TLSv1", "help": "TLSv1.", "label": "Tlsv1", "name": "TLSv1"}, {"description": "TLSv1", "help": "TLSv1.1.", "label": "Tlsv1 1", "name": "TLSv1-1"}, {"description": "TLSv1", "help": "TLSv1.2.", "label": "Tlsv1 2", "name": "TLSv1-2"}, {"description": "TLSv1", "help": "TLSv1.3.", "label": "Tlsv1 3", "name": "TLSv1-3"}]]  # Minimum SSL/TLS protocol version for HTTPS transport (defaul
    auto_discover_kdc: NotRequired[Literal[{"description": "Enable automatic discovery of KDC IP addresses", "help": "Enable automatic discovery of KDC IP addresses.", "label": "Enable", "name": "enable"}, {"description": "Disable automatic discovery of KDC IP addresses", "help": "Disable automatic discovery of KDC IP addresses.", "label": "Disable", "name": "disable"}]]  # Enable/disable automatic discovery of KDC IP addresses.
    kdc_ip: NotRequired[list[dict[str, Any]]]  # KDC IPv4 addresses for Kerberos authentication.


class Exchange:
    """
    Configure MS Exchange server entries.
    
    Path: user/exchange
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
        payload_dict: ExchangePayload | None = ...,
        name: str | None = ...,
        server_name: str | None = ...,
        domain_name: str | None = ...,
        username: str | None = ...,
        password: str | None = ...,
        ip: str | None = ...,
        connect_protocol: Literal[{"description": "Connect using RPC-over-TCP", "help": "Connect using RPC-over-TCP. Use for MS Exchange 2010 and earlier versions. Supported in MS Exchange 2013.", "label": "Rpc Over Tcp", "name": "rpc-over-tcp"}, {"description": "Connect using RPC-over-HTTP", "help": "Connect using RPC-over-HTTP. Use for MS Exchange 2016 and later versions. Supported in MS Exchange 2013.", "label": "Rpc Over Http", "name": "rpc-over-http"}, {"description": "Connect using RPC-over-HTTPS", "help": "Connect using RPC-over-HTTPS. Use for MS Exchange 2016 and later versions. Supported in MS Exchange 2013.", "label": "Rpc Over Https", "name": "rpc-over-https"}] | None = ...,
        validate_server_certificate: Literal[{"description": "Disable validation of server certificate", "help": "Disable validation of server certificate.", "label": "Disable", "name": "disable"}, {"description": "Enable validation of server certificate", "help": "Enable validation of server certificate.", "label": "Enable", "name": "enable"}] | None = ...,
        auth_type: Literal[{"description": "Negotiate authentication", "help": "Negotiate authentication.", "label": "Spnego", "name": "spnego"}, {"description": "NTLM authentication", "help": "NTLM authentication.", "label": "Ntlm", "name": "ntlm"}, {"description": "Kerberos authentication", "help": "Kerberos authentication.", "label": "Kerberos", "name": "kerberos"}] | None = ...,
        auth_level: Literal[{"description": "RPC authentication level \u0027connect\u0027", "help": "RPC authentication level \u0027connect\u0027.", "label": "Connect", "name": "connect"}, {"description": "RPC authentication level \u0027call\u0027", "help": "RPC authentication level \u0027call\u0027.", "label": "Call", "name": "call"}, {"description": "RPC authentication level \u0027packet\u0027", "help": "RPC authentication level \u0027packet\u0027.", "label": "Packet", "name": "packet"}, {"description": "RPC authentication level \u0027integrity\u0027", "help": "RPC authentication level \u0027integrity\u0027.", "label": "Integrity", "name": "integrity"}, {"description": "RPC authentication level \u0027privacy\u0027", "help": "RPC authentication level \u0027privacy\u0027.", "label": "Privacy", "name": "privacy"}] | None = ...,
        http_auth_type: Literal[{"description": "Basic HTTP authentication", "help": "Basic HTTP authentication.", "label": "Basic", "name": "basic"}, {"description": "NTLM HTTP authentication", "help": "NTLM HTTP authentication.", "label": "Ntlm", "name": "ntlm"}] | None = ...,
        ssl_min_proto_version: Literal[{"description": "Follow system global setting", "help": "Follow system global setting.", "label": "Default", "name": "default"}, {"description": "SSLv3", "help": "SSLv3.", "label": "Sslv3", "name": "SSLv3"}, {"description": "TLSv1", "help": "TLSv1.", "label": "Tlsv1", "name": "TLSv1"}, {"description": "TLSv1", "help": "TLSv1.1.", "label": "Tlsv1 1", "name": "TLSv1-1"}, {"description": "TLSv1", "help": "TLSv1.2.", "label": "Tlsv1 2", "name": "TLSv1-2"}, {"description": "TLSv1", "help": "TLSv1.3.", "label": "Tlsv1 3", "name": "TLSv1-3"}] | None = ...,
        auto_discover_kdc: Literal[{"description": "Enable automatic discovery of KDC IP addresses", "help": "Enable automatic discovery of KDC IP addresses.", "label": "Enable", "name": "enable"}, {"description": "Disable automatic discovery of KDC IP addresses", "help": "Disable automatic discovery of KDC IP addresses.", "label": "Disable", "name": "disable"}] | None = ...,
        kdc_ip: list[dict[str, Any]] | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: ExchangePayload | None = ...,
        name: str | None = ...,
        server_name: str | None = ...,
        domain_name: str | None = ...,
        username: str | None = ...,
        password: str | None = ...,
        ip: str | None = ...,
        connect_protocol: Literal[{"description": "Connect using RPC-over-TCP", "help": "Connect using RPC-over-TCP. Use for MS Exchange 2010 and earlier versions. Supported in MS Exchange 2013.", "label": "Rpc Over Tcp", "name": "rpc-over-tcp"}, {"description": "Connect using RPC-over-HTTP", "help": "Connect using RPC-over-HTTP. Use for MS Exchange 2016 and later versions. Supported in MS Exchange 2013.", "label": "Rpc Over Http", "name": "rpc-over-http"}, {"description": "Connect using RPC-over-HTTPS", "help": "Connect using RPC-over-HTTPS. Use for MS Exchange 2016 and later versions. Supported in MS Exchange 2013.", "label": "Rpc Over Https", "name": "rpc-over-https"}] | None = ...,
        validate_server_certificate: Literal[{"description": "Disable validation of server certificate", "help": "Disable validation of server certificate.", "label": "Disable", "name": "disable"}, {"description": "Enable validation of server certificate", "help": "Enable validation of server certificate.", "label": "Enable", "name": "enable"}] | None = ...,
        auth_type: Literal[{"description": "Negotiate authentication", "help": "Negotiate authentication.", "label": "Spnego", "name": "spnego"}, {"description": "NTLM authentication", "help": "NTLM authentication.", "label": "Ntlm", "name": "ntlm"}, {"description": "Kerberos authentication", "help": "Kerberos authentication.", "label": "Kerberos", "name": "kerberos"}] | None = ...,
        auth_level: Literal[{"description": "RPC authentication level \u0027connect\u0027", "help": "RPC authentication level \u0027connect\u0027.", "label": "Connect", "name": "connect"}, {"description": "RPC authentication level \u0027call\u0027", "help": "RPC authentication level \u0027call\u0027.", "label": "Call", "name": "call"}, {"description": "RPC authentication level \u0027packet\u0027", "help": "RPC authentication level \u0027packet\u0027.", "label": "Packet", "name": "packet"}, {"description": "RPC authentication level \u0027integrity\u0027", "help": "RPC authentication level \u0027integrity\u0027.", "label": "Integrity", "name": "integrity"}, {"description": "RPC authentication level \u0027privacy\u0027", "help": "RPC authentication level \u0027privacy\u0027.", "label": "Privacy", "name": "privacy"}] | None = ...,
        http_auth_type: Literal[{"description": "Basic HTTP authentication", "help": "Basic HTTP authentication.", "label": "Basic", "name": "basic"}, {"description": "NTLM HTTP authentication", "help": "NTLM HTTP authentication.", "label": "Ntlm", "name": "ntlm"}] | None = ...,
        ssl_min_proto_version: Literal[{"description": "Follow system global setting", "help": "Follow system global setting.", "label": "Default", "name": "default"}, {"description": "SSLv3", "help": "SSLv3.", "label": "Sslv3", "name": "SSLv3"}, {"description": "TLSv1", "help": "TLSv1.", "label": "Tlsv1", "name": "TLSv1"}, {"description": "TLSv1", "help": "TLSv1.1.", "label": "Tlsv1 1", "name": "TLSv1-1"}, {"description": "TLSv1", "help": "TLSv1.2.", "label": "Tlsv1 2", "name": "TLSv1-2"}, {"description": "TLSv1", "help": "TLSv1.3.", "label": "Tlsv1 3", "name": "TLSv1-3"}] | None = ...,
        auto_discover_kdc: Literal[{"description": "Enable automatic discovery of KDC IP addresses", "help": "Enable automatic discovery of KDC IP addresses.", "label": "Enable", "name": "enable"}, {"description": "Disable automatic discovery of KDC IP addresses", "help": "Disable automatic discovery of KDC IP addresses.", "label": "Disable", "name": "disable"}] | None = ...,
        kdc_ip: list[dict[str, Any]] | None = ...,
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
        payload_dict: ExchangePayload | None = ...,
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
    "Exchange",
    "ExchangePayload",
]