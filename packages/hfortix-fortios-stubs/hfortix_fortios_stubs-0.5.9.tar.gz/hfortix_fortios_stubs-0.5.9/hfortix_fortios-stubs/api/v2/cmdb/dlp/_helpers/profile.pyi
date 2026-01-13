from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_FEATURE_SET: Literal[{"description": "Flow feature set", "help": "Flow feature set.", "label": "Flow", "name": "flow"}, {"description": "Proxy feature set", "help": "Proxy feature set.", "label": "Proxy", "name": "proxy"}]
VALID_BODY_DLP_LOG: Literal[{"description": "Enable DLP logging", "help": "Enable DLP logging.", "label": "Enable", "name": "enable"}, {"description": "Disable DLP logging", "help": "Disable DLP logging.", "label": "Disable", "name": "disable"}]
VALID_BODY_EXTENDED_LOG: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]
VALID_BODY_NAC_QUAR_LOG: Literal[{"description": "Enable NAC quarantine logging", "help": "Enable NAC quarantine logging.", "label": "Enable", "name": "enable"}, {"description": "Disable NAC quarantine logging", "help": "Disable NAC quarantine logging.", "label": "Disable", "name": "disable"}]
VALID_BODY_FULL_ARCHIVE_PROTO: Literal[{"description": "SMTP", "help": "SMTP.", "label": "Smtp", "name": "smtp"}, {"description": "POP3", "help": "POP3.", "label": "Pop3", "name": "pop3"}, {"description": "IMAP", "help": "IMAP.", "label": "Imap", "name": "imap"}, {"description": "HTTP GET", "help": "HTTP GET.", "label": "Http Get", "name": "http-get"}, {"description": "HTTP POST", "help": "HTTP POST.", "label": "Http Post", "name": "http-post"}, {"description": "FTP", "help": "FTP.", "label": "Ftp", "name": "ftp"}, {"description": "NNTP", "help": "NNTP.", "label": "Nntp", "name": "nntp"}, {"description": "MAPI", "help": "MAPI.", "label": "Mapi", "name": "mapi"}, {"description": "SFTP and SCP", "help": "SFTP and SCP.", "label": "Ssh", "name": "ssh"}, {"description": "CIFS", "help": "CIFS.", "label": "Cifs", "name": "cifs"}]
VALID_BODY_SUMMARY_PROTO: Literal[{"description": "SMTP", "help": "SMTP.", "label": "Smtp", "name": "smtp"}, {"description": "POP3", "help": "POP3.", "label": "Pop3", "name": "pop3"}, {"description": "IMAP", "help": "IMAP.", "label": "Imap", "name": "imap"}, {"description": "HTTP GET", "help": "HTTP GET.", "label": "Http Get", "name": "http-get"}, {"description": "HTTP POST", "help": "HTTP POST.", "label": "Http Post", "name": "http-post"}, {"description": "FTP", "help": "FTP.", "label": "Ftp", "name": "ftp"}, {"description": "NNTP", "help": "NNTP.", "label": "Nntp", "name": "nntp"}, {"description": "MAPI", "help": "MAPI.", "label": "Mapi", "name": "mapi"}, {"description": "SFTP and SCP", "help": "SFTP and SCP.", "label": "Ssh", "name": "ssh"}, {"description": "CIFS", "help": "CIFS.", "label": "Cifs", "name": "cifs"}]
VALID_BODY_FORTIDATA_ERROR_ACTION: Literal[{"description": "Log failure, but allow the file", "help": "Log failure, but allow the file.", "label": "Log Only", "name": "log-only"}, {"description": "Block the file", "help": "Block the file.", "label": "Block", "name": "block"}, {"description": "Behave as if FortiData returned no match", "help": "Behave as if FortiData returned no match.", "label": "Ignore", "name": "ignore"}]

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
    "VALID_BODY_DLP_LOG",
    "VALID_BODY_EXTENDED_LOG",
    "VALID_BODY_NAC_QUAR_LOG",
    "VALID_BODY_FULL_ARCHIVE_PROTO",
    "VALID_BODY_SUMMARY_PROTO",
    "VALID_BODY_FORTIDATA_ERROR_ACTION",
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