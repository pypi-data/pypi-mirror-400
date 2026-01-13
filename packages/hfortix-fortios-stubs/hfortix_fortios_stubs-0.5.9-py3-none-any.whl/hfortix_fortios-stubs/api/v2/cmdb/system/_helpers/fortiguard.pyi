from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_FORTIGUARD_ANYCAST: Literal[{"description": "Enable use of FortiGuard\u0027s Anycast network", "help": "Enable use of FortiGuard\u0027s Anycast network.", "label": "Enable", "name": "enable"}, {"description": "Disable use of FortiGuard\u0027s Anycast network", "help": "Disable use of FortiGuard\u0027s Anycast network.", "label": "Disable", "name": "disable"}]
VALID_BODY_FORTIGUARD_ANYCAST_SOURCE: Literal[{"description": "Use Fortinet\u0027s servers to provide FortiGuard services in FortiGuard\u0027s anycast network", "help": "Use Fortinet\u0027s servers to provide FortiGuard services in FortiGuard\u0027s anycast network.", "label": "Fortinet", "name": "fortinet"}, {"description": "Use Fortinet\u0027s AWS servers to provide FortiGuard services in FortiGuard\u0027s anycast network", "help": "Use Fortinet\u0027s AWS servers to provide FortiGuard services in FortiGuard\u0027s anycast network.", "label": "Aws", "name": "aws"}, {"description": "Use Fortinet\u0027s internal test servers to provide FortiGuard services in FortiGuard\u0027s anycast network", "help": "Use Fortinet\u0027s internal test servers to provide FortiGuard services in FortiGuard\u0027s anycast network.", "label": "Debug", "name": "debug"}]
VALID_BODY_PROTOCOL: Literal[{"description": "UDP for server communication (for use by FortiGuard or FortiManager)", "help": "UDP for server communication (for use by FortiGuard or FortiManager).", "label": "Udp", "name": "udp"}, {"description": "HTTP for server communication (for use only by FortiManager)", "help": "HTTP for server communication (for use only by FortiManager).", "label": "Http", "name": "http"}, {"description": "HTTPS for server communication (for use by FortiGuard or FortiManager)", "help": "HTTPS for server communication (for use by FortiGuard or FortiManager).", "label": "Https", "name": "https"}]
VALID_BODY_PORT: Literal[{"description": "port 8888 for server communication", "help": "port 8888 for server communication.", "label": "8888", "name": "8888"}, {"description": "port 53 for server communication", "help": "port 53 for server communication.", "label": "53", "name": "53"}, {"description": "port 80 for server communication", "help": "port 80 for server communication.", "label": "80", "name": "80"}, {"description": "port 443 for server communication", "help": "port 443 for server communication.", "label": "443", "name": "443"}]
VALID_BODY_AUTO_JOIN_FORTICLOUD: Literal[{"description": "Enable automatic connection and login to FortiCloud", "help": "Enable automatic connection and login to FortiCloud.", "label": "Enable", "name": "enable"}, {"description": "Disable automatic connection and login to FortiCloud", "help": "Disable automatic connection and login to FortiCloud.", "label": "Disable", "name": "disable"}]
VALID_BODY_UPDATE_SERVER_LOCATION: Literal[{"description": "FortiGuard servers chosen based on closest proximity to FortiGate unit", "help": "FortiGuard servers chosen based on closest proximity to FortiGate unit.", "label": "Automatic", "name": "automatic"}, {"description": "FortiGuard servers in United States", "help": "FortiGuard servers in United States.", "label": "Usa", "name": "usa"}, {"description": "FortiGuard servers in the European Union", "help": "FortiGuard servers in the European Union.", "label": "Eu", "name": "eu"}]
VALID_BODY_SANDBOX_INLINE_SCAN: Literal[{"help": "Enable FortiCloud Sandbox inline scan.", "label": "Enable", "name": "enable"}, {"help": "Disable FortiCloud Sandbox inline scan.", "label": "Disable", "name": "disable"}]
VALID_BODY_UPDATE_FFDB: Literal[{"description": "Enable Internet Service Database update", "help": "Enable Internet Service Database update.", "label": "Enable", "name": "enable"}, {"description": "Disable Internet Service Database update", "help": "Disable Internet Service Database update.", "label": "Disable", "name": "disable"}]
VALID_BODY_UPDATE_UWDB: Literal[{"description": "Enable allowlist update", "help": "Enable allowlist update.", "label": "Enable", "name": "enable"}, {"description": "Disable allowlist update", "help": "Disable allowlist update.", "label": "Disable", "name": "disable"}]
VALID_BODY_UPDATE_DLDB: Literal[{"description": "Enable DLP signature update", "help": "Enable DLP signature update.", "label": "Enable", "name": "enable"}, {"description": "Disable DLP signature update", "help": "Disable DLP signature update.", "label": "Disable", "name": "disable"}]
VALID_BODY_UPDATE_EXTDB: Literal[{"description": "Enable external resource update", "help": "Enable external resource update.", "label": "Enable", "name": "enable"}, {"description": "Disable external resource update", "help": "Disable external resource update.", "label": "Disable", "name": "disable"}]
VALID_BODY_UPDATE_BUILD_PROXY: Literal[{"description": "Enable proxy dictionary rebuild", "help": "Enable proxy dictionary rebuild.", "label": "Enable", "name": "enable"}, {"description": "Disable proxy dictionary rebuild", "help": "Disable proxy dictionary rebuild.", "label": "Disable", "name": "disable"}]
VALID_BODY_PERSISTENT_CONNECTION: Literal[{"description": "Enable persistent connection to receive update notification from FortiGuard", "help": "Enable persistent connection to receive update notification from FortiGuard.", "label": "Enable", "name": "enable"}, {"description": "Disable persistent connection to receive update notification from FortiGuard", "help": "Disable persistent connection to receive update notification from FortiGuard.", "label": "Disable", "name": "disable"}]
VALID_BODY_AUTO_FIRMWARE_UPGRADE: Literal[{"description": "Enable automatic patch-level firmware upgrade to latest version from FortiGuard", "help": "Enable automatic patch-level firmware upgrade to latest version from FortiGuard.", "label": "Enable", "name": "enable"}, {"description": "Disable automatic patch-level firmware upgrade to latest version from FortiGuard", "help": "Disable automatic patch-level firmware upgrade to latest version from FortiGuard.", "label": "Disable", "name": "disable"}]
VALID_BODY_AUTO_FIRMWARE_UPGRADE_DAY: Literal[{"description": "Sunday", "help": "Sunday.", "label": "Sunday", "name": "sunday"}, {"description": "Monday", "help": "Monday.", "label": "Monday", "name": "monday"}, {"description": "Tuesday", "help": "Tuesday.", "label": "Tuesday", "name": "tuesday"}, {"description": "Wednesday", "help": "Wednesday.", "label": "Wednesday", "name": "wednesday"}, {"description": "Thursday", "help": "Thursday.", "label": "Thursday", "name": "thursday"}, {"description": "Friday", "help": "Friday.", "label": "Friday", "name": "friday"}, {"description": "Saturday", "help": "Saturday.", "label": "Saturday", "name": "saturday"}]
VALID_BODY_SUBSCRIBE_UPDATE_NOTIFICATION: Literal[{"description": "Enable subscription to receive update notification from FortiGuard", "help": "Enable subscription to receive update notification from FortiGuard.", "label": "Enable", "name": "enable"}, {"description": "Disable subscription to receive update notification from FortiGuard", "help": "Disable subscription to receive update notification from FortiGuard.", "label": "Disable", "name": "disable"}]
VALID_BODY_ANTISPAM_FORCE_OFF: Literal[{"description": "Turn off the FortiGuard antispam service", "help": "Turn off the FortiGuard antispam service.", "label": "Enable", "name": "enable"}, {"description": "Allow the FortiGuard antispam service", "help": "Allow the FortiGuard antispam service.", "label": "Disable", "name": "disable"}]
VALID_BODY_ANTISPAM_CACHE: Literal[{"description": "Enable FortiGuard antispam request caching", "help": "Enable FortiGuard antispam request caching.", "label": "Enable", "name": "enable"}, {"description": "Disable FortiGuard antispam request caching", "help": "Disable FortiGuard antispam request caching.", "label": "Disable", "name": "disable"}]
VALID_BODY_OUTBREAK_PREVENTION_FORCE_OFF: Literal[{"description": "Turn off FortiGuard antivirus service", "help": "Turn off FortiGuard antivirus service.", "label": "Enable", "name": "enable"}, {"description": "Allow the FortiGuard antivirus service", "help": "Allow the FortiGuard antivirus service.", "label": "Disable", "name": "disable"}]
VALID_BODY_OUTBREAK_PREVENTION_CACHE: Literal[{"description": "Enable FortiGuard antivirus caching", "help": "Enable FortiGuard antivirus caching.", "label": "Enable", "name": "enable"}, {"description": "Disable FortiGuard antivirus caching", "help": "Disable FortiGuard antivirus caching.", "label": "Disable", "name": "disable"}]
VALID_BODY_WEBFILTER_FORCE_OFF: Literal[{"description": "Turn off the FortiGuard web filtering service", "help": "Turn off the FortiGuard web filtering service.", "label": "Enable", "name": "enable"}, {"description": "Allow the FortiGuard web filtering service to operate", "help": "Allow the FortiGuard web filtering service to operate.", "label": "Disable", "name": "disable"}]
VALID_BODY_WEBFILTER_CACHE: Literal[{"description": "Enable FortiGuard web filter caching", "help": "Enable FortiGuard web filter caching.", "label": "Enable", "name": "enable"}, {"description": "Disable FortiGuard web filter caching", "help": "Disable FortiGuard web filter caching.", "label": "Disable", "name": "disable"}]
VALID_BODY_SDNS_OPTIONS: Literal[{"description": "Include DNS question section in the FortiGuard DNS setup message", "help": "Include DNS question section in the FortiGuard DNS setup message.", "label": "Include Question Section", "name": "include-question-section"}]
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
    "VALID_BODY_FORTIGUARD_ANYCAST",
    "VALID_BODY_FORTIGUARD_ANYCAST_SOURCE",
    "VALID_BODY_PROTOCOL",
    "VALID_BODY_PORT",
    "VALID_BODY_AUTO_JOIN_FORTICLOUD",
    "VALID_BODY_UPDATE_SERVER_LOCATION",
    "VALID_BODY_SANDBOX_INLINE_SCAN",
    "VALID_BODY_UPDATE_FFDB",
    "VALID_BODY_UPDATE_UWDB",
    "VALID_BODY_UPDATE_DLDB",
    "VALID_BODY_UPDATE_EXTDB",
    "VALID_BODY_UPDATE_BUILD_PROXY",
    "VALID_BODY_PERSISTENT_CONNECTION",
    "VALID_BODY_AUTO_FIRMWARE_UPGRADE",
    "VALID_BODY_AUTO_FIRMWARE_UPGRADE_DAY",
    "VALID_BODY_SUBSCRIBE_UPDATE_NOTIFICATION",
    "VALID_BODY_ANTISPAM_FORCE_OFF",
    "VALID_BODY_ANTISPAM_CACHE",
    "VALID_BODY_OUTBREAK_PREVENTION_FORCE_OFF",
    "VALID_BODY_OUTBREAK_PREVENTION_CACHE",
    "VALID_BODY_WEBFILTER_FORCE_OFF",
    "VALID_BODY_WEBFILTER_CACHE",
    "VALID_BODY_SDNS_OPTIONS",
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