from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_SCOPE: Literal[{"description": "VDOM access", "help": "VDOM access.", "label": "Vdom", "name": "vdom"}, {"description": "Global access", "help": "Global access.", "label": "Global", "name": "global"}]
VALID_BODY_SECFABGRP: Literal[{"description": "No access", "help": "No access.", "label": "None", "name": "none"}, {"description": "Read access", "help": "Read access.", "label": "Read", "name": "read"}, {"description": "Read/write access", "help": "Read/write access.", "label": "Read Write", "name": "read-write"}, {"description": "Customized access", "help": "Customized access.", "label": "Custom", "name": "custom"}]
VALID_BODY_FTVIEWGRP: Literal[{"description": "No access", "help": "No access.", "label": "None", "name": "none"}, {"description": "Read access", "help": "Read access.", "label": "Read", "name": "read"}, {"description": "Read/write access", "help": "Read/write access.", "label": "Read Write", "name": "read-write"}]
VALID_BODY_AUTHGRP: Literal[{"description": "No access", "help": "No access.", "label": "None", "name": "none"}, {"description": "Read access", "help": "Read access.", "label": "Read", "name": "read"}, {"description": "Read/write access", "help": "Read/write access.", "label": "Read Write", "name": "read-write"}]
VALID_BODY_SYSGRP: Literal[{"description": "No access", "help": "No access.", "label": "None", "name": "none"}, {"description": "Read access", "help": "Read access.", "label": "Read", "name": "read"}, {"description": "Read/write access", "help": "Read/write access.", "label": "Read Write", "name": "read-write"}, {"description": "Customized access", "help": "Customized access.", "label": "Custom", "name": "custom"}]
VALID_BODY_NETGRP: Literal[{"description": "No access", "help": "No access.", "label": "None", "name": "none"}, {"description": "Read access", "help": "Read access.", "label": "Read", "name": "read"}, {"description": "Read/write access", "help": "Read/write access.", "label": "Read Write", "name": "read-write"}, {"description": "Customized access", "help": "Customized access.", "label": "Custom", "name": "custom"}]
VALID_BODY_LOGGRP: Literal[{"description": "No access", "help": "No access.", "label": "None", "name": "none"}, {"description": "Read access", "help": "Read access.", "label": "Read", "name": "read"}, {"description": "Read/write access", "help": "Read/write access.", "label": "Read Write", "name": "read-write"}, {"description": "Customized access", "help": "Customized access.", "label": "Custom", "name": "custom"}]
VALID_BODY_FWGRP: Literal[{"description": "No access", "help": "No access.", "label": "None", "name": "none"}, {"description": "Read access", "help": "Read access.", "label": "Read", "name": "read"}, {"description": "Read/write access", "help": "Read/write access.", "label": "Read Write", "name": "read-write"}, {"description": "Customized access", "help": "Customized access.", "label": "Custom", "name": "custom"}]
VALID_BODY_VPNGRP: Literal[{"description": "No access", "help": "No access.", "label": "None", "name": "none"}, {"description": "Read access", "help": "Read access.", "label": "Read", "name": "read"}, {"description": "Read/write access", "help": "Read/write access.", "label": "Read Write", "name": "read-write"}]
VALID_BODY_UTMGRP: Literal[{"description": "No access", "help": "No access.", "label": "None", "name": "none"}, {"description": "Read access", "help": "Read access.", "label": "Read", "name": "read"}, {"description": "Read/write access", "help": "Read/write access.", "label": "Read Write", "name": "read-write"}, {"description": "Customized access", "help": "Customized access.", "label": "Custom", "name": "custom"}]
VALID_BODY_WANOPTGRP: Literal[{"help": "No access.", "label": "None", "name": "none"}, {"help": "Read access.", "label": "Read", "name": "read"}, {"help": "Read/write access.", "label": "Read Write", "name": "read-write"}]
VALID_BODY_WIFI: Literal[{"description": "No access", "help": "No access.", "label": "None", "name": "none"}, {"description": "Read access", "help": "Read access.", "label": "Read", "name": "read"}, {"description": "Read/write access", "help": "Read/write access.", "label": "Read Write", "name": "read-write"}]
VALID_BODY_ADMINTIMEOUT_OVERRIDE: Literal[{"description": "Enable overriding the global administrator idle timeout", "help": "Enable overriding the global administrator idle timeout.", "label": "Enable", "name": "enable"}, {"description": "Disable overriding the global administrator idle timeout", "help": "Disable overriding the global administrator idle timeout.", "label": "Disable", "name": "disable"}]
VALID_BODY_CLI_DIAGNOSE: Literal[{"description": "Enable permission to run diagnostic commands", "help": "Enable permission to run diagnostic commands.", "label": "Enable", "name": "enable"}, {"description": "Disable permission to run diagnostic commands", "help": "Disable permission to run diagnostic commands.", "label": "Disable", "name": "disable"}]
VALID_BODY_CLI_GET: Literal[{"description": "Enable permission to run get commands", "help": "Enable permission to run get commands.", "label": "Enable", "name": "enable"}, {"description": "Disable permission to run get commands", "help": "Disable permission to run get commands.", "label": "Disable", "name": "disable"}]
VALID_BODY_CLI_SHOW: Literal[{"description": "Enable permission to run show commands", "help": "Enable permission to run show commands.", "label": "Enable", "name": "enable"}, {"description": "Disable permission to run show commands", "help": "Disable permission to run show commands.", "label": "Disable", "name": "disable"}]
VALID_BODY_CLI_EXEC: Literal[{"description": "Enable permission to run execute commands", "help": "Enable permission to run execute commands.", "label": "Enable", "name": "enable"}, {"description": "Disable permission to run execute commands", "help": "Disable permission to run execute commands.", "label": "Disable", "name": "disable"}]
VALID_BODY_CLI_CONFIG: Literal[{"description": "Enable permission to run config commands", "help": "Enable permission to run config commands.", "label": "Enable", "name": "enable"}, {"description": "Disable permission to run config commands", "help": "Disable permission to run config commands.", "label": "Disable", "name": "disable"}]
VALID_BODY_SYSTEM_EXECUTE_SSH: Literal[{"description": "Enable permission to execute SSH commands", "help": "Enable permission to execute SSH commands.", "label": "Enable", "name": "enable"}, {"description": "Disable permission to execute SSH commands", "help": "Disable permission to execute SSH commands.", "label": "Disable", "name": "disable"}]
VALID_BODY_SYSTEM_EXECUTE_TELNET: Literal[{"description": "Enable permission to execute TELNET commands", "help": "Enable permission to execute TELNET commands.", "label": "Enable", "name": "enable"}, {"description": "Disable permission to execute TELNET commands", "help": "Disable permission to execute TELNET commands.", "label": "Disable", "name": "disable"}]

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
    "VALID_BODY_SCOPE",
    "VALID_BODY_SECFABGRP",
    "VALID_BODY_FTVIEWGRP",
    "VALID_BODY_AUTHGRP",
    "VALID_BODY_SYSGRP",
    "VALID_BODY_NETGRP",
    "VALID_BODY_LOGGRP",
    "VALID_BODY_FWGRP",
    "VALID_BODY_VPNGRP",
    "VALID_BODY_UTMGRP",
    "VALID_BODY_WANOPTGRP",
    "VALID_BODY_WIFI",
    "VALID_BODY_ADMINTIMEOUT_OVERRIDE",
    "VALID_BODY_CLI_DIAGNOSE",
    "VALID_BODY_CLI_GET",
    "VALID_BODY_CLI_SHOW",
    "VALID_BODY_CLI_EXEC",
    "VALID_BODY_CLI_CONFIG",
    "VALID_BODY_SYSTEM_EXECUTE_SSH",
    "VALID_BODY_SYSTEM_EXECUTE_TELNET",
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