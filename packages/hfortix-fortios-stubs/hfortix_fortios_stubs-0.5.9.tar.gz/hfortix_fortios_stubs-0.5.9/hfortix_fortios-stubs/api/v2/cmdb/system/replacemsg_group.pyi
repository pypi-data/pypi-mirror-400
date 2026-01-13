from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class ReplacemsgGroupPayload(TypedDict, total=False):
    """
    Type hints for system/replacemsg_group payload fields.
    
    Configure replacement message groups.
    
    **Usage:**
        payload: ReplacemsgGroupPayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    name: NotRequired[str]  # Group name.
    comment: NotRequired[str]  # Comment.
    group_type: Literal[{"description": "Per-vdom replacement messages", "help": "Per-vdom replacement messages.", "label": "Default", "name": "default"}, {"description": "For use with UTM settings in firewall policies", "help": "For use with UTM settings in firewall policies.", "label": "Utm", "name": "utm"}, {"description": "For use with authentication pages in firewall policies", "help": "For use with authentication pages in firewall policies.", "label": "Auth", "name": "auth"}]  # Group type.
    mail: NotRequired[list[dict[str, Any]]]  # Replacement message table entries.
    http: NotRequired[list[dict[str, Any]]]  # Replacement message table entries.
    webproxy: NotRequired[list[dict[str, Any]]]  # Replacement message table entries.
    ftp: NotRequired[list[dict[str, Any]]]  # Replacement message table entries.
    fortiguard_wf: NotRequired[list[dict[str, Any]]]  # Replacement message table entries.
    spam: NotRequired[list[dict[str, Any]]]  # Replacement message table entries.
    alertmail: NotRequired[list[dict[str, Any]]]  # Replacement message table entries.
    admin: NotRequired[list[dict[str, Any]]]  # Replacement message table entries.
    auth: NotRequired[list[dict[str, Any]]]  # Replacement message table entries.
    sslvpn: NotRequired[list[dict[str, Any]]]  # Replacement message table entries.
    nac_quar: NotRequired[list[dict[str, Any]]]  # Replacement message table entries.
    traffic_quota: NotRequired[list[dict[str, Any]]]  # Replacement message table entries.
    utm: NotRequired[list[dict[str, Any]]]  # Replacement message table entries.
    custom_message: NotRequired[list[dict[str, Any]]]  # Replacement message table entries.
    icap: NotRequired[list[dict[str, Any]]]  # Replacement message table entries.
    automation: NotRequired[list[dict[str, Any]]]  # Replacement message table entries.


class ReplacemsgGroup:
    """
    Configure replacement message groups.
    
    Path: system/replacemsg_group
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
        payload_dict: ReplacemsgGroupPayload | None = ...,
        name: str | None = ...,
        comment: str | None = ...,
        group_type: Literal[{"description": "Per-vdom replacement messages", "help": "Per-vdom replacement messages.", "label": "Default", "name": "default"}, {"description": "For use with UTM settings in firewall policies", "help": "For use with UTM settings in firewall policies.", "label": "Utm", "name": "utm"}, {"description": "For use with authentication pages in firewall policies", "help": "For use with authentication pages in firewall policies.", "label": "Auth", "name": "auth"}] | None = ...,
        mail: list[dict[str, Any]] | None = ...,
        http: list[dict[str, Any]] | None = ...,
        webproxy: list[dict[str, Any]] | None = ...,
        ftp: list[dict[str, Any]] | None = ...,
        fortiguard_wf: list[dict[str, Any]] | None = ...,
        spam: list[dict[str, Any]] | None = ...,
        alertmail: list[dict[str, Any]] | None = ...,
        admin: list[dict[str, Any]] | None = ...,
        auth: list[dict[str, Any]] | None = ...,
        sslvpn: list[dict[str, Any]] | None = ...,
        nac_quar: list[dict[str, Any]] | None = ...,
        traffic_quota: list[dict[str, Any]] | None = ...,
        utm: list[dict[str, Any]] | None = ...,
        custom_message: list[dict[str, Any]] | None = ...,
        icap: list[dict[str, Any]] | None = ...,
        automation: list[dict[str, Any]] | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: ReplacemsgGroupPayload | None = ...,
        name: str | None = ...,
        comment: str | None = ...,
        group_type: Literal[{"description": "Per-vdom replacement messages", "help": "Per-vdom replacement messages.", "label": "Default", "name": "default"}, {"description": "For use with UTM settings in firewall policies", "help": "For use with UTM settings in firewall policies.", "label": "Utm", "name": "utm"}, {"description": "For use with authentication pages in firewall policies", "help": "For use with authentication pages in firewall policies.", "label": "Auth", "name": "auth"}] | None = ...,
        mail: list[dict[str, Any]] | None = ...,
        http: list[dict[str, Any]] | None = ...,
        webproxy: list[dict[str, Any]] | None = ...,
        ftp: list[dict[str, Any]] | None = ...,
        fortiguard_wf: list[dict[str, Any]] | None = ...,
        spam: list[dict[str, Any]] | None = ...,
        alertmail: list[dict[str, Any]] | None = ...,
        admin: list[dict[str, Any]] | None = ...,
        auth: list[dict[str, Any]] | None = ...,
        sslvpn: list[dict[str, Any]] | None = ...,
        nac_quar: list[dict[str, Any]] | None = ...,
        traffic_quota: list[dict[str, Any]] | None = ...,
        utm: list[dict[str, Any]] | None = ...,
        custom_message: list[dict[str, Any]] | None = ...,
        icap: list[dict[str, Any]] | None = ...,
        automation: list[dict[str, Any]] | None = ...,
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
        payload_dict: ReplacemsgGroupPayload | None = ...,
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
    "ReplacemsgGroup",
    "ReplacemsgGroupPayload",
]