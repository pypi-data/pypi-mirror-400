from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_MODEM_ID: Literal[{"description": "Modem one", "help": "Modem one.", "label": "Modem1", "name": "modem1"}, {"description": "Modem two", "help": "Modem two.", "label": "Modem2", "name": "modem2"}, {"description": "All modems", "help": "All modems.", "label": "All", "name": "all"}]
VALID_BODY_TYPE: Literal[{"description": "Assign by SIM carrier", "help": "Assign by SIM carrier.", "label": "Carrier", "name": "carrier"}, {"description": "Assign to SIM slot 1 or 2", "help": "Assign to SIM slot 1 or 2.", "label": "Slot", "name": "slot"}, {"description": "Assign to a specific SIM by ICCID", "help": "Assign to a specific SIM by ICCID.", "label": "Iccid", "name": "iccid"}, {"description": "Compatible with any SIM", "help": "Compatible with any SIM. Assigned if no other dataplan matches the chosen SIM.", "label": "Generic", "name": "generic"}]
VALID_BODY_SLOT: Literal[{"description": "Sim slot one", "help": "Sim slot one.", "label": "Sim1", "name": "sim1"}, {"description": "Sim slot two", "help": "Sim slot two.", "label": "Sim2", "name": "sim2"}]
VALID_BODY_AUTH_TYPE: Literal[{"description": "No authentication", "help": "No authentication.", "label": "None", "name": "none"}, {"description": "PAP", "help": "PAP.", "label": "Pap", "name": "pap"}, {"description": "CHAP", "help": "CHAP.", "label": "Chap", "name": "chap"}]
VALID_BODY_PDN: Literal[{"description": "IPv4 only PDN activation", "help": "IPv4 only PDN activation.", "label": "Ipv4 Only", "name": "ipv4-only"}, {"description": "IPv6 only PDN activation", "help": "IPv6 only PDN activation.", "label": "Ipv6 Only", "name": "ipv6-only"}, {"description": "Both IPv4 and IPv6 PDN activations", "help": "Both IPv4 and IPv6 PDN activations.", "label": "Ipv4 Ipv6", "name": "ipv4-ipv6"}]
VALID_BODY_OVERAGE: Literal[{"description": "Disable dataplan overage detection", "help": "Disable dataplan overage detection.", "label": "Disable", "name": "disable"}, {"description": "Enable dataplan overage detection", "help": "Enable dataplan overage detection.", "label": "Enable", "name": "enable"}]
VALID_BODY_PRIVATE_NETWORK: Literal[{"description": "Disable dataplan private network support", "help": "Disable dataplan private network support.", "label": "Disable", "name": "disable"}, {"description": "Enable dataplan private network support", "help": "Enable dataplan private network support.", "label": "Enable", "name": "enable"}]

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
    "VALID_BODY_MODEM_ID",
    "VALID_BODY_TYPE",
    "VALID_BODY_SLOT",
    "VALID_BODY_AUTH_TYPE",
    "VALID_BODY_PDN",
    "VALID_BODY_OVERAGE",
    "VALID_BODY_PRIVATE_NETWORK",
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