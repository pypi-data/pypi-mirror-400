from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_STATUS: Literal[{"description": "Enable sniffer status", "help": "Enable sniffer status.", "label": "Enable", "name": "enable"}, {"description": "Disable sniffer status", "help": "Disable sniffer status.", "label": "Disable", "name": "disable"}]
VALID_BODY_LOGTRAFFIC: Literal[{"description": "Log all sessions accepted or denied by this policy", "help": "Log all sessions accepted or denied by this policy.", "label": "All", "name": "all"}, {"description": "Log traffic that has a security profile applied to it", "help": "Log traffic that has a security profile applied to it.", "label": "Utm", "name": "utm"}, {"description": "Disable all logging for this policy", "help": "Disable all logging for this policy.", "label": "Disable", "name": "disable"}]
VALID_BODY_IPV6: Literal[{"description": "Enable sniffer for IPv6 packets", "help": "Enable sniffer for IPv6 packets.", "label": "Enable", "name": "enable"}, {"description": "Disable sniffer for IPv6 packets", "help": "Disable sniffer for IPv6 packets.", "label": "Disable", "name": "disable"}]
VALID_BODY_NON_IP: Literal[{"description": "Enable sniffer for non-IP packets", "help": "Enable sniffer for non-IP packets.", "label": "Enable", "name": "enable"}, {"description": "Disable sniffer for non-IP packets", "help": "Disable sniffer for non-IP packets.", "label": "Disable", "name": "disable"}]
VALID_BODY_APPLICATION_LIST_STATUS: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]
VALID_BODY_IPS_SENSOR_STATUS: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]
VALID_BODY_DSRI: Literal[{"description": "Enable DSRI", "help": "Enable DSRI.", "label": "Enable", "name": "enable"}, {"description": "Disable DSRI", "help": "Disable DSRI.", "label": "Disable", "name": "disable"}]
VALID_BODY_AV_PROFILE_STATUS: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]
VALID_BODY_WEBFILTER_PROFILE_STATUS: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]
VALID_BODY_EMAILFILTER_PROFILE_STATUS: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]
VALID_BODY_DLP_PROFILE_STATUS: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]
VALID_BODY_IP_THREATFEED_STATUS: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]
VALID_BODY_FILE_FILTER_PROFILE_STATUS: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]
VALID_BODY_IPS_DOS_STATUS: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]

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
    "VALID_BODY_STATUS",
    "VALID_BODY_LOGTRAFFIC",
    "VALID_BODY_IPV6",
    "VALID_BODY_NON_IP",
    "VALID_BODY_APPLICATION_LIST_STATUS",
    "VALID_BODY_IPS_SENSOR_STATUS",
    "VALID_BODY_DSRI",
    "VALID_BODY_AV_PROFILE_STATUS",
    "VALID_BODY_WEBFILTER_PROFILE_STATUS",
    "VALID_BODY_EMAILFILTER_PROFILE_STATUS",
    "VALID_BODY_DLP_PROFILE_STATUS",
    "VALID_BODY_IP_THREATFEED_STATUS",
    "VALID_BODY_FILE_FILTER_PROFILE_STATUS",
    "VALID_BODY_IPS_DOS_STATUS",
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