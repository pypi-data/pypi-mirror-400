from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_STATUS: Literal[{"description": "Log to remote syslog server", "help": "Log to remote syslog server.", "label": "Enable", "name": "enable"}, {"description": "Do not log to remote syslog server", "help": "Do not log to remote syslog server.", "label": "Disable", "name": "disable"}]
VALID_BODY_MODE: Literal[{"description": "Enable syslogging over UDP", "help": "Enable syslogging over UDP.", "label": "Udp", "name": "udp"}, {"description": "Enable legacy reliable syslogging by RFC3195 (Reliable Delivery for Syslog)", "help": "Enable legacy reliable syslogging by RFC3195 (Reliable Delivery for Syslog).", "label": "Legacy Reliable", "name": "legacy-reliable"}, {"description": "Enable reliable syslogging by RFC6587 (Transmission of Syslog Messages over TCP)", "help": "Enable reliable syslogging by RFC6587 (Transmission of Syslog Messages over TCP).", "label": "Reliable", "name": "reliable"}]
VALID_BODY_USE_MANAGEMENT_VDOM: Literal[{"description": "Enable use of management VDOM as source VDOM", "help": "Enable use of management VDOM as source VDOM.", "label": "Enable", "name": "enable"}, {"description": "Use the current VDOM as source VDOM", "help": "Use the current VDOM as source VDOM.", "label": "Disable", "name": "disable"}]
VALID_BODY_FACILITY: Literal[{"description": "Kernel messages", "help": "Kernel messages.", "label": "Kernel", "name": "kernel"}, {"description": "Random user-level messages", "help": "Random user-level messages.", "label": "User", "name": "user"}, {"description": "Mail system", "help": "Mail system.", "label": "Mail", "name": "mail"}, {"description": "System daemons", "help": "System daemons.", "label": "Daemon", "name": "daemon"}, {"description": "Security/authorization messages", "help": "Security/authorization messages.", "label": "Auth", "name": "auth"}, {"description": "Messages generated internally by syslog", "help": "Messages generated internally by syslog.", "label": "Syslog", "name": "syslog"}, {"description": "Line printer subsystem", "help": "Line printer subsystem.", "label": "Lpr", "name": "lpr"}, {"description": "Network news subsystem", "help": "Network news subsystem.", "label": "News", "name": "news"}, {"description": "Network news subsystem", "help": "Network news subsystem.", "label": "Uucp", "name": "uucp"}, {"description": "Clock daemon", "help": "Clock daemon.", "label": "Cron", "name": "cron"}, {"description": "Security/authorization messages (private)", "help": "Security/authorization messages (private).", "label": "Authpriv", "name": "authpriv"}, {"description": "FTP daemon", "help": "FTP daemon.", "label": "Ftp", "name": "ftp"}, {"description": "NTP daemon", "help": "NTP daemon.", "label": "Ntp", "name": "ntp"}, {"description": "Log audit", "help": "Log audit.", "label": "Audit", "name": "audit"}, {"description": "Log alert", "help": "Log alert.", "label": "Alert", "name": "alert"}, {"description": "Clock daemon", "help": "Clock daemon.", "label": "Clock", "name": "clock"}, {"description": "Reserved for local use", "help": "Reserved for local use.", "label": "Local0", "name": "local0"}, {"description": "Reserved for local use", "help": "Reserved for local use.", "label": "Local1", "name": "local1"}, {"description": "Reserved for local use", "help": "Reserved for local use.", "label": "Local2", "name": "local2"}, {"description": "Reserved for local use", "help": "Reserved for local use.", "label": "Local3", "name": "local3"}, {"description": "Reserved for local use", "help": "Reserved for local use.", "label": "Local4", "name": "local4"}, {"description": "Reserved for local use", "help": "Reserved for local use.", "label": "Local5", "name": "local5"}, {"description": "Reserved for local use", "help": "Reserved for local use.", "label": "Local6", "name": "local6"}, {"description": "Reserved for local use", "help": "Reserved for local use.", "label": "Local7", "name": "local7"}]
VALID_BODY_FORMAT: Literal[{"description": "Syslog format", "help": "Syslog format.", "label": "Default", "name": "default"}, {"description": "CSV (Comma Separated Values) format", "help": "CSV (Comma Separated Values) format.", "label": "Csv", "name": "csv"}, {"description": "CEF (Common Event Format) format", "help": "CEF (Common Event Format) format.", "label": "Cef", "name": "cef"}, {"description": "Syslog RFC5424 format", "help": "Syslog RFC5424 format.", "label": "Rfc5424", "name": "rfc5424"}, {"description": "JSON (JavaScript Object Notation) format", "help": "JSON (JavaScript Object Notation) format.", "label": "Json", "name": "json"}]
VALID_BODY_PRIORITY: Literal[{"description": "Set Syslog transmission priority to default", "help": "Set Syslog transmission priority to default.", "label": "Default", "name": "default"}, {"description": "Set Syslog transmission priority to low", "help": "Set Syslog transmission priority to low.", "label": "Low", "name": "low"}]
VALID_BODY_ENC_ALGORITHM: Literal[{"description": "SSL communication with high and medium encryption algorithms", "help": "SSL communication with high and medium encryption algorithms.", "label": "High Medium", "name": "high-medium"}, {"description": "SSL communication with high encryption algorithms", "help": "SSL communication with high encryption algorithms.", "label": "High", "name": "high"}, {"description": "SSL communication with low encryption algorithms", "help": "SSL communication with low encryption algorithms.", "label": "Low", "name": "low"}, {"description": "Disable SSL communication", "help": "Disable SSL communication.", "label": "Disable", "name": "disable"}]
VALID_BODY_SSL_MIN_PROTO_VERSION: Literal[{"description": "Follow system global setting", "help": "Follow system global setting.", "label": "Default", "name": "default"}, {"description": "SSLv3", "help": "SSLv3.", "label": "Sslv3", "name": "SSLv3"}, {"description": "TLSv1", "help": "TLSv1.", "label": "Tlsv1", "name": "TLSv1"}, {"description": "TLSv1", "help": "TLSv1.1.", "label": "Tlsv1 1", "name": "TLSv1-1"}, {"description": "TLSv1", "help": "TLSv1.2.", "label": "Tlsv1 2", "name": "TLSv1-2"}, {"description": "TLSv1", "help": "TLSv1.3.", "label": "Tlsv1 3", "name": "TLSv1-3"}]
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
    "VALID_BODY_STATUS",
    "VALID_BODY_MODE",
    "VALID_BODY_USE_MANAGEMENT_VDOM",
    "VALID_BODY_FACILITY",
    "VALID_BODY_FORMAT",
    "VALID_BODY_PRIORITY",
    "VALID_BODY_ENC_ALGORITHM",
    "VALID_BODY_SSL_MIN_PROTO_VERSION",
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