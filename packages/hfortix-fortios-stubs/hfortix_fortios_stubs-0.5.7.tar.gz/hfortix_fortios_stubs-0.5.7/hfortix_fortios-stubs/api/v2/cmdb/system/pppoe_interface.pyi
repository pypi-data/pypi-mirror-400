from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class PppoeInterfacePayload(TypedDict, total=False):
    """
    Type hints for system/pppoe_interface payload fields.
    
    Configure the PPPoE interfaces.
    
    **Related Resources:**

    Dependencies (resources this endpoint references):
        - :class:`~.system.interface.InterfaceEndpoint` (via: device)

    **Usage:**
        payload: PppoeInterfacePayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    name: NotRequired[str]  # Name of the PPPoE interface.
    dial_on_demand: NotRequired[Literal[{"description": "Enable dial on demand", "help": "Enable dial on demand.", "label": "Enable", "name": "enable"}, {"description": "Disable dial on demand", "help": "Disable dial on demand.", "label": "Disable", "name": "disable"}]]  # Enable/disable dial on demand to dial the PPPoE interface wh
    ipv6: NotRequired[Literal[{"description": "Enable IPv6CP", "help": "Enable IPv6CP.", "label": "Enable", "name": "enable"}, {"description": "Disable IPv6CP", "help": "Disable IPv6CP.", "label": "Disable", "name": "disable"}]]  # Enable/disable IPv6 Control Protocol (IPv6CP).
    device: str  # Name for the physical interface.
    username: NotRequired[str]  # User name.
    password: NotRequired[str]  # Enter the password.
    pppoe_egress_cos: NotRequired[Literal[{"description": "CoS 0", "help": "CoS 0.", "label": "Cos0", "name": "cos0"}, {"description": "CoS 1", "help": "CoS 1.", "label": "Cos1", "name": "cos1"}, {"description": "CoS 2", "help": "CoS 2.", "label": "Cos2", "name": "cos2"}, {"description": "CoS 3", "help": "CoS 3.", "label": "Cos3", "name": "cos3"}, {"description": "CoS 4", "help": "CoS 4.", "label": "Cos4", "name": "cos4"}, {"description": "CoS 5", "help": "CoS 5.", "label": "Cos5", "name": "cos5"}, {"description": "CoS 6", "help": "CoS 6.", "label": "Cos6", "name": "cos6"}, {"description": "CoS 7", "help": "CoS 7.", "label": "Cos7", "name": "cos7"}]]  # CoS in VLAN tag for outgoing PPPoE/PPP packets.
    auth_type: NotRequired[Literal[{"description": "Automatically choose the authentication method", "help": "Automatically choose the authentication method.", "label": "Auto", "name": "auto"}, {"description": "PAP authentication", "help": "PAP authentication.", "label": "Pap", "name": "pap"}, {"description": "CHAP authentication", "help": "CHAP authentication.", "label": "Chap", "name": "chap"}, {"description": "MS-CHAPv1 authentication", "help": "MS-CHAPv1 authentication.", "label": "Mschapv1", "name": "mschapv1"}, {"description": "MS-CHAPv2 authentication", "help": "MS-CHAPv2 authentication.", "label": "Mschapv2", "name": "mschapv2"}]]  # PPP authentication type to use.
    ipunnumbered: NotRequired[str]  # PPPoE unnumbered IP.
    pppoe_unnumbered_negotiate: NotRequired[Literal[{"description": "Enable PPPoE unnumbered negotiation", "help": "Enable PPPoE unnumbered negotiation.", "label": "Enable", "name": "enable"}, {"description": "Disable PPPoE unnumbered negotiation", "help": "Disable PPPoE unnumbered negotiation.", "label": "Disable", "name": "disable"}]]  # Enable/disable PPPoE unnumbered negotiation.
    idle_timeout: NotRequired[int]  # PPPoE auto disconnect after idle timeout (0-4294967295 sec).
    multilink: NotRequired[Literal[{"description": "Enable PPP multilink support", "help": "Enable PPP multilink support.", "label": "Enable", "name": "enable"}, {"description": "Disable PPP multilink support", "help": "Disable PPP multilink support.", "label": "Disable", "name": "disable"}]]  # Enable/disable PPP multilink support.
    mrru: NotRequired[int]  # PPP MRRU (296 - 65535, default = 1500).
    disc_retry_timeout: NotRequired[int]  # PPPoE discovery init timeout value in (0-4294967295 sec).
    padt_retry_timeout: NotRequired[int]  # PPPoE terminate timeout value in (0-4294967295 sec).
    service_name: NotRequired[str]  # PPPoE service name.
    ac_name: NotRequired[str]  # PPPoE AC name.
    lcp_echo_interval: NotRequired[int]  # Time in seconds between PPPoE Link Control Protocol (LCP) ec
    lcp_max_echo_fails: NotRequired[int]  # Maximum missed LCP echo messages before disconnect.


class PppoeInterface:
    """
    Configure the PPPoE interfaces.
    
    Path: system/pppoe_interface
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
        payload_dict: PppoeInterfacePayload | None = ...,
        name: str | None = ...,
        dial_on_demand: Literal[{"description": "Enable dial on demand", "help": "Enable dial on demand.", "label": "Enable", "name": "enable"}, {"description": "Disable dial on demand", "help": "Disable dial on demand.", "label": "Disable", "name": "disable"}] | None = ...,
        ipv6: Literal[{"description": "Enable IPv6CP", "help": "Enable IPv6CP.", "label": "Enable", "name": "enable"}, {"description": "Disable IPv6CP", "help": "Disable IPv6CP.", "label": "Disable", "name": "disable"}] | None = ...,
        device: str | None = ...,
        username: str | None = ...,
        password: str | None = ...,
        pppoe_egress_cos: Literal[{"description": "CoS 0", "help": "CoS 0.", "label": "Cos0", "name": "cos0"}, {"description": "CoS 1", "help": "CoS 1.", "label": "Cos1", "name": "cos1"}, {"description": "CoS 2", "help": "CoS 2.", "label": "Cos2", "name": "cos2"}, {"description": "CoS 3", "help": "CoS 3.", "label": "Cos3", "name": "cos3"}, {"description": "CoS 4", "help": "CoS 4.", "label": "Cos4", "name": "cos4"}, {"description": "CoS 5", "help": "CoS 5.", "label": "Cos5", "name": "cos5"}, {"description": "CoS 6", "help": "CoS 6.", "label": "Cos6", "name": "cos6"}, {"description": "CoS 7", "help": "CoS 7.", "label": "Cos7", "name": "cos7"}] | None = ...,
        auth_type: Literal[{"description": "Automatically choose the authentication method", "help": "Automatically choose the authentication method.", "label": "Auto", "name": "auto"}, {"description": "PAP authentication", "help": "PAP authentication.", "label": "Pap", "name": "pap"}, {"description": "CHAP authentication", "help": "CHAP authentication.", "label": "Chap", "name": "chap"}, {"description": "MS-CHAPv1 authentication", "help": "MS-CHAPv1 authentication.", "label": "Mschapv1", "name": "mschapv1"}, {"description": "MS-CHAPv2 authentication", "help": "MS-CHAPv2 authentication.", "label": "Mschapv2", "name": "mschapv2"}] | None = ...,
        ipunnumbered: str | None = ...,
        pppoe_unnumbered_negotiate: Literal[{"description": "Enable PPPoE unnumbered negotiation", "help": "Enable PPPoE unnumbered negotiation.", "label": "Enable", "name": "enable"}, {"description": "Disable PPPoE unnumbered negotiation", "help": "Disable PPPoE unnumbered negotiation.", "label": "Disable", "name": "disable"}] | None = ...,
        idle_timeout: int | None = ...,
        multilink: Literal[{"description": "Enable PPP multilink support", "help": "Enable PPP multilink support.", "label": "Enable", "name": "enable"}, {"description": "Disable PPP multilink support", "help": "Disable PPP multilink support.", "label": "Disable", "name": "disable"}] | None = ...,
        mrru: int | None = ...,
        disc_retry_timeout: int | None = ...,
        padt_retry_timeout: int | None = ...,
        service_name: str | None = ...,
        ac_name: str | None = ...,
        lcp_echo_interval: int | None = ...,
        lcp_max_echo_fails: int | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: PppoeInterfacePayload | None = ...,
        name: str | None = ...,
        dial_on_demand: Literal[{"description": "Enable dial on demand", "help": "Enable dial on demand.", "label": "Enable", "name": "enable"}, {"description": "Disable dial on demand", "help": "Disable dial on demand.", "label": "Disable", "name": "disable"}] | None = ...,
        ipv6: Literal[{"description": "Enable IPv6CP", "help": "Enable IPv6CP.", "label": "Enable", "name": "enable"}, {"description": "Disable IPv6CP", "help": "Disable IPv6CP.", "label": "Disable", "name": "disable"}] | None = ...,
        device: str | None = ...,
        username: str | None = ...,
        password: str | None = ...,
        pppoe_egress_cos: Literal[{"description": "CoS 0", "help": "CoS 0.", "label": "Cos0", "name": "cos0"}, {"description": "CoS 1", "help": "CoS 1.", "label": "Cos1", "name": "cos1"}, {"description": "CoS 2", "help": "CoS 2.", "label": "Cos2", "name": "cos2"}, {"description": "CoS 3", "help": "CoS 3.", "label": "Cos3", "name": "cos3"}, {"description": "CoS 4", "help": "CoS 4.", "label": "Cos4", "name": "cos4"}, {"description": "CoS 5", "help": "CoS 5.", "label": "Cos5", "name": "cos5"}, {"description": "CoS 6", "help": "CoS 6.", "label": "Cos6", "name": "cos6"}, {"description": "CoS 7", "help": "CoS 7.", "label": "Cos7", "name": "cos7"}] | None = ...,
        auth_type: Literal[{"description": "Automatically choose the authentication method", "help": "Automatically choose the authentication method.", "label": "Auto", "name": "auto"}, {"description": "PAP authentication", "help": "PAP authentication.", "label": "Pap", "name": "pap"}, {"description": "CHAP authentication", "help": "CHAP authentication.", "label": "Chap", "name": "chap"}, {"description": "MS-CHAPv1 authentication", "help": "MS-CHAPv1 authentication.", "label": "Mschapv1", "name": "mschapv1"}, {"description": "MS-CHAPv2 authentication", "help": "MS-CHAPv2 authentication.", "label": "Mschapv2", "name": "mschapv2"}] | None = ...,
        ipunnumbered: str | None = ...,
        pppoe_unnumbered_negotiate: Literal[{"description": "Enable PPPoE unnumbered negotiation", "help": "Enable PPPoE unnumbered negotiation.", "label": "Enable", "name": "enable"}, {"description": "Disable PPPoE unnumbered negotiation", "help": "Disable PPPoE unnumbered negotiation.", "label": "Disable", "name": "disable"}] | None = ...,
        idle_timeout: int | None = ...,
        multilink: Literal[{"description": "Enable PPP multilink support", "help": "Enable PPP multilink support.", "label": "Enable", "name": "enable"}, {"description": "Disable PPP multilink support", "help": "Disable PPP multilink support.", "label": "Disable", "name": "disable"}] | None = ...,
        mrru: int | None = ...,
        disc_retry_timeout: int | None = ...,
        padt_retry_timeout: int | None = ...,
        service_name: str | None = ...,
        ac_name: str | None = ...,
        lcp_echo_interval: int | None = ...,
        lcp_max_echo_fails: int | None = ...,
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
        payload_dict: PppoeInterfacePayload | None = ...,
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
    "PppoeInterface",
    "PppoeInterfacePayload",
]