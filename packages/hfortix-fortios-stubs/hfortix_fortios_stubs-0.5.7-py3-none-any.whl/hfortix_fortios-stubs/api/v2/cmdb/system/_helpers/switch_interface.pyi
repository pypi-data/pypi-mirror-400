from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_TYPE: Literal[{"description": "Switch for normal switch functionality (available in NAT mode only)", "help": "Switch for normal switch functionality (available in NAT mode only).", "label": "Switch", "name": "switch"}, {"description": "Hub to duplicate packets to all member ports", "help": "Hub to duplicate packets to all member ports.", "label": "Hub", "name": "hub"}]
VALID_BODY_INTRA_SWITCH_POLICY: Literal[{"description": "Traffic between switch members is implicitly allowed", "help": "Traffic between switch members is implicitly allowed.", "label": "Implicit", "name": "implicit"}, {"description": "Traffic between switch members must match firewall policies", "help": "Traffic between switch members must match firewall policies.", "label": "Explicit", "name": "explicit"}]
VALID_BODY_SPAN: Literal[{"description": "Disable port spanning", "help": "Disable port spanning.", "label": "Disable", "name": "disable"}, {"description": "Enable port spanning", "help": "Enable port spanning.", "label": "Enable", "name": "enable"}]
VALID_BODY_SPAN_DIRECTION: Literal[{"description": "Copies only received packets from source SPAN ports to the destination SPAN port", "help": "Copies only received packets from source SPAN ports to the destination SPAN port.", "label": "Rx", "name": "rx"}, {"description": "Copies only transmitted packets from source SPAN ports to the destination SPAN port", "help": "Copies only transmitted packets from source SPAN ports to the destination SPAN port.", "label": "Tx", "name": "tx"}, {"description": "Copies both received and transmitted packets from source SPAN ports to the destination SPAN port", "help": "Copies both received and transmitted packets from source SPAN ports to the destination SPAN port.", "label": "Both", "name": "both"}]

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
    "VALID_BODY_INTRA_SWITCH_POLICY",
    "VALID_BODY_SPAN",
    "VALID_BODY_SPAN_DIRECTION",
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