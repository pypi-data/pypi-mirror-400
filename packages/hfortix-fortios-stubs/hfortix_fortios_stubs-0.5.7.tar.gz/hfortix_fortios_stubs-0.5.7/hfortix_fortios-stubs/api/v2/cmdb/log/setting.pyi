from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class SettingPayload(TypedDict, total=False):
    """
    Type hints for log/setting payload fields.
    
    Configure general log settings.
    
    **Usage:**
        payload: SettingPayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    resolve_ip: NotRequired[Literal[{"description": "Enable adding resolved domain names to traffic logs", "help": "Enable adding resolved domain names to traffic logs.", "label": "Enable", "name": "enable"}, {"description": "Disable adding resolved domain names to traffic logs", "help": "Disable adding resolved domain names to traffic logs.", "label": "Disable", "name": "disable"}]]  # Enable/disable adding resolved domain names to traffic logs 
    resolve_port: NotRequired[Literal[{"description": "Enable adding resolved service names to traffic logs", "help": "Enable adding resolved service names to traffic logs.", "label": "Enable", "name": "enable"}, {"description": "Disable adding resolved service names to traffic logs", "help": "Disable adding resolved service names to traffic logs.", "label": "Disable", "name": "disable"}]]  # Enable/disable adding resolved service names to traffic logs
    log_user_in_upper: NotRequired[Literal[{"description": "Enable logs with user-in-upper", "help": "Enable logs with user-in-upper.", "label": "Enable", "name": "enable"}, {"description": "Disable logs with user-in-upper", "help": "Disable logs with user-in-upper.", "label": "Disable", "name": "disable"}]]  # Enable/disable logs with user-in-upper.
    fwpolicy_implicit_log: NotRequired[Literal[{"description": "Enable implicit firewall policy logging", "help": "Enable implicit firewall policy logging.", "label": "Enable", "name": "enable"}, {"description": "Disable implicit firewall policy logging", "help": "Disable implicit firewall policy logging.", "label": "Disable", "name": "disable"}]]  # Enable/disable implicit firewall policy logging.
    fwpolicy6_implicit_log: NotRequired[Literal[{"description": "Enable implicit firewall policy6 logging", "help": "Enable implicit firewall policy6 logging.", "label": "Enable", "name": "enable"}, {"description": "Disable implicit firewall policy6 logging", "help": "Disable implicit firewall policy6 logging.", "label": "Disable", "name": "disable"}]]  # Enable/disable implicit firewall policy6 logging.
    extended_log: NotRequired[Literal[{"description": "Enable extended traffic logging", "help": "Enable extended traffic logging.", "label": "Enable", "name": "enable"}, {"description": "Disable extended traffic logging", "help": "Disable extended traffic logging.", "label": "Disable", "name": "disable"}]]  # Enable/disable extended traffic logging.
    local_in_allow: NotRequired[Literal[{"description": "Enable local-in-allow logging", "help": "Enable local-in-allow logging.", "label": "Enable", "name": "enable"}, {"description": "Disable local-in-allow logging", "help": "Disable local-in-allow logging.", "label": "Disable", "name": "disable"}]]  # Enable/disable local-in-allow logging.
    local_in_deny_unicast: NotRequired[Literal[{"description": "Enable local-in-deny-unicast logging", "help": "Enable local-in-deny-unicast logging.", "label": "Enable", "name": "enable"}, {"description": "Disable local-in-deny-unicast logging", "help": "Disable local-in-deny-unicast logging.", "label": "Disable", "name": "disable"}]]  # Enable/disable local-in-deny-unicast logging.
    local_in_deny_broadcast: NotRequired[Literal[{"description": "Enable local-in-deny-broadcast logging", "help": "Enable local-in-deny-broadcast logging.", "label": "Enable", "name": "enable"}, {"description": "Disable local-in-deny-broadcast logging", "help": "Disable local-in-deny-broadcast logging.", "label": "Disable", "name": "disable"}]]  # Enable/disable local-in-deny-broadcast logging.
    local_in_policy_log: NotRequired[Literal[{"description": "Enable local-in-policy logging", "help": "Enable local-in-policy logging.", "label": "Enable", "name": "enable"}, {"description": "Disable local-in-policy logging", "help": "Disable local-in-policy logging.", "label": "Disable", "name": "disable"}]]  # Enable/disable local-in-policy logging.
    local_out: NotRequired[Literal[{"description": "Enable local-out logging", "help": "Enable local-out logging.", "label": "Enable", "name": "enable"}, {"description": "Disable local-out logging", "help": "Disable local-out logging.", "label": "Disable", "name": "disable"}]]  # Enable/disable local-out logging.
    local_out_ioc_detection: NotRequired[Literal[{"description": "Enable local-out traffic IoC detection", "help": "Enable local-out traffic IoC detection. Requires local-out to be enabled.", "label": "Enable", "name": "enable"}, {"description": "Disable local-out traffic IoC detection", "help": "Disable local-out traffic IoC detection.", "label": "Disable", "name": "disable"}]]  # Enable/disable local-out traffic IoC detection. Requires loc
    daemon_log: NotRequired[Literal[{"description": "Enable daemon logging", "help": "Enable daemon logging.", "label": "Enable", "name": "enable"}, {"description": "Disable daemon logging", "help": "Disable daemon logging.", "label": "Disable", "name": "disable"}]]  # Enable/disable daemon logging.
    neighbor_event: NotRequired[Literal[{"description": "Enable neighbor event logging", "help": "Enable neighbor event logging.", "label": "Enable", "name": "enable"}, {"description": "Disable neighbor event logging", "help": "Disable neighbor event logging.", "label": "Disable", "name": "disable"}]]  # Enable/disable neighbor event logging.
    brief_traffic_format: NotRequired[Literal[{"description": "Enable brief format traffic logging", "help": "Enable brief format traffic logging.", "label": "Enable", "name": "enable"}, {"description": "Disable brief format traffic logging", "help": "Disable brief format traffic logging.", "label": "Disable", "name": "disable"}]]  # Enable/disable brief format traffic logging.
    user_anonymize: NotRequired[Literal[{"description": "Enable anonymizing user names in log messages", "help": "Enable anonymizing user names in log messages.", "label": "Enable", "name": "enable"}, {"description": "Disable anonymizing user names in log messages", "help": "Disable anonymizing user names in log messages.", "label": "Disable", "name": "disable"}]]  # Enable/disable anonymizing user names in log messages.
    expolicy_implicit_log: NotRequired[Literal[{"description": "Enable proxy firewall implicit policy logging", "help": "Enable proxy firewall implicit policy logging.", "label": "Enable", "name": "enable"}, {"description": "Disable proxy firewall implicit policy logging", "help": "Disable proxy firewall implicit policy logging.", "label": "Disable", "name": "disable"}]]  # Enable/disable proxy firewall implicit policy logging.
    log_policy_comment: NotRequired[Literal[{"description": "Enable inserting policy comments into traffic logs", "help": "Enable inserting policy comments into traffic logs.", "label": "Enable", "name": "enable"}, {"description": "Disable inserting policy comments into traffic logs", "help": "Disable inserting policy comments into traffic logs.", "label": "Disable", "name": "disable"}]]  # Enable/disable inserting policy comments into traffic logs.
    faz_override: NotRequired[Literal[{"description": "Enable override FortiAnalyzer settings", "help": "Enable override FortiAnalyzer settings.", "label": "Enable", "name": "enable"}, {"description": "Disable override FortiAnalyzer settings", "help": "Disable override FortiAnalyzer settings.", "label": "Disable", "name": "disable"}]]  # Enable/disable override FortiAnalyzer settings.
    syslog_override: NotRequired[Literal[{"description": "Enable override Syslog settings", "help": "Enable override Syslog settings.", "label": "Enable", "name": "enable"}, {"description": "Disable override Syslog settings", "help": "Disable override Syslog settings.", "label": "Disable", "name": "disable"}]]  # Enable/disable override Syslog settings.
    rest_api_set: NotRequired[Literal[{"description": "Enable POST/PUT/DELETE REST API logging", "help": "Enable POST/PUT/DELETE REST API logging.", "label": "Enable", "name": "enable"}, {"description": "Disable POST/PUT/DELETE REST API logging", "help": "Disable POST/PUT/DELETE REST API logging.", "label": "Disable", "name": "disable"}]]  # Enable/disable REST API POST/PUT/DELETE request logging.
    rest_api_get: NotRequired[Literal[{"description": "Enable GET REST API logging", "help": "Enable GET REST API logging.", "label": "Enable", "name": "enable"}, {"description": "Disable GET REST API logging", "help": "Disable GET REST API logging.", "label": "Disable", "name": "disable"}]]  # Enable/disable REST API GET request logging.
    rest_api_performance: NotRequired[Literal[{"description": "Enable REST API performance stats in REST API logs", "help": "Enable REST API performance stats in REST API logs.", "label": "Enable", "name": "enable"}, {"description": "Disable REST API performance stats in REST API logs", "help": "Disable REST API performance stats in REST API logs.", "label": "Disable", "name": "disable"}]]  # Enable/disable REST API memory and performance stats in rest
    long_live_session_stat: NotRequired[Literal[{"description": "Enable long-live-session statistics logging", "help": "Enable long-live-session statistics logging.", "label": "Enable", "name": "enable"}, {"description": "Disable long-live-session statistics logging", "help": "Disable long-live-session statistics logging.", "label": "Disable", "name": "disable"}]]  # Enable/disable long-live-session statistics logging.
    extended_utm_log: NotRequired[Literal[{"description": "Enable extended UTM logging", "help": "Enable extended UTM logging.", "label": "Enable", "name": "enable"}, {"description": "Disable extended UTM logging", "help": "Disable extended UTM logging.", "label": "Disable", "name": "disable"}]]  # Enable/disable extended UTM logging.
    zone_name: NotRequired[Literal[{"description": "Enable zone name logging", "help": "Enable zone name logging.", "label": "Enable", "name": "enable"}, {"description": "Disable zone name logging", "help": "Disable zone name logging.", "label": "Disable", "name": "disable"}]]  # Enable/disable zone name logging.
    web_svc_perf: NotRequired[Literal[{"description": "Enable web-svc performance logging", "help": "Enable web-svc performance logging.", "label": "Enable", "name": "enable"}, {"description": "Disable web-svc performance logging", "help": "Disable web-svc performance logging.", "label": "Disable", "name": "disable"}]]  # Enable/disable web-svc performance logging.
    custom_log_fields: NotRequired[list[dict[str, Any]]]  # Custom fields to append to all log messages.
    anonymization_hash: NotRequired[str]  # User name anonymization hash salt.


class Setting:
    """
    Configure general log settings.
    
    Path: log/setting
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
        payload_dict: SettingPayload | None = ...,
        resolve_ip: Literal[{"description": "Enable adding resolved domain names to traffic logs", "help": "Enable adding resolved domain names to traffic logs.", "label": "Enable", "name": "enable"}, {"description": "Disable adding resolved domain names to traffic logs", "help": "Disable adding resolved domain names to traffic logs.", "label": "Disable", "name": "disable"}] | None = ...,
        resolve_port: Literal[{"description": "Enable adding resolved service names to traffic logs", "help": "Enable adding resolved service names to traffic logs.", "label": "Enable", "name": "enable"}, {"description": "Disable adding resolved service names to traffic logs", "help": "Disable adding resolved service names to traffic logs.", "label": "Disable", "name": "disable"}] | None = ...,
        log_user_in_upper: Literal[{"description": "Enable logs with user-in-upper", "help": "Enable logs with user-in-upper.", "label": "Enable", "name": "enable"}, {"description": "Disable logs with user-in-upper", "help": "Disable logs with user-in-upper.", "label": "Disable", "name": "disable"}] | None = ...,
        fwpolicy_implicit_log: Literal[{"description": "Enable implicit firewall policy logging", "help": "Enable implicit firewall policy logging.", "label": "Enable", "name": "enable"}, {"description": "Disable implicit firewall policy logging", "help": "Disable implicit firewall policy logging.", "label": "Disable", "name": "disable"}] | None = ...,
        fwpolicy6_implicit_log: Literal[{"description": "Enable implicit firewall policy6 logging", "help": "Enable implicit firewall policy6 logging.", "label": "Enable", "name": "enable"}, {"description": "Disable implicit firewall policy6 logging", "help": "Disable implicit firewall policy6 logging.", "label": "Disable", "name": "disable"}] | None = ...,
        extended_log: Literal[{"description": "Enable extended traffic logging", "help": "Enable extended traffic logging.", "label": "Enable", "name": "enable"}, {"description": "Disable extended traffic logging", "help": "Disable extended traffic logging.", "label": "Disable", "name": "disable"}] | None = ...,
        local_in_allow: Literal[{"description": "Enable local-in-allow logging", "help": "Enable local-in-allow logging.", "label": "Enable", "name": "enable"}, {"description": "Disable local-in-allow logging", "help": "Disable local-in-allow logging.", "label": "Disable", "name": "disable"}] | None = ...,
        local_in_deny_unicast: Literal[{"description": "Enable local-in-deny-unicast logging", "help": "Enable local-in-deny-unicast logging.", "label": "Enable", "name": "enable"}, {"description": "Disable local-in-deny-unicast logging", "help": "Disable local-in-deny-unicast logging.", "label": "Disable", "name": "disable"}] | None = ...,
        local_in_deny_broadcast: Literal[{"description": "Enable local-in-deny-broadcast logging", "help": "Enable local-in-deny-broadcast logging.", "label": "Enable", "name": "enable"}, {"description": "Disable local-in-deny-broadcast logging", "help": "Disable local-in-deny-broadcast logging.", "label": "Disable", "name": "disable"}] | None = ...,
        local_in_policy_log: Literal[{"description": "Enable local-in-policy logging", "help": "Enable local-in-policy logging.", "label": "Enable", "name": "enable"}, {"description": "Disable local-in-policy logging", "help": "Disable local-in-policy logging.", "label": "Disable", "name": "disable"}] | None = ...,
        local_out: Literal[{"description": "Enable local-out logging", "help": "Enable local-out logging.", "label": "Enable", "name": "enable"}, {"description": "Disable local-out logging", "help": "Disable local-out logging.", "label": "Disable", "name": "disable"}] | None = ...,
        local_out_ioc_detection: Literal[{"description": "Enable local-out traffic IoC detection", "help": "Enable local-out traffic IoC detection. Requires local-out to be enabled.", "label": "Enable", "name": "enable"}, {"description": "Disable local-out traffic IoC detection", "help": "Disable local-out traffic IoC detection.", "label": "Disable", "name": "disable"}] | None = ...,
        daemon_log: Literal[{"description": "Enable daemon logging", "help": "Enable daemon logging.", "label": "Enable", "name": "enable"}, {"description": "Disable daemon logging", "help": "Disable daemon logging.", "label": "Disable", "name": "disable"}] | None = ...,
        neighbor_event: Literal[{"description": "Enable neighbor event logging", "help": "Enable neighbor event logging.", "label": "Enable", "name": "enable"}, {"description": "Disable neighbor event logging", "help": "Disable neighbor event logging.", "label": "Disable", "name": "disable"}] | None = ...,
        brief_traffic_format: Literal[{"description": "Enable brief format traffic logging", "help": "Enable brief format traffic logging.", "label": "Enable", "name": "enable"}, {"description": "Disable brief format traffic logging", "help": "Disable brief format traffic logging.", "label": "Disable", "name": "disable"}] | None = ...,
        user_anonymize: Literal[{"description": "Enable anonymizing user names in log messages", "help": "Enable anonymizing user names in log messages.", "label": "Enable", "name": "enable"}, {"description": "Disable anonymizing user names in log messages", "help": "Disable anonymizing user names in log messages.", "label": "Disable", "name": "disable"}] | None = ...,
        expolicy_implicit_log: Literal[{"description": "Enable proxy firewall implicit policy logging", "help": "Enable proxy firewall implicit policy logging.", "label": "Enable", "name": "enable"}, {"description": "Disable proxy firewall implicit policy logging", "help": "Disable proxy firewall implicit policy logging.", "label": "Disable", "name": "disable"}] | None = ...,
        log_policy_comment: Literal[{"description": "Enable inserting policy comments into traffic logs", "help": "Enable inserting policy comments into traffic logs.", "label": "Enable", "name": "enable"}, {"description": "Disable inserting policy comments into traffic logs", "help": "Disable inserting policy comments into traffic logs.", "label": "Disable", "name": "disable"}] | None = ...,
        faz_override: Literal[{"description": "Enable override FortiAnalyzer settings", "help": "Enable override FortiAnalyzer settings.", "label": "Enable", "name": "enable"}, {"description": "Disable override FortiAnalyzer settings", "help": "Disable override FortiAnalyzer settings.", "label": "Disable", "name": "disable"}] | None = ...,
        syslog_override: Literal[{"description": "Enable override Syslog settings", "help": "Enable override Syslog settings.", "label": "Enable", "name": "enable"}, {"description": "Disable override Syslog settings", "help": "Disable override Syslog settings.", "label": "Disable", "name": "disable"}] | None = ...,
        rest_api_set: Literal[{"description": "Enable POST/PUT/DELETE REST API logging", "help": "Enable POST/PUT/DELETE REST API logging.", "label": "Enable", "name": "enable"}, {"description": "Disable POST/PUT/DELETE REST API logging", "help": "Disable POST/PUT/DELETE REST API logging.", "label": "Disable", "name": "disable"}] | None = ...,
        rest_api_get: Literal[{"description": "Enable GET REST API logging", "help": "Enable GET REST API logging.", "label": "Enable", "name": "enable"}, {"description": "Disable GET REST API logging", "help": "Disable GET REST API logging.", "label": "Disable", "name": "disable"}] | None = ...,
        rest_api_performance: Literal[{"description": "Enable REST API performance stats in REST API logs", "help": "Enable REST API performance stats in REST API logs.", "label": "Enable", "name": "enable"}, {"description": "Disable REST API performance stats in REST API logs", "help": "Disable REST API performance stats in REST API logs.", "label": "Disable", "name": "disable"}] | None = ...,
        long_live_session_stat: Literal[{"description": "Enable long-live-session statistics logging", "help": "Enable long-live-session statistics logging.", "label": "Enable", "name": "enable"}, {"description": "Disable long-live-session statistics logging", "help": "Disable long-live-session statistics logging.", "label": "Disable", "name": "disable"}] | None = ...,
        extended_utm_log: Literal[{"description": "Enable extended UTM logging", "help": "Enable extended UTM logging.", "label": "Enable", "name": "enable"}, {"description": "Disable extended UTM logging", "help": "Disable extended UTM logging.", "label": "Disable", "name": "disable"}] | None = ...,
        zone_name: Literal[{"description": "Enable zone name logging", "help": "Enable zone name logging.", "label": "Enable", "name": "enable"}, {"description": "Disable zone name logging", "help": "Disable zone name logging.", "label": "Disable", "name": "disable"}] | None = ...,
        web_svc_perf: Literal[{"description": "Enable web-svc performance logging", "help": "Enable web-svc performance logging.", "label": "Enable", "name": "enable"}, {"description": "Disable web-svc performance logging", "help": "Disable web-svc performance logging.", "label": "Disable", "name": "disable"}] | None = ...,
        custom_log_fields: list[dict[str, Any]] | None = ...,
        anonymization_hash: str | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: SettingPayload | None = ...,
        resolve_ip: Literal[{"description": "Enable adding resolved domain names to traffic logs", "help": "Enable adding resolved domain names to traffic logs.", "label": "Enable", "name": "enable"}, {"description": "Disable adding resolved domain names to traffic logs", "help": "Disable adding resolved domain names to traffic logs.", "label": "Disable", "name": "disable"}] | None = ...,
        resolve_port: Literal[{"description": "Enable adding resolved service names to traffic logs", "help": "Enable adding resolved service names to traffic logs.", "label": "Enable", "name": "enable"}, {"description": "Disable adding resolved service names to traffic logs", "help": "Disable adding resolved service names to traffic logs.", "label": "Disable", "name": "disable"}] | None = ...,
        log_user_in_upper: Literal[{"description": "Enable logs with user-in-upper", "help": "Enable logs with user-in-upper.", "label": "Enable", "name": "enable"}, {"description": "Disable logs with user-in-upper", "help": "Disable logs with user-in-upper.", "label": "Disable", "name": "disable"}] | None = ...,
        fwpolicy_implicit_log: Literal[{"description": "Enable implicit firewall policy logging", "help": "Enable implicit firewall policy logging.", "label": "Enable", "name": "enable"}, {"description": "Disable implicit firewall policy logging", "help": "Disable implicit firewall policy logging.", "label": "Disable", "name": "disable"}] | None = ...,
        fwpolicy6_implicit_log: Literal[{"description": "Enable implicit firewall policy6 logging", "help": "Enable implicit firewall policy6 logging.", "label": "Enable", "name": "enable"}, {"description": "Disable implicit firewall policy6 logging", "help": "Disable implicit firewall policy6 logging.", "label": "Disable", "name": "disable"}] | None = ...,
        extended_log: Literal[{"description": "Enable extended traffic logging", "help": "Enable extended traffic logging.", "label": "Enable", "name": "enable"}, {"description": "Disable extended traffic logging", "help": "Disable extended traffic logging.", "label": "Disable", "name": "disable"}] | None = ...,
        local_in_allow: Literal[{"description": "Enable local-in-allow logging", "help": "Enable local-in-allow logging.", "label": "Enable", "name": "enable"}, {"description": "Disable local-in-allow logging", "help": "Disable local-in-allow logging.", "label": "Disable", "name": "disable"}] | None = ...,
        local_in_deny_unicast: Literal[{"description": "Enable local-in-deny-unicast logging", "help": "Enable local-in-deny-unicast logging.", "label": "Enable", "name": "enable"}, {"description": "Disable local-in-deny-unicast logging", "help": "Disable local-in-deny-unicast logging.", "label": "Disable", "name": "disable"}] | None = ...,
        local_in_deny_broadcast: Literal[{"description": "Enable local-in-deny-broadcast logging", "help": "Enable local-in-deny-broadcast logging.", "label": "Enable", "name": "enable"}, {"description": "Disable local-in-deny-broadcast logging", "help": "Disable local-in-deny-broadcast logging.", "label": "Disable", "name": "disable"}] | None = ...,
        local_in_policy_log: Literal[{"description": "Enable local-in-policy logging", "help": "Enable local-in-policy logging.", "label": "Enable", "name": "enable"}, {"description": "Disable local-in-policy logging", "help": "Disable local-in-policy logging.", "label": "Disable", "name": "disable"}] | None = ...,
        local_out: Literal[{"description": "Enable local-out logging", "help": "Enable local-out logging.", "label": "Enable", "name": "enable"}, {"description": "Disable local-out logging", "help": "Disable local-out logging.", "label": "Disable", "name": "disable"}] | None = ...,
        local_out_ioc_detection: Literal[{"description": "Enable local-out traffic IoC detection", "help": "Enable local-out traffic IoC detection. Requires local-out to be enabled.", "label": "Enable", "name": "enable"}, {"description": "Disable local-out traffic IoC detection", "help": "Disable local-out traffic IoC detection.", "label": "Disable", "name": "disable"}] | None = ...,
        daemon_log: Literal[{"description": "Enable daemon logging", "help": "Enable daemon logging.", "label": "Enable", "name": "enable"}, {"description": "Disable daemon logging", "help": "Disable daemon logging.", "label": "Disable", "name": "disable"}] | None = ...,
        neighbor_event: Literal[{"description": "Enable neighbor event logging", "help": "Enable neighbor event logging.", "label": "Enable", "name": "enable"}, {"description": "Disable neighbor event logging", "help": "Disable neighbor event logging.", "label": "Disable", "name": "disable"}] | None = ...,
        brief_traffic_format: Literal[{"description": "Enable brief format traffic logging", "help": "Enable brief format traffic logging.", "label": "Enable", "name": "enable"}, {"description": "Disable brief format traffic logging", "help": "Disable brief format traffic logging.", "label": "Disable", "name": "disable"}] | None = ...,
        user_anonymize: Literal[{"description": "Enable anonymizing user names in log messages", "help": "Enable anonymizing user names in log messages.", "label": "Enable", "name": "enable"}, {"description": "Disable anonymizing user names in log messages", "help": "Disable anonymizing user names in log messages.", "label": "Disable", "name": "disable"}] | None = ...,
        expolicy_implicit_log: Literal[{"description": "Enable proxy firewall implicit policy logging", "help": "Enable proxy firewall implicit policy logging.", "label": "Enable", "name": "enable"}, {"description": "Disable proxy firewall implicit policy logging", "help": "Disable proxy firewall implicit policy logging.", "label": "Disable", "name": "disable"}] | None = ...,
        log_policy_comment: Literal[{"description": "Enable inserting policy comments into traffic logs", "help": "Enable inserting policy comments into traffic logs.", "label": "Enable", "name": "enable"}, {"description": "Disable inserting policy comments into traffic logs", "help": "Disable inserting policy comments into traffic logs.", "label": "Disable", "name": "disable"}] | None = ...,
        faz_override: Literal[{"description": "Enable override FortiAnalyzer settings", "help": "Enable override FortiAnalyzer settings.", "label": "Enable", "name": "enable"}, {"description": "Disable override FortiAnalyzer settings", "help": "Disable override FortiAnalyzer settings.", "label": "Disable", "name": "disable"}] | None = ...,
        syslog_override: Literal[{"description": "Enable override Syslog settings", "help": "Enable override Syslog settings.", "label": "Enable", "name": "enable"}, {"description": "Disable override Syslog settings", "help": "Disable override Syslog settings.", "label": "Disable", "name": "disable"}] | None = ...,
        rest_api_set: Literal[{"description": "Enable POST/PUT/DELETE REST API logging", "help": "Enable POST/PUT/DELETE REST API logging.", "label": "Enable", "name": "enable"}, {"description": "Disable POST/PUT/DELETE REST API logging", "help": "Disable POST/PUT/DELETE REST API logging.", "label": "Disable", "name": "disable"}] | None = ...,
        rest_api_get: Literal[{"description": "Enable GET REST API logging", "help": "Enable GET REST API logging.", "label": "Enable", "name": "enable"}, {"description": "Disable GET REST API logging", "help": "Disable GET REST API logging.", "label": "Disable", "name": "disable"}] | None = ...,
        rest_api_performance: Literal[{"description": "Enable REST API performance stats in REST API logs", "help": "Enable REST API performance stats in REST API logs.", "label": "Enable", "name": "enable"}, {"description": "Disable REST API performance stats in REST API logs", "help": "Disable REST API performance stats in REST API logs.", "label": "Disable", "name": "disable"}] | None = ...,
        long_live_session_stat: Literal[{"description": "Enable long-live-session statistics logging", "help": "Enable long-live-session statistics logging.", "label": "Enable", "name": "enable"}, {"description": "Disable long-live-session statistics logging", "help": "Disable long-live-session statistics logging.", "label": "Disable", "name": "disable"}] | None = ...,
        extended_utm_log: Literal[{"description": "Enable extended UTM logging", "help": "Enable extended UTM logging.", "label": "Enable", "name": "enable"}, {"description": "Disable extended UTM logging", "help": "Disable extended UTM logging.", "label": "Disable", "name": "disable"}] | None = ...,
        zone_name: Literal[{"description": "Enable zone name logging", "help": "Enable zone name logging.", "label": "Enable", "name": "enable"}, {"description": "Disable zone name logging", "help": "Disable zone name logging.", "label": "Disable", "name": "disable"}] | None = ...,
        web_svc_perf: Literal[{"description": "Enable web-svc performance logging", "help": "Enable web-svc performance logging.", "label": "Enable", "name": "enable"}, {"description": "Disable web-svc performance logging", "help": "Disable web-svc performance logging.", "label": "Disable", "name": "disable"}] | None = ...,
        custom_log_fields: list[dict[str, Any]] | None = ...,
        anonymization_hash: str | None = ...,
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
        payload_dict: SettingPayload | None = ...,
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
    "Setting",
    "SettingPayload",
]