from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_SRCADDR_NEGATE: Literal[{"description": "Enable source address negate", "help": "Enable source address negate.", "label": "Enable", "name": "enable"}, {"description": "Disable source address negate", "help": "Disable source address negate.", "label": "Disable", "name": "disable"}]
VALID_BODY_DSTADDR_NEGATE: Literal[{"description": "Enable destination address negate", "help": "Enable destination address negate.", "label": "Enable", "name": "enable"}, {"description": "Disable destination address negate", "help": "Disable destination address negate.", "label": "Disable", "name": "disable"}]
VALID_BODY_SRCADDR6_NEGATE: Literal[{"description": "Enable IPv6 source address negate", "help": "Enable IPv6 source address negate.", "label": "Enable", "name": "enable"}, {"description": "Disable IPv6 source address negate", "help": "Disable IPv6 source address negate.", "label": "Disable", "name": "disable"}]
VALID_BODY_DSTADDR6_NEGATE: Literal[{"description": "Enable IPv6 destination address negate", "help": "Enable IPv6 destination address negate.", "label": "Enable", "name": "enable"}, {"description": "Disable IPv6 destination address negate", "help": "Disable IPv6 destination address negate.", "label": "Disable", "name": "disable"}]
VALID_BODY_INTERNET_SERVICE: Literal[{"description": "Enable use of Internet Services in policy", "help": "Enable use of Internet Services in policy.", "label": "Enable", "name": "enable"}, {"description": "Disable use of Internet Services in policy", "help": "Disable use of Internet Services in policy.", "label": "Disable", "name": "disable"}]
VALID_BODY_INTERNET_SERVICE_NEGATE: Literal[{"description": "Enable negated Internet Service match", "help": "Enable negated Internet Service match.", "label": "Enable", "name": "enable"}, {"description": "Disable negated Internet Service match", "help": "Disable negated Internet Service match.", "label": "Disable", "name": "disable"}]
VALID_BODY_INTERNET_SERVICE_SRC: Literal[{"description": "Enable use of Internet Services source in policy", "help": "Enable use of Internet Services source in policy.", "label": "Enable", "name": "enable"}, {"description": "Disable use of Internet Services source in policy", "help": "Disable use of Internet Services source in policy.", "label": "Disable", "name": "disable"}]
VALID_BODY_INTERNET_SERVICE_SRC_NEGATE: Literal[{"description": "Enable negated Internet Service source match", "help": "Enable negated Internet Service source match.", "label": "Enable", "name": "enable"}, {"description": "Disable negated Internet Service source match", "help": "Disable negated Internet Service source match.", "label": "Disable", "name": "disable"}]
VALID_BODY_INTERNET_SERVICE6: Literal[{"description": "Enable use of IPv6 Internet Services in policy", "help": "Enable use of IPv6 Internet Services in policy.", "label": "Enable", "name": "enable"}, {"description": "Disable use of IPv6 Internet Services in policy", "help": "Disable use of IPv6 Internet Services in policy.", "label": "Disable", "name": "disable"}]
VALID_BODY_INTERNET_SERVICE6_NEGATE: Literal[{"description": "Enable negated IPv6 Internet Service match", "help": "Enable negated IPv6 Internet Service match.", "label": "Enable", "name": "enable"}, {"description": "Disable negated IPv6 Internet Service match", "help": "Disable negated IPv6 Internet Service match.", "label": "Disable", "name": "disable"}]
VALID_BODY_INTERNET_SERVICE6_SRC: Literal[{"description": "Enable use of IPv6 Internet Services source in policy", "help": "Enable use of IPv6 Internet Services source in policy.", "label": "Enable", "name": "enable"}, {"description": "Disable use of IPv6 Internet Services source in policy", "help": "Disable use of IPv6 Internet Services source in policy.", "label": "Disable", "name": "disable"}]
VALID_BODY_INTERNET_SERVICE6_SRC_NEGATE: Literal[{"description": "Enable negated IPv6 Internet Service source match", "help": "Enable negated IPv6 Internet Service source match.", "label": "Enable", "name": "enable"}, {"description": "Disable negated IPv6 Internet Service source match", "help": "Disable negated IPv6 Internet Service source match.", "label": "Disable", "name": "disable"}]
VALID_BODY_ENFORCE_DEFAULT_APP_PORT: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]
VALID_BODY_SERVICE_NEGATE: Literal[{"description": "Enable negated service match", "help": "Enable negated service match.", "label": "Enable", "name": "enable"}, {"description": "Disable negated service match", "help": "Disable negated service match.", "label": "Disable", "name": "disable"}]
VALID_BODY_ACTION: Literal[{"description": "Allows session that match the firewall policy", "help": "Allows session that match the firewall policy.", "label": "Accept", "name": "accept"}, {"description": "Blocks sessions that match the firewall policy", "help": "Blocks sessions that match the firewall policy.", "label": "Deny", "name": "deny"}]
VALID_BODY_SEND_DENY_PACKET: Literal[{"description": "Disable deny-packet sending", "help": "Disable deny-packet sending.", "label": "Disable", "name": "disable"}, {"description": "Enable deny-packet sending", "help": "Enable deny-packet sending.", "label": "Enable", "name": "enable"}]
VALID_BODY_STATUS: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]
VALID_BODY_LOGTRAFFIC: Literal[{"description": "Log all sessions accepted or denied by this policy", "help": "Log all sessions accepted or denied by this policy.", "label": "All", "name": "all"}, {"description": "Log traffic that has a security profile applied to it", "help": "Log traffic that has a security profile applied to it.", "label": "Utm", "name": "utm"}, {"description": "Disable all logging for this policy", "help": "Disable all logging for this policy.", "label": "Disable", "name": "disable"}]
VALID_BODY_LEARNING_MODE: Literal[{"description": "Enable learning mode", "help": "Enable learning mode.", "label": "Enable", "name": "enable"}, {"description": "Disable learning mode", "help": "Disable learning mode.", "label": "Disable", "name": "disable"}]
VALID_BODY_NAT46: Literal[{"description": "Enable NAT46", "help": "Enable NAT46.", "label": "Enable", "name": "enable"}, {"description": "Disable NAT46", "help": "Disable NAT46.", "label": "Disable", "name": "disable"}]
VALID_BODY_NAT64: Literal[{"description": "Enable NAT64", "help": "Enable NAT64.", "label": "Enable", "name": "enable"}, {"description": "Disable NAT64", "help": "Disable NAT64.", "label": "Disable", "name": "disable"}]
VALID_BODY_PROFILE_TYPE: Literal[{"description": "Do not allow security profile groups", "help": "Do not allow security profile groups.", "label": "Single", "name": "single"}, {"description": "Allow security profile groups", "help": "Allow security profile groups.", "label": "Group", "name": "group"}]

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
    "VALID_BODY_SRCADDR_NEGATE",
    "VALID_BODY_DSTADDR_NEGATE",
    "VALID_BODY_SRCADDR6_NEGATE",
    "VALID_BODY_DSTADDR6_NEGATE",
    "VALID_BODY_INTERNET_SERVICE",
    "VALID_BODY_INTERNET_SERVICE_NEGATE",
    "VALID_BODY_INTERNET_SERVICE_SRC",
    "VALID_BODY_INTERNET_SERVICE_SRC_NEGATE",
    "VALID_BODY_INTERNET_SERVICE6",
    "VALID_BODY_INTERNET_SERVICE6_NEGATE",
    "VALID_BODY_INTERNET_SERVICE6_SRC",
    "VALID_BODY_INTERNET_SERVICE6_SRC_NEGATE",
    "VALID_BODY_ENFORCE_DEFAULT_APP_PORT",
    "VALID_BODY_SERVICE_NEGATE",
    "VALID_BODY_ACTION",
    "VALID_BODY_SEND_DENY_PACKET",
    "VALID_BODY_STATUS",
    "VALID_BODY_LOGTRAFFIC",
    "VALID_BODY_LEARNING_MODE",
    "VALID_BODY_NAT46",
    "VALID_BODY_NAT64",
    "VALID_BODY_PROFILE_TYPE",
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