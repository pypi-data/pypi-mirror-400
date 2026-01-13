from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_DIAL_ON_DEMAND: Literal[{"description": "Enable dial on demand", "help": "Enable dial on demand.", "label": "Enable", "name": "enable"}, {"description": "Disable dial on demand", "help": "Disable dial on demand.", "label": "Disable", "name": "disable"}]
VALID_BODY_IPV6: Literal[{"description": "Enable IPv6CP", "help": "Enable IPv6CP.", "label": "Enable", "name": "enable"}, {"description": "Disable IPv6CP", "help": "Disable IPv6CP.", "label": "Disable", "name": "disable"}]
VALID_BODY_PPPOE_EGRESS_COS: Literal[{"description": "CoS 0", "help": "CoS 0.", "label": "Cos0", "name": "cos0"}, {"description": "CoS 1", "help": "CoS 1.", "label": "Cos1", "name": "cos1"}, {"description": "CoS 2", "help": "CoS 2.", "label": "Cos2", "name": "cos2"}, {"description": "CoS 3", "help": "CoS 3.", "label": "Cos3", "name": "cos3"}, {"description": "CoS 4", "help": "CoS 4.", "label": "Cos4", "name": "cos4"}, {"description": "CoS 5", "help": "CoS 5.", "label": "Cos5", "name": "cos5"}, {"description": "CoS 6", "help": "CoS 6.", "label": "Cos6", "name": "cos6"}, {"description": "CoS 7", "help": "CoS 7.", "label": "Cos7", "name": "cos7"}]
VALID_BODY_AUTH_TYPE: Literal[{"description": "Automatically choose the authentication method", "help": "Automatically choose the authentication method.", "label": "Auto", "name": "auto"}, {"description": "PAP authentication", "help": "PAP authentication.", "label": "Pap", "name": "pap"}, {"description": "CHAP authentication", "help": "CHAP authentication.", "label": "Chap", "name": "chap"}, {"description": "MS-CHAPv1 authentication", "help": "MS-CHAPv1 authentication.", "label": "Mschapv1", "name": "mschapv1"}, {"description": "MS-CHAPv2 authentication", "help": "MS-CHAPv2 authentication.", "label": "Mschapv2", "name": "mschapv2"}]
VALID_BODY_PPPOE_UNNUMBERED_NEGOTIATE: Literal[{"description": "Enable PPPoE unnumbered negotiation", "help": "Enable PPPoE unnumbered negotiation.", "label": "Enable", "name": "enable"}, {"description": "Disable PPPoE unnumbered negotiation", "help": "Disable PPPoE unnumbered negotiation.", "label": "Disable", "name": "disable"}]
VALID_BODY_MULTILINK: Literal[{"description": "Enable PPP multilink support", "help": "Enable PPP multilink support.", "label": "Enable", "name": "enable"}, {"description": "Disable PPP multilink support", "help": "Disable PPP multilink support.", "label": "Disable", "name": "disable"}]

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
    "VALID_BODY_DIAL_ON_DEMAND",
    "VALID_BODY_IPV6",
    "VALID_BODY_PPPOE_EGRESS_COS",
    "VALID_BODY_AUTH_TYPE",
    "VALID_BODY_PPPOE_UNNUMBERED_NEGOTIATE",
    "VALID_BODY_MULTILINK",
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