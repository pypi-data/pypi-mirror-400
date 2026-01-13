from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_RESOLVE_IP: Literal[{"description": "Enable adding resolved domain names to traffic logs", "help": "Enable adding resolved domain names to traffic logs.", "label": "Enable", "name": "enable"}, {"description": "Disable adding resolved domain names to traffic logs", "help": "Disable adding resolved domain names to traffic logs.", "label": "Disable", "name": "disable"}]
VALID_BODY_RESOLVE_PORT: Literal[{"description": "Enable adding resolved service names to traffic logs", "help": "Enable adding resolved service names to traffic logs.", "label": "Enable", "name": "enable"}, {"description": "Disable adding resolved service names to traffic logs", "help": "Disable adding resolved service names to traffic logs.", "label": "Disable", "name": "disable"}]
VALID_BODY_LOG_USER_IN_UPPER: Literal[{"description": "Enable logs with user-in-upper", "help": "Enable logs with user-in-upper.", "label": "Enable", "name": "enable"}, {"description": "Disable logs with user-in-upper", "help": "Disable logs with user-in-upper.", "label": "Disable", "name": "disable"}]
VALID_BODY_FWPOLICY_IMPLICIT_LOG: Literal[{"description": "Enable implicit firewall policy logging", "help": "Enable implicit firewall policy logging.", "label": "Enable", "name": "enable"}, {"description": "Disable implicit firewall policy logging", "help": "Disable implicit firewall policy logging.", "label": "Disable", "name": "disable"}]
VALID_BODY_FWPOLICY6_IMPLICIT_LOG: Literal[{"description": "Enable implicit firewall policy6 logging", "help": "Enable implicit firewall policy6 logging.", "label": "Enable", "name": "enable"}, {"description": "Disable implicit firewall policy6 logging", "help": "Disable implicit firewall policy6 logging.", "label": "Disable", "name": "disable"}]
VALID_BODY_EXTENDED_LOG: Literal[{"description": "Enable extended traffic logging", "help": "Enable extended traffic logging.", "label": "Enable", "name": "enable"}, {"description": "Disable extended traffic logging", "help": "Disable extended traffic logging.", "label": "Disable", "name": "disable"}]
VALID_BODY_LOCAL_IN_ALLOW: Literal[{"description": "Enable local-in-allow logging", "help": "Enable local-in-allow logging.", "label": "Enable", "name": "enable"}, {"description": "Disable local-in-allow logging", "help": "Disable local-in-allow logging.", "label": "Disable", "name": "disable"}]
VALID_BODY_LOCAL_IN_DENY_UNICAST: Literal[{"description": "Enable local-in-deny-unicast logging", "help": "Enable local-in-deny-unicast logging.", "label": "Enable", "name": "enable"}, {"description": "Disable local-in-deny-unicast logging", "help": "Disable local-in-deny-unicast logging.", "label": "Disable", "name": "disable"}]
VALID_BODY_LOCAL_IN_DENY_BROADCAST: Literal[{"description": "Enable local-in-deny-broadcast logging", "help": "Enable local-in-deny-broadcast logging.", "label": "Enable", "name": "enable"}, {"description": "Disable local-in-deny-broadcast logging", "help": "Disable local-in-deny-broadcast logging.", "label": "Disable", "name": "disable"}]
VALID_BODY_LOCAL_IN_POLICY_LOG: Literal[{"description": "Enable local-in-policy logging", "help": "Enable local-in-policy logging.", "label": "Enable", "name": "enable"}, {"description": "Disable local-in-policy logging", "help": "Disable local-in-policy logging.", "label": "Disable", "name": "disable"}]
VALID_BODY_LOCAL_OUT: Literal[{"description": "Enable local-out logging", "help": "Enable local-out logging.", "label": "Enable", "name": "enable"}, {"description": "Disable local-out logging", "help": "Disable local-out logging.", "label": "Disable", "name": "disable"}]
VALID_BODY_LOCAL_OUT_IOC_DETECTION: Literal[{"description": "Enable local-out traffic IoC detection", "help": "Enable local-out traffic IoC detection. Requires local-out to be enabled.", "label": "Enable", "name": "enable"}, {"description": "Disable local-out traffic IoC detection", "help": "Disable local-out traffic IoC detection.", "label": "Disable", "name": "disable"}]
VALID_BODY_DAEMON_LOG: Literal[{"description": "Enable daemon logging", "help": "Enable daemon logging.", "label": "Enable", "name": "enable"}, {"description": "Disable daemon logging", "help": "Disable daemon logging.", "label": "Disable", "name": "disable"}]
VALID_BODY_NEIGHBOR_EVENT: Literal[{"description": "Enable neighbor event logging", "help": "Enable neighbor event logging.", "label": "Enable", "name": "enable"}, {"description": "Disable neighbor event logging", "help": "Disable neighbor event logging.", "label": "Disable", "name": "disable"}]
VALID_BODY_BRIEF_TRAFFIC_FORMAT: Literal[{"description": "Enable brief format traffic logging", "help": "Enable brief format traffic logging.", "label": "Enable", "name": "enable"}, {"description": "Disable brief format traffic logging", "help": "Disable brief format traffic logging.", "label": "Disable", "name": "disable"}]
VALID_BODY_USER_ANONYMIZE: Literal[{"description": "Enable anonymizing user names in log messages", "help": "Enable anonymizing user names in log messages.", "label": "Enable", "name": "enable"}, {"description": "Disable anonymizing user names in log messages", "help": "Disable anonymizing user names in log messages.", "label": "Disable", "name": "disable"}]
VALID_BODY_EXPOLICY_IMPLICIT_LOG: Literal[{"description": "Enable proxy firewall implicit policy logging", "help": "Enable proxy firewall implicit policy logging.", "label": "Enable", "name": "enable"}, {"description": "Disable proxy firewall implicit policy logging", "help": "Disable proxy firewall implicit policy logging.", "label": "Disable", "name": "disable"}]
VALID_BODY_LOG_POLICY_COMMENT: Literal[{"description": "Enable inserting policy comments into traffic logs", "help": "Enable inserting policy comments into traffic logs.", "label": "Enable", "name": "enable"}, {"description": "Disable inserting policy comments into traffic logs", "help": "Disable inserting policy comments into traffic logs.", "label": "Disable", "name": "disable"}]
VALID_BODY_FAZ_OVERRIDE: Literal[{"description": "Enable override FortiAnalyzer settings", "help": "Enable override FortiAnalyzer settings.", "label": "Enable", "name": "enable"}, {"description": "Disable override FortiAnalyzer settings", "help": "Disable override FortiAnalyzer settings.", "label": "Disable", "name": "disable"}]
VALID_BODY_SYSLOG_OVERRIDE: Literal[{"description": "Enable override Syslog settings", "help": "Enable override Syslog settings.", "label": "Enable", "name": "enable"}, {"description": "Disable override Syslog settings", "help": "Disable override Syslog settings.", "label": "Disable", "name": "disable"}]
VALID_BODY_REST_API_SET: Literal[{"description": "Enable POST/PUT/DELETE REST API logging", "help": "Enable POST/PUT/DELETE REST API logging.", "label": "Enable", "name": "enable"}, {"description": "Disable POST/PUT/DELETE REST API logging", "help": "Disable POST/PUT/DELETE REST API logging.", "label": "Disable", "name": "disable"}]
VALID_BODY_REST_API_GET: Literal[{"description": "Enable GET REST API logging", "help": "Enable GET REST API logging.", "label": "Enable", "name": "enable"}, {"description": "Disable GET REST API logging", "help": "Disable GET REST API logging.", "label": "Disable", "name": "disable"}]
VALID_BODY_REST_API_PERFORMANCE: Literal[{"description": "Enable REST API performance stats in REST API logs", "help": "Enable REST API performance stats in REST API logs.", "label": "Enable", "name": "enable"}, {"description": "Disable REST API performance stats in REST API logs", "help": "Disable REST API performance stats in REST API logs.", "label": "Disable", "name": "disable"}]
VALID_BODY_LONG_LIVE_SESSION_STAT: Literal[{"description": "Enable long-live-session statistics logging", "help": "Enable long-live-session statistics logging.", "label": "Enable", "name": "enable"}, {"description": "Disable long-live-session statistics logging", "help": "Disable long-live-session statistics logging.", "label": "Disable", "name": "disable"}]
VALID_BODY_EXTENDED_UTM_LOG: Literal[{"description": "Enable extended UTM logging", "help": "Enable extended UTM logging.", "label": "Enable", "name": "enable"}, {"description": "Disable extended UTM logging", "help": "Disable extended UTM logging.", "label": "Disable", "name": "disable"}]
VALID_BODY_ZONE_NAME: Literal[{"description": "Enable zone name logging", "help": "Enable zone name logging.", "label": "Enable", "name": "enable"}, {"description": "Disable zone name logging", "help": "Disable zone name logging.", "label": "Disable", "name": "disable"}]
VALID_BODY_WEB_SVC_PERF: Literal[{"description": "Enable web-svc performance logging", "help": "Enable web-svc performance logging.", "label": "Enable", "name": "enable"}, {"description": "Disable web-svc performance logging", "help": "Disable web-svc performance logging.", "label": "Disable", "name": "disable"}]

# Metadata dictionaries
FIELD_TYPES: dict[str, str]
FIELD_DESCRIPTIONS: dict[str, str]
FIELD_CONSTRAINTS: dict[str, dict[str, Any]]
NESTED_SCHEMAS: dict[str, dict[str, Any]]
FIELDS_WITH_DEFAULTS: dict[str, Any]

# Helper functions
def get_field_type(field_name: str) -> str | None: ...
def get_field_description(field_name: str) -> str | None: ...
def get_field_default(field_name: str) -> Any: ...
def get_field_constraints(field_name: str) -> dict[str, Any]: ...
def get_nested_schema(field_name: str) -> dict[str, Any] | None: ...
def get_field_metadata(field_name: str) -> dict[str, Any]: ...
def validate_field_value(field_name: str, value: Any) -> bool: ...
def get_all_fields() -> list[str]: ...
def get_required_fields() -> list[str]: ...
def get_schema_info() -> dict[str, Any]: ...


__all__ = [
    "VALID_BODY_RESOLVE_IP",
    "VALID_BODY_RESOLVE_PORT",
    "VALID_BODY_LOG_USER_IN_UPPER",
    "VALID_BODY_FWPOLICY_IMPLICIT_LOG",
    "VALID_BODY_FWPOLICY6_IMPLICIT_LOG",
    "VALID_BODY_EXTENDED_LOG",
    "VALID_BODY_LOCAL_IN_ALLOW",
    "VALID_BODY_LOCAL_IN_DENY_UNICAST",
    "VALID_BODY_LOCAL_IN_DENY_BROADCAST",
    "VALID_BODY_LOCAL_IN_POLICY_LOG",
    "VALID_BODY_LOCAL_OUT",
    "VALID_BODY_LOCAL_OUT_IOC_DETECTION",
    "VALID_BODY_DAEMON_LOG",
    "VALID_BODY_NEIGHBOR_EVENT",
    "VALID_BODY_BRIEF_TRAFFIC_FORMAT",
    "VALID_BODY_USER_ANONYMIZE",
    "VALID_BODY_EXPOLICY_IMPLICIT_LOG",
    "VALID_BODY_LOG_POLICY_COMMENT",
    "VALID_BODY_FAZ_OVERRIDE",
    "VALID_BODY_SYSLOG_OVERRIDE",
    "VALID_BODY_REST_API_SET",
    "VALID_BODY_REST_API_GET",
    "VALID_BODY_REST_API_PERFORMANCE",
    "VALID_BODY_LONG_LIVE_SESSION_STAT",
    "VALID_BODY_EXTENDED_UTM_LOG",
    "VALID_BODY_ZONE_NAME",
    "VALID_BODY_WEB_SVC_PERF",
    "FIELD_TYPES",
    "FIELD_DESCRIPTIONS",
    "FIELD_CONSTRAINTS",
    "NESTED_SCHEMAS",
    "FIELDS_WITH_DEFAULTS",
    "get_field_type",
    "get_field_description",
    "get_field_default",
    "get_field_constraints",
    "get_nested_schema",
    "get_field_metadata",
    "validate_field_value",
    "get_all_fields",
    "get_required_fields",
    "get_schema_info",
]