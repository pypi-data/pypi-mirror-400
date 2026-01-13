from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_DH_MULTIPROCESS: Literal[{"description": "Enable multiprocess Diffie-Hellman for IKE", "help": "Enable multiprocess Diffie-Hellman for IKE.", "label": "Enable", "name": "enable"}, {"description": "Disable multiprocess Diffie-Hellman for IKE", "help": "Disable multiprocess Diffie-Hellman for IKE.", "label": "Disable", "name": "disable"}]
VALID_BODY_DH_MODE: Literal[{"description": "Prefer CPU to perform Diffie-Hellman calculations", "help": "Prefer CPU to perform Diffie-Hellman calculations.", "label": "Software", "name": "software"}, {"description": "Prefer CPX to perform Diffie-Hellman calculations", "help": "Prefer CPX to perform Diffie-Hellman calculations.", "label": "Hardware", "name": "hardware"}]
VALID_BODY_DH_KEYPAIR_CACHE: Literal[{"description": "Enable Diffie-Hellman key pair cache", "help": "Enable Diffie-Hellman key pair cache.", "label": "Enable", "name": "enable"}, {"description": "Disable Diffie-Hellman key pair cache", "help": "Disable Diffie-Hellman key pair cache.", "label": "Disable", "name": "disable"}]
VALID_BODY_DH_KEYPAIR_THROTTLE: Literal[{"description": "Enable Diffie-Hellman key pair cache CPU throttling", "help": "Enable Diffie-Hellman key pair cache CPU throttling.", "label": "Enable", "name": "enable"}, {"description": "Disable Diffie-Hellman key pair cache CPU throttling", "help": "Disable Diffie-Hellman key pair cache CPU throttling.", "label": "Disable", "name": "disable"}]

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
    "VALID_BODY_DH_MULTIPROCESS",
    "VALID_BODY_DH_MODE",
    "VALID_BODY_DH_KEYPAIR_CACHE",
    "VALID_BODY_DH_KEYPAIR_THROTTLE",
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