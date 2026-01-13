from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_FEATURE_SET: Literal[{"description": "Flow feature set", "help": "Flow feature set.", "label": "Flow", "name": "flow"}, {"description": "Proxy feature set", "help": "Proxy feature set.", "label": "Proxy", "name": "proxy"}]
VALID_BODY_OPTIONS: Literal[{"description": "ActiveX filter", "help": "ActiveX filter.", "label": "Activexfilter", "name": "activexfilter"}, {"description": "Cookie filter", "help": "Cookie filter.", "label": "Cookiefilter", "name": "cookiefilter"}, {"description": "Java applet filter", "help": "Java applet filter.", "label": "Javafilter", "name": "javafilter"}, {"description": "Block sessions contained an invalid domain name", "help": "Block sessions contained an invalid domain name.", "label": "Block Invalid Url", "name": "block-invalid-url"}, {"description": "Javascript block", "help": "Javascript block.", "label": "Jscript", "name": "jscript"}, {"description": "JS block", "help": "JS block.", "label": "Js", "name": "js"}, {"description": "VB script block", "help": "VB script block.", "label": "Vbs", "name": "vbs"}, {"description": "Unknown script block", "help": "Unknown script block.", "label": "Unknown", "name": "unknown"}, {"description": "Intrinsic script block", "help": "Intrinsic script block.", "label": "Intrinsic", "name": "intrinsic"}, {"description": "Referring block", "help": "Referring block.", "label": "Wf Referer", "name": "wf-referer"}, {"description": "Cookie block", "help": "Cookie block.", "label": "Wf Cookie", "name": "wf-cookie"}, {"help": "Per-user block/allow list filter", "label": "Per User Bal", "name": "per-user-bal"}]
VALID_BODY_HTTPS_REPLACEMSG: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]
VALID_BODY_WEB_FLOW_LOG_ENCODING: Literal[{"description": "UTF-8 encoding", "help": "UTF-8 encoding.", "label": "Utf 8", "name": "utf-8"}, {"description": "Punycode encoding", "help": "Punycode encoding.", "label": "Punycode", "name": "punycode"}]
VALID_BODY_OVRD_PERM: Literal[{"description": "Banned word override", "help": "Banned word override.", "label": "Bannedword Override", "name": "bannedword-override"}, {"description": "URL filter override", "help": "URL filter override.", "label": "Urlfilter Override", "name": "urlfilter-override"}, {"description": "FortiGuard Web Filter override", "help": "FortiGuard Web Filter override.", "label": "Fortiguard Wf Override", "name": "fortiguard-wf-override"}, {"description": "Content-type header override", "help": "Content-type header override.", "label": "Contenttype Check Override", "name": "contenttype-check-override"}]
VALID_BODY_POST_ACTION: Literal[{"description": "Normal, POST requests are allowed", "help": "Normal, POST requests are allowed.", "label": "Normal", "name": "normal"}, {"description": "POST requests are blocked", "help": "POST requests are blocked.", "label": "Block", "name": "block"}]
VALID_BODY_WISP: Literal[{"description": "Enable web proxy WISP", "help": "Enable web proxy WISP.", "label": "Enable", "name": "enable"}, {"description": "Disable web proxy WISP", "help": "Disable web proxy WISP.", "label": "Disable", "name": "disable"}]
VALID_BODY_WISP_ALGORITHM: Literal[{"description": "Select the first healthy server in order", "help": "Select the first healthy server in order.", "label": "Primary Secondary", "name": "primary-secondary"}, {"description": "Select the next healthy server", "help": "Select the next healthy server.", "label": "Round Robin", "name": "round-robin"}, {"description": "Select the lightest loading healthy server", "help": "Select the lightest loading healthy server.", "label": "Auto Learning", "name": "auto-learning"}]
VALID_BODY_LOG_ALL_URL: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]
VALID_BODY_WEB_CONTENT_LOG: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]
VALID_BODY_WEB_FILTER_ACTIVEX_LOG: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]
VALID_BODY_WEB_FILTER_COMMAND_BLOCK_LOG: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]
VALID_BODY_WEB_FILTER_COOKIE_LOG: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]
VALID_BODY_WEB_FILTER_APPLET_LOG: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]
VALID_BODY_WEB_FILTER_JSCRIPT_LOG: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]
VALID_BODY_WEB_FILTER_JS_LOG: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]
VALID_BODY_WEB_FILTER_VBS_LOG: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]
VALID_BODY_WEB_FILTER_UNKNOWN_LOG: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]
VALID_BODY_WEB_FILTER_REFERER_LOG: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]
VALID_BODY_WEB_FILTER_COOKIE_REMOVAL_LOG: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]
VALID_BODY_WEB_URL_LOG: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]
VALID_BODY_WEB_INVALID_DOMAIN_LOG: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]
VALID_BODY_WEB_FTGD_ERR_LOG: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]
VALID_BODY_WEB_FTGD_QUOTA_USAGE: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]
VALID_BODY_EXTENDED_LOG: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]
VALID_BODY_WEB_EXTENDED_ALL_ACTION_LOG: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]
VALID_BODY_WEB_ANTIPHISHING_LOG: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]

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
    "VALID_BODY_OPTIONS",
    "VALID_BODY_HTTPS_REPLACEMSG",
    "VALID_BODY_WEB_FLOW_LOG_ENCODING",
    "VALID_BODY_OVRD_PERM",
    "VALID_BODY_POST_ACTION",
    "VALID_BODY_WISP",
    "VALID_BODY_WISP_ALGORITHM",
    "VALID_BODY_LOG_ALL_URL",
    "VALID_BODY_WEB_CONTENT_LOG",
    "VALID_BODY_WEB_FILTER_ACTIVEX_LOG",
    "VALID_BODY_WEB_FILTER_COMMAND_BLOCK_LOG",
    "VALID_BODY_WEB_FILTER_COOKIE_LOG",
    "VALID_BODY_WEB_FILTER_APPLET_LOG",
    "VALID_BODY_WEB_FILTER_JSCRIPT_LOG",
    "VALID_BODY_WEB_FILTER_JS_LOG",
    "VALID_BODY_WEB_FILTER_VBS_LOG",
    "VALID_BODY_WEB_FILTER_UNKNOWN_LOG",
    "VALID_BODY_WEB_FILTER_REFERER_LOG",
    "VALID_BODY_WEB_FILTER_COOKIE_REMOVAL_LOG",
    "VALID_BODY_WEB_URL_LOG",
    "VALID_BODY_WEB_INVALID_DOMAIN_LOG",
    "VALID_BODY_WEB_FTGD_ERR_LOG",
    "VALID_BODY_WEB_FTGD_QUOTA_USAGE",
    "VALID_BODY_EXTENDED_LOG",
    "VALID_BODY_WEB_EXTENDED_ALL_ACTION_LOG",
    "VALID_BODY_WEB_ANTIPHISHING_LOG",
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