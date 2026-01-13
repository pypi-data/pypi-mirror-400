from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class EventfilterPayload(TypedDict, total=False):
    """
    Type hints for log/eventfilter payload fields.
    
    Configure log event filters.
    
    **Usage:**
        payload: EventfilterPayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    event: NotRequired[Literal[{"description": "Enable event logging", "help": "Enable event logging.", "label": "Enable", "name": "enable"}, {"description": "Disable event logging", "help": "Disable event logging.", "label": "Disable", "name": "disable"}]]  # Enable/disable event logging.
    system: NotRequired[Literal[{"description": "Enable system event logging", "help": "Enable system event logging.", "label": "Enable", "name": "enable"}, {"description": "Disable system event logging", "help": "Disable system event logging.", "label": "Disable", "name": "disable"}]]  # Enable/disable system event logging.
    vpn: NotRequired[Literal[{"description": "Enable VPN event logging", "help": "Enable VPN event logging.", "label": "Enable", "name": "enable"}, {"description": "Disable VPN event logging", "help": "Disable VPN event logging.", "label": "Disable", "name": "disable"}]]  # Enable/disable VPN event logging.
    user: NotRequired[Literal[{"description": "Enable user authentication event logging", "help": "Enable user authentication event logging.", "label": "Enable", "name": "enable"}, {"description": "Disable user authentication event logging", "help": "Disable user authentication event logging.", "label": "Disable", "name": "disable"}]]  # Enable/disable user authentication event logging.
    router: NotRequired[Literal[{"description": "Enable router event logging", "help": "Enable router event logging.", "label": "Enable", "name": "enable"}, {"description": "Disable router event logging", "help": "Disable router event logging.", "label": "Disable", "name": "disable"}]]  # Enable/disable router event logging.
    wireless_activity: NotRequired[Literal[{"description": "Enable wireless event logging", "help": "Enable wireless event logging.", "label": "Enable", "name": "enable"}, {"description": "Disable wireless event logging", "help": "Disable wireless event logging.", "label": "Disable", "name": "disable"}]]  # Enable/disable wireless event logging.
    wan_opt: NotRequired[Literal[{"description": "Enable WAN optimization event logging", "help": "Enable WAN optimization event logging.", "label": "Enable", "name": "enable"}, {"description": "Disable WAN optimization event logging", "help": "Disable WAN optimization event logging.", "label": "Disable", "name": "disable"}]]  # Enable/disable WAN optimization event logging.
    endpoint: NotRequired[Literal[{"description": "Enable endpoint event logging", "help": "Enable endpoint event logging.", "label": "Enable", "name": "enable"}, {"description": "Disable endpoint event logging", "help": "Disable endpoint event logging.", "label": "Disable", "name": "disable"}]]  # Enable/disable endpoint event logging.
    ha: NotRequired[Literal[{"description": "Enable ha event logging", "help": "Enable ha event logging.", "label": "Enable", "name": "enable"}, {"description": "Disable ha event logging", "help": "Disable ha event logging.", "label": "Disable", "name": "disable"}]]  # Enable/disable ha event logging.
    security_rating: NotRequired[Literal[{"description": "Enable Security Fabric audit result logging", "help": "Enable Security Fabric audit result logging.", "label": "Enable", "name": "enable"}, {"description": "Disable Security Fabric audit result logging", "help": "Disable Security Fabric audit result logging.", "label": "Disable", "name": "disable"}]]  # Enable/disable Security Rating result logging.
    fortiextender: NotRequired[Literal[{"description": "Enable Forti-Extender logging", "help": "Enable Forti-Extender logging.", "label": "Enable", "name": "enable"}, {"description": "Disable Forti-Extender logging", "help": "Disable Forti-Extender logging.", "label": "Disable", "name": "disable"}]]  # Enable/disable FortiExtender logging.
    connector: NotRequired[Literal[{"description": "Enable SDN connector logging", "help": "Enable SDN connector logging.", "label": "Enable", "name": "enable"}, {"description": "Disable SDN connector logging", "help": "Disable SDN connector logging.", "label": "Disable", "name": "disable"}]]  # Enable/disable SDN connector logging.
    sdwan: NotRequired[Literal[{"description": "Enable SD-WAN logging", "help": "Enable SD-WAN logging.", "label": "Enable", "name": "enable"}, {"description": "Disable SD-WAN logging", "help": "Disable SD-WAN logging.", "label": "Disable", "name": "disable"}]]  # Enable/disable SD-WAN logging.
    cifs: NotRequired[Literal[{"description": "Enable CIFS logging", "help": "Enable CIFS logging.", "label": "Enable", "name": "enable"}, {"description": "Disable CIFS logging", "help": "Disable CIFS logging.", "label": "Disable", "name": "disable"}]]  # Enable/disable CIFS logging.
    switch_controller: NotRequired[Literal[{"description": "Enable Switch-Controller logging", "help": "Enable Switch-Controller logging.", "label": "Enable", "name": "enable"}, {"description": "Disable Switch-Controller logging", "help": "Disable Switch-Controller logging.", "label": "Disable", "name": "disable"}]]  # Enable/disable Switch-Controller logging.
    rest_api: NotRequired[Literal[{"description": "Enable REST API logging", "help": "Enable REST API logging.", "label": "Enable", "name": "enable"}, {"description": "Disable REST API logging", "help": "Disable REST API logging.", "label": "Disable", "name": "disable"}]]  # Enable/disable REST API logging.
    web_svc: NotRequired[Literal[{"description": "Enable web-svc daemon logging", "help": "Enable web-svc daemon logging.", "label": "Enable", "name": "enable"}, {"description": "Disable web-svc daemon logging", "help": "Disable web-svc daemon logging.", "label": "Disable", "name": "disable"}]]  # Enable/disable web-svc performance logging.
    webproxy: NotRequired[Literal[{"help": "Enable Web Proxy event logging.", "label": "Enable", "name": "enable"}, {"help": "Disable Web Proxy event logging.", "label": "Disable", "name": "disable"}]]  # Enable/disable web proxy event logging.


class Eventfilter:
    """
    Configure log event filters.
    
    Path: log/eventfilter
    Category: cmdb
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
        payload_dict: EventfilterPayload | None = ...,
        event: Literal[{"description": "Enable event logging", "help": "Enable event logging.", "label": "Enable", "name": "enable"}, {"description": "Disable event logging", "help": "Disable event logging.", "label": "Disable", "name": "disable"}] | None = ...,
        system: Literal[{"description": "Enable system event logging", "help": "Enable system event logging.", "label": "Enable", "name": "enable"}, {"description": "Disable system event logging", "help": "Disable system event logging.", "label": "Disable", "name": "disable"}] | None = ...,
        vpn: Literal[{"description": "Enable VPN event logging", "help": "Enable VPN event logging.", "label": "Enable", "name": "enable"}, {"description": "Disable VPN event logging", "help": "Disable VPN event logging.", "label": "Disable", "name": "disable"}] | None = ...,
        user: Literal[{"description": "Enable user authentication event logging", "help": "Enable user authentication event logging.", "label": "Enable", "name": "enable"}, {"description": "Disable user authentication event logging", "help": "Disable user authentication event logging.", "label": "Disable", "name": "disable"}] | None = ...,
        router: Literal[{"description": "Enable router event logging", "help": "Enable router event logging.", "label": "Enable", "name": "enable"}, {"description": "Disable router event logging", "help": "Disable router event logging.", "label": "Disable", "name": "disable"}] | None = ...,
        wireless_activity: Literal[{"description": "Enable wireless event logging", "help": "Enable wireless event logging.", "label": "Enable", "name": "enable"}, {"description": "Disable wireless event logging", "help": "Disable wireless event logging.", "label": "Disable", "name": "disable"}] | None = ...,
        wan_opt: Literal[{"description": "Enable WAN optimization event logging", "help": "Enable WAN optimization event logging.", "label": "Enable", "name": "enable"}, {"description": "Disable WAN optimization event logging", "help": "Disable WAN optimization event logging.", "label": "Disable", "name": "disable"}] | None = ...,
        endpoint: Literal[{"description": "Enable endpoint event logging", "help": "Enable endpoint event logging.", "label": "Enable", "name": "enable"}, {"description": "Disable endpoint event logging", "help": "Disable endpoint event logging.", "label": "Disable", "name": "disable"}] | None = ...,
        ha: Literal[{"description": "Enable ha event logging", "help": "Enable ha event logging.", "label": "Enable", "name": "enable"}, {"description": "Disable ha event logging", "help": "Disable ha event logging.", "label": "Disable", "name": "disable"}] | None = ...,
        security_rating: Literal[{"description": "Enable Security Fabric audit result logging", "help": "Enable Security Fabric audit result logging.", "label": "Enable", "name": "enable"}, {"description": "Disable Security Fabric audit result logging", "help": "Disable Security Fabric audit result logging.", "label": "Disable", "name": "disable"}] | None = ...,
        fortiextender: Literal[{"description": "Enable Forti-Extender logging", "help": "Enable Forti-Extender logging.", "label": "Enable", "name": "enable"}, {"description": "Disable Forti-Extender logging", "help": "Disable Forti-Extender logging.", "label": "Disable", "name": "disable"}] | None = ...,
        connector: Literal[{"description": "Enable SDN connector logging", "help": "Enable SDN connector logging.", "label": "Enable", "name": "enable"}, {"description": "Disable SDN connector logging", "help": "Disable SDN connector logging.", "label": "Disable", "name": "disable"}] | None = ...,
        sdwan: Literal[{"description": "Enable SD-WAN logging", "help": "Enable SD-WAN logging.", "label": "Enable", "name": "enable"}, {"description": "Disable SD-WAN logging", "help": "Disable SD-WAN logging.", "label": "Disable", "name": "disable"}] | None = ...,
        cifs: Literal[{"description": "Enable CIFS logging", "help": "Enable CIFS logging.", "label": "Enable", "name": "enable"}, {"description": "Disable CIFS logging", "help": "Disable CIFS logging.", "label": "Disable", "name": "disable"}] | None = ...,
        switch_controller: Literal[{"description": "Enable Switch-Controller logging", "help": "Enable Switch-Controller logging.", "label": "Enable", "name": "enable"}, {"description": "Disable Switch-Controller logging", "help": "Disable Switch-Controller logging.", "label": "Disable", "name": "disable"}] | None = ...,
        rest_api: Literal[{"description": "Enable REST API logging", "help": "Enable REST API logging.", "label": "Enable", "name": "enable"}, {"description": "Disable REST API logging", "help": "Disable REST API logging.", "label": "Disable", "name": "disable"}] | None = ...,
        web_svc: Literal[{"description": "Enable web-svc daemon logging", "help": "Enable web-svc daemon logging.", "label": "Enable", "name": "enable"}, {"description": "Disable web-svc daemon logging", "help": "Disable web-svc daemon logging.", "label": "Disable", "name": "disable"}] | None = ...,
        webproxy: Literal[{"help": "Enable Web Proxy event logging.", "label": "Enable", "name": "enable"}, {"help": "Disable Web Proxy event logging.", "label": "Disable", "name": "disable"}] | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: EventfilterPayload | None = ...,
        event: Literal[{"description": "Enable event logging", "help": "Enable event logging.", "label": "Enable", "name": "enable"}, {"description": "Disable event logging", "help": "Disable event logging.", "label": "Disable", "name": "disable"}] | None = ...,
        system: Literal[{"description": "Enable system event logging", "help": "Enable system event logging.", "label": "Enable", "name": "enable"}, {"description": "Disable system event logging", "help": "Disable system event logging.", "label": "Disable", "name": "disable"}] | None = ...,
        vpn: Literal[{"description": "Enable VPN event logging", "help": "Enable VPN event logging.", "label": "Enable", "name": "enable"}, {"description": "Disable VPN event logging", "help": "Disable VPN event logging.", "label": "Disable", "name": "disable"}] | None = ...,
        user: Literal[{"description": "Enable user authentication event logging", "help": "Enable user authentication event logging.", "label": "Enable", "name": "enable"}, {"description": "Disable user authentication event logging", "help": "Disable user authentication event logging.", "label": "Disable", "name": "disable"}] | None = ...,
        router: Literal[{"description": "Enable router event logging", "help": "Enable router event logging.", "label": "Enable", "name": "enable"}, {"description": "Disable router event logging", "help": "Disable router event logging.", "label": "Disable", "name": "disable"}] | None = ...,
        wireless_activity: Literal[{"description": "Enable wireless event logging", "help": "Enable wireless event logging.", "label": "Enable", "name": "enable"}, {"description": "Disable wireless event logging", "help": "Disable wireless event logging.", "label": "Disable", "name": "disable"}] | None = ...,
        wan_opt: Literal[{"description": "Enable WAN optimization event logging", "help": "Enable WAN optimization event logging.", "label": "Enable", "name": "enable"}, {"description": "Disable WAN optimization event logging", "help": "Disable WAN optimization event logging.", "label": "Disable", "name": "disable"}] | None = ...,
        endpoint: Literal[{"description": "Enable endpoint event logging", "help": "Enable endpoint event logging.", "label": "Enable", "name": "enable"}, {"description": "Disable endpoint event logging", "help": "Disable endpoint event logging.", "label": "Disable", "name": "disable"}] | None = ...,
        ha: Literal[{"description": "Enable ha event logging", "help": "Enable ha event logging.", "label": "Enable", "name": "enable"}, {"description": "Disable ha event logging", "help": "Disable ha event logging.", "label": "Disable", "name": "disable"}] | None = ...,
        security_rating: Literal[{"description": "Enable Security Fabric audit result logging", "help": "Enable Security Fabric audit result logging.", "label": "Enable", "name": "enable"}, {"description": "Disable Security Fabric audit result logging", "help": "Disable Security Fabric audit result logging.", "label": "Disable", "name": "disable"}] | None = ...,
        fortiextender: Literal[{"description": "Enable Forti-Extender logging", "help": "Enable Forti-Extender logging.", "label": "Enable", "name": "enable"}, {"description": "Disable Forti-Extender logging", "help": "Disable Forti-Extender logging.", "label": "Disable", "name": "disable"}] | None = ...,
        connector: Literal[{"description": "Enable SDN connector logging", "help": "Enable SDN connector logging.", "label": "Enable", "name": "enable"}, {"description": "Disable SDN connector logging", "help": "Disable SDN connector logging.", "label": "Disable", "name": "disable"}] | None = ...,
        sdwan: Literal[{"description": "Enable SD-WAN logging", "help": "Enable SD-WAN logging.", "label": "Enable", "name": "enable"}, {"description": "Disable SD-WAN logging", "help": "Disable SD-WAN logging.", "label": "Disable", "name": "disable"}] | None = ...,
        cifs: Literal[{"description": "Enable CIFS logging", "help": "Enable CIFS logging.", "label": "Enable", "name": "enable"}, {"description": "Disable CIFS logging", "help": "Disable CIFS logging.", "label": "Disable", "name": "disable"}] | None = ...,
        switch_controller: Literal[{"description": "Enable Switch-Controller logging", "help": "Enable Switch-Controller logging.", "label": "Enable", "name": "enable"}, {"description": "Disable Switch-Controller logging", "help": "Disable Switch-Controller logging.", "label": "Disable", "name": "disable"}] | None = ...,
        rest_api: Literal[{"description": "Enable REST API logging", "help": "Enable REST API logging.", "label": "Enable", "name": "enable"}, {"description": "Disable REST API logging", "help": "Disable REST API logging.", "label": "Disable", "name": "disable"}] | None = ...,
        web_svc: Literal[{"description": "Enable web-svc daemon logging", "help": "Enable web-svc daemon logging.", "label": "Enable", "name": "enable"}, {"description": "Disable web-svc daemon logging", "help": "Disable web-svc daemon logging.", "label": "Disable", "name": "disable"}] | None = ...,
        webproxy: Literal[{"help": "Enable Web Proxy event logging.", "label": "Enable", "name": "enable"}, {"help": "Disable Web Proxy event logging.", "label": "Disable", "name": "disable"}] | None = ...,
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
        payload_dict: EventfilterPayload | None = ...,
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
    "Eventfilter",
    "EventfilterPayload",
]