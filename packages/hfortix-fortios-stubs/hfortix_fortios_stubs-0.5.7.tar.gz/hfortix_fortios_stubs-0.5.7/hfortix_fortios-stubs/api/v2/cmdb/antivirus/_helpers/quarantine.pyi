from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_DROP_INFECTED: Literal[{"description": "IMAP", "help": "IMAP.", "label": "Imap", "name": "imap"}, {"description": "SMTP", "help": "SMTP.", "label": "Smtp", "name": "smtp"}, {"description": "POP3", "help": "POP3.", "label": "Pop3", "name": "pop3"}, {"description": "HTTP", "help": "HTTP.", "label": "Http", "name": "http"}, {"description": "FTP", "help": "FTP.", "label": "Ftp", "name": "ftp"}, {"description": "NNTP", "help": "NNTP.", "label": "Nntp", "name": "nntp"}, {"description": "IMAPS", "help": "IMAPS.", "label": "Imaps", "name": "imaps"}, {"description": "SMTPS", "help": "SMTPS.", "label": "Smtps", "name": "smtps"}, {"description": "POP3S", "help": "POP3S.", "label": "Pop3S", "name": "pop3s"}, {"description": "HTTPS", "help": "HTTPS.", "label": "Https", "name": "https"}, {"description": "FTPS", "help": "FTPS.", "label": "Ftps", "name": "ftps"}, {"description": "MAPI", "help": "MAPI.", "label": "Mapi", "name": "mapi"}, {"description": "CIFS", "help": "CIFS.", "label": "Cifs", "name": "cifs"}, {"description": "SSH", "help": "SSH.", "label": "Ssh", "name": "ssh"}]
VALID_BODY_STORE_INFECTED: Literal[{"description": "IMAP", "help": "IMAP.", "label": "Imap", "name": "imap"}, {"description": "SMTP", "help": "SMTP.", "label": "Smtp", "name": "smtp"}, {"description": "POP3", "help": "POP3.", "label": "Pop3", "name": "pop3"}, {"description": "HTTP", "help": "HTTP.", "label": "Http", "name": "http"}, {"description": "FTP", "help": "FTP.", "label": "Ftp", "name": "ftp"}, {"description": "NNTP", "help": "NNTP.", "label": "Nntp", "name": "nntp"}, {"description": "IMAPS", "help": "IMAPS.", "label": "Imaps", "name": "imaps"}, {"description": "SMTPS", "help": "SMTPS.", "label": "Smtps", "name": "smtps"}, {"description": "POP3S", "help": "POP3S.", "label": "Pop3S", "name": "pop3s"}, {"description": "HTTPS", "help": "HTTPS.", "label": "Https", "name": "https"}, {"description": "FTPS", "help": "FTPS.", "label": "Ftps", "name": "ftps"}, {"description": "MAPI", "help": "MAPI.", "label": "Mapi", "name": "mapi"}, {"description": "CIFS", "help": "CIFS.", "label": "Cifs", "name": "cifs"}, {"description": "SSH", "help": "SSH.", "label": "Ssh", "name": "ssh"}]
VALID_BODY_DROP_MACHINE_LEARNING: Literal[{"description": "IMAP", "help": "IMAP.", "label": "Imap", "name": "imap"}, {"description": "SMTP", "help": "SMTP.", "label": "Smtp", "name": "smtp"}, {"description": "POP3", "help": "POP3.", "label": "Pop3", "name": "pop3"}, {"description": "HTTP", "help": "HTTP.", "label": "Http", "name": "http"}, {"description": "FTP", "help": "FTP.", "label": "Ftp", "name": "ftp"}, {"description": "NNTP", "help": "NNTP.", "label": "Nntp", "name": "nntp"}, {"description": "IMAPS", "help": "IMAPS.", "label": "Imaps", "name": "imaps"}, {"description": "SMTPS", "help": "SMTPS.", "label": "Smtps", "name": "smtps"}, {"description": "POP3S", "help": "POP3S.", "label": "Pop3S", "name": "pop3s"}, {"description": "HTTPS", "help": "HTTPS.", "label": "Https", "name": "https"}, {"description": "FTPS", "help": "FTPS.", "label": "Ftps", "name": "ftps"}, {"description": "MAPI", "help": "MAPI.", "label": "Mapi", "name": "mapi"}, {"description": "CIFS", "help": "CIFS.", "label": "Cifs", "name": "cifs"}, {"description": "SSH", "help": "SSH.", "label": "Ssh", "name": "ssh"}]
VALID_BODY_STORE_MACHINE_LEARNING: Literal[{"description": "IMAP", "help": "IMAP.", "label": "Imap", "name": "imap"}, {"description": "SMTP", "help": "SMTP.", "label": "Smtp", "name": "smtp"}, {"description": "POP3", "help": "POP3.", "label": "Pop3", "name": "pop3"}, {"description": "HTTP", "help": "HTTP.", "label": "Http", "name": "http"}, {"description": "FTP", "help": "FTP.", "label": "Ftp", "name": "ftp"}, {"description": "NNTP", "help": "NNTP.", "label": "Nntp", "name": "nntp"}, {"description": "IMAPS", "help": "IMAPS.", "label": "Imaps", "name": "imaps"}, {"description": "SMTPS", "help": "SMTPS.", "label": "Smtps", "name": "smtps"}, {"description": "POP3S", "help": "POP3S.", "label": "Pop3S", "name": "pop3s"}, {"description": "HTTPS", "help": "HTTPS.", "label": "Https", "name": "https"}, {"description": "FTPS", "help": "FTPS.", "label": "Ftps", "name": "ftps"}, {"description": "MAPI", "help": "MAPI.", "label": "Mapi", "name": "mapi"}, {"description": "CIFS", "help": "CIFS.", "label": "Cifs", "name": "cifs"}, {"description": "SSH", "help": "SSH.", "label": "Ssh", "name": "ssh"}]
VALID_BODY_LOWSPACE: Literal[{"description": "Drop (delete) the most recently quarantined files", "help": "Drop (delete) the most recently quarantined files.", "label": "Drop New", "name": "drop-new"}, {"description": "Overwrite the oldest quarantined files", "help": "Overwrite the oldest quarantined files. That is, the files that are closest to being deleted from the quarantine.", "label": "Ovrw Old", "name": "ovrw-old"}]
VALID_BODY_DESTINATION: Literal[{"description": "Files that would be quarantined are deleted", "help": "Files that would be quarantined are deleted.", "label": "Null", "name": "NULL"}, {"description": "Quarantine files to the FortiGate hard disk", "help": "Quarantine files to the FortiGate hard disk.", "label": "Disk", "name": "disk"}, {"description": "FortiAnalyzer", "help": "FortiAnalyzer", "label": "Fortianalyzer", "name": "FortiAnalyzer"}]

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
    "VALID_BODY_DROP_INFECTED",
    "VALID_BODY_STORE_INFECTED",
    "VALID_BODY_DROP_MACHINE_LEARNING",
    "VALID_BODY_STORE_MACHINE_LEARNING",
    "VALID_BODY_LOWSPACE",
    "VALID_BODY_DESTINATION",
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