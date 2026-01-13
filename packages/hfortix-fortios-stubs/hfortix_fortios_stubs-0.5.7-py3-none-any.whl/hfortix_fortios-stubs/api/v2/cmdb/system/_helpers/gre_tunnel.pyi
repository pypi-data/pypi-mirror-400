from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_IP_VERSION: Literal[{"description": "Use IPv4 addressing for gateways", "help": "Use IPv4 addressing for gateways.", "label": "4", "name": "4"}, {"description": "Use IPv6 addressing for gateways", "help": "Use IPv6 addressing for gateways.", "label": "6", "name": "6"}]
VALID_BODY_USE_SDWAN: Literal[{"description": "Disable use of SD-WAN to reach remote gateway", "help": "Disable use of SD-WAN to reach remote gateway.", "label": "Disable", "name": "disable"}, {"description": "Enable use of SD-WAN to reach remote gateway", "help": "Enable use of SD-WAN to reach remote gateway.", "label": "Enable", "name": "enable"}]
VALID_BODY_SEQUENCE_NUMBER_TRANSMISSION: Literal[{"description": "Include sequence numbers in transmitted GRE packets", "help": "Include sequence numbers in transmitted GRE packets.", "label": "Disable", "name": "disable"}, {"description": "Do not  include sequence numbers in transmitted GRE packets", "help": "Do not  include sequence numbers in transmitted GRE packets.", "label": "Enable", "name": "enable"}]
VALID_BODY_SEQUENCE_NUMBER_RECEPTION: Literal[{"description": "Do not validate sequence number in received GRE packets", "help": "Do not validate sequence number in received GRE packets.", "label": "Disable", "name": "disable"}, {"description": "Validate sequence numbers in received GRE packets", "help": "Validate sequence numbers in received GRE packets.", "label": "Enable", "name": "enable"}]
VALID_BODY_CHECKSUM_TRANSMISSION: Literal[{"description": "Do not include checksums in transmitted GRE packets", "help": "Do not include checksums in transmitted GRE packets.", "label": "Disable", "name": "disable"}, {"description": "Include checksums in transmitted GRE packets", "help": "Include checksums in transmitted GRE packets.", "label": "Enable", "name": "enable"}]
VALID_BODY_CHECKSUM_RECEPTION: Literal[{"description": "Do not validate checksums in received GRE packets", "help": "Do not validate checksums in received GRE packets.", "label": "Disable", "name": "disable"}, {"description": "Validate checksums in received GRE packets", "help": "Validate checksums in received GRE packets.", "label": "Enable", "name": "enable"}]
VALID_BODY_DSCP_COPYING: Literal[{"description": "Disable DSCP copying", "help": "Disable DSCP copying.", "label": "Disable", "name": "disable"}, {"description": "Enable DSCP copying", "help": "Enable DSCP copying.", "label": "Enable", "name": "enable"}]

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
    "VALID_BODY_IP_VERSION",
    "VALID_BODY_USE_SDWAN",
    "VALID_BODY_SEQUENCE_NUMBER_TRANSMISSION",
    "VALID_BODY_SEQUENCE_NUMBER_RECEPTION",
    "VALID_BODY_CHECKSUM_TRANSMISSION",
    "VALID_BODY_CHECKSUM_RECEPTION",
    "VALID_BODY_DSCP_COPYING",
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