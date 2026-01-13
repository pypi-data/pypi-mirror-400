from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class SettingPayload(TypedDict, total=False):
    """
    Type hints for log/disk/setting payload fields.
    
    Settings for local disk logging.
    
    **Related Resources:**

    Dependencies (resources this endpoint references):
        - :class:`~.system.interface.InterfaceEndpoint` (via: interface)

    **Usage:**
        payload: SettingPayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    status: Literal[{"description": "Log to local disk", "help": "Log to local disk.", "label": "Enable", "name": "enable"}, {"description": "Do not log to local disk", "help": "Do not log to local disk.", "label": "Disable", "name": "disable"}]  # Enable/disable local disk logging.
    ips_archive: NotRequired[Literal[{"description": "Enable IPS packet archiving", "help": "Enable IPS packet archiving.", "label": "Enable", "name": "enable"}, {"description": "Disable IPS packet archiving", "help": "Disable IPS packet archiving.", "label": "Disable", "name": "disable"}]]  # Enable/disable IPS packet archiving to the local disk.
    max_log_file_size: NotRequired[int]  # Maximum log file size before rolling (1 - 100 Mbytes).
    max_policy_packet_capture_size: NotRequired[int]  # Maximum size of policy sniffer in MB (0 means unlimited).
    roll_schedule: NotRequired[Literal[{"description": "Check the log file once a day", "help": "Check the log file once a day.", "label": "Daily", "name": "daily"}, {"description": "Check the log file once a week", "help": "Check the log file once a week.", "label": "Weekly", "name": "weekly"}]]  # Frequency to check log file for rolling.
    roll_day: NotRequired[Literal[{"description": "Sunday    monday:Monday    tuesday:Tuesday    wednesday:Wednesday    thursday:Thursday    friday:Friday    saturday:Saturday", "help": "Sunday", "label": "Sunday", "name": "sunday"}, {"help": "Monday", "label": "Monday", "name": "monday"}, {"help": "Tuesday", "label": "Tuesday", "name": "tuesday"}, {"help": "Wednesday", "label": "Wednesday", "name": "wednesday"}, {"help": "Thursday", "label": "Thursday", "name": "thursday"}, {"help": "Friday", "label": "Friday", "name": "friday"}, {"help": "Saturday", "label": "Saturday", "name": "saturday"}]]  # Day of week on which to roll log file.
    roll_time: NotRequired[str]  # Time of day to roll the log file (hh:mm).
    diskfull: NotRequired[Literal[{"description": "Overwrite the oldest logs when the log disk is full", "help": "Overwrite the oldest logs when the log disk is full.", "label": "Overwrite", "name": "overwrite"}, {"description": "Stop logging when the log disk is full", "help": "Stop logging when the log disk is full.", "label": "Nolog", "name": "nolog"}]]  # Action to take when disk is full. The system can overwrite t
    log_quota: NotRequired[int]  # Disk log quota (MB).
    dlp_archive_quota: NotRequired[int]  # DLP archive quota (MB).
    report_quota: NotRequired[int]  # Report db quota (MB).
    maximum_log_age: NotRequired[int]  # Delete log files older than (days).
    upload: NotRequired[Literal[{"description": "Enable uploading log files when they are rolled", "help": "Enable uploading log files when they are rolled.", "label": "Enable", "name": "enable"}, {"description": "Disable uploading log files when they are rolled", "help": "Disable uploading log files when they are rolled.", "label": "Disable", "name": "disable"}]]  # Enable/disable uploading log files when they are rolled.
    upload_destination: NotRequired[Literal[{"description": "Upload rolled log files to an FTP server", "help": "Upload rolled log files to an FTP server.", "label": "Ftp Server", "name": "ftp-server"}]]  # The type of server to upload log files to. Only FTP is curre
    uploadip: str  # IP address of the FTP server to upload log files to.
    uploadport: NotRequired[int]  # TCP port to use for communicating with the FTP server (defau
    source_ip: NotRequired[str]  # Source IP address to use for uploading disk log files.
    uploaduser: str  # Username required to log into the FTP server to upload disk 
    uploadpass: NotRequired[str]  # Password required to log into the FTP server to upload disk 
    uploaddir: NotRequired[str]  # The remote directory on the FTP server to upload log files t
    uploadtype: NotRequired[Literal[{"description": "Upload traffic log", "help": "Upload traffic log.", "label": "Traffic", "name": "traffic"}, {"description": "Upload event log", "help": "Upload event log.", "label": "Event", "name": "event"}, {"description": "Upload anti-virus log", "help": "Upload anti-virus log.", "label": "Virus", "name": "virus"}, {"description": "Upload web filter log", "help": "Upload web filter log.", "label": "Webfilter", "name": "webfilter"}, {"description": "Upload IPS log", "help": "Upload IPS log.", "label": "Ips", "name": "IPS"}, {"description": "Upload spam filter log", "help": "Upload spam filter log.", "label": "Emailfilter", "name": "emailfilter"}, {"description": "Upload DLP archive", "help": "Upload DLP archive.", "label": "Dlp Archive", "name": "dlp-archive"}, {"description": "Upload anomaly log", "help": "Upload anomaly log.", "label": "Anomaly", "name": "anomaly"}, {"description": "Upload VoIP log", "help": "Upload VoIP log.", "label": "Voip", "name": "voip"}, {"description": "Upload DLP log", "help": "Upload DLP log.", "label": "Dlp", "name": "dlp"}, {"description": "Upload application control log", "help": "Upload application control log.", "label": "App Ctrl", "name": "app-ctrl"}, {"description": "Upload web application firewall log", "help": "Upload web application firewall log.", "label": "Waf", "name": "waf"}, {"help": "Upload GTP log.", "label": "Gtp", "name": "gtp"}, {"description": "Upload DNS log", "help": "Upload DNS log.", "label": "Dns", "name": "dns"}, {"description": "Upload SSH log", "help": "Upload SSH log.", "label": "Ssh", "name": "ssh"}, {"description": "Upload SSL log", "help": "Upload SSL log.", "label": "Ssl", "name": "ssl"}, {"description": "Upload file-filter log", "help": "Upload file-filter log.", "label": "File Filter", "name": "file-filter"}, {"description": "Upload ICAP log", "help": "Upload ICAP log.", "label": "Icap", "name": "icap"}, {"description": "Upload virtual-patch log", "help": "Upload virtual-patch log.", "label": "Virtual Patch", "name": "virtual-patch"}, {"description": "Upload debug log", "help": "Upload debug log.", "label": "Debug", "name": "debug"}]]  # Types of log files to upload. Separate multiple entries with
    uploadsched: NotRequired[Literal[{"description": "Upload when rolling", "help": "Upload when rolling.", "label": "Disable", "name": "disable"}, {"description": "Scheduled upload", "help": "Scheduled upload.", "label": "Enable", "name": "enable"}]]  # Set the schedule for uploading log files to the FTP server (
    uploadtime: NotRequired[str]  # Time of day at which log files are uploaded if uploadsched i
    upload_delete_files: NotRequired[Literal[{"description": "Delete log files after uploading", "help": "Delete log files after uploading.", "label": "Enable", "name": "enable"}, {"description": "Do not delete log files after uploading", "help": "Do not delete log files after uploading.", "label": "Disable", "name": "disable"}]]  # Delete log files after uploading (default = enable).
    upload_ssl_conn: NotRequired[Literal[{"description": "FTPS with high and medium encryption algorithms", "help": "FTPS with high and medium encryption algorithms.", "label": "Default", "name": "default"}, {"description": "FTPS with high encryption algorithms", "help": "FTPS with high encryption algorithms.", "label": "High", "name": "high"}, {"description": "FTPS with low encryption algorithms", "help": "FTPS with low encryption algorithms.", "label": "Low", "name": "low"}, {"description": "Disable FTPS communication", "help": "Disable FTPS communication.", "label": "Disable", "name": "disable"}]]  # Enable/disable encrypted FTPS communication to upload log fi
    full_first_warning_threshold: NotRequired[int]  # Log full first warning threshold as a percent (1 - 98, defau
    full_second_warning_threshold: NotRequired[int]  # Log full second warning threshold as a percent (2 - 99, defa
    full_final_warning_threshold: NotRequired[int]  # Log full final warning threshold as a percent (3 - 100, defa
    interface_select_method: NotRequired[Literal[{"description": "Set outgoing interface automatically", "help": "Set outgoing interface automatically.", "label": "Auto", "name": "auto"}, {"description": "Set outgoing interface by SD-WAN or policy routing rules", "help": "Set outgoing interface by SD-WAN or policy routing rules.", "label": "Sdwan", "name": "sdwan"}, {"description": "Set outgoing interface manually", "help": "Set outgoing interface manually.", "label": "Specify", "name": "specify"}]]  # Specify how to select outgoing interface to reach server.
    interface: str  # Specify outgoing interface to reach server.
    vrf_select: NotRequired[int]  # VRF ID used for connection to server.


class Setting:
    """
    Settings for local disk logging.
    
    Path: log/disk/setting
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
        payload_dict: SettingPayload | None = ...,
        status: Literal[{"description": "Log to local disk", "help": "Log to local disk.", "label": "Enable", "name": "enable"}, {"description": "Do not log to local disk", "help": "Do not log to local disk.", "label": "Disable", "name": "disable"}] | None = ...,
        ips_archive: Literal[{"description": "Enable IPS packet archiving", "help": "Enable IPS packet archiving.", "label": "Enable", "name": "enable"}, {"description": "Disable IPS packet archiving", "help": "Disable IPS packet archiving.", "label": "Disable", "name": "disable"}] | None = ...,
        max_log_file_size: int | None = ...,
        max_policy_packet_capture_size: int | None = ...,
        roll_schedule: Literal[{"description": "Check the log file once a day", "help": "Check the log file once a day.", "label": "Daily", "name": "daily"}, {"description": "Check the log file once a week", "help": "Check the log file once a week.", "label": "Weekly", "name": "weekly"}] | None = ...,
        roll_day: Literal[{"description": "Sunday    monday:Monday    tuesday:Tuesday    wednesday:Wednesday    thursday:Thursday    friday:Friday    saturday:Saturday", "help": "Sunday", "label": "Sunday", "name": "sunday"}, {"help": "Monday", "label": "Monday", "name": "monday"}, {"help": "Tuesday", "label": "Tuesday", "name": "tuesday"}, {"help": "Wednesday", "label": "Wednesday", "name": "wednesday"}, {"help": "Thursday", "label": "Thursday", "name": "thursday"}, {"help": "Friday", "label": "Friday", "name": "friday"}, {"help": "Saturday", "label": "Saturday", "name": "saturday"}] | None = ...,
        roll_time: str | None = ...,
        diskfull: Literal[{"description": "Overwrite the oldest logs when the log disk is full", "help": "Overwrite the oldest logs when the log disk is full.", "label": "Overwrite", "name": "overwrite"}, {"description": "Stop logging when the log disk is full", "help": "Stop logging when the log disk is full.", "label": "Nolog", "name": "nolog"}] | None = ...,
        log_quota: int | None = ...,
        dlp_archive_quota: int | None = ...,
        report_quota: int | None = ...,
        maximum_log_age: int | None = ...,
        upload: Literal[{"description": "Enable uploading log files when they are rolled", "help": "Enable uploading log files when they are rolled.", "label": "Enable", "name": "enable"}, {"description": "Disable uploading log files when they are rolled", "help": "Disable uploading log files when they are rolled.", "label": "Disable", "name": "disable"}] | None = ...,
        upload_destination: Literal[{"description": "Upload rolled log files to an FTP server", "help": "Upload rolled log files to an FTP server.", "label": "Ftp Server", "name": "ftp-server"}] | None = ...,
        uploadip: str | None = ...,
        uploadport: int | None = ...,
        source_ip: str | None = ...,
        uploaduser: str | None = ...,
        uploadpass: str | None = ...,
        uploaddir: str | None = ...,
        uploadtype: Literal[{"description": "Upload traffic log", "help": "Upload traffic log.", "label": "Traffic", "name": "traffic"}, {"description": "Upload event log", "help": "Upload event log.", "label": "Event", "name": "event"}, {"description": "Upload anti-virus log", "help": "Upload anti-virus log.", "label": "Virus", "name": "virus"}, {"description": "Upload web filter log", "help": "Upload web filter log.", "label": "Webfilter", "name": "webfilter"}, {"description": "Upload IPS log", "help": "Upload IPS log.", "label": "Ips", "name": "IPS"}, {"description": "Upload spam filter log", "help": "Upload spam filter log.", "label": "Emailfilter", "name": "emailfilter"}, {"description": "Upload DLP archive", "help": "Upload DLP archive.", "label": "Dlp Archive", "name": "dlp-archive"}, {"description": "Upload anomaly log", "help": "Upload anomaly log.", "label": "Anomaly", "name": "anomaly"}, {"description": "Upload VoIP log", "help": "Upload VoIP log.", "label": "Voip", "name": "voip"}, {"description": "Upload DLP log", "help": "Upload DLP log.", "label": "Dlp", "name": "dlp"}, {"description": "Upload application control log", "help": "Upload application control log.", "label": "App Ctrl", "name": "app-ctrl"}, {"description": "Upload web application firewall log", "help": "Upload web application firewall log.", "label": "Waf", "name": "waf"}, {"help": "Upload GTP log.", "label": "Gtp", "name": "gtp"}, {"description": "Upload DNS log", "help": "Upload DNS log.", "label": "Dns", "name": "dns"}, {"description": "Upload SSH log", "help": "Upload SSH log.", "label": "Ssh", "name": "ssh"}, {"description": "Upload SSL log", "help": "Upload SSL log.", "label": "Ssl", "name": "ssl"}, {"description": "Upload file-filter log", "help": "Upload file-filter log.", "label": "File Filter", "name": "file-filter"}, {"description": "Upload ICAP log", "help": "Upload ICAP log.", "label": "Icap", "name": "icap"}, {"description": "Upload virtual-patch log", "help": "Upload virtual-patch log.", "label": "Virtual Patch", "name": "virtual-patch"}, {"description": "Upload debug log", "help": "Upload debug log.", "label": "Debug", "name": "debug"}] | None = ...,
        uploadsched: Literal[{"description": "Upload when rolling", "help": "Upload when rolling.", "label": "Disable", "name": "disable"}, {"description": "Scheduled upload", "help": "Scheduled upload.", "label": "Enable", "name": "enable"}] | None = ...,
        uploadtime: str | None = ...,
        upload_delete_files: Literal[{"description": "Delete log files after uploading", "help": "Delete log files after uploading.", "label": "Enable", "name": "enable"}, {"description": "Do not delete log files after uploading", "help": "Do not delete log files after uploading.", "label": "Disable", "name": "disable"}] | None = ...,
        upload_ssl_conn: Literal[{"description": "FTPS with high and medium encryption algorithms", "help": "FTPS with high and medium encryption algorithms.", "label": "Default", "name": "default"}, {"description": "FTPS with high encryption algorithms", "help": "FTPS with high encryption algorithms.", "label": "High", "name": "high"}, {"description": "FTPS with low encryption algorithms", "help": "FTPS with low encryption algorithms.", "label": "Low", "name": "low"}, {"description": "Disable FTPS communication", "help": "Disable FTPS communication.", "label": "Disable", "name": "disable"}] | None = ...,
        full_first_warning_threshold: int | None = ...,
        full_second_warning_threshold: int | None = ...,
        full_final_warning_threshold: int | None = ...,
        interface_select_method: Literal[{"description": "Set outgoing interface automatically", "help": "Set outgoing interface automatically.", "label": "Auto", "name": "auto"}, {"description": "Set outgoing interface by SD-WAN or policy routing rules", "help": "Set outgoing interface by SD-WAN or policy routing rules.", "label": "Sdwan", "name": "sdwan"}, {"description": "Set outgoing interface manually", "help": "Set outgoing interface manually.", "label": "Specify", "name": "specify"}] | None = ...,
        interface: str | None = ...,
        vrf_select: int | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: SettingPayload | None = ...,
        status: Literal[{"description": "Log to local disk", "help": "Log to local disk.", "label": "Enable", "name": "enable"}, {"description": "Do not log to local disk", "help": "Do not log to local disk.", "label": "Disable", "name": "disable"}] | None = ...,
        ips_archive: Literal[{"description": "Enable IPS packet archiving", "help": "Enable IPS packet archiving.", "label": "Enable", "name": "enable"}, {"description": "Disable IPS packet archiving", "help": "Disable IPS packet archiving.", "label": "Disable", "name": "disable"}] | None = ...,
        max_log_file_size: int | None = ...,
        max_policy_packet_capture_size: int | None = ...,
        roll_schedule: Literal[{"description": "Check the log file once a day", "help": "Check the log file once a day.", "label": "Daily", "name": "daily"}, {"description": "Check the log file once a week", "help": "Check the log file once a week.", "label": "Weekly", "name": "weekly"}] | None = ...,
        roll_day: Literal[{"description": "Sunday    monday:Monday    tuesday:Tuesday    wednesday:Wednesday    thursday:Thursday    friday:Friday    saturday:Saturday", "help": "Sunday", "label": "Sunday", "name": "sunday"}, {"help": "Monday", "label": "Monday", "name": "monday"}, {"help": "Tuesday", "label": "Tuesday", "name": "tuesday"}, {"help": "Wednesday", "label": "Wednesday", "name": "wednesday"}, {"help": "Thursday", "label": "Thursday", "name": "thursday"}, {"help": "Friday", "label": "Friday", "name": "friday"}, {"help": "Saturday", "label": "Saturday", "name": "saturday"}] | None = ...,
        roll_time: str | None = ...,
        diskfull: Literal[{"description": "Overwrite the oldest logs when the log disk is full", "help": "Overwrite the oldest logs when the log disk is full.", "label": "Overwrite", "name": "overwrite"}, {"description": "Stop logging when the log disk is full", "help": "Stop logging when the log disk is full.", "label": "Nolog", "name": "nolog"}] | None = ...,
        log_quota: int | None = ...,
        dlp_archive_quota: int | None = ...,
        report_quota: int | None = ...,
        maximum_log_age: int | None = ...,
        upload: Literal[{"description": "Enable uploading log files when they are rolled", "help": "Enable uploading log files when they are rolled.", "label": "Enable", "name": "enable"}, {"description": "Disable uploading log files when they are rolled", "help": "Disable uploading log files when they are rolled.", "label": "Disable", "name": "disable"}] | None = ...,
        upload_destination: Literal[{"description": "Upload rolled log files to an FTP server", "help": "Upload rolled log files to an FTP server.", "label": "Ftp Server", "name": "ftp-server"}] | None = ...,
        uploadip: str | None = ...,
        uploadport: int | None = ...,
        source_ip: str | None = ...,
        uploaduser: str | None = ...,
        uploadpass: str | None = ...,
        uploaddir: str | None = ...,
        uploadtype: Literal[{"description": "Upload traffic log", "help": "Upload traffic log.", "label": "Traffic", "name": "traffic"}, {"description": "Upload event log", "help": "Upload event log.", "label": "Event", "name": "event"}, {"description": "Upload anti-virus log", "help": "Upload anti-virus log.", "label": "Virus", "name": "virus"}, {"description": "Upload web filter log", "help": "Upload web filter log.", "label": "Webfilter", "name": "webfilter"}, {"description": "Upload IPS log", "help": "Upload IPS log.", "label": "Ips", "name": "IPS"}, {"description": "Upload spam filter log", "help": "Upload spam filter log.", "label": "Emailfilter", "name": "emailfilter"}, {"description": "Upload DLP archive", "help": "Upload DLP archive.", "label": "Dlp Archive", "name": "dlp-archive"}, {"description": "Upload anomaly log", "help": "Upload anomaly log.", "label": "Anomaly", "name": "anomaly"}, {"description": "Upload VoIP log", "help": "Upload VoIP log.", "label": "Voip", "name": "voip"}, {"description": "Upload DLP log", "help": "Upload DLP log.", "label": "Dlp", "name": "dlp"}, {"description": "Upload application control log", "help": "Upload application control log.", "label": "App Ctrl", "name": "app-ctrl"}, {"description": "Upload web application firewall log", "help": "Upload web application firewall log.", "label": "Waf", "name": "waf"}, {"help": "Upload GTP log.", "label": "Gtp", "name": "gtp"}, {"description": "Upload DNS log", "help": "Upload DNS log.", "label": "Dns", "name": "dns"}, {"description": "Upload SSH log", "help": "Upload SSH log.", "label": "Ssh", "name": "ssh"}, {"description": "Upload SSL log", "help": "Upload SSL log.", "label": "Ssl", "name": "ssl"}, {"description": "Upload file-filter log", "help": "Upload file-filter log.", "label": "File Filter", "name": "file-filter"}, {"description": "Upload ICAP log", "help": "Upload ICAP log.", "label": "Icap", "name": "icap"}, {"description": "Upload virtual-patch log", "help": "Upload virtual-patch log.", "label": "Virtual Patch", "name": "virtual-patch"}, {"description": "Upload debug log", "help": "Upload debug log.", "label": "Debug", "name": "debug"}] | None = ...,
        uploadsched: Literal[{"description": "Upload when rolling", "help": "Upload when rolling.", "label": "Disable", "name": "disable"}, {"description": "Scheduled upload", "help": "Scheduled upload.", "label": "Enable", "name": "enable"}] | None = ...,
        uploadtime: str | None = ...,
        upload_delete_files: Literal[{"description": "Delete log files after uploading", "help": "Delete log files after uploading.", "label": "Enable", "name": "enable"}, {"description": "Do not delete log files after uploading", "help": "Do not delete log files after uploading.", "label": "Disable", "name": "disable"}] | None = ...,
        upload_ssl_conn: Literal[{"description": "FTPS with high and medium encryption algorithms", "help": "FTPS with high and medium encryption algorithms.", "label": "Default", "name": "default"}, {"description": "FTPS with high encryption algorithms", "help": "FTPS with high encryption algorithms.", "label": "High", "name": "high"}, {"description": "FTPS with low encryption algorithms", "help": "FTPS with low encryption algorithms.", "label": "Low", "name": "low"}, {"description": "Disable FTPS communication", "help": "Disable FTPS communication.", "label": "Disable", "name": "disable"}] | None = ...,
        full_first_warning_threshold: int | None = ...,
        full_second_warning_threshold: int | None = ...,
        full_final_warning_threshold: int | None = ...,
        interface_select_method: Literal[{"description": "Set outgoing interface automatically", "help": "Set outgoing interface automatically.", "label": "Auto", "name": "auto"}, {"description": "Set outgoing interface by SD-WAN or policy routing rules", "help": "Set outgoing interface by SD-WAN or policy routing rules.", "label": "Sdwan", "name": "sdwan"}, {"description": "Set outgoing interface manually", "help": "Set outgoing interface manually.", "label": "Specify", "name": "specify"}] | None = ...,
        interface: str | None = ...,
        vrf_select: int | None = ...,
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
        payload_dict: SettingPayload | None = ...,
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
    "Setting",
    "SettingPayload",
]