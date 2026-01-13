from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class ManualkeyInterfacePayload(TypedDict, total=False):
    """
    Type hints for vpn/ipsec/manualkey_interface payload fields.
    
    Configure IPsec manual keys.
    
    **Related Resources:**

    Dependencies (resources this endpoint references):
        - :class:`~.system.interface.InterfaceEndpoint` (via: interface)

    **Usage:**
        payload: ManualkeyInterfacePayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    name: NotRequired[str]  # IPsec tunnel name.
    interface: str  # Name of the physical, aggregate, or VLAN interface.
    ip_version: NotRequired[Literal[{"description": "Use IPv4 addressing for gateways", "help": "Use IPv4 addressing for gateways.", "label": "4", "name": "4"}, {"description": "Use IPv6 addressing for gateways", "help": "Use IPv6 addressing for gateways.", "label": "6", "name": "6"}]]  # IP version to use for VPN interface.
    addr_type: NotRequired[Literal[{"description": "Use IPv4 addressing for IP packets", "help": "Use IPv4 addressing for IP packets.", "label": "4", "name": "4"}, {"description": "Use IPv6 addressing for IP packets", "help": "Use IPv6 addressing for IP packets.", "label": "6", "name": "6"}]]  # IP version to use for IP packets.
    remote_gw: str  # IPv4 address of the remote gateway's external interface.
    remote_gw6: str  # Remote IPv6 address of VPN gateway.
    local_gw: NotRequired[str]  # IPv4 address of the local gateway's external interface.
    local_gw6: NotRequired[str]  # Local IPv6 address of VPN gateway.
    auth_alg: Literal[{"description": "null    md5:md5    sha1:sha1    sha256:sha256    sha384:sha384    sha512:sha512", "help": "null", "label": "Null", "name": "null"}, {"help": "md5", "label": "Md5", "name": "md5"}, {"help": "sha1", "label": "Sha1", "name": "sha1"}, {"help": "sha256", "label": "Sha256", "name": "sha256"}, {"help": "sha384", "label": "Sha384", "name": "sha384"}, {"help": "sha512", "label": "Sha512", "name": "sha512"}]  # Authentication algorithm. Must be the same for both ends of 
    enc_alg: Literal[{"description": "null    des:des    3des:3des    aes128:aes128    aes192:aes192    aes256:aes256    aria128:aria128    aria192:aria192    aria256:aria256    seed:seed", "help": "null", "label": "Null", "name": "null"}, {"help": "des", "label": "Des", "name": "des"}, {"help": "3des", "label": "3Des", "name": "3des"}, {"help": "aes128", "label": "Aes128", "name": "aes128"}, {"help": "aes192", "label": "Aes192", "name": "aes192"}, {"help": "aes256", "label": "Aes256", "name": "aes256"}, {"help": "aria128", "label": "Aria128", "name": "aria128"}, {"help": "aria192", "label": "Aria192", "name": "aria192"}, {"help": "aria256", "label": "Aria256", "name": "aria256"}, {"help": "seed", "label": "Seed", "name": "seed"}]  # Encryption algorithm. Must be the same for both ends of the 
    auth_key: str  # Hexadecimal authentication key in 16-digit (8-byte) segments
    enc_key: str  # Hexadecimal encryption key in 16-digit (8-byte) segments sep
    local_spi: str  # Local SPI, a hexadecimal 8-digit (4-byte) tag. Discerns betw
    remote_spi: str  # Remote SPI, a hexadecimal 8-digit (4-byte) tag. Discerns bet
    npu_offload: NotRequired[Literal[{"description": "Enable NPU offloading", "help": "Enable NPU offloading.", "label": "Enable", "name": "enable"}, {"description": "Disable NPU offloading", "help": "Disable NPU offloading.", "label": "Disable", "name": "disable"}]]  # Enable/disable offloading IPsec VPN manual key sessions to N


class ManualkeyInterface:
    """
    Configure IPsec manual keys.
    
    Path: vpn/ipsec/manualkey_interface
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
        payload_dict: ManualkeyInterfacePayload | None = ...,
        name: str | None = ...,
        interface: str | None = ...,
        ip_version: Literal[{"description": "Use IPv4 addressing for gateways", "help": "Use IPv4 addressing for gateways.", "label": "4", "name": "4"}, {"description": "Use IPv6 addressing for gateways", "help": "Use IPv6 addressing for gateways.", "label": "6", "name": "6"}] | None = ...,
        addr_type: Literal[{"description": "Use IPv4 addressing for IP packets", "help": "Use IPv4 addressing for IP packets.", "label": "4", "name": "4"}, {"description": "Use IPv6 addressing for IP packets", "help": "Use IPv6 addressing for IP packets.", "label": "6", "name": "6"}] | None = ...,
        remote_gw: str | None = ...,
        remote_gw6: str | None = ...,
        local_gw: str | None = ...,
        local_gw6: str | None = ...,
        auth_alg: Literal[{"description": "null    md5:md5    sha1:sha1    sha256:sha256    sha384:sha384    sha512:sha512", "help": "null", "label": "Null", "name": "null"}, {"help": "md5", "label": "Md5", "name": "md5"}, {"help": "sha1", "label": "Sha1", "name": "sha1"}, {"help": "sha256", "label": "Sha256", "name": "sha256"}, {"help": "sha384", "label": "Sha384", "name": "sha384"}, {"help": "sha512", "label": "Sha512", "name": "sha512"}] | None = ...,
        enc_alg: Literal[{"description": "null    des:des    3des:3des    aes128:aes128    aes192:aes192    aes256:aes256    aria128:aria128    aria192:aria192    aria256:aria256    seed:seed", "help": "null", "label": "Null", "name": "null"}, {"help": "des", "label": "Des", "name": "des"}, {"help": "3des", "label": "3Des", "name": "3des"}, {"help": "aes128", "label": "Aes128", "name": "aes128"}, {"help": "aes192", "label": "Aes192", "name": "aes192"}, {"help": "aes256", "label": "Aes256", "name": "aes256"}, {"help": "aria128", "label": "Aria128", "name": "aria128"}, {"help": "aria192", "label": "Aria192", "name": "aria192"}, {"help": "aria256", "label": "Aria256", "name": "aria256"}, {"help": "seed", "label": "Seed", "name": "seed"}] | None = ...,
        auth_key: str | None = ...,
        enc_key: str | None = ...,
        local_spi: str | None = ...,
        remote_spi: str | None = ...,
        npu_offload: Literal[{"description": "Enable NPU offloading", "help": "Enable NPU offloading.", "label": "Enable", "name": "enable"}, {"description": "Disable NPU offloading", "help": "Disable NPU offloading.", "label": "Disable", "name": "disable"}] | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: ManualkeyInterfacePayload | None = ...,
        name: str | None = ...,
        interface: str | None = ...,
        ip_version: Literal[{"description": "Use IPv4 addressing for gateways", "help": "Use IPv4 addressing for gateways.", "label": "4", "name": "4"}, {"description": "Use IPv6 addressing for gateways", "help": "Use IPv6 addressing for gateways.", "label": "6", "name": "6"}] | None = ...,
        addr_type: Literal[{"description": "Use IPv4 addressing for IP packets", "help": "Use IPv4 addressing for IP packets.", "label": "4", "name": "4"}, {"description": "Use IPv6 addressing for IP packets", "help": "Use IPv6 addressing for IP packets.", "label": "6", "name": "6"}] | None = ...,
        remote_gw: str | None = ...,
        remote_gw6: str | None = ...,
        local_gw: str | None = ...,
        local_gw6: str | None = ...,
        auth_alg: Literal[{"description": "null    md5:md5    sha1:sha1    sha256:sha256    sha384:sha384    sha512:sha512", "help": "null", "label": "Null", "name": "null"}, {"help": "md5", "label": "Md5", "name": "md5"}, {"help": "sha1", "label": "Sha1", "name": "sha1"}, {"help": "sha256", "label": "Sha256", "name": "sha256"}, {"help": "sha384", "label": "Sha384", "name": "sha384"}, {"help": "sha512", "label": "Sha512", "name": "sha512"}] | None = ...,
        enc_alg: Literal[{"description": "null    des:des    3des:3des    aes128:aes128    aes192:aes192    aes256:aes256    aria128:aria128    aria192:aria192    aria256:aria256    seed:seed", "help": "null", "label": "Null", "name": "null"}, {"help": "des", "label": "Des", "name": "des"}, {"help": "3des", "label": "3Des", "name": "3des"}, {"help": "aes128", "label": "Aes128", "name": "aes128"}, {"help": "aes192", "label": "Aes192", "name": "aes192"}, {"help": "aes256", "label": "Aes256", "name": "aes256"}, {"help": "aria128", "label": "Aria128", "name": "aria128"}, {"help": "aria192", "label": "Aria192", "name": "aria192"}, {"help": "aria256", "label": "Aria256", "name": "aria256"}, {"help": "seed", "label": "Seed", "name": "seed"}] | None = ...,
        auth_key: str | None = ...,
        enc_key: str | None = ...,
        local_spi: str | None = ...,
        remote_spi: str | None = ...,
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
        payload_dict: ManualkeyInterfacePayload | None = ...,
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
    "ManualkeyInterface",
    "ManualkeyInterfacePayload",
]