from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class ForwardServerGroupPayload(TypedDict, total=False):
    """
    Type hints for web_proxy/forward_server_group payload fields.
    
    Configure a forward server group consisting or multiple forward servers. Supports failover and load balancing.
    
    **Usage:**
        payload: ForwardServerGroupPayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    name: NotRequired[str]  # Configure a forward server group consisting one or multiple 
    affinity: NotRequired[Literal[{"description": "Enable affinity", "help": "Enable affinity.", "label": "Enable", "name": "enable"}, {"description": "Disable affinity", "help": "Disable affinity.", "label": "Disable", "name": "disable"}]]  # Enable/disable affinity, attaching a source-ip's traffic to 
    ldb_method: NotRequired[Literal[{"description": "Load balance traffic to forward servers based on assigned weights", "help": "Load balance traffic to forward servers based on assigned weights. Weights are ratios of total number of sessions.", "label": "Weighted", "name": "weighted"}, {"description": "Send new sessions to the server with lowest session count", "help": "Send new sessions to the server with lowest session count.", "label": "Least Session", "name": "least-session"}, {"description": "Send new sessions to the next active server in the list", "help": "Send new sessions to the next active server in the list. Servers are selected with highest weight first and then in order as they are configured. Traffic switches back to the first server upon failure recovery.", "label": "Active Passive", "name": "active-passive"}]]  # Load balance method: weighted or least-session.
    group_down_option: NotRequired[Literal[{"description": "Block sessions until at least one server in the group is back up", "help": "Block sessions until at least one server in the group is back up.", "label": "Block", "name": "block"}, {"description": "Pass sessions to their destination bypassing servers in the forward server group", "help": "Pass sessions to their destination bypassing servers in the forward server group.", "label": "Pass", "name": "pass"}]]  # Action to take when all of the servers in the forward server
    server_list: NotRequired[list[dict[str, Any]]]  # Add web forward servers to a list to form a server group. Op


class ForwardServerGroup:
    """
    Configure a forward server group consisting or multiple forward servers. Supports failover and load balancing.
    
    Path: web_proxy/forward_server_group
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
        payload_dict: ForwardServerGroupPayload | None = ...,
        name: str | None = ...,
        affinity: Literal[{"description": "Enable affinity", "help": "Enable affinity.", "label": "Enable", "name": "enable"}, {"description": "Disable affinity", "help": "Disable affinity.", "label": "Disable", "name": "disable"}] | None = ...,
        ldb_method: Literal[{"description": "Load balance traffic to forward servers based on assigned weights", "help": "Load balance traffic to forward servers based on assigned weights. Weights are ratios of total number of sessions.", "label": "Weighted", "name": "weighted"}, {"description": "Send new sessions to the server with lowest session count", "help": "Send new sessions to the server with lowest session count.", "label": "Least Session", "name": "least-session"}, {"description": "Send new sessions to the next active server in the list", "help": "Send new sessions to the next active server in the list. Servers are selected with highest weight first and then in order as they are configured. Traffic switches back to the first server upon failure recovery.", "label": "Active Passive", "name": "active-passive"}] | None = ...,
        group_down_option: Literal[{"description": "Block sessions until at least one server in the group is back up", "help": "Block sessions until at least one server in the group is back up.", "label": "Block", "name": "block"}, {"description": "Pass sessions to their destination bypassing servers in the forward server group", "help": "Pass sessions to their destination bypassing servers in the forward server group.", "label": "Pass", "name": "pass"}] | None = ...,
        server_list: list[dict[str, Any]] | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: ForwardServerGroupPayload | None = ...,
        name: str | None = ...,
        affinity: Literal[{"description": "Enable affinity", "help": "Enable affinity.", "label": "Enable", "name": "enable"}, {"description": "Disable affinity", "help": "Disable affinity.", "label": "Disable", "name": "disable"}] | None = ...,
        ldb_method: Literal[{"description": "Load balance traffic to forward servers based on assigned weights", "help": "Load balance traffic to forward servers based on assigned weights. Weights are ratios of total number of sessions.", "label": "Weighted", "name": "weighted"}, {"description": "Send new sessions to the server with lowest session count", "help": "Send new sessions to the server with lowest session count.", "label": "Least Session", "name": "least-session"}, {"description": "Send new sessions to the next active server in the list", "help": "Send new sessions to the next active server in the list. Servers are selected with highest weight first and then in order as they are configured. Traffic switches back to the first server upon failure recovery.", "label": "Active Passive", "name": "active-passive"}] | None = ...,
        group_down_option: Literal[{"description": "Block sessions until at least one server in the group is back up", "help": "Block sessions until at least one server in the group is back up.", "label": "Block", "name": "block"}, {"description": "Pass sessions to their destination bypassing servers in the forward server group", "help": "Pass sessions to their destination bypassing servers in the forward server group.", "label": "Pass", "name": "pass"}] | None = ...,
        server_list: list[dict[str, Any]] | None = ...,
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
        payload_dict: ForwardServerGroupPayload | None = ...,
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
    "ForwardServerGroup",
    "ForwardServerGroupPayload",
]