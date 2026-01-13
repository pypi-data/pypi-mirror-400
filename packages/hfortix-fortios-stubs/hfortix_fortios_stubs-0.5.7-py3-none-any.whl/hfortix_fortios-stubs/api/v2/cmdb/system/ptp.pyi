from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class PtpPayload(TypedDict, total=False):
    """
    Type hints for system/ptp payload fields.
    
    Configure system PTP information.
    
    **Related Resources:**

    Dependencies (resources this endpoint references):
        - :class:`~.system.interface.InterfaceEndpoint` (via: interface)

    **Usage:**
        payload: PtpPayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    status: NotRequired[Literal[{"description": "Enable synchronization with PTP Server", "help": "Enable synchronization with PTP Server.", "label": "Enable", "name": "enable"}, {"description": "Disable synchronization with PTP Server", "help": "Disable synchronization with PTP Server.", "label": "Disable", "name": "disable"}]]  # Enable/disable setting the FortiGate system time by synchron
    mode: NotRequired[Literal[{"description": "Send PTP packets with multicast", "help": "Send PTP packets with multicast.", "label": "Multicast", "name": "multicast"}, {"description": "Send PTP packets with unicast and multicast", "help": "Send PTP packets with unicast and multicast.", "label": "Hybrid", "name": "hybrid"}]]  # Multicast transmission or hybrid transmission.
    delay_mechanism: NotRequired[Literal[{"description": "End to end delay detection", "help": "End to end delay detection.", "label": "E2E", "name": "E2E"}, {"description": "Peer to peer delay detection", "help": "Peer to peer delay detection.", "label": "P2P", "name": "P2P"}]]  # End to end delay detection or peer to peer delay detection.
    request_interval: NotRequired[int]  # The delay request value is the logarithmic mean interval in 
    interface: str  # PTP client will reply through this interface.
    server_mode: NotRequired[Literal[{"description": "Enable FortiGate PTP server mode", "help": "Enable FortiGate PTP server mode.", "label": "Enable", "name": "enable"}, {"description": "Disable FortiGate PTP server mode", "help": "Disable FortiGate PTP server mode.", "label": "Disable", "name": "disable"}]]  # Enable/disable FortiGate PTP server mode. Your FortiGate bec
    server_interface: NotRequired[list[dict[str, Any]]]  # FortiGate interface(s) with PTP server mode enabled. Devices


class Ptp:
    """
    Configure system PTP information.
    
    Path: system/ptp
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
        payload_dict: PtpPayload | None = ...,
        status: Literal[{"description": "Enable synchronization with PTP Server", "help": "Enable synchronization with PTP Server.", "label": "Enable", "name": "enable"}, {"description": "Disable synchronization with PTP Server", "help": "Disable synchronization with PTP Server.", "label": "Disable", "name": "disable"}] | None = ...,
        mode: Literal[{"description": "Send PTP packets with multicast", "help": "Send PTP packets with multicast.", "label": "Multicast", "name": "multicast"}, {"description": "Send PTP packets with unicast and multicast", "help": "Send PTP packets with unicast and multicast.", "label": "Hybrid", "name": "hybrid"}] | None = ...,
        delay_mechanism: Literal[{"description": "End to end delay detection", "help": "End to end delay detection.", "label": "E2E", "name": "E2E"}, {"description": "Peer to peer delay detection", "help": "Peer to peer delay detection.", "label": "P2P", "name": "P2P"}] | None = ...,
        request_interval: int | None = ...,
        interface: str | None = ...,
        server_mode: Literal[{"description": "Enable FortiGate PTP server mode", "help": "Enable FortiGate PTP server mode.", "label": "Enable", "name": "enable"}, {"description": "Disable FortiGate PTP server mode", "help": "Disable FortiGate PTP server mode.", "label": "Disable", "name": "disable"}] | None = ...,
        server_interface: list[dict[str, Any]] | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: PtpPayload | None = ...,
        status: Literal[{"description": "Enable synchronization with PTP Server", "help": "Enable synchronization with PTP Server.", "label": "Enable", "name": "enable"}, {"description": "Disable synchronization with PTP Server", "help": "Disable synchronization with PTP Server.", "label": "Disable", "name": "disable"}] | None = ...,
        mode: Literal[{"description": "Send PTP packets with multicast", "help": "Send PTP packets with multicast.", "label": "Multicast", "name": "multicast"}, {"description": "Send PTP packets with unicast and multicast", "help": "Send PTP packets with unicast and multicast.", "label": "Hybrid", "name": "hybrid"}] | None = ...,
        delay_mechanism: Literal[{"description": "End to end delay detection", "help": "End to end delay detection.", "label": "E2E", "name": "E2E"}, {"description": "Peer to peer delay detection", "help": "Peer to peer delay detection.", "label": "P2P", "name": "P2P"}] | None = ...,
        request_interval: int | None = ...,
        interface: str | None = ...,
        server_mode: Literal[{"description": "Enable FortiGate PTP server mode", "help": "Enable FortiGate PTP server mode.", "label": "Enable", "name": "enable"}, {"description": "Disable FortiGate PTP server mode", "help": "Disable FortiGate PTP server mode.", "label": "Disable", "name": "disable"}] | None = ...,
        server_interface: list[dict[str, Any]] | None = ...,
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
        payload_dict: PtpPayload | None = ...,
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
    "Ptp",
    "PtpPayload",
]