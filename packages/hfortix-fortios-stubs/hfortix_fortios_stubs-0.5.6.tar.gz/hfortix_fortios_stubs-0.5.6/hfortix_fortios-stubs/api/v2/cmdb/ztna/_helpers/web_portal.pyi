from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_LOG_BLOCKED_TRAFFIC: Literal[{"description": "Do not log all traffic denied by this ZTNA web-proxy", "help": "Do not log all traffic denied by this ZTNA web-proxy.", "label": "Disable", "name": "disable"}, {"description": "Log all traffic denied by this ZTNA web-proxy", "help": "Log all traffic denied by this ZTNA web-proxy.", "label": "Enable", "name": "enable"}]
VALID_BODY_AUTH_PORTAL: Literal[{"description": "Disable authentication portal", "help": "Disable authentication portal.", "label": "Disable", "name": "disable"}, {"description": "Enable authentication portal", "help": "Enable authentication portal.", "label": "Enable", "name": "enable"}]
VALID_BODY_DISPLAY_BOOKMARK: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]
VALID_BODY_FOCUS_BOOKMARK: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]
VALID_BODY_DISPLAY_STATUS: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]
VALID_BODY_DISPLAY_HISTORY: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]
VALID_BODY_POLICY_AUTH_SSO: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]
VALID_BODY_THEME: Literal[{"description": "Jade theme", "help": "Jade theme.", "label": "Jade", "name": "jade"}, {"description": "Neutrino theme", "help": "Neutrino theme.", "label": "Neutrino", "name": "neutrino"}, {"description": "Mariner theme", "help": "Mariner theme.", "label": "Mariner", "name": "mariner"}, {"description": "Graphite theme", "help": "Graphite theme.", "label": "Graphite", "name": "graphite"}, {"description": "Melongene theme", "help": "Melongene theme.", "label": "Melongene", "name": "melongene"}, {"description": "Jet Stream theme", "help": "Jet Stream theme.", "label": "Jet Stream", "name": "jet-stream"}, {"description": "Security Fabric theme", "help": "Security Fabric theme.", "label": "Security Fabric", "name": "security-fabric"}, {"description": "Dark Matter theme", "help": "Dark Matter theme.", "label": "Dark Matter", "name": "dark-matter"}, {"description": "Onyx theme", "help": "Onyx theme.", "label": "Onyx", "name": "onyx"}, {"description": "Eclipse theme", "help": "Eclipse theme.", "label": "Eclipse", "name": "eclipse"}]
VALID_BODY_CLIPBOARD: Literal[{"description": "Enable support of RDP/VNC clipboard", "help": "Enable support of RDP/VNC clipboard.", "label": "Enable", "name": "enable"}, {"description": "Disable support of RDP/VNC clipboard", "help": "Disable support of RDP/VNC clipboard.", "label": "Disable", "name": "disable"}]
VALID_BODY_FORTICLIENT_DOWNLOAD: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]
VALID_BODY_CUSTOMIZE_FORTICLIENT_DOWNLOAD_URL: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]

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
    "VALID_BODY_LOG_BLOCKED_TRAFFIC",
    "VALID_BODY_AUTH_PORTAL",
    "VALID_BODY_DISPLAY_BOOKMARK",
    "VALID_BODY_FOCUS_BOOKMARK",
    "VALID_BODY_DISPLAY_STATUS",
    "VALID_BODY_DISPLAY_HISTORY",
    "VALID_BODY_POLICY_AUTH_SSO",
    "VALID_BODY_THEME",
    "VALID_BODY_CLIPBOARD",
    "VALID_BODY_FORTICLIENT_DOWNLOAD",
    "VALID_BODY_CUSTOMIZE_FORTICLIENT_DOWNLOAD_URL",
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