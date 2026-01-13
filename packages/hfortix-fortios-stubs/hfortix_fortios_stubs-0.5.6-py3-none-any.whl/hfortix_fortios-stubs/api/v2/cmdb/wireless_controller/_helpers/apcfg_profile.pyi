from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_AP_FAMILY: Literal[{"description": "FortiAP Family", "help": "FortiAP Family.", "label": "Fap", "name": "fap"}, {"description": "FortiAP-U Family", "help": "FortiAP-U Family.", "label": "Fap U", "name": "fap-u"}, {"description": "FortiAP-C Family", "help": "FortiAP-C Family.", "label": "Fap C", "name": "fap-c"}]
VALID_BODY_AC_TYPE: Literal[{"description": "This controller is the one and only controller that the AP could join after applying AP local configuration", "help": "This controller is the one and only controller that the AP could join after applying AP local configuration.", "label": "Default", "name": "default"}, {"description": "Specified controller is the one and only controller that the AP could join after applying AP local configuration", "help": "Specified controller is the one and only controller that the AP could join after applying AP local configuration.", "label": "Specify", "name": "specify"}, {"description": "Any controller defined by AP local configuration after applying AP local configuration", "help": "Any controller defined by AP local configuration after applying AP local configuration.", "label": "Apcfg", "name": "apcfg"}]

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
    "VALID_BODY_AP_FAMILY",
    "VALID_BODY_AC_TYPE",
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