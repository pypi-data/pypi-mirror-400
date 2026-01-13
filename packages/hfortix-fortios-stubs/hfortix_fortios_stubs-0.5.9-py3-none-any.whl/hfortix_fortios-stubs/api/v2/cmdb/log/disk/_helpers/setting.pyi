from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_STATUS: Literal[{"description": "Log to local disk", "help": "Log to local disk.", "label": "Enable", "name": "enable"}, {"description": "Do not log to local disk", "help": "Do not log to local disk.", "label": "Disable", "name": "disable"}]
VALID_BODY_IPS_ARCHIVE: Literal[{"description": "Enable IPS packet archiving", "help": "Enable IPS packet archiving.", "label": "Enable", "name": "enable"}, {"description": "Disable IPS packet archiving", "help": "Disable IPS packet archiving.", "label": "Disable", "name": "disable"}]
VALID_BODY_ROLL_SCHEDULE: Literal[{"description": "Check the log file once a day", "help": "Check the log file once a day.", "label": "Daily", "name": "daily"}, {"description": "Check the log file once a week", "help": "Check the log file once a week.", "label": "Weekly", "name": "weekly"}]
VALID_BODY_ROLL_DAY: Literal[{"description": "Sunday    monday:Monday    tuesday:Tuesday    wednesday:Wednesday    thursday:Thursday    friday:Friday    saturday:Saturday", "help": "Sunday", "label": "Sunday", "name": "sunday"}, {"help": "Monday", "label": "Monday", "name": "monday"}, {"help": "Tuesday", "label": "Tuesday", "name": "tuesday"}, {"help": "Wednesday", "label": "Wednesday", "name": "wednesday"}, {"help": "Thursday", "label": "Thursday", "name": "thursday"}, {"help": "Friday", "label": "Friday", "name": "friday"}, {"help": "Saturday", "label": "Saturday", "name": "saturday"}]
VALID_BODY_DISKFULL: Literal[{"description": "Overwrite the oldest logs when the log disk is full", "help": "Overwrite the oldest logs when the log disk is full.", "label": "Overwrite", "name": "overwrite"}, {"description": "Stop logging when the log disk is full", "help": "Stop logging when the log disk is full.", "label": "Nolog", "name": "nolog"}]
VALID_BODY_UPLOAD: Literal[{"description": "Enable uploading log files when they are rolled", "help": "Enable uploading log files when they are rolled.", "label": "Enable", "name": "enable"}, {"description": "Disable uploading log files when they are rolled", "help": "Disable uploading log files when they are rolled.", "label": "Disable", "name": "disable"}]
VALID_BODY_UPLOAD_DESTINATION: Literal[{"description": "Upload rolled log files to an FTP server", "help": "Upload rolled log files to an FTP server.", "label": "Ftp Server", "name": "ftp-server"}]
VALID_BODY_UPLOADTYPE: Literal[{"description": "Upload traffic log", "help": "Upload traffic log.", "label": "Traffic", "name": "traffic"}, {"description": "Upload event log", "help": "Upload event log.", "label": "Event", "name": "event"}, {"description": "Upload anti-virus log", "help": "Upload anti-virus log.", "label": "Virus", "name": "virus"}, {"description": "Upload web filter log", "help": "Upload web filter log.", "label": "Webfilter", "name": "webfilter"}, {"description": "Upload IPS log", "help": "Upload IPS log.", "label": "Ips", "name": "IPS"}, {"description": "Upload spam filter log", "help": "Upload spam filter log.", "label": "Emailfilter", "name": "emailfilter"}, {"description": "Upload DLP archive", "help": "Upload DLP archive.", "label": "Dlp Archive", "name": "dlp-archive"}, {"description": "Upload anomaly log", "help": "Upload anomaly log.", "label": "Anomaly", "name": "anomaly"}, {"description": "Upload VoIP log", "help": "Upload VoIP log.", "label": "Voip", "name": "voip"}, {"description": "Upload DLP log", "help": "Upload DLP log.", "label": "Dlp", "name": "dlp"}, {"description": "Upload application control log", "help": "Upload application control log.", "label": "App Ctrl", "name": "app-ctrl"}, {"description": "Upload web application firewall log", "help": "Upload web application firewall log.", "label": "Waf", "name": "waf"}, {"help": "Upload GTP log.", "label": "Gtp", "name": "gtp"}, {"description": "Upload DNS log", "help": "Upload DNS log.", "label": "Dns", "name": "dns"}, {"description": "Upload SSH log", "help": "Upload SSH log.", "label": "Ssh", "name": "ssh"}, {"description": "Upload SSL log", "help": "Upload SSL log.", "label": "Ssl", "name": "ssl"}, {"description": "Upload file-filter log", "help": "Upload file-filter log.", "label": "File Filter", "name": "file-filter"}, {"description": "Upload ICAP log", "help": "Upload ICAP log.", "label": "Icap", "name": "icap"}, {"description": "Upload virtual-patch log", "help": "Upload virtual-patch log.", "label": "Virtual Patch", "name": "virtual-patch"}, {"description": "Upload debug log", "help": "Upload debug log.", "label": "Debug", "name": "debug"}]
VALID_BODY_UPLOADSCHED: Literal[{"description": "Upload when rolling", "help": "Upload when rolling.", "label": "Disable", "name": "disable"}, {"description": "Scheduled upload", "help": "Scheduled upload.", "label": "Enable", "name": "enable"}]
VALID_BODY_UPLOAD_DELETE_FILES: Literal[{"description": "Delete log files after uploading", "help": "Delete log files after uploading.", "label": "Enable", "name": "enable"}, {"description": "Do not delete log files after uploading", "help": "Do not delete log files after uploading.", "label": "Disable", "name": "disable"}]
VALID_BODY_UPLOAD_SSL_CONN: Literal[{"description": "FTPS with high and medium encryption algorithms", "help": "FTPS with high and medium encryption algorithms.", "label": "Default", "name": "default"}, {"description": "FTPS with high encryption algorithms", "help": "FTPS with high encryption algorithms.", "label": "High", "name": "high"}, {"description": "FTPS with low encryption algorithms", "help": "FTPS with low encryption algorithms.", "label": "Low", "name": "low"}, {"description": "Disable FTPS communication", "help": "Disable FTPS communication.", "label": "Disable", "name": "disable"}]
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
    "VALID_BODY_IPS_ARCHIVE",
    "VALID_BODY_ROLL_SCHEDULE",
    "VALID_BODY_ROLL_DAY",
    "VALID_BODY_DISKFULL",
    "VALID_BODY_UPLOAD",
    "VALID_BODY_UPLOAD_DESTINATION",
    "VALID_BODY_UPLOADTYPE",
    "VALID_BODY_UPLOADSCHED",
    "VALID_BODY_UPLOAD_DELETE_FILES",
    "VALID_BODY_UPLOAD_SSL_CONN",
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