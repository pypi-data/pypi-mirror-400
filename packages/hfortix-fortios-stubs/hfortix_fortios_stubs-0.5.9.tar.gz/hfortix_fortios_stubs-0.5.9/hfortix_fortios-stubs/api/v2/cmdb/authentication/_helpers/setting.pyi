from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_PERSISTENT_COOKIE: Literal[{"description": "Enable persistent cookie", "help": "Enable persistent cookie.", "label": "Enable", "name": "enable"}, {"description": "Disable persistent cookie", "help": "Disable persistent cookie.", "label": "Disable", "name": "disable"}]
VALID_BODY_IP_AUTH_COOKIE: Literal[{"description": "Enable persistent cookie for IP-based authentication", "help": "Enable persistent cookie for IP-based authentication.", "label": "Enable", "name": "enable"}, {"description": "Disable persistent cookie for IP-based authentication", "help": "Disable persistent cookie for IP-based authentication.", "label": "Disable", "name": "disable"}]
VALID_BODY_CAPTIVE_PORTAL_TYPE: Literal[{"description": "Use FQDN for captive portal", "help": "Use FQDN for captive portal.", "label": "Fqdn", "name": "fqdn"}, {"description": "Use an IP address for captive portal", "help": "Use an IP address for captive portal.", "label": "Ip", "name": "ip"}]
VALID_BODY_CERT_AUTH: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]
VALID_BODY_AUTH_HTTPS: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]

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
    "VALID_BODY_PERSISTENT_COOKIE",
    "VALID_BODY_IP_AUTH_COOKIE",
    "VALID_BODY_CAPTIVE_PORTAL_TYPE",
    "VALID_BODY_CERT_AUTH",
    "VALID_BODY_AUTH_HTTPS",
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