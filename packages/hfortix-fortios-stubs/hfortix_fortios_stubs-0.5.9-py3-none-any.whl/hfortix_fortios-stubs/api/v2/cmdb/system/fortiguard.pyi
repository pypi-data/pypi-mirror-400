from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class FortiguardPayload(TypedDict, total=False):
    """
    Type hints for system/fortiguard payload fields.
    
    Configure FortiGuard services.
    
    **Related Resources:**

    Dependencies (resources this endpoint references):
        - :class:`~.system.interface.InterfaceEndpoint` (via: interface)
        - :class:`~.system.vdom.VdomEndpoint` (via: vdom)

    **Usage:**
        payload: FortiguardPayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    fortiguard_anycast: NotRequired[Literal[{"description": "Enable use of FortiGuard\u0027s Anycast network", "help": "Enable use of FortiGuard\u0027s Anycast network.", "label": "Enable", "name": "enable"}, {"description": "Disable use of FortiGuard\u0027s Anycast network", "help": "Disable use of FortiGuard\u0027s Anycast network.", "label": "Disable", "name": "disable"}]]  # Enable/disable use of FortiGuard's Anycast network.
    fortiguard_anycast_source: NotRequired[Literal[{"description": "Use Fortinet\u0027s servers to provide FortiGuard services in FortiGuard\u0027s anycast network", "help": "Use Fortinet\u0027s servers to provide FortiGuard services in FortiGuard\u0027s anycast network.", "label": "Fortinet", "name": "fortinet"}, {"description": "Use Fortinet\u0027s AWS servers to provide FortiGuard services in FortiGuard\u0027s anycast network", "help": "Use Fortinet\u0027s AWS servers to provide FortiGuard services in FortiGuard\u0027s anycast network.", "label": "Aws", "name": "aws"}, {"description": "Use Fortinet\u0027s internal test servers to provide FortiGuard services in FortiGuard\u0027s anycast network", "help": "Use Fortinet\u0027s internal test servers to provide FortiGuard services in FortiGuard\u0027s anycast network.", "label": "Debug", "name": "debug"}]]  # Configure which of Fortinet's servers to provide FortiGuard 
    protocol: NotRequired[Literal[{"description": "UDP for server communication (for use by FortiGuard or FortiManager)", "help": "UDP for server communication (for use by FortiGuard or FortiManager).", "label": "Udp", "name": "udp"}, {"description": "HTTP for server communication (for use only by FortiManager)", "help": "HTTP for server communication (for use only by FortiManager).", "label": "Http", "name": "http"}, {"description": "HTTPS for server communication (for use by FortiGuard or FortiManager)", "help": "HTTPS for server communication (for use by FortiGuard or FortiManager).", "label": "Https", "name": "https"}]]  # Protocol used to communicate with the FortiGuard servers.
    port: NotRequired[Literal[{"description": "port 8888 for server communication", "help": "port 8888 for server communication.", "label": "8888", "name": "8888"}, {"description": "port 53 for server communication", "help": "port 53 for server communication.", "label": "53", "name": "53"}, {"description": "port 80 for server communication", "help": "port 80 for server communication.", "label": "80", "name": "80"}, {"description": "port 443 for server communication", "help": "port 443 for server communication.", "label": "443", "name": "443"}]]  # Port used to communicate with the FortiGuard servers.
    load_balance_servers: NotRequired[int]  # Number of servers to alternate between as first FortiGuard o
    auto_join_forticloud: NotRequired[Literal[{"description": "Enable automatic connection and login to FortiCloud", "help": "Enable automatic connection and login to FortiCloud.", "label": "Enable", "name": "enable"}, {"description": "Disable automatic connection and login to FortiCloud", "help": "Disable automatic connection and login to FortiCloud.", "label": "Disable", "name": "disable"}]]  # Automatically connect to and login to FortiCloud.
    update_server_location: NotRequired[Literal[{"description": "FortiGuard servers chosen based on closest proximity to FortiGate unit", "help": "FortiGuard servers chosen based on closest proximity to FortiGate unit.", "label": "Automatic", "name": "automatic"}, {"description": "FortiGuard servers in United States", "help": "FortiGuard servers in United States.", "label": "Usa", "name": "usa"}, {"description": "FortiGuard servers in the European Union", "help": "FortiGuard servers in the European Union.", "label": "Eu", "name": "eu"}]]  # Location from which to receive FortiGuard updates.
    sandbox_region: NotRequired[str]  # FortiCloud Sandbox region.
    sandbox_inline_scan: NotRequired[Literal[{"help": "Enable FortiCloud Sandbox inline scan.", "label": "Enable", "name": "enable"}, {"help": "Disable FortiCloud Sandbox inline scan.", "label": "Disable", "name": "disable"}]]  # Enable/disable FortiCloud Sandbox inline-scan.
    update_ffdb: NotRequired[Literal[{"description": "Enable Internet Service Database update", "help": "Enable Internet Service Database update.", "label": "Enable", "name": "enable"}, {"description": "Disable Internet Service Database update", "help": "Disable Internet Service Database update.", "label": "Disable", "name": "disable"}]]  # Enable/disable Internet Service Database update.
    update_uwdb: NotRequired[Literal[{"description": "Enable allowlist update", "help": "Enable allowlist update.", "label": "Enable", "name": "enable"}, {"description": "Disable allowlist update", "help": "Disable allowlist update.", "label": "Disable", "name": "disable"}]]  # Enable/disable allowlist update.
    update_dldb: NotRequired[Literal[{"description": "Enable DLP signature update", "help": "Enable DLP signature update.", "label": "Enable", "name": "enable"}, {"description": "Disable DLP signature update", "help": "Disable DLP signature update.", "label": "Disable", "name": "disable"}]]  # Enable/disable DLP signature update.
    update_extdb: NotRequired[Literal[{"description": "Enable external resource update", "help": "Enable external resource update.", "label": "Enable", "name": "enable"}, {"description": "Disable external resource update", "help": "Disable external resource update.", "label": "Disable", "name": "disable"}]]  # Enable/disable external resource update.
    update_build_proxy: NotRequired[Literal[{"description": "Enable proxy dictionary rebuild", "help": "Enable proxy dictionary rebuild.", "label": "Enable", "name": "enable"}, {"description": "Disable proxy dictionary rebuild", "help": "Disable proxy dictionary rebuild.", "label": "Disable", "name": "disable"}]]  # Enable/disable proxy dictionary rebuild.
    persistent_connection: NotRequired[Literal[{"description": "Enable persistent connection to receive update notification from FortiGuard", "help": "Enable persistent connection to receive update notification from FortiGuard.", "label": "Enable", "name": "enable"}, {"description": "Disable persistent connection to receive update notification from FortiGuard", "help": "Disable persistent connection to receive update notification from FortiGuard.", "label": "Disable", "name": "disable"}]]  # Enable/disable use of persistent connection to receive updat
    vdom: NotRequired[str]  # FortiGuard Service virtual domain name.
    auto_firmware_upgrade: NotRequired[Literal[{"description": "Enable automatic patch-level firmware upgrade to latest version from FortiGuard", "help": "Enable automatic patch-level firmware upgrade to latest version from FortiGuard.", "label": "Enable", "name": "enable"}, {"description": "Disable automatic patch-level firmware upgrade to latest version from FortiGuard", "help": "Disable automatic patch-level firmware upgrade to latest version from FortiGuard.", "label": "Disable", "name": "disable"}]]  # Enable/disable automatic patch-level firmware upgrade from F
    auto_firmware_upgrade_day: NotRequired[Literal[{"description": "Sunday", "help": "Sunday.", "label": "Sunday", "name": "sunday"}, {"description": "Monday", "help": "Monday.", "label": "Monday", "name": "monday"}, {"description": "Tuesday", "help": "Tuesday.", "label": "Tuesday", "name": "tuesday"}, {"description": "Wednesday", "help": "Wednesday.", "label": "Wednesday", "name": "wednesday"}, {"description": "Thursday", "help": "Thursday.", "label": "Thursday", "name": "thursday"}, {"description": "Friday", "help": "Friday.", "label": "Friday", "name": "friday"}, {"description": "Saturday", "help": "Saturday.", "label": "Saturday", "name": "saturday"}]]  # Allowed day(s) of the week to install an automatic patch-lev
    auto_firmware_upgrade_delay: NotRequired[int]  # Delay of day(s) before installing an automatic patch-level f
    auto_firmware_upgrade_start_hour: NotRequired[int]  # Start time in the designated time window for automatic patch
    auto_firmware_upgrade_end_hour: NotRequired[int]  # End time in the designated time window for automatic patch-l
    FDS_license_expiring_days: NotRequired[int]  # Threshold for number of days before FortiGuard license expir
    subscribe_update_notification: NotRequired[Literal[{"description": "Enable subscription to receive update notification from FortiGuard", "help": "Enable subscription to receive update notification from FortiGuard.", "label": "Enable", "name": "enable"}, {"description": "Disable subscription to receive update notification from FortiGuard", "help": "Disable subscription to receive update notification from FortiGuard.", "label": "Disable", "name": "disable"}]]  # Enable/disable subscription to receive update notification f
    antispam_force_off: NotRequired[Literal[{"description": "Turn off the FortiGuard antispam service", "help": "Turn off the FortiGuard antispam service.", "label": "Enable", "name": "enable"}, {"description": "Allow the FortiGuard antispam service", "help": "Allow the FortiGuard antispam service.", "label": "Disable", "name": "disable"}]]  # Enable/disable turning off the FortiGuard antispam service.
    antispam_cache: NotRequired[Literal[{"description": "Enable FortiGuard antispam request caching", "help": "Enable FortiGuard antispam request caching.", "label": "Enable", "name": "enable"}, {"description": "Disable FortiGuard antispam request caching", "help": "Disable FortiGuard antispam request caching.", "label": "Disable", "name": "disable"}]]  # Enable/disable FortiGuard antispam request caching. Uses a s
    antispam_cache_ttl: NotRequired[int]  # Time-to-live for antispam cache entries in seconds (300 - 86
    antispam_cache_mpermille: NotRequired[int]  # Maximum permille of FortiGate memory the antispam cache is a
    antispam_license: NotRequired[int]  # Interval of time between license checks for the FortiGuard a
    antispam_expiration: NotRequired[int]  # Expiration date of the FortiGuard antispam contract.
    antispam_timeout: int  # Antispam query time out (1 - 30 sec, default = 7).
    outbreak_prevention_force_off: NotRequired[Literal[{"description": "Turn off FortiGuard antivirus service", "help": "Turn off FortiGuard antivirus service.", "label": "Enable", "name": "enable"}, {"description": "Allow the FortiGuard antivirus service", "help": "Allow the FortiGuard antivirus service.", "label": "Disable", "name": "disable"}]]  # Turn off FortiGuard Virus Outbreak Prevention service.
    outbreak_prevention_cache: NotRequired[Literal[{"description": "Enable FortiGuard antivirus caching", "help": "Enable FortiGuard antivirus caching.", "label": "Enable", "name": "enable"}, {"description": "Disable FortiGuard antivirus caching", "help": "Disable FortiGuard antivirus caching.", "label": "Disable", "name": "disable"}]]  # Enable/disable FortiGuard Virus Outbreak Prevention cache.
    outbreak_prevention_cache_ttl: NotRequired[int]  # Time-to-live for FortiGuard Virus Outbreak Prevention cache 
    outbreak_prevention_cache_mpermille: NotRequired[int]  # Maximum permille of memory FortiGuard Virus Outbreak Prevent
    outbreak_prevention_license: NotRequired[int]  # Interval of time between license checks for FortiGuard Virus
    outbreak_prevention_expiration: NotRequired[int]  # Expiration date of FortiGuard Virus Outbreak Prevention cont
    outbreak_prevention_timeout: int  # FortiGuard Virus Outbreak Prevention time out (1 - 30 sec, d
    webfilter_force_off: NotRequired[Literal[{"description": "Turn off the FortiGuard web filtering service", "help": "Turn off the FortiGuard web filtering service.", "label": "Enable", "name": "enable"}, {"description": "Allow the FortiGuard web filtering service to operate", "help": "Allow the FortiGuard web filtering service to operate.", "label": "Disable", "name": "disable"}]]  # Enable/disable turning off the FortiGuard web filtering serv
    webfilter_cache: NotRequired[Literal[{"description": "Enable FortiGuard web filter caching", "help": "Enable FortiGuard web filter caching.", "label": "Enable", "name": "enable"}, {"description": "Disable FortiGuard web filter caching", "help": "Disable FortiGuard web filter caching.", "label": "Disable", "name": "disable"}]]  # Enable/disable FortiGuard web filter caching.
    webfilter_cache_ttl: NotRequired[int]  # Time-to-live for web filter cache entries in seconds (300 - 
    webfilter_license: NotRequired[int]  # Interval of time between license checks for the FortiGuard w
    webfilter_expiration: NotRequired[int]  # Expiration date of the FortiGuard web filter contract.
    webfilter_timeout: int  # Web filter query time out (1 - 30 sec, default = 15).
    sdns_server_ip: NotRequired[list[dict[str, Any]]]  # IP address of the FortiGuard DNS rating server.
    sdns_server_port: NotRequired[int]  # Port to connect to on the FortiGuard DNS rating server.
    anycast_sdns_server_ip: NotRequired[str]  # IP address of the FortiGuard anycast DNS rating server.
    anycast_sdns_server_port: NotRequired[int]  # Port to connect to on the FortiGuard anycast DNS rating serv
    sdns_options: NotRequired[Literal[{"description": "Include DNS question section in the FortiGuard DNS setup message", "help": "Include DNS question section in the FortiGuard DNS setup message.", "label": "Include Question Section", "name": "include-question-section"}]]  # Customization options for the FortiGuard DNS service.
    source_ip: NotRequired[str]  # Source IPv4 address used to communicate with FortiGuard.
    source_ip6: NotRequired[str]  # Source IPv6 address used to communicate with FortiGuard.
    proxy_server_ip: NotRequired[str]  # Hostname or IPv4 address of the proxy server.
    proxy_server_port: NotRequired[int]  # Port used to communicate with the proxy server.
    proxy_username: NotRequired[str]  # Proxy user name.
    proxy_password: NotRequired[str]  # Proxy user password.
    ddns_server_ip: NotRequired[str]  # IP address of the FortiDDNS server.
    ddns_server_ip6: NotRequired[str]  # IPv6 address of the FortiDDNS server.
    ddns_server_port: NotRequired[int]  # Port used to communicate with FortiDDNS servers.
    interface_select_method: NotRequired[Literal[{"description": "Set outgoing interface automatically", "help": "Set outgoing interface automatically.", "label": "Auto", "name": "auto"}, {"description": "Set outgoing interface by SD-WAN or policy routing rules", "help": "Set outgoing interface by SD-WAN or policy routing rules.", "label": "Sdwan", "name": "sdwan"}, {"description": "Set outgoing interface manually", "help": "Set outgoing interface manually.", "label": "Specify", "name": "specify"}]]  # Specify how to select outgoing interface to reach server.
    interface: str  # Specify outgoing interface to reach server.
    vrf_select: NotRequired[int]  # VRF ID used for connection to server.


class Fortiguard:
    """
    Configure FortiGuard services.
    
    Path: system/fortiguard
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
        payload_dict: FortiguardPayload | None = ...,
        fortiguard_anycast: Literal[{"description": "Enable use of FortiGuard\u0027s Anycast network", "help": "Enable use of FortiGuard\u0027s Anycast network.", "label": "Enable", "name": "enable"}, {"description": "Disable use of FortiGuard\u0027s Anycast network", "help": "Disable use of FortiGuard\u0027s Anycast network.", "label": "Disable", "name": "disable"}] | None = ...,
        fortiguard_anycast_source: Literal[{"description": "Use Fortinet\u0027s servers to provide FortiGuard services in FortiGuard\u0027s anycast network", "help": "Use Fortinet\u0027s servers to provide FortiGuard services in FortiGuard\u0027s anycast network.", "label": "Fortinet", "name": "fortinet"}, {"description": "Use Fortinet\u0027s AWS servers to provide FortiGuard services in FortiGuard\u0027s anycast network", "help": "Use Fortinet\u0027s AWS servers to provide FortiGuard services in FortiGuard\u0027s anycast network.", "label": "Aws", "name": "aws"}, {"description": "Use Fortinet\u0027s internal test servers to provide FortiGuard services in FortiGuard\u0027s anycast network", "help": "Use Fortinet\u0027s internal test servers to provide FortiGuard services in FortiGuard\u0027s anycast network.", "label": "Debug", "name": "debug"}] | None = ...,
        protocol: Literal[{"description": "UDP for server communication (for use by FortiGuard or FortiManager)", "help": "UDP for server communication (for use by FortiGuard or FortiManager).", "label": "Udp", "name": "udp"}, {"description": "HTTP for server communication (for use only by FortiManager)", "help": "HTTP for server communication (for use only by FortiManager).", "label": "Http", "name": "http"}, {"description": "HTTPS for server communication (for use by FortiGuard or FortiManager)", "help": "HTTPS for server communication (for use by FortiGuard or FortiManager).", "label": "Https", "name": "https"}] | None = ...,
        port: Literal[{"description": "port 8888 for server communication", "help": "port 8888 for server communication.", "label": "8888", "name": "8888"}, {"description": "port 53 for server communication", "help": "port 53 for server communication.", "label": "53", "name": "53"}, {"description": "port 80 for server communication", "help": "port 80 for server communication.", "label": "80", "name": "80"}, {"description": "port 443 for server communication", "help": "port 443 for server communication.", "label": "443", "name": "443"}] | None = ...,
        load_balance_servers: int | None = ...,
        auto_join_forticloud: Literal[{"description": "Enable automatic connection and login to FortiCloud", "help": "Enable automatic connection and login to FortiCloud.", "label": "Enable", "name": "enable"}, {"description": "Disable automatic connection and login to FortiCloud", "help": "Disable automatic connection and login to FortiCloud.", "label": "Disable", "name": "disable"}] | None = ...,
        update_server_location: Literal[{"description": "FortiGuard servers chosen based on closest proximity to FortiGate unit", "help": "FortiGuard servers chosen based on closest proximity to FortiGate unit.", "label": "Automatic", "name": "automatic"}, {"description": "FortiGuard servers in United States", "help": "FortiGuard servers in United States.", "label": "Usa", "name": "usa"}, {"description": "FortiGuard servers in the European Union", "help": "FortiGuard servers in the European Union.", "label": "Eu", "name": "eu"}] | None = ...,
        sandbox_region: str | None = ...,
        sandbox_inline_scan: Literal[{"help": "Enable FortiCloud Sandbox inline scan.", "label": "Enable", "name": "enable"}, {"help": "Disable FortiCloud Sandbox inline scan.", "label": "Disable", "name": "disable"}] | None = ...,
        update_ffdb: Literal[{"description": "Enable Internet Service Database update", "help": "Enable Internet Service Database update.", "label": "Enable", "name": "enable"}, {"description": "Disable Internet Service Database update", "help": "Disable Internet Service Database update.", "label": "Disable", "name": "disable"}] | None = ...,
        update_uwdb: Literal[{"description": "Enable allowlist update", "help": "Enable allowlist update.", "label": "Enable", "name": "enable"}, {"description": "Disable allowlist update", "help": "Disable allowlist update.", "label": "Disable", "name": "disable"}] | None = ...,
        update_dldb: Literal[{"description": "Enable DLP signature update", "help": "Enable DLP signature update.", "label": "Enable", "name": "enable"}, {"description": "Disable DLP signature update", "help": "Disable DLP signature update.", "label": "Disable", "name": "disable"}] | None = ...,
        update_extdb: Literal[{"description": "Enable external resource update", "help": "Enable external resource update.", "label": "Enable", "name": "enable"}, {"description": "Disable external resource update", "help": "Disable external resource update.", "label": "Disable", "name": "disable"}] | None = ...,
        update_build_proxy: Literal[{"description": "Enable proxy dictionary rebuild", "help": "Enable proxy dictionary rebuild.", "label": "Enable", "name": "enable"}, {"description": "Disable proxy dictionary rebuild", "help": "Disable proxy dictionary rebuild.", "label": "Disable", "name": "disable"}] | None = ...,
        persistent_connection: Literal[{"description": "Enable persistent connection to receive update notification from FortiGuard", "help": "Enable persistent connection to receive update notification from FortiGuard.", "label": "Enable", "name": "enable"}, {"description": "Disable persistent connection to receive update notification from FortiGuard", "help": "Disable persistent connection to receive update notification from FortiGuard.", "label": "Disable", "name": "disable"}] | None = ...,
        auto_firmware_upgrade: Literal[{"description": "Enable automatic patch-level firmware upgrade to latest version from FortiGuard", "help": "Enable automatic patch-level firmware upgrade to latest version from FortiGuard.", "label": "Enable", "name": "enable"}, {"description": "Disable automatic patch-level firmware upgrade to latest version from FortiGuard", "help": "Disable automatic patch-level firmware upgrade to latest version from FortiGuard.", "label": "Disable", "name": "disable"}] | None = ...,
        auto_firmware_upgrade_day: Literal[{"description": "Sunday", "help": "Sunday.", "label": "Sunday", "name": "sunday"}, {"description": "Monday", "help": "Monday.", "label": "Monday", "name": "monday"}, {"description": "Tuesday", "help": "Tuesday.", "label": "Tuesday", "name": "tuesday"}, {"description": "Wednesday", "help": "Wednesday.", "label": "Wednesday", "name": "wednesday"}, {"description": "Thursday", "help": "Thursday.", "label": "Thursday", "name": "thursday"}, {"description": "Friday", "help": "Friday.", "label": "Friday", "name": "friday"}, {"description": "Saturday", "help": "Saturday.", "label": "Saturday", "name": "saturday"}] | None = ...,
        auto_firmware_upgrade_delay: int | None = ...,
        auto_firmware_upgrade_start_hour: int | None = ...,
        auto_firmware_upgrade_end_hour: int | None = ...,
        FDS_license_expiring_days: int | None = ...,
        subscribe_update_notification: Literal[{"description": "Enable subscription to receive update notification from FortiGuard", "help": "Enable subscription to receive update notification from FortiGuard.", "label": "Enable", "name": "enable"}, {"description": "Disable subscription to receive update notification from FortiGuard", "help": "Disable subscription to receive update notification from FortiGuard.", "label": "Disable", "name": "disable"}] | None = ...,
        antispam_force_off: Literal[{"description": "Turn off the FortiGuard antispam service", "help": "Turn off the FortiGuard antispam service.", "label": "Enable", "name": "enable"}, {"description": "Allow the FortiGuard antispam service", "help": "Allow the FortiGuard antispam service.", "label": "Disable", "name": "disable"}] | None = ...,
        antispam_cache: Literal[{"description": "Enable FortiGuard antispam request caching", "help": "Enable FortiGuard antispam request caching.", "label": "Enable", "name": "enable"}, {"description": "Disable FortiGuard antispam request caching", "help": "Disable FortiGuard antispam request caching.", "label": "Disable", "name": "disable"}] | None = ...,
        antispam_cache_ttl: int | None = ...,
        antispam_cache_mpermille: int | None = ...,
        antispam_license: int | None = ...,
        antispam_expiration: int | None = ...,
        antispam_timeout: int | None = ...,
        outbreak_prevention_force_off: Literal[{"description": "Turn off FortiGuard antivirus service", "help": "Turn off FortiGuard antivirus service.", "label": "Enable", "name": "enable"}, {"description": "Allow the FortiGuard antivirus service", "help": "Allow the FortiGuard antivirus service.", "label": "Disable", "name": "disable"}] | None = ...,
        outbreak_prevention_cache: Literal[{"description": "Enable FortiGuard antivirus caching", "help": "Enable FortiGuard antivirus caching.", "label": "Enable", "name": "enable"}, {"description": "Disable FortiGuard antivirus caching", "help": "Disable FortiGuard antivirus caching.", "label": "Disable", "name": "disable"}] | None = ...,
        outbreak_prevention_cache_ttl: int | None = ...,
        outbreak_prevention_cache_mpermille: int | None = ...,
        outbreak_prevention_license: int | None = ...,
        outbreak_prevention_expiration: int | None = ...,
        outbreak_prevention_timeout: int | None = ...,
        webfilter_force_off: Literal[{"description": "Turn off the FortiGuard web filtering service", "help": "Turn off the FortiGuard web filtering service.", "label": "Enable", "name": "enable"}, {"description": "Allow the FortiGuard web filtering service to operate", "help": "Allow the FortiGuard web filtering service to operate.", "label": "Disable", "name": "disable"}] | None = ...,
        webfilter_cache: Literal[{"description": "Enable FortiGuard web filter caching", "help": "Enable FortiGuard web filter caching.", "label": "Enable", "name": "enable"}, {"description": "Disable FortiGuard web filter caching", "help": "Disable FortiGuard web filter caching.", "label": "Disable", "name": "disable"}] | None = ...,
        webfilter_cache_ttl: int | None = ...,
        webfilter_license: int | None = ...,
        webfilter_expiration: int | None = ...,
        webfilter_timeout: int | None = ...,
        sdns_server_ip: list[dict[str, Any]] | None = ...,
        sdns_server_port: int | None = ...,
        anycast_sdns_server_ip: str | None = ...,
        anycast_sdns_server_port: int | None = ...,
        sdns_options: Literal[{"description": "Include DNS question section in the FortiGuard DNS setup message", "help": "Include DNS question section in the FortiGuard DNS setup message.", "label": "Include Question Section", "name": "include-question-section"}] | None = ...,
        source_ip: str | None = ...,
        source_ip6: str | None = ...,
        proxy_server_ip: str | None = ...,
        proxy_server_port: int | None = ...,
        proxy_username: str | None = ...,
        proxy_password: str | None = ...,
        ddns_server_ip: str | None = ...,
        ddns_server_ip6: str | None = ...,
        ddns_server_port: int | None = ...,
        interface_select_method: Literal[{"description": "Set outgoing interface automatically", "help": "Set outgoing interface automatically.", "label": "Auto", "name": "auto"}, {"description": "Set outgoing interface by SD-WAN or policy routing rules", "help": "Set outgoing interface by SD-WAN or policy routing rules.", "label": "Sdwan", "name": "sdwan"}, {"description": "Set outgoing interface manually", "help": "Set outgoing interface manually.", "label": "Specify", "name": "specify"}] | None = ...,
        interface: str | None = ...,
        vrf_select: int | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: FortiguardPayload | None = ...,
        fortiguard_anycast: Literal[{"description": "Enable use of FortiGuard\u0027s Anycast network", "help": "Enable use of FortiGuard\u0027s Anycast network.", "label": "Enable", "name": "enable"}, {"description": "Disable use of FortiGuard\u0027s Anycast network", "help": "Disable use of FortiGuard\u0027s Anycast network.", "label": "Disable", "name": "disable"}] | None = ...,
        fortiguard_anycast_source: Literal[{"description": "Use Fortinet\u0027s servers to provide FortiGuard services in FortiGuard\u0027s anycast network", "help": "Use Fortinet\u0027s servers to provide FortiGuard services in FortiGuard\u0027s anycast network.", "label": "Fortinet", "name": "fortinet"}, {"description": "Use Fortinet\u0027s AWS servers to provide FortiGuard services in FortiGuard\u0027s anycast network", "help": "Use Fortinet\u0027s AWS servers to provide FortiGuard services in FortiGuard\u0027s anycast network.", "label": "Aws", "name": "aws"}, {"description": "Use Fortinet\u0027s internal test servers to provide FortiGuard services in FortiGuard\u0027s anycast network", "help": "Use Fortinet\u0027s internal test servers to provide FortiGuard services in FortiGuard\u0027s anycast network.", "label": "Debug", "name": "debug"}] | None = ...,
        protocol: Literal[{"description": "UDP for server communication (for use by FortiGuard or FortiManager)", "help": "UDP for server communication (for use by FortiGuard or FortiManager).", "label": "Udp", "name": "udp"}, {"description": "HTTP for server communication (for use only by FortiManager)", "help": "HTTP for server communication (for use only by FortiManager).", "label": "Http", "name": "http"}, {"description": "HTTPS for server communication (for use by FortiGuard or FortiManager)", "help": "HTTPS for server communication (for use by FortiGuard or FortiManager).", "label": "Https", "name": "https"}] | None = ...,
        port: Literal[{"description": "port 8888 for server communication", "help": "port 8888 for server communication.", "label": "8888", "name": "8888"}, {"description": "port 53 for server communication", "help": "port 53 for server communication.", "label": "53", "name": "53"}, {"description": "port 80 for server communication", "help": "port 80 for server communication.", "label": "80", "name": "80"}, {"description": "port 443 for server communication", "help": "port 443 for server communication.", "label": "443", "name": "443"}] | None = ...,
        load_balance_servers: int | None = ...,
        auto_join_forticloud: Literal[{"description": "Enable automatic connection and login to FortiCloud", "help": "Enable automatic connection and login to FortiCloud.", "label": "Enable", "name": "enable"}, {"description": "Disable automatic connection and login to FortiCloud", "help": "Disable automatic connection and login to FortiCloud.", "label": "Disable", "name": "disable"}] | None = ...,
        update_server_location: Literal[{"description": "FortiGuard servers chosen based on closest proximity to FortiGate unit", "help": "FortiGuard servers chosen based on closest proximity to FortiGate unit.", "label": "Automatic", "name": "automatic"}, {"description": "FortiGuard servers in United States", "help": "FortiGuard servers in United States.", "label": "Usa", "name": "usa"}, {"description": "FortiGuard servers in the European Union", "help": "FortiGuard servers in the European Union.", "label": "Eu", "name": "eu"}] | None = ...,
        sandbox_region: str | None = ...,
        sandbox_inline_scan: Literal[{"help": "Enable FortiCloud Sandbox inline scan.", "label": "Enable", "name": "enable"}, {"help": "Disable FortiCloud Sandbox inline scan.", "label": "Disable", "name": "disable"}] | None = ...,
        update_ffdb: Literal[{"description": "Enable Internet Service Database update", "help": "Enable Internet Service Database update.", "label": "Enable", "name": "enable"}, {"description": "Disable Internet Service Database update", "help": "Disable Internet Service Database update.", "label": "Disable", "name": "disable"}] | None = ...,
        update_uwdb: Literal[{"description": "Enable allowlist update", "help": "Enable allowlist update.", "label": "Enable", "name": "enable"}, {"description": "Disable allowlist update", "help": "Disable allowlist update.", "label": "Disable", "name": "disable"}] | None = ...,
        update_dldb: Literal[{"description": "Enable DLP signature update", "help": "Enable DLP signature update.", "label": "Enable", "name": "enable"}, {"description": "Disable DLP signature update", "help": "Disable DLP signature update.", "label": "Disable", "name": "disable"}] | None = ...,
        update_extdb: Literal[{"description": "Enable external resource update", "help": "Enable external resource update.", "label": "Enable", "name": "enable"}, {"description": "Disable external resource update", "help": "Disable external resource update.", "label": "Disable", "name": "disable"}] | None = ...,
        update_build_proxy: Literal[{"description": "Enable proxy dictionary rebuild", "help": "Enable proxy dictionary rebuild.", "label": "Enable", "name": "enable"}, {"description": "Disable proxy dictionary rebuild", "help": "Disable proxy dictionary rebuild.", "label": "Disable", "name": "disable"}] | None = ...,
        persistent_connection: Literal[{"description": "Enable persistent connection to receive update notification from FortiGuard", "help": "Enable persistent connection to receive update notification from FortiGuard.", "label": "Enable", "name": "enable"}, {"description": "Disable persistent connection to receive update notification from FortiGuard", "help": "Disable persistent connection to receive update notification from FortiGuard.", "label": "Disable", "name": "disable"}] | None = ...,
        auto_firmware_upgrade: Literal[{"description": "Enable automatic patch-level firmware upgrade to latest version from FortiGuard", "help": "Enable automatic patch-level firmware upgrade to latest version from FortiGuard.", "label": "Enable", "name": "enable"}, {"description": "Disable automatic patch-level firmware upgrade to latest version from FortiGuard", "help": "Disable automatic patch-level firmware upgrade to latest version from FortiGuard.", "label": "Disable", "name": "disable"}] | None = ...,
        auto_firmware_upgrade_day: Literal[{"description": "Sunday", "help": "Sunday.", "label": "Sunday", "name": "sunday"}, {"description": "Monday", "help": "Monday.", "label": "Monday", "name": "monday"}, {"description": "Tuesday", "help": "Tuesday.", "label": "Tuesday", "name": "tuesday"}, {"description": "Wednesday", "help": "Wednesday.", "label": "Wednesday", "name": "wednesday"}, {"description": "Thursday", "help": "Thursday.", "label": "Thursday", "name": "thursday"}, {"description": "Friday", "help": "Friday.", "label": "Friday", "name": "friday"}, {"description": "Saturday", "help": "Saturday.", "label": "Saturday", "name": "saturday"}] | None = ...,
        auto_firmware_upgrade_delay: int | None = ...,
        auto_firmware_upgrade_start_hour: int | None = ...,
        auto_firmware_upgrade_end_hour: int | None = ...,
        FDS_license_expiring_days: int | None = ...,
        subscribe_update_notification: Literal[{"description": "Enable subscription to receive update notification from FortiGuard", "help": "Enable subscription to receive update notification from FortiGuard.", "label": "Enable", "name": "enable"}, {"description": "Disable subscription to receive update notification from FortiGuard", "help": "Disable subscription to receive update notification from FortiGuard.", "label": "Disable", "name": "disable"}] | None = ...,
        antispam_force_off: Literal[{"description": "Turn off the FortiGuard antispam service", "help": "Turn off the FortiGuard antispam service.", "label": "Enable", "name": "enable"}, {"description": "Allow the FortiGuard antispam service", "help": "Allow the FortiGuard antispam service.", "label": "Disable", "name": "disable"}] | None = ...,
        antispam_cache: Literal[{"description": "Enable FortiGuard antispam request caching", "help": "Enable FortiGuard antispam request caching.", "label": "Enable", "name": "enable"}, {"description": "Disable FortiGuard antispam request caching", "help": "Disable FortiGuard antispam request caching.", "label": "Disable", "name": "disable"}] | None = ...,
        antispam_cache_ttl: int | None = ...,
        antispam_cache_mpermille: int | None = ...,
        antispam_license: int | None = ...,
        antispam_expiration: int | None = ...,
        antispam_timeout: int | None = ...,
        outbreak_prevention_force_off: Literal[{"description": "Turn off FortiGuard antivirus service", "help": "Turn off FortiGuard antivirus service.", "label": "Enable", "name": "enable"}, {"description": "Allow the FortiGuard antivirus service", "help": "Allow the FortiGuard antivirus service.", "label": "Disable", "name": "disable"}] | None = ...,
        outbreak_prevention_cache: Literal[{"description": "Enable FortiGuard antivirus caching", "help": "Enable FortiGuard antivirus caching.", "label": "Enable", "name": "enable"}, {"description": "Disable FortiGuard antivirus caching", "help": "Disable FortiGuard antivirus caching.", "label": "Disable", "name": "disable"}] | None = ...,
        outbreak_prevention_cache_ttl: int | None = ...,
        outbreak_prevention_cache_mpermille: int | None = ...,
        outbreak_prevention_license: int | None = ...,
        outbreak_prevention_expiration: int | None = ...,
        outbreak_prevention_timeout: int | None = ...,
        webfilter_force_off: Literal[{"description": "Turn off the FortiGuard web filtering service", "help": "Turn off the FortiGuard web filtering service.", "label": "Enable", "name": "enable"}, {"description": "Allow the FortiGuard web filtering service to operate", "help": "Allow the FortiGuard web filtering service to operate.", "label": "Disable", "name": "disable"}] | None = ...,
        webfilter_cache: Literal[{"description": "Enable FortiGuard web filter caching", "help": "Enable FortiGuard web filter caching.", "label": "Enable", "name": "enable"}, {"description": "Disable FortiGuard web filter caching", "help": "Disable FortiGuard web filter caching.", "label": "Disable", "name": "disable"}] | None = ...,
        webfilter_cache_ttl: int | None = ...,
        webfilter_license: int | None = ...,
        webfilter_expiration: int | None = ...,
        webfilter_timeout: int | None = ...,
        sdns_server_ip: list[dict[str, Any]] | None = ...,
        sdns_server_port: int | None = ...,
        anycast_sdns_server_ip: str | None = ...,
        anycast_sdns_server_port: int | None = ...,
        sdns_options: Literal[{"description": "Include DNS question section in the FortiGuard DNS setup message", "help": "Include DNS question section in the FortiGuard DNS setup message.", "label": "Include Question Section", "name": "include-question-section"}] | None = ...,
        source_ip: str | None = ...,
        source_ip6: str | None = ...,
        proxy_server_ip: str | None = ...,
        proxy_server_port: int | None = ...,
        proxy_username: str | None = ...,
        proxy_password: str | None = ...,
        ddns_server_ip: str | None = ...,
        ddns_server_ip6: str | None = ...,
        ddns_server_port: int | None = ...,
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
        payload_dict: FortiguardPayload | None = ...,
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
    "Fortiguard",
    "FortiguardPayload",
]