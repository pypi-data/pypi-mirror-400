from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_MED_TLVS: Literal[{"description": "Inventory management TLVs", "help": "Inventory management TLVs.", "label": "Inventory Management", "name": "inventory-management"}, {"description": "Network policy TLVs", "help": "Network policy TLVs.", "label": "Network Policy", "name": "network-policy"}, {"description": "Power manangement TLVs", "help": "Power manangement TLVs.", "label": "Power Management", "name": "power-management"}, {"description": "Location identificaion TLVs", "help": "Location identificaion TLVs.", "label": "Location Identification", "name": "location-identification"}]
VALID_BODY_802_1_TLVS: Literal[{"description": "Port native VLAN TLV", "help": "Port native VLAN TLV.", "label": "Port Vlan Id", "name": "port-vlan-id"}]
VALID_BODY_802_3_TLVS: Literal[{"description": "Maximum frame size TLV", "help": "Maximum frame size TLV.", "label": "Max Frame Size", "name": "max-frame-size"}, {"description": "PoE+ classification TLV", "help": "PoE+ classification TLV.", "label": "Power Negotiation", "name": "power-negotiation"}]
VALID_BODY_AUTO_ISL: Literal[{"description": "Disable automatic MCLAG inter chassis link", "help": "Disable automatic MCLAG inter chassis link.", "label": "Disable", "name": "disable"}, {"description": "Enable automatic MCLAG inter chassis link", "help": "Enable automatic MCLAG inter chassis link.", "label": "Enable", "name": "enable"}]
VALID_BODY_AUTO_MCLAG_ICL: Literal[{"description": "Disable auto inter-switch-LAG", "help": "Disable auto inter-switch-LAG.", "label": "Disable", "name": "disable"}, {"description": "Enable auto inter-switch-LAG", "help": "Enable auto inter-switch-LAG.", "label": "Enable", "name": "enable"}]
VALID_BODY_AUTO_ISL_AUTH: Literal[{"description": "No auto inter-switch-LAG authentication", "help": "No auto inter-switch-LAG authentication.", "label": "Legacy", "name": "legacy"}, {"description": "Strict auto inter-switch-LAG authentication", "help": "Strict auto inter-switch-LAG authentication.", "label": "Strict", "name": "strict"}, {"description": "Relax auto inter-switch-LAG authentication", "help": "Relax auto inter-switch-LAG authentication.", "label": "Relax", "name": "relax"}]
VALID_BODY_AUTO_ISL_AUTH_ENCRYPT: Literal[{"description": "No auto inter-switch-LAG encryption", "help": "No auto inter-switch-LAG encryption.", "label": "None", "name": "none"}, {"description": "Mixed auto inter-switch-LAG encryption", "help": "Mixed auto inter-switch-LAG encryption.", "label": "Mixed", "name": "mixed"}, {"description": "Must auto inter-switch-LAG encryption", "help": "Must auto inter-switch-LAG encryption.", "label": "Must", "name": "must"}]

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
    "VALID_BODY_MED_TLVS",
    "VALID_BODY_802_1_TLVS",
    "VALID_BODY_802_3_TLVS",
    "VALID_BODY_AUTO_ISL",
    "VALID_BODY_AUTO_MCLAG_ICL",
    "VALID_BODY_AUTO_ISL_AUTH",
    "VALID_BODY_AUTO_ISL_AUTH_ENCRYPT",
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