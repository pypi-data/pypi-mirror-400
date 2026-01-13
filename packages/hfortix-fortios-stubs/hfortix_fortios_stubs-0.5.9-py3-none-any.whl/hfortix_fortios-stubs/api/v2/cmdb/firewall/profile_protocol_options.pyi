from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class ProfileProtocolOptionsPayload(TypedDict, total=False):
    """
    Type hints for firewall/profile_protocol_options payload fields.
    
    Configure protocol options.
    
    **Related Resources:**

    Dependencies (resources this endpoint references):
        - :class:`~.system.replacemsg-group.ReplacemsgGroupEndpoint` (via: replacemsg-group)

    **Usage:**
        payload: ProfileProtocolOptionsPayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    name: str  # Name.
    comment: NotRequired[str]  # Optional comments.
    replacemsg_group: NotRequired[str]  # Name of the replacement message group to be used.
    oversize_log: NotRequired[Literal[{"description": "Disable logging for antivirus oversize file blocking", "help": "Disable logging for antivirus oversize file blocking.", "label": "Disable", "name": "disable"}, {"description": "Enable logging for antivirus oversize file blocking", "help": "Enable logging for antivirus oversize file blocking.", "label": "Enable", "name": "enable"}]]  # Enable/disable logging for antivirus oversize file blocking.
    switching_protocols_log: NotRequired[Literal[{"description": "Disable logging for HTTP/HTTPS switching protocols", "help": "Disable logging for HTTP/HTTPS switching protocols.", "label": "Disable", "name": "disable"}, {"description": "Enable logging for HTTP/HTTPS switching protocols", "help": "Enable logging for HTTP/HTTPS switching protocols.", "label": "Enable", "name": "enable"}]]  # Enable/disable logging for HTTP/HTTPS switching protocols.
    http: NotRequired[str]  # Configure HTTP protocol options.
    ftp: NotRequired[str]  # Configure FTP protocol options.
    imap: NotRequired[str]  # Configure IMAP protocol options.
    mapi: NotRequired[str]  # Configure MAPI protocol options.
    pop3: NotRequired[str]  # Configure POP3 protocol options.
    smtp: NotRequired[str]  # Configure SMTP protocol options.
    nntp: NotRequired[str]  # Configure NNTP protocol options.
    ssh: NotRequired[str]  # Configure SFTP and SCP protocol options.
    dns: NotRequired[str]  # Configure DNS protocol options.
    cifs: NotRequired[str]  # Configure CIFS protocol options.
    mail_signature: NotRequired[str]  # Configure Mail signature.
    rpc_over_http: NotRequired[Literal[{"description": "Enable inspection of RPC over HTTP", "help": "Enable inspection of RPC over HTTP.", "label": "Enable", "name": "enable"}, {"description": "Disable inspection of RPC over HTTP", "help": "Disable inspection of RPC over HTTP.", "label": "Disable", "name": "disable"}]]  # Enable/disable inspection of RPC over HTTP.


class ProfileProtocolOptions:
    """
    Configure protocol options.
    
    Path: firewall/profile_protocol_options
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
        payload_dict: ProfileProtocolOptionsPayload | None = ...,
        name: str | None = ...,
        comment: str | None = ...,
        replacemsg_group: str | None = ...,
        oversize_log: Literal[{"description": "Disable logging for antivirus oversize file blocking", "help": "Disable logging for antivirus oversize file blocking.", "label": "Disable", "name": "disable"}, {"description": "Enable logging for antivirus oversize file blocking", "help": "Enable logging for antivirus oversize file blocking.", "label": "Enable", "name": "enable"}] | None = ...,
        switching_protocols_log: Literal[{"description": "Disable logging for HTTP/HTTPS switching protocols", "help": "Disable logging for HTTP/HTTPS switching protocols.", "label": "Disable", "name": "disable"}, {"description": "Enable logging for HTTP/HTTPS switching protocols", "help": "Enable logging for HTTP/HTTPS switching protocols.", "label": "Enable", "name": "enable"}] | None = ...,
        http: str | None = ...,
        ftp: str | None = ...,
        imap: str | None = ...,
        mapi: str | None = ...,
        pop3: str | None = ...,
        smtp: str | None = ...,
        nntp: str | None = ...,
        ssh: str | None = ...,
        dns: str | None = ...,
        cifs: str | None = ...,
        mail_signature: str | None = ...,
        rpc_over_http: Literal[{"description": "Enable inspection of RPC over HTTP", "help": "Enable inspection of RPC over HTTP.", "label": "Enable", "name": "enable"}, {"description": "Disable inspection of RPC over HTTP", "help": "Disable inspection of RPC over HTTP.", "label": "Disable", "name": "disable"}] | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: ProfileProtocolOptionsPayload | None = ...,
        name: str | None = ...,
        comment: str | None = ...,
        replacemsg_group: str | None = ...,
        oversize_log: Literal[{"description": "Disable logging for antivirus oversize file blocking", "help": "Disable logging for antivirus oversize file blocking.", "label": "Disable", "name": "disable"}, {"description": "Enable logging for antivirus oversize file blocking", "help": "Enable logging for antivirus oversize file blocking.", "label": "Enable", "name": "enable"}] | None = ...,
        switching_protocols_log: Literal[{"description": "Disable logging for HTTP/HTTPS switching protocols", "help": "Disable logging for HTTP/HTTPS switching protocols.", "label": "Disable", "name": "disable"}, {"description": "Enable logging for HTTP/HTTPS switching protocols", "help": "Enable logging for HTTP/HTTPS switching protocols.", "label": "Enable", "name": "enable"}] | None = ...,
        http: str | None = ...,
        ftp: str | None = ...,
        imap: str | None = ...,
        mapi: str | None = ...,
        pop3: str | None = ...,
        smtp: str | None = ...,
        nntp: str | None = ...,
        ssh: str | None = ...,
        dns: str | None = ...,
        cifs: str | None = ...,
        mail_signature: str | None = ...,
        rpc_over_http: Literal[{"description": "Enable inspection of RPC over HTTP", "help": "Enable inspection of RPC over HTTP.", "label": "Enable", "name": "enable"}, {"description": "Disable inspection of RPC over HTTP", "help": "Disable inspection of RPC over HTTP.", "label": "Disable", "name": "disable"}] | None = ...,
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
        payload_dict: ProfileProtocolOptionsPayload | None = ...,
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
    "ProfileProtocolOptions",
    "ProfileProtocolOptionsPayload",
]