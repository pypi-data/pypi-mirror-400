from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class QuarantinePayload(TypedDict, total=False):
    """
    Type hints for antivirus/quarantine payload fields.
    
    Configure quarantine options.
    
    **Usage:**
        payload: QuarantinePayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    agelimit: NotRequired[int]  # Age limit for quarantined files (0 - 479 hours, 0 means fore
    maxfilesize: NotRequired[int]  # Maximum file size to quarantine (0 - 500 Mbytes, 0 means unl
    quarantine_quota: NotRequired[int]  # The amount of disk space to reserve for quarantining files (
    drop_infected: NotRequired[Literal[{"description": "IMAP", "help": "IMAP.", "label": "Imap", "name": "imap"}, {"description": "SMTP", "help": "SMTP.", "label": "Smtp", "name": "smtp"}, {"description": "POP3", "help": "POP3.", "label": "Pop3", "name": "pop3"}, {"description": "HTTP", "help": "HTTP.", "label": "Http", "name": "http"}, {"description": "FTP", "help": "FTP.", "label": "Ftp", "name": "ftp"}, {"description": "NNTP", "help": "NNTP.", "label": "Nntp", "name": "nntp"}, {"description": "IMAPS", "help": "IMAPS.", "label": "Imaps", "name": "imaps"}, {"description": "SMTPS", "help": "SMTPS.", "label": "Smtps", "name": "smtps"}, {"description": "POP3S", "help": "POP3S.", "label": "Pop3S", "name": "pop3s"}, {"description": "HTTPS", "help": "HTTPS.", "label": "Https", "name": "https"}, {"description": "FTPS", "help": "FTPS.", "label": "Ftps", "name": "ftps"}, {"description": "MAPI", "help": "MAPI.", "label": "Mapi", "name": "mapi"}, {"description": "CIFS", "help": "CIFS.", "label": "Cifs", "name": "cifs"}, {"description": "SSH", "help": "SSH.", "label": "Ssh", "name": "ssh"}]]  # Do not quarantine infected files found in sessions using the
    store_infected: NotRequired[Literal[{"description": "IMAP", "help": "IMAP.", "label": "Imap", "name": "imap"}, {"description": "SMTP", "help": "SMTP.", "label": "Smtp", "name": "smtp"}, {"description": "POP3", "help": "POP3.", "label": "Pop3", "name": "pop3"}, {"description": "HTTP", "help": "HTTP.", "label": "Http", "name": "http"}, {"description": "FTP", "help": "FTP.", "label": "Ftp", "name": "ftp"}, {"description": "NNTP", "help": "NNTP.", "label": "Nntp", "name": "nntp"}, {"description": "IMAPS", "help": "IMAPS.", "label": "Imaps", "name": "imaps"}, {"description": "SMTPS", "help": "SMTPS.", "label": "Smtps", "name": "smtps"}, {"description": "POP3S", "help": "POP3S.", "label": "Pop3S", "name": "pop3s"}, {"description": "HTTPS", "help": "HTTPS.", "label": "Https", "name": "https"}, {"description": "FTPS", "help": "FTPS.", "label": "Ftps", "name": "ftps"}, {"description": "MAPI", "help": "MAPI.", "label": "Mapi", "name": "mapi"}, {"description": "CIFS", "help": "CIFS.", "label": "Cifs", "name": "cifs"}, {"description": "SSH", "help": "SSH.", "label": "Ssh", "name": "ssh"}]]  # Quarantine infected files found in sessions using the select
    drop_machine_learning: NotRequired[Literal[{"description": "IMAP", "help": "IMAP.", "label": "Imap", "name": "imap"}, {"description": "SMTP", "help": "SMTP.", "label": "Smtp", "name": "smtp"}, {"description": "POP3", "help": "POP3.", "label": "Pop3", "name": "pop3"}, {"description": "HTTP", "help": "HTTP.", "label": "Http", "name": "http"}, {"description": "FTP", "help": "FTP.", "label": "Ftp", "name": "ftp"}, {"description": "NNTP", "help": "NNTP.", "label": "Nntp", "name": "nntp"}, {"description": "IMAPS", "help": "IMAPS.", "label": "Imaps", "name": "imaps"}, {"description": "SMTPS", "help": "SMTPS.", "label": "Smtps", "name": "smtps"}, {"description": "POP3S", "help": "POP3S.", "label": "Pop3S", "name": "pop3s"}, {"description": "HTTPS", "help": "HTTPS.", "label": "Https", "name": "https"}, {"description": "FTPS", "help": "FTPS.", "label": "Ftps", "name": "ftps"}, {"description": "MAPI", "help": "MAPI.", "label": "Mapi", "name": "mapi"}, {"description": "CIFS", "help": "CIFS.", "label": "Cifs", "name": "cifs"}, {"description": "SSH", "help": "SSH.", "label": "Ssh", "name": "ssh"}]]  # Do not quarantine files detected by machine learning found i
    store_machine_learning: NotRequired[Literal[{"description": "IMAP", "help": "IMAP.", "label": "Imap", "name": "imap"}, {"description": "SMTP", "help": "SMTP.", "label": "Smtp", "name": "smtp"}, {"description": "POP3", "help": "POP3.", "label": "Pop3", "name": "pop3"}, {"description": "HTTP", "help": "HTTP.", "label": "Http", "name": "http"}, {"description": "FTP", "help": "FTP.", "label": "Ftp", "name": "ftp"}, {"description": "NNTP", "help": "NNTP.", "label": "Nntp", "name": "nntp"}, {"description": "IMAPS", "help": "IMAPS.", "label": "Imaps", "name": "imaps"}, {"description": "SMTPS", "help": "SMTPS.", "label": "Smtps", "name": "smtps"}, {"description": "POP3S", "help": "POP3S.", "label": "Pop3S", "name": "pop3s"}, {"description": "HTTPS", "help": "HTTPS.", "label": "Https", "name": "https"}, {"description": "FTPS", "help": "FTPS.", "label": "Ftps", "name": "ftps"}, {"description": "MAPI", "help": "MAPI.", "label": "Mapi", "name": "mapi"}, {"description": "CIFS", "help": "CIFS.", "label": "Cifs", "name": "cifs"}, {"description": "SSH", "help": "SSH.", "label": "Ssh", "name": "ssh"}]]  # Quarantine files detected by machine learning found in sessi
    lowspace: NotRequired[Literal[{"description": "Drop (delete) the most recently quarantined files", "help": "Drop (delete) the most recently quarantined files.", "label": "Drop New", "name": "drop-new"}, {"description": "Overwrite the oldest quarantined files", "help": "Overwrite the oldest quarantined files. That is, the files that are closest to being deleted from the quarantine.", "label": "Ovrw Old", "name": "ovrw-old"}]]  # Select the method for handling additional files when running
    destination: NotRequired[Literal[{"description": "Files that would be quarantined are deleted", "help": "Files that would be quarantined are deleted.", "label": "Null", "name": "NULL"}, {"description": "Quarantine files to the FortiGate hard disk", "help": "Quarantine files to the FortiGate hard disk.", "label": "Disk", "name": "disk"}, {"description": "FortiAnalyzer", "help": "FortiAnalyzer", "label": "Fortianalyzer", "name": "FortiAnalyzer"}]]  # Choose whether to quarantine files to the FortiGate disk or 


class Quarantine:
    """
    Configure quarantine options.
    
    Path: antivirus/quarantine
    Category: cmdb
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
        payload_dict: QuarantinePayload | None = ...,
        agelimit: int | None = ...,
        maxfilesize: int | None = ...,
        quarantine_quota: int | None = ...,
        drop_infected: Literal[{"description": "IMAP", "help": "IMAP.", "label": "Imap", "name": "imap"}, {"description": "SMTP", "help": "SMTP.", "label": "Smtp", "name": "smtp"}, {"description": "POP3", "help": "POP3.", "label": "Pop3", "name": "pop3"}, {"description": "HTTP", "help": "HTTP.", "label": "Http", "name": "http"}, {"description": "FTP", "help": "FTP.", "label": "Ftp", "name": "ftp"}, {"description": "NNTP", "help": "NNTP.", "label": "Nntp", "name": "nntp"}, {"description": "IMAPS", "help": "IMAPS.", "label": "Imaps", "name": "imaps"}, {"description": "SMTPS", "help": "SMTPS.", "label": "Smtps", "name": "smtps"}, {"description": "POP3S", "help": "POP3S.", "label": "Pop3S", "name": "pop3s"}, {"description": "HTTPS", "help": "HTTPS.", "label": "Https", "name": "https"}, {"description": "FTPS", "help": "FTPS.", "label": "Ftps", "name": "ftps"}, {"description": "MAPI", "help": "MAPI.", "label": "Mapi", "name": "mapi"}, {"description": "CIFS", "help": "CIFS.", "label": "Cifs", "name": "cifs"}, {"description": "SSH", "help": "SSH.", "label": "Ssh", "name": "ssh"}] | None = ...,
        store_infected: Literal[{"description": "IMAP", "help": "IMAP.", "label": "Imap", "name": "imap"}, {"description": "SMTP", "help": "SMTP.", "label": "Smtp", "name": "smtp"}, {"description": "POP3", "help": "POP3.", "label": "Pop3", "name": "pop3"}, {"description": "HTTP", "help": "HTTP.", "label": "Http", "name": "http"}, {"description": "FTP", "help": "FTP.", "label": "Ftp", "name": "ftp"}, {"description": "NNTP", "help": "NNTP.", "label": "Nntp", "name": "nntp"}, {"description": "IMAPS", "help": "IMAPS.", "label": "Imaps", "name": "imaps"}, {"description": "SMTPS", "help": "SMTPS.", "label": "Smtps", "name": "smtps"}, {"description": "POP3S", "help": "POP3S.", "label": "Pop3S", "name": "pop3s"}, {"description": "HTTPS", "help": "HTTPS.", "label": "Https", "name": "https"}, {"description": "FTPS", "help": "FTPS.", "label": "Ftps", "name": "ftps"}, {"description": "MAPI", "help": "MAPI.", "label": "Mapi", "name": "mapi"}, {"description": "CIFS", "help": "CIFS.", "label": "Cifs", "name": "cifs"}, {"description": "SSH", "help": "SSH.", "label": "Ssh", "name": "ssh"}] | None = ...,
        drop_machine_learning: Literal[{"description": "IMAP", "help": "IMAP.", "label": "Imap", "name": "imap"}, {"description": "SMTP", "help": "SMTP.", "label": "Smtp", "name": "smtp"}, {"description": "POP3", "help": "POP3.", "label": "Pop3", "name": "pop3"}, {"description": "HTTP", "help": "HTTP.", "label": "Http", "name": "http"}, {"description": "FTP", "help": "FTP.", "label": "Ftp", "name": "ftp"}, {"description": "NNTP", "help": "NNTP.", "label": "Nntp", "name": "nntp"}, {"description": "IMAPS", "help": "IMAPS.", "label": "Imaps", "name": "imaps"}, {"description": "SMTPS", "help": "SMTPS.", "label": "Smtps", "name": "smtps"}, {"description": "POP3S", "help": "POP3S.", "label": "Pop3S", "name": "pop3s"}, {"description": "HTTPS", "help": "HTTPS.", "label": "Https", "name": "https"}, {"description": "FTPS", "help": "FTPS.", "label": "Ftps", "name": "ftps"}, {"description": "MAPI", "help": "MAPI.", "label": "Mapi", "name": "mapi"}, {"description": "CIFS", "help": "CIFS.", "label": "Cifs", "name": "cifs"}, {"description": "SSH", "help": "SSH.", "label": "Ssh", "name": "ssh"}] | None = ...,
        store_machine_learning: Literal[{"description": "IMAP", "help": "IMAP.", "label": "Imap", "name": "imap"}, {"description": "SMTP", "help": "SMTP.", "label": "Smtp", "name": "smtp"}, {"description": "POP3", "help": "POP3.", "label": "Pop3", "name": "pop3"}, {"description": "HTTP", "help": "HTTP.", "label": "Http", "name": "http"}, {"description": "FTP", "help": "FTP.", "label": "Ftp", "name": "ftp"}, {"description": "NNTP", "help": "NNTP.", "label": "Nntp", "name": "nntp"}, {"description": "IMAPS", "help": "IMAPS.", "label": "Imaps", "name": "imaps"}, {"description": "SMTPS", "help": "SMTPS.", "label": "Smtps", "name": "smtps"}, {"description": "POP3S", "help": "POP3S.", "label": "Pop3S", "name": "pop3s"}, {"description": "HTTPS", "help": "HTTPS.", "label": "Https", "name": "https"}, {"description": "FTPS", "help": "FTPS.", "label": "Ftps", "name": "ftps"}, {"description": "MAPI", "help": "MAPI.", "label": "Mapi", "name": "mapi"}, {"description": "CIFS", "help": "CIFS.", "label": "Cifs", "name": "cifs"}, {"description": "SSH", "help": "SSH.", "label": "Ssh", "name": "ssh"}] | None = ...,
        lowspace: Literal[{"description": "Drop (delete) the most recently quarantined files", "help": "Drop (delete) the most recently quarantined files.", "label": "Drop New", "name": "drop-new"}, {"description": "Overwrite the oldest quarantined files", "help": "Overwrite the oldest quarantined files. That is, the files that are closest to being deleted from the quarantine.", "label": "Ovrw Old", "name": "ovrw-old"}] | None = ...,
        destination: Literal[{"description": "Files that would be quarantined are deleted", "help": "Files that would be quarantined are deleted.", "label": "Null", "name": "NULL"}, {"description": "Quarantine files to the FortiGate hard disk", "help": "Quarantine files to the FortiGate hard disk.", "label": "Disk", "name": "disk"}, {"description": "FortiAnalyzer", "help": "FortiAnalyzer", "label": "Fortianalyzer", "name": "FortiAnalyzer"}] | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: QuarantinePayload | None = ...,
        agelimit: int | None = ...,
        maxfilesize: int | None = ...,
        quarantine_quota: int | None = ...,
        drop_infected: Literal[{"description": "IMAP", "help": "IMAP.", "label": "Imap", "name": "imap"}, {"description": "SMTP", "help": "SMTP.", "label": "Smtp", "name": "smtp"}, {"description": "POP3", "help": "POP3.", "label": "Pop3", "name": "pop3"}, {"description": "HTTP", "help": "HTTP.", "label": "Http", "name": "http"}, {"description": "FTP", "help": "FTP.", "label": "Ftp", "name": "ftp"}, {"description": "NNTP", "help": "NNTP.", "label": "Nntp", "name": "nntp"}, {"description": "IMAPS", "help": "IMAPS.", "label": "Imaps", "name": "imaps"}, {"description": "SMTPS", "help": "SMTPS.", "label": "Smtps", "name": "smtps"}, {"description": "POP3S", "help": "POP3S.", "label": "Pop3S", "name": "pop3s"}, {"description": "HTTPS", "help": "HTTPS.", "label": "Https", "name": "https"}, {"description": "FTPS", "help": "FTPS.", "label": "Ftps", "name": "ftps"}, {"description": "MAPI", "help": "MAPI.", "label": "Mapi", "name": "mapi"}, {"description": "CIFS", "help": "CIFS.", "label": "Cifs", "name": "cifs"}, {"description": "SSH", "help": "SSH.", "label": "Ssh", "name": "ssh"}] | None = ...,
        store_infected: Literal[{"description": "IMAP", "help": "IMAP.", "label": "Imap", "name": "imap"}, {"description": "SMTP", "help": "SMTP.", "label": "Smtp", "name": "smtp"}, {"description": "POP3", "help": "POP3.", "label": "Pop3", "name": "pop3"}, {"description": "HTTP", "help": "HTTP.", "label": "Http", "name": "http"}, {"description": "FTP", "help": "FTP.", "label": "Ftp", "name": "ftp"}, {"description": "NNTP", "help": "NNTP.", "label": "Nntp", "name": "nntp"}, {"description": "IMAPS", "help": "IMAPS.", "label": "Imaps", "name": "imaps"}, {"description": "SMTPS", "help": "SMTPS.", "label": "Smtps", "name": "smtps"}, {"description": "POP3S", "help": "POP3S.", "label": "Pop3S", "name": "pop3s"}, {"description": "HTTPS", "help": "HTTPS.", "label": "Https", "name": "https"}, {"description": "FTPS", "help": "FTPS.", "label": "Ftps", "name": "ftps"}, {"description": "MAPI", "help": "MAPI.", "label": "Mapi", "name": "mapi"}, {"description": "CIFS", "help": "CIFS.", "label": "Cifs", "name": "cifs"}, {"description": "SSH", "help": "SSH.", "label": "Ssh", "name": "ssh"}] | None = ...,
        drop_machine_learning: Literal[{"description": "IMAP", "help": "IMAP.", "label": "Imap", "name": "imap"}, {"description": "SMTP", "help": "SMTP.", "label": "Smtp", "name": "smtp"}, {"description": "POP3", "help": "POP3.", "label": "Pop3", "name": "pop3"}, {"description": "HTTP", "help": "HTTP.", "label": "Http", "name": "http"}, {"description": "FTP", "help": "FTP.", "label": "Ftp", "name": "ftp"}, {"description": "NNTP", "help": "NNTP.", "label": "Nntp", "name": "nntp"}, {"description": "IMAPS", "help": "IMAPS.", "label": "Imaps", "name": "imaps"}, {"description": "SMTPS", "help": "SMTPS.", "label": "Smtps", "name": "smtps"}, {"description": "POP3S", "help": "POP3S.", "label": "Pop3S", "name": "pop3s"}, {"description": "HTTPS", "help": "HTTPS.", "label": "Https", "name": "https"}, {"description": "FTPS", "help": "FTPS.", "label": "Ftps", "name": "ftps"}, {"description": "MAPI", "help": "MAPI.", "label": "Mapi", "name": "mapi"}, {"description": "CIFS", "help": "CIFS.", "label": "Cifs", "name": "cifs"}, {"description": "SSH", "help": "SSH.", "label": "Ssh", "name": "ssh"}] | None = ...,
        store_machine_learning: Literal[{"description": "IMAP", "help": "IMAP.", "label": "Imap", "name": "imap"}, {"description": "SMTP", "help": "SMTP.", "label": "Smtp", "name": "smtp"}, {"description": "POP3", "help": "POP3.", "label": "Pop3", "name": "pop3"}, {"description": "HTTP", "help": "HTTP.", "label": "Http", "name": "http"}, {"description": "FTP", "help": "FTP.", "label": "Ftp", "name": "ftp"}, {"description": "NNTP", "help": "NNTP.", "label": "Nntp", "name": "nntp"}, {"description": "IMAPS", "help": "IMAPS.", "label": "Imaps", "name": "imaps"}, {"description": "SMTPS", "help": "SMTPS.", "label": "Smtps", "name": "smtps"}, {"description": "POP3S", "help": "POP3S.", "label": "Pop3S", "name": "pop3s"}, {"description": "HTTPS", "help": "HTTPS.", "label": "Https", "name": "https"}, {"description": "FTPS", "help": "FTPS.", "label": "Ftps", "name": "ftps"}, {"description": "MAPI", "help": "MAPI.", "label": "Mapi", "name": "mapi"}, {"description": "CIFS", "help": "CIFS.", "label": "Cifs", "name": "cifs"}, {"description": "SSH", "help": "SSH.", "label": "Ssh", "name": "ssh"}] | None = ...,
        lowspace: Literal[{"description": "Drop (delete) the most recently quarantined files", "help": "Drop (delete) the most recently quarantined files.", "label": "Drop New", "name": "drop-new"}, {"description": "Overwrite the oldest quarantined files", "help": "Overwrite the oldest quarantined files. That is, the files that are closest to being deleted from the quarantine.", "label": "Ovrw Old", "name": "ovrw-old"}] | None = ...,
        destination: Literal[{"description": "Files that would be quarantined are deleted", "help": "Files that would be quarantined are deleted.", "label": "Null", "name": "NULL"}, {"description": "Quarantine files to the FortiGate hard disk", "help": "Quarantine files to the FortiGate hard disk.", "label": "Disk", "name": "disk"}, {"description": "FortiAnalyzer", "help": "FortiAnalyzer", "label": "Fortianalyzer", "name": "FortiAnalyzer"}] | None = ...,
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
        payload_dict: QuarantinePayload | None = ...,
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
    "Quarantine",
    "QuarantinePayload",
]