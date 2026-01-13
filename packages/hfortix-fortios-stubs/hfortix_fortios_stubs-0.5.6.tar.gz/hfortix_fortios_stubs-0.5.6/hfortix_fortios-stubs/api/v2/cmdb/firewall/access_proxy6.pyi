from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class AccessProxy6Payload(TypedDict, total=False):
    """
    Type hints for firewall/access_proxy6 payload fields.
    
    Configure IPv6 access proxy.
    
    **Related Resources:**

    Dependencies (resources this endpoint references):
        - :class:`~.firewall.access-proxy-virtual-host.AccessProxyVirtualHostEndpoint` (via: auth-virtual-host)
        - :class:`~.firewall.decrypted-traffic-mirror.DecryptedTrafficMirrorEndpoint` (via: decrypted-traffic-mirror)
        - :class:`~.firewall.vip6.Vip6Endpoint` (via: vip)

    **Usage:**
        payload: AccessProxy6Payload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    name: NotRequired[str]  # Access Proxy name.
    vip: str  # Virtual IP name.
    auth_portal: NotRequired[Literal[{"description": "Disable authentication portal", "help": "Disable authentication portal.", "label": "Disable", "name": "disable"}, {"description": "Enable authentication portal", "help": "Enable authentication portal.", "label": "Enable", "name": "enable"}]]  # Enable/disable authentication portal.
    auth_virtual_host: NotRequired[str]  # Virtual host for authentication portal.
    log_blocked_traffic: NotRequired[Literal[{"description": "Log all traffic denied by this access proxy", "help": "Log all traffic denied by this access proxy.", "label": "Enable", "name": "enable"}, {"description": "Do not log all traffic denied by this access proxy", "help": "Do not log all traffic denied by this access proxy.", "label": "Disable", "name": "disable"}]]  # Enable/disable logging of blocked traffic.
    add_vhost_domain_to_dnsdb: NotRequired[Literal[{"description": "add dns entry for all vhosts used by access proxy", "help": "add dns entry for all vhosts used by access proxy.", "label": "Enable", "name": "enable"}, {"description": "Do not add dns entry for all vhosts used by access proxy", "help": "Do not add dns entry for all vhosts used by access proxy.", "label": "Disable", "name": "disable"}]]  # Enable/disable adding vhost/domain to dnsdb for ztna dox tun
    svr_pool_multiplex: NotRequired[Literal[{"description": "Enable server pool multiplexing", "help": "Enable server pool multiplexing.  Share connected server.", "label": "Enable", "name": "enable"}, {"description": "Disable server pool multiplexing", "help": "Disable server pool multiplexing.  Do not share connected server.", "label": "Disable", "name": "disable"}]]  # Enable/disable server pool multiplexing (default = disable).
    svr_pool_ttl: NotRequired[int]  # Time-to-live in the server pool for idle connections to serv
    svr_pool_server_max_request: NotRequired[int]  # Maximum number of requests that servers in server pool handl
    svr_pool_server_max_concurrent_request: NotRequired[int]  # Maximum number of concurrent requests that servers in server
    decrypted_traffic_mirror: NotRequired[str]  # Decrypted traffic mirror.
    api_gateway: NotRequired[list[dict[str, Any]]]  # Set IPv4 API Gateway.
    api_gateway6: NotRequired[list[dict[str, Any]]]  # Set IPv6 API Gateway.


class AccessProxy6:
    """
    Configure IPv6 access proxy.
    
    Path: firewall/access_proxy6
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
        payload_dict: AccessProxy6Payload | None = ...,
        name: str | None = ...,
        vip: str | None = ...,
        auth_portal: Literal[{"description": "Disable authentication portal", "help": "Disable authentication portal.", "label": "Disable", "name": "disable"}, {"description": "Enable authentication portal", "help": "Enable authentication portal.", "label": "Enable", "name": "enable"}] | None = ...,
        auth_virtual_host: str | None = ...,
        log_blocked_traffic: Literal[{"description": "Log all traffic denied by this access proxy", "help": "Log all traffic denied by this access proxy.", "label": "Enable", "name": "enable"}, {"description": "Do not log all traffic denied by this access proxy", "help": "Do not log all traffic denied by this access proxy.", "label": "Disable", "name": "disable"}] | None = ...,
        add_vhost_domain_to_dnsdb: Literal[{"description": "add dns entry for all vhosts used by access proxy", "help": "add dns entry for all vhosts used by access proxy.", "label": "Enable", "name": "enable"}, {"description": "Do not add dns entry for all vhosts used by access proxy", "help": "Do not add dns entry for all vhosts used by access proxy.", "label": "Disable", "name": "disable"}] | None = ...,
        svr_pool_multiplex: Literal[{"description": "Enable server pool multiplexing", "help": "Enable server pool multiplexing.  Share connected server.", "label": "Enable", "name": "enable"}, {"description": "Disable server pool multiplexing", "help": "Disable server pool multiplexing.  Do not share connected server.", "label": "Disable", "name": "disable"}] | None = ...,
        svr_pool_ttl: int | None = ...,
        svr_pool_server_max_request: int | None = ...,
        svr_pool_server_max_concurrent_request: int | None = ...,
        decrypted_traffic_mirror: str | None = ...,
        api_gateway: list[dict[str, Any]] | None = ...,
        api_gateway6: list[dict[str, Any]] | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: AccessProxy6Payload | None = ...,
        name: str | None = ...,
        vip: str | None = ...,
        auth_portal: Literal[{"description": "Disable authentication portal", "help": "Disable authentication portal.", "label": "Disable", "name": "disable"}, {"description": "Enable authentication portal", "help": "Enable authentication portal.", "label": "Enable", "name": "enable"}] | None = ...,
        auth_virtual_host: str | None = ...,
        log_blocked_traffic: Literal[{"description": "Log all traffic denied by this access proxy", "help": "Log all traffic denied by this access proxy.", "label": "Enable", "name": "enable"}, {"description": "Do not log all traffic denied by this access proxy", "help": "Do not log all traffic denied by this access proxy.", "label": "Disable", "name": "disable"}] | None = ...,
        add_vhost_domain_to_dnsdb: Literal[{"description": "add dns entry for all vhosts used by access proxy", "help": "add dns entry for all vhosts used by access proxy.", "label": "Enable", "name": "enable"}, {"description": "Do not add dns entry for all vhosts used by access proxy", "help": "Do not add dns entry for all vhosts used by access proxy.", "label": "Disable", "name": "disable"}] | None = ...,
        svr_pool_multiplex: Literal[{"description": "Enable server pool multiplexing", "help": "Enable server pool multiplexing.  Share connected server.", "label": "Enable", "name": "enable"}, {"description": "Disable server pool multiplexing", "help": "Disable server pool multiplexing.  Do not share connected server.", "label": "Disable", "name": "disable"}] | None = ...,
        svr_pool_ttl: int | None = ...,
        svr_pool_server_max_request: int | None = ...,
        svr_pool_server_max_concurrent_request: int | None = ...,
        decrypted_traffic_mirror: str | None = ...,
        api_gateway: list[dict[str, Any]] | None = ...,
        api_gateway6: list[dict[str, Any]] | None = ...,
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
        payload_dict: AccessProxy6Payload | None = ...,
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
    "AccessProxy6",
    "AccessProxy6Payload",
]