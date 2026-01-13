from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_AD_MODE: Literal[{"description": "The server is not configured as an Active Directory Domain Server (AD DS)", "help": "The server is not configured as an Active Directory Domain Server (AD DS).", "label": "None", "name": "none"}, {"description": "The server is configured as an Active Directory Domain Server (AD DS)", "help": "The server is configured as an Active Directory Domain Server (AD DS).", "label": "Ds", "name": "ds"}, {"description": "The server is an Active Directory Lightweight Domain Server (AD LDS)", "help": "The server is an Active Directory Lightweight Domain Server (AD LDS).", "label": "Lds", "name": "lds"}]
VALID_BODY_INTERFACE_SELECT_METHOD: Literal[{"description": "Set outgoing interface automatically", "help": "Set outgoing interface automatically.", "label": "Auto", "name": "auto"}, {"description": "Set outgoing interface by SD-WAN or policy routing rules", "help": "Set outgoing interface by SD-WAN or policy routing rules.", "label": "Sdwan", "name": "sdwan"}, {"description": "Set outgoing interface manually", "help": "Set outgoing interface manually.", "label": "Specify", "name": "specify"}]
VALID_BODY_CHANGE_DETECTION: Literal[{"description": "Enable detection of a configuration change in the Active Directory server", "help": "Enable detection of a configuration change in the Active Directory server.", "label": "Enable", "name": "enable"}, {"description": "Disable detection of a configuration change in the Active Directory server", "help": "Disable detection of a configuration change in the Active Directory server.", "label": "Disable", "name": "disable"}]
VALID_BODY_DNS_SRV_LOOKUP: Literal[{"description": "Enable DNS service lookup", "help": "Enable DNS service lookup.", "label": "Enable", "name": "enable"}, {"description": "Disable DNS service lookup", "help": "Disable DNS service lookup.", "label": "Disable", "name": "disable"}]

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
    "VALID_BODY_AD_MODE",
    "VALID_BODY_INTERFACE_SELECT_METHOD",
    "VALID_BODY_CHANGE_DETECTION",
    "VALID_BODY_DNS_SRV_LOOKUP",
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