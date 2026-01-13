from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class AccessProxyVirtualHostPayload(TypedDict, total=False):
    """
    Type hints for firewall/access_proxy_virtual_host payload fields.
    
    Configure Access Proxy virtual hosts.
    
    **Related Resources:**

    Dependencies (resources this endpoint references):
        - :class:`~.system.replacemsg-group.ReplacemsgGroupEndpoint` (via: replacemsg-group)

    **Usage:**
        payload: AccessProxyVirtualHostPayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    name: NotRequired[str]  # Virtual host name.
    ssl_certificate: list[dict[str, Any]]  # SSL certificates for this host.
    host: str  # The host name.
    host_type: Literal[{"description": "Match the pattern if a string contains the sub-string", "help": "Match the pattern if a string contains the sub-string.", "label": "Sub String", "name": "sub-string"}, {"description": "Match the pattern with wildcards", "help": "Match the pattern with wildcards.", "label": "Wildcard", "name": "wildcard"}]  # Type of host pattern.
    replacemsg_group: NotRequired[str]  # Access-proxy-virtual-host replacement message override group
    empty_cert_action: NotRequired[Literal[{"description": "Accept the SSL handshake if the client certificate is empty", "help": "Accept the SSL handshake if the client certificate is empty.", "label": "Accept", "name": "accept"}, {"description": "Block the SSL handshake if the client certificate is empty", "help": "Block the SSL handshake if the client certificate is empty.", "label": "Block", "name": "block"}, {"description": "Accept the SSL handshake only if the end-point is unmanageable", "help": "Accept the SSL handshake only if the end-point is unmanageable.", "label": "Accept Unmanageable", "name": "accept-unmanageable"}]]  # Action for an empty client certificate.
    user_agent_detect: NotRequired[Literal[{"description": "Disable detecting unknown devices by HTTP user-agent if no client certificate is provided", "help": "Disable detecting unknown devices by HTTP user-agent if no client certificate is provided.", "label": "Disable", "name": "disable"}, {"description": "Enable detecting unknown devices by HTTP user-agent if no client certificate is provided", "help": "Enable detecting unknown devices by HTTP user-agent if no client certificate is provided.", "label": "Enable", "name": "enable"}]]  # Enable/disable detecting device type by HTTP user-agent if n
    client_cert: NotRequired[Literal[{"description": "Disable client certificate request", "help": "Disable client certificate request.", "label": "Disable", "name": "disable"}, {"description": "Enable client certificate request", "help": "Enable client certificate request.", "label": "Enable", "name": "enable"}]]  # Enable/disable requesting client certificate.


class AccessProxyVirtualHost:
    """
    Configure Access Proxy virtual hosts.
    
    Path: firewall/access_proxy_virtual_host
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
        payload_dict: AccessProxyVirtualHostPayload | None = ...,
        name: str | None = ...,
        ssl_certificate: list[dict[str, Any]] | None = ...,
        host: str | None = ...,
        host_type: Literal[{"description": "Match the pattern if a string contains the sub-string", "help": "Match the pattern if a string contains the sub-string.", "label": "Sub String", "name": "sub-string"}, {"description": "Match the pattern with wildcards", "help": "Match the pattern with wildcards.", "label": "Wildcard", "name": "wildcard"}] | None = ...,
        replacemsg_group: str | None = ...,
        empty_cert_action: Literal[{"description": "Accept the SSL handshake if the client certificate is empty", "help": "Accept the SSL handshake if the client certificate is empty.", "label": "Accept", "name": "accept"}, {"description": "Block the SSL handshake if the client certificate is empty", "help": "Block the SSL handshake if the client certificate is empty.", "label": "Block", "name": "block"}, {"description": "Accept the SSL handshake only if the end-point is unmanageable", "help": "Accept the SSL handshake only if the end-point is unmanageable.", "label": "Accept Unmanageable", "name": "accept-unmanageable"}] | None = ...,
        user_agent_detect: Literal[{"description": "Disable detecting unknown devices by HTTP user-agent if no client certificate is provided", "help": "Disable detecting unknown devices by HTTP user-agent if no client certificate is provided.", "label": "Disable", "name": "disable"}, {"description": "Enable detecting unknown devices by HTTP user-agent if no client certificate is provided", "help": "Enable detecting unknown devices by HTTP user-agent if no client certificate is provided.", "label": "Enable", "name": "enable"}] | None = ...,
        client_cert: Literal[{"description": "Disable client certificate request", "help": "Disable client certificate request.", "label": "Disable", "name": "disable"}, {"description": "Enable client certificate request", "help": "Enable client certificate request.", "label": "Enable", "name": "enable"}] | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: AccessProxyVirtualHostPayload | None = ...,
        name: str | None = ...,
        ssl_certificate: list[dict[str, Any]] | None = ...,
        host: str | None = ...,
        host_type: Literal[{"description": "Match the pattern if a string contains the sub-string", "help": "Match the pattern if a string contains the sub-string.", "label": "Sub String", "name": "sub-string"}, {"description": "Match the pattern with wildcards", "help": "Match the pattern with wildcards.", "label": "Wildcard", "name": "wildcard"}] | None = ...,
        replacemsg_group: str | None = ...,
        empty_cert_action: Literal[{"description": "Accept the SSL handshake if the client certificate is empty", "help": "Accept the SSL handshake if the client certificate is empty.", "label": "Accept", "name": "accept"}, {"description": "Block the SSL handshake if the client certificate is empty", "help": "Block the SSL handshake if the client certificate is empty.", "label": "Block", "name": "block"}, {"description": "Accept the SSL handshake only if the end-point is unmanageable", "help": "Accept the SSL handshake only if the end-point is unmanageable.", "label": "Accept Unmanageable", "name": "accept-unmanageable"}] | None = ...,
        user_agent_detect: Literal[{"description": "Disable detecting unknown devices by HTTP user-agent if no client certificate is provided", "help": "Disable detecting unknown devices by HTTP user-agent if no client certificate is provided.", "label": "Disable", "name": "disable"}, {"description": "Enable detecting unknown devices by HTTP user-agent if no client certificate is provided", "help": "Enable detecting unknown devices by HTTP user-agent if no client certificate is provided.", "label": "Enable", "name": "enable"}] | None = ...,
        client_cert: Literal[{"description": "Disable client certificate request", "help": "Disable client certificate request.", "label": "Disable", "name": "disable"}, {"description": "Enable client certificate request", "help": "Enable client certificate request.", "label": "Enable", "name": "enable"}] | None = ...,
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
        payload_dict: AccessProxyVirtualHostPayload | None = ...,
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
    "AccessProxyVirtualHost",
    "AccessProxyVirtualHostPayload",
]