from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_TYPE: Literal[{"description": "IPv6 addresses in the IP pool can be shared by clients", "help": "IPv6 addresses in the IP pool can be shared by clients.", "label": "Overload", "name": "overload"}, {"description": "NPTv6 one to one mapping", "help": "NPTv6 one to one mapping.", "label": "Nptv6", "name": "nptv6"}]
VALID_BODY_NAT46: Literal[{"description": "Disable NAT46", "help": "Disable NAT46.", "label": "Disable", "name": "disable"}, {"description": "Enable NAT46", "help": "Enable NAT46.", "label": "Enable", "name": "enable"}]
VALID_BODY_ADD_NAT46_ROUTE: Literal[{"description": "Disable adding NAT46 route", "help": "Disable adding NAT46 route.", "label": "Disable", "name": "disable"}, {"description": "Enable adding NAT46 route", "help": "Enable adding NAT46 route.", "label": "Enable", "name": "enable"}]

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
    "VALID_BODY_NAT46",
    "VALID_BODY_ADD_NAT46_ROUTE",
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