from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_IPV6_ADDRESS_TYPE: Literal[{"description": "Address type not available", "help": "Address type not available.", "label": "Not Available", "name": "not-available"}, {"description": "Address type available", "help": "Address type available.", "label": "Available", "name": "available"}, {"description": "Availability of the address type not known", "help": "Availability of the address type not known.", "label": "Not Known", "name": "not-known"}]
VALID_BODY_IPV4_ADDRESS_TYPE: Literal[{"description": "Address type not available", "help": "Address type not available.", "label": "Not Available", "name": "not-available"}, {"description": "Public IPv4 address available", "help": "Public IPv4 address available.", "label": "Public", "name": "public"}, {"description": "Port-restricted IPv4 address available", "help": "Port-restricted IPv4 address available.", "label": "Port Restricted", "name": "port-restricted"}, {"description": "Single NATed private IPv4 address available", "help": "Single NATed private IPv4 address available.", "label": "Single Nated Private", "name": "single-NATed-private"}, {"description": "Double NATed private IPv4 address available", "help": "Double NATed private IPv4 address available.", "label": "Double Nated Private", "name": "double-NATed-private"}, {"description": "Port-restricted IPv4 address and single NATed IPv4 address available", "help": "Port-restricted IPv4 address and single NATed IPv4 address available.", "label": "Port Restricted And Single Nated", "name": "port-restricted-and-single-NATed"}, {"description": "Port-restricted IPv4 address and double NATed IPv4 address available", "help": "Port-restricted IPv4 address and double NATed IPv4 address available.", "label": "Port Restricted And Double Nated", "name": "port-restricted-and-double-NATed"}, {"description": "Availability of the address type is not known", "help": "Availability of the address type is not known.", "label": "Not Known", "name": "not-known"}]

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
    "VALID_BODY_IPV6_ADDRESS_TYPE",
    "VALID_BODY_IPV4_ADDRESS_TYPE",
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