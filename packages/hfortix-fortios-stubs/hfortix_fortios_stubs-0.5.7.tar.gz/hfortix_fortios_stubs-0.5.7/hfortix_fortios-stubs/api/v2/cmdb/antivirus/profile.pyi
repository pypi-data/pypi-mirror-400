from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class ProfilePayload(TypedDict, total=False):
    """
    Type hints for antivirus/profile payload fields.
    
    Configure AntiVirus profiles.
    
    **Related Resources:**

    Dependencies (resources this endpoint references):
        - :class:`~.dlp.filepattern.FilepatternEndpoint` (via: analytics-accept-filetype, analytics-ignore-filetype)
        - :class:`~.system.replacemsg-group.ReplacemsgGroupEndpoint` (via: replacemsg-group)

    **Usage:**
        payload: ProfilePayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    name: str  # Profile name.
    comment: NotRequired[str]  # Comment.
    replacemsg_group: NotRequired[str]  # Replacement message group customized for this profile.
    feature_set: NotRequired[Literal[{"description": "Flow feature set", "help": "Flow feature set.", "label": "Flow", "name": "flow"}, {"description": "Proxy feature set", "help": "Proxy feature set.", "label": "Proxy", "name": "proxy"}]]  # Flow/proxy feature set.
    fortisandbox_mode: NotRequired[Literal[{"help": "FortiSandbox inline scan.", "label": "Inline", "name": "inline"}, {"description": "FortiSandbox post-transfer scan: submit supported files if heuristics or other methods determine they are suspicious", "help": "FortiSandbox post-transfer scan: submit supported files if heuristics or other methods determine they are suspicious.", "label": "Analytics Suspicious", "name": "analytics-suspicious"}, {"description": "FortiSandbox post-transfer scan: submit supported files for inspection", "help": "FortiSandbox post-transfer scan: submit supported files for inspection.", "label": "Analytics Everything", "name": "analytics-everything"}]]  # FortiSandbox scan modes.
    fortisandbox_max_upload: NotRequired[int]  # Maximum size of files that can be uploaded to FortiSandbox i
    analytics_ignore_filetype: NotRequired[int]  # Do not submit files matching this DLP file-pattern to FortiS
    analytics_accept_filetype: NotRequired[int]  # Only submit files matching this DLP file-pattern to FortiSan
    analytics_db: NotRequired[Literal[{"description": "Use only the standard AV signature databases", "help": "Use only the standard AV signature databases.", "label": "Disable", "name": "disable"}, {"description": "Also use the FortiSandbox signature database", "help": "Also use the FortiSandbox signature database.", "label": "Enable", "name": "enable"}]]  # Enable/disable using the FortiSandbox signature database to 
    mobile_malware_db: NotRequired[Literal[{"description": "Do not use the mobile malware signature database", "help": "Do not use the mobile malware signature database.", "label": "Disable", "name": "disable"}, {"description": "Also use the mobile malware signature database", "help": "Also use the mobile malware signature database.", "label": "Enable", "name": "enable"}]]  # Enable/disable using the mobile malware signature database.
    http: NotRequired[str]  # Configure HTTP AntiVirus options.
    ftp: NotRequired[str]  # Configure FTP AntiVirus options.
    imap: NotRequired[str]  # Configure IMAP AntiVirus options.
    pop3: NotRequired[str]  # Configure POP3 AntiVirus options.
    smtp: NotRequired[str]  # Configure SMTP AntiVirus options.
    mapi: NotRequired[str]  # Configure MAPI AntiVirus options.
    nntp: NotRequired[str]  # Configure NNTP AntiVirus options.
    cifs: NotRequired[str]  # Configure CIFS AntiVirus options.
    ssh: NotRequired[str]  # Configure SFTP and SCP AntiVirus options.
    nac_quar: NotRequired[str]  # Configure AntiVirus quarantine settings.
    content_disarm: NotRequired[str]  # AV Content Disarm and Reconstruction settings.
    outbreak_prevention_archive_scan: NotRequired[Literal[{"description": "Analyze files as sent, not the content of archives", "help": "Analyze files as sent, not the content of archives.", "label": "Disable", "name": "disable"}, {"description": "Analyze files including the content of archives", "help": "Analyze files including the content of archives.", "label": "Enable", "name": "enable"}]]  # Enable/disable outbreak-prevention archive scanning.
    external_blocklist_enable_all: NotRequired[Literal[{"description": "Use configured external blocklists", "help": "Use configured external blocklists.", "label": "Disable", "name": "disable"}, {"description": "Enable all external blocklists", "help": "Enable all external blocklists.", "label": "Enable", "name": "enable"}]]  # Enable/disable all external blocklists.
    external_blocklist: NotRequired[list[dict[str, Any]]]  # One or more external malware block lists.
    ems_threat_feed: NotRequired[Literal[{"description": "Disable use of EMS threat feed when performing AntiVirus scan", "help": "Disable use of EMS threat feed when performing AntiVirus scan.", "label": "Disable", "name": "disable"}, {"description": "Enable use of EMS threat feed when performing AntiVirus scan", "help": "Enable use of EMS threat feed when performing AntiVirus scan.", "label": "Enable", "name": "enable"}]]  # Enable/disable use of EMS threat feed when performing AntiVi
    fortindr_error_action: NotRequired[Literal[{"help": "Log FortiNDR error, but allow the file.", "label": "Log Only", "name": "log-only"}, {"help": "Block the file on FortiNDR error.", "label": "Block", "name": "block"}, {"help": "Do nothing on FortiNDR error.", "label": "Ignore", "name": "ignore"}]]  # Action to take if FortiNDR encounters an error.
    fortindr_timeout_action: NotRequired[Literal[{"help": "Log FortiNDR scan timeout, but allow the file.", "label": "Log Only", "name": "log-only"}, {"help": "Block the file on FortiNDR scan timeout.", "label": "Block", "name": "block"}, {"help": "Do nothing on FortiNDR scan timeout.", "label": "Ignore", "name": "ignore"}]]  # Action to take if FortiNDR encounters a scan timeout.
    fortisandbox_scan_timeout: NotRequired[int]  # FortiSandbox inline scan timeout in seconds (30 - 180, defau
    fortisandbox_error_action: NotRequired[Literal[{"help": "Log FortiSandbox inline scan error, but allow the file.", "label": "Log Only", "name": "log-only"}, {"help": "Block the file on FortiSandbox inline scan error.", "label": "Block", "name": "block"}, {"help": "Do nothing on FortiSandbox inline scan error.", "label": "Ignore", "name": "ignore"}]]  # Action to take if FortiSandbox inline scan encounters an err
    fortisandbox_timeout_action: NotRequired[Literal[{"help": "Log FortiSandbox inline scan timeout, but allow the file.", "label": "Log Only", "name": "log-only"}, {"help": "Block the file on FortiSandbox inline scan timeout.", "label": "Block", "name": "block"}, {"help": "Do nothing on FortiSandbox inline scan timeout.", "label": "Ignore", "name": "ignore"}]]  # Action to take if FortiSandbox inline scan encounters a scan
    av_virus_log: NotRequired[Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]]  # Enable/disable AntiVirus logging.
    extended_log: NotRequired[Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]]  # Enable/disable extended logging for antivirus.
    scan_mode: NotRequired[Literal[{"description": "On the fly decompression and scanning of certain archive files", "help": "On the fly decompression and scanning of certain archive files.", "label": "Default", "name": "default"}, {"description": "Scan archive files only after the entire file is received", "help": "Scan archive files only after the entire file is received.", "label": "Legacy", "name": "legacy"}]]  # Configure scan mode (default or legacy).


class Profile:
    """
    Configure AntiVirus profiles.
    
    Path: antivirus/profile
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
        replacemsg_group: str | None = ...,
        feature_set: Literal[{"description": "Flow feature set", "help": "Flow feature set.", "label": "Flow", "name": "flow"}, {"description": "Proxy feature set", "help": "Proxy feature set.", "label": "Proxy", "name": "proxy"}] | None = ...,
        fortisandbox_mode: Literal[{"help": "FortiSandbox inline scan.", "label": "Inline", "name": "inline"}, {"description": "FortiSandbox post-transfer scan: submit supported files if heuristics or other methods determine they are suspicious", "help": "FortiSandbox post-transfer scan: submit supported files if heuristics or other methods determine they are suspicious.", "label": "Analytics Suspicious", "name": "analytics-suspicious"}, {"description": "FortiSandbox post-transfer scan: submit supported files for inspection", "help": "FortiSandbox post-transfer scan: submit supported files for inspection.", "label": "Analytics Everything", "name": "analytics-everything"}] | None = ...,
        fortisandbox_max_upload: int | None = ...,
        analytics_ignore_filetype: int | None = ...,
        analytics_accept_filetype: int | None = ...,
        analytics_db: Literal[{"description": "Use only the standard AV signature databases", "help": "Use only the standard AV signature databases.", "label": "Disable", "name": "disable"}, {"description": "Also use the FortiSandbox signature database", "help": "Also use the FortiSandbox signature database.", "label": "Enable", "name": "enable"}] | None = ...,
        mobile_malware_db: Literal[{"description": "Do not use the mobile malware signature database", "help": "Do not use the mobile malware signature database.", "label": "Disable", "name": "disable"}, {"description": "Also use the mobile malware signature database", "help": "Also use the mobile malware signature database.", "label": "Enable", "name": "enable"}] | None = ...,
        http: str | None = ...,
        ftp: str | None = ...,
        imap: str | None = ...,
        pop3: str | None = ...,
        smtp: str | None = ...,
        mapi: str | None = ...,
        nntp: str | None = ...,
        cifs: str | None = ...,
        ssh: str | None = ...,
        nac_quar: str | None = ...,
        content_disarm: str | None = ...,
        outbreak_prevention_archive_scan: Literal[{"description": "Analyze files as sent, not the content of archives", "help": "Analyze files as sent, not the content of archives.", "label": "Disable", "name": "disable"}, {"description": "Analyze files including the content of archives", "help": "Analyze files including the content of archives.", "label": "Enable", "name": "enable"}] | None = ...,
        external_blocklist_enable_all: Literal[{"description": "Use configured external blocklists", "help": "Use configured external blocklists.", "label": "Disable", "name": "disable"}, {"description": "Enable all external blocklists", "help": "Enable all external blocklists.", "label": "Enable", "name": "enable"}] | None = ...,
        external_blocklist: list[dict[str, Any]] | None = ...,
        ems_threat_feed: Literal[{"description": "Disable use of EMS threat feed when performing AntiVirus scan", "help": "Disable use of EMS threat feed when performing AntiVirus scan.", "label": "Disable", "name": "disable"}, {"description": "Enable use of EMS threat feed when performing AntiVirus scan", "help": "Enable use of EMS threat feed when performing AntiVirus scan.", "label": "Enable", "name": "enable"}] | None = ...,
        fortindr_error_action: Literal[{"help": "Log FortiNDR error, but allow the file.", "label": "Log Only", "name": "log-only"}, {"help": "Block the file on FortiNDR error.", "label": "Block", "name": "block"}, {"help": "Do nothing on FortiNDR error.", "label": "Ignore", "name": "ignore"}] | None = ...,
        fortindr_timeout_action: Literal[{"help": "Log FortiNDR scan timeout, but allow the file.", "label": "Log Only", "name": "log-only"}, {"help": "Block the file on FortiNDR scan timeout.", "label": "Block", "name": "block"}, {"help": "Do nothing on FortiNDR scan timeout.", "label": "Ignore", "name": "ignore"}] | None = ...,
        fortisandbox_scan_timeout: int | None = ...,
        fortisandbox_error_action: Literal[{"help": "Log FortiSandbox inline scan error, but allow the file.", "label": "Log Only", "name": "log-only"}, {"help": "Block the file on FortiSandbox inline scan error.", "label": "Block", "name": "block"}, {"help": "Do nothing on FortiSandbox inline scan error.", "label": "Ignore", "name": "ignore"}] | None = ...,
        fortisandbox_timeout_action: Literal[{"help": "Log FortiSandbox inline scan timeout, but allow the file.", "label": "Log Only", "name": "log-only"}, {"help": "Block the file on FortiSandbox inline scan timeout.", "label": "Block", "name": "block"}, {"help": "Do nothing on FortiSandbox inline scan timeout.", "label": "Ignore", "name": "ignore"}] | None = ...,
        av_virus_log: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        extended_log: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        scan_mode: Literal[{"description": "On the fly decompression and scanning of certain archive files", "help": "On the fly decompression and scanning of certain archive files.", "label": "Default", "name": "default"}, {"description": "Scan archive files only after the entire file is received", "help": "Scan archive files only after the entire file is received.", "label": "Legacy", "name": "legacy"}] | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: ProfilePayload | None = ...,
        name: str | None = ...,
        comment: str | None = ...,
        replacemsg_group: str | None = ...,
        feature_set: Literal[{"description": "Flow feature set", "help": "Flow feature set.", "label": "Flow", "name": "flow"}, {"description": "Proxy feature set", "help": "Proxy feature set.", "label": "Proxy", "name": "proxy"}] | None = ...,
        fortisandbox_mode: Literal[{"help": "FortiSandbox inline scan.", "label": "Inline", "name": "inline"}, {"description": "FortiSandbox post-transfer scan: submit supported files if heuristics or other methods determine they are suspicious", "help": "FortiSandbox post-transfer scan: submit supported files if heuristics or other methods determine they are suspicious.", "label": "Analytics Suspicious", "name": "analytics-suspicious"}, {"description": "FortiSandbox post-transfer scan: submit supported files for inspection", "help": "FortiSandbox post-transfer scan: submit supported files for inspection.", "label": "Analytics Everything", "name": "analytics-everything"}] | None = ...,
        fortisandbox_max_upload: int | None = ...,
        analytics_ignore_filetype: int | None = ...,
        analytics_accept_filetype: int | None = ...,
        analytics_db: Literal[{"description": "Use only the standard AV signature databases", "help": "Use only the standard AV signature databases.", "label": "Disable", "name": "disable"}, {"description": "Also use the FortiSandbox signature database", "help": "Also use the FortiSandbox signature database.", "label": "Enable", "name": "enable"}] | None = ...,
        mobile_malware_db: Literal[{"description": "Do not use the mobile malware signature database", "help": "Do not use the mobile malware signature database.", "label": "Disable", "name": "disable"}, {"description": "Also use the mobile malware signature database", "help": "Also use the mobile malware signature database.", "label": "Enable", "name": "enable"}] | None = ...,
        http: str | None = ...,
        ftp: str | None = ...,
        imap: str | None = ...,
        pop3: str | None = ...,
        smtp: str | None = ...,
        mapi: str | None = ...,
        nntp: str | None = ...,
        cifs: str | None = ...,
        ssh: str | None = ...,
        nac_quar: str | None = ...,
        content_disarm: str | None = ...,
        outbreak_prevention_archive_scan: Literal[{"description": "Analyze files as sent, not the content of archives", "help": "Analyze files as sent, not the content of archives.", "label": "Disable", "name": "disable"}, {"description": "Analyze files including the content of archives", "help": "Analyze files including the content of archives.", "label": "Enable", "name": "enable"}] | None = ...,
        external_blocklist_enable_all: Literal[{"description": "Use configured external blocklists", "help": "Use configured external blocklists.", "label": "Disable", "name": "disable"}, {"description": "Enable all external blocklists", "help": "Enable all external blocklists.", "label": "Enable", "name": "enable"}] | None = ...,
        external_blocklist: list[dict[str, Any]] | None = ...,
        ems_threat_feed: Literal[{"description": "Disable use of EMS threat feed when performing AntiVirus scan", "help": "Disable use of EMS threat feed when performing AntiVirus scan.", "label": "Disable", "name": "disable"}, {"description": "Enable use of EMS threat feed when performing AntiVirus scan", "help": "Enable use of EMS threat feed when performing AntiVirus scan.", "label": "Enable", "name": "enable"}] | None = ...,
        fortindr_error_action: Literal[{"help": "Log FortiNDR error, but allow the file.", "label": "Log Only", "name": "log-only"}, {"help": "Block the file on FortiNDR error.", "label": "Block", "name": "block"}, {"help": "Do nothing on FortiNDR error.", "label": "Ignore", "name": "ignore"}] | None = ...,
        fortindr_timeout_action: Literal[{"help": "Log FortiNDR scan timeout, but allow the file.", "label": "Log Only", "name": "log-only"}, {"help": "Block the file on FortiNDR scan timeout.", "label": "Block", "name": "block"}, {"help": "Do nothing on FortiNDR scan timeout.", "label": "Ignore", "name": "ignore"}] | None = ...,
        fortisandbox_scan_timeout: int | None = ...,
        fortisandbox_error_action: Literal[{"help": "Log FortiSandbox inline scan error, but allow the file.", "label": "Log Only", "name": "log-only"}, {"help": "Block the file on FortiSandbox inline scan error.", "label": "Block", "name": "block"}, {"help": "Do nothing on FortiSandbox inline scan error.", "label": "Ignore", "name": "ignore"}] | None = ...,
        fortisandbox_timeout_action: Literal[{"help": "Log FortiSandbox inline scan timeout, but allow the file.", "label": "Log Only", "name": "log-only"}, {"help": "Block the file on FortiSandbox inline scan timeout.", "label": "Block", "name": "block"}, {"help": "Do nothing on FortiSandbox inline scan timeout.", "label": "Ignore", "name": "ignore"}] | None = ...,
        av_virus_log: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        extended_log: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        scan_mode: Literal[{"description": "On the fly decompression and scanning of certain archive files", "help": "On the fly decompression and scanning of certain archive files.", "label": "Default", "name": "default"}, {"description": "Scan archive files only after the entire file is received", "help": "Scan archive files only after the entire file is received.", "label": "Legacy", "name": "legacy"}] | None = ...,
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