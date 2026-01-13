from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_PROXY: Literal[{"description": "Explicit Web Proxy    transparent-web:Transparent Web Proxy    ftp:Explicit FTP Proxy    ssh:SSH Proxy    ssh-tunnel:SSH Tunnel    access-proxy:Access Proxy    ztna-proxy:ZTNA Proxy", "help": "Explicit Web Proxy", "label": "Explicit Web", "name": "explicit-web"}, {"help": "Transparent Web Proxy", "label": "Transparent Web", "name": "transparent-web"}, {"help": "Explicit FTP Proxy", "label": "Ftp", "name": "ftp"}, {"help": "SSH Proxy", "label": "Ssh", "name": "ssh"}, {"help": "SSH Tunnel", "label": "Ssh Tunnel", "name": "ssh-tunnel"}, {"help": "Access Proxy", "label": "Access Proxy", "name": "access-proxy"}, {"help": "ZTNA Proxy", "label": "Ztna Proxy", "name": "ztna-proxy"}, {"help": "WANopt Tunnel", "label": "Wanopt", "name": "wanopt"}]
VALID_BODY_ZTNA_TAGS_MATCH_LOGIC: Literal[{"description": "Match ZTNA tags using a logical OR operator", "help": "Match ZTNA tags using a logical OR operator.", "label": "Or", "name": "or"}, {"description": "Match ZTNA tags using a logical AND operator", "help": "Match ZTNA tags using a logical AND operator.", "label": "And", "name": "and"}]
VALID_BODY_DEVICE_OWNERSHIP: Literal[{"description": "Enable device ownership", "help": "Enable device ownership.", "label": "Enable", "name": "enable"}, {"description": "Disable device ownership", "help": "Disable device ownership.", "label": "Disable", "name": "disable"}]
VALID_BODY_INTERNET_SERVICE: Literal[{"description": "Enable use of Internet Services in policy", "help": "Enable use of Internet Services in policy.", "label": "Enable", "name": "enable"}, {"description": "Disable use of Internet Services in policy", "help": "Disable use of Internet Services in policy.", "label": "Disable", "name": "disable"}]
VALID_BODY_INTERNET_SERVICE_NEGATE: Literal[{"description": "Enable negated Internet Service match", "help": "Enable negated Internet Service match.", "label": "Enable", "name": "enable"}, {"description": "Disable negated Internet Service match", "help": "Disable negated Internet Service match.", "label": "Disable", "name": "disable"}]
VALID_BODY_INTERNET_SERVICE6: Literal[{"description": "Enable use of IPv6 Internet Services in policy", "help": "Enable use of IPv6 Internet Services in policy.", "label": "Enable", "name": "enable"}, {"description": "Disable use of IPv6 Internet Services in policy", "help": "Disable use of IPv6 Internet Services in policy.", "label": "Disable", "name": "disable"}]
VALID_BODY_INTERNET_SERVICE6_NEGATE: Literal[{"description": "Enable negated IPv6 Internet Service match", "help": "Enable negated IPv6 Internet Service match.", "label": "Enable", "name": "enable"}, {"description": "Disable negated IPv6 Internet Service match", "help": "Disable negated IPv6 Internet Service match.", "label": "Disable", "name": "disable"}]
VALID_BODY_SRCADDR_NEGATE: Literal[{"description": "Enable source address negate", "help": "Enable source address negate.", "label": "Enable", "name": "enable"}, {"description": "Disable destination address negate", "help": "Disable destination address negate.", "label": "Disable", "name": "disable"}]
VALID_BODY_DSTADDR_NEGATE: Literal[{"description": "Enable source address negate", "help": "Enable source address negate.", "label": "Enable", "name": "enable"}, {"description": "Disable destination address negate", "help": "Disable destination address negate.", "label": "Disable", "name": "disable"}]
VALID_BODY_ZTNA_EMS_TAG_NEGATE: Literal[{"description": "Enable ZTNA EMS tags negate", "help": "Enable ZTNA EMS tags negate.", "label": "Enable", "name": "enable"}, {"description": "Disable ZTNA EMS tags negate", "help": "Disable ZTNA EMS tags negate.", "label": "Disable", "name": "disable"}]
VALID_BODY_SERVICE_NEGATE: Literal[{"description": "Enable negated service match", "help": "Enable negated service match.", "label": "Enable", "name": "enable"}, {"description": "Disable negated service match", "help": "Disable negated service match.", "label": "Disable", "name": "disable"}]
VALID_BODY_ACTION: Literal[{"description": "Action accept", "help": "Action accept.", "label": "Accept", "name": "accept"}, {"description": "Action deny", "help": "Action deny.", "label": "Deny", "name": "deny"}, {"description": "Action redirect", "help": "Action redirect.", "label": "Redirect", "name": "redirect"}, {"description": "Action isolate", "help": "Action isolate.", "label": "Isolate", "name": "isolate"}]
VALID_BODY_STATUS: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]
VALID_BODY_LOGTRAFFIC: Literal[{"description": "Log all sessions", "help": "Log all sessions.", "label": "All", "name": "all"}, {"description": "UTM event and matched application traffic log", "help": "UTM event and matched application traffic log.", "label": "Utm", "name": "utm"}, {"description": "Disable traffic and application log", "help": "Disable traffic and application log.", "label": "Disable", "name": "disable"}]
VALID_BODY_HTTP_TUNNEL_AUTH: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]
VALID_BODY_SSH_POLICY_REDIRECT: Literal[{"description": "Enable SSH policy redirect", "help": "Enable SSH policy redirect.", "label": "Enable", "name": "enable"}, {"description": "Disable SSH policy redirect", "help": "Disable SSH policy redirect.", "label": "Disable", "name": "disable"}]
VALID_BODY_TRANSPARENT: Literal[{"description": "Enable use of IP address of client to connect to server", "help": "Enable use of IP address of client to connect to server.", "label": "Enable", "name": "enable"}, {"description": "Disable use of IP address of client to connect to server", "help": "Disable use of IP address of client to connect to server.", "label": "Disable", "name": "disable"}]
VALID_BODY_WEBCACHE: Literal[{"help": "Enable setting.", "label": "Enable", "name": "enable"}, {"help": "Disable setting.", "label": "Disable", "name": "disable"}]
VALID_BODY_WEBCACHE_HTTPS: Literal[{"help": "Disable web cache for HTTPS.", "label": "Disable", "name": "disable"}, {"help": "Enable web cache for HTTPS.", "label": "Enable", "name": "enable"}]
VALID_BODY_DISCLAIMER: Literal[{"description": "Disable disclaimer", "help": "Disable disclaimer.", "label": "Disable", "name": "disable"}, {"description": "Display disclaimer for domain    policy:Display disclaimer for policy    user:Display disclaimer for current user", "help": "Display disclaimer for domain", "label": "Domain", "name": "domain"}, {"help": "Display disclaimer for policy", "label": "Policy", "name": "policy"}, {"help": "Display disclaimer for current user", "label": "User", "name": "user"}]
VALID_BODY_UTM_STATUS: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]
VALID_BODY_PROFILE_TYPE: Literal[{"description": "Do not allow security profile groups", "help": "Do not allow security profile groups.", "label": "Single", "name": "single"}, {"description": "Allow security profile groups", "help": "Allow security profile groups.", "label": "Group", "name": "group"}]
VALID_BODY_LOGTRAFFIC_START: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]
VALID_BODY_LOG_HTTP_TRANSACTION: Literal[{"description": "Enable HTTP transaction log", "help": "Enable HTTP transaction log.", "label": "Enable", "name": "enable"}, {"description": "Disable HTTP transaction log", "help": "Disable HTTP transaction log.", "label": "Disable", "name": "disable"}]
VALID_BODY_BLOCK_NOTIFICATION: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]
VALID_BODY_HTTPS_SUB_CATEGORY: Literal[{"description": "Enable HTTPS sub-category policy matching", "help": "Enable HTTPS sub-category policy matching.", "label": "Enable", "name": "enable"}, {"description": "Disable HTTPS sub-category policy matching", "help": "Disable HTTPS sub-category policy matching.", "label": "Disable", "name": "disable"}]
VALID_BODY_DETECT_HTTPS_IN_HTTP_REQUEST: Literal[{"description": "Enable detection of HTTPS in HTTP request", "help": "Enable detection of HTTPS in HTTP request.", "label": "Enable", "name": "enable"}, {"description": "Disable detection of HTTPS in HTTP request", "help": "Disable detection of HTTPS in HTTP request.", "label": "Disable", "name": "disable"}]

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
    "VALID_BODY_PROXY",
    "VALID_BODY_ZTNA_TAGS_MATCH_LOGIC",
    "VALID_BODY_DEVICE_OWNERSHIP",
    "VALID_BODY_INTERNET_SERVICE",
    "VALID_BODY_INTERNET_SERVICE_NEGATE",
    "VALID_BODY_INTERNET_SERVICE6",
    "VALID_BODY_INTERNET_SERVICE6_NEGATE",
    "VALID_BODY_SRCADDR_NEGATE",
    "VALID_BODY_DSTADDR_NEGATE",
    "VALID_BODY_ZTNA_EMS_TAG_NEGATE",
    "VALID_BODY_SERVICE_NEGATE",
    "VALID_BODY_ACTION",
    "VALID_BODY_STATUS",
    "VALID_BODY_LOGTRAFFIC",
    "VALID_BODY_HTTP_TUNNEL_AUTH",
    "VALID_BODY_SSH_POLICY_REDIRECT",
    "VALID_BODY_TRANSPARENT",
    "VALID_BODY_WEBCACHE",
    "VALID_BODY_WEBCACHE_HTTPS",
    "VALID_BODY_DISCLAIMER",
    "VALID_BODY_UTM_STATUS",
    "VALID_BODY_PROFILE_TYPE",
    "VALID_BODY_LOGTRAFFIC_START",
    "VALID_BODY_LOG_HTTP_TRANSACTION",
    "VALID_BODY_BLOCK_NOTIFICATION",
    "VALID_BODY_HTTPS_SUB_CATEGORY",
    "VALID_BODY_DETECT_HTTPS_IN_HTTP_REQUEST",
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