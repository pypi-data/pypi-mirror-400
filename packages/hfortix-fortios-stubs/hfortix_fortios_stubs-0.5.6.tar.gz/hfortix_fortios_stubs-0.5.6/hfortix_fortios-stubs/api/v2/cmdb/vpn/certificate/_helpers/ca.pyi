from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_RANGE: Literal[{"description": "Global range", "help": "Global range.", "label": "Global", "name": "global"}, {"description": "VDOM IP address range", "help": "VDOM IP address range.", "label": "Vdom", "name": "vdom"}]
VALID_BODY_SOURCE: Literal[{"description": "Factory installed certificate", "help": "Factory installed certificate.", "label": "Factory", "name": "factory"}, {"description": "User generated certificate", "help": "User generated certificate.", "label": "User", "name": "user"}, {"description": "Bundle file certificate", "help": "Bundle file certificate.", "label": "Bundle", "name": "bundle"}]
VALID_BODY_SSL_INSPECTION_TRUSTED: Literal[{"description": "Trusted CA for SSL inspection", "help": "Trusted CA for SSL inspection.", "label": "Enable", "name": "enable"}, {"description": "Untrusted CA for SSL inspection", "help": "Untrusted CA for SSL inspection.", "label": "Disable", "name": "disable"}]
VALID_BODY_OBSOLETE: Literal[{"description": "Alive", "help": "Alive.", "label": "Disable", "name": "disable"}, {"description": "Obsolete", "help": "Obsolete.", "label": "Enable", "name": "enable"}]
VALID_BODY_FABRIC_CA: Literal[{"description": "Disable synchronization of CA across Security Fabric", "help": "Disable synchronization of CA across Security Fabric.", "label": "Disable", "name": "disable"}, {"description": "Enable synchronization of CA across Security Fabric", "help": "Enable synchronization of CA across Security Fabric.", "label": "Enable", "name": "enable"}]

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
    "VALID_BODY_RANGE",
    "VALID_BODY_SOURCE",
    "VALID_BODY_SSL_INSPECTION_TRUSTED",
    "VALID_BODY_OBSOLETE",
    "VALID_BODY_FABRIC_CA",
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