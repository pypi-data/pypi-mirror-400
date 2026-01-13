from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class ManualkeyPayload(TypedDict, total=False):
    """
    Type hints for vpn/ipsec/manualkey payload fields.
    
    Configure IPsec manual keys.
    
    **Related Resources:**

    Dependencies (resources this endpoint references):
        - :class:`~.system.interface.InterfaceEndpoint` (via: interface)

    **Usage:**
        payload: ManualkeyPayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    name: NotRequired[str]  # IPsec tunnel name.
    interface: str  # Name of the physical, aggregate, or VLAN interface.
    remote_gw: str  # Peer gateway.
    local_gw: NotRequired[str]  # Local gateway.
    authentication: Literal[{"description": "Null", "help": "Null.", "label": "Null", "name": "null"}, {"description": "MD5", "help": "MD5.", "label": "Md5", "name": "md5"}, {"description": "SHA1", "help": "SHA1.", "label": "Sha1", "name": "sha1"}, {"description": "SHA256", "help": "SHA256.", "label": "Sha256", "name": "sha256"}, {"description": "SHA384", "help": "SHA384.", "label": "Sha384", "name": "sha384"}, {"description": "SHA512", "help": "SHA512.", "label": "Sha512", "name": "sha512"}]  # Authentication algorithm. Must be the same for both ends of 
    encryption: Literal[{"description": "Null", "help": "Null.", "label": "Null", "name": "null"}, {"description": "DES", "help": "DES.", "label": "Des", "name": "des"}, {"description": "3DES", "help": "3DES.", "label": "3Des", "name": "3des"}, {"description": "AES128", "help": "AES128.", "label": "Aes128", "name": "aes128"}, {"description": "AES192", "help": "AES192.", "label": "Aes192", "name": "aes192"}, {"description": "AES256", "help": "AES256.", "label": "Aes256", "name": "aes256"}, {"description": "ARIA128", "help": "ARIA128.", "label": "Aria128", "name": "aria128"}, {"description": "ARIA192", "help": "ARIA192.", "label": "Aria192", "name": "aria192"}, {"description": "ARIA256", "help": "ARIA256.", "label": "Aria256", "name": "aria256"}, {"description": "Seed", "help": "Seed.", "label": "Seed", "name": "seed"}]  # Encryption algorithm. Must be the same for both ends of the 
    authkey: str  # Hexadecimal authentication key in 16-digit (8-byte) segments
    enckey: str  # Hexadecimal encryption key in 16-digit (8-byte) segments sep
    localspi: str  # Local SPI, a hexadecimal 8-digit (4-byte) tag. Discerns betw
    remotespi: str  # Remote SPI, a hexadecimal 8-digit (4-byte) tag. Discerns bet
    npu_offload: NotRequired[Literal[{"description": "Enable NPU offloading", "help": "Enable NPU offloading.", "label": "Enable", "name": "enable"}, {"description": "Disable NPU offloading", "help": "Disable NPU offloading.", "label": "Disable", "name": "disable"}]]  # Enable/disable NPU offloading.


class Manualkey:
    """
    Configure IPsec manual keys.
    
    Path: vpn/ipsec/manualkey
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
        payload_dict: ManualkeyPayload | None = ...,
        name: str | None = ...,
        interface: str | None = ...,
        remote_gw: str | None = ...,
        local_gw: str | None = ...,
        authentication: Literal[{"description": "Null", "help": "Null.", "label": "Null", "name": "null"}, {"description": "MD5", "help": "MD5.", "label": "Md5", "name": "md5"}, {"description": "SHA1", "help": "SHA1.", "label": "Sha1", "name": "sha1"}, {"description": "SHA256", "help": "SHA256.", "label": "Sha256", "name": "sha256"}, {"description": "SHA384", "help": "SHA384.", "label": "Sha384", "name": "sha384"}, {"description": "SHA512", "help": "SHA512.", "label": "Sha512", "name": "sha512"}] | None = ...,
        encryption: Literal[{"description": "Null", "help": "Null.", "label": "Null", "name": "null"}, {"description": "DES", "help": "DES.", "label": "Des", "name": "des"}, {"description": "3DES", "help": "3DES.", "label": "3Des", "name": "3des"}, {"description": "AES128", "help": "AES128.", "label": "Aes128", "name": "aes128"}, {"description": "AES192", "help": "AES192.", "label": "Aes192", "name": "aes192"}, {"description": "AES256", "help": "AES256.", "label": "Aes256", "name": "aes256"}, {"description": "ARIA128", "help": "ARIA128.", "label": "Aria128", "name": "aria128"}, {"description": "ARIA192", "help": "ARIA192.", "label": "Aria192", "name": "aria192"}, {"description": "ARIA256", "help": "ARIA256.", "label": "Aria256", "name": "aria256"}, {"description": "Seed", "help": "Seed.", "label": "Seed", "name": "seed"}] | None = ...,
        authkey: str | None = ...,
        enckey: str | None = ...,
        localspi: str | None = ...,
        remotespi: str | None = ...,
        npu_offload: Literal[{"description": "Enable NPU offloading", "help": "Enable NPU offloading.", "label": "Enable", "name": "enable"}, {"description": "Disable NPU offloading", "help": "Disable NPU offloading.", "label": "Disable", "name": "disable"}] | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: ManualkeyPayload | None = ...,
        name: str | None = ...,
        interface: str | None = ...,
        remote_gw: str | None = ...,
        local_gw: str | None = ...,
        authentication: Literal[{"description": "Null", "help": "Null.", "label": "Null", "name": "null"}, {"description": "MD5", "help": "MD5.", "label": "Md5", "name": "md5"}, {"description": "SHA1", "help": "SHA1.", "label": "Sha1", "name": "sha1"}, {"description": "SHA256", "help": "SHA256.", "label": "Sha256", "name": "sha256"}, {"description": "SHA384", "help": "SHA384.", "label": "Sha384", "name": "sha384"}, {"description": "SHA512", "help": "SHA512.", "label": "Sha512", "name": "sha512"}] | None = ...,
        encryption: Literal[{"description": "Null", "help": "Null.", "label": "Null", "name": "null"}, {"description": "DES", "help": "DES.", "label": "Des", "name": "des"}, {"description": "3DES", "help": "3DES.", "label": "3Des", "name": "3des"}, {"description": "AES128", "help": "AES128.", "label": "Aes128", "name": "aes128"}, {"description": "AES192", "help": "AES192.", "label": "Aes192", "name": "aes192"}, {"description": "AES256", "help": "AES256.", "label": "Aes256", "name": "aes256"}, {"description": "ARIA128", "help": "ARIA128.", "label": "Aria128", "name": "aria128"}, {"description": "ARIA192", "help": "ARIA192.", "label": "Aria192", "name": "aria192"}, {"description": "ARIA256", "help": "ARIA256.", "label": "Aria256", "name": "aria256"}, {"description": "Seed", "help": "Seed.", "label": "Seed", "name": "seed"}] | None = ...,
        authkey: str | None = ...,
        enckey: str | None = ...,
        localspi: str | None = ...,
        remotespi: str | None = ...,
        npu_offload: Literal[{"description": "Enable NPU offloading", "help": "Enable NPU offloading.", "label": "Enable", "name": "enable"}, {"description": "Disable NPU offloading", "help": "Disable NPU offloading.", "label": "Disable", "name": "disable"}] | None = ...,
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
        payload_dict: ManualkeyPayload | None = ...,
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
    "Manualkey",
    "ManualkeyPayload",
]