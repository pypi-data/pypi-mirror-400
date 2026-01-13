from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_EXTENDED_LOG: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]
VALID_BODY_OTHER_APPLICATION_ACTION: Literal[{"description": "Allow sessions matching an application in this application list", "help": "Allow sessions matching an application in this application list.", "label": "Pass", "name": "pass"}, {"description": "Block sessions matching an application in this application list", "help": "Block sessions matching an application in this application list.", "label": "Block", "name": "block"}]
VALID_BODY_APP_REPLACEMSG: Literal[{"description": "Disable replacement messages for blocked applications", "help": "Disable replacement messages for blocked applications.", "label": "Disable", "name": "disable"}, {"description": "Enable replacement messages for blocked applications", "help": "Enable replacement messages for blocked applications.", "label": "Enable", "name": "enable"}]
VALID_BODY_OTHER_APPLICATION_LOG: Literal[{"description": "Disable logging for other applications", "help": "Disable logging for other applications.", "label": "Disable", "name": "disable"}, {"description": "Enable logging for other applications", "help": "Enable logging for other applications.", "label": "Enable", "name": "enable"}]
VALID_BODY_ENFORCE_DEFAULT_APP_PORT: Literal[{"description": "Disable default application port enforcement", "help": "Disable default application port enforcement.", "label": "Disable", "name": "disable"}, {"description": "Enable default application port enforcement", "help": "Enable default application port enforcement.", "label": "Enable", "name": "enable"}]
VALID_BODY_FORCE_INCLUSION_SSL_DI_SIGS: Literal[{"description": "Disable forced inclusion of signatures which normally require SSL deep inspection", "help": "Disable forced inclusion of signatures which normally require SSL deep inspection.", "label": "Disable", "name": "disable"}, {"description": "Enable forced inclusion of signatures which normally require SSL deep inspection", "help": "Enable forced inclusion of signatures which normally require SSL deep inspection.", "label": "Enable", "name": "enable"}]
VALID_BODY_UNKNOWN_APPLICATION_ACTION: Literal[{"description": "Pass or allow unknown applications", "help": "Pass or allow unknown applications.", "label": "Pass", "name": "pass"}, {"description": "Drop or block unknown applications", "help": "Drop or block unknown applications.", "label": "Block", "name": "block"}]
VALID_BODY_UNKNOWN_APPLICATION_LOG: Literal[{"description": "Disable logging for unknown applications", "help": "Disable logging for unknown applications.", "label": "Disable", "name": "disable"}, {"description": "Enable logging for unknown applications", "help": "Enable logging for unknown applications.", "label": "Enable", "name": "enable"}]
VALID_BODY_P2P_BLOCK_LIST: Literal[{"description": "Skype", "help": "Skype.", "label": "Skype", "name": "skype"}, {"description": "Edonkey", "help": "Edonkey.", "label": "Edonkey", "name": "edonkey"}, {"description": "Bit torrent", "help": "Bit torrent.", "label": "Bittorrent", "name": "bittorrent"}]
VALID_BODY_DEEP_APP_INSPECTION: Literal[{"description": "Disable deep application inspection", "help": "Disable deep application inspection.", "label": "Disable", "name": "disable"}, {"description": "Enable deep application inspection", "help": "Enable deep application inspection.", "label": "Enable", "name": "enable"}]
VALID_BODY_OPTIONS: Literal[{"description": "Allow DNS", "help": "Allow DNS.", "label": "Allow Dns", "name": "allow-dns"}, {"description": "Allow ICMP", "help": "Allow ICMP.", "label": "Allow Icmp", "name": "allow-icmp"}, {"description": "Allow generic HTTP web browsing", "help": "Allow generic HTTP web browsing.", "label": "Allow Http", "name": "allow-http"}, {"description": "Allow generic SSL communication", "help": "Allow generic SSL communication.", "label": "Allow Ssl", "name": "allow-ssl"}]
VALID_BODY_CONTROL_DEFAULT_NETWORK_SERVICES: Literal[{"description": "Disable protocol enforcement over selected ports", "help": "Disable protocol enforcement over selected ports.", "label": "Disable", "name": "disable"}, {"description": "Enable protocol enforcement over selected ports", "help": "Enable protocol enforcement over selected ports.", "label": "Enable", "name": "enable"}]

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
    "VALID_BODY_EXTENDED_LOG",
    "VALID_BODY_OTHER_APPLICATION_ACTION",
    "VALID_BODY_APP_REPLACEMSG",
    "VALID_BODY_OTHER_APPLICATION_LOG",
    "VALID_BODY_ENFORCE_DEFAULT_APP_PORT",
    "VALID_BODY_FORCE_INCLUSION_SSL_DI_SIGS",
    "VALID_BODY_UNKNOWN_APPLICATION_ACTION",
    "VALID_BODY_UNKNOWN_APPLICATION_LOG",
    "VALID_BODY_P2P_BLOCK_LIST",
    "VALID_BODY_DEEP_APP_INSPECTION",
    "VALID_BODY_OPTIONS",
    "VALID_BODY_CONTROL_DEFAULT_NETWORK_SERVICES",
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