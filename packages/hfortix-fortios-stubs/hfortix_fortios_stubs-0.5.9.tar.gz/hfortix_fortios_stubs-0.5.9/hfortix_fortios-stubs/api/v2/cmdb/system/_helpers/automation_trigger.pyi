from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_TRIGGER_TYPE: Literal[{"description": "Event based trigger", "help": "Event based trigger.", "label": "Event Based", "name": "event-based"}, {"description": "Scheduled trigger", "help": "Scheduled trigger.", "label": "Scheduled", "name": "scheduled"}]
VALID_BODY_EVENT_TYPE: Literal[{"description": "Indicator of compromise detected", "help": "Indicator of compromise detected.", "label": "Ioc", "name": "ioc"}, {"description": "Use log ID as trigger", "help": "Use log ID as trigger.", "label": "Event Log", "name": "event-log"}, {"description": "Device reboot", "help": "Device reboot.", "label": "Reboot", "name": "reboot"}, {"description": "Conserve mode due to low memory", "help": "Conserve mode due to low memory.", "label": "Low Memory", "name": "low-memory"}, {"description": "High CPU usage", "help": "High CPU usage.", "label": "High Cpu", "name": "high-cpu"}, {"description": "License near expiration date", "help": "License near expiration date.", "label": "License Near Expiry", "name": "license-near-expiry"}, {"description": "The local certificate near expiration date", "help": "The local certificate near expiration date.", "label": "Local Cert Near Expiry", "name": "local-cert-near-expiry"}, {"description": "HA failover", "help": "HA failover.", "label": "Ha Failover", "name": "ha-failover"}, {"description": "Configuration change", "help": "Configuration change.", "label": "Config Change", "name": "config-change"}, {"description": "Security rating summary", "help": "Security rating summary.", "label": "Security Rating Summary", "name": "security-rating-summary"}, {"description": "Virus and IPS database updated", "help": "Virus and IPS database updated.", "label": "Virus Ips Db Updated", "name": "virus-ips-db-updated"}, {"description": "FortiAnalyzer event", "help": "FortiAnalyzer event.", "label": "Faz Event", "name": "faz-event"}, {"description": "Incoming webhook call", "help": "Incoming webhook call.", "label": "Incoming Webhook", "name": "incoming-webhook"}, {"description": "Fabric connector event", "help": "Fabric connector event.", "label": "Fabric Event", "name": "fabric-event"}, {"description": "IPS logs", "help": "IPS logs.", "label": "Ips Logs", "name": "ips-logs"}, {"description": "Anomaly logs", "help": "Anomaly logs.", "label": "Anomaly Logs", "name": "anomaly-logs"}, {"description": "Virus logs", "help": "Virus logs.", "label": "Virus Logs", "name": "virus-logs"}, {"description": "SSH logs", "help": "SSH logs.", "label": "Ssh Logs", "name": "ssh-logs"}, {"description": "Webfilter violation", "help": "Webfilter violation.", "label": "Webfilter Violation", "name": "webfilter-violation"}, {"description": "Traffic violation", "help": "Traffic violation.", "label": "Traffic Violation", "name": "traffic-violation"}, {"description": "Specified stitch has been triggered", "help": "Specified stitch has been triggered.", "label": "Stitch", "name": "stitch"}]
VALID_BODY_LICENSE_TYPE: Literal[{"description": "FortiCare support license", "help": "FortiCare support license.", "label": "Forticare Support", "name": "forticare-support"}, {"description": "FortiGuard web filter license", "help": "FortiGuard web filter license.", "label": "Fortiguard Webfilter", "name": "fortiguard-webfilter"}, {"description": "FortiGuard antispam license", "help": "FortiGuard antispam license.", "label": "Fortiguard Antispam", "name": "fortiguard-antispam"}, {"description": "FortiGuard AntiVirus license", "help": "FortiGuard AntiVirus license.", "label": "Fortiguard Antivirus", "name": "fortiguard-antivirus"}, {"description": "FortiGuard IPS license", "help": "FortiGuard IPS license.", "label": "Fortiguard Ips", "name": "fortiguard-ips"}, {"description": "FortiGuard management service license", "help": "FortiGuard management service license.", "label": "Fortiguard Management", "name": "fortiguard-management"}, {"description": "FortiCloud license", "help": "FortiCloud license.", "label": "Forticloud", "name": "forticloud"}, {"description": "Any license", "help": "Any license.", "label": "Any", "name": "any"}]
VALID_BODY_REPORT_TYPE: Literal[{"description": "Posture report", "help": "Posture report.", "label": "Posture", "name": "posture"}, {"description": "Coverage report", "help": "Coverage report.", "label": "Coverage", "name": "coverage"}, {"description": "Optimization report    any:Any report", "help": "Optimization report", "label": "Optimization", "name": "optimization"}, {"help": "Any report.", "label": "Any", "name": "any"}]
VALID_BODY_TRIGGER_FREQUENCY: Literal[{"description": "Run hourly", "help": "Run hourly.", "label": "Hourly", "name": "hourly"}, {"description": "Run daily", "help": "Run daily.", "label": "Daily", "name": "daily"}, {"description": "Run weekly", "help": "Run weekly.", "label": "Weekly", "name": "weekly"}, {"description": "Run monthly", "help": "Run monthly.", "label": "Monthly", "name": "monthly"}, {"description": "Run once at specified date time", "help": "Run once at specified date time.", "label": "Once", "name": "once"}]
VALID_BODY_TRIGGER_WEEKDAY: Literal[{"description": "Sunday", "help": "Sunday.", "label": "Sunday", "name": "sunday"}, {"description": "Monday", "help": "Monday.", "label": "Monday", "name": "monday"}, {"description": "Tuesday", "help": "Tuesday.", "label": "Tuesday", "name": "tuesday"}, {"description": "Wednesday", "help": "Wednesday.", "label": "Wednesday", "name": "wednesday"}, {"description": "Thursday", "help": "Thursday.", "label": "Thursday", "name": "thursday"}, {"description": "Friday", "help": "Friday.", "label": "Friday", "name": "friday"}, {"description": "Saturday", "help": "Saturday.", "label": "Saturday", "name": "saturday"}]

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
    "VALID_BODY_TRIGGER_TYPE",
    "VALID_BODY_EVENT_TYPE",
    "VALID_BODY_LICENSE_TYPE",
    "VALID_BODY_REPORT_TYPE",
    "VALID_BODY_TRIGGER_FREQUENCY",
    "VALID_BODY_TRIGGER_WEEKDAY",
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