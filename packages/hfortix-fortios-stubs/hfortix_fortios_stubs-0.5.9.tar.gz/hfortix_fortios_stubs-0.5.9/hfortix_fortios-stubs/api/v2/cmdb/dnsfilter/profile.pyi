from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class ProfilePayload(TypedDict, total=False):
    """
    Type hints for dnsfilter/profile payload fields.
    
    Configure DNS domain filter profile.
    
    **Usage:**
        payload: ProfilePayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    name: str  # Profile name.
    comment: NotRequired[str]  # Comment.
    domain_filter: NotRequired[str]  # Domain filter settings.
    ftgd_dns: NotRequired[str]  # FortiGuard DNS Filter settings.
    log_all_domain: NotRequired[Literal[{"description": "Enable logging of all domains visited", "help": "Enable logging of all domains visited.", "label": "Enable", "name": "enable"}, {"description": "Disable logging of all domains visited", "help": "Disable logging of all domains visited.", "label": "Disable", "name": "disable"}]]  # Enable/disable logging of all domains visited (detailed DNS 
    sdns_ftgd_err_log: NotRequired[Literal[{"description": "Enable FortiGuard SDNS rating error logging", "help": "Enable FortiGuard SDNS rating error logging.", "label": "Enable", "name": "enable"}, {"description": "Disable FortiGuard SDNS rating error logging", "help": "Disable FortiGuard SDNS rating error logging.", "label": "Disable", "name": "disable"}]]  # Enable/disable FortiGuard SDNS rating error logging.
    sdns_domain_log: NotRequired[Literal[{"description": "Enable domain filtering and botnet domain logging", "help": "Enable domain filtering and botnet domain logging.", "label": "Enable", "name": "enable"}, {"description": "Disable domain filtering and botnet domain logging", "help": "Disable domain filtering and botnet domain logging.", "label": "Disable", "name": "disable"}]]  # Enable/disable domain filtering and botnet domain logging.
    block_action: NotRequired[Literal[{"description": "Return NXDOMAIN for blocked domains", "help": "Return NXDOMAIN for blocked domains.", "label": "Block", "name": "block"}, {"description": "Redirect blocked domains to SDNS portal", "help": "Redirect blocked domains to SDNS portal.", "label": "Redirect", "name": "redirect"}, {"description": "Return SERVFAIL for blocked domains", "help": "Return SERVFAIL for blocked domains.", "label": "Block Sevrfail", "name": "block-sevrfail"}]]  # Action to take for blocked domains.
    redirect_portal: NotRequired[str]  # IPv4 address of the SDNS redirect portal.
    redirect_portal6: NotRequired[str]  # IPv6 address of the SDNS redirect portal.
    block_botnet: NotRequired[Literal[{"description": "Disable blocking botnet C\u0026C DNS lookups", "help": "Disable blocking botnet C\u0026C DNS lookups.", "label": "Disable", "name": "disable"}, {"description": "Enable blocking botnet C\u0026C DNS lookups", "help": "Enable blocking botnet C\u0026C DNS lookups.", "label": "Enable", "name": "enable"}]]  # Enable/disable blocking botnet C&C DNS lookups.
    safe_search: NotRequired[Literal[{"description": "Disable Google, Bing, YouTube, Qwant, DuckDuckGo safe search", "help": "Disable Google, Bing, YouTube, Qwant, DuckDuckGo safe search.", "label": "Disable", "name": "disable"}, {"description": "Enable Google, Bing, YouTube, Qwant, DuckDuckGo safe search", "help": "Enable Google, Bing, YouTube, Qwant, DuckDuckGo safe search.", "label": "Enable", "name": "enable"}]]  # Enable/disable Google, Bing, YouTube, Qwant, DuckDuckGo safe
    youtube_restrict: NotRequired[Literal[{"description": "Enable strict safe seach for YouTube", "help": "Enable strict safe seach for YouTube.", "label": "Strict", "name": "strict"}, {"description": "Enable moderate safe search for YouTube", "help": "Enable moderate safe search for YouTube.", "label": "Moderate", "name": "moderate"}, {"description": "Disable safe search for YouTube", "help": "Disable safe search for YouTube.", "label": "None", "name": "none"}]]  # Set safe search for YouTube restriction level.
    external_ip_blocklist: NotRequired[list[dict[str, Any]]]  # One or more external IP block lists.
    dns_translation: NotRequired[list[dict[str, Any]]]  # DNS translation settings.
    transparent_dns_database: NotRequired[list[dict[str, Any]]]  # Transparent DNS database zones.
    strip_ech: NotRequired[Literal[{"description": "Disable removal of the encrypted client hello service parameter from supporting DNS RRs", "help": "Disable removal of the encrypted client hello service parameter from supporting DNS RRs.", "label": "Disable", "name": "disable"}, {"description": "Enable removal of the encrypted client hello service parameter from supporting DNS RRs", "help": "Enable removal of the encrypted client hello service parameter from supporting DNS RRs.", "label": "Enable", "name": "enable"}]]  # Enable/disable removal of the encrypted client hello service


class Profile:
    """
    Configure DNS domain filter profile.
    
    Path: dnsfilter/profile
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
        payload_dict: ProfilePayload | None = ...,
        name: str | None = ...,
        comment: str | None = ...,
        domain_filter: str | None = ...,
        ftgd_dns: str | None = ...,
        log_all_domain: Literal[{"description": "Enable logging of all domains visited", "help": "Enable logging of all domains visited.", "label": "Enable", "name": "enable"}, {"description": "Disable logging of all domains visited", "help": "Disable logging of all domains visited.", "label": "Disable", "name": "disable"}] | None = ...,
        sdns_ftgd_err_log: Literal[{"description": "Enable FortiGuard SDNS rating error logging", "help": "Enable FortiGuard SDNS rating error logging.", "label": "Enable", "name": "enable"}, {"description": "Disable FortiGuard SDNS rating error logging", "help": "Disable FortiGuard SDNS rating error logging.", "label": "Disable", "name": "disable"}] | None = ...,
        sdns_domain_log: Literal[{"description": "Enable domain filtering and botnet domain logging", "help": "Enable domain filtering and botnet domain logging.", "label": "Enable", "name": "enable"}, {"description": "Disable domain filtering and botnet domain logging", "help": "Disable domain filtering and botnet domain logging.", "label": "Disable", "name": "disable"}] | None = ...,
        block_action: Literal[{"description": "Return NXDOMAIN for blocked domains", "help": "Return NXDOMAIN for blocked domains.", "label": "Block", "name": "block"}, {"description": "Redirect blocked domains to SDNS portal", "help": "Redirect blocked domains to SDNS portal.", "label": "Redirect", "name": "redirect"}, {"description": "Return SERVFAIL for blocked domains", "help": "Return SERVFAIL for blocked domains.", "label": "Block Sevrfail", "name": "block-sevrfail"}] | None = ...,
        redirect_portal: str | None = ...,
        redirect_portal6: str | None = ...,
        block_botnet: Literal[{"description": "Disable blocking botnet C\u0026C DNS lookups", "help": "Disable blocking botnet C\u0026C DNS lookups.", "label": "Disable", "name": "disable"}, {"description": "Enable blocking botnet C\u0026C DNS lookups", "help": "Enable blocking botnet C\u0026C DNS lookups.", "label": "Enable", "name": "enable"}] | None = ...,
        safe_search: Literal[{"description": "Disable Google, Bing, YouTube, Qwant, DuckDuckGo safe search", "help": "Disable Google, Bing, YouTube, Qwant, DuckDuckGo safe search.", "label": "Disable", "name": "disable"}, {"description": "Enable Google, Bing, YouTube, Qwant, DuckDuckGo safe search", "help": "Enable Google, Bing, YouTube, Qwant, DuckDuckGo safe search.", "label": "Enable", "name": "enable"}] | None = ...,
        youtube_restrict: Literal[{"description": "Enable strict safe seach for YouTube", "help": "Enable strict safe seach for YouTube.", "label": "Strict", "name": "strict"}, {"description": "Enable moderate safe search for YouTube", "help": "Enable moderate safe search for YouTube.", "label": "Moderate", "name": "moderate"}, {"description": "Disable safe search for YouTube", "help": "Disable safe search for YouTube.", "label": "None", "name": "none"}] | None = ...,
        external_ip_blocklist: list[dict[str, Any]] | None = ...,
        dns_translation: list[dict[str, Any]] | None = ...,
        transparent_dns_database: list[dict[str, Any]] | None = ...,
        strip_ech: Literal[{"description": "Disable removal of the encrypted client hello service parameter from supporting DNS RRs", "help": "Disable removal of the encrypted client hello service parameter from supporting DNS RRs.", "label": "Disable", "name": "disable"}, {"description": "Enable removal of the encrypted client hello service parameter from supporting DNS RRs", "help": "Enable removal of the encrypted client hello service parameter from supporting DNS RRs.", "label": "Enable", "name": "enable"}] | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: ProfilePayload | None = ...,
        name: str | None = ...,
        comment: str | None = ...,
        domain_filter: str | None = ...,
        ftgd_dns: str | None = ...,
        log_all_domain: Literal[{"description": "Enable logging of all domains visited", "help": "Enable logging of all domains visited.", "label": "Enable", "name": "enable"}, {"description": "Disable logging of all domains visited", "help": "Disable logging of all domains visited.", "label": "Disable", "name": "disable"}] | None = ...,
        sdns_ftgd_err_log: Literal[{"description": "Enable FortiGuard SDNS rating error logging", "help": "Enable FortiGuard SDNS rating error logging.", "label": "Enable", "name": "enable"}, {"description": "Disable FortiGuard SDNS rating error logging", "help": "Disable FortiGuard SDNS rating error logging.", "label": "Disable", "name": "disable"}] | None = ...,
        sdns_domain_log: Literal[{"description": "Enable domain filtering and botnet domain logging", "help": "Enable domain filtering and botnet domain logging.", "label": "Enable", "name": "enable"}, {"description": "Disable domain filtering and botnet domain logging", "help": "Disable domain filtering and botnet domain logging.", "label": "Disable", "name": "disable"}] | None = ...,
        block_action: Literal[{"description": "Return NXDOMAIN for blocked domains", "help": "Return NXDOMAIN for blocked domains.", "label": "Block", "name": "block"}, {"description": "Redirect blocked domains to SDNS portal", "help": "Redirect blocked domains to SDNS portal.", "label": "Redirect", "name": "redirect"}, {"description": "Return SERVFAIL for blocked domains", "help": "Return SERVFAIL for blocked domains.", "label": "Block Sevrfail", "name": "block-sevrfail"}] | None = ...,
        redirect_portal: str | None = ...,
        redirect_portal6: str | None = ...,
        block_botnet: Literal[{"description": "Disable blocking botnet C\u0026C DNS lookups", "help": "Disable blocking botnet C\u0026C DNS lookups.", "label": "Disable", "name": "disable"}, {"description": "Enable blocking botnet C\u0026C DNS lookups", "help": "Enable blocking botnet C\u0026C DNS lookups.", "label": "Enable", "name": "enable"}] | None = ...,
        safe_search: Literal[{"description": "Disable Google, Bing, YouTube, Qwant, DuckDuckGo safe search", "help": "Disable Google, Bing, YouTube, Qwant, DuckDuckGo safe search.", "label": "Disable", "name": "disable"}, {"description": "Enable Google, Bing, YouTube, Qwant, DuckDuckGo safe search", "help": "Enable Google, Bing, YouTube, Qwant, DuckDuckGo safe search.", "label": "Enable", "name": "enable"}] | None = ...,
        youtube_restrict: Literal[{"description": "Enable strict safe seach for YouTube", "help": "Enable strict safe seach for YouTube.", "label": "Strict", "name": "strict"}, {"description": "Enable moderate safe search for YouTube", "help": "Enable moderate safe search for YouTube.", "label": "Moderate", "name": "moderate"}, {"description": "Disable safe search for YouTube", "help": "Disable safe search for YouTube.", "label": "None", "name": "none"}] | None = ...,
        external_ip_blocklist: list[dict[str, Any]] | None = ...,
        dns_translation: list[dict[str, Any]] | None = ...,
        transparent_dns_database: list[dict[str, Any]] | None = ...,
        strip_ech: Literal[{"description": "Disable removal of the encrypted client hello service parameter from supporting DNS RRs", "help": "Disable removal of the encrypted client hello service parameter from supporting DNS RRs.", "label": "Disable", "name": "disable"}, {"description": "Enable removal of the encrypted client hello service parameter from supporting DNS RRs", "help": "Enable removal of the encrypted client hello service parameter from supporting DNS RRs.", "label": "Enable", "name": "enable"}] | None = ...,
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
        payload_dict: ProfilePayload | None = ...,
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
    "Profile",
    "ProfilePayload",
]