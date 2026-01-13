from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class ProfilePayload(TypedDict, total=False):
    """
    Type hints for icap/profile payload fields.
    
    Configure ICAP profiles.
    
    **Related Resources:**

    Dependencies (resources this endpoint references):
        - :class:`~.icap.server.ServerEndpoint` (via: file-transfer-server, request-server, response-server)
        - :class:`~.icap.server-group.ServerGroupEndpoint` (via: file-transfer-server, request-server, response-server)
        - :class:`~.system.replacemsg-group.ReplacemsgGroupEndpoint` (via: replacemsg-group)

    **Usage:**
        payload: ProfilePayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    replacemsg_group: NotRequired[str]  # Replacement message group.
    name: NotRequired[str]  # ICAP profile name.
    comment: NotRequired[str]  # Comment.
    request: NotRequired[Literal[{"description": "Disable HTTP request passing to ICAP server", "help": "Disable HTTP request passing to ICAP server.", "label": "Disable", "name": "disable"}, {"description": "Enable HTTP request passing to ICAP server", "help": "Enable HTTP request passing to ICAP server.", "label": "Enable", "name": "enable"}]]  # Enable/disable whether an HTTP request is passed to an ICAP 
    response: NotRequired[Literal[{"description": "Disable HTTP response passing to ICAP server", "help": "Disable HTTP response passing to ICAP server.", "label": "Disable", "name": "disable"}, {"description": "Enable HTTP response passing to ICAP server", "help": "Enable HTTP response passing to ICAP server.", "label": "Enable", "name": "enable"}]]  # Enable/disable whether an HTTP response is passed to an ICAP
    file_transfer: NotRequired[Literal[{"description": "Forward file transfer with SSH protocol to ICAP server for further processing", "help": "Forward file transfer with SSH protocol to ICAP server for further processing.", "label": "Ssh", "name": "ssh"}, {"description": "Forward file transfer with FTP protocol to ICAP server for further processing", "help": "Forward file transfer with FTP protocol to ICAP server for further processing.", "label": "Ftp", "name": "ftp"}]]  # Configure the file transfer protocols to pass transferred fi
    streaming_content_bypass: NotRequired[Literal[{"description": "Disable bypassing of ICAP server for streaming content", "help": "Disable bypassing of ICAP server for streaming content.", "label": "Disable", "name": "disable"}, {"description": "Enable bypassing of ICAP server for streaming content", "help": "Enable bypassing of ICAP server for streaming content.", "label": "Enable", "name": "enable"}]]  # Enable/disable bypassing of ICAP server for streaming conten
    ocr_only: NotRequired[Literal[{"description": "Disable this FortiGate unit to submit only OCR interested content to the ICAP server", "help": "Disable this FortiGate unit to submit only OCR interested content to the ICAP server.", "label": "Disable", "name": "disable"}, {"description": "Enable this FortiGate unit to submit only OCR interested content to the ICAP server", "help": "Enable this FortiGate unit to submit only OCR interested content to the ICAP server.", "label": "Enable", "name": "enable"}]]  # Enable/disable this FortiGate unit to submit only OCR intere
    size_limit_204: NotRequired[int]  # 204 response size limit to be saved by ICAP client in megaby
    response_204: NotRequired[Literal[{"description": "Disable allowance of 204 response from ICAP server", "help": "Disable allowance of 204 response from ICAP server.", "label": "Disable", "name": "disable"}, {"description": "Enable allowance of 204 response from ICAP server", "help": "Enable allowance of 204 response from ICAP server.", "label": "Enable", "name": "enable"}]]  # Enable/disable allowance of 204 response from ICAP server.
    preview: NotRequired[Literal[{"description": "Disable preview of data to ICAP server", "help": "Disable preview of data to ICAP server.", "label": "Disable", "name": "disable"}, {"description": "Enable preview of data to ICAP server", "help": "Enable preview of data to ICAP server.", "label": "Enable", "name": "enable"}]]  # Enable/disable preview of data to ICAP server.
    preview_data_length: NotRequired[int]  # Preview data length to be sent to ICAP server.
    request_server: str  # ICAP server to use for an HTTP request.
    response_server: str  # ICAP server to use for an HTTP response.
    file_transfer_server: str  # ICAP server to use for a file transfer.
    request_failure: NotRequired[Literal[{"description": "Error", "help": "Error.", "label": "Error", "name": "error"}, {"description": "Bypass", "help": "Bypass.", "label": "Bypass", "name": "bypass"}]]  # Action to take if the ICAP server cannot be contacted when p
    response_failure: NotRequired[Literal[{"description": "Error", "help": "Error.", "label": "Error", "name": "error"}, {"description": "Bypass", "help": "Bypass.", "label": "Bypass", "name": "bypass"}]]  # Action to take if the ICAP server cannot be contacted when p
    file_transfer_failure: NotRequired[Literal[{"description": "Error", "help": "Error.", "label": "Error", "name": "error"}, {"description": "Bypass", "help": "Bypass.", "label": "Bypass", "name": "bypass"}]]  # Action to take if the ICAP server cannot be contacted when p
    request_path: NotRequired[str]  # Path component of the ICAP URI that identifies the HTTP requ
    response_path: NotRequired[str]  # Path component of the ICAP URI that identifies the HTTP resp
    file_transfer_path: NotRequired[str]  # Path component of the ICAP URI that identifies the file tran
    methods: NotRequired[Literal[{"description": "Forward HTTP request or response with DELETE method to ICAP server for further processing", "help": "Forward HTTP request or response with DELETE method to ICAP server for further processing.", "label": "Delete", "name": "delete"}, {"description": "Forward HTTP request or response with GET method to ICAP server for further processing", "help": "Forward HTTP request or response with GET method to ICAP server for further processing.", "label": "Get", "name": "get"}, {"description": "Forward HTTP request or response with HEAD method to ICAP server for further processing", "help": "Forward HTTP request or response with HEAD method to ICAP server for further processing.", "label": "Head", "name": "head"}, {"description": "Forward HTTP request or response with OPTIONS method to ICAP server for further processing", "help": "Forward HTTP request or response with OPTIONS method to ICAP server for further processing.", "label": "Options", "name": "options"}, {"description": "Forward HTTP request or response with POST method to ICAP server for further processing", "help": "Forward HTTP request or response with POST method to ICAP server for further processing.", "label": "Post", "name": "post"}, {"description": "Forward HTTP request or response with PUT method to ICAP server for further processing", "help": "Forward HTTP request or response with PUT method to ICAP server for further processing.", "label": "Put", "name": "put"}, {"description": "Forward HTTP request or response with TRACE method to ICAP server for further processing", "help": "Forward HTTP request or response with TRACE method to ICAP server for further processing.", "label": "Trace", "name": "trace"}, {"description": "Forward HTTP request or response with CONNECT method to ICAP server for further processing", "help": "Forward HTTP request or response with CONNECT method to ICAP server for further processing.", "label": "Connect", "name": "connect"}, {"description": "Forward HTTP request or response with All other methods to ICAP server for further processing", "help": "Forward HTTP request or response with All other methods to ICAP server for further processing.", "label": "Other", "name": "other"}]]  # The allowed HTTP methods that will be sent to ICAP server fo
    response_req_hdr: NotRequired[Literal[{"description": "Do not add req-hdr for response modification (respmod) processing", "help": "Do not add req-hdr for response modification (respmod) processing.", "label": "Disable", "name": "disable"}, {"description": "Add req-hdr for response modification (respmod) processing", "help": "Add req-hdr for response modification (respmod) processing.", "label": "Enable", "name": "enable"}]]  # Enable/disable addition of req-hdr for ICAP response modific
    respmod_default_action: NotRequired[Literal[{"description": "Forward response to ICAP server unless a rule specifies not to", "help": "Forward response to ICAP server unless a rule specifies not to.", "label": "Forward", "name": "forward"}, {"description": "Don\u0027t forward request to ICAP server unless a rule specifies to forward the request", "help": "Don\u0027t forward request to ICAP server unless a rule specifies to forward the request.", "label": "Bypass", "name": "bypass"}]]  # Default action to ICAP response modification (respmod) proce
    icap_block_log: NotRequired[Literal[{"description": "Disable UTM log when infection found", "help": "Disable UTM log when infection found.", "label": "Disable", "name": "disable"}, {"description": "Enable UTM log when infection found", "help": "Enable UTM log when infection found.", "label": "Enable", "name": "enable"}]]  # Enable/disable UTM log when infection found (default = disab
    chunk_encap: NotRequired[Literal[{"description": "Do not encapsulate chunked data", "help": "Do not encapsulate chunked data.", "label": "Disable", "name": "disable"}, {"description": "Encapsulate chunked data into a new chunk", "help": "Encapsulate chunked data into a new chunk.", "label": "Enable", "name": "enable"}]]  # Enable/disable chunked encapsulation (default = disable).
    extension_feature: NotRequired[Literal[{"description": "Support X-Scan-Progress-Interval ICAP header", "help": "Support X-Scan-Progress-Interval ICAP header.", "label": "Scan Progress", "name": "scan-progress"}]]  # Enable/disable ICAP extension features.
    scan_progress_interval: NotRequired[int]  # Scan progress interval value.
    timeout: NotRequired[int]  # Time (in seconds) that ICAP client waits for the response fr
    icap_headers: NotRequired[list[dict[str, Any]]]  # Configure ICAP forwarded request headers.
    respmod_forward_rules: NotRequired[list[dict[str, Any]]]  # ICAP response mode forward rules.


class Profile:
    """
    Configure ICAP profiles.
    
    Path: icap/profile
    Category: cmdb
    Primary Key: name
    """
    
    # Overloads for get() with response_mode="object"
    @overload
    def get(
        self,
        name: str | None = ...,
        filter: list[str] | None = ...,
        count: int | None = ...,
        start: int | None = ...,
        payload_dict: dict[str, Any] | None = ...,
        range: list[int] | None = ...,
        sort: str | None = ...,
        format: str | None = ...,
        action: str | None = ...,
        vdom: str | bool | None = ...,
        raw_json: Literal[False] = ...,
        response_mode: Literal["object"] = ...,
        **kwargs: Any,
    ) -> list[FortiObject]: ...
    
    @overload
    def get(
        self,
        name: str,
        filter: list[str] | None = ...,
        count: int | None = ...,
        start: int | None = ...,
        payload_dict: dict[str, Any] | None = ...,
        range: list[int] | None = ...,
        sort: str | None = ...,
        format: str | None = ...,
        action: str | None = ...,
        vdom: str | bool | None = ...,
        raw_json: Literal[False] = ...,
        response_mode: Literal["object"] = ...,
        **kwargs: Any,
    ) -> FortiObject: ...
    
    @overload
    def get(
        self,
        name: str | None = ...,
        filter: list[str] | None = ...,
        count: int | None = ...,
        start: int | None = ...,
        payload_dict: dict[str, Any] | None = ...,
        range: list[int] | None = ...,
        sort: str | None = ...,
        format: str | None = ...,
        action: str | None = ...,
        vdom: str | bool | None = ...,
        raw_json: Literal[True] = ...,
        response_mode: Literal["object"] = ...,
        **kwargs: Any,
    ) -> dict[str, Any]: ...
    
    # Default overload for dict mode
    @overload
    def get(
        self,
        name: str | None = ...,
        filter: list[str] | None = ...,
        count: int | None = ...,
        start: int | None = ...,
        payload_dict: dict[str, Any] | None = ...,
        range: list[int] | None = ...,
        sort: str | None = ...,
        format: str | None = ...,
        action: str | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        response_mode: Literal["dict"] | None = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], list[dict[str, Any]]]: ...
    
    def get(
        self,
        name: str | None = ...,
        filter: list[str] | None = ...,
        count: int | None = ...,
        start: int | None = ...,
        payload_dict: dict[str, Any] | None = ...,
        range: list[int] | None = ...,
        sort: str | None = ...,
        format: str | None = ...,
        action: str | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        response_mode: str | None = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], list[dict[str, Any]], FortiObject, list[FortiObject]]: ...
    
    def get_schema(
        self,
        vdom: str | None = ...,
        format: str = ...,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def post(
        self,
        payload_dict: ProfilePayload | None = ...,
        replacemsg_group: str | None = ...,
        name: str | None = ...,
        comment: str | None = ...,
        request: Literal[{"description": "Disable HTTP request passing to ICAP server", "help": "Disable HTTP request passing to ICAP server.", "label": "Disable", "name": "disable"}, {"description": "Enable HTTP request passing to ICAP server", "help": "Enable HTTP request passing to ICAP server.", "label": "Enable", "name": "enable"}] | None = ...,
        response: Literal[{"description": "Disable HTTP response passing to ICAP server", "help": "Disable HTTP response passing to ICAP server.", "label": "Disable", "name": "disable"}, {"description": "Enable HTTP response passing to ICAP server", "help": "Enable HTTP response passing to ICAP server.", "label": "Enable", "name": "enable"}] | None = ...,
        file_transfer: Literal[{"description": "Forward file transfer with SSH protocol to ICAP server for further processing", "help": "Forward file transfer with SSH protocol to ICAP server for further processing.", "label": "Ssh", "name": "ssh"}, {"description": "Forward file transfer with FTP protocol to ICAP server for further processing", "help": "Forward file transfer with FTP protocol to ICAP server for further processing.", "label": "Ftp", "name": "ftp"}] | None = ...,
        streaming_content_bypass: Literal[{"description": "Disable bypassing of ICAP server for streaming content", "help": "Disable bypassing of ICAP server for streaming content.", "label": "Disable", "name": "disable"}, {"description": "Enable bypassing of ICAP server for streaming content", "help": "Enable bypassing of ICAP server for streaming content.", "label": "Enable", "name": "enable"}] | None = ...,
        ocr_only: Literal[{"description": "Disable this FortiGate unit to submit only OCR interested content to the ICAP server", "help": "Disable this FortiGate unit to submit only OCR interested content to the ICAP server.", "label": "Disable", "name": "disable"}, {"description": "Enable this FortiGate unit to submit only OCR interested content to the ICAP server", "help": "Enable this FortiGate unit to submit only OCR interested content to the ICAP server.", "label": "Enable", "name": "enable"}] | None = ...,
        size_limit_204: int | None = ...,
        response_204: Literal[{"description": "Disable allowance of 204 response from ICAP server", "help": "Disable allowance of 204 response from ICAP server.", "label": "Disable", "name": "disable"}, {"description": "Enable allowance of 204 response from ICAP server", "help": "Enable allowance of 204 response from ICAP server.", "label": "Enable", "name": "enable"}] | None = ...,
        preview: Literal[{"description": "Disable preview of data to ICAP server", "help": "Disable preview of data to ICAP server.", "label": "Disable", "name": "disable"}, {"description": "Enable preview of data to ICAP server", "help": "Enable preview of data to ICAP server.", "label": "Enable", "name": "enable"}] | None = ...,
        preview_data_length: int | None = ...,
        request_server: str | None = ...,
        response_server: str | None = ...,
        file_transfer_server: str | None = ...,
        request_failure: Literal[{"description": "Error", "help": "Error.", "label": "Error", "name": "error"}, {"description": "Bypass", "help": "Bypass.", "label": "Bypass", "name": "bypass"}] | None = ...,
        response_failure: Literal[{"description": "Error", "help": "Error.", "label": "Error", "name": "error"}, {"description": "Bypass", "help": "Bypass.", "label": "Bypass", "name": "bypass"}] | None = ...,
        file_transfer_failure: Literal[{"description": "Error", "help": "Error.", "label": "Error", "name": "error"}, {"description": "Bypass", "help": "Bypass.", "label": "Bypass", "name": "bypass"}] | None = ...,
        request_path: str | None = ...,
        response_path: str | None = ...,
        file_transfer_path: str | None = ...,
        methods: Literal[{"description": "Forward HTTP request or response with DELETE method to ICAP server for further processing", "help": "Forward HTTP request or response with DELETE method to ICAP server for further processing.", "label": "Delete", "name": "delete"}, {"description": "Forward HTTP request or response with GET method to ICAP server for further processing", "help": "Forward HTTP request or response with GET method to ICAP server for further processing.", "label": "Get", "name": "get"}, {"description": "Forward HTTP request or response with HEAD method to ICAP server for further processing", "help": "Forward HTTP request or response with HEAD method to ICAP server for further processing.", "label": "Head", "name": "head"}, {"description": "Forward HTTP request or response with OPTIONS method to ICAP server for further processing", "help": "Forward HTTP request or response with OPTIONS method to ICAP server for further processing.", "label": "Options", "name": "options"}, {"description": "Forward HTTP request or response with POST method to ICAP server for further processing", "help": "Forward HTTP request or response with POST method to ICAP server for further processing.", "label": "Post", "name": "post"}, {"description": "Forward HTTP request or response with PUT method to ICAP server for further processing", "help": "Forward HTTP request or response with PUT method to ICAP server for further processing.", "label": "Put", "name": "put"}, {"description": "Forward HTTP request or response with TRACE method to ICAP server for further processing", "help": "Forward HTTP request or response with TRACE method to ICAP server for further processing.", "label": "Trace", "name": "trace"}, {"description": "Forward HTTP request or response with CONNECT method to ICAP server for further processing", "help": "Forward HTTP request or response with CONNECT method to ICAP server for further processing.", "label": "Connect", "name": "connect"}, {"description": "Forward HTTP request or response with All other methods to ICAP server for further processing", "help": "Forward HTTP request or response with All other methods to ICAP server for further processing.", "label": "Other", "name": "other"}] | None = ...,
        response_req_hdr: Literal[{"description": "Do not add req-hdr for response modification (respmod) processing", "help": "Do not add req-hdr for response modification (respmod) processing.", "label": "Disable", "name": "disable"}, {"description": "Add req-hdr for response modification (respmod) processing", "help": "Add req-hdr for response modification (respmod) processing.", "label": "Enable", "name": "enable"}] | None = ...,
        respmod_default_action: Literal[{"description": "Forward response to ICAP server unless a rule specifies not to", "help": "Forward response to ICAP server unless a rule specifies not to.", "label": "Forward", "name": "forward"}, {"description": "Don\u0027t forward request to ICAP server unless a rule specifies to forward the request", "help": "Don\u0027t forward request to ICAP server unless a rule specifies to forward the request.", "label": "Bypass", "name": "bypass"}] | None = ...,
        icap_block_log: Literal[{"description": "Disable UTM log when infection found", "help": "Disable UTM log when infection found.", "label": "Disable", "name": "disable"}, {"description": "Enable UTM log when infection found", "help": "Enable UTM log when infection found.", "label": "Enable", "name": "enable"}] | None = ...,
        chunk_encap: Literal[{"description": "Do not encapsulate chunked data", "help": "Do not encapsulate chunked data.", "label": "Disable", "name": "disable"}, {"description": "Encapsulate chunked data into a new chunk", "help": "Encapsulate chunked data into a new chunk.", "label": "Enable", "name": "enable"}] | None = ...,
        extension_feature: Literal[{"description": "Support X-Scan-Progress-Interval ICAP header", "help": "Support X-Scan-Progress-Interval ICAP header.", "label": "Scan Progress", "name": "scan-progress"}] | None = ...,
        scan_progress_interval: int | None = ...,
        timeout: int | None = ...,
        icap_headers: list[dict[str, Any]] | None = ...,
        respmod_forward_rules: list[dict[str, Any]] | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: ProfilePayload | None = ...,
        replacemsg_group: str | None = ...,
        name: str | None = ...,
        comment: str | None = ...,
        request: Literal[{"description": "Disable HTTP request passing to ICAP server", "help": "Disable HTTP request passing to ICAP server.", "label": "Disable", "name": "disable"}, {"description": "Enable HTTP request passing to ICAP server", "help": "Enable HTTP request passing to ICAP server.", "label": "Enable", "name": "enable"}] | None = ...,
        response: Literal[{"description": "Disable HTTP response passing to ICAP server", "help": "Disable HTTP response passing to ICAP server.", "label": "Disable", "name": "disable"}, {"description": "Enable HTTP response passing to ICAP server", "help": "Enable HTTP response passing to ICAP server.", "label": "Enable", "name": "enable"}] | None = ...,
        file_transfer: Literal[{"description": "Forward file transfer with SSH protocol to ICAP server for further processing", "help": "Forward file transfer with SSH protocol to ICAP server for further processing.", "label": "Ssh", "name": "ssh"}, {"description": "Forward file transfer with FTP protocol to ICAP server for further processing", "help": "Forward file transfer with FTP protocol to ICAP server for further processing.", "label": "Ftp", "name": "ftp"}] | None = ...,
        streaming_content_bypass: Literal[{"description": "Disable bypassing of ICAP server for streaming content", "help": "Disable bypassing of ICAP server for streaming content.", "label": "Disable", "name": "disable"}, {"description": "Enable bypassing of ICAP server for streaming content", "help": "Enable bypassing of ICAP server for streaming content.", "label": "Enable", "name": "enable"}] | None = ...,
        ocr_only: Literal[{"description": "Disable this FortiGate unit to submit only OCR interested content to the ICAP server", "help": "Disable this FortiGate unit to submit only OCR interested content to the ICAP server.", "label": "Disable", "name": "disable"}, {"description": "Enable this FortiGate unit to submit only OCR interested content to the ICAP server", "help": "Enable this FortiGate unit to submit only OCR interested content to the ICAP server.", "label": "Enable", "name": "enable"}] | None = ...,
        size_limit_204: int | None = ...,
        response_204: Literal[{"description": "Disable allowance of 204 response from ICAP server", "help": "Disable allowance of 204 response from ICAP server.", "label": "Disable", "name": "disable"}, {"description": "Enable allowance of 204 response from ICAP server", "help": "Enable allowance of 204 response from ICAP server.", "label": "Enable", "name": "enable"}] | None = ...,
        preview: Literal[{"description": "Disable preview of data to ICAP server", "help": "Disable preview of data to ICAP server.", "label": "Disable", "name": "disable"}, {"description": "Enable preview of data to ICAP server", "help": "Enable preview of data to ICAP server.", "label": "Enable", "name": "enable"}] | None = ...,
        preview_data_length: int | None = ...,
        request_server: str | None = ...,
        response_server: str | None = ...,
        file_transfer_server: str | None = ...,
        request_failure: Literal[{"description": "Error", "help": "Error.", "label": "Error", "name": "error"}, {"description": "Bypass", "help": "Bypass.", "label": "Bypass", "name": "bypass"}] | None = ...,
        response_failure: Literal[{"description": "Error", "help": "Error.", "label": "Error", "name": "error"}, {"description": "Bypass", "help": "Bypass.", "label": "Bypass", "name": "bypass"}] | None = ...,
        file_transfer_failure: Literal[{"description": "Error", "help": "Error.", "label": "Error", "name": "error"}, {"description": "Bypass", "help": "Bypass.", "label": "Bypass", "name": "bypass"}] | None = ...,
        request_path: str | None = ...,
        response_path: str | None = ...,
        file_transfer_path: str | None = ...,
        methods: Literal[{"description": "Forward HTTP request or response with DELETE method to ICAP server for further processing", "help": "Forward HTTP request or response with DELETE method to ICAP server for further processing.", "label": "Delete", "name": "delete"}, {"description": "Forward HTTP request or response with GET method to ICAP server for further processing", "help": "Forward HTTP request or response with GET method to ICAP server for further processing.", "label": "Get", "name": "get"}, {"description": "Forward HTTP request or response with HEAD method to ICAP server for further processing", "help": "Forward HTTP request or response with HEAD method to ICAP server for further processing.", "label": "Head", "name": "head"}, {"description": "Forward HTTP request or response with OPTIONS method to ICAP server for further processing", "help": "Forward HTTP request or response with OPTIONS method to ICAP server for further processing.", "label": "Options", "name": "options"}, {"description": "Forward HTTP request or response with POST method to ICAP server for further processing", "help": "Forward HTTP request or response with POST method to ICAP server for further processing.", "label": "Post", "name": "post"}, {"description": "Forward HTTP request or response with PUT method to ICAP server for further processing", "help": "Forward HTTP request or response with PUT method to ICAP server for further processing.", "label": "Put", "name": "put"}, {"description": "Forward HTTP request or response with TRACE method to ICAP server for further processing", "help": "Forward HTTP request or response with TRACE method to ICAP server for further processing.", "label": "Trace", "name": "trace"}, {"description": "Forward HTTP request or response with CONNECT method to ICAP server for further processing", "help": "Forward HTTP request or response with CONNECT method to ICAP server for further processing.", "label": "Connect", "name": "connect"}, {"description": "Forward HTTP request or response with All other methods to ICAP server for further processing", "help": "Forward HTTP request or response with All other methods to ICAP server for further processing.", "label": "Other", "name": "other"}] | None = ...,
        response_req_hdr: Literal[{"description": "Do not add req-hdr for response modification (respmod) processing", "help": "Do not add req-hdr for response modification (respmod) processing.", "label": "Disable", "name": "disable"}, {"description": "Add req-hdr for response modification (respmod) processing", "help": "Add req-hdr for response modification (respmod) processing.", "label": "Enable", "name": "enable"}] | None = ...,
        respmod_default_action: Literal[{"description": "Forward response to ICAP server unless a rule specifies not to", "help": "Forward response to ICAP server unless a rule specifies not to.", "label": "Forward", "name": "forward"}, {"description": "Don\u0027t forward request to ICAP server unless a rule specifies to forward the request", "help": "Don\u0027t forward request to ICAP server unless a rule specifies to forward the request.", "label": "Bypass", "name": "bypass"}] | None = ...,
        icap_block_log: Literal[{"description": "Disable UTM log when infection found", "help": "Disable UTM log when infection found.", "label": "Disable", "name": "disable"}, {"description": "Enable UTM log when infection found", "help": "Enable UTM log when infection found.", "label": "Enable", "name": "enable"}] | None = ...,
        chunk_encap: Literal[{"description": "Do not encapsulate chunked data", "help": "Do not encapsulate chunked data.", "label": "Disable", "name": "disable"}, {"description": "Encapsulate chunked data into a new chunk", "help": "Encapsulate chunked data into a new chunk.", "label": "Enable", "name": "enable"}] | None = ...,
        extension_feature: Literal[{"description": "Support X-Scan-Progress-Interval ICAP header", "help": "Support X-Scan-Progress-Interval ICAP header.", "label": "Scan Progress", "name": "scan-progress"}] | None = ...,
        scan_progress_interval: int | None = ...,
        timeout: int | None = ...,
        icap_headers: list[dict[str, Any]] | None = ...,
        respmod_forward_rules: list[dict[str, Any]] | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def delete(
        self,
        name: str | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def exists(
        self,
        name: str,
        vdom: str | bool | None = ...,
    ) -> Union[bool, Coroutine[Any, Any, bool]]: ...
    
    def set(
        self,
        payload_dict: ProfilePayload | None = ...,
        vdom: str | bool | None = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    # Helper methods
    @staticmethod
    def help(field_name: str | None = ...) -> str: ...
    
    @staticmethod
    def fields(detailed: bool = ...) -> Union[list[str], list[dict[str, Any]]]: ...
    
    @staticmethod
    def field_info(field_name: str) -> dict[str, Any]: ...
    
    @staticmethod
    def validate_field(name: str, value: Any) -> bool: ...
    
    @staticmethod
    def required_fields() -> list[str]: ...
    
    @staticmethod
    def defaults() -> dict[str, Any]: ...
    
    @staticmethod
    def schema() -> dict[str, Any]: ...


__all__ = [
    "Profile",
    "ProfilePayload",
]