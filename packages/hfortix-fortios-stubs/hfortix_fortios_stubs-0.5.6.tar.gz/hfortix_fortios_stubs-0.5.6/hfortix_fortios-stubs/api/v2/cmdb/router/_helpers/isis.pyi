from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_IS_TYPE: Literal[{"description": "Level 1 and 2", "help": "Level 1 and 2.", "label": "Level 1 2", "name": "level-1-2"}, {"description": "Level 1 only", "help": "Level 1 only.", "label": "Level 1", "name": "level-1"}, {"description": "Level 2 only", "help": "Level 2 only.", "label": "Level 2 Only", "name": "level-2-only"}]
VALID_BODY_ADV_PASSIVE_ONLY: Literal[{"description": "Advertise passive interfaces only", "help": "Advertise passive interfaces only.", "label": "Enable", "name": "enable"}, {"description": "Advertise all IS-IS enabled interfaces", "help": "Advertise all IS-IS enabled interfaces.", "label": "Disable", "name": "disable"}]
VALID_BODY_ADV_PASSIVE_ONLY6: Literal[{"description": "Advertise passive interfaces only", "help": "Advertise passive interfaces only.", "label": "Enable", "name": "enable"}, {"description": "Advertise all IS-IS enabled interfaces", "help": "Advertise all IS-IS enabled interfaces.", "label": "Disable", "name": "disable"}]
VALID_BODY_AUTH_MODE_L1: Literal[{"description": "Password", "help": "Password.", "label": "Password", "name": "password"}, {"description": "MD5", "help": "MD5.", "label": "Md5", "name": "md5"}]
VALID_BODY_AUTH_MODE_L2: Literal[{"description": "Password", "help": "Password.", "label": "Password", "name": "password"}, {"description": "MD5", "help": "MD5.", "label": "Md5", "name": "md5"}]
VALID_BODY_AUTH_SENDONLY_L1: Literal[{"description": "Enable level 1 authentication send-only", "help": "Enable level 1 authentication send-only.", "label": "Enable", "name": "enable"}, {"description": "Disable level 1 authentication send-only", "help": "Disable level 1 authentication send-only.", "label": "Disable", "name": "disable"}]
VALID_BODY_AUTH_SENDONLY_L2: Literal[{"description": "Enable level 2 authentication send-only", "help": "Enable level 2 authentication send-only.", "label": "Enable", "name": "enable"}, {"description": "Disable level 2 authentication send-only", "help": "Disable level 2 authentication send-only.", "label": "Disable", "name": "disable"}]
VALID_BODY_IGNORE_LSP_ERRORS: Literal[{"description": "Enable ignoring of LSP errors with bad checksums", "help": "Enable ignoring of LSP errors with bad checksums.", "label": "Enable", "name": "enable"}, {"description": "Disable ignoring of LSP errors with bad checksums", "help": "Disable ignoring of LSP errors with bad checksums.", "label": "Disable", "name": "disable"}]
VALID_BODY_DYNAMIC_HOSTNAME: Literal[{"description": "Enable dynamic hostname", "help": "Enable dynamic hostname.", "label": "Enable", "name": "enable"}, {"description": "Disable dynamic hostname", "help": "Disable dynamic hostname.", "label": "Disable", "name": "disable"}]
VALID_BODY_ADJACENCY_CHECK: Literal[{"description": "Enable adjacency check", "help": "Enable adjacency check.", "label": "Enable", "name": "enable"}, {"description": "Disable adjacency check", "help": "Disable adjacency check.", "label": "Disable", "name": "disable"}]
VALID_BODY_ADJACENCY_CHECK6: Literal[{"description": "Enable IPv6 adjacency check", "help": "Enable IPv6 adjacency check.", "label": "Enable", "name": "enable"}, {"description": "Disable IPv6 adjacency check", "help": "Disable IPv6 adjacency check.", "label": "Disable", "name": "disable"}]
VALID_BODY_OVERLOAD_BIT: Literal[{"description": "Enable overload bit", "help": "Enable overload bit.", "label": "Enable", "name": "enable"}, {"description": "Disable overload bit", "help": "Disable overload bit.", "label": "Disable", "name": "disable"}]
VALID_BODY_OVERLOAD_BIT_SUPPRESS: Literal[{"description": "External", "help": "External.", "label": "External", "name": "external"}, {"description": "Inter-level", "help": "Inter-level.", "label": "Interlevel", "name": "interlevel"}]
VALID_BODY_DEFAULT_ORIGINATE: Literal[{"description": "Enable distribution of default route information", "help": "Enable distribution of default route information.", "label": "Enable", "name": "enable"}, {"description": "Disable distribution of default route information", "help": "Disable distribution of default route information.", "label": "Disable", "name": "disable"}]
VALID_BODY_DEFAULT_ORIGINATE6: Literal[{"description": "Enable distribution of default IPv6 route information", "help": "Enable distribution of default IPv6 route information.", "label": "Enable", "name": "enable"}, {"description": "Disable distribution of default IPv6 route information", "help": "Disable distribution of default IPv6 route information.", "label": "Disable", "name": "disable"}]
VALID_BODY_METRIC_STYLE: Literal[{"description": "Use old style of TLVs with narrow metric", "help": "Use old style of TLVs with narrow metric.", "label": "Narrow", "name": "narrow"}, {"description": "Use new style of TLVs to carry wider metric", "help": "Use new style of TLVs to carry wider metric.", "label": "Wide", "name": "wide"}, {"description": "Send and accept both styles of TLVs during transition", "help": "Send and accept both styles of TLVs during transition.", "label": "Transition", "name": "transition"}, {"description": "Narrow and accept both styles of TLVs during transition", "help": "Narrow and accept both styles of TLVs during transition.", "label": "Narrow Transition", "name": "narrow-transition"}, {"description": "Narrow-transition level-1 only", "help": "Narrow-transition level-1 only.", "label": "Narrow Transition L1", "name": "narrow-transition-l1"}, {"description": "Narrow-transition level-2 only", "help": "Narrow-transition level-2 only.", "label": "Narrow Transition L2", "name": "narrow-transition-l2"}, {"description": "Wide level-1 only", "help": "Wide level-1 only.", "label": "Wide L1", "name": "wide-l1"}, {"description": "Wide level-2 only", "help": "Wide level-2 only.", "label": "Wide L2", "name": "wide-l2"}, {"description": "Wide and accept both styles of TLVs during transition", "help": "Wide and accept both styles of TLVs during transition.", "label": "Wide Transition", "name": "wide-transition"}, {"description": "Wide-transition level-1 only", "help": "Wide-transition level-1 only.", "label": "Wide Transition L1", "name": "wide-transition-l1"}, {"description": "Wide-transition level-2 only", "help": "Wide-transition level-2 only.", "label": "Wide Transition L2", "name": "wide-transition-l2"}, {"description": "Transition level-1 only", "help": "Transition level-1 only.", "label": "Transition L1", "name": "transition-l1"}, {"description": "Transition level-2 only", "help": "Transition level-2 only.", "label": "Transition L2", "name": "transition-l2"}]
VALID_BODY_REDISTRIBUTE_L1: Literal[{"description": "Enable redistribution of level 1 routes into level 2", "help": "Enable redistribution of level 1 routes into level 2.", "label": "Enable", "name": "enable"}, {"description": "Disable redistribution of level 1 routes into level 2", "help": "Disable redistribution of level 1 routes into level 2.", "label": "Disable", "name": "disable"}]
VALID_BODY_REDISTRIBUTE_L2: Literal[{"description": "Enable redistribution of level 2 routes into level 1", "help": "Enable redistribution of level 2 routes into level 1.", "label": "Enable", "name": "enable"}, {"description": "Disable redistribution of  level 2 routes into level 1", "help": "Disable redistribution of  level 2 routes into level 1.", "label": "Disable", "name": "disable"}]
VALID_BODY_REDISTRIBUTE6_L1: Literal[{"description": "Enable redistribution of level 1 IPv6 routes into level 2", "help": "Enable redistribution of level 1 IPv6 routes into level 2.", "label": "Enable", "name": "enable"}, {"description": "Disable redistribution of level 1 IPv6 routes into level 2", "help": "Disable redistribution of level 1 IPv6 routes into level 2.", "label": "Disable", "name": "disable"}]
VALID_BODY_REDISTRIBUTE6_L2: Literal[{"description": "Enable redistribution of level 2 IPv6 routes into level 1", "help": "Enable redistribution of level 2 IPv6 routes into level 1.", "label": "Enable", "name": "enable"}, {"description": "Disable redistribution of level 2 IPv6 routes into level 1", "help": "Disable redistribution of level 2 IPv6 routes into level 1.", "label": "Disable", "name": "disable"}]

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
    "VALID_BODY_IS_TYPE",
    "VALID_BODY_ADV_PASSIVE_ONLY",
    "VALID_BODY_ADV_PASSIVE_ONLY6",
    "VALID_BODY_AUTH_MODE_L1",
    "VALID_BODY_AUTH_MODE_L2",
    "VALID_BODY_AUTH_SENDONLY_L1",
    "VALID_BODY_AUTH_SENDONLY_L2",
    "VALID_BODY_IGNORE_LSP_ERRORS",
    "VALID_BODY_DYNAMIC_HOSTNAME",
    "VALID_BODY_ADJACENCY_CHECK",
    "VALID_BODY_ADJACENCY_CHECK6",
    "VALID_BODY_OVERLOAD_BIT",
    "VALID_BODY_OVERLOAD_BIT_SUPPRESS",
    "VALID_BODY_DEFAULT_ORIGINATE",
    "VALID_BODY_DEFAULT_ORIGINATE6",
    "VALID_BODY_METRIC_STYLE",
    "VALID_BODY_REDISTRIBUTE_L1",
    "VALID_BODY_REDISTRIBUTE_L2",
    "VALID_BODY_REDISTRIBUTE6_L1",
    "VALID_BODY_REDISTRIBUTE6_L2",
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