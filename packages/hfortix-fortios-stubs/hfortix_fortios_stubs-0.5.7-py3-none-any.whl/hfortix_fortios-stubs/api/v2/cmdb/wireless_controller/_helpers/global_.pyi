from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_IMAGE_DOWNLOAD: Literal[{"description": "Enable WTP image download at join time", "help": "Enable WTP image download at join time.", "label": "Enable", "name": "enable"}, {"description": "Disable WTP image download at join time", "help": "Disable WTP image download at join time.", "label": "Disable", "name": "disable"}]
VALID_BODY_ROLLING_WTP_UPGRADE: Literal[{"description": "Enable rolling WTP upgrade", "help": "Enable rolling WTP upgrade.", "label": "Enable", "name": "enable"}, {"description": "Disable rolling WTP upgrade", "help": "Disable rolling WTP upgrade.", "label": "Disable", "name": "disable"}]
VALID_BODY_CONTROL_MESSAGE_OFFLOAD: Literal[{"description": "Ekahau blink protocol (EBP) frames", "help": "Ekahau blink protocol (EBP) frames.", "label": "Ebp Frame", "name": "ebp-frame"}, {"description": "AeroScout tag", "help": "AeroScout tag.", "label": "Aeroscout Tag", "name": "aeroscout-tag"}, {"description": "Rogue AP list", "help": "Rogue AP list.", "label": "Ap List", "name": "ap-list"}, {"description": "Rogue STA list", "help": "Rogue STA list.", "label": "Sta List", "name": "sta-list"}, {"description": "STA capability list", "help": "STA capability list.", "label": "Sta Cap List", "name": "sta-cap-list"}, {"description": "WTP, radio, VAP, and STA statistics", "help": "WTP, radio, VAP, and STA statistics.", "label": "Stats", "name": "stats"}, {"description": "AeroScout Mobile Unit (MU) report", "help": "AeroScout Mobile Unit (MU) report.", "label": "Aeroscout Mu", "name": "aeroscout-mu"}, {"description": "STA health log", "help": "STA health log.", "label": "Sta Health", "name": "sta-health"}, {"description": "Spectral analysis report", "help": "Spectral analysis report.", "label": "Spectral Analysis", "name": "spectral-analysis"}]
VALID_BODY_DATA_ETHERNET_II: Literal[{"description": "Use Ethernet II frames with 802", "help": "Use Ethernet II frames with 802.3 data tunnel mode.", "label": "Enable", "name": "enable"}, {"description": "Use 802", "help": "Use 802.3 Ethernet frames with 802.3 data tunnel mode.", "label": "Disable", "name": "disable"}]
VALID_BODY_LINK_AGGREGATION: Literal[{"description": "Enable calculating the CAPWAP transmit hash", "help": "Enable calculating the CAPWAP transmit hash.", "label": "Enable", "name": "enable"}, {"description": "Disable calculating the CAPWAP transmit hash", "help": "Disable calculating the CAPWAP transmit hash.", "label": "Disable", "name": "disable"}]
VALID_BODY_WTP_SHARE: Literal[{"description": "WTP can be shared between all VDOMs", "help": "WTP can be shared between all VDOMs.", "label": "Enable", "name": "enable"}, {"description": "WTP can be used only in its own VDOM", "help": "WTP can be used only in its own VDOM.", "label": "Disable", "name": "disable"}]
VALID_BODY_TUNNEL_MODE: Literal[{"description": "Allow for backward compatible ciphers(3DES+SHA1+Strong list)", "help": "Allow for backward compatible ciphers(3DES+SHA1+Strong list).", "label": "Compatible", "name": "compatible"}, {"description": "Follow system level strong-crypto ciphers", "help": "Follow system level strong-crypto ciphers.", "label": "Strict", "name": "strict"}]
VALID_BODY_AP_LOG_SERVER: Literal[{"description": "Enable AP log server", "help": "Enable AP log server.", "label": "Enable", "name": "enable"}, {"description": "Disable AP log server", "help": "Disable AP log server.", "label": "Disable", "name": "disable"}]

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
    "VALID_BODY_IMAGE_DOWNLOAD",
    "VALID_BODY_ROLLING_WTP_UPGRADE",
    "VALID_BODY_CONTROL_MESSAGE_OFFLOAD",
    "VALID_BODY_DATA_ETHERNET_II",
    "VALID_BODY_LINK_AGGREGATION",
    "VALID_BODY_WTP_SHARE",
    "VALID_BODY_TUNNEL_MODE",
    "VALID_BODY_AP_LOG_SERVER",
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