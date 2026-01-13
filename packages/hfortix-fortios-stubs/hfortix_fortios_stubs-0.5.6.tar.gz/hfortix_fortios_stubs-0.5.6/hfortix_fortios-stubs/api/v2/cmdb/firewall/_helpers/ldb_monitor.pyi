from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_TYPE: Literal[{"description": "PING health monitor", "help": "PING health monitor.", "label": "Ping", "name": "ping"}, {"description": "TCP-connect health monitor", "help": "TCP-connect health monitor.", "label": "Tcp", "name": "tcp"}, {"description": "HTTP-GET health monitor", "help": "HTTP-GET health monitor.", "label": "Http", "name": "http"}, {"description": "HTTP-GET health monitor with SSL", "help": "HTTP-GET health monitor with SSL.", "label": "Https", "name": "https"}, {"description": "DNS health monitor", "help": "DNS health monitor.", "label": "Dns", "name": "dns"}]
VALID_BODY_DNS_PROTOCOL: Literal[{"description": "UDP", "help": "UDP.", "label": "Udp", "name": "udp"}, {"description": "TCP", "help": "TCP.", "label": "Tcp", "name": "tcp"}]

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
    "VALID_BODY_DNS_PROTOCOL",
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