from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_USE_MANAGEMENT_VDOM: Literal[{"description": "Enable use of management VDOM IP address as source IP for logs sent to FortiAnalyzer", "help": "Enable use of management VDOM IP address as source IP for logs sent to FortiAnalyzer.", "label": "Enable", "name": "enable"}, {"description": "Disable use of management VDOM IP address as source IP for logs sent to FortiAnalyzer", "help": "Disable use of management VDOM IP address as source IP for logs sent to FortiAnalyzer.", "label": "Disable", "name": "disable"}]
VALID_BODY_STATUS: Literal[{"description": "Enable logging to FortiAnalyzer", "help": "Enable logging to FortiAnalyzer.", "label": "Enable", "name": "enable"}, {"description": "Disable logging to FortiAnalyzer", "help": "Disable logging to FortiAnalyzer.", "label": "Disable", "name": "disable"}]
VALID_BODY_IPS_ARCHIVE: Literal[{"description": "Enable IPS packet archive logging", "help": "Enable IPS packet archive logging.", "label": "Enable", "name": "enable"}, {"description": "Disable IPS packet archive logging", "help": "Disable IPS packet archive logging.", "label": "Disable", "name": "disable"}]
VALID_BODY_FALLBACK_TO_PRIMARY: Literal[{"description": "Enable this FortiGate unit to fallback to the primary FortiAnalyzer when it is available", "help": "Enable this FortiGate unit to fallback to the primary FortiAnalyzer when it is available.", "label": "Enable", "name": "enable"}, {"description": "Disable this FortiGate unit to fallback to the primary FortiAnalyzer when it is available", "help": "Disable this FortiGate unit to fallback to the primary FortiAnalyzer when it is available.", "label": "Disable", "name": "disable"}]
VALID_BODY_CERTIFICATE_VERIFICATION: Literal[{"description": "Enable identity verification of FortiAnalyzer by use of certificate", "help": "Enable identity verification of FortiAnalyzer by use of certificate.", "label": "Enable", "name": "enable"}, {"description": "Disable identity verification of FortiAnalyzer by use of certificate", "help": "Disable identity verification of FortiAnalyzer by use of certificate.", "label": "Disable", "name": "disable"}]
VALID_BODY_ACCESS_CONFIG: Literal[{"description": "Enable FortiAnalyzer access to configuration and data", "help": "Enable FortiAnalyzer access to configuration and data.", "label": "Enable", "name": "enable"}, {"description": "Disable FortiAnalyzer access to configuration and data", "help": "Disable FortiAnalyzer access to configuration and data.", "label": "Disable", "name": "disable"}]
VALID_BODY_HMAC_ALGORITHM: Literal[{"description": "Use SHA256 as HMAC algorithm", "help": "Use SHA256 as HMAC algorithm.", "label": "Sha256", "name": "sha256"}]
VALID_BODY_ENC_ALGORITHM: Literal[{"description": "Encrypt logs using high and medium encryption algorithms", "help": "Encrypt logs using high and medium encryption algorithms.", "label": "High Medium", "name": "high-medium"}, {"description": "Encrypt logs using high encryption algorithms", "help": "Encrypt logs using high encryption algorithms.", "label": "High", "name": "high"}, {"description": "Encrypt logs using all encryption algorithms", "help": "Encrypt logs using all encryption algorithms.", "label": "Low", "name": "low"}]
VALID_BODY_SSL_MIN_PROTO_VERSION: Literal[{"description": "Follow system global setting", "help": "Follow system global setting.", "label": "Default", "name": "default"}, {"description": "SSLv3", "help": "SSLv3.", "label": "Sslv3", "name": "SSLv3"}, {"description": "TLSv1", "help": "TLSv1.", "label": "Tlsv1", "name": "TLSv1"}, {"description": "TLSv1", "help": "TLSv1.1.", "label": "Tlsv1 1", "name": "TLSv1-1"}, {"description": "TLSv1", "help": "TLSv1.2.", "label": "Tlsv1 2", "name": "TLSv1-2"}, {"description": "TLSv1", "help": "TLSv1.3.", "label": "Tlsv1 3", "name": "TLSv1-3"}]
VALID_BODY_UPLOAD_OPTION: Literal[{"description": "Log to hard disk and then upload to FortiAnalyzer", "help": "Log to hard disk and then upload to FortiAnalyzer.", "label": "Store And Upload", "name": "store-and-upload"}, {"description": "Log directly to FortiAnalyzer in real time", "help": "Log directly to FortiAnalyzer in real time.", "label": "Realtime", "name": "realtime"}, {"description": "Log directly to FortiAnalyzer at least every 1 minute", "help": "Log directly to FortiAnalyzer at least every 1 minute.", "label": "1 Minute", "name": "1-minute"}, {"description": "Log directly to FortiAnalyzer at least every 5 minutes", "help": "Log directly to FortiAnalyzer at least every 5 minutes.", "label": "5 Minute", "name": "5-minute"}]
VALID_BODY_UPLOAD_INTERVAL: Literal[{"description": "Upload log files to FortiAnalyzer once a day", "help": "Upload log files to FortiAnalyzer once a day.", "label": "Daily", "name": "daily"}, {"description": "Upload log files to FortiAnalyzer once a week", "help": "Upload log files to FortiAnalyzer once a week.", "label": "Weekly", "name": "weekly"}, {"description": "Upload log files to FortiAnalyzer once a month", "help": "Upload log files to FortiAnalyzer once a month.", "label": "Monthly", "name": "monthly"}]
VALID_BODY_RELIABLE: Literal[{"description": "Enable reliable logging to FortiAnalyzer", "help": "Enable reliable logging to FortiAnalyzer.", "label": "Enable", "name": "enable"}, {"description": "Disable reliable logging to FortiAnalyzer", "help": "Disable reliable logging to FortiAnalyzer.", "label": "Disable", "name": "disable"}]
VALID_BODY_PRIORITY: Literal[{"description": "Set FortiAnalyzer log transmission priority to default", "help": "Set FortiAnalyzer log transmission priority to default.", "label": "Default", "name": "default"}, {"description": "Set FortiAnalyzer log transmission priority to low", "help": "Set FortiAnalyzer log transmission priority to low.", "label": "Low", "name": "low"}]
VALID_BODY_INTERFACE_SELECT_METHOD: Literal[{"description": "Set outgoing interface automatically", "help": "Set outgoing interface automatically.", "label": "Auto", "name": "auto"}, {"description": "Set outgoing interface by SD-WAN or policy routing rules", "help": "Set outgoing interface by SD-WAN or policy routing rules.", "label": "Sdwan", "name": "sdwan"}, {"description": "Set outgoing interface manually", "help": "Set outgoing interface manually.", "label": "Specify", "name": "specify"}]

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
    "VALID_BODY_USE_MANAGEMENT_VDOM",
    "VALID_BODY_STATUS",
    "VALID_BODY_IPS_ARCHIVE",
    "VALID_BODY_FALLBACK_TO_PRIMARY",
    "VALID_BODY_CERTIFICATE_VERIFICATION",
    "VALID_BODY_ACCESS_CONFIG",
    "VALID_BODY_HMAC_ALGORITHM",
    "VALID_BODY_ENC_ALGORITHM",
    "VALID_BODY_SSL_MIN_PROTO_VERSION",
    "VALID_BODY_UPLOAD_OPTION",
    "VALID_BODY_UPLOAD_INTERVAL",
    "VALID_BODY_RELIABLE",
    "VALID_BODY_PRIORITY",
    "VALID_BODY_INTERFACE_SELECT_METHOD",
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