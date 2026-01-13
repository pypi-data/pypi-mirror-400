from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class ProfilePayload(TypedDict, total=False):
    """
    Type hints for dlp/profile payload fields.
    
    Configure DLP profiles.
    
    **Related Resources:**

    Dependencies (resources this endpoint references):
        - :class:`~.system.replacemsg-group.ReplacemsgGroupEndpoint` (via: replacemsg-group)

    **Usage:**
        payload: ProfilePayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    name: str  # Name of the DLP profile.
    comment: NotRequired[str]  # Comment.
    feature_set: NotRequired[Literal[{"description": "Flow feature set", "help": "Flow feature set.", "label": "Flow", "name": "flow"}, {"description": "Proxy feature set", "help": "Proxy feature set.", "label": "Proxy", "name": "proxy"}]]  # Flow/proxy feature set.
    replacemsg_group: NotRequired[str]  # Replacement message group used by this DLP profile.
    rule: NotRequired[list[dict[str, Any]]]  # Set up DLP rules for this profile.
    dlp_log: NotRequired[Literal[{"description": "Enable DLP logging", "help": "Enable DLP logging.", "label": "Enable", "name": "enable"}, {"description": "Disable DLP logging", "help": "Disable DLP logging.", "label": "Disable", "name": "disable"}]]  # Enable/disable DLP logging.
    extended_log: NotRequired[Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]]  # Enable/disable extended logging for data loss prevention.
    nac_quar_log: NotRequired[Literal[{"description": "Enable NAC quarantine logging", "help": "Enable NAC quarantine logging.", "label": "Enable", "name": "enable"}, {"description": "Disable NAC quarantine logging", "help": "Disable NAC quarantine logging.", "label": "Disable", "name": "disable"}]]  # Enable/disable NAC quarantine logging.
    full_archive_proto: NotRequired[Literal[{"description": "SMTP", "help": "SMTP.", "label": "Smtp", "name": "smtp"}, {"description": "POP3", "help": "POP3.", "label": "Pop3", "name": "pop3"}, {"description": "IMAP", "help": "IMAP.", "label": "Imap", "name": "imap"}, {"description": "HTTP GET", "help": "HTTP GET.", "label": "Http Get", "name": "http-get"}, {"description": "HTTP POST", "help": "HTTP POST.", "label": "Http Post", "name": "http-post"}, {"description": "FTP", "help": "FTP.", "label": "Ftp", "name": "ftp"}, {"description": "NNTP", "help": "NNTP.", "label": "Nntp", "name": "nntp"}, {"description": "MAPI", "help": "MAPI.", "label": "Mapi", "name": "mapi"}, {"description": "SFTP and SCP", "help": "SFTP and SCP.", "label": "Ssh", "name": "ssh"}, {"description": "CIFS", "help": "CIFS.", "label": "Cifs", "name": "cifs"}]]  # Protocols to always content archive.
    summary_proto: NotRequired[Literal[{"description": "SMTP", "help": "SMTP.", "label": "Smtp", "name": "smtp"}, {"description": "POP3", "help": "POP3.", "label": "Pop3", "name": "pop3"}, {"description": "IMAP", "help": "IMAP.", "label": "Imap", "name": "imap"}, {"description": "HTTP GET", "help": "HTTP GET.", "label": "Http Get", "name": "http-get"}, {"description": "HTTP POST", "help": "HTTP POST.", "label": "Http Post", "name": "http-post"}, {"description": "FTP", "help": "FTP.", "label": "Ftp", "name": "ftp"}, {"description": "NNTP", "help": "NNTP.", "label": "Nntp", "name": "nntp"}, {"description": "MAPI", "help": "MAPI.", "label": "Mapi", "name": "mapi"}, {"description": "SFTP and SCP", "help": "SFTP and SCP.", "label": "Ssh", "name": "ssh"}, {"description": "CIFS", "help": "CIFS.", "label": "Cifs", "name": "cifs"}]]  # Protocols to always log summary.
    fortidata_error_action: NotRequired[Literal[{"description": "Log failure, but allow the file", "help": "Log failure, but allow the file.", "label": "Log Only", "name": "log-only"}, {"description": "Block the file", "help": "Block the file.", "label": "Block", "name": "block"}, {"description": "Behave as if FortiData returned no match", "help": "Behave as if FortiData returned no match.", "label": "Ignore", "name": "ignore"}]]  # Action to take if FortiData query fails.


class Profile:
    """
    Configure DLP profiles.
    
    Path: dlp/profile
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
        name: str | None = ...,
        comment: str | None = ...,
        feature_set: Literal[{"description": "Flow feature set", "help": "Flow feature set.", "label": "Flow", "name": "flow"}, {"description": "Proxy feature set", "help": "Proxy feature set.", "label": "Proxy", "name": "proxy"}] | None = ...,
        replacemsg_group: str | None = ...,
        rule: list[dict[str, Any]] | None = ...,
        dlp_log: Literal[{"description": "Enable DLP logging", "help": "Enable DLP logging.", "label": "Enable", "name": "enable"}, {"description": "Disable DLP logging", "help": "Disable DLP logging.", "label": "Disable", "name": "disable"}] | None = ...,
        extended_log: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        nac_quar_log: Literal[{"description": "Enable NAC quarantine logging", "help": "Enable NAC quarantine logging.", "label": "Enable", "name": "enable"}, {"description": "Disable NAC quarantine logging", "help": "Disable NAC quarantine logging.", "label": "Disable", "name": "disable"}] | None = ...,
        full_archive_proto: Literal[{"description": "SMTP", "help": "SMTP.", "label": "Smtp", "name": "smtp"}, {"description": "POP3", "help": "POP3.", "label": "Pop3", "name": "pop3"}, {"description": "IMAP", "help": "IMAP.", "label": "Imap", "name": "imap"}, {"description": "HTTP GET", "help": "HTTP GET.", "label": "Http Get", "name": "http-get"}, {"description": "HTTP POST", "help": "HTTP POST.", "label": "Http Post", "name": "http-post"}, {"description": "FTP", "help": "FTP.", "label": "Ftp", "name": "ftp"}, {"description": "NNTP", "help": "NNTP.", "label": "Nntp", "name": "nntp"}, {"description": "MAPI", "help": "MAPI.", "label": "Mapi", "name": "mapi"}, {"description": "SFTP and SCP", "help": "SFTP and SCP.", "label": "Ssh", "name": "ssh"}, {"description": "CIFS", "help": "CIFS.", "label": "Cifs", "name": "cifs"}] | None = ...,
        summary_proto: Literal[{"description": "SMTP", "help": "SMTP.", "label": "Smtp", "name": "smtp"}, {"description": "POP3", "help": "POP3.", "label": "Pop3", "name": "pop3"}, {"description": "IMAP", "help": "IMAP.", "label": "Imap", "name": "imap"}, {"description": "HTTP GET", "help": "HTTP GET.", "label": "Http Get", "name": "http-get"}, {"description": "HTTP POST", "help": "HTTP POST.", "label": "Http Post", "name": "http-post"}, {"description": "FTP", "help": "FTP.", "label": "Ftp", "name": "ftp"}, {"description": "NNTP", "help": "NNTP.", "label": "Nntp", "name": "nntp"}, {"description": "MAPI", "help": "MAPI.", "label": "Mapi", "name": "mapi"}, {"description": "SFTP and SCP", "help": "SFTP and SCP.", "label": "Ssh", "name": "ssh"}, {"description": "CIFS", "help": "CIFS.", "label": "Cifs", "name": "cifs"}] | None = ...,
        fortidata_error_action: Literal[{"description": "Log failure, but allow the file", "help": "Log failure, but allow the file.", "label": "Log Only", "name": "log-only"}, {"description": "Block the file", "help": "Block the file.", "label": "Block", "name": "block"}, {"description": "Behave as if FortiData returned no match", "help": "Behave as if FortiData returned no match.", "label": "Ignore", "name": "ignore"}] | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: ProfilePayload | None = ...,
        name: str | None = ...,
        comment: str | None = ...,
        feature_set: Literal[{"description": "Flow feature set", "help": "Flow feature set.", "label": "Flow", "name": "flow"}, {"description": "Proxy feature set", "help": "Proxy feature set.", "label": "Proxy", "name": "proxy"}] | None = ...,
        replacemsg_group: str | None = ...,
        rule: list[dict[str, Any]] | None = ...,
        dlp_log: Literal[{"description": "Enable DLP logging", "help": "Enable DLP logging.", "label": "Enable", "name": "enable"}, {"description": "Disable DLP logging", "help": "Disable DLP logging.", "label": "Disable", "name": "disable"}] | None = ...,
        extended_log: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        nac_quar_log: Literal[{"description": "Enable NAC quarantine logging", "help": "Enable NAC quarantine logging.", "label": "Enable", "name": "enable"}, {"description": "Disable NAC quarantine logging", "help": "Disable NAC quarantine logging.", "label": "Disable", "name": "disable"}] | None = ...,
        full_archive_proto: Literal[{"description": "SMTP", "help": "SMTP.", "label": "Smtp", "name": "smtp"}, {"description": "POP3", "help": "POP3.", "label": "Pop3", "name": "pop3"}, {"description": "IMAP", "help": "IMAP.", "label": "Imap", "name": "imap"}, {"description": "HTTP GET", "help": "HTTP GET.", "label": "Http Get", "name": "http-get"}, {"description": "HTTP POST", "help": "HTTP POST.", "label": "Http Post", "name": "http-post"}, {"description": "FTP", "help": "FTP.", "label": "Ftp", "name": "ftp"}, {"description": "NNTP", "help": "NNTP.", "label": "Nntp", "name": "nntp"}, {"description": "MAPI", "help": "MAPI.", "label": "Mapi", "name": "mapi"}, {"description": "SFTP and SCP", "help": "SFTP and SCP.", "label": "Ssh", "name": "ssh"}, {"description": "CIFS", "help": "CIFS.", "label": "Cifs", "name": "cifs"}] | None = ...,
        summary_proto: Literal[{"description": "SMTP", "help": "SMTP.", "label": "Smtp", "name": "smtp"}, {"description": "POP3", "help": "POP3.", "label": "Pop3", "name": "pop3"}, {"description": "IMAP", "help": "IMAP.", "label": "Imap", "name": "imap"}, {"description": "HTTP GET", "help": "HTTP GET.", "label": "Http Get", "name": "http-get"}, {"description": "HTTP POST", "help": "HTTP POST.", "label": "Http Post", "name": "http-post"}, {"description": "FTP", "help": "FTP.", "label": "Ftp", "name": "ftp"}, {"description": "NNTP", "help": "NNTP.", "label": "Nntp", "name": "nntp"}, {"description": "MAPI", "help": "MAPI.", "label": "Mapi", "name": "mapi"}, {"description": "SFTP and SCP", "help": "SFTP and SCP.", "label": "Ssh", "name": "ssh"}, {"description": "CIFS", "help": "CIFS.", "label": "Cifs", "name": "cifs"}] | None = ...,
        fortidata_error_action: Literal[{"description": "Log failure, but allow the file", "help": "Log failure, but allow the file.", "label": "Log Only", "name": "log-only"}, {"description": "Block the file", "help": "Block the file.", "label": "Block", "name": "block"}, {"description": "Behave as if FortiData returned no match", "help": "Behave as if FortiData returned no match.", "label": "Ignore", "name": "ignore"}] | None = ...,
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