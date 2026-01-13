from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_REQUEST: Literal[{"description": "Disable HTTP request passing to ICAP server", "help": "Disable HTTP request passing to ICAP server.", "label": "Disable", "name": "disable"}, {"description": "Enable HTTP request passing to ICAP server", "help": "Enable HTTP request passing to ICAP server.", "label": "Enable", "name": "enable"}]
VALID_BODY_RESPONSE: Literal[{"description": "Disable HTTP response passing to ICAP server", "help": "Disable HTTP response passing to ICAP server.", "label": "Disable", "name": "disable"}, {"description": "Enable HTTP response passing to ICAP server", "help": "Enable HTTP response passing to ICAP server.", "label": "Enable", "name": "enable"}]
VALID_BODY_FILE_TRANSFER: Literal[{"description": "Forward file transfer with SSH protocol to ICAP server for further processing", "help": "Forward file transfer with SSH protocol to ICAP server for further processing.", "label": "Ssh", "name": "ssh"}, {"description": "Forward file transfer with FTP protocol to ICAP server for further processing", "help": "Forward file transfer with FTP protocol to ICAP server for further processing.", "label": "Ftp", "name": "ftp"}]
VALID_BODY_STREAMING_CONTENT_BYPASS: Literal[{"description": "Disable bypassing of ICAP server for streaming content", "help": "Disable bypassing of ICAP server for streaming content.", "label": "Disable", "name": "disable"}, {"description": "Enable bypassing of ICAP server for streaming content", "help": "Enable bypassing of ICAP server for streaming content.", "label": "Enable", "name": "enable"}]
VALID_BODY_OCR_ONLY: Literal[{"description": "Disable this FortiGate unit to submit only OCR interested content to the ICAP server", "help": "Disable this FortiGate unit to submit only OCR interested content to the ICAP server.", "label": "Disable", "name": "disable"}, {"description": "Enable this FortiGate unit to submit only OCR interested content to the ICAP server", "help": "Enable this FortiGate unit to submit only OCR interested content to the ICAP server.", "label": "Enable", "name": "enable"}]
VALID_BODY_204_RESPONSE: Literal[{"description": "Disable allowance of 204 response from ICAP server", "help": "Disable allowance of 204 response from ICAP server.", "label": "Disable", "name": "disable"}, {"description": "Enable allowance of 204 response from ICAP server", "help": "Enable allowance of 204 response from ICAP server.", "label": "Enable", "name": "enable"}]
VALID_BODY_PREVIEW: Literal[{"description": "Disable preview of data to ICAP server", "help": "Disable preview of data to ICAP server.", "label": "Disable", "name": "disable"}, {"description": "Enable preview of data to ICAP server", "help": "Enable preview of data to ICAP server.", "label": "Enable", "name": "enable"}]
VALID_BODY_REQUEST_FAILURE: Literal[{"description": "Error", "help": "Error.", "label": "Error", "name": "error"}, {"description": "Bypass", "help": "Bypass.", "label": "Bypass", "name": "bypass"}]
VALID_BODY_RESPONSE_FAILURE: Literal[{"description": "Error", "help": "Error.", "label": "Error", "name": "error"}, {"description": "Bypass", "help": "Bypass.", "label": "Bypass", "name": "bypass"}]
VALID_BODY_FILE_TRANSFER_FAILURE: Literal[{"description": "Error", "help": "Error.", "label": "Error", "name": "error"}, {"description": "Bypass", "help": "Bypass.", "label": "Bypass", "name": "bypass"}]
VALID_BODY_METHODS: Literal[{"description": "Forward HTTP request or response with DELETE method to ICAP server for further processing", "help": "Forward HTTP request or response with DELETE method to ICAP server for further processing.", "label": "Delete", "name": "delete"}, {"description": "Forward HTTP request or response with GET method to ICAP server for further processing", "help": "Forward HTTP request or response with GET method to ICAP server for further processing.", "label": "Get", "name": "get"}, {"description": "Forward HTTP request or response with HEAD method to ICAP server for further processing", "help": "Forward HTTP request or response with HEAD method to ICAP server for further processing.", "label": "Head", "name": "head"}, {"description": "Forward HTTP request or response with OPTIONS method to ICAP server for further processing", "help": "Forward HTTP request or response with OPTIONS method to ICAP server for further processing.", "label": "Options", "name": "options"}, {"description": "Forward HTTP request or response with POST method to ICAP server for further processing", "help": "Forward HTTP request or response with POST method to ICAP server for further processing.", "label": "Post", "name": "post"}, {"description": "Forward HTTP request or response with PUT method to ICAP server for further processing", "help": "Forward HTTP request or response with PUT method to ICAP server for further processing.", "label": "Put", "name": "put"}, {"description": "Forward HTTP request or response with TRACE method to ICAP server for further processing", "help": "Forward HTTP request or response with TRACE method to ICAP server for further processing.", "label": "Trace", "name": "trace"}, {"description": "Forward HTTP request or response with CONNECT method to ICAP server for further processing", "help": "Forward HTTP request or response with CONNECT method to ICAP server for further processing.", "label": "Connect", "name": "connect"}, {"description": "Forward HTTP request or response with All other methods to ICAP server for further processing", "help": "Forward HTTP request or response with All other methods to ICAP server for further processing.", "label": "Other", "name": "other"}]
VALID_BODY_RESPONSE_REQ_HDR: Literal[{"description": "Do not add req-hdr for response modification (respmod) processing", "help": "Do not add req-hdr for response modification (respmod) processing.", "label": "Disable", "name": "disable"}, {"description": "Add req-hdr for response modification (respmod) processing", "help": "Add req-hdr for response modification (respmod) processing.", "label": "Enable", "name": "enable"}]
VALID_BODY_RESPMOD_DEFAULT_ACTION: Literal[{"description": "Forward response to ICAP server unless a rule specifies not to", "help": "Forward response to ICAP server unless a rule specifies not to.", "label": "Forward", "name": "forward"}, {"description": "Don\u0027t forward request to ICAP server unless a rule specifies to forward the request", "help": "Don\u0027t forward request to ICAP server unless a rule specifies to forward the request.", "label": "Bypass", "name": "bypass"}]
VALID_BODY_ICAP_BLOCK_LOG: Literal[{"description": "Disable UTM log when infection found", "help": "Disable UTM log when infection found.", "label": "Disable", "name": "disable"}, {"description": "Enable UTM log when infection found", "help": "Enable UTM log when infection found.", "label": "Enable", "name": "enable"}]
VALID_BODY_CHUNK_ENCAP: Literal[{"description": "Do not encapsulate chunked data", "help": "Do not encapsulate chunked data.", "label": "Disable", "name": "disable"}, {"description": "Encapsulate chunked data into a new chunk", "help": "Encapsulate chunked data into a new chunk.", "label": "Enable", "name": "enable"}]
VALID_BODY_EXTENSION_FEATURE: Literal[{"description": "Support X-Scan-Progress-Interval ICAP header", "help": "Support X-Scan-Progress-Interval ICAP header.", "label": "Scan Progress", "name": "scan-progress"}]

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
    "VALID_BODY_REQUEST",
    "VALID_BODY_RESPONSE",
    "VALID_BODY_FILE_TRANSFER",
    "VALID_BODY_STREAMING_CONTENT_BYPASS",
    "VALID_BODY_OCR_ONLY",
    "VALID_BODY_204_RESPONSE",
    "VALID_BODY_PREVIEW",
    "VALID_BODY_REQUEST_FAILURE",
    "VALID_BODY_RESPONSE_FAILURE",
    "VALID_BODY_FILE_TRANSFER_FAILURE",
    "VALID_BODY_METHODS",
    "VALID_BODY_RESPONSE_REQ_HDR",
    "VALID_BODY_RESPMOD_DEFAULT_ACTION",
    "VALID_BODY_ICAP_BLOCK_LOG",
    "VALID_BODY_CHUNK_ENCAP",
    "VALID_BODY_EXTENSION_FEATURE",
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