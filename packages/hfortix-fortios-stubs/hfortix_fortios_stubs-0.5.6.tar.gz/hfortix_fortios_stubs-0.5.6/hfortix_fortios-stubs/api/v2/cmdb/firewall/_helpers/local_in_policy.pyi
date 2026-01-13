from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_HA_MGMT_INTF_ONLY: Literal[{"description": "Enable dedicating HA management interface only for local-in policy", "help": "Enable dedicating HA management interface only for local-in policy.", "label": "Enable", "name": "enable"}, {"description": "Disable dedicating HA management interface only for local-in policy", "help": "Disable dedicating HA management interface only for local-in policy.", "label": "Disable", "name": "disable"}]
VALID_BODY_SRCADDR_NEGATE: Literal[{"description": "Enable source address negate", "help": "Enable source address negate.", "label": "Enable", "name": "enable"}, {"description": "Disable source address negate", "help": "Disable source address negate.", "label": "Disable", "name": "disable"}]
VALID_BODY_INTERNET_SERVICE_SRC: Literal[{"description": "Enable use of Internet Services source in local-in policy", "help": "Enable use of Internet Services source in local-in policy.", "label": "Enable", "name": "enable"}, {"description": "Disable use of Internet Services source in local-in policy", "help": "Disable use of Internet Services source in local-in policy.", "label": "Disable", "name": "disable"}]
VALID_BODY_DSTADDR_NEGATE: Literal[{"description": "Enable destination address negate", "help": "Enable destination address negate.", "label": "Enable", "name": "enable"}, {"description": "Disable destination address negate", "help": "Disable destination address negate.", "label": "Disable", "name": "disable"}]
VALID_BODY_ACTION: Literal[{"description": "Allow traffic matching this policy", "help": "Allow traffic matching this policy.", "label": "Accept", "name": "accept"}, {"description": "Deny or block traffic matching this policy", "help": "Deny or block traffic matching this policy.", "label": "Deny", "name": "deny"}]
VALID_BODY_SERVICE_NEGATE: Literal[{"description": "Enable negated service match", "help": "Enable negated service match.", "label": "Enable", "name": "enable"}, {"description": "Disable negated service match", "help": "Disable negated service match.", "label": "Disable", "name": "disable"}]
VALID_BODY_INTERNET_SERVICE_SRC_NEGATE: Literal[{"description": "Enable negated Internet Service source match", "help": "Enable negated Internet Service source match.", "label": "Enable", "name": "enable"}, {"description": "Disable negated Internet Service source match", "help": "Disable negated Internet Service source match.", "label": "Disable", "name": "disable"}]
VALID_BODY_STATUS: Literal[{"description": "Enable this local-in policy", "help": "Enable this local-in policy.", "label": "Enable", "name": "enable"}, {"description": "Disable this local-in policy", "help": "Disable this local-in policy.", "label": "Disable", "name": "disable"}]
VALID_BODY_VIRTUAL_PATCH: Literal[{"description": "Enable virtual patching", "help": "Enable virtual patching.", "label": "Enable", "name": "enable"}, {"description": "Disable virtual patching", "help": "Disable virtual patching.", "label": "Disable", "name": "disable"}]
VALID_BODY_LOGTRAFFIC: Literal[{"description": "Enable local-in traffic logging", "help": "Enable local-in traffic logging.", "label": "Enable", "name": "enable"}, {"description": "Disable local-in traffic logging", "help": "Disable local-in traffic logging.", "label": "Disable", "name": "disable"}]

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
    "VALID_BODY_HA_MGMT_INTF_ONLY",
    "VALID_BODY_SRCADDR_NEGATE",
    "VALID_BODY_INTERNET_SERVICE_SRC",
    "VALID_BODY_DSTADDR_NEGATE",
    "VALID_BODY_ACTION",
    "VALID_BODY_SERVICE_NEGATE",
    "VALID_BODY_INTERNET_SERVICE_SRC_NEGATE",
    "VALID_BODY_STATUS",
    "VALID_BODY_VIRTUAL_PATCH",
    "VALID_BODY_LOGTRAFFIC",
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