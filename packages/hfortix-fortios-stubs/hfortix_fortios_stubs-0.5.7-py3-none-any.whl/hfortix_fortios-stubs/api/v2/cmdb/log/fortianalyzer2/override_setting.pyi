from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class OverrideSettingPayload(TypedDict, total=False):
    """
    Type hints for log/fortianalyzer2/override_setting payload fields.
    
    Override FortiAnalyzer settings.
    
    **Related Resources:**

    Dependencies (resources this endpoint references):
        - :class:`~.certificate.ca.CaEndpoint` (via: server-cert-ca)
        - :class:`~.certificate.local.LocalEndpoint` (via: certificate)
        - :class:`~.system.interface.InterfaceEndpoint` (via: interface)
        - :class:`~.vpn.certificate.ca.CaEndpoint` (via: server-cert-ca)

    **Usage:**
        payload: OverrideSettingPayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    use_management_vdom: NotRequired[Literal[{"description": "Enable use of management VDOM IP address as source IP for logs sent to FortiAnalyzer", "help": "Enable use of management VDOM IP address as source IP for logs sent to FortiAnalyzer.", "label": "Enable", "name": "enable"}, {"description": "Disable use of management VDOM IP address as source IP for logs sent to FortiAnalyzer", "help": "Disable use of management VDOM IP address as source IP for logs sent to FortiAnalyzer.", "label": "Disable", "name": "disable"}]]  # Enable/disable use of management VDOM IP address as source I
    status: NotRequired[Literal[{"description": "Enable logging to FortiAnalyzer", "help": "Enable logging to FortiAnalyzer.", "label": "Enable", "name": "enable"}, {"description": "Disable logging to FortiAnalyzer", "help": "Disable logging to FortiAnalyzer.", "label": "Disable", "name": "disable"}]]  # Enable/disable logging to FortiAnalyzer.
    ips_archive: NotRequired[Literal[{"description": "Enable IPS packet archive logging", "help": "Enable IPS packet archive logging.", "label": "Enable", "name": "enable"}, {"description": "Disable IPS packet archive logging", "help": "Disable IPS packet archive logging.", "label": "Disable", "name": "disable"}]]  # Enable/disable IPS packet archive logging.
    server: str  # The remote FortiAnalyzer.
    alt_server: NotRequired[str]  # Alternate FortiAnalyzer.
    fallback_to_primary: NotRequired[Literal[{"description": "Enable this FortiGate unit to fallback to the primary FortiAnalyzer when it is available", "help": "Enable this FortiGate unit to fallback to the primary FortiAnalyzer when it is available.", "label": "Enable", "name": "enable"}, {"description": "Disable this FortiGate unit to fallback to the primary FortiAnalyzer when it is available", "help": "Disable this FortiGate unit to fallback to the primary FortiAnalyzer when it is available.", "label": "Disable", "name": "disable"}]]  # Enable/disable this FortiGate unit to fallback to the primar
    certificate_verification: NotRequired[Literal[{"description": "Enable identity verification of FortiAnalyzer by use of certificate", "help": "Enable identity verification of FortiAnalyzer by use of certificate.", "label": "Enable", "name": "enable"}, {"description": "Disable identity verification of FortiAnalyzer by use of certificate", "help": "Disable identity verification of FortiAnalyzer by use of certificate.", "label": "Disable", "name": "disable"}]]  # Enable/disable identity verification of FortiAnalyzer by use
    serial: NotRequired[list[dict[str, Any]]]  # Serial numbers of the FortiAnalyzer.
    server_cert_ca: NotRequired[str]  # Mandatory CA on FortiGate in certificate chain of server.
    preshared_key: NotRequired[str]  # Preshared-key used for auto-authorization on FortiAnalyzer.
    access_config: NotRequired[Literal[{"description": "Enable FortiAnalyzer access to configuration and data", "help": "Enable FortiAnalyzer access to configuration and data.", "label": "Enable", "name": "enable"}, {"description": "Disable FortiAnalyzer access to configuration and data", "help": "Disable FortiAnalyzer access to configuration and data.", "label": "Disable", "name": "disable"}]]  # Enable/disable FortiAnalyzer access to configuration and dat
    hmac_algorithm: NotRequired[Literal[{"description": "Use SHA256 as HMAC algorithm", "help": "Use SHA256 as HMAC algorithm.", "label": "Sha256", "name": "sha256"}]]  # OFTP login hash algorithm.
    enc_algorithm: NotRequired[Literal[{"description": "Encrypt logs using high and medium encryption algorithms", "help": "Encrypt logs using high and medium encryption algorithms.", "label": "High Medium", "name": "high-medium"}, {"description": "Encrypt logs using high encryption algorithms", "help": "Encrypt logs using high encryption algorithms.", "label": "High", "name": "high"}, {"description": "Encrypt logs using all encryption algorithms", "help": "Encrypt logs using all encryption algorithms.", "label": "Low", "name": "low"}]]  # Configure the level of SSL protection for secure communicati
    ssl_min_proto_version: NotRequired[Literal[{"description": "Follow system global setting", "help": "Follow system global setting.", "label": "Default", "name": "default"}, {"description": "SSLv3", "help": "SSLv3.", "label": "Sslv3", "name": "SSLv3"}, {"description": "TLSv1", "help": "TLSv1.", "label": "Tlsv1", "name": "TLSv1"}, {"description": "TLSv1", "help": "TLSv1.1.", "label": "Tlsv1 1", "name": "TLSv1-1"}, {"description": "TLSv1", "help": "TLSv1.2.", "label": "Tlsv1 2", "name": "TLSv1-2"}, {"description": "TLSv1", "help": "TLSv1.3.", "label": "Tlsv1 3", "name": "TLSv1-3"}]]  # Minimum supported protocol version for SSL/TLS connections (
    conn_timeout: NotRequired[int]  # FortiAnalyzer connection time-out in seconds (for status and
    monitor_keepalive_period: NotRequired[int]  # Time between OFTP keepalives in seconds (for status and log 
    monitor_failure_retry_period: NotRequired[int]  # Time between FortiAnalyzer connection retries in seconds (fo
    certificate: NotRequired[str]  # Certificate used to communicate with FortiAnalyzer.
    source_ip: NotRequired[str]  # Source IPv4 or IPv6 address used to communicate with FortiAn
    upload_option: NotRequired[Literal[{"description": "Log to hard disk and then upload to FortiAnalyzer", "help": "Log to hard disk and then upload to FortiAnalyzer.", "label": "Store And Upload", "name": "store-and-upload"}, {"description": "Log directly to FortiAnalyzer in real time", "help": "Log directly to FortiAnalyzer in real time.", "label": "Realtime", "name": "realtime"}, {"description": "Log directly to FortiAnalyzer at least every 1 minute", "help": "Log directly to FortiAnalyzer at least every 1 minute.", "label": "1 Minute", "name": "1-minute"}, {"description": "Log directly to FortiAnalyzer at least every 5 minutes", "help": "Log directly to FortiAnalyzer at least every 5 minutes.", "label": "5 Minute", "name": "5-minute"}]]  # Enable/disable logging to hard disk and then uploading to Fo
    upload_interval: NotRequired[Literal[{"description": "Upload log files to FortiAnalyzer once a day", "help": "Upload log files to FortiAnalyzer once a day.", "label": "Daily", "name": "daily"}, {"description": "Upload log files to FortiAnalyzer once a week", "help": "Upload log files to FortiAnalyzer once a week.", "label": "Weekly", "name": "weekly"}, {"description": "Upload log files to FortiAnalyzer once a month", "help": "Upload log files to FortiAnalyzer once a month.", "label": "Monthly", "name": "monthly"}]]  # Frequency to upload log files to FortiAnalyzer.
    upload_day: NotRequired[str]  # Day of week (month) to upload logs.
    upload_time: NotRequired[str]  # Time to upload logs (hh:mm).
    reliable: NotRequired[Literal[{"description": "Enable reliable logging to FortiAnalyzer", "help": "Enable reliable logging to FortiAnalyzer.", "label": "Enable", "name": "enable"}, {"description": "Disable reliable logging to FortiAnalyzer", "help": "Disable reliable logging to FortiAnalyzer.", "label": "Disable", "name": "disable"}]]  # Enable/disable reliable logging to FortiAnalyzer.
    priority: NotRequired[Literal[{"description": "Set FortiAnalyzer log transmission priority to default", "help": "Set FortiAnalyzer log transmission priority to default.", "label": "Default", "name": "default"}, {"description": "Set FortiAnalyzer log transmission priority to low", "help": "Set FortiAnalyzer log transmission priority to low.", "label": "Low", "name": "low"}]]  # Set log transmission priority.
    max_log_rate: NotRequired[int]  # FortiAnalyzer maximum log rate in MBps (0 = unlimited).
    interface_select_method: NotRequired[Literal[{"description": "Set outgoing interface automatically", "help": "Set outgoing interface automatically.", "label": "Auto", "name": "auto"}, {"description": "Set outgoing interface by SD-WAN or policy routing rules", "help": "Set outgoing interface by SD-WAN or policy routing rules.", "label": "Sdwan", "name": "sdwan"}, {"description": "Set outgoing interface manually", "help": "Set outgoing interface manually.", "label": "Specify", "name": "specify"}]]  # Specify how to select outgoing interface to reach server.
    interface: str  # Specify outgoing interface to reach server.
    vrf_select: NotRequired[int]  # VRF ID used for connection to server.


class OverrideSetting:
    """
    Override FortiAnalyzer settings.
    
    Path: log/fortianalyzer2/override_setting
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
        payload_dict: OverrideSettingPayload | None = ...,
        use_management_vdom: Literal[{"description": "Enable use of management VDOM IP address as source IP for logs sent to FortiAnalyzer", "help": "Enable use of management VDOM IP address as source IP for logs sent to FortiAnalyzer.", "label": "Enable", "name": "enable"}, {"description": "Disable use of management VDOM IP address as source IP for logs sent to FortiAnalyzer", "help": "Disable use of management VDOM IP address as source IP for logs sent to FortiAnalyzer.", "label": "Disable", "name": "disable"}] | None = ...,
        status: Literal[{"description": "Enable logging to FortiAnalyzer", "help": "Enable logging to FortiAnalyzer.", "label": "Enable", "name": "enable"}, {"description": "Disable logging to FortiAnalyzer", "help": "Disable logging to FortiAnalyzer.", "label": "Disable", "name": "disable"}] | None = ...,
        ips_archive: Literal[{"description": "Enable IPS packet archive logging", "help": "Enable IPS packet archive logging.", "label": "Enable", "name": "enable"}, {"description": "Disable IPS packet archive logging", "help": "Disable IPS packet archive logging.", "label": "Disable", "name": "disable"}] | None = ...,
        server: str | None = ...,
        alt_server: str | None = ...,
        fallback_to_primary: Literal[{"description": "Enable this FortiGate unit to fallback to the primary FortiAnalyzer when it is available", "help": "Enable this FortiGate unit to fallback to the primary FortiAnalyzer when it is available.", "label": "Enable", "name": "enable"}, {"description": "Disable this FortiGate unit to fallback to the primary FortiAnalyzer when it is available", "help": "Disable this FortiGate unit to fallback to the primary FortiAnalyzer when it is available.", "label": "Disable", "name": "disable"}] | None = ...,
        certificate_verification: Literal[{"description": "Enable identity verification of FortiAnalyzer by use of certificate", "help": "Enable identity verification of FortiAnalyzer by use of certificate.", "label": "Enable", "name": "enable"}, {"description": "Disable identity verification of FortiAnalyzer by use of certificate", "help": "Disable identity verification of FortiAnalyzer by use of certificate.", "label": "Disable", "name": "disable"}] | None = ...,
        serial: list[dict[str, Any]] | None = ...,
        server_cert_ca: str | None = ...,
        preshared_key: str | None = ...,
        access_config: Literal[{"description": "Enable FortiAnalyzer access to configuration and data", "help": "Enable FortiAnalyzer access to configuration and data.", "label": "Enable", "name": "enable"}, {"description": "Disable FortiAnalyzer access to configuration and data", "help": "Disable FortiAnalyzer access to configuration and data.", "label": "Disable", "name": "disable"}] | None = ...,
        hmac_algorithm: Literal[{"description": "Use SHA256 as HMAC algorithm", "help": "Use SHA256 as HMAC algorithm.", "label": "Sha256", "name": "sha256"}] | None = ...,
        enc_algorithm: Literal[{"description": "Encrypt logs using high and medium encryption algorithms", "help": "Encrypt logs using high and medium encryption algorithms.", "label": "High Medium", "name": "high-medium"}, {"description": "Encrypt logs using high encryption algorithms", "help": "Encrypt logs using high encryption algorithms.", "label": "High", "name": "high"}, {"description": "Encrypt logs using all encryption algorithms", "help": "Encrypt logs using all encryption algorithms.", "label": "Low", "name": "low"}] | None = ...,
        ssl_min_proto_version: Literal[{"description": "Follow system global setting", "help": "Follow system global setting.", "label": "Default", "name": "default"}, {"description": "SSLv3", "help": "SSLv3.", "label": "Sslv3", "name": "SSLv3"}, {"description": "TLSv1", "help": "TLSv1.", "label": "Tlsv1", "name": "TLSv1"}, {"description": "TLSv1", "help": "TLSv1.1.", "label": "Tlsv1 1", "name": "TLSv1-1"}, {"description": "TLSv1", "help": "TLSv1.2.", "label": "Tlsv1 2", "name": "TLSv1-2"}, {"description": "TLSv1", "help": "TLSv1.3.", "label": "Tlsv1 3", "name": "TLSv1-3"}] | None = ...,
        conn_timeout: int | None = ...,
        monitor_keepalive_period: int | None = ...,
        monitor_failure_retry_period: int | None = ...,
        certificate: str | None = ...,
        source_ip: str | None = ...,
        upload_option: Literal[{"description": "Log to hard disk and then upload to FortiAnalyzer", "help": "Log to hard disk and then upload to FortiAnalyzer.", "label": "Store And Upload", "name": "store-and-upload"}, {"description": "Log directly to FortiAnalyzer in real time", "help": "Log directly to FortiAnalyzer in real time.", "label": "Realtime", "name": "realtime"}, {"description": "Log directly to FortiAnalyzer at least every 1 minute", "help": "Log directly to FortiAnalyzer at least every 1 minute.", "label": "1 Minute", "name": "1-minute"}, {"description": "Log directly to FortiAnalyzer at least every 5 minutes", "help": "Log directly to FortiAnalyzer at least every 5 minutes.", "label": "5 Minute", "name": "5-minute"}] | None = ...,
        upload_interval: Literal[{"description": "Upload log files to FortiAnalyzer once a day", "help": "Upload log files to FortiAnalyzer once a day.", "label": "Daily", "name": "daily"}, {"description": "Upload log files to FortiAnalyzer once a week", "help": "Upload log files to FortiAnalyzer once a week.", "label": "Weekly", "name": "weekly"}, {"description": "Upload log files to FortiAnalyzer once a month", "help": "Upload log files to FortiAnalyzer once a month.", "label": "Monthly", "name": "monthly"}] | None = ...,
        upload_day: str | None = ...,
        upload_time: str | None = ...,
        reliable: Literal[{"description": "Enable reliable logging to FortiAnalyzer", "help": "Enable reliable logging to FortiAnalyzer.", "label": "Enable", "name": "enable"}, {"description": "Disable reliable logging to FortiAnalyzer", "help": "Disable reliable logging to FortiAnalyzer.", "label": "Disable", "name": "disable"}] | None = ...,
        priority: Literal[{"description": "Set FortiAnalyzer log transmission priority to default", "help": "Set FortiAnalyzer log transmission priority to default.", "label": "Default", "name": "default"}, {"description": "Set FortiAnalyzer log transmission priority to low", "help": "Set FortiAnalyzer log transmission priority to low.", "label": "Low", "name": "low"}] | None = ...,
        max_log_rate: int | None = ...,
        interface_select_method: Literal[{"description": "Set outgoing interface automatically", "help": "Set outgoing interface automatically.", "label": "Auto", "name": "auto"}, {"description": "Set outgoing interface by SD-WAN or policy routing rules", "help": "Set outgoing interface by SD-WAN or policy routing rules.", "label": "Sdwan", "name": "sdwan"}, {"description": "Set outgoing interface manually", "help": "Set outgoing interface manually.", "label": "Specify", "name": "specify"}] | None = ...,
        interface: str | None = ...,
        vrf_select: int | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: OverrideSettingPayload | None = ...,
        use_management_vdom: Literal[{"description": "Enable use of management VDOM IP address as source IP for logs sent to FortiAnalyzer", "help": "Enable use of management VDOM IP address as source IP for logs sent to FortiAnalyzer.", "label": "Enable", "name": "enable"}, {"description": "Disable use of management VDOM IP address as source IP for logs sent to FortiAnalyzer", "help": "Disable use of management VDOM IP address as source IP for logs sent to FortiAnalyzer.", "label": "Disable", "name": "disable"}] | None = ...,
        status: Literal[{"description": "Enable logging to FortiAnalyzer", "help": "Enable logging to FortiAnalyzer.", "label": "Enable", "name": "enable"}, {"description": "Disable logging to FortiAnalyzer", "help": "Disable logging to FortiAnalyzer.", "label": "Disable", "name": "disable"}] | None = ...,
        ips_archive: Literal[{"description": "Enable IPS packet archive logging", "help": "Enable IPS packet archive logging.", "label": "Enable", "name": "enable"}, {"description": "Disable IPS packet archive logging", "help": "Disable IPS packet archive logging.", "label": "Disable", "name": "disable"}] | None = ...,
        server: str | None = ...,
        alt_server: str | None = ...,
        fallback_to_primary: Literal[{"description": "Enable this FortiGate unit to fallback to the primary FortiAnalyzer when it is available", "help": "Enable this FortiGate unit to fallback to the primary FortiAnalyzer when it is available.", "label": "Enable", "name": "enable"}, {"description": "Disable this FortiGate unit to fallback to the primary FortiAnalyzer when it is available", "help": "Disable this FortiGate unit to fallback to the primary FortiAnalyzer when it is available.", "label": "Disable", "name": "disable"}] | None = ...,
        certificate_verification: Literal[{"description": "Enable identity verification of FortiAnalyzer by use of certificate", "help": "Enable identity verification of FortiAnalyzer by use of certificate.", "label": "Enable", "name": "enable"}, {"description": "Disable identity verification of FortiAnalyzer by use of certificate", "help": "Disable identity verification of FortiAnalyzer by use of certificate.", "label": "Disable", "name": "disable"}] | None = ...,
        serial: list[dict[str, Any]] | None = ...,
        server_cert_ca: str | None = ...,
        preshared_key: str | None = ...,
        access_config: Literal[{"description": "Enable FortiAnalyzer access to configuration and data", "help": "Enable FortiAnalyzer access to configuration and data.", "label": "Enable", "name": "enable"}, {"description": "Disable FortiAnalyzer access to configuration and data", "help": "Disable FortiAnalyzer access to configuration and data.", "label": "Disable", "name": "disable"}] | None = ...,
        hmac_algorithm: Literal[{"description": "Use SHA256 as HMAC algorithm", "help": "Use SHA256 as HMAC algorithm.", "label": "Sha256", "name": "sha256"}] | None = ...,
        enc_algorithm: Literal[{"description": "Encrypt logs using high and medium encryption algorithms", "help": "Encrypt logs using high and medium encryption algorithms.", "label": "High Medium", "name": "high-medium"}, {"description": "Encrypt logs using high encryption algorithms", "help": "Encrypt logs using high encryption algorithms.", "label": "High", "name": "high"}, {"description": "Encrypt logs using all encryption algorithms", "help": "Encrypt logs using all encryption algorithms.", "label": "Low", "name": "low"}] | None = ...,
        ssl_min_proto_version: Literal[{"description": "Follow system global setting", "help": "Follow system global setting.", "label": "Default", "name": "default"}, {"description": "SSLv3", "help": "SSLv3.", "label": "Sslv3", "name": "SSLv3"}, {"description": "TLSv1", "help": "TLSv1.", "label": "Tlsv1", "name": "TLSv1"}, {"description": "TLSv1", "help": "TLSv1.1.", "label": "Tlsv1 1", "name": "TLSv1-1"}, {"description": "TLSv1", "help": "TLSv1.2.", "label": "Tlsv1 2", "name": "TLSv1-2"}, {"description": "TLSv1", "help": "TLSv1.3.", "label": "Tlsv1 3", "name": "TLSv1-3"}] | None = ...,
        conn_timeout: int | None = ...,
        monitor_keepalive_period: int | None = ...,
        monitor_failure_retry_period: int | None = ...,
        certificate: str | None = ...,
        source_ip: str | None = ...,
        upload_option: Literal[{"description": "Log to hard disk and then upload to FortiAnalyzer", "help": "Log to hard disk and then upload to FortiAnalyzer.", "label": "Store And Upload", "name": "store-and-upload"}, {"description": "Log directly to FortiAnalyzer in real time", "help": "Log directly to FortiAnalyzer in real time.", "label": "Realtime", "name": "realtime"}, {"description": "Log directly to FortiAnalyzer at least every 1 minute", "help": "Log directly to FortiAnalyzer at least every 1 minute.", "label": "1 Minute", "name": "1-minute"}, {"description": "Log directly to FortiAnalyzer at least every 5 minutes", "help": "Log directly to FortiAnalyzer at least every 5 minutes.", "label": "5 Minute", "name": "5-minute"}] | None = ...,
        upload_interval: Literal[{"description": "Upload log files to FortiAnalyzer once a day", "help": "Upload log files to FortiAnalyzer once a day.", "label": "Daily", "name": "daily"}, {"description": "Upload log files to FortiAnalyzer once a week", "help": "Upload log files to FortiAnalyzer once a week.", "label": "Weekly", "name": "weekly"}, {"description": "Upload log files to FortiAnalyzer once a month", "help": "Upload log files to FortiAnalyzer once a month.", "label": "Monthly", "name": "monthly"}] | None = ...,
        upload_day: str | None = ...,
        upload_time: str | None = ...,
        reliable: Literal[{"description": "Enable reliable logging to FortiAnalyzer", "help": "Enable reliable logging to FortiAnalyzer.", "label": "Enable", "name": "enable"}, {"description": "Disable reliable logging to FortiAnalyzer", "help": "Disable reliable logging to FortiAnalyzer.", "label": "Disable", "name": "disable"}] | None = ...,
        priority: Literal[{"description": "Set FortiAnalyzer log transmission priority to default", "help": "Set FortiAnalyzer log transmission priority to default.", "label": "Default", "name": "default"}, {"description": "Set FortiAnalyzer log transmission priority to low", "help": "Set FortiAnalyzer log transmission priority to low.", "label": "Low", "name": "low"}] | None = ...,
        max_log_rate: int | None = ...,
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
        payload_dict: OverrideSettingPayload | None = ...,
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
    "OverrideSetting",
    "OverrideSettingPayload",
]