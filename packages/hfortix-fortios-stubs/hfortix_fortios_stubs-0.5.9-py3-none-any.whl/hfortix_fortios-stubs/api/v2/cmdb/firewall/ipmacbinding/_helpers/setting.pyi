from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_BINDTHROUGHFW: Literal[{"description": "Enable IP/MAC binding for packets that would normally go through the firewall", "help": "Enable IP/MAC binding for packets that would normally go through the firewall.", "label": "Enable", "name": "enable"}, {"description": "Disable IP/MAC binding for packets that would normally go through the firewall", "help": "Disable IP/MAC binding for packets that would normally go through the firewall.", "label": "Disable", "name": "disable"}]
VALID_BODY_BINDTOFW: Literal[{"description": "Enable IP/MAC binding for packets that would normally go to the firewall", "help": "Enable IP/MAC binding for packets that would normally go to the firewall.", "label": "Enable", "name": "enable"}, {"description": "Disable IP/MAC binding for packets that would normally go to the firewall", "help": "Disable IP/MAC binding for packets that would normally go to the firewall.", "label": "Disable", "name": "disable"}]
VALID_BODY_UNDEFINEDHOST: Literal[{"description": "Allow packets from MAC addresses not in the IP/MAC list", "help": "Allow packets from MAC addresses not in the IP/MAC list.", "label": "Allow", "name": "allow"}, {"description": "Block packets from MAC addresses not in the IP/MAC list", "help": "Block packets from MAC addresses not in the IP/MAC list.", "label": "Block", "name": "block"}]

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
    "VALID_BODY_BINDTHROUGHFW",
    "VALID_BODY_BINDTOFW",
    "VALID_BODY_UNDEFINEDHOST",
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