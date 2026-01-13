from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class SnmpUserPayload(TypedDict, total=False):
    """
    Type hints for switch_controller/snmp_user payload fields.
    
    Configure FortiSwitch SNMP v3 users globally.
    
    **Usage:**
        payload: SnmpUserPayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    name: NotRequired[str]  # SNMP user name.
    queries: NotRequired[Literal[{"description": "Disable SNMP queries for this user", "help": "Disable SNMP queries for this user.", "label": "Disable", "name": "disable"}, {"description": "Enable SNMP queries for this user", "help": "Enable SNMP queries for this user.", "label": "Enable", "name": "enable"}]]  # Enable/disable SNMP queries for this user.
    query_port: NotRequired[int]  # SNMPv3 query port (default = 161).
    security_level: NotRequired[Literal[{"description": "Message with no authentication and no privacy (encryption)", "help": "Message with no authentication and no privacy (encryption).", "label": "No Auth No Priv", "name": "no-auth-no-priv"}, {"description": "Message with authentication but no privacy (encryption)", "help": "Message with authentication but no privacy (encryption).", "label": "Auth No Priv", "name": "auth-no-priv"}, {"description": "Message with authentication and privacy (encryption)", "help": "Message with authentication and privacy (encryption).", "label": "Auth Priv", "name": "auth-priv"}]]  # Security level for message authentication and encryption.
    auth_proto: NotRequired[Literal[{"description": "HMAC-MD5-96 authentication protocol", "help": "HMAC-MD5-96 authentication protocol.", "label": "Md5", "name": "md5"}, {"description": "HMAC-SHA-1 authentication protocol", "help": "HMAC-SHA-1 authentication protocol.", "label": "Sha1", "name": "sha1"}, {"description": "HMAC-SHA-224 authentication protocol", "help": "HMAC-SHA-224 authentication protocol.", "label": "Sha224", "name": "sha224"}, {"description": "HMAC-SHA-256 authentication protocol", "help": "HMAC-SHA-256 authentication protocol.", "label": "Sha256", "name": "sha256"}, {"description": "HMAC-SHA-384 authentication protocol", "help": "HMAC-SHA-384 authentication protocol.", "label": "Sha384", "name": "sha384"}, {"description": "HMAC-SHA-512 authentication protocol", "help": "HMAC-SHA-512 authentication protocol.", "label": "Sha512", "name": "sha512"}]]  # Authentication protocol.
    auth_pwd: str  # Password for authentication protocol.
    priv_proto: NotRequired[Literal[{"description": "CFB128-AES-128 symmetric encryption protocol", "help": "CFB128-AES-128 symmetric encryption protocol.", "label": "Aes128", "name": "aes128"}, {"description": "CFB128-AES-192 symmetric encryption protocol", "help": "CFB128-AES-192 symmetric encryption protocol.", "label": "Aes192", "name": "aes192"}, {"description": "CFB128-AES-192-C symmetric encryption protocol", "help": "CFB128-AES-192-C symmetric encryption protocol.", "label": "Aes192C", "name": "aes192c"}, {"description": "CFB128-AES-256 symmetric encryption protocol", "help": "CFB128-AES-256 symmetric encryption protocol.", "label": "Aes256", "name": "aes256"}, {"description": "CFB128-AES-256-C symmetric encryption protocol", "help": "CFB128-AES-256-C symmetric encryption protocol.", "label": "Aes256C", "name": "aes256c"}, {"description": "CBC-DES symmetric encryption protocol", "help": "CBC-DES symmetric encryption protocol.", "label": "Des", "name": "des"}]]  # Privacy (encryption) protocol.
    priv_pwd: str  # Password for privacy (encryption) protocol.


class SnmpUser:
    """
    Configure FortiSwitch SNMP v3 users globally.
    
    Path: switch_controller/snmp_user
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
        payload_dict: SnmpUserPayload | None = ...,
        name: str | None = ...,
        queries: Literal[{"description": "Disable SNMP queries for this user", "help": "Disable SNMP queries for this user.", "label": "Disable", "name": "disable"}, {"description": "Enable SNMP queries for this user", "help": "Enable SNMP queries for this user.", "label": "Enable", "name": "enable"}] | None = ...,
        query_port: int | None = ...,
        security_level: Literal[{"description": "Message with no authentication and no privacy (encryption)", "help": "Message with no authentication and no privacy (encryption).", "label": "No Auth No Priv", "name": "no-auth-no-priv"}, {"description": "Message with authentication but no privacy (encryption)", "help": "Message with authentication but no privacy (encryption).", "label": "Auth No Priv", "name": "auth-no-priv"}, {"description": "Message with authentication and privacy (encryption)", "help": "Message with authentication and privacy (encryption).", "label": "Auth Priv", "name": "auth-priv"}] | None = ...,
        auth_proto: Literal[{"description": "HMAC-MD5-96 authentication protocol", "help": "HMAC-MD5-96 authentication protocol.", "label": "Md5", "name": "md5"}, {"description": "HMAC-SHA-1 authentication protocol", "help": "HMAC-SHA-1 authentication protocol.", "label": "Sha1", "name": "sha1"}, {"description": "HMAC-SHA-224 authentication protocol", "help": "HMAC-SHA-224 authentication protocol.", "label": "Sha224", "name": "sha224"}, {"description": "HMAC-SHA-256 authentication protocol", "help": "HMAC-SHA-256 authentication protocol.", "label": "Sha256", "name": "sha256"}, {"description": "HMAC-SHA-384 authentication protocol", "help": "HMAC-SHA-384 authentication protocol.", "label": "Sha384", "name": "sha384"}, {"description": "HMAC-SHA-512 authentication protocol", "help": "HMAC-SHA-512 authentication protocol.", "label": "Sha512", "name": "sha512"}] | None = ...,
        auth_pwd: str | None = ...,
        priv_proto: Literal[{"description": "CFB128-AES-128 symmetric encryption protocol", "help": "CFB128-AES-128 symmetric encryption protocol.", "label": "Aes128", "name": "aes128"}, {"description": "CFB128-AES-192 symmetric encryption protocol", "help": "CFB128-AES-192 symmetric encryption protocol.", "label": "Aes192", "name": "aes192"}, {"description": "CFB128-AES-192-C symmetric encryption protocol", "help": "CFB128-AES-192-C symmetric encryption protocol.", "label": "Aes192C", "name": "aes192c"}, {"description": "CFB128-AES-256 symmetric encryption protocol", "help": "CFB128-AES-256 symmetric encryption protocol.", "label": "Aes256", "name": "aes256"}, {"description": "CFB128-AES-256-C symmetric encryption protocol", "help": "CFB128-AES-256-C symmetric encryption protocol.", "label": "Aes256C", "name": "aes256c"}, {"description": "CBC-DES symmetric encryption protocol", "help": "CBC-DES symmetric encryption protocol.", "label": "Des", "name": "des"}] | None = ...,
        priv_pwd: str | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: SnmpUserPayload | None = ...,
        name: str | None = ...,
        queries: Literal[{"description": "Disable SNMP queries for this user", "help": "Disable SNMP queries for this user.", "label": "Disable", "name": "disable"}, {"description": "Enable SNMP queries for this user", "help": "Enable SNMP queries for this user.", "label": "Enable", "name": "enable"}] | None = ...,
        query_port: int | None = ...,
        security_level: Literal[{"description": "Message with no authentication and no privacy (encryption)", "help": "Message with no authentication and no privacy (encryption).", "label": "No Auth No Priv", "name": "no-auth-no-priv"}, {"description": "Message with authentication but no privacy (encryption)", "help": "Message with authentication but no privacy (encryption).", "label": "Auth No Priv", "name": "auth-no-priv"}, {"description": "Message with authentication and privacy (encryption)", "help": "Message with authentication and privacy (encryption).", "label": "Auth Priv", "name": "auth-priv"}] | None = ...,
        auth_proto: Literal[{"description": "HMAC-MD5-96 authentication protocol", "help": "HMAC-MD5-96 authentication protocol.", "label": "Md5", "name": "md5"}, {"description": "HMAC-SHA-1 authentication protocol", "help": "HMAC-SHA-1 authentication protocol.", "label": "Sha1", "name": "sha1"}, {"description": "HMAC-SHA-224 authentication protocol", "help": "HMAC-SHA-224 authentication protocol.", "label": "Sha224", "name": "sha224"}, {"description": "HMAC-SHA-256 authentication protocol", "help": "HMAC-SHA-256 authentication protocol.", "label": "Sha256", "name": "sha256"}, {"description": "HMAC-SHA-384 authentication protocol", "help": "HMAC-SHA-384 authentication protocol.", "label": "Sha384", "name": "sha384"}, {"description": "HMAC-SHA-512 authentication protocol", "help": "HMAC-SHA-512 authentication protocol.", "label": "Sha512", "name": "sha512"}] | None = ...,
        auth_pwd: str | None = ...,
        priv_proto: Literal[{"description": "CFB128-AES-128 symmetric encryption protocol", "help": "CFB128-AES-128 symmetric encryption protocol.", "label": "Aes128", "name": "aes128"}, {"description": "CFB128-AES-192 symmetric encryption protocol", "help": "CFB128-AES-192 symmetric encryption protocol.", "label": "Aes192", "name": "aes192"}, {"description": "CFB128-AES-192-C symmetric encryption protocol", "help": "CFB128-AES-192-C symmetric encryption protocol.", "label": "Aes192C", "name": "aes192c"}, {"description": "CFB128-AES-256 symmetric encryption protocol", "help": "CFB128-AES-256 symmetric encryption protocol.", "label": "Aes256", "name": "aes256"}, {"description": "CFB128-AES-256-C symmetric encryption protocol", "help": "CFB128-AES-256-C symmetric encryption protocol.", "label": "Aes256C", "name": "aes256c"}, {"description": "CBC-DES symmetric encryption protocol", "help": "CBC-DES symmetric encryption protocol.", "label": "Des", "name": "des"}] | None = ...,
        priv_pwd: str | None = ...,
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
        payload_dict: SnmpUserPayload | None = ...,
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
    "SnmpUser",
    "SnmpUserPayload",
]