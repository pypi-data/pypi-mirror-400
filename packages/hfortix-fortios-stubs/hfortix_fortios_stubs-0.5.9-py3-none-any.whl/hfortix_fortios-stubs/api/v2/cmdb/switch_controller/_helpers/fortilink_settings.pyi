from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_LINK_DOWN_FLUSH: Literal[{"description": "Disable clearing NAC and dynamic devices on a switch port when link down event happens", "help": "Disable clearing NAC and dynamic devices on a switch port when link down event happens.", "label": "Disable", "name": "disable"}, {"description": "Enable clearing NAC and dynamic devices on a switch port when link down event happens", "help": "Enable clearing NAC and dynamic devices on a switch port when link down event happens.", "label": "Enable", "name": "enable"}]
VALID_BODY_ACCESS_VLAN_MODE: Literal[{"description": "Backward compatible behavior", "help": "Backward compatible behavior.", "label": "Legacy", "name": "legacy"}, {"description": "When connection to FortiGate is lost, traffic on the VLAN may continue directly between end points", "help": "When connection to FortiGate is lost, traffic on the VLAN may continue directly between end points.", "label": "Fail Open", "name": "fail-open"}, {"description": "When connection to FortiGate is lost, traffic between endpoints on the VLAN is blocked", "help": "When connection to FortiGate is lost, traffic between endpoints on the VLAN is blocked.", "label": "Fail Close", "name": "fail-close"}]

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
    "VALID_BODY_LINK_DOWN_FLUSH",
    "VALID_BODY_ACCESS_VLAN_MODE",
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