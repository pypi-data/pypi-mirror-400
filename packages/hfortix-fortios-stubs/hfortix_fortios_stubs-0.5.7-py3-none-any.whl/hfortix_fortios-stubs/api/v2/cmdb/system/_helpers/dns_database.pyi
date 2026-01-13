from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_STATUS: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]
VALID_BODY_TYPE: Literal[{"description": "Primary DNS zone, to manage entries directly", "help": "Primary DNS zone, to manage entries directly.", "label": "Primary", "name": "primary"}, {"description": "Secondary DNS zone, to import entries from other DNS zones", "help": "Secondary DNS zone, to import entries from other DNS zones.", "label": "Secondary", "name": "secondary"}]
VALID_BODY_VIEW: Literal[{"description": "Shadow DNS zone to serve internal clients", "help": "Shadow DNS zone to serve internal clients.", "label": "Shadow", "name": "shadow"}, {"description": "Public DNS zone to serve public clients", "help": "Public DNS zone to serve public clients.", "label": "Public", "name": "public"}, {"description": "implicit DNS zone for ztna dox tunnel", "help": "implicit DNS zone for ztna dox tunnel.", "label": "Shadow Ztna", "name": "shadow-ztna"}, {"description": "Shadow DNS zone for internal proxy", "help": "Shadow DNS zone for internal proxy.", "label": "Proxy", "name": "proxy"}]
VALID_BODY_AUTHORITATIVE: Literal[{"description": "Enable authoritative zone", "help": "Enable authoritative zone.", "label": "Enable", "name": "enable"}, {"description": "Disable authoritative zone", "help": "Disable authoritative zone.", "label": "Disable", "name": "disable"}]
VALID_BODY_INTERFACE_SELECT_METHOD: Literal[{"description": "Set outgoing interface automatically", "help": "Set outgoing interface automatically.", "label": "Auto", "name": "auto"}, {"description": "Set outgoing interface by SD-WAN or policy routing rules", "help": "Set outgoing interface by SD-WAN or policy routing rules.", "label": "Sdwan", "name": "sdwan"}, {"description": "Set outgoing interface manually", "help": "Set outgoing interface manually.", "label": "Specify", "name": "specify"}]

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
    "VALID_BODY_STATUS",
    "VALID_BODY_TYPE",
    "VALID_BODY_VIEW",
    "VALID_BODY_AUTHORITATIVE",
    "VALID_BODY_INTERFACE_SELECT_METHOD",
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