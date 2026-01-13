from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class ExternalIdentityProviderPayload(TypedDict, total=False):
    """
    Type hints for user/external_identity_provider payload fields.
    
    Configure external identity provider.
    
    **Related Resources:**

    Dependencies (resources this endpoint references):
        - :class:`~.system.interface.InterfaceEndpoint` (via: interface)

    **Usage:**
        payload: ExternalIdentityProviderPayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    name: NotRequired[str]  # External identity provider name.
    type: Literal[{"description": "Microsoft Graph server", "help": "Microsoft Graph server.", "label": "Ms Graph", "name": "ms-graph"}]  # External identity provider type.
    version: NotRequired[Literal[{"help": "MS Graph REST API v1.0.", "label": "V1.0", "name": "v1.0"}, {"description": "MS Graph REST API beta (debug build only)", "help": "MS Graph REST API beta (debug build only).", "label": "Beta", "name": "beta"}]]  # External identity API version.
    url: NotRequired[str]  # External identity provider URL (e.g. "https://example.com:80
    user_attr_name: NotRequired[str]  # User attribute name in authentication query.
    group_attr_name: NotRequired[str]  # Group attribute name in authentication query.
    port: NotRequired[int]  # External identity provider service port number (0 to use def
    source_ip: NotRequired[str]  # Use this IPv4/v6 address to connect to the external identity
    interface_select_method: NotRequired[Literal[{"description": "Set outgoing interface automatically", "help": "Set outgoing interface automatically.", "label": "Auto", "name": "auto"}, {"description": "Set outgoing interface by SD-WAN or policy routing rules", "help": "Set outgoing interface by SD-WAN or policy routing rules.", "label": "Sdwan", "name": "sdwan"}, {"description": "Set outgoing interface manually", "help": "Set outgoing interface manually.", "label": "Specify", "name": "specify"}]]  # Specify how to select outgoing interface to reach server.
    interface: str  # Specify outgoing interface to reach server.
    vrf_select: NotRequired[int]  # VRF ID used for connection to server.
    server_identity_check: NotRequired[Literal[{"description": "Do not check server\u0027s identity against its certificate and subject alternative name(s)", "help": "Do not check server\u0027s identity against its certificate and subject alternative name(s).", "label": "Disable", "name": "disable"}, {"description": "Check server\u0027s identity against its certificate and subject alternative name(s)", "help": "Check server\u0027s identity against its certificate and subject alternative name(s).", "label": "Enable", "name": "enable"}]]  # Enable/disable server's identity check against its certifica
    timeout: NotRequired[int]  # Connection timeout value in seconds (default=5).


class ExternalIdentityProvider:
    """
    Configure external identity provider.
    
    Path: user/external_identity_provider
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
        payload_dict: ExternalIdentityProviderPayload | None = ...,
        name: str | None = ...,
        type: Literal[{"description": "Microsoft Graph server", "help": "Microsoft Graph server.", "label": "Ms Graph", "name": "ms-graph"}] | None = ...,
        version: Literal[{"help": "MS Graph REST API v1.0.", "label": "V1.0", "name": "v1.0"}, {"description": "MS Graph REST API beta (debug build only)", "help": "MS Graph REST API beta (debug build only).", "label": "Beta", "name": "beta"}] | None = ...,
        url: str | None = ...,
        user_attr_name: str | None = ...,
        group_attr_name: str | None = ...,
        port: int | None = ...,
        source_ip: str | None = ...,
        interface_select_method: Literal[{"description": "Set outgoing interface automatically", "help": "Set outgoing interface automatically.", "label": "Auto", "name": "auto"}, {"description": "Set outgoing interface by SD-WAN or policy routing rules", "help": "Set outgoing interface by SD-WAN or policy routing rules.", "label": "Sdwan", "name": "sdwan"}, {"description": "Set outgoing interface manually", "help": "Set outgoing interface manually.", "label": "Specify", "name": "specify"}] | None = ...,
        interface: str | None = ...,
        vrf_select: int | None = ...,
        server_identity_check: Literal[{"description": "Do not check server\u0027s identity against its certificate and subject alternative name(s)", "help": "Do not check server\u0027s identity against its certificate and subject alternative name(s).", "label": "Disable", "name": "disable"}, {"description": "Check server\u0027s identity against its certificate and subject alternative name(s)", "help": "Check server\u0027s identity against its certificate and subject alternative name(s).", "label": "Enable", "name": "enable"}] | None = ...,
        timeout: int | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: ExternalIdentityProviderPayload | None = ...,
        name: str | None = ...,
        type: Literal[{"description": "Microsoft Graph server", "help": "Microsoft Graph server.", "label": "Ms Graph", "name": "ms-graph"}] | None = ...,
        version: Literal[{"help": "MS Graph REST API v1.0.", "label": "V1.0", "name": "v1.0"}, {"description": "MS Graph REST API beta (debug build only)", "help": "MS Graph REST API beta (debug build only).", "label": "Beta", "name": "beta"}] | None = ...,
        url: str | None = ...,
        user_attr_name: str | None = ...,
        group_attr_name: str | None = ...,
        port: int | None = ...,
        source_ip: str | None = ...,
        interface_select_method: Literal[{"description": "Set outgoing interface automatically", "help": "Set outgoing interface automatically.", "label": "Auto", "name": "auto"}, {"description": "Set outgoing interface by SD-WAN or policy routing rules", "help": "Set outgoing interface by SD-WAN or policy routing rules.", "label": "Sdwan", "name": "sdwan"}, {"description": "Set outgoing interface manually", "help": "Set outgoing interface manually.", "label": "Specify", "name": "specify"}] | None = ...,
        interface: str | None = ...,
        vrf_select: int | None = ...,
        server_identity_check: Literal[{"description": "Do not check server\u0027s identity against its certificate and subject alternative name(s)", "help": "Do not check server\u0027s identity against its certificate and subject alternative name(s).", "label": "Disable", "name": "disable"}, {"description": "Check server\u0027s identity against its certificate and subject alternative name(s)", "help": "Check server\u0027s identity against its certificate and subject alternative name(s).", "label": "Enable", "name": "enable"}] | None = ...,
        timeout: int | None = ...,
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
        payload_dict: ExternalIdentityProviderPayload | None = ...,
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
    "ExternalIdentityProvider",
    "ExternalIdentityProviderPayload",
]