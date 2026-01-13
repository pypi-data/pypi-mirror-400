from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_STATUS: Literal[{"description": "Enable logging by FortiSwitch device to a remote syslog server", "help": "Enable logging by FortiSwitch device to a remote syslog server.", "label": "Enable", "name": "enable"}, {"description": "Disable logging by FortiSwitch device to a remote syslog server", "help": "Disable logging by FortiSwitch device to a remote syslog server.", "label": "Disable", "name": "disable"}]
VALID_BODY_SEVERITY: Literal[{"description": "Emergency level", "help": "Emergency level.", "label": "Emergency", "name": "emergency"}, {"description": "Alert level", "help": "Alert level.", "label": "Alert", "name": "alert"}, {"description": "Critical level", "help": "Critical level.", "label": "Critical", "name": "critical"}, {"description": "Error level", "help": "Error level.", "label": "Error", "name": "error"}, {"description": "Warning level", "help": "Warning level.", "label": "Warning", "name": "warning"}, {"description": "Notification level", "help": "Notification level.", "label": "Notification", "name": "notification"}, {"description": "Information level", "help": "Information level.", "label": "Information", "name": "information"}, {"description": "Debug level", "help": "Debug level.", "label": "Debug", "name": "debug"}]
VALID_BODY_CSV: Literal[{"description": "Enable comma-separated value (CSV) strings", "help": "Enable comma-separated value (CSV) strings.", "label": "Enable", "name": "enable"}, {"description": "Disable comma-separated value (CSV) strings", "help": "Disable comma-separated value (CSV) strings.", "label": "Disable", "name": "disable"}]
VALID_BODY_FACILITY: Literal[{"description": "Kernel messages", "help": "Kernel messages.", "label": "Kernel", "name": "kernel"}, {"description": "Random user-level messages", "help": "Random user-level messages.", "label": "User", "name": "user"}, {"description": "Mail system", "help": "Mail system.", "label": "Mail", "name": "mail"}, {"description": "System daemons", "help": "System daemons.", "label": "Daemon", "name": "daemon"}, {"description": "Security/authorization messages", "help": "Security/authorization messages.", "label": "Auth", "name": "auth"}, {"description": "Messages generated internally by syslogd", "help": "Messages generated internally by syslogd.", "label": "Syslog", "name": "syslog"}, {"description": "Line printer subsystem", "help": "Line printer subsystem.", "label": "Lpr", "name": "lpr"}, {"description": "Network news subsystem", "help": "Network news subsystem.", "label": "News", "name": "news"}, {"description": "UUCP server messages", "help": "UUCP server messages.", "label": "Uucp", "name": "uucp"}, {"description": "Clock daemon", "help": "Clock daemon.", "label": "Cron", "name": "cron"}, {"description": "Security/authorization messages (private)", "help": "Security/authorization messages (private).", "label": "Authpriv", "name": "authpriv"}, {"description": "FTP daemon", "help": "FTP daemon.", "label": "Ftp", "name": "ftp"}, {"description": "NTP daemon", "help": "NTP daemon.", "label": "Ntp", "name": "ntp"}, {"description": "Log audit", "help": "Log audit.", "label": "Audit", "name": "audit"}, {"description": "Log alert", "help": "Log alert.", "label": "Alert", "name": "alert"}, {"description": "Clock daemon", "help": "Clock daemon.", "label": "Clock", "name": "clock"}, {"description": "Reserved for local use", "help": "Reserved for local use.", "label": "Local0", "name": "local0"}, {"description": "Reserved for local use", "help": "Reserved for local use.", "label": "Local1", "name": "local1"}, {"description": "Reserved for local use", "help": "Reserved for local use.", "label": "Local2", "name": "local2"}, {"description": "Reserved for local use", "help": "Reserved for local use.", "label": "Local3", "name": "local3"}, {"description": "Reserved for local use", "help": "Reserved for local use.", "label": "Local4", "name": "local4"}, {"description": "Reserved for local use", "help": "Reserved for local use.", "label": "Local5", "name": "local5"}, {"description": "Reserved for local use", "help": "Reserved for local use.", "label": "Local6", "name": "local6"}, {"description": "Reserved for local use", "help": "Reserved for local use.", "label": "Local7", "name": "local7"}]

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
    "VALID_BODY_SEVERITY",
    "VALID_BODY_CSV",
    "VALID_BODY_FACILITY",
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