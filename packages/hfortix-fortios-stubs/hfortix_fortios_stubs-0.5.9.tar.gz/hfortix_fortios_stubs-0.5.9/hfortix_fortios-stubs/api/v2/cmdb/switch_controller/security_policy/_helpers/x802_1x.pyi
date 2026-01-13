from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_SECURITY_MODE: Literal[{"help": "802.1X port based authentication.", "label": "802.1X", "name": "802.1X"}, {"help": "802.1X MAC based authentication.", "label": "802.1X Mac Based", "name": "802.1X-mac-based"}]
VALID_BODY_MAC_AUTH_BYPASS: Literal[{"description": "Disable MAB", "help": "Disable MAB.", "label": "Disable", "name": "disable"}, {"description": "Enable MAB", "help": "Enable MAB.", "label": "Enable", "name": "enable"}]
VALID_BODY_AUTH_ORDER: Literal[{"description": "Use EAP 1X authentication first then MAB", "help": "Use EAP 1X authentication first then MAB.", "label": "Dot1X Mab", "name": "dot1x-mab"}, {"description": "Use MAB authentication first then EAP 1X", "help": "Use MAB authentication first then EAP 1X.", "label": "Mab Dot1X", "name": "mab-dot1x"}, {"description": "Use MAB authentication only", "help": "Use MAB authentication only.", "label": "Mab", "name": "mab"}]
VALID_BODY_AUTH_PRIORITY: Literal[{"description": "EAP 1X authentication has a higher priority than MAB with the legacy implementation", "help": "EAP 1X authentication has a higher priority than MAB with the legacy implementation.", "label": "Legacy", "name": "legacy"}, {"description": "EAP 1X authentication has a higher priority than MAB", "help": "EAP 1X authentication has a higher priority than MAB.", "label": "Dot1X Mab", "name": "dot1x-mab"}, {"description": "MAB authentication has a higher priority than EAP 1X", "help": "MAB authentication has a higher priority than EAP 1X.", "label": "Mab Dot1X", "name": "mab-dot1x"}]
VALID_BODY_OPEN_AUTH: Literal[{"description": "Disable open authentication", "help": "Disable open authentication.", "label": "Disable", "name": "disable"}, {"description": "Enable open authentication", "help": "Enable open authentication.", "label": "Enable", "name": "enable"}]
VALID_BODY_EAP_PASSTHRU: Literal[{"description": "Disable EAP pass-through mode on this interface", "help": "Disable EAP pass-through mode on this interface.", "label": "Disable", "name": "disable"}, {"description": "Enable EAP pass-through mode on this interface", "help": "Enable EAP pass-through mode on this interface.", "label": "Enable", "name": "enable"}]
VALID_BODY_EAP_AUTO_UNTAGGED_VLANS: Literal[{"description": "Disable automatic inclusion of untagged VLANs", "help": "Disable automatic inclusion of untagged VLANs.", "label": "Disable", "name": "disable"}, {"description": "Enable automatic inclusion of untagged VLANs", "help": "Enable automatic inclusion of untagged VLANs.", "label": "Enable", "name": "enable"}]
VALID_BODY_GUEST_VLAN: Literal[{"description": "Disable guest VLAN on this interface", "help": "Disable guest VLAN on this interface.", "label": "Disable", "name": "disable"}, {"description": "Enable guest VLAN on this interface", "help": "Enable guest VLAN on this interface.", "label": "Enable", "name": "enable"}]
VALID_BODY_AUTH_FAIL_VLAN: Literal[{"description": "Disable authentication fail VLAN on this interface", "help": "Disable authentication fail VLAN on this interface.", "label": "Disable", "name": "disable"}, {"description": "Enable authentication fail VLAN on this interface", "help": "Enable authentication fail VLAN on this interface.", "label": "Enable", "name": "enable"}]
VALID_BODY_FRAMEVID_APPLY: Literal[{"description": "Disable the capability to apply the EAP/MAB frame VLAN to the port native VLAN", "help": "Disable the capability to apply the EAP/MAB frame VLAN to the port native VLAN.", "label": "Disable", "name": "disable"}, {"description": "Enable the capability to apply the EAP/MAB frame VLAN to the port native VLAN", "help": "Enable the capability to apply the EAP/MAB frame VLAN to the port native VLAN.", "label": "Enable", "name": "enable"}]
VALID_BODY_RADIUS_TIMEOUT_OVERWRITE: Literal[{"description": "Override the global RADIUS session timeout", "help": "Override the global RADIUS session timeout.", "label": "Disable", "name": "disable"}, {"description": "Use the global RADIUS session timeout", "help": "Use the global RADIUS session timeout.", "label": "Enable", "name": "enable"}]
VALID_BODY_POLICY_TYPE: Literal[{"help": "802.1X security policy.", "label": "802.1X", "name": "802.1X"}]
VALID_BODY_AUTHSERVER_TIMEOUT_VLAN: Literal[{"description": "Disable authentication server timeout VLAN on this interface", "help": "Disable authentication server timeout VLAN on this interface.", "label": "Disable", "name": "disable"}, {"description": "Enable authentication server timeout VLAN on this interface", "help": "Enable authentication server timeout VLAN on this interface.", "label": "Enable", "name": "enable"}]
VALID_BODY_AUTHSERVER_TIMEOUT_TAGGED: Literal[{"description": "Disable authentication server timeout on this interface", "help": "Disable authentication server timeout on this interface.", "label": "Disable", "name": "disable"}, {"description": "LLDP voice timeout for the tagged VLAN on this interface", "help": "LLDP voice timeout for the tagged VLAN on this interface.", "label": "Lldp Voice", "name": "lldp-voice"}, {"description": "Static timeout for the tagged VLAN on this interface", "help": "Static timeout for the tagged VLAN on this interface.", "label": "Static", "name": "static"}]
VALID_BODY_DACL: Literal[{"description": "Disable dynamic access control list on this interface", "help": "Disable dynamic access control list on this interface.", "label": "Disable", "name": "disable"}, {"description": "Enable dynamic access control on this interface", "help": "Enable dynamic access control on this interface.", "label": "Enable", "name": "enable"}]

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
    "VALID_BODY_SECURITY_MODE",
    "VALID_BODY_MAC_AUTH_BYPASS",
    "VALID_BODY_AUTH_ORDER",
    "VALID_BODY_AUTH_PRIORITY",
    "VALID_BODY_OPEN_AUTH",
    "VALID_BODY_EAP_PASSTHRU",
    "VALID_BODY_EAP_AUTO_UNTAGGED_VLANS",
    "VALID_BODY_GUEST_VLAN",
    "VALID_BODY_AUTH_FAIL_VLAN",
    "VALID_BODY_FRAMEVID_APPLY",
    "VALID_BODY_RADIUS_TIMEOUT_OVERWRITE",
    "VALID_BODY_POLICY_TYPE",
    "VALID_BODY_AUTHSERVER_TIMEOUT_VLAN",
    "VALID_BODY_AUTHSERVER_TIMEOUT_TAGGED",
    "VALID_BODY_DACL",
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