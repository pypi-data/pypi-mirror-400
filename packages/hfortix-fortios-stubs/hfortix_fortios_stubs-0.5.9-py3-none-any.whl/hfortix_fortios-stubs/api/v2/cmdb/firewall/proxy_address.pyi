from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class ProxyAddressPayload(TypedDict, total=False):
    """
    Type hints for firewall/proxy_address payload fields.
    
    Configure web proxy address.
    
    **Related Resources:**

    Dependencies (resources this endpoint references):
        - :class:`~.firewall.address.AddressEndpoint` (via: host)
        - :class:`~.firewall.addrgrp.AddrgrpEndpoint` (via: host)
        - :class:`~.firewall.proxy-address.ProxyAddressEndpoint` (via: host)
        - :class:`~.firewall.vip.VipEndpoint` (via: host)
        - :class:`~.firewall.vipgrp.VipgrpEndpoint` (via: host)

    **Usage:**
        payload: ProxyAddressPayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    name: NotRequired[str]  # Address name.
    uuid: NotRequired[str]  # Universally Unique Identifier (UUID; automatically assigned 
    type: NotRequired[Literal[{"description": "Host regular expression", "help": "Host regular expression.", "label": "Host Regex", "name": "host-regex"}, {"description": "HTTP URL", "help": "HTTP URL.", "label": "Url", "name": "url"}, {"description": "FortiGuard URL catgegory", "help": "FortiGuard URL catgegory.", "label": "Category", "name": "category"}, {"description": "HTTP request method", "help": "HTTP request method.", "label": "Method", "name": "method"}, {"description": "HTTP request user agent", "help": "HTTP request user agent.", "label": "Ua", "name": "ua"}, {"description": "HTTP request header", "help": "HTTP request header.", "label": "Header", "name": "header"}, {"description": "HTTP advanced source criteria", "help": "HTTP advanced source criteria.", "label": "Src Advanced", "name": "src-advanced"}, {"description": "HTTP advanced destination criteria", "help": "HTTP advanced destination criteria.", "label": "Dst Advanced", "name": "dst-advanced"}, {"description": "SaaS application", "help": "SaaS application.", "label": "Saas", "name": "saas"}]]  # Proxy address type.
    host: str  # Address object for the host.
    host_regex: NotRequired[str]  # Host name as a regular expression.
    path: NotRequired[str]  # URL path as a regular expression.
    query: NotRequired[str]  # Match the query part of the URL as a regular expression.
    referrer: NotRequired[Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]]  # Enable/disable use of referrer field in the HTTP header to m
    category: NotRequired[list[dict[str, Any]]]  # FortiGuard category ID.
    method: NotRequired[Literal[{"description": "GET method", "help": "GET method.", "label": "Get", "name": "get"}, {"description": "POST method", "help": "POST method.", "label": "Post", "name": "post"}, {"description": "PUT method", "help": "PUT method.", "label": "Put", "name": "put"}, {"description": "HEAD method", "help": "HEAD method.", "label": "Head", "name": "head"}, {"description": "CONNECT method", "help": "CONNECT method.", "label": "Connect", "name": "connect"}, {"description": "TRACE method", "help": "TRACE method.", "label": "Trace", "name": "trace"}, {"description": "OPTIONS method", "help": "OPTIONS method.", "label": "Options", "name": "options"}, {"description": "DELETE method", "help": "DELETE method.", "label": "Delete", "name": "delete"}, {"description": "UPDATE method", "help": "UPDATE method.", "label": "Update", "name": "update"}, {"description": "PATCH method", "help": "PATCH method.", "label": "Patch", "name": "patch"}, {"description": "Other methods", "help": "Other methods.", "label": "Other", "name": "other"}]]  # HTTP request methods to be used.
    ua: NotRequired[Literal[{"description": "Google Chrome", "help": "Google Chrome.", "label": "Chrome", "name": "chrome"}, {"description": "Microsoft Internet Explorer or EDGE", "help": "Microsoft Internet Explorer or EDGE.", "label": "Ms", "name": "ms"}, {"description": "Mozilla Firefox", "help": "Mozilla Firefox.", "label": "Firefox", "name": "firefox"}, {"description": "Apple Safari", "help": "Apple Safari.", "label": "Safari", "name": "safari"}, {"description": "Microsoft Internet Explorer", "help": "Microsoft Internet Explorer.", "label": "Ie", "name": "ie"}, {"description": "Microsoft Edge", "help": "Microsoft Edge.", "label": "Edge", "name": "edge"}, {"description": "Other browsers", "help": "Other browsers.", "label": "Other", "name": "other"}]]  # Names of browsers to be used as user agent.
    ua_min_ver: NotRequired[str]  # Minimum version of the user agent specified in dotted notati
    ua_max_ver: NotRequired[str]  # Maximum version of the user agent specified in dotted notati
    header_name: NotRequired[str]  # Name of HTTP header.
    header: NotRequired[str]  # HTTP header name as a regular expression.
    case_sensitivity: NotRequired[Literal[{"description": "Case insensitive in pattern", "help": "Case insensitive in pattern.", "label": "Disable", "name": "disable"}, {"description": "Case sensitive in pattern", "help": "Case sensitive in pattern.", "label": "Enable", "name": "enable"}]]  # Enable to make the pattern case sensitive.
    header_group: NotRequired[list[dict[str, Any]]]  # HTTP header group.
    color: NotRequired[int]  # Integer value to determine the color of the icon in the GUI 
    tagging: NotRequired[list[dict[str, Any]]]  # Config object tagging.
    comment: NotRequired[str]  # Optional comments.
    application: list[dict[str, Any]]  # SaaS application.


class ProxyAddress:
    """
    Configure web proxy address.
    
    Path: firewall/proxy_address
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
        payload_dict: ProxyAddressPayload | None = ...,
        name: str | None = ...,
        uuid: str | None = ...,
        type: Literal[{"description": "Host regular expression", "help": "Host regular expression.", "label": "Host Regex", "name": "host-regex"}, {"description": "HTTP URL", "help": "HTTP URL.", "label": "Url", "name": "url"}, {"description": "FortiGuard URL catgegory", "help": "FortiGuard URL catgegory.", "label": "Category", "name": "category"}, {"description": "HTTP request method", "help": "HTTP request method.", "label": "Method", "name": "method"}, {"description": "HTTP request user agent", "help": "HTTP request user agent.", "label": "Ua", "name": "ua"}, {"description": "HTTP request header", "help": "HTTP request header.", "label": "Header", "name": "header"}, {"description": "HTTP advanced source criteria", "help": "HTTP advanced source criteria.", "label": "Src Advanced", "name": "src-advanced"}, {"description": "HTTP advanced destination criteria", "help": "HTTP advanced destination criteria.", "label": "Dst Advanced", "name": "dst-advanced"}, {"description": "SaaS application", "help": "SaaS application.", "label": "Saas", "name": "saas"}] | None = ...,
        host: str | None = ...,
        host_regex: str | None = ...,
        path: str | None = ...,
        query: str | None = ...,
        referrer: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        category: list[dict[str, Any]] | None = ...,
        method: Literal[{"description": "GET method", "help": "GET method.", "label": "Get", "name": "get"}, {"description": "POST method", "help": "POST method.", "label": "Post", "name": "post"}, {"description": "PUT method", "help": "PUT method.", "label": "Put", "name": "put"}, {"description": "HEAD method", "help": "HEAD method.", "label": "Head", "name": "head"}, {"description": "CONNECT method", "help": "CONNECT method.", "label": "Connect", "name": "connect"}, {"description": "TRACE method", "help": "TRACE method.", "label": "Trace", "name": "trace"}, {"description": "OPTIONS method", "help": "OPTIONS method.", "label": "Options", "name": "options"}, {"description": "DELETE method", "help": "DELETE method.", "label": "Delete", "name": "delete"}, {"description": "UPDATE method", "help": "UPDATE method.", "label": "Update", "name": "update"}, {"description": "PATCH method", "help": "PATCH method.", "label": "Patch", "name": "patch"}, {"description": "Other methods", "help": "Other methods.", "label": "Other", "name": "other"}] | None = ...,
        ua: Literal[{"description": "Google Chrome", "help": "Google Chrome.", "label": "Chrome", "name": "chrome"}, {"description": "Microsoft Internet Explorer or EDGE", "help": "Microsoft Internet Explorer or EDGE.", "label": "Ms", "name": "ms"}, {"description": "Mozilla Firefox", "help": "Mozilla Firefox.", "label": "Firefox", "name": "firefox"}, {"description": "Apple Safari", "help": "Apple Safari.", "label": "Safari", "name": "safari"}, {"description": "Microsoft Internet Explorer", "help": "Microsoft Internet Explorer.", "label": "Ie", "name": "ie"}, {"description": "Microsoft Edge", "help": "Microsoft Edge.", "label": "Edge", "name": "edge"}, {"description": "Other browsers", "help": "Other browsers.", "label": "Other", "name": "other"}] | None = ...,
        ua_min_ver: str | None = ...,
        ua_max_ver: str | None = ...,
        header_name: str | None = ...,
        header: str | None = ...,
        case_sensitivity: Literal[{"description": "Case insensitive in pattern", "help": "Case insensitive in pattern.", "label": "Disable", "name": "disable"}, {"description": "Case sensitive in pattern", "help": "Case sensitive in pattern.", "label": "Enable", "name": "enable"}] | None = ...,
        header_group: list[dict[str, Any]] | None = ...,
        color: int | None = ...,
        tagging: list[dict[str, Any]] | None = ...,
        comment: str | None = ...,
        application: list[dict[str, Any]] | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: ProxyAddressPayload | None = ...,
        name: str | None = ...,
        uuid: str | None = ...,
        type: Literal[{"description": "Host regular expression", "help": "Host regular expression.", "label": "Host Regex", "name": "host-regex"}, {"description": "HTTP URL", "help": "HTTP URL.", "label": "Url", "name": "url"}, {"description": "FortiGuard URL catgegory", "help": "FortiGuard URL catgegory.", "label": "Category", "name": "category"}, {"description": "HTTP request method", "help": "HTTP request method.", "label": "Method", "name": "method"}, {"description": "HTTP request user agent", "help": "HTTP request user agent.", "label": "Ua", "name": "ua"}, {"description": "HTTP request header", "help": "HTTP request header.", "label": "Header", "name": "header"}, {"description": "HTTP advanced source criteria", "help": "HTTP advanced source criteria.", "label": "Src Advanced", "name": "src-advanced"}, {"description": "HTTP advanced destination criteria", "help": "HTTP advanced destination criteria.", "label": "Dst Advanced", "name": "dst-advanced"}, {"description": "SaaS application", "help": "SaaS application.", "label": "Saas", "name": "saas"}] | None = ...,
        host: str | None = ...,
        host_regex: str | None = ...,
        path: str | None = ...,
        query: str | None = ...,
        referrer: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        category: list[dict[str, Any]] | None = ...,
        method: Literal[{"description": "GET method", "help": "GET method.", "label": "Get", "name": "get"}, {"description": "POST method", "help": "POST method.", "label": "Post", "name": "post"}, {"description": "PUT method", "help": "PUT method.", "label": "Put", "name": "put"}, {"description": "HEAD method", "help": "HEAD method.", "label": "Head", "name": "head"}, {"description": "CONNECT method", "help": "CONNECT method.", "label": "Connect", "name": "connect"}, {"description": "TRACE method", "help": "TRACE method.", "label": "Trace", "name": "trace"}, {"description": "OPTIONS method", "help": "OPTIONS method.", "label": "Options", "name": "options"}, {"description": "DELETE method", "help": "DELETE method.", "label": "Delete", "name": "delete"}, {"description": "UPDATE method", "help": "UPDATE method.", "label": "Update", "name": "update"}, {"description": "PATCH method", "help": "PATCH method.", "label": "Patch", "name": "patch"}, {"description": "Other methods", "help": "Other methods.", "label": "Other", "name": "other"}] | None = ...,
        ua: Literal[{"description": "Google Chrome", "help": "Google Chrome.", "label": "Chrome", "name": "chrome"}, {"description": "Microsoft Internet Explorer or EDGE", "help": "Microsoft Internet Explorer or EDGE.", "label": "Ms", "name": "ms"}, {"description": "Mozilla Firefox", "help": "Mozilla Firefox.", "label": "Firefox", "name": "firefox"}, {"description": "Apple Safari", "help": "Apple Safari.", "label": "Safari", "name": "safari"}, {"description": "Microsoft Internet Explorer", "help": "Microsoft Internet Explorer.", "label": "Ie", "name": "ie"}, {"description": "Microsoft Edge", "help": "Microsoft Edge.", "label": "Edge", "name": "edge"}, {"description": "Other browsers", "help": "Other browsers.", "label": "Other", "name": "other"}] | None = ...,
        ua_min_ver: str | None = ...,
        ua_max_ver: str | None = ...,
        header_name: str | None = ...,
        header: str | None = ...,
        case_sensitivity: Literal[{"description": "Case insensitive in pattern", "help": "Case insensitive in pattern.", "label": "Disable", "name": "disable"}, {"description": "Case sensitive in pattern", "help": "Case sensitive in pattern.", "label": "Enable", "name": "enable"}] | None = ...,
        header_group: list[dict[str, Any]] | None = ...,
        color: int | None = ...,
        tagging: list[dict[str, Any]] | None = ...,
        comment: str | None = ...,
        application: list[dict[str, Any]] | None = ...,
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
        payload_dict: ProxyAddressPayload | None = ...,
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
    "ProxyAddress",
    "ProxyAddressPayload",
]