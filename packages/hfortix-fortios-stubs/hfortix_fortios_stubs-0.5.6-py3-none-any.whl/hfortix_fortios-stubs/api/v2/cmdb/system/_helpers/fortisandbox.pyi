from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_STATUS: Literal[{"description": "Enable FortiSandbox", "help": "Enable FortiSandbox.", "label": "Enable", "name": "enable"}, {"description": "Disable FortiSandbox", "help": "Disable FortiSandbox.", "label": "Disable", "name": "disable"}]
VALID_BODY_FORTICLOUD: Literal[{"description": "Enable FortiSandbox Cloud", "help": "Enable FortiSandbox Cloud.", "label": "Enable", "name": "enable"}, {"description": "Disable FortiSandbox Cloud", "help": "Disable FortiSandbox Cloud.", "label": "Disable", "name": "disable"}]
VALID_BODY_INLINE_SCAN: Literal[{"help": "Enable FortiSandbox inline scan.", "label": "Enable", "name": "enable"}, {"help": "Disable FortiSandbox inline scan.", "label": "Disable", "name": "disable"}]
VALID_BODY_INTERFACE_SELECT_METHOD: Literal[{"description": "Set outgoing interface automatically", "help": "Set outgoing interface automatically.", "label": "Auto", "name": "auto"}, {"description": "Set outgoing interface by SD-WAN or policy routing rules", "help": "Set outgoing interface by SD-WAN or policy routing rules.", "label": "Sdwan", "name": "sdwan"}, {"description": "Set outgoing interface manually", "help": "Set outgoing interface manually.", "label": "Specify", "name": "specify"}]
VALID_BODY_ENC_ALGORITHM: Literal[{"description": "SSL communication with high and medium encryption algorithms", "help": "SSL communication with high and medium encryption algorithms.", "label": "Default", "name": "default"}, {"description": "SSL communication with high encryption algorithms", "help": "SSL communication with high encryption algorithms.", "label": "High", "name": "high"}, {"description": "SSL communication with low encryption algorithms", "help": "SSL communication with low encryption algorithms.", "label": "Low", "name": "low"}]
VALID_BODY_SSL_MIN_PROTO_VERSION: Literal[{"description": "Follow system global setting", "help": "Follow system global setting.", "label": "Default", "name": "default"}, {"description": "SSLv3", "help": "SSLv3.", "label": "Sslv3", "name": "SSLv3"}, {"description": "TLSv1", "help": "TLSv1.", "label": "Tlsv1", "name": "TLSv1"}, {"description": "TLSv1", "help": "TLSv1.1.", "label": "Tlsv1 1", "name": "TLSv1-1"}, {"description": "TLSv1", "help": "TLSv1.2.", "label": "Tlsv1 2", "name": "TLSv1-2"}, {"description": "TLSv1", "help": "TLSv1.3.", "label": "Tlsv1 3", "name": "TLSv1-3"}]
VALID_BODY_CERTIFICATE_VERIFICATION: Literal[{"description": "Enable identity verification of FortiSandbox by use of certificate", "help": "Enable identity verification of FortiSandbox by use of certificate.", "label": "Enable", "name": "enable"}, {"description": "Disable identity verification of FortiSandbox by use of certificate", "help": "Disable identity verification of FortiSandbox by use of certificate.", "label": "Disable", "name": "disable"}]

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
    "VALID_BODY_STATUS",
    "VALID_BODY_FORTICLOUD",
    "VALID_BODY_INLINE_SCAN",
    "VALID_BODY_INTERFACE_SELECT_METHOD",
    "VALID_BODY_ENC_ALGORITHM",
    "VALID_BODY_SSL_MIN_PROTO_VERSION",
    "VALID_BODY_CERTIFICATE_VERIFICATION",
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