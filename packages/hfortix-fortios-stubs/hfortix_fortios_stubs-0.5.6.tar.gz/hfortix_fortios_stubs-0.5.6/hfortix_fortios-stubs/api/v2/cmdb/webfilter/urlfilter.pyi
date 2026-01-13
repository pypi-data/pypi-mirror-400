from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class UrlfilterPayload(TypedDict, total=False):
    """
    Type hints for webfilter/urlfilter payload fields.
    
    Configure URL filter lists.
    
    **Usage:**
        payload: UrlfilterPayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    id: int  # ID.
    name: str  # Name of URL filter list.
    comment: NotRequired[str]  # Optional comments.
    one_arm_ips_urlfilter: NotRequired[Literal[{"description": "Enable DNS resolver for one-arm IPS URL filter operation", "help": "Enable DNS resolver for one-arm IPS URL filter operation.", "label": "Enable", "name": "enable"}, {"description": "Disable DNS resolver for one-arm IPS URL filter operation", "help": "Disable DNS resolver for one-arm IPS URL filter operation.", "label": "Disable", "name": "disable"}]]  # Enable/disable DNS resolver for one-arm IPS URL filter opera
    ip_addr_block: NotRequired[Literal[{"description": "Enable blocking URLs when the hostname appears as an IP address", "help": "Enable blocking URLs when the hostname appears as an IP address.", "label": "Enable", "name": "enable"}, {"description": "Disable blocking URLs when the hostname appears as an IP address", "help": "Disable blocking URLs when the hostname appears as an IP address.", "label": "Disable", "name": "disable"}]]  # Enable/disable blocking URLs when the hostname appears as an
    ip4_mapped_ip6: NotRequired[Literal[{"description": "Enable matching IPv4 mapped IPv6 URLs", "help": "Enable matching IPv4 mapped IPv6 URLs.", "label": "Enable", "name": "enable"}, {"description": "Disable matching IPv4 mapped IPv6 URLs", "help": "Disable matching IPv4 mapped IPv6 URLs.", "label": "Disable", "name": "disable"}]]  # Enable/disable matching of IPv4 mapped IPv6 URLs.
    include_subdomains: NotRequired[Literal[{"description": "Enable matching subdomains", "help": "Enable matching subdomains. Applies only to simple type.", "label": "Enable", "name": "enable"}, {"description": "Disable matching subdomains", "help": "Disable matching subdomains. Applies only to simple type.", "label": "Disable", "name": "disable"}]]  # Enable/disable matching subdomains. Applies only to simple t
    entries: list[dict[str, Any]]  # URL filter entries.


class Urlfilter:
    """
    Configure URL filter lists.
    
    Path: webfilter/urlfilter
    Category: cmdb
    Primary Key: id
    """
    
    # Overloads for get() with response_mode="object"
    @overload
    def get(
        self,
        id: int | None = ...,
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
        id: int,
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
        id: int | None = ...,
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
        id: int | None = ...,
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
        id: int | None = ...,
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
        payload_dict: UrlfilterPayload | None = ...,
        id: int | None = ...,
        name: str | None = ...,
        comment: str | None = ...,
        one_arm_ips_urlfilter: Literal[{"description": "Enable DNS resolver for one-arm IPS URL filter operation", "help": "Enable DNS resolver for one-arm IPS URL filter operation.", "label": "Enable", "name": "enable"}, {"description": "Disable DNS resolver for one-arm IPS URL filter operation", "help": "Disable DNS resolver for one-arm IPS URL filter operation.", "label": "Disable", "name": "disable"}] | None = ...,
        ip_addr_block: Literal[{"description": "Enable blocking URLs when the hostname appears as an IP address", "help": "Enable blocking URLs when the hostname appears as an IP address.", "label": "Enable", "name": "enable"}, {"description": "Disable blocking URLs when the hostname appears as an IP address", "help": "Disable blocking URLs when the hostname appears as an IP address.", "label": "Disable", "name": "disable"}] | None = ...,
        ip4_mapped_ip6: Literal[{"description": "Enable matching IPv4 mapped IPv6 URLs", "help": "Enable matching IPv4 mapped IPv6 URLs.", "label": "Enable", "name": "enable"}, {"description": "Disable matching IPv4 mapped IPv6 URLs", "help": "Disable matching IPv4 mapped IPv6 URLs.", "label": "Disable", "name": "disable"}] | None = ...,
        include_subdomains: Literal[{"description": "Enable matching subdomains", "help": "Enable matching subdomains. Applies only to simple type.", "label": "Enable", "name": "enable"}, {"description": "Disable matching subdomains", "help": "Disable matching subdomains. Applies only to simple type.", "label": "Disable", "name": "disable"}] | None = ...,
        entries: list[dict[str, Any]] | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: UrlfilterPayload | None = ...,
        id: int | None = ...,
        name: str | None = ...,
        comment: str | None = ...,
        one_arm_ips_urlfilter: Literal[{"description": "Enable DNS resolver for one-arm IPS URL filter operation", "help": "Enable DNS resolver for one-arm IPS URL filter operation.", "label": "Enable", "name": "enable"}, {"description": "Disable DNS resolver for one-arm IPS URL filter operation", "help": "Disable DNS resolver for one-arm IPS URL filter operation.", "label": "Disable", "name": "disable"}] | None = ...,
        ip_addr_block: Literal[{"description": "Enable blocking URLs when the hostname appears as an IP address", "help": "Enable blocking URLs when the hostname appears as an IP address.", "label": "Enable", "name": "enable"}, {"description": "Disable blocking URLs when the hostname appears as an IP address", "help": "Disable blocking URLs when the hostname appears as an IP address.", "label": "Disable", "name": "disable"}] | None = ...,
        ip4_mapped_ip6: Literal[{"description": "Enable matching IPv4 mapped IPv6 URLs", "help": "Enable matching IPv4 mapped IPv6 URLs.", "label": "Enable", "name": "enable"}, {"description": "Disable matching IPv4 mapped IPv6 URLs", "help": "Disable matching IPv4 mapped IPv6 URLs.", "label": "Disable", "name": "disable"}] | None = ...,
        include_subdomains: Literal[{"description": "Enable matching subdomains", "help": "Enable matching subdomains. Applies only to simple type.", "label": "Enable", "name": "enable"}, {"description": "Disable matching subdomains", "help": "Disable matching subdomains. Applies only to simple type.", "label": "Disable", "name": "disable"}] | None = ...,
        entries: list[dict[str, Any]] | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def delete(
        self,
        id: int | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def exists(
        self,
        id: int,
        vdom: str | bool | None = ...,
    ) -> Union[bool, Coroutine[Any, Any, bool]]: ...
    
    def set(
        self,
        payload_dict: UrlfilterPayload | None = ...,
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
    "Urlfilter",
    "UrlfilterPayload",
]