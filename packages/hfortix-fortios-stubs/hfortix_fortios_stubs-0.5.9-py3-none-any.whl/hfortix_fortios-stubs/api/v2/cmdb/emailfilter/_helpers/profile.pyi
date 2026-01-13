from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_FEATURE_SET: Literal[{"description": "Flow feature set", "help": "Flow feature set.", "label": "Flow", "name": "flow"}, {"description": "Proxy feature set", "help": "Proxy feature set.", "label": "Proxy", "name": "proxy"}]
VALID_BODY_SPAM_LOG: Literal[{"description": "Disable spam logging for email filtering", "help": "Disable spam logging for email filtering.", "label": "Disable", "name": "disable"}, {"description": "Enable spam logging for email filtering", "help": "Enable spam logging for email filtering.", "label": "Enable", "name": "enable"}]
VALID_BODY_SPAM_LOG_FORTIGUARD_RESPONSE: Literal[{"description": "Disable logging FortiGuard spam response", "help": "Disable logging FortiGuard spam response.", "label": "Disable", "name": "disable"}, {"description": "Enable logging FortiGuard spam response", "help": "Enable logging FortiGuard spam response.", "label": "Enable", "name": "enable"}]
VALID_BODY_SPAM_FILTERING: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]
VALID_BODY_EXTERNAL: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]
VALID_BODY_OPTIONS: Literal[{"description": "Content block", "help": "Content block.", "label": "Bannedword", "name": "bannedword"}, {"description": "Block/allow list", "help": "Block/allow list.", "label": "Spambal", "name": "spambal"}, {"description": "Email IP address FortiGuard AntiSpam block list check", "help": "Email IP address FortiGuard AntiSpam block list check.", "label": "Spamfsip", "name": "spamfsip"}, {"description": "Add FortiGuard AntiSpam spam submission text", "help": "Add FortiGuard AntiSpam spam submission text.", "label": "Spamfssubmit", "name": "spamfssubmit"}, {"description": "Email checksum FortiGuard AntiSpam check", "help": "Email checksum FortiGuard AntiSpam check.", "label": "Spamfschksum", "name": "spamfschksum"}, {"description": "Email content URL FortiGuard AntiSpam check", "help": "Email content URL FortiGuard AntiSpam check.", "label": "Spamfsurl", "name": "spamfsurl"}, {"description": "Email helo/ehlo domain DNS check", "help": "Email helo/ehlo domain DNS check.", "label": "Spamhelodns", "name": "spamhelodns"}, {"description": "Email return address DNS check", "help": "Email return address DNS check.", "label": "Spamraddrdns", "name": "spamraddrdns"}, {"description": "Email DNSBL \u0026 ORBL check", "help": "Email DNSBL \u0026 ORBL check.", "label": "Spamrbl", "name": "spamrbl"}, {"description": "Email mime header check", "help": "Email mime header check.", "label": "Spamhdrcheck", "name": "spamhdrcheck"}, {"description": "Email content phishing URL FortiGuard AntiSpam check", "help": "Email content phishing URL FortiGuard AntiSpam check.", "label": "Spamfsphish", "name": "spamfsphish"}]

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
    "VALID_BODY_FEATURE_SET",
    "VALID_BODY_SPAM_LOG",
    "VALID_BODY_SPAM_LOG_FORTIGUARD_RESPONSE",
    "VALID_BODY_SPAM_FILTERING",
    "VALID_BODY_EXTERNAL",
    "VALID_BODY_OPTIONS",
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