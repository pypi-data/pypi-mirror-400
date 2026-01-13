from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_FILTER_MODE: Literal[{"description": "Filter based on category", "help": "Filter based on category.", "label": "Category", "name": "category"}, {"description": "Filter based on severity", "help": "Filter based on severity.", "label": "Threshold", "name": "threshold"}]
VALID_BODY_IPS_LOGS: Literal[{"description": "Enable IPS logs in alert email", "help": "Enable IPS logs in alert email.", "label": "Enable", "name": "enable"}, {"description": "Disable IPS logs in alert email", "help": "Disable IPS logs in alert email.", "label": "Disable", "name": "disable"}]
VALID_BODY_FIREWALL_AUTHENTICATION_FAILURE_LOGS: Literal[{"description": "Enable firewall authentication failure logs in alert email", "help": "Enable firewall authentication failure logs in alert email.", "label": "Enable", "name": "enable"}, {"description": "Disable firewall authentication failure logs in alert email", "help": "Disable firewall authentication failure logs in alert email.", "label": "Disable", "name": "disable"}]
VALID_BODY_HA_LOGS: Literal[{"description": "Enable HA logs in alert email", "help": "Enable HA logs in alert email.", "label": "Enable", "name": "enable"}, {"description": "Disable HA logs in alert email", "help": "Disable HA logs in alert email.", "label": "Disable", "name": "disable"}]
VALID_BODY_IPSEC_ERRORS_LOGS: Literal[{"description": "Enable IPsec error logs in alert email", "help": "Enable IPsec error logs in alert email.", "label": "Enable", "name": "enable"}, {"description": "Disable IPsec error logs in alert email", "help": "Disable IPsec error logs in alert email.", "label": "Disable", "name": "disable"}]
VALID_BODY_FDS_UPDATE_LOGS: Literal[{"description": "Enable FortiGuard update logs in alert email", "help": "Enable FortiGuard update logs in alert email.", "label": "Enable", "name": "enable"}, {"description": "Disable FortiGuard update logs in alert email", "help": "Disable FortiGuard update logs in alert email.", "label": "Disable", "name": "disable"}]
VALID_BODY_PPP_ERRORS_LOGS: Literal[{"description": "Enable PPP error logs in alert email", "help": "Enable PPP error logs in alert email.", "label": "Enable", "name": "enable"}, {"description": "Disable PPP error logs in alert email", "help": "Disable PPP error logs in alert email.", "label": "Disable", "name": "disable"}]
VALID_BODY_SSLVPN_AUTHENTICATION_ERRORS_LOGS: Literal[{"help": "Enable Agentless VPN authentication error logs in alert email.", "label": "Enable", "name": "enable"}, {"help": "Disable Agentless VPN authentication error logs in alert email.", "label": "Disable", "name": "disable"}]
VALID_BODY_ANTIVIRUS_LOGS: Literal[{"description": "Enable antivirus logs in alert email", "help": "Enable antivirus logs in alert email.", "label": "Enable", "name": "enable"}, {"description": "Disable antivirus logs in alert email", "help": "Disable antivirus logs in alert email.", "label": "Disable", "name": "disable"}]
VALID_BODY_WEBFILTER_LOGS: Literal[{"description": "Enable web filter logs in alert email", "help": "Enable web filter logs in alert email.", "label": "Enable", "name": "enable"}, {"description": "Disable web filter logs in alert email", "help": "Disable web filter logs in alert email.", "label": "Disable", "name": "disable"}]
VALID_BODY_CONFIGURATION_CHANGES_LOGS: Literal[{"description": "Enable configuration change logs in alert email", "help": "Enable configuration change logs in alert email.", "label": "Enable", "name": "enable"}, {"description": "Disable configuration change logs in alert email", "help": "Disable configuration change logs in alert email.", "label": "Disable", "name": "disable"}]
VALID_BODY_VIOLATION_TRAFFIC_LOGS: Literal[{"description": "Enable violation traffic logs in alert email", "help": "Enable violation traffic logs in alert email.", "label": "Enable", "name": "enable"}, {"description": "Disable violation traffic logs in alert email", "help": "Disable violation traffic logs in alert email.", "label": "Disable", "name": "disable"}]
VALID_BODY_ADMIN_LOGIN_LOGS: Literal[{"description": "Enable administrator login/logout logs in alert email", "help": "Enable administrator login/logout logs in alert email.", "label": "Enable", "name": "enable"}, {"description": "Disable administrator login/logout logs in alert email", "help": "Disable administrator login/logout logs in alert email.", "label": "Disable", "name": "disable"}]
VALID_BODY_FDS_LICENSE_EXPIRING_WARNING: Literal[{"description": "Enable FortiGuard license expiration warnings in alert email", "help": "Enable FortiGuard license expiration warnings in alert email.", "label": "Enable", "name": "enable"}, {"description": "Disable FortiGuard license expiration warnings in alert email", "help": "Disable FortiGuard license expiration warnings in alert email.", "label": "Disable", "name": "disable"}]
VALID_BODY_LOG_DISK_USAGE_WARNING: Literal[{"description": "Enable disk usage warnings in alert email", "help": "Enable disk usage warnings in alert email.", "label": "Enable", "name": "enable"}, {"description": "Disable disk usage warnings in alert email", "help": "Disable disk usage warnings in alert email.", "label": "Disable", "name": "disable"}]
VALID_BODY_FORTIGUARD_LOG_QUOTA_WARNING: Literal[{"description": "Enable FortiCloud log quota warnings in alert email", "help": "Enable FortiCloud log quota warnings in alert email.", "label": "Enable", "name": "enable"}, {"description": "Disable FortiCloud log quota warnings in alert email", "help": "Disable FortiCloud log quota warnings in alert email.", "label": "Disable", "name": "disable"}]
VALID_BODY_AMC_INTERFACE_BYPASS_MODE: Literal[{"description": "Enable Fortinet Advanced Mezzanine Card (AMC) interface bypass mode logs in alert email", "help": "Enable Fortinet Advanced Mezzanine Card (AMC) interface bypass mode logs in alert email.", "label": "Enable", "name": "enable"}, {"description": "Disable Fortinet Advanced Mezzanine Card (AMC) interface bypass mode logs in alert email", "help": "Disable Fortinet Advanced Mezzanine Card (AMC) interface bypass mode logs in alert email.", "label": "Disable", "name": "disable"}]
VALID_BODY_FIPS_CC_ERRORS: Literal[{"description": "Enable FIPS and Common Criteria error logs in alert email", "help": "Enable FIPS and Common Criteria error logs in alert email.", "label": "Enable", "name": "enable"}, {"description": "Disable FIPS and Common Criteria error logs in alert email", "help": "Disable FIPS and Common Criteria error logs in alert email.", "label": "Disable", "name": "disable"}]
VALID_BODY_FSSO_DISCONNECT_LOGS: Literal[{"description": "Enable logging of FSSO collector agent disconnect", "help": "Enable logging of FSSO collector agent disconnect.", "label": "Enable", "name": "enable"}, {"description": "Disable logging of FSSO collector agent disconnect", "help": "Disable logging of FSSO collector agent disconnect.", "label": "Disable", "name": "disable"}]
VALID_BODY_SSH_LOGS: Literal[{"description": "Enable SSH logs in alert email", "help": "Enable SSH logs in alert email.", "label": "Enable", "name": "enable"}, {"description": "Disable SSH logs in alert email", "help": "Disable SSH logs in alert email.", "label": "Disable", "name": "disable"}]
VALID_BODY_SEVERITY: Literal[{"description": "Emergency level", "help": "Emergency level.", "label": "Emergency", "name": "emergency"}, {"description": "Alert level", "help": "Alert level.", "label": "Alert", "name": "alert"}, {"description": "Critical level", "help": "Critical level.", "label": "Critical", "name": "critical"}, {"description": "Error level", "help": "Error level.", "label": "Error", "name": "error"}, {"description": "Warning level", "help": "Warning level.", "label": "Warning", "name": "warning"}, {"description": "Notification level", "help": "Notification level.", "label": "Notification", "name": "notification"}, {"description": "Information level", "help": "Information level.", "label": "Information", "name": "information"}, {"description": "Debug level", "help": "Debug level.", "label": "Debug", "name": "debug"}]

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
    "VALID_BODY_FILTER_MODE",
    "VALID_BODY_IPS_LOGS",
    "VALID_BODY_FIREWALL_AUTHENTICATION_FAILURE_LOGS",
    "VALID_BODY_HA_LOGS",
    "VALID_BODY_IPSEC_ERRORS_LOGS",
    "VALID_BODY_FDS_UPDATE_LOGS",
    "VALID_BODY_PPP_ERRORS_LOGS",
    "VALID_BODY_SSLVPN_AUTHENTICATION_ERRORS_LOGS",
    "VALID_BODY_ANTIVIRUS_LOGS",
    "VALID_BODY_WEBFILTER_LOGS",
    "VALID_BODY_CONFIGURATION_CHANGES_LOGS",
    "VALID_BODY_VIOLATION_TRAFFIC_LOGS",
    "VALID_BODY_ADMIN_LOGIN_LOGS",
    "VALID_BODY_FDS_LICENSE_EXPIRING_WARNING",
    "VALID_BODY_LOG_DISK_USAGE_WARNING",
    "VALID_BODY_FORTIGUARD_LOG_QUOTA_WARNING",
    "VALID_BODY_AMC_INTERFACE_BYPASS_MODE",
    "VALID_BODY_FIPS_CC_ERRORS",
    "VALID_BODY_FSSO_DISCONNECT_LOGS",
    "VALID_BODY_SSH_LOGS",
    "VALID_BODY_SEVERITY",
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