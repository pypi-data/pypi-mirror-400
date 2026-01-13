from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_CATEGORY: Literal[{"description": "Device category", "help": "Device category.", "label": "Device", "name": "device"}, {"description": "Firewall user category", "help": "Firewall user category.", "label": "Firewall User", "name": "firewall-user"}, {"description": "EMS Tag category", "help": "EMS Tag category.", "label": "Ems Tag", "name": "ems-tag"}, {"description": "FortiVoice Tag category", "help": "FortiVoice Tag category.", "label": "Fortivoice Tag", "name": "fortivoice-tag"}, {"description": "Vulnerability category", "help": "Vulnerability category.", "label": "Vulnerability", "name": "vulnerability"}]
VALID_BODY_STATUS: Literal[{"description": "Enable NAC policy", "help": "Enable NAC policy.", "label": "Enable", "name": "enable"}, {"description": "Disable NAC policy", "help": "Disable NAC policy.", "label": "Disable", "name": "disable"}]
VALID_BODY_MATCH_TYPE: Literal[{"description": "Matched devices will be removed on dynamic events like link-down,device-inactivity,switch-offline", "help": "Matched devices will be removed on dynamic events like link-down,device-inactivity,switch-offline.", "label": "Dynamic", "name": "dynamic"}, {"description": "Matched devices will be retained until the match-period", "help": "Matched devices will be retained until the match-period.", "label": "Override", "name": "override"}]
VALID_BODY_MATCH_REMOVE: Literal[{"description": "Remove the matched override devices based on the match period", "help": "Remove the matched override devices based on the match period.", "label": "Default", "name": "default"}, {"description": "Remove the matched override devices based on switch port link down event", "help": "Remove the matched override devices based on switch port link down event.", "label": "Link Down", "name": "link-down"}]

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
    "VALID_BODY_CATEGORY",
    "VALID_BODY_STATUS",
    "VALID_BODY_MATCH_TYPE",
    "VALID_BODY_MATCH_REMOVE",
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