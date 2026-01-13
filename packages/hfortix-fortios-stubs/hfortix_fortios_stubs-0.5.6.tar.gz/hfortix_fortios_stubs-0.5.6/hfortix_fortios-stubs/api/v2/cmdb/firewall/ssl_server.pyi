from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class SslServerPayload(TypedDict, total=False):
    """
    Type hints for firewall/ssl_server payload fields.
    
    Configure SSL servers.
    
    **Usage:**
        payload: SslServerPayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    name: NotRequired[str]  # Server name.
    ip: str  # IPv4 address of the SSL server.
    port: int  # Server service port (1 - 65535, default = 443).
    ssl_mode: NotRequired[Literal[{"description": "Client to FortiGate SSL", "help": "Client to FortiGate SSL.", "label": "Half", "name": "half"}, {"description": "Client to FortiGate and FortiGate to Server SSL", "help": "Client to FortiGate and FortiGate to Server SSL.", "label": "Full", "name": "full"}]]  # SSL/TLS mode for encryption and decryption of traffic.
    add_header_x_forwarded_proto: NotRequired[Literal[{"description": "Add X-Forwarded-Proto header", "help": "Add X-Forwarded-Proto header.", "label": "Enable", "name": "enable"}, {"description": "Do not add X-Forwarded-Proto header", "help": "Do not add X-Forwarded-Proto header.", "label": "Disable", "name": "disable"}]]  # Enable/disable adding an X-Forwarded-Proto header to forward
    mapped_port: int  # Mapped server service port (1 - 65535, default = 80).
    ssl_cert: NotRequired[list[dict[str, Any]]]  # List of certificate names to use for SSL connections to this
    ssl_dh_bits: NotRequired[Literal[{"description": "768-bit Diffie-Hellman prime", "help": "768-bit Diffie-Hellman prime.", "label": "768", "name": "768"}, {"description": "1024-bit Diffie-Hellman prime", "help": "1024-bit Diffie-Hellman prime.", "label": "1024", "name": "1024"}, {"description": "1536-bit Diffie-Hellman prime", "help": "1536-bit Diffie-Hellman prime.", "label": "1536", "name": "1536"}, {"description": "2048-bit Diffie-Hellman prime", "help": "2048-bit Diffie-Hellman prime.", "label": "2048", "name": "2048"}]]  # Bit-size of Diffie-Hellman (DH) prime used in DHE-RSA negoti
    ssl_algorithm: NotRequired[Literal[{"description": "High encryption", "help": "High encryption. Allow only AES and ChaCha", "label": "High", "name": "high"}, {"help": "Medium encryption. Allow AES, ChaCha, 3DES, and RC4.", "label": "Medium", "name": "medium"}, {"description": "Low encryption", "help": "Low encryption. Allow AES, ChaCha, 3DES, RC4, and DES.", "label": "Low", "name": "low"}]]  # Relative strength of encryption algorithms accepted in negot
    ssl_client_renegotiation: NotRequired[Literal[{"description": "Allow a SSL client to renegotiate", "help": "Allow a SSL client to renegotiate.", "label": "Allow", "name": "allow"}, {"description": "Abort any SSL connection that attempts to renegotiate", "help": "Abort any SSL connection that attempts to renegotiate.", "label": "Deny", "name": "deny"}, {"description": "Reject any SSL connection that does not offer a RFC 5746 Secure Renegotiation Indication", "help": "Reject any SSL connection that does not offer a RFC 5746 Secure Renegotiation Indication.", "label": "Secure", "name": "secure"}]]  # Allow or block client renegotiation by server.
    ssl_min_version: NotRequired[Literal[{"help": "TLS 1.0.", "label": "Tls 1.0", "name": "tls-1.0"}, {"help": "TLS 1.1.", "label": "Tls 1.1", "name": "tls-1.1"}, {"help": "TLS 1.2.", "label": "Tls 1.2", "name": "tls-1.2"}, {"help": "TLS 1.3.", "label": "Tls 1.3", "name": "tls-1.3"}]]  # Lowest SSL/TLS version to negotiate.
    ssl_max_version: NotRequired[Literal[{"help": "TLS 1.0.", "label": "Tls 1.0", "name": "tls-1.0"}, {"help": "TLS 1.1.", "label": "Tls 1.1", "name": "tls-1.1"}, {"help": "TLS 1.2.", "label": "Tls 1.2", "name": "tls-1.2"}, {"help": "TLS 1.3.", "label": "Tls 1.3", "name": "tls-1.3"}]]  # Highest SSL/TLS version to negotiate.
    ssl_send_empty_frags: NotRequired[Literal[{"description": "Send empty fragments", "help": "Send empty fragments.", "label": "Enable", "name": "enable"}, {"description": "Do not send empty fragments", "help": "Do not send empty fragments.", "label": "Disable", "name": "disable"}]]  # Enable/disable sending empty fragments to avoid attack on CB
    url_rewrite: NotRequired[Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]]  # Enable/disable rewriting the URL.


class SslServer:
    """
    Configure SSL servers.
    
    Path: firewall/ssl_server
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
        payload_dict: SslServerPayload | None = ...,
        name: str | None = ...,
        ip: str | None = ...,
        port: int | None = ...,
        ssl_mode: Literal[{"description": "Client to FortiGate SSL", "help": "Client to FortiGate SSL.", "label": "Half", "name": "half"}, {"description": "Client to FortiGate and FortiGate to Server SSL", "help": "Client to FortiGate and FortiGate to Server SSL.", "label": "Full", "name": "full"}] | None = ...,
        add_header_x_forwarded_proto: Literal[{"description": "Add X-Forwarded-Proto header", "help": "Add X-Forwarded-Proto header.", "label": "Enable", "name": "enable"}, {"description": "Do not add X-Forwarded-Proto header", "help": "Do not add X-Forwarded-Proto header.", "label": "Disable", "name": "disable"}] | None = ...,
        mapped_port: int | None = ...,
        ssl_cert: list[dict[str, Any]] | None = ...,
        ssl_dh_bits: Literal[{"description": "768-bit Diffie-Hellman prime", "help": "768-bit Diffie-Hellman prime.", "label": "768", "name": "768"}, {"description": "1024-bit Diffie-Hellman prime", "help": "1024-bit Diffie-Hellman prime.", "label": "1024", "name": "1024"}, {"description": "1536-bit Diffie-Hellman prime", "help": "1536-bit Diffie-Hellman prime.", "label": "1536", "name": "1536"}, {"description": "2048-bit Diffie-Hellman prime", "help": "2048-bit Diffie-Hellman prime.", "label": "2048", "name": "2048"}] | None = ...,
        ssl_algorithm: Literal[{"description": "High encryption", "help": "High encryption. Allow only AES and ChaCha", "label": "High", "name": "high"}, {"help": "Medium encryption. Allow AES, ChaCha, 3DES, and RC4.", "label": "Medium", "name": "medium"}, {"description": "Low encryption", "help": "Low encryption. Allow AES, ChaCha, 3DES, RC4, and DES.", "label": "Low", "name": "low"}] | None = ...,
        ssl_client_renegotiation: Literal[{"description": "Allow a SSL client to renegotiate", "help": "Allow a SSL client to renegotiate.", "label": "Allow", "name": "allow"}, {"description": "Abort any SSL connection that attempts to renegotiate", "help": "Abort any SSL connection that attempts to renegotiate.", "label": "Deny", "name": "deny"}, {"description": "Reject any SSL connection that does not offer a RFC 5746 Secure Renegotiation Indication", "help": "Reject any SSL connection that does not offer a RFC 5746 Secure Renegotiation Indication.", "label": "Secure", "name": "secure"}] | None = ...,
        ssl_min_version: Literal[{"help": "TLS 1.0.", "label": "Tls 1.0", "name": "tls-1.0"}, {"help": "TLS 1.1.", "label": "Tls 1.1", "name": "tls-1.1"}, {"help": "TLS 1.2.", "label": "Tls 1.2", "name": "tls-1.2"}, {"help": "TLS 1.3.", "label": "Tls 1.3", "name": "tls-1.3"}] | None = ...,
        ssl_max_version: Literal[{"help": "TLS 1.0.", "label": "Tls 1.0", "name": "tls-1.0"}, {"help": "TLS 1.1.", "label": "Tls 1.1", "name": "tls-1.1"}, {"help": "TLS 1.2.", "label": "Tls 1.2", "name": "tls-1.2"}, {"help": "TLS 1.3.", "label": "Tls 1.3", "name": "tls-1.3"}] | None = ...,
        ssl_send_empty_frags: Literal[{"description": "Send empty fragments", "help": "Send empty fragments.", "label": "Enable", "name": "enable"}, {"description": "Do not send empty fragments", "help": "Do not send empty fragments.", "label": "Disable", "name": "disable"}] | None = ...,
        url_rewrite: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: SslServerPayload | None = ...,
        name: str | None = ...,
        ip: str | None = ...,
        port: int | None = ...,
        ssl_mode: Literal[{"description": "Client to FortiGate SSL", "help": "Client to FortiGate SSL.", "label": "Half", "name": "half"}, {"description": "Client to FortiGate and FortiGate to Server SSL", "help": "Client to FortiGate and FortiGate to Server SSL.", "label": "Full", "name": "full"}] | None = ...,
        add_header_x_forwarded_proto: Literal[{"description": "Add X-Forwarded-Proto header", "help": "Add X-Forwarded-Proto header.", "label": "Enable", "name": "enable"}, {"description": "Do not add X-Forwarded-Proto header", "help": "Do not add X-Forwarded-Proto header.", "label": "Disable", "name": "disable"}] | None = ...,
        mapped_port: int | None = ...,
        ssl_cert: list[dict[str, Any]] | None = ...,
        ssl_dh_bits: Literal[{"description": "768-bit Diffie-Hellman prime", "help": "768-bit Diffie-Hellman prime.", "label": "768", "name": "768"}, {"description": "1024-bit Diffie-Hellman prime", "help": "1024-bit Diffie-Hellman prime.", "label": "1024", "name": "1024"}, {"description": "1536-bit Diffie-Hellman prime", "help": "1536-bit Diffie-Hellman prime.", "label": "1536", "name": "1536"}, {"description": "2048-bit Diffie-Hellman prime", "help": "2048-bit Diffie-Hellman prime.", "label": "2048", "name": "2048"}] | None = ...,
        ssl_algorithm: Literal[{"description": "High encryption", "help": "High encryption. Allow only AES and ChaCha", "label": "High", "name": "high"}, {"help": "Medium encryption. Allow AES, ChaCha, 3DES, and RC4.", "label": "Medium", "name": "medium"}, {"description": "Low encryption", "help": "Low encryption. Allow AES, ChaCha, 3DES, RC4, and DES.", "label": "Low", "name": "low"}] | None = ...,
        ssl_client_renegotiation: Literal[{"description": "Allow a SSL client to renegotiate", "help": "Allow a SSL client to renegotiate.", "label": "Allow", "name": "allow"}, {"description": "Abort any SSL connection that attempts to renegotiate", "help": "Abort any SSL connection that attempts to renegotiate.", "label": "Deny", "name": "deny"}, {"description": "Reject any SSL connection that does not offer a RFC 5746 Secure Renegotiation Indication", "help": "Reject any SSL connection that does not offer a RFC 5746 Secure Renegotiation Indication.", "label": "Secure", "name": "secure"}] | None = ...,
        ssl_min_version: Literal[{"help": "TLS 1.0.", "label": "Tls 1.0", "name": "tls-1.0"}, {"help": "TLS 1.1.", "label": "Tls 1.1", "name": "tls-1.1"}, {"help": "TLS 1.2.", "label": "Tls 1.2", "name": "tls-1.2"}, {"help": "TLS 1.3.", "label": "Tls 1.3", "name": "tls-1.3"}] | None = ...,
        ssl_max_version: Literal[{"help": "TLS 1.0.", "label": "Tls 1.0", "name": "tls-1.0"}, {"help": "TLS 1.1.", "label": "Tls 1.1", "name": "tls-1.1"}, {"help": "TLS 1.2.", "label": "Tls 1.2", "name": "tls-1.2"}, {"help": "TLS 1.3.", "label": "Tls 1.3", "name": "tls-1.3"}] | None = ...,
        ssl_send_empty_frags: Literal[{"description": "Send empty fragments", "help": "Send empty fragments.", "label": "Enable", "name": "enable"}, {"description": "Do not send empty fragments", "help": "Do not send empty fragments.", "label": "Disable", "name": "disable"}] | None = ...,
        url_rewrite: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
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
        payload_dict: SslServerPayload | None = ...,
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
    "SslServer",
    "SslServerPayload",
]