from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class DnsServerPayload(TypedDict, total=False):
    """
    Type hints for system/dns_server payload fields.
    
    Configure DNS servers.
    
    **Related Resources:**

    Dependencies (resources this endpoint references):
        - :class:`~.dnsfilter.profile.ProfileEndpoint` (via: dnsfilter-profile)
        - :class:`~.system.interface.InterfaceEndpoint` (via: name)

    **Usage:**
        payload: DnsServerPayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    name: NotRequired[str]  # DNS server name.
    mode: NotRequired[Literal[{"description": "Shadow DNS database and forward", "help": "Shadow DNS database and forward.", "label": "Recursive", "name": "recursive"}, {"description": "Public DNS database only", "help": "Public DNS database only.", "label": "Non Recursive", "name": "non-recursive"}, {"description": "Forward only", "help": "Forward only.", "label": "Forward Only", "name": "forward-only"}, {"description": "Recursive resolver mode", "help": "Recursive resolver mode.", "label": "Resolver", "name": "resolver"}]]  # DNS server mode.
    dnsfilter_profile: NotRequired[str]  # DNS filter profile.
    doh: NotRequired[Literal[{"description": "Enable DNS over HTTPS", "help": "Enable DNS over HTTPS.", "label": "Enable", "name": "enable"}, {"description": "Disable DNS over HTTPS", "help": "Disable DNS over HTTPS.", "label": "Disable", "name": "disable"}]]  # Enable/disable DNS over HTTPS/443 (default = disable).
    doh3: NotRequired[Literal[{"description": "Enable DNS over HTTP3/QUIC", "help": "Enable DNS over HTTP3/QUIC.", "label": "Enable", "name": "enable"}, {"description": "Disable DNS over HTTP3/QUIC", "help": "Disable DNS over HTTP3/QUIC.", "label": "Disable", "name": "disable"}]]  # Enable/disable DNS over QUIC/HTTP3/443 (default = disable).
    doq: NotRequired[Literal[{"description": "Enable DNS over QUIC", "help": "Enable DNS over QUIC.", "label": "Enable", "name": "enable"}, {"description": "Disable DNS over QUIC", "help": "Disable DNS over QUIC.", "label": "Disable", "name": "disable"}]]  # Enable/disable DNS over QUIC/853 (default = disable).


class DnsServer:
    """
    Configure DNS servers.
    
    Path: system/dns_server
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
        payload_dict: DnsServerPayload | None = ...,
        name: str | None = ...,
        mode: Literal[{"description": "Shadow DNS database and forward", "help": "Shadow DNS database and forward.", "label": "Recursive", "name": "recursive"}, {"description": "Public DNS database only", "help": "Public DNS database only.", "label": "Non Recursive", "name": "non-recursive"}, {"description": "Forward only", "help": "Forward only.", "label": "Forward Only", "name": "forward-only"}, {"description": "Recursive resolver mode", "help": "Recursive resolver mode.", "label": "Resolver", "name": "resolver"}] | None = ...,
        dnsfilter_profile: str | None = ...,
        doh: Literal[{"description": "Enable DNS over HTTPS", "help": "Enable DNS over HTTPS.", "label": "Enable", "name": "enable"}, {"description": "Disable DNS over HTTPS", "help": "Disable DNS over HTTPS.", "label": "Disable", "name": "disable"}] | None = ...,
        doh3: Literal[{"description": "Enable DNS over HTTP3/QUIC", "help": "Enable DNS over HTTP3/QUIC.", "label": "Enable", "name": "enable"}, {"description": "Disable DNS over HTTP3/QUIC", "help": "Disable DNS over HTTP3/QUIC.", "label": "Disable", "name": "disable"}] | None = ...,
        doq: Literal[{"description": "Enable DNS over QUIC", "help": "Enable DNS over QUIC.", "label": "Enable", "name": "enable"}, {"description": "Disable DNS over QUIC", "help": "Disable DNS over QUIC.", "label": "Disable", "name": "disable"}] | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: DnsServerPayload | None = ...,
        name: str | None = ...,
        mode: Literal[{"description": "Shadow DNS database and forward", "help": "Shadow DNS database and forward.", "label": "Recursive", "name": "recursive"}, {"description": "Public DNS database only", "help": "Public DNS database only.", "label": "Non Recursive", "name": "non-recursive"}, {"description": "Forward only", "help": "Forward only.", "label": "Forward Only", "name": "forward-only"}, {"description": "Recursive resolver mode", "help": "Recursive resolver mode.", "label": "Resolver", "name": "resolver"}] | None = ...,
        dnsfilter_profile: str | None = ...,
        doh: Literal[{"description": "Enable DNS over HTTPS", "help": "Enable DNS over HTTPS.", "label": "Enable", "name": "enable"}, {"description": "Disable DNS over HTTPS", "help": "Disable DNS over HTTPS.", "label": "Disable", "name": "disable"}] | None = ...,
        doh3: Literal[{"description": "Enable DNS over HTTP3/QUIC", "help": "Enable DNS over HTTP3/QUIC.", "label": "Enable", "name": "enable"}, {"description": "Disable DNS over HTTP3/QUIC", "help": "Disable DNS over HTTP3/QUIC.", "label": "Disable", "name": "disable"}] | None = ...,
        doq: Literal[{"description": "Enable DNS over QUIC", "help": "Enable DNS over QUIC.", "label": "Enable", "name": "enable"}, {"description": "Disable DNS over QUIC", "help": "Disable DNS over QUIC.", "label": "Disable", "name": "disable"}] | None = ...,
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
        payload_dict: DnsServerPayload | None = ...,
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
    "DnsServer",
    "DnsServerPayload",
]