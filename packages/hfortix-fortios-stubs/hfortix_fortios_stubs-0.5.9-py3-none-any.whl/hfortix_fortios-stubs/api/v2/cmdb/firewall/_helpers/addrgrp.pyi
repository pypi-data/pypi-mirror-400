from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_TYPE: Literal[{"description": "Default address group type (address may belong to multiple groups)", "help": "Default address group type (address may belong to multiple groups).", "label": "Default", "name": "default"}, {"description": "Address folder group (members may not belong to any other group)", "help": "Address folder group (members may not belong to any other group).", "label": "Folder", "name": "folder"}]
VALID_BODY_CATEGORY: Literal[{"description": "Default address group category (cannot be used as ztna-ems-tag/ztna-geo-tag in policy)", "help": "Default address group category (cannot be used as ztna-ems-tag/ztna-geo-tag in policy).", "label": "Default", "name": "default"}, {"description": "Members must be ztna-ems-tag group or ems-tag address, can be used as ztna-ems-tag in policy", "help": "Members must be ztna-ems-tag group or ems-tag address, can be used as ztna-ems-tag in policy.", "label": "Ztna Ems Tag", "name": "ztna-ems-tag"}, {"description": "Members must be ztna-geo-tag group or geographic address, can be used as ztna-geo-tag in policy", "help": "Members must be ztna-geo-tag group or geographic address, can be used as ztna-geo-tag in policy.", "label": "Ztna Geo Tag", "name": "ztna-geo-tag"}]
VALID_BODY_ALLOW_ROUTING: Literal[{"description": "Enable use of this group in routing configurations", "help": "Enable use of this group in routing configurations.", "label": "Enable", "name": "enable"}, {"description": "Disable use of this group in routing configurations", "help": "Disable use of this group in routing configurations.", "label": "Disable", "name": "disable"}]
VALID_BODY_EXCLUDE: Literal[{"description": "Enable address exclusion", "help": "Enable address exclusion.", "label": "Enable", "name": "enable"}, {"description": "Disable address exclusion", "help": "Disable address exclusion.", "label": "Disable", "name": "disable"}]
VALID_BODY_FABRIC_OBJECT: Literal[{"description": "Object is set as a security fabric-wide global object", "help": "Object is set as a security fabric-wide global object.", "label": "Enable", "name": "enable"}, {"description": "Object is local to this security fabric member", "help": "Object is local to this security fabric member.", "label": "Disable", "name": "disable"}]

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
    "VALID_BODY_CATEGORY",
    "VALID_BODY_ALLOW_ROUTING",
    "VALID_BODY_EXCLUDE",
    "VALID_BODY_FABRIC_OBJECT",
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