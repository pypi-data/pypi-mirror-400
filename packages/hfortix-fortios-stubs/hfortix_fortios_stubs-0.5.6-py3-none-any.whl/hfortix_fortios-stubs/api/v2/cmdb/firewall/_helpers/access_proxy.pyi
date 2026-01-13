from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_AUTH_PORTAL: Literal[{"description": "Disable authentication portal", "help": "Disable authentication portal.", "label": "Disable", "name": "disable"}, {"description": "Enable authentication portal", "help": "Enable authentication portal.", "label": "Enable", "name": "enable"}]
VALID_BODY_LOG_BLOCKED_TRAFFIC: Literal[{"description": "Log all traffic denied by this access proxy", "help": "Log all traffic denied by this access proxy.", "label": "Enable", "name": "enable"}, {"description": "Do not log all traffic denied by this access proxy", "help": "Do not log all traffic denied by this access proxy.", "label": "Disable", "name": "disable"}]
VALID_BODY_ADD_VHOST_DOMAIN_TO_DNSDB: Literal[{"description": "add dns entry for all vhosts used by access proxy", "help": "add dns entry for all vhosts used by access proxy.", "label": "Enable", "name": "enable"}, {"description": "Do not add dns entry for all vhosts used by access proxy", "help": "Do not add dns entry for all vhosts used by access proxy.", "label": "Disable", "name": "disable"}]
VALID_BODY_SVR_POOL_MULTIPLEX: Literal[{"description": "Enable server pool multiplexing", "help": "Enable server pool multiplexing.  Share connected server.", "label": "Enable", "name": "enable"}, {"description": "Disable server pool multiplexing", "help": "Disable server pool multiplexing.  Do not share connected server.", "label": "Disable", "name": "disable"}]

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
    "VALID_BODY_AUTH_PORTAL",
    "VALID_BODY_LOG_BLOCKED_TRAFFIC",
    "VALID_BODY_ADD_VHOST_DOMAIN_TO_DNSDB",
    "VALID_BODY_SVR_POOL_MULTIPLEX",
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