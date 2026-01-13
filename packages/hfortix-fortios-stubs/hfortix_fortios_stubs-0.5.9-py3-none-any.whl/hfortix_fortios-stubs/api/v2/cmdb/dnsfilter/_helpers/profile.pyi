from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_LOG_ALL_DOMAIN: Literal[{"description": "Enable logging of all domains visited", "help": "Enable logging of all domains visited.", "label": "Enable", "name": "enable"}, {"description": "Disable logging of all domains visited", "help": "Disable logging of all domains visited.", "label": "Disable", "name": "disable"}]
VALID_BODY_SDNS_FTGD_ERR_LOG: Literal[{"description": "Enable FortiGuard SDNS rating error logging", "help": "Enable FortiGuard SDNS rating error logging.", "label": "Enable", "name": "enable"}, {"description": "Disable FortiGuard SDNS rating error logging", "help": "Disable FortiGuard SDNS rating error logging.", "label": "Disable", "name": "disable"}]
VALID_BODY_SDNS_DOMAIN_LOG: Literal[{"description": "Enable domain filtering and botnet domain logging", "help": "Enable domain filtering and botnet domain logging.", "label": "Enable", "name": "enable"}, {"description": "Disable domain filtering and botnet domain logging", "help": "Disable domain filtering and botnet domain logging.", "label": "Disable", "name": "disable"}]
VALID_BODY_BLOCK_ACTION: Literal[{"description": "Return NXDOMAIN for blocked domains", "help": "Return NXDOMAIN for blocked domains.", "label": "Block", "name": "block"}, {"description": "Redirect blocked domains to SDNS portal", "help": "Redirect blocked domains to SDNS portal.", "label": "Redirect", "name": "redirect"}, {"description": "Return SERVFAIL for blocked domains", "help": "Return SERVFAIL for blocked domains.", "label": "Block Sevrfail", "name": "block-sevrfail"}]
VALID_BODY_BLOCK_BOTNET: Literal[{"description": "Disable blocking botnet C\u0026C DNS lookups", "help": "Disable blocking botnet C\u0026C DNS lookups.", "label": "Disable", "name": "disable"}, {"description": "Enable blocking botnet C\u0026C DNS lookups", "help": "Enable blocking botnet C\u0026C DNS lookups.", "label": "Enable", "name": "enable"}]
VALID_BODY_SAFE_SEARCH: Literal[{"description": "Disable Google, Bing, YouTube, Qwant, DuckDuckGo safe search", "help": "Disable Google, Bing, YouTube, Qwant, DuckDuckGo safe search.", "label": "Disable", "name": "disable"}, {"description": "Enable Google, Bing, YouTube, Qwant, DuckDuckGo safe search", "help": "Enable Google, Bing, YouTube, Qwant, DuckDuckGo safe search.", "label": "Enable", "name": "enable"}]
VALID_BODY_YOUTUBE_RESTRICT: Literal[{"description": "Enable strict safe seach for YouTube", "help": "Enable strict safe seach for YouTube.", "label": "Strict", "name": "strict"}, {"description": "Enable moderate safe search for YouTube", "help": "Enable moderate safe search for YouTube.", "label": "Moderate", "name": "moderate"}, {"description": "Disable safe search for YouTube", "help": "Disable safe search for YouTube.", "label": "None", "name": "none"}]
VALID_BODY_STRIP_ECH: Literal[{"description": "Disable removal of the encrypted client hello service parameter from supporting DNS RRs", "help": "Disable removal of the encrypted client hello service parameter from supporting DNS RRs.", "label": "Disable", "name": "disable"}, {"description": "Enable removal of the encrypted client hello service parameter from supporting DNS RRs", "help": "Enable removal of the encrypted client hello service parameter from supporting DNS RRs.", "label": "Enable", "name": "enable"}]

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
    "VALID_BODY_LOG_ALL_DOMAIN",
    "VALID_BODY_SDNS_FTGD_ERR_LOG",
    "VALID_BODY_SDNS_DOMAIN_LOG",
    "VALID_BODY_BLOCK_ACTION",
    "VALID_BODY_BLOCK_BOTNET",
    "VALID_BODY_SAFE_SEARCH",
    "VALID_BODY_YOUTUBE_RESTRICT",
    "VALID_BODY_STRIP_ECH",
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