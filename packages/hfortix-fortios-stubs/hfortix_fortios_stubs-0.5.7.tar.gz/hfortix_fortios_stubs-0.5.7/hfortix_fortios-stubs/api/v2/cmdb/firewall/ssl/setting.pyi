from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class SettingPayload(TypedDict, total=False):
    """
    Type hints for firewall/ssl/setting payload fields.
    
    SSL proxy settings.
    
    **Usage:**
        payload: SettingPayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    proxy_connect_timeout: int  # Time limit to make an internal connection to the appropriate
    ssl_dh_bits: Literal[{"description": "768-bit Diffie-Hellman prime", "help": "768-bit Diffie-Hellman prime.", "label": "768", "name": "768"}, {"description": "1024-bit Diffie-Hellman prime", "help": "1024-bit Diffie-Hellman prime.", "label": "1024", "name": "1024"}, {"description": "1536-bit Diffie-Hellman prime", "help": "1536-bit Diffie-Hellman prime.", "label": "1536", "name": "1536"}, {"description": "2048-bit Diffie-Hellman prime", "help": "2048-bit Diffie-Hellman prime.", "label": "2048", "name": "2048"}]  # Bit-size of Diffie-Hellman (DH) prime used in DHE-RSA negoti
    ssl_send_empty_frags: Literal[{"description": "Send empty fragments", "help": "Send empty fragments.", "label": "Enable", "name": "enable"}, {"description": "Do not send empty fragments", "help": "Do not send empty fragments.", "label": "Disable", "name": "disable"}]  # Enable/disable sending empty fragments to avoid attack on CB
    no_matching_cipher_action: Literal[{"description": "Bypass connection", "help": "Bypass connection.", "label": "Bypass", "name": "bypass"}, {"description": "Drop connection", "help": "Drop connection.", "label": "Drop", "name": "drop"}]  # Bypass or drop the connection when no matching cipher is fou
    cert_manager_cache_timeout: int  # Time limit for certificate manager to keep FortiGate re-sign
    resigned_short_lived_certificate: Literal[{"description": "Enable short-lived certificate: re-signed certificate will remain valid until either the origin server ceritificate expires or cache timeouts", "help": "Enable short-lived certificate: re-signed certificate will remain valid until either the origin server ceritificate expires or cache timeouts.", "label": "Enable", "name": "enable"}, {"description": "Disable short-lived certificate: re-signed certificate will have the same validation period as the origin server ceritificate", "help": "Disable short-lived certificate: re-signed certificate will have the same validation period as the origin server ceritificate.", "label": "Disable", "name": "disable"}]  # Enable/disable short-lived certificate.
    cert_cache_capacity: int  # Maximum capacity of the host certificate cache (0 - 500, def
    cert_cache_timeout: int  # Time limit to keep certificate cache (1 - 120 min, default =
    session_cache_capacity: int  # Capacity of the SSL session cache (--Obsolete--) (1 - 1000, 
    session_cache_timeout: int  # Time limit to keep SSL session state (1 - 60 min, default = 
    abbreviate_handshake: NotRequired[Literal[{"description": "Enable use of SSL abbreviated handshake", "help": "Enable use of SSL abbreviated handshake.", "label": "Enable", "name": "enable"}, {"description": "Disable use of SSL abbreviated handshake", "help": "Disable use of SSL abbreviated handshake.", "label": "Disable", "name": "disable"}]]  # Enable/disable use of SSL abbreviated handshake.


class Setting:
    """
    SSL proxy settings.
    
    Path: firewall/ssl/setting
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
        payload_dict: SettingPayload | None = ...,
        proxy_connect_timeout: int | None = ...,
        ssl_dh_bits: Literal[{"description": "768-bit Diffie-Hellman prime", "help": "768-bit Diffie-Hellman prime.", "label": "768", "name": "768"}, {"description": "1024-bit Diffie-Hellman prime", "help": "1024-bit Diffie-Hellman prime.", "label": "1024", "name": "1024"}, {"description": "1536-bit Diffie-Hellman prime", "help": "1536-bit Diffie-Hellman prime.", "label": "1536", "name": "1536"}, {"description": "2048-bit Diffie-Hellman prime", "help": "2048-bit Diffie-Hellman prime.", "label": "2048", "name": "2048"}] | None = ...,
        ssl_send_empty_frags: Literal[{"description": "Send empty fragments", "help": "Send empty fragments.", "label": "Enable", "name": "enable"}, {"description": "Do not send empty fragments", "help": "Do not send empty fragments.", "label": "Disable", "name": "disable"}] | None = ...,
        no_matching_cipher_action: Literal[{"description": "Bypass connection", "help": "Bypass connection.", "label": "Bypass", "name": "bypass"}, {"description": "Drop connection", "help": "Drop connection.", "label": "Drop", "name": "drop"}] | None = ...,
        cert_manager_cache_timeout: int | None = ...,
        resigned_short_lived_certificate: Literal[{"description": "Enable short-lived certificate: re-signed certificate will remain valid until either the origin server ceritificate expires or cache timeouts", "help": "Enable short-lived certificate: re-signed certificate will remain valid until either the origin server ceritificate expires or cache timeouts.", "label": "Enable", "name": "enable"}, {"description": "Disable short-lived certificate: re-signed certificate will have the same validation period as the origin server ceritificate", "help": "Disable short-lived certificate: re-signed certificate will have the same validation period as the origin server ceritificate.", "label": "Disable", "name": "disable"}] | None = ...,
        cert_cache_capacity: int | None = ...,
        cert_cache_timeout: int | None = ...,
        session_cache_capacity: int | None = ...,
        session_cache_timeout: int | None = ...,
        abbreviate_handshake: Literal[{"description": "Enable use of SSL abbreviated handshake", "help": "Enable use of SSL abbreviated handshake.", "label": "Enable", "name": "enable"}, {"description": "Disable use of SSL abbreviated handshake", "help": "Disable use of SSL abbreviated handshake.", "label": "Disable", "name": "disable"}] | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: SettingPayload | None = ...,
        proxy_connect_timeout: int | None = ...,
        ssl_dh_bits: Literal[{"description": "768-bit Diffie-Hellman prime", "help": "768-bit Diffie-Hellman prime.", "label": "768", "name": "768"}, {"description": "1024-bit Diffie-Hellman prime", "help": "1024-bit Diffie-Hellman prime.", "label": "1024", "name": "1024"}, {"description": "1536-bit Diffie-Hellman prime", "help": "1536-bit Diffie-Hellman prime.", "label": "1536", "name": "1536"}, {"description": "2048-bit Diffie-Hellman prime", "help": "2048-bit Diffie-Hellman prime.", "label": "2048", "name": "2048"}] | None = ...,
        ssl_send_empty_frags: Literal[{"description": "Send empty fragments", "help": "Send empty fragments.", "label": "Enable", "name": "enable"}, {"description": "Do not send empty fragments", "help": "Do not send empty fragments.", "label": "Disable", "name": "disable"}] | None = ...,
        no_matching_cipher_action: Literal[{"description": "Bypass connection", "help": "Bypass connection.", "label": "Bypass", "name": "bypass"}, {"description": "Drop connection", "help": "Drop connection.", "label": "Drop", "name": "drop"}] | None = ...,
        cert_manager_cache_timeout: int | None = ...,
        resigned_short_lived_certificate: Literal[{"description": "Enable short-lived certificate: re-signed certificate will remain valid until either the origin server ceritificate expires or cache timeouts", "help": "Enable short-lived certificate: re-signed certificate will remain valid until either the origin server ceritificate expires or cache timeouts.", "label": "Enable", "name": "enable"}, {"description": "Disable short-lived certificate: re-signed certificate will have the same validation period as the origin server ceritificate", "help": "Disable short-lived certificate: re-signed certificate will have the same validation period as the origin server ceritificate.", "label": "Disable", "name": "disable"}] | None = ...,
        cert_cache_capacity: int | None = ...,
        cert_cache_timeout: int | None = ...,
        session_cache_capacity: int | None = ...,
        session_cache_timeout: int | None = ...,
        abbreviate_handshake: Literal[{"description": "Enable use of SSL abbreviated handshake", "help": "Enable use of SSL abbreviated handshake.", "label": "Enable", "name": "enable"}, {"description": "Disable use of SSL abbreviated handshake", "help": "Disable use of SSL abbreviated handshake.", "label": "Disable", "name": "disable"}] | None = ...,
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
        payload_dict: SettingPayload | None = ...,
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
    "Setting",
    "SettingPayload",
]