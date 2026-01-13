from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class SearchEnginePayload(TypedDict, total=False):
    """
    Type hints for webfilter/search_engine payload fields.
    
    Configure web filter search engines.
    
    **Usage:**
        payload: SearchEnginePayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    name: str  # Search engine name.
    hostname: NotRequired[str]  # Hostname (regular expression).
    url: NotRequired[str]  # URL (regular expression).
    query: NotRequired[str]  # Code used to prefix a query (must end with an equals charact
    safesearch: NotRequired[Literal[{"description": "Site does not support safe search", "help": "Site does not support safe search.", "label": "Disable", "name": "disable"}, {"description": "Safe search selected with a parameter in the URL", "help": "Safe search selected with a parameter in the URL.", "label": "Url", "name": "url"}, {"description": "Safe search selected by search header (i", "help": "Safe search selected by search header (i.e. youtube.edu).", "label": "Header", "name": "header"}, {"description": "Perform URL FortiGuard check on translated URL", "help": "Perform URL FortiGuard check on translated URL.", "label": "Translate", "name": "translate"}, {"description": "Pattern to match YouTube channel ID", "help": "Pattern to match YouTube channel ID.", "label": "Yt Pattern", "name": "yt-pattern"}, {"description": "Perform IPS scan", "help": "Perform IPS scan.", "label": "Yt Scan", "name": "yt-scan"}, {"description": "Pattern to match YouTube video name", "help": "Pattern to match YouTube video name.", "label": "Yt Video", "name": "yt-video"}, {"description": "Pattern to match YouTube channel name", "help": "Pattern to match YouTube channel name.", "label": "Yt Channel", "name": "yt-channel"}]]  # Safe search method. You can disable safe search, add the saf
    charset: NotRequired[Literal[{"description": "UTF-8 encoding", "help": "UTF-8 encoding.", "label": "Utf 8", "name": "utf-8"}, {"description": "GB2312 encoding", "help": "GB2312 encoding.", "label": "Gb2312", "name": "gb2312"}]]  # Search engine charset.
    safesearch_str: NotRequired[str]  # Safe search parameter used in the URL in URL mode. In transl


class SearchEngine:
    """
    Configure web filter search engines.
    
    Path: webfilter/search_engine
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
        payload_dict: SearchEnginePayload | None = ...,
        name: str | None = ...,
        hostname: str | None = ...,
        url: str | None = ...,
        query: str | None = ...,
        safesearch: Literal[{"description": "Site does not support safe search", "help": "Site does not support safe search.", "label": "Disable", "name": "disable"}, {"description": "Safe search selected with a parameter in the URL", "help": "Safe search selected with a parameter in the URL.", "label": "Url", "name": "url"}, {"description": "Safe search selected by search header (i", "help": "Safe search selected by search header (i.e. youtube.edu).", "label": "Header", "name": "header"}, {"description": "Perform URL FortiGuard check on translated URL", "help": "Perform URL FortiGuard check on translated URL.", "label": "Translate", "name": "translate"}, {"description": "Pattern to match YouTube channel ID", "help": "Pattern to match YouTube channel ID.", "label": "Yt Pattern", "name": "yt-pattern"}, {"description": "Perform IPS scan", "help": "Perform IPS scan.", "label": "Yt Scan", "name": "yt-scan"}, {"description": "Pattern to match YouTube video name", "help": "Pattern to match YouTube video name.", "label": "Yt Video", "name": "yt-video"}, {"description": "Pattern to match YouTube channel name", "help": "Pattern to match YouTube channel name.", "label": "Yt Channel", "name": "yt-channel"}] | None = ...,
        charset: Literal[{"description": "UTF-8 encoding", "help": "UTF-8 encoding.", "label": "Utf 8", "name": "utf-8"}, {"description": "GB2312 encoding", "help": "GB2312 encoding.", "label": "Gb2312", "name": "gb2312"}] | None = ...,
        safesearch_str: str | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: SearchEnginePayload | None = ...,
        name: str | None = ...,
        hostname: str | None = ...,
        url: str | None = ...,
        query: str | None = ...,
        safesearch: Literal[{"description": "Site does not support safe search", "help": "Site does not support safe search.", "label": "Disable", "name": "disable"}, {"description": "Safe search selected with a parameter in the URL", "help": "Safe search selected with a parameter in the URL.", "label": "Url", "name": "url"}, {"description": "Safe search selected by search header (i", "help": "Safe search selected by search header (i.e. youtube.edu).", "label": "Header", "name": "header"}, {"description": "Perform URL FortiGuard check on translated URL", "help": "Perform URL FortiGuard check on translated URL.", "label": "Translate", "name": "translate"}, {"description": "Pattern to match YouTube channel ID", "help": "Pattern to match YouTube channel ID.", "label": "Yt Pattern", "name": "yt-pattern"}, {"description": "Perform IPS scan", "help": "Perform IPS scan.", "label": "Yt Scan", "name": "yt-scan"}, {"description": "Pattern to match YouTube video name", "help": "Pattern to match YouTube video name.", "label": "Yt Video", "name": "yt-video"}, {"description": "Pattern to match YouTube channel name", "help": "Pattern to match YouTube channel name.", "label": "Yt Channel", "name": "yt-channel"}] | None = ...,
        charset: Literal[{"description": "UTF-8 encoding", "help": "UTF-8 encoding.", "label": "Utf 8", "name": "utf-8"}, {"description": "GB2312 encoding", "help": "GB2312 encoding.", "label": "Gb2312", "name": "gb2312"}] | None = ...,
        safesearch_str: str | None = ...,
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
        payload_dict: SearchEnginePayload | None = ...,
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
    "SearchEngine",
    "SearchEnginePayload",
]