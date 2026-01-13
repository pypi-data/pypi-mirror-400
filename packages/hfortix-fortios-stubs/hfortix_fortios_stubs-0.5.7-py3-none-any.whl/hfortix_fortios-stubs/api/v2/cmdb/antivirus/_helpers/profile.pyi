from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_FEATURE_SET: Literal[{"description": "Flow feature set", "help": "Flow feature set.", "label": "Flow", "name": "flow"}, {"description": "Proxy feature set", "help": "Proxy feature set.", "label": "Proxy", "name": "proxy"}]
VALID_BODY_FORTISANDBOX_MODE: Literal[{"help": "FortiSandbox inline scan.", "label": "Inline", "name": "inline"}, {"description": "FortiSandbox post-transfer scan: submit supported files if heuristics or other methods determine they are suspicious", "help": "FortiSandbox post-transfer scan: submit supported files if heuristics or other methods determine they are suspicious.", "label": "Analytics Suspicious", "name": "analytics-suspicious"}, {"description": "FortiSandbox post-transfer scan: submit supported files for inspection", "help": "FortiSandbox post-transfer scan: submit supported files for inspection.", "label": "Analytics Everything", "name": "analytics-everything"}]
VALID_BODY_ANALYTICS_DB: Literal[{"description": "Use only the standard AV signature databases", "help": "Use only the standard AV signature databases.", "label": "Disable", "name": "disable"}, {"description": "Also use the FortiSandbox signature database", "help": "Also use the FortiSandbox signature database.", "label": "Enable", "name": "enable"}]
VALID_BODY_MOBILE_MALWARE_DB: Literal[{"description": "Do not use the mobile malware signature database", "help": "Do not use the mobile malware signature database.", "label": "Disable", "name": "disable"}, {"description": "Also use the mobile malware signature database", "help": "Also use the mobile malware signature database.", "label": "Enable", "name": "enable"}]
VALID_BODY_OUTBREAK_PREVENTION_ARCHIVE_SCAN: Literal[{"description": "Analyze files as sent, not the content of archives", "help": "Analyze files as sent, not the content of archives.", "label": "Disable", "name": "disable"}, {"description": "Analyze files including the content of archives", "help": "Analyze files including the content of archives.", "label": "Enable", "name": "enable"}]
VALID_BODY_EXTERNAL_BLOCKLIST_ENABLE_ALL: Literal[{"description": "Use configured external blocklists", "help": "Use configured external blocklists.", "label": "Disable", "name": "disable"}, {"description": "Enable all external blocklists", "help": "Enable all external blocklists.", "label": "Enable", "name": "enable"}]
VALID_BODY_EMS_THREAT_FEED: Literal[{"description": "Disable use of EMS threat feed when performing AntiVirus scan", "help": "Disable use of EMS threat feed when performing AntiVirus scan.", "label": "Disable", "name": "disable"}, {"description": "Enable use of EMS threat feed when performing AntiVirus scan", "help": "Enable use of EMS threat feed when performing AntiVirus scan.", "label": "Enable", "name": "enable"}]
VALID_BODY_FORTINDR_ERROR_ACTION: Literal[{"help": "Log FortiNDR error, but allow the file.", "label": "Log Only", "name": "log-only"}, {"help": "Block the file on FortiNDR error.", "label": "Block", "name": "block"}, {"help": "Do nothing on FortiNDR error.", "label": "Ignore", "name": "ignore"}]
VALID_BODY_FORTINDR_TIMEOUT_ACTION: Literal[{"help": "Log FortiNDR scan timeout, but allow the file.", "label": "Log Only", "name": "log-only"}, {"help": "Block the file on FortiNDR scan timeout.", "label": "Block", "name": "block"}, {"help": "Do nothing on FortiNDR scan timeout.", "label": "Ignore", "name": "ignore"}]
VALID_BODY_FORTISANDBOX_ERROR_ACTION: Literal[{"help": "Log FortiSandbox inline scan error, but allow the file.", "label": "Log Only", "name": "log-only"}, {"help": "Block the file on FortiSandbox inline scan error.", "label": "Block", "name": "block"}, {"help": "Do nothing on FortiSandbox inline scan error.", "label": "Ignore", "name": "ignore"}]
VALID_BODY_FORTISANDBOX_TIMEOUT_ACTION: Literal[{"help": "Log FortiSandbox inline scan timeout, but allow the file.", "label": "Log Only", "name": "log-only"}, {"help": "Block the file on FortiSandbox inline scan timeout.", "label": "Block", "name": "block"}, {"help": "Do nothing on FortiSandbox inline scan timeout.", "label": "Ignore", "name": "ignore"}]
VALID_BODY_AV_VIRUS_LOG: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]
VALID_BODY_EXTENDED_LOG: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]
VALID_BODY_SCAN_MODE: Literal[{"description": "On the fly decompression and scanning of certain archive files", "help": "On the fly decompression and scanning of certain archive files.", "label": "Default", "name": "default"}, {"description": "Scan archive files only after the entire file is received", "help": "Scan archive files only after the entire file is received.", "label": "Legacy", "name": "legacy"}]

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
    "VALID_BODY_FORTISANDBOX_MODE",
    "VALID_BODY_ANALYTICS_DB",
    "VALID_BODY_MOBILE_MALWARE_DB",
    "VALID_BODY_OUTBREAK_PREVENTION_ARCHIVE_SCAN",
    "VALID_BODY_EXTERNAL_BLOCKLIST_ENABLE_ALL",
    "VALID_BODY_EMS_THREAT_FEED",
    "VALID_BODY_FORTINDR_ERROR_ACTION",
    "VALID_BODY_FORTINDR_TIMEOUT_ACTION",
    "VALID_BODY_FORTISANDBOX_ERROR_ACTION",
    "VALID_BODY_FORTISANDBOX_TIMEOUT_ACTION",
    "VALID_BODY_AV_VIRUS_LOG",
    "VALID_BODY_EXTENDED_LOG",
    "VALID_BODY_SCAN_MODE",
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