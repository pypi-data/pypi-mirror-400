from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_ACTION_TYPE: Literal[{"description": "Send notification email", "help": "Send notification email.", "label": "Email", "name": "email"}, {"description": "Send push notification to FortiExplorer", "help": "Send push notification to FortiExplorer.", "label": "Fortiexplorer Notification", "name": "fortiexplorer-notification"}, {"description": "Generate FortiOS dashboard alert", "help": "Generate FortiOS dashboard alert.", "label": "Alert", "name": "alert"}, {"description": "Disable interface", "help": "Disable interface.", "label": "Disable Ssid", "name": "disable-ssid"}, {"description": "Perform immediate system operations on this FortiGate unit", "help": "Perform immediate system operations on this FortiGate unit.", "label": "System Actions", "name": "system-actions"}, {"description": "Quarantine host", "help": "Quarantine host.", "label": "Quarantine", "name": "quarantine"}, {"description": "Quarantine FortiClient by EMS", "help": "Quarantine FortiClient by EMS.", "label": "Quarantine Forticlient", "name": "quarantine-forticlient"}, {"description": "Quarantine NSX instance", "help": "Quarantine NSX instance.", "label": "Quarantine Nsx", "name": "quarantine-nsx"}, {"description": "Quarantine host by FortiNAC", "help": "Quarantine host by FortiNAC.", "label": "Quarantine Fortinac", "name": "quarantine-fortinac"}, {"description": "Ban IP address", "help": "Ban IP address.", "label": "Ban Ip", "name": "ban-ip"}, {"description": "Send log data to integrated AWS service", "help": "Send log data to integrated AWS service.", "label": "Aws Lambda", "name": "aws-lambda"}, {"description": "Send log data to an Azure function", "help": "Send log data to an Azure function.", "label": "Azure Function", "name": "azure-function"}, {"description": "Send log data to a Google Cloud function", "help": "Send log data to a Google Cloud function.", "label": "Google Cloud Function", "name": "google-cloud-function"}, {"description": "Send log data to an AliCloud function", "help": "Send log data to an AliCloud function.", "label": "Alicloud Function", "name": "alicloud-function"}, {"description": "Send an HTTP request", "help": "Send an HTTP request.", "label": "Webhook", "name": "webhook"}, {"description": "Run CLI script", "help": "Run CLI script.", "label": "Cli Script", "name": "cli-script"}, {"description": "Run diagnose script", "help": "Run diagnose script.", "label": "Diagnose Script", "name": "diagnose-script"}, {"description": "Match pattern on input text", "help": "Match pattern on input text.", "label": "Regular Expression", "name": "regular-expression"}, {"description": "Send a notification message to a Slack incoming webhook", "help": "Send a notification message to a Slack incoming webhook.", "label": "Slack Notification", "name": "slack-notification"}, {"description": "Send a notification message to a Microsoft Teams incoming webhook", "help": "Send a notification message to a Microsoft Teams incoming webhook.", "label": "Microsoft Teams Notification", "name": "microsoft-teams-notification"}]
VALID_BODY_SYSTEM_ACTION: Literal[{"description": "Reboot this FortiGate unit", "help": "Reboot this FortiGate unit.", "label": "Reboot", "name": "reboot"}, {"description": "Shutdown this FortiGate unit", "help": "Shutdown this FortiGate unit.", "label": "Shutdown", "name": "shutdown"}, {"description": "Backup current configuration to the disk revisions", "help": "Backup current configuration to the disk revisions.", "label": "Backup Config", "name": "backup-config"}]
VALID_BODY_FORTICARE_EMAIL: Literal[{"description": "Enable use of your FortiCare email address as the email-to address", "help": "Enable use of your FortiCare email address as the email-to address.", "label": "Enable", "name": "enable"}, {"description": "Disable use of your FortiCare email address as the email-to address", "help": "Disable use of your FortiCare email address as the email-to address.", "label": "Disable", "name": "disable"}]
VALID_BODY_AZURE_FUNCTION_AUTHORIZATION: Literal[{"description": "Anonymous authorization level (No authorization required)", "help": "Anonymous authorization level (No authorization required).", "label": "Anonymous", "name": "anonymous"}, {"description": "Function authorization level (Function or Host Key required)", "help": "Function authorization level (Function or Host Key required).", "label": "Function", "name": "function"}, {"description": "Admin authorization level (Master Host Key required)", "help": "Admin authorization level (Master Host Key required).", "label": "Admin", "name": "admin"}]
VALID_BODY_ALICLOUD_FUNCTION_AUTHORIZATION: Literal[{"description": "Anonymous authorization (No authorization required)", "help": "Anonymous authorization (No authorization required).", "label": "Anonymous", "name": "anonymous"}, {"description": "Function authorization (Authorization required)", "help": "Function authorization (Authorization required).", "label": "Function", "name": "function"}]
VALID_BODY_MESSAGE_TYPE: Literal[{"description": "Plaintext", "help": "Plaintext.", "label": "Text", "name": "text"}, {"description": "Custom JSON", "help": "Custom JSON.", "label": "Json", "name": "json"}, {"description": "Multipart/form-data", "help": "Multipart/form-data", "label": "Form Data", "name": "form-data"}]
VALID_BODY_REPLACEMENT_MESSAGE: Literal[{"description": "Enable replacement message", "help": "Enable replacement message.", "label": "Enable", "name": "enable"}, {"description": "Disable replacement message", "help": "Disable replacement message.", "label": "Disable", "name": "disable"}]
VALID_BODY_PROTOCOL: Literal[{"description": "HTTP", "help": "HTTP.", "label": "Http", "name": "http"}, {"description": "HTTPS", "help": "HTTPS.", "label": "Https", "name": "https"}]
VALID_BODY_METHOD: Literal[{"description": "POST", "help": "POST.", "label": "Post", "name": "post"}, {"description": "PUT", "help": "PUT.", "label": "Put", "name": "put"}, {"description": "GET", "help": "GET.", "label": "Get", "name": "get"}, {"description": "PATCH", "help": "PATCH.", "label": "Patch", "name": "patch"}, {"description": "DELETE", "help": "DELETE.", "label": "Delete", "name": "delete"}]
VALID_BODY_VERIFY_HOST_CERT: Literal[{"description": "Enable verification of the remote host certificate", "help": "Enable verification of the remote host certificate.", "label": "Enable", "name": "enable"}, {"description": "Disable verification of the remote host certificate", "help": "Disable verification of the remote host certificate.", "label": "Disable", "name": "disable"}]
VALID_BODY_FILE_ONLY: Literal[{"description": "The output of the diag CLI will only be files", "help": "The output of the diag CLI will only be files.", "label": "Enable", "name": "enable"}, {"description": "The output of the diag CLI will be in raw text, output larger than 64KB will be in files", "help": "The output of the diag CLI will be in raw text, output larger than 64KB will be in files.", "label": "Disable", "name": "disable"}]
VALID_BODY_EXECUTE_SECURITY_FABRIC: Literal[{"description": "CLI script executes on all FortiGate units in the Security Fabric", "help": "CLI script executes on all FortiGate units in the Security Fabric.", "label": "Enable", "name": "enable"}, {"description": "CLI script executes only on the FortiGate unit that the stitch is triggered", "help": "CLI script executes only on the FortiGate unit that the stitch is triggered.", "label": "Disable", "name": "disable"}]
VALID_BODY_LOG_DEBUG_PRINT: Literal[{"description": "Enable logging debug print output from diagnose action", "help": "Enable logging debug print output from diagnose action.", "label": "Enable", "name": "enable"}, {"description": "Disable logging debug print output from diagnose action", "help": "Disable logging debug print output from diagnose action.", "label": "Disable", "name": "disable"}]

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
    "VALID_BODY_ACTION_TYPE",
    "VALID_BODY_SYSTEM_ACTION",
    "VALID_BODY_FORTICARE_EMAIL",
    "VALID_BODY_AZURE_FUNCTION_AUTHORIZATION",
    "VALID_BODY_ALICLOUD_FUNCTION_AUTHORIZATION",
    "VALID_BODY_MESSAGE_TYPE",
    "VALID_BODY_REPLACEMENT_MESSAGE",
    "VALID_BODY_PROTOCOL",
    "VALID_BODY_METHOD",
    "VALID_BODY_VERIFY_HOST_CERT",
    "VALID_BODY_FILE_ONLY",
    "VALID_BODY_EXECUTE_SECURITY_FABRIC",
    "VALID_BODY_LOG_DEBUG_PRINT",
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