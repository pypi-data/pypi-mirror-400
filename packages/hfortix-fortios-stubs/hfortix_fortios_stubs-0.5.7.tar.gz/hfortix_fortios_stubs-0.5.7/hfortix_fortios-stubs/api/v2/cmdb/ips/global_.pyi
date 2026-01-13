from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class GlobalPayload(TypedDict, total=False):
    """
    Type hints for ips/global_ payload fields.
    
    Configure IPS global parameter.
    
    **Usage:**
        payload: GlobalPayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    fail_open: NotRequired[Literal[{"description": "Enable IPS fail open", "help": "Enable IPS fail open.", "label": "Enable", "name": "enable"}, {"description": "Disable IPS fail open", "help": "Disable IPS fail open.", "label": "Disable", "name": "disable"}]]  # Enable to allow traffic if the IPS buffer is full. Default i
    database: NotRequired[Literal[{"description": "IPS regular database package", "help": "IPS regular database package.", "label": "Regular", "name": "regular"}, {"description": "IPS extended database package", "help": "IPS extended database package.", "label": "Extended", "name": "extended"}]]  # Regular or extended IPS database. Regular protects against t
    traffic_submit: NotRequired[Literal[{"description": "Enable traffic submit", "help": "Enable traffic submit.", "label": "Enable", "name": "enable"}, {"description": "Disable traffic submit", "help": "Disable traffic submit.", "label": "Disable", "name": "disable"}]]  # Enable/disable submitting attack data found by this FortiGat
    anomaly_mode: NotRequired[Literal[{"description": "After an anomaly is detected, allow the number of packets per second according to the anomaly configuration", "help": "After an anomaly is detected, allow the number of packets per second according to the anomaly configuration.", "label": "Periodical", "name": "periodical"}, {"description": "Block packets once an anomaly is detected", "help": "Block packets once an anomaly is detected. Overrides individual anomaly settings.", "label": "Continuous", "name": "continuous"}]]  # Global blocking mode for rate-based anomalies.
    session_limit_mode: NotRequired[Literal[{"description": "Accurately count concurrent sessions, demands more resources", "help": "Accurately count concurrent sessions, demands more resources.", "label": "Accurate", "name": "accurate"}, {"description": "Use heuristics to estimate the number of concurrent sessions", "help": "Use heuristics to estimate the number of concurrent sessions. Acceptable in most cases.", "label": "Heuristic", "name": "heuristic"}]]  # Method of counting concurrent sessions used by session limit
    socket_size: NotRequired[int]  # IPS socket buffer size. Max and default value depend on avai
    engine_count: NotRequired[int]  # Number of IPS engines running. If set to the default value o
    sync_session_ttl: NotRequired[Literal[{"description": "Enable use of kernel session TTL for IPS sessions", "help": "Enable use of kernel session TTL for IPS sessions.", "label": "Enable", "name": "enable"}, {"description": "Disable use of kernel session TTL for IPS sessions", "help": "Disable use of kernel session TTL for IPS sessions.", "label": "Disable", "name": "disable"}]]  # Enable/disable use of kernel session TTL for IPS sessions.
    deep_app_insp_timeout: NotRequired[int]  # Timeout for Deep application inspection (1 - 2147483647 sec.
    deep_app_insp_db_limit: NotRequired[int]  # Limit on number of entries in deep application inspection da
    exclude_signatures: NotRequired[Literal[{"description": "No signatures excluded", "help": "No signatures excluded.", "label": "None", "name": "none"}, {"description": "Exclude ot signatures", "help": "Exclude ot signatures.", "label": "Ot", "name": "ot"}]]  # Excluded signatures.
    packet_log_queue_depth: NotRequired[int]  # Packet/pcap log queue depth per IPS engine.
    ngfw_max_scan_range: NotRequired[int]  # NGFW policy-mode app detection threshold.
    av_mem_limit: NotRequired[int]  # Maximum percentage of system memory allowed for use on AV sc
    machine_learning_detection: NotRequired[Literal[{"description": "Enable ML detection", "help": "Enable ML detection.", "label": "Enable", "name": "enable"}, {"description": "Disable ML detection", "help": "Disable ML detection.", "label": "Disable", "name": "disable"}]]  # Enable/disable machine learning detection.
    tls_active_probe: NotRequired[str]  # TLS active probe configuration.


class Global:
    """
    Configure IPS global parameter.
    
    Path: ips/global_
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
        payload_dict: GlobalPayload | None = ...,
        fail_open: Literal[{"description": "Enable IPS fail open", "help": "Enable IPS fail open.", "label": "Enable", "name": "enable"}, {"description": "Disable IPS fail open", "help": "Disable IPS fail open.", "label": "Disable", "name": "disable"}] | None = ...,
        database: Literal[{"description": "IPS regular database package", "help": "IPS regular database package.", "label": "Regular", "name": "regular"}, {"description": "IPS extended database package", "help": "IPS extended database package.", "label": "Extended", "name": "extended"}] | None = ...,
        traffic_submit: Literal[{"description": "Enable traffic submit", "help": "Enable traffic submit.", "label": "Enable", "name": "enable"}, {"description": "Disable traffic submit", "help": "Disable traffic submit.", "label": "Disable", "name": "disable"}] | None = ...,
        anomaly_mode: Literal[{"description": "After an anomaly is detected, allow the number of packets per second according to the anomaly configuration", "help": "After an anomaly is detected, allow the number of packets per second according to the anomaly configuration.", "label": "Periodical", "name": "periodical"}, {"description": "Block packets once an anomaly is detected", "help": "Block packets once an anomaly is detected. Overrides individual anomaly settings.", "label": "Continuous", "name": "continuous"}] | None = ...,
        session_limit_mode: Literal[{"description": "Accurately count concurrent sessions, demands more resources", "help": "Accurately count concurrent sessions, demands more resources.", "label": "Accurate", "name": "accurate"}, {"description": "Use heuristics to estimate the number of concurrent sessions", "help": "Use heuristics to estimate the number of concurrent sessions. Acceptable in most cases.", "label": "Heuristic", "name": "heuristic"}] | None = ...,
        socket_size: int | None = ...,
        engine_count: int | None = ...,
        sync_session_ttl: Literal[{"description": "Enable use of kernel session TTL for IPS sessions", "help": "Enable use of kernel session TTL for IPS sessions.", "label": "Enable", "name": "enable"}, {"description": "Disable use of kernel session TTL for IPS sessions", "help": "Disable use of kernel session TTL for IPS sessions.", "label": "Disable", "name": "disable"}] | None = ...,
        deep_app_insp_timeout: int | None = ...,
        deep_app_insp_db_limit: int | None = ...,
        exclude_signatures: Literal[{"description": "No signatures excluded", "help": "No signatures excluded.", "label": "None", "name": "none"}, {"description": "Exclude ot signatures", "help": "Exclude ot signatures.", "label": "Ot", "name": "ot"}] | None = ...,
        packet_log_queue_depth: int | None = ...,
        ngfw_max_scan_range: int | None = ...,
        av_mem_limit: int | None = ...,
        machine_learning_detection: Literal[{"description": "Enable ML detection", "help": "Enable ML detection.", "label": "Enable", "name": "enable"}, {"description": "Disable ML detection", "help": "Disable ML detection.", "label": "Disable", "name": "disable"}] | None = ...,
        tls_active_probe: str | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: GlobalPayload | None = ...,
        fail_open: Literal[{"description": "Enable IPS fail open", "help": "Enable IPS fail open.", "label": "Enable", "name": "enable"}, {"description": "Disable IPS fail open", "help": "Disable IPS fail open.", "label": "Disable", "name": "disable"}] | None = ...,
        database: Literal[{"description": "IPS regular database package", "help": "IPS regular database package.", "label": "Regular", "name": "regular"}, {"description": "IPS extended database package", "help": "IPS extended database package.", "label": "Extended", "name": "extended"}] | None = ...,
        traffic_submit: Literal[{"description": "Enable traffic submit", "help": "Enable traffic submit.", "label": "Enable", "name": "enable"}, {"description": "Disable traffic submit", "help": "Disable traffic submit.", "label": "Disable", "name": "disable"}] | None = ...,
        anomaly_mode: Literal[{"description": "After an anomaly is detected, allow the number of packets per second according to the anomaly configuration", "help": "After an anomaly is detected, allow the number of packets per second according to the anomaly configuration.", "label": "Periodical", "name": "periodical"}, {"description": "Block packets once an anomaly is detected", "help": "Block packets once an anomaly is detected. Overrides individual anomaly settings.", "label": "Continuous", "name": "continuous"}] | None = ...,
        session_limit_mode: Literal[{"description": "Accurately count concurrent sessions, demands more resources", "help": "Accurately count concurrent sessions, demands more resources.", "label": "Accurate", "name": "accurate"}, {"description": "Use heuristics to estimate the number of concurrent sessions", "help": "Use heuristics to estimate the number of concurrent sessions. Acceptable in most cases.", "label": "Heuristic", "name": "heuristic"}] | None = ...,
        socket_size: int | None = ...,
        engine_count: int | None = ...,
        sync_session_ttl: Literal[{"description": "Enable use of kernel session TTL for IPS sessions", "help": "Enable use of kernel session TTL for IPS sessions.", "label": "Enable", "name": "enable"}, {"description": "Disable use of kernel session TTL for IPS sessions", "help": "Disable use of kernel session TTL for IPS sessions.", "label": "Disable", "name": "disable"}] | None = ...,
        deep_app_insp_timeout: int | None = ...,
        deep_app_insp_db_limit: int | None = ...,
        exclude_signatures: Literal[{"description": "No signatures excluded", "help": "No signatures excluded.", "label": "None", "name": "none"}, {"description": "Exclude ot signatures", "help": "Exclude ot signatures.", "label": "Ot", "name": "ot"}] | None = ...,
        packet_log_queue_depth: int | None = ...,
        ngfw_max_scan_range: int | None = ...,
        av_mem_limit: int | None = ...,
        machine_learning_detection: Literal[{"description": "Enable ML detection", "help": "Enable ML detection.", "label": "Enable", "name": "enable"}, {"description": "Disable ML detection", "help": "Disable ML detection.", "label": "Disable", "name": "disable"}] | None = ...,
        tls_active_probe: str | None = ...,
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
        payload_dict: GlobalPayload | None = ...,
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
    "Global",
    "GlobalPayload",
]