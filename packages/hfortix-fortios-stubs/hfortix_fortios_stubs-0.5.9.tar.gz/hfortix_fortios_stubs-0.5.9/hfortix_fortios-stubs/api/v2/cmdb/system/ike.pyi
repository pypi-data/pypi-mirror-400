from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class IkePayload(TypedDict, total=False):
    """
    Type hints for system/ike payload fields.
    
    Configure IKE global attributes.
    
    **Usage:**
        payload: IkePayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    embryonic_limit: NotRequired[int]  # Maximum number of IPsec tunnels to negotiate simultaneously.
    dh_multiprocess: NotRequired[Literal[{"description": "Enable multiprocess Diffie-Hellman for IKE", "help": "Enable multiprocess Diffie-Hellman for IKE.", "label": "Enable", "name": "enable"}, {"description": "Disable multiprocess Diffie-Hellman for IKE", "help": "Disable multiprocess Diffie-Hellman for IKE.", "label": "Disable", "name": "disable"}]]  # Enable/disable multiprocess Diffie-Hellman daemon for IKE.
    dh_worker_count: NotRequired[int]  # Number of Diffie-Hellman workers to start.
    dh_mode: NotRequired[Literal[{"description": "Prefer CPU to perform Diffie-Hellman calculations", "help": "Prefer CPU to perform Diffie-Hellman calculations.", "label": "Software", "name": "software"}, {"description": "Prefer CPX to perform Diffie-Hellman calculations", "help": "Prefer CPX to perform Diffie-Hellman calculations.", "label": "Hardware", "name": "hardware"}]]  # Use software (CPU) or hardware (CPX) to perform Diffie-Hellm
    dh_keypair_cache: NotRequired[Literal[{"description": "Enable Diffie-Hellman key pair cache", "help": "Enable Diffie-Hellman key pair cache.", "label": "Enable", "name": "enable"}, {"description": "Disable Diffie-Hellman key pair cache", "help": "Disable Diffie-Hellman key pair cache.", "label": "Disable", "name": "disable"}]]  # Enable/disable Diffie-Hellman key pair cache.
    dh_keypair_count: NotRequired[int]  # Number of key pairs to pre-generate for each Diffie-Hellman 
    dh_keypair_throttle: NotRequired[Literal[{"description": "Enable Diffie-Hellman key pair cache CPU throttling", "help": "Enable Diffie-Hellman key pair cache CPU throttling.", "label": "Enable", "name": "enable"}, {"description": "Disable Diffie-Hellman key pair cache CPU throttling", "help": "Disable Diffie-Hellman key pair cache CPU throttling.", "label": "Disable", "name": "disable"}]]  # Enable/disable Diffie-Hellman key pair cache CPU throttling.
    dh_group_1: NotRequired[str]  # Diffie-Hellman group 1 (MODP-768).
    dh_group_2: NotRequired[str]  # Diffie-Hellman group 2 (MODP-1024).
    dh_group_5: NotRequired[str]  # Diffie-Hellman group 5 (MODP-1536).
    dh_group_14: NotRequired[str]  # Diffie-Hellman group 14 (MODP-2048).
    dh_group_15: NotRequired[str]  # Diffie-Hellman group 15 (MODP-3072).
    dh_group_16: NotRequired[str]  # Diffie-Hellman group 16 (MODP-4096).
    dh_group_17: NotRequired[str]  # Diffie-Hellman group 17 (MODP-6144).
    dh_group_18: NotRequired[str]  # Diffie-Hellman group 18 (MODP-8192).
    dh_group_19: NotRequired[str]  # Diffie-Hellman group 19 (EC-P256).
    dh_group_20: NotRequired[str]  # Diffie-Hellman group 20 (EC-P384).
    dh_group_21: NotRequired[str]  # Diffie-Hellman group 21 (EC-P521).
    dh_group_27: NotRequired[str]  # Diffie-Hellman group 27 (EC-P224BP).
    dh_group_28: NotRequired[str]  # Diffie-Hellman group 28 (EC-P256BP).
    dh_group_29: NotRequired[str]  # Diffie-Hellman group 29 (EC-P384BP).
    dh_group_30: NotRequired[str]  # Diffie-Hellman group 30 (EC-P512BP).
    dh_group_31: NotRequired[str]  # Diffie-Hellman group 31 (EC-X25519).
    dh_group_32: NotRequired[str]  # Diffie-Hellman group 32 (EC-X448).


class Ike:
    """
    Configure IKE global attributes.
    
    Path: system/ike
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
        payload_dict: IkePayload | None = ...,
        embryonic_limit: int | None = ...,
        dh_multiprocess: Literal[{"description": "Enable multiprocess Diffie-Hellman for IKE", "help": "Enable multiprocess Diffie-Hellman for IKE.", "label": "Enable", "name": "enable"}, {"description": "Disable multiprocess Diffie-Hellman for IKE", "help": "Disable multiprocess Diffie-Hellman for IKE.", "label": "Disable", "name": "disable"}] | None = ...,
        dh_worker_count: int | None = ...,
        dh_mode: Literal[{"description": "Prefer CPU to perform Diffie-Hellman calculations", "help": "Prefer CPU to perform Diffie-Hellman calculations.", "label": "Software", "name": "software"}, {"description": "Prefer CPX to perform Diffie-Hellman calculations", "help": "Prefer CPX to perform Diffie-Hellman calculations.", "label": "Hardware", "name": "hardware"}] | None = ...,
        dh_keypair_cache: Literal[{"description": "Enable Diffie-Hellman key pair cache", "help": "Enable Diffie-Hellman key pair cache.", "label": "Enable", "name": "enable"}, {"description": "Disable Diffie-Hellman key pair cache", "help": "Disable Diffie-Hellman key pair cache.", "label": "Disable", "name": "disable"}] | None = ...,
        dh_keypair_count: int | None = ...,
        dh_keypair_throttle: Literal[{"description": "Enable Diffie-Hellman key pair cache CPU throttling", "help": "Enable Diffie-Hellman key pair cache CPU throttling.", "label": "Enable", "name": "enable"}, {"description": "Disable Diffie-Hellman key pair cache CPU throttling", "help": "Disable Diffie-Hellman key pair cache CPU throttling.", "label": "Disable", "name": "disable"}] | None = ...,
        dh_group_1: str | None = ...,
        dh_group_2: str | None = ...,
        dh_group_5: str | None = ...,
        dh_group_14: str | None = ...,
        dh_group_15: str | None = ...,
        dh_group_16: str | None = ...,
        dh_group_17: str | None = ...,
        dh_group_18: str | None = ...,
        dh_group_19: str | None = ...,
        dh_group_20: str | None = ...,
        dh_group_21: str | None = ...,
        dh_group_27: str | None = ...,
        dh_group_28: str | None = ...,
        dh_group_29: str | None = ...,
        dh_group_30: str | None = ...,
        dh_group_31: str | None = ...,
        dh_group_32: str | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: IkePayload | None = ...,
        embryonic_limit: int | None = ...,
        dh_multiprocess: Literal[{"description": "Enable multiprocess Diffie-Hellman for IKE", "help": "Enable multiprocess Diffie-Hellman for IKE.", "label": "Enable", "name": "enable"}, {"description": "Disable multiprocess Diffie-Hellman for IKE", "help": "Disable multiprocess Diffie-Hellman for IKE.", "label": "Disable", "name": "disable"}] | None = ...,
        dh_worker_count: int | None = ...,
        dh_mode: Literal[{"description": "Prefer CPU to perform Diffie-Hellman calculations", "help": "Prefer CPU to perform Diffie-Hellman calculations.", "label": "Software", "name": "software"}, {"description": "Prefer CPX to perform Diffie-Hellman calculations", "help": "Prefer CPX to perform Diffie-Hellman calculations.", "label": "Hardware", "name": "hardware"}] | None = ...,
        dh_keypair_cache: Literal[{"description": "Enable Diffie-Hellman key pair cache", "help": "Enable Diffie-Hellman key pair cache.", "label": "Enable", "name": "enable"}, {"description": "Disable Diffie-Hellman key pair cache", "help": "Disable Diffie-Hellman key pair cache.", "label": "Disable", "name": "disable"}] | None = ...,
        dh_keypair_count: int | None = ...,
        dh_keypair_throttle: Literal[{"description": "Enable Diffie-Hellman key pair cache CPU throttling", "help": "Enable Diffie-Hellman key pair cache CPU throttling.", "label": "Enable", "name": "enable"}, {"description": "Disable Diffie-Hellman key pair cache CPU throttling", "help": "Disable Diffie-Hellman key pair cache CPU throttling.", "label": "Disable", "name": "disable"}] | None = ...,
        dh_group_1: str | None = ...,
        dh_group_2: str | None = ...,
        dh_group_5: str | None = ...,
        dh_group_14: str | None = ...,
        dh_group_15: str | None = ...,
        dh_group_16: str | None = ...,
        dh_group_17: str | None = ...,
        dh_group_18: str | None = ...,
        dh_group_19: str | None = ...,
        dh_group_20: str | None = ...,
        dh_group_21: str | None = ...,
        dh_group_27: str | None = ...,
        dh_group_28: str | None = ...,
        dh_group_29: str | None = ...,
        dh_group_30: str | None = ...,
        dh_group_31: str | None = ...,
        dh_group_32: str | None = ...,
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
        payload_dict: IkePayload | None = ...,
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
    "Ike",
    "IkePayload",
]