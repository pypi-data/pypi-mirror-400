from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class SettingPayload(TypedDict, total=False):
    """
    Type hints for firewall/ssh/setting payload fields.
    
    SSH proxy settings.
    
    **Related Resources:**

    Dependencies (resources this endpoint references):
        - :class:`~.firewall.ssh.local-ca.LocalCaEndpoint` (via: caname, untrusted-caname)
        - :class:`~.firewall.ssh.local-key.LocalKeyEndpoint` (via: hostkey-dsa1024, hostkey-ecdsa256, hostkey-ecdsa384, +3 more)

    **Usage:**
        payload: SettingPayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    caname: NotRequired[str]  # CA certificate used by SSH Inspection.
    untrusted_caname: NotRequired[str]  # Untrusted CA certificate used by SSH Inspection.
    hostkey_rsa2048: NotRequired[str]  # RSA certificate used by SSH proxy.
    hostkey_dsa1024: NotRequired[str]  # DSA certificate used by SSH proxy.
    hostkey_ecdsa256: NotRequired[str]  # ECDSA nid256 certificate used by SSH proxy.
    hostkey_ecdsa384: NotRequired[str]  # ECDSA nid384 certificate used by SSH proxy.
    hostkey_ecdsa521: NotRequired[str]  # ECDSA nid384 certificate used by SSH proxy.
    hostkey_ed25519: NotRequired[str]  # ED25519 hostkey used by SSH proxy.
    host_trusted_checking: NotRequired[Literal[{"description": "Enable host key trusted checking", "help": "Enable host key trusted checking.", "label": "Enable", "name": "enable"}, {"description": "Disable host key trusted checking", "help": "Disable host key trusted checking.", "label": "Disable", "name": "disable"}]]  # Enable/disable host trusted checking.


class Setting:
    """
    SSH proxy settings.
    
    Path: firewall/ssh/setting
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
        caname: str | None = ...,
        untrusted_caname: str | None = ...,
        hostkey_rsa2048: str | None = ...,
        hostkey_dsa1024: str | None = ...,
        hostkey_ecdsa256: str | None = ...,
        hostkey_ecdsa384: str | None = ...,
        hostkey_ecdsa521: str | None = ...,
        hostkey_ed25519: str | None = ...,
        host_trusted_checking: Literal[{"description": "Enable host key trusted checking", "help": "Enable host key trusted checking.", "label": "Enable", "name": "enable"}, {"description": "Disable host key trusted checking", "help": "Disable host key trusted checking.", "label": "Disable", "name": "disable"}] | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: SettingPayload | None = ...,
        caname: str | None = ...,
        untrusted_caname: str | None = ...,
        hostkey_rsa2048: str | None = ...,
        hostkey_dsa1024: str | None = ...,
        hostkey_ecdsa256: str | None = ...,
        hostkey_ecdsa384: str | None = ...,
        hostkey_ecdsa521: str | None = ...,
        hostkey_ed25519: str | None = ...,
        host_trusted_checking: Literal[{"description": "Enable host key trusted checking", "help": "Enable host key trusted checking.", "label": "Enable", "name": "enable"}, {"description": "Disable host key trusted checking", "help": "Disable host key trusted checking.", "label": "Disable", "name": "disable"}] | None = ...,
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