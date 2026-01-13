from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class ExplicitPayload(TypedDict, total=False):
    """
    Type hints for ftp_proxy/explicit payload fields.
    
    Configure explicit FTP proxy settings.
    
    **Usage:**
        payload: ExplicitPayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    status: NotRequired[Literal[{"description": "Enable the explicit FTP proxy", "help": "Enable the explicit FTP proxy.", "label": "Enable", "name": "enable"}, {"description": "Disable the explicit FTP proxy", "help": "Disable the explicit FTP proxy.", "label": "Disable", "name": "disable"}]]  # Enable/disable the explicit FTP proxy.
    incoming_port: NotRequired[str]  # Accept incoming FTP requests on one or more ports.
    incoming_ip: NotRequired[str]  # Accept incoming FTP requests from this IP address. An interf
    outgoing_ip: NotRequired[list[dict[str, Any]]]  # Outgoing FTP requests will leave from this IP address. An in
    sec_default_action: NotRequired[Literal[{"description": "Accept requests", "help": "Accept requests. All explicit FTP proxy traffic is accepted whether there is an explicit FTP proxy policy or not", "label": "Accept", "name": "accept"}, {"help": "Deny requests unless there is a matching explicit FTP proxy policy.", "label": "Deny", "name": "deny"}]]  # Accept or deny explicit FTP proxy sessions when no FTP proxy
    server_data_mode: NotRequired[Literal[{"description": "Use the same transmission mode for client and server data sessions", "help": "Use the same transmission mode for client and server data sessions.", "label": "Client", "name": "client"}, {"description": "Use passive mode on server data session", "help": "Use passive mode on server data session.", "label": "Passive", "name": "passive"}]]  # Determine mode of data session on FTP server side.
    ssl: NotRequired[Literal[{"description": "Enable the explicit FTPS proxy", "help": "Enable the explicit FTPS proxy.", "label": "Enable", "name": "enable"}, {"description": "Disable the explicit FTPS proxy", "help": "Disable the explicit FTPS proxy.", "label": "Disable", "name": "disable"}]]  # Enable/disable the explicit FTPS proxy.
    ssl_cert: NotRequired[list[dict[str, Any]]]  # List of certificate names to use for SSL connections to this
    ssl_dh_bits: NotRequired[Literal[{"description": "768-bit Diffie-Hellman prime", "help": "768-bit Diffie-Hellman prime.", "label": "768", "name": "768"}, {"description": "1024-bit Diffie-Hellman prime", "help": "1024-bit Diffie-Hellman prime.", "label": "1024", "name": "1024"}, {"description": "1536-bit Diffie-Hellman prime", "help": "1536-bit Diffie-Hellman prime.", "label": "1536", "name": "1536"}, {"description": "2048-bit Diffie-Hellman prime", "help": "2048-bit Diffie-Hellman prime.", "label": "2048", "name": "2048"}]]  # Bit-size of Diffie-Hellman (DH) prime used in DHE-RSA negoti
    ssl_algorithm: NotRequired[Literal[{"description": "High encryption", "help": "High encryption. Allow only AES and ChaCha", "label": "High", "name": "high"}, {"help": "Medium encryption. Allow AES, ChaCha, 3DES, and RC4.", "label": "Medium", "name": "medium"}, {"description": "Low encryption", "help": "Low encryption. Allow AES, ChaCha, 3DES, RC4, and DES.", "label": "Low", "name": "low"}]]  # Relative strength of encryption algorithms accepted in negot


class Explicit:
    """
    Configure explicit FTP proxy settings.
    
    Path: ftp_proxy/explicit
    Category: cmdb
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
        payload_dict: ExplicitPayload | None = ...,
        status: Literal[{"description": "Enable the explicit FTP proxy", "help": "Enable the explicit FTP proxy.", "label": "Enable", "name": "enable"}, {"description": "Disable the explicit FTP proxy", "help": "Disable the explicit FTP proxy.", "label": "Disable", "name": "disable"}] | None = ...,
        incoming_port: str | None = ...,
        incoming_ip: str | None = ...,
        outgoing_ip: list[dict[str, Any]] | None = ...,
        sec_default_action: Literal[{"description": "Accept requests", "help": "Accept requests. All explicit FTP proxy traffic is accepted whether there is an explicit FTP proxy policy or not", "label": "Accept", "name": "accept"}, {"help": "Deny requests unless there is a matching explicit FTP proxy policy.", "label": "Deny", "name": "deny"}] | None = ...,
        server_data_mode: Literal[{"description": "Use the same transmission mode for client and server data sessions", "help": "Use the same transmission mode for client and server data sessions.", "label": "Client", "name": "client"}, {"description": "Use passive mode on server data session", "help": "Use passive mode on server data session.", "label": "Passive", "name": "passive"}] | None = ...,
        ssl: Literal[{"description": "Enable the explicit FTPS proxy", "help": "Enable the explicit FTPS proxy.", "label": "Enable", "name": "enable"}, {"description": "Disable the explicit FTPS proxy", "help": "Disable the explicit FTPS proxy.", "label": "Disable", "name": "disable"}] | None = ...,
        ssl_cert: list[dict[str, Any]] | None = ...,
        ssl_dh_bits: Literal[{"description": "768-bit Diffie-Hellman prime", "help": "768-bit Diffie-Hellman prime.", "label": "768", "name": "768"}, {"description": "1024-bit Diffie-Hellman prime", "help": "1024-bit Diffie-Hellman prime.", "label": "1024", "name": "1024"}, {"description": "1536-bit Diffie-Hellman prime", "help": "1536-bit Diffie-Hellman prime.", "label": "1536", "name": "1536"}, {"description": "2048-bit Diffie-Hellman prime", "help": "2048-bit Diffie-Hellman prime.", "label": "2048", "name": "2048"}] | None = ...,
        ssl_algorithm: Literal[{"description": "High encryption", "help": "High encryption. Allow only AES and ChaCha", "label": "High", "name": "high"}, {"help": "Medium encryption. Allow AES, ChaCha, 3DES, and RC4.", "label": "Medium", "name": "medium"}, {"description": "Low encryption", "help": "Low encryption. Allow AES, ChaCha, 3DES, RC4, and DES.", "label": "Low", "name": "low"}] | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: ExplicitPayload | None = ...,
        status: Literal[{"description": "Enable the explicit FTP proxy", "help": "Enable the explicit FTP proxy.", "label": "Enable", "name": "enable"}, {"description": "Disable the explicit FTP proxy", "help": "Disable the explicit FTP proxy.", "label": "Disable", "name": "disable"}] | None = ...,
        incoming_port: str | None = ...,
        incoming_ip: str | None = ...,
        outgoing_ip: list[dict[str, Any]] | None = ...,
        sec_default_action: Literal[{"description": "Accept requests", "help": "Accept requests. All explicit FTP proxy traffic is accepted whether there is an explicit FTP proxy policy or not", "label": "Accept", "name": "accept"}, {"help": "Deny requests unless there is a matching explicit FTP proxy policy.", "label": "Deny", "name": "deny"}] | None = ...,
        server_data_mode: Literal[{"description": "Use the same transmission mode for client and server data sessions", "help": "Use the same transmission mode for client and server data sessions.", "label": "Client", "name": "client"}, {"description": "Use passive mode on server data session", "help": "Use passive mode on server data session.", "label": "Passive", "name": "passive"}] | None = ...,
        ssl: Literal[{"description": "Enable the explicit FTPS proxy", "help": "Enable the explicit FTPS proxy.", "label": "Enable", "name": "enable"}, {"description": "Disable the explicit FTPS proxy", "help": "Disable the explicit FTPS proxy.", "label": "Disable", "name": "disable"}] | None = ...,
        ssl_cert: list[dict[str, Any]] | None = ...,
        ssl_dh_bits: Literal[{"description": "768-bit Diffie-Hellman prime", "help": "768-bit Diffie-Hellman prime.", "label": "768", "name": "768"}, {"description": "1024-bit Diffie-Hellman prime", "help": "1024-bit Diffie-Hellman prime.", "label": "1024", "name": "1024"}, {"description": "1536-bit Diffie-Hellman prime", "help": "1536-bit Diffie-Hellman prime.", "label": "1536", "name": "1536"}, {"description": "2048-bit Diffie-Hellman prime", "help": "2048-bit Diffie-Hellman prime.", "label": "2048", "name": "2048"}] | None = ...,
        ssl_algorithm: Literal[{"description": "High encryption", "help": "High encryption. Allow only AES and ChaCha", "label": "High", "name": "high"}, {"help": "Medium encryption. Allow AES, ChaCha, 3DES, and RC4.", "label": "Medium", "name": "medium"}, {"description": "Low encryption", "help": "Low encryption. Allow AES, ChaCha, 3DES, RC4, and DES.", "label": "Low", "name": "low"}] | None = ...,
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
        payload_dict: ExplicitPayload | None = ...,
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
    "Explicit",
    "ExplicitPayload",
]