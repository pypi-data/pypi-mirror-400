from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class SpeedTestSchedulePayload(TypedDict, total=False):
    """
    Type hints for system/speed_test_schedule payload fields.
    
    Speed test schedule for each interface.
    
    **Related Resources:**

    Dependencies (resources this endpoint references):
        - :class:`~.system.interface.InterfaceEndpoint` (via: interface)
        - :class:`~.system.speed-test-server.SpeedTestServerEndpoint` (via: server-name)

    **Usage:**
        payload: SpeedTestSchedulePayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    interface: NotRequired[str]  # Interface name.
    status: NotRequired[Literal[{"description": "Disable scheduled speed test", "help": "Disable scheduled speed test.", "label": "Disable", "name": "disable"}, {"description": "Enable scheduled speed test", "help": "Enable scheduled speed test.", "label": "Enable", "name": "enable"}]]  # Enable/disable scheduled speed test.
    diffserv: NotRequired[str]  # DSCP used for speed test.
    server_name: NotRequired[str]  # Speed test server name in system.speed-test-server list or l
    mode: NotRequired[Literal[{"description": "Protocol UDP for speed test", "help": "Protocol UDP for speed test.", "label": "Udp", "name": "UDP"}, {"description": "Protocol TCP for speed test", "help": "Protocol TCP for speed test.", "label": "Tcp", "name": "TCP"}, {"description": "Dynamically selects TCP or UDP based on the speed test setting", "help": "Dynamically selects TCP or UDP based on the speed test setting", "label": "Auto", "name": "Auto"}]]  # Protocol Auto(default), TCP or UDP used for speed test.
    schedules: list[dict[str, Any]]  # Schedules for the interface.
    dynamic_server: NotRequired[Literal[{"description": "Disable dynamic server", "help": "Disable dynamic server.", "label": "Disable", "name": "disable"}, {"description": "Enable dynamic server", "help": "Enable dynamic server.The speed test server will be found automatically.", "label": "Enable", "name": "enable"}]]  # Enable/disable dynamic server option.
    ctrl_port: NotRequired[int]  # Port of the controller to get access token.
    server_port: NotRequired[int]  # Port of the server to run speed test.
    update_shaper: NotRequired[Literal[{"description": "Disable updating egress shaper", "help": "Disable updating egress shaper.", "label": "Disable", "name": "disable"}, {"description": "Update local-side egress shaper", "help": "Update local-side egress shaper.", "label": "Local", "name": "local"}, {"description": "Update remote-side egress shaper", "help": "Update remote-side egress shaper.", "label": "Remote", "name": "remote"}, {"description": "Update both local-side and remote-side egress shaper", "help": "Update both local-side and remote-side egress shaper.", "label": "Both", "name": "both"}]]  # Set egress shaper based on the test result.
    update_inbandwidth: NotRequired[Literal[{"description": "Honor interface\u0027s inbandwidth shaping", "help": "Honor interface\u0027s inbandwidth shaping.", "label": "Disable", "name": "disable"}, {"description": "Ignore interface\u0027s inbandwidth shaping", "help": "Ignore interface\u0027s inbandwidth shaping.", "label": "Enable", "name": "enable"}]]  # Enable/disable bypassing interface's inbound bandwidth setti
    update_outbandwidth: NotRequired[Literal[{"description": "Honor interface\u0027s outbandwidth shaping", "help": "Honor interface\u0027s outbandwidth shaping.", "label": "Disable", "name": "disable"}, {"description": "Ignore updating interface\u0027s outbandwidth shaping", "help": "Ignore updating interface\u0027s outbandwidth shaping.", "label": "Enable", "name": "enable"}]]  # Enable/disable bypassing interface's outbound bandwidth sett
    update_interface_shaping: NotRequired[Literal[{"description": "Disable updating interface shaping", "help": "Disable updating interface shaping.", "label": "Disable", "name": "disable"}, {"description": "Enable updating interface shaping", "help": "Enable updating interface shaping.", "label": "Enable", "name": "enable"}]]  # Enable/disable using the speedtest results as reference for 
    update_inbandwidth_maximum: NotRequired[int]  # Maximum downloading bandwidth (kbps) to be used in a speed t
    update_inbandwidth_minimum: NotRequired[int]  # Minimum downloading bandwidth (kbps) to be considered effect
    update_outbandwidth_maximum: NotRequired[int]  # Maximum uploading bandwidth (kbps) to be used in a speed tes
    update_outbandwidth_minimum: NotRequired[int]  # Minimum uploading bandwidth (kbps) to be considered effectiv
    expected_inbandwidth_minimum: NotRequired[int]  # Set the minimum inbandwidth threshold for applying speedtest
    expected_inbandwidth_maximum: NotRequired[int]  # Set the maximum inbandwidth threshold for applying speedtest
    expected_outbandwidth_minimum: NotRequired[int]  # Set the minimum outbandwidth threshold for applying speedtes
    expected_outbandwidth_maximum: NotRequired[int]  # Set the maximum outbandwidth threshold for applying speedtes
    retries: NotRequired[int]  # Maximum number of times the FortiGate unit will attempt to c
    retry_pause: NotRequired[int]  # Number of seconds the FortiGate pauses between successive sp


class SpeedTestSchedule:
    """
    Speed test schedule for each interface.
    
    Path: system/speed_test_schedule
    Category: cmdb
    Primary Key: interface
    """
    
    # Overloads for get() with response_mode="object"
    @overload
    def get(
        self,
        interface: str | None = ...,
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
        interface: str,
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
        interface: str | None = ...,
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
        interface: str | None = ...,
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
        interface: str | None = ...,
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
        payload_dict: SpeedTestSchedulePayload | None = ...,
        interface: str | None = ...,
        status: Literal[{"description": "Disable scheduled speed test", "help": "Disable scheduled speed test.", "label": "Disable", "name": "disable"}, {"description": "Enable scheduled speed test", "help": "Enable scheduled speed test.", "label": "Enable", "name": "enable"}] | None = ...,
        diffserv: str | None = ...,
        server_name: str | None = ...,
        mode: Literal[{"description": "Protocol UDP for speed test", "help": "Protocol UDP for speed test.", "label": "Udp", "name": "UDP"}, {"description": "Protocol TCP for speed test", "help": "Protocol TCP for speed test.", "label": "Tcp", "name": "TCP"}, {"description": "Dynamically selects TCP or UDP based on the speed test setting", "help": "Dynamically selects TCP or UDP based on the speed test setting", "label": "Auto", "name": "Auto"}] | None = ...,
        schedules: list[dict[str, Any]] | None = ...,
        dynamic_server: Literal[{"description": "Disable dynamic server", "help": "Disable dynamic server.", "label": "Disable", "name": "disable"}, {"description": "Enable dynamic server", "help": "Enable dynamic server.The speed test server will be found automatically.", "label": "Enable", "name": "enable"}] | None = ...,
        ctrl_port: int | None = ...,
        server_port: int | None = ...,
        update_shaper: Literal[{"description": "Disable updating egress shaper", "help": "Disable updating egress shaper.", "label": "Disable", "name": "disable"}, {"description": "Update local-side egress shaper", "help": "Update local-side egress shaper.", "label": "Local", "name": "local"}, {"description": "Update remote-side egress shaper", "help": "Update remote-side egress shaper.", "label": "Remote", "name": "remote"}, {"description": "Update both local-side and remote-side egress shaper", "help": "Update both local-side and remote-side egress shaper.", "label": "Both", "name": "both"}] | None = ...,
        update_inbandwidth: Literal[{"description": "Honor interface\u0027s inbandwidth shaping", "help": "Honor interface\u0027s inbandwidth shaping.", "label": "Disable", "name": "disable"}, {"description": "Ignore interface\u0027s inbandwidth shaping", "help": "Ignore interface\u0027s inbandwidth shaping.", "label": "Enable", "name": "enable"}] | None = ...,
        update_outbandwidth: Literal[{"description": "Honor interface\u0027s outbandwidth shaping", "help": "Honor interface\u0027s outbandwidth shaping.", "label": "Disable", "name": "disable"}, {"description": "Ignore updating interface\u0027s outbandwidth shaping", "help": "Ignore updating interface\u0027s outbandwidth shaping.", "label": "Enable", "name": "enable"}] | None = ...,
        update_interface_shaping: Literal[{"description": "Disable updating interface shaping", "help": "Disable updating interface shaping.", "label": "Disable", "name": "disable"}, {"description": "Enable updating interface shaping", "help": "Enable updating interface shaping.", "label": "Enable", "name": "enable"}] | None = ...,
        update_inbandwidth_maximum: int | None = ...,
        update_inbandwidth_minimum: int | None = ...,
        update_outbandwidth_maximum: int | None = ...,
        update_outbandwidth_minimum: int | None = ...,
        expected_inbandwidth_minimum: int | None = ...,
        expected_inbandwidth_maximum: int | None = ...,
        expected_outbandwidth_minimum: int | None = ...,
        expected_outbandwidth_maximum: int | None = ...,
        retries: int | None = ...,
        retry_pause: int | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: SpeedTestSchedulePayload | None = ...,
        interface: str | None = ...,
        status: Literal[{"description": "Disable scheduled speed test", "help": "Disable scheduled speed test.", "label": "Disable", "name": "disable"}, {"description": "Enable scheduled speed test", "help": "Enable scheduled speed test.", "label": "Enable", "name": "enable"}] | None = ...,
        diffserv: str | None = ...,
        server_name: str | None = ...,
        mode: Literal[{"description": "Protocol UDP for speed test", "help": "Protocol UDP for speed test.", "label": "Udp", "name": "UDP"}, {"description": "Protocol TCP for speed test", "help": "Protocol TCP for speed test.", "label": "Tcp", "name": "TCP"}, {"description": "Dynamically selects TCP or UDP based on the speed test setting", "help": "Dynamically selects TCP or UDP based on the speed test setting", "label": "Auto", "name": "Auto"}] | None = ...,
        schedules: list[dict[str, Any]] | None = ...,
        dynamic_server: Literal[{"description": "Disable dynamic server", "help": "Disable dynamic server.", "label": "Disable", "name": "disable"}, {"description": "Enable dynamic server", "help": "Enable dynamic server.The speed test server will be found automatically.", "label": "Enable", "name": "enable"}] | None = ...,
        ctrl_port: int | None = ...,
        server_port: int | None = ...,
        update_shaper: Literal[{"description": "Disable updating egress shaper", "help": "Disable updating egress shaper.", "label": "Disable", "name": "disable"}, {"description": "Update local-side egress shaper", "help": "Update local-side egress shaper.", "label": "Local", "name": "local"}, {"description": "Update remote-side egress shaper", "help": "Update remote-side egress shaper.", "label": "Remote", "name": "remote"}, {"description": "Update both local-side and remote-side egress shaper", "help": "Update both local-side and remote-side egress shaper.", "label": "Both", "name": "both"}] | None = ...,
        update_inbandwidth: Literal[{"description": "Honor interface\u0027s inbandwidth shaping", "help": "Honor interface\u0027s inbandwidth shaping.", "label": "Disable", "name": "disable"}, {"description": "Ignore interface\u0027s inbandwidth shaping", "help": "Ignore interface\u0027s inbandwidth shaping.", "label": "Enable", "name": "enable"}] | None = ...,
        update_outbandwidth: Literal[{"description": "Honor interface\u0027s outbandwidth shaping", "help": "Honor interface\u0027s outbandwidth shaping.", "label": "Disable", "name": "disable"}, {"description": "Ignore updating interface\u0027s outbandwidth shaping", "help": "Ignore updating interface\u0027s outbandwidth shaping.", "label": "Enable", "name": "enable"}] | None = ...,
        update_interface_shaping: Literal[{"description": "Disable updating interface shaping", "help": "Disable updating interface shaping.", "label": "Disable", "name": "disable"}, {"description": "Enable updating interface shaping", "help": "Enable updating interface shaping.", "label": "Enable", "name": "enable"}] | None = ...,
        update_inbandwidth_maximum: int | None = ...,
        update_inbandwidth_minimum: int | None = ...,
        update_outbandwidth_maximum: int | None = ...,
        update_outbandwidth_minimum: int | None = ...,
        expected_inbandwidth_minimum: int | None = ...,
        expected_inbandwidth_maximum: int | None = ...,
        expected_outbandwidth_minimum: int | None = ...,
        expected_outbandwidth_maximum: int | None = ...,
        retries: int | None = ...,
        retry_pause: int | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def delete(
        self,
        interface: str | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def exists(
        self,
        interface: str,
        vdom: str | bool | None = ...,
    ) -> Union[bool, Coroutine[Any, Any, bool]]: ...
    
    def set(
        self,
        payload_dict: SpeedTestSchedulePayload | None = ...,
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
    "SpeedTestSchedule",
    "SpeedTestSchedulePayload",
]