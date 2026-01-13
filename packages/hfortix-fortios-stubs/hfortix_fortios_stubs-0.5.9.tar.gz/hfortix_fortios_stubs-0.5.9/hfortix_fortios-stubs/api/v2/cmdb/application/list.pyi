from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class ListPayload(TypedDict, total=False):
    """
    Type hints for application/list payload fields.
    
    Configure application control lists.
    
    **Related Resources:**

    Dependencies (resources this endpoint references):
        - :class:`~.system.replacemsg-group.ReplacemsgGroupEndpoint` (via: replacemsg-group)

    **Usage:**
        payload: ListPayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    name: str  # List name.
    comment: NotRequired[str]  # Comments.
    replacemsg_group: NotRequired[str]  # Replacement message group.
    extended_log: NotRequired[Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]]  # Enable/disable extended logging.
    other_application_action: NotRequired[Literal[{"description": "Allow sessions matching an application in this application list", "help": "Allow sessions matching an application in this application list.", "label": "Pass", "name": "pass"}, {"description": "Block sessions matching an application in this application list", "help": "Block sessions matching an application in this application list.", "label": "Block", "name": "block"}]]  # Action for other applications.
    app_replacemsg: NotRequired[Literal[{"description": "Disable replacement messages for blocked applications", "help": "Disable replacement messages for blocked applications.", "label": "Disable", "name": "disable"}, {"description": "Enable replacement messages for blocked applications", "help": "Enable replacement messages for blocked applications.", "label": "Enable", "name": "enable"}]]  # Enable/disable replacement messages for blocked applications
    other_application_log: NotRequired[Literal[{"description": "Disable logging for other applications", "help": "Disable logging for other applications.", "label": "Disable", "name": "disable"}, {"description": "Enable logging for other applications", "help": "Enable logging for other applications.", "label": "Enable", "name": "enable"}]]  # Enable/disable logging for other applications.
    enforce_default_app_port: NotRequired[Literal[{"description": "Disable default application port enforcement", "help": "Disable default application port enforcement.", "label": "Disable", "name": "disable"}, {"description": "Enable default application port enforcement", "help": "Enable default application port enforcement.", "label": "Enable", "name": "enable"}]]  # Enable/disable default application port enforcement for allo
    force_inclusion_ssl_di_sigs: NotRequired[Literal[{"description": "Disable forced inclusion of signatures which normally require SSL deep inspection", "help": "Disable forced inclusion of signatures which normally require SSL deep inspection.", "label": "Disable", "name": "disable"}, {"description": "Enable forced inclusion of signatures which normally require SSL deep inspection", "help": "Enable forced inclusion of signatures which normally require SSL deep inspection.", "label": "Enable", "name": "enable"}]]  # Enable/disable forced inclusion of SSL deep inspection signa
    unknown_application_action: NotRequired[Literal[{"description": "Pass or allow unknown applications", "help": "Pass or allow unknown applications.", "label": "Pass", "name": "pass"}, {"description": "Drop or block unknown applications", "help": "Drop or block unknown applications.", "label": "Block", "name": "block"}]]  # Pass or block traffic from unknown applications.
    unknown_application_log: NotRequired[Literal[{"description": "Disable logging for unknown applications", "help": "Disable logging for unknown applications.", "label": "Disable", "name": "disable"}, {"description": "Enable logging for unknown applications", "help": "Enable logging for unknown applications.", "label": "Enable", "name": "enable"}]]  # Enable/disable logging for unknown applications.
    p2p_block_list: NotRequired[Literal[{"description": "Skype", "help": "Skype.", "label": "Skype", "name": "skype"}, {"description": "Edonkey", "help": "Edonkey.", "label": "Edonkey", "name": "edonkey"}, {"description": "Bit torrent", "help": "Bit torrent.", "label": "Bittorrent", "name": "bittorrent"}]]  # P2P applications to be block listed.
    deep_app_inspection: NotRequired[Literal[{"description": "Disable deep application inspection", "help": "Disable deep application inspection.", "label": "Disable", "name": "disable"}, {"description": "Enable deep application inspection", "help": "Enable deep application inspection.", "label": "Enable", "name": "enable"}]]  # Enable/disable deep application inspection.
    options: NotRequired[Literal[{"description": "Allow DNS", "help": "Allow DNS.", "label": "Allow Dns", "name": "allow-dns"}, {"description": "Allow ICMP", "help": "Allow ICMP.", "label": "Allow Icmp", "name": "allow-icmp"}, {"description": "Allow generic HTTP web browsing", "help": "Allow generic HTTP web browsing.", "label": "Allow Http", "name": "allow-http"}, {"description": "Allow generic SSL communication", "help": "Allow generic SSL communication.", "label": "Allow Ssl", "name": "allow-ssl"}]]  # Basic application protocol signatures allowed by default.
    entries: NotRequired[list[dict[str, Any]]]  # Application list entries.
    control_default_network_services: NotRequired[Literal[{"description": "Disable protocol enforcement over selected ports", "help": "Disable protocol enforcement over selected ports.", "label": "Disable", "name": "disable"}, {"description": "Enable protocol enforcement over selected ports", "help": "Enable protocol enforcement over selected ports.", "label": "Enable", "name": "enable"}]]  # Enable/disable enforcement of protocols over selected ports.
    default_network_services: NotRequired[list[dict[str, Any]]]  # Default network service entries.


class List:
    """
    Configure application control lists.
    
    Path: application/list
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
        payload_dict: ListPayload | None = ...,
        name: str | None = ...,
        comment: str | None = ...,
        replacemsg_group: str | None = ...,
        extended_log: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        other_application_action: Literal[{"description": "Allow sessions matching an application in this application list", "help": "Allow sessions matching an application in this application list.", "label": "Pass", "name": "pass"}, {"description": "Block sessions matching an application in this application list", "help": "Block sessions matching an application in this application list.", "label": "Block", "name": "block"}] | None = ...,
        app_replacemsg: Literal[{"description": "Disable replacement messages for blocked applications", "help": "Disable replacement messages for blocked applications.", "label": "Disable", "name": "disable"}, {"description": "Enable replacement messages for blocked applications", "help": "Enable replacement messages for blocked applications.", "label": "Enable", "name": "enable"}] | None = ...,
        other_application_log: Literal[{"description": "Disable logging for other applications", "help": "Disable logging for other applications.", "label": "Disable", "name": "disable"}, {"description": "Enable logging for other applications", "help": "Enable logging for other applications.", "label": "Enable", "name": "enable"}] | None = ...,
        enforce_default_app_port: Literal[{"description": "Disable default application port enforcement", "help": "Disable default application port enforcement.", "label": "Disable", "name": "disable"}, {"description": "Enable default application port enforcement", "help": "Enable default application port enforcement.", "label": "Enable", "name": "enable"}] | None = ...,
        force_inclusion_ssl_di_sigs: Literal[{"description": "Disable forced inclusion of signatures which normally require SSL deep inspection", "help": "Disable forced inclusion of signatures which normally require SSL deep inspection.", "label": "Disable", "name": "disable"}, {"description": "Enable forced inclusion of signatures which normally require SSL deep inspection", "help": "Enable forced inclusion of signatures which normally require SSL deep inspection.", "label": "Enable", "name": "enable"}] | None = ...,
        unknown_application_action: Literal[{"description": "Pass or allow unknown applications", "help": "Pass or allow unknown applications.", "label": "Pass", "name": "pass"}, {"description": "Drop or block unknown applications", "help": "Drop or block unknown applications.", "label": "Block", "name": "block"}] | None = ...,
        unknown_application_log: Literal[{"description": "Disable logging for unknown applications", "help": "Disable logging for unknown applications.", "label": "Disable", "name": "disable"}, {"description": "Enable logging for unknown applications", "help": "Enable logging for unknown applications.", "label": "Enable", "name": "enable"}] | None = ...,
        p2p_block_list: Literal[{"description": "Skype", "help": "Skype.", "label": "Skype", "name": "skype"}, {"description": "Edonkey", "help": "Edonkey.", "label": "Edonkey", "name": "edonkey"}, {"description": "Bit torrent", "help": "Bit torrent.", "label": "Bittorrent", "name": "bittorrent"}] | None = ...,
        deep_app_inspection: Literal[{"description": "Disable deep application inspection", "help": "Disable deep application inspection.", "label": "Disable", "name": "disable"}, {"description": "Enable deep application inspection", "help": "Enable deep application inspection.", "label": "Enable", "name": "enable"}] | None = ...,
        options: Literal[{"description": "Allow DNS", "help": "Allow DNS.", "label": "Allow Dns", "name": "allow-dns"}, {"description": "Allow ICMP", "help": "Allow ICMP.", "label": "Allow Icmp", "name": "allow-icmp"}, {"description": "Allow generic HTTP web browsing", "help": "Allow generic HTTP web browsing.", "label": "Allow Http", "name": "allow-http"}, {"description": "Allow generic SSL communication", "help": "Allow generic SSL communication.", "label": "Allow Ssl", "name": "allow-ssl"}] | None = ...,
        entries: list[dict[str, Any]] | None = ...,
        control_default_network_services: Literal[{"description": "Disable protocol enforcement over selected ports", "help": "Disable protocol enforcement over selected ports.", "label": "Disable", "name": "disable"}, {"description": "Enable protocol enforcement over selected ports", "help": "Enable protocol enforcement over selected ports.", "label": "Enable", "name": "enable"}] | None = ...,
        default_network_services: list[dict[str, Any]] | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: ListPayload | None = ...,
        name: str | None = ...,
        comment: str | None = ...,
        replacemsg_group: str | None = ...,
        extended_log: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        other_application_action: Literal[{"description": "Allow sessions matching an application in this application list", "help": "Allow sessions matching an application in this application list.", "label": "Pass", "name": "pass"}, {"description": "Block sessions matching an application in this application list", "help": "Block sessions matching an application in this application list.", "label": "Block", "name": "block"}] | None = ...,
        app_replacemsg: Literal[{"description": "Disable replacement messages for blocked applications", "help": "Disable replacement messages for blocked applications.", "label": "Disable", "name": "disable"}, {"description": "Enable replacement messages for blocked applications", "help": "Enable replacement messages for blocked applications.", "label": "Enable", "name": "enable"}] | None = ...,
        other_application_log: Literal[{"description": "Disable logging for other applications", "help": "Disable logging for other applications.", "label": "Disable", "name": "disable"}, {"description": "Enable logging for other applications", "help": "Enable logging for other applications.", "label": "Enable", "name": "enable"}] | None = ...,
        enforce_default_app_port: Literal[{"description": "Disable default application port enforcement", "help": "Disable default application port enforcement.", "label": "Disable", "name": "disable"}, {"description": "Enable default application port enforcement", "help": "Enable default application port enforcement.", "label": "Enable", "name": "enable"}] | None = ...,
        force_inclusion_ssl_di_sigs: Literal[{"description": "Disable forced inclusion of signatures which normally require SSL deep inspection", "help": "Disable forced inclusion of signatures which normally require SSL deep inspection.", "label": "Disable", "name": "disable"}, {"description": "Enable forced inclusion of signatures which normally require SSL deep inspection", "help": "Enable forced inclusion of signatures which normally require SSL deep inspection.", "label": "Enable", "name": "enable"}] | None = ...,
        unknown_application_action: Literal[{"description": "Pass or allow unknown applications", "help": "Pass or allow unknown applications.", "label": "Pass", "name": "pass"}, {"description": "Drop or block unknown applications", "help": "Drop or block unknown applications.", "label": "Block", "name": "block"}] | None = ...,
        unknown_application_log: Literal[{"description": "Disable logging for unknown applications", "help": "Disable logging for unknown applications.", "label": "Disable", "name": "disable"}, {"description": "Enable logging for unknown applications", "help": "Enable logging for unknown applications.", "label": "Enable", "name": "enable"}] | None = ...,
        p2p_block_list: Literal[{"description": "Skype", "help": "Skype.", "label": "Skype", "name": "skype"}, {"description": "Edonkey", "help": "Edonkey.", "label": "Edonkey", "name": "edonkey"}, {"description": "Bit torrent", "help": "Bit torrent.", "label": "Bittorrent", "name": "bittorrent"}] | None = ...,
        deep_app_inspection: Literal[{"description": "Disable deep application inspection", "help": "Disable deep application inspection.", "label": "Disable", "name": "disable"}, {"description": "Enable deep application inspection", "help": "Enable deep application inspection.", "label": "Enable", "name": "enable"}] | None = ...,
        options: Literal[{"description": "Allow DNS", "help": "Allow DNS.", "label": "Allow Dns", "name": "allow-dns"}, {"description": "Allow ICMP", "help": "Allow ICMP.", "label": "Allow Icmp", "name": "allow-icmp"}, {"description": "Allow generic HTTP web browsing", "help": "Allow generic HTTP web browsing.", "label": "Allow Http", "name": "allow-http"}, {"description": "Allow generic SSL communication", "help": "Allow generic SSL communication.", "label": "Allow Ssl", "name": "allow-ssl"}] | None = ...,
        entries: list[dict[str, Any]] | None = ...,
        control_default_network_services: Literal[{"description": "Disable protocol enforcement over selected ports", "help": "Disable protocol enforcement over selected ports.", "label": "Disable", "name": "disable"}, {"description": "Enable protocol enforcement over selected ports", "help": "Enable protocol enforcement over selected ports.", "label": "Enable", "name": "enable"}] | None = ...,
        default_network_services: list[dict[str, Any]] | None = ...,
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
        payload_dict: ListPayload | None = ...,
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
    "List",
    "ListPayload",
]