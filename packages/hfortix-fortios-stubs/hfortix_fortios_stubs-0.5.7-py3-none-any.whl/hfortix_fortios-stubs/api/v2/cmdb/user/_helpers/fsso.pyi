from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_TYPE: Literal[{"description": "All other unspecified types of servers", "help": "All other unspecified types of servers.", "label": "Default", "name": "default"}, {"description": "FortiNAC server", "help": "FortiNAC server.", "label": "Fortinac", "name": "fortinac"}]
VALID_BODY_LDAP_POLL: Literal[{"description": "Enable automatic fetching of groups from LDAP server", "help": "Enable automatic fetching of groups from LDAP server.", "label": "Enable", "name": "enable"}, {"description": "Disable automatic fetching of groups from LDAP server", "help": "Disable automatic fetching of groups from LDAP server.", "label": "Disable", "name": "disable"}]
VALID_BODY_SSL: Literal[{"description": "Enable use of SSL", "help": "Enable use of SSL.", "label": "Enable", "name": "enable"}, {"description": "Disable use of SSL", "help": "Disable use of SSL.", "label": "Disable", "name": "disable"}]
VALID_BODY_SSL_SERVER_HOST_IP_CHECK: Literal[{"description": "Enable server host/IP verification", "help": "Enable server host/IP verification.", "label": "Enable", "name": "enable"}, {"description": "Disable server host/IP verification", "help": "Disable server host/IP verification.", "label": "Disable", "name": "disable"}]
VALID_BODY_INTERFACE_SELECT_METHOD: Literal[{"description": "Set outgoing interface automatically", "help": "Set outgoing interface automatically.", "label": "Auto", "name": "auto"}, {"description": "Set outgoing interface by SD-WAN or policy routing rules", "help": "Set outgoing interface by SD-WAN or policy routing rules.", "label": "Sdwan", "name": "sdwan"}, {"description": "Set outgoing interface manually", "help": "Set outgoing interface manually.", "label": "Specify", "name": "specify"}]

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
    "VALID_BODY_TYPE",
    "VALID_BODY_LDAP_POLL",
    "VALID_BODY_SSL",
    "VALID_BODY_SSL_SERVER_HOST_IP_CHECK",
    "VALID_BODY_INTERFACE_SELECT_METHOD",
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