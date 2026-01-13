from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class CentralManagementPayload(TypedDict, total=False):
    """
    Type hints for system/central_management payload fields.
    
    Configure central management.
    
    **Related Resources:**

    Dependencies (resources this endpoint references):
        - :class:`~.certificate.ca.CaEndpoint` (via: ca-cert)
        - :class:`~.certificate.local.LocalEndpoint` (via: local-cert)
        - :class:`~.system.accprofile.AccprofileEndpoint` (via: fortigate-cloud-sso-default-profile)
        - :class:`~.system.interface.InterfaceEndpoint` (via: interface)
        - :class:`~.system.vdom.VdomEndpoint` (via: vdom)

    **Usage:**
        payload: CentralManagementPayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    mode: NotRequired[Literal[{"description": "Manage and configure this FortiGate from FortiManager", "help": "Manage and configure this FortiGate from FortiManager.", "label": "Normal", "name": "normal"}, {"description": "Manage and configure this FortiGate locally and back up its configuration to FortiManager", "help": "Manage and configure this FortiGate locally and back up its configuration to FortiManager.", "label": "Backup", "name": "backup"}]]  # Central management mode.
    type: NotRequired[Literal[{"description": "FortiManager", "help": "FortiManager.", "label": "Fortimanager", "name": "fortimanager"}, {"description": "Central management of this FortiGate using FortiCloud", "help": "Central management of this FortiGate using FortiCloud.", "label": "Fortiguard", "name": "fortiguard"}, {"description": "No central management", "help": "No central management.", "label": "None", "name": "none"}]]  # Central management type.
    fortigate_cloud_sso_default_profile: NotRequired[str]  # Override access profile. Permission is set to read-only with
    schedule_config_restore: NotRequired[Literal[{"description": "Enable scheduled configuration restore", "help": "Enable scheduled configuration restore.", "label": "Enable", "name": "enable"}, {"description": "Disable scheduled configuration restore", "help": "Disable scheduled configuration restore.", "label": "Disable", "name": "disable"}]]  # Enable/disable allowing the central management server to res
    schedule_script_restore: NotRequired[Literal[{"description": "Enable scheduled script restore", "help": "Enable scheduled script restore.", "label": "Enable", "name": "enable"}, {"description": "Disable scheduled script restore", "help": "Disable scheduled script restore.", "label": "Disable", "name": "disable"}]]  # Enable/disable allowing the central management server to res
    allow_push_configuration: NotRequired[Literal[{"description": "Enable push configuration", "help": "Enable push configuration.", "label": "Enable", "name": "enable"}, {"description": "Disable push configuration", "help": "Disable push configuration.", "label": "Disable", "name": "disable"}]]  # Enable/disable allowing the central management server to pus
    allow_push_firmware: NotRequired[Literal[{"description": "Enable push firmware", "help": "Enable push firmware.", "label": "Enable", "name": "enable"}, {"description": "Disable push firmware", "help": "Disable push firmware.", "label": "Disable", "name": "disable"}]]  # Enable/disable allowing the central management server to pus
    allow_remote_firmware_upgrade: NotRequired[Literal[{"description": "Enable remote firmware upgrade", "help": "Enable remote firmware upgrade.", "label": "Enable", "name": "enable"}, {"description": "Disable remote firmware upgrade", "help": "Disable remote firmware upgrade.", "label": "Disable", "name": "disable"}]]  # Enable/disable remotely upgrading the firmware on this Forti
    allow_monitor: NotRequired[Literal[{"description": "Enable remote monitoring of device", "help": "Enable remote monitoring of device.", "label": "Enable", "name": "enable"}, {"description": "Disable remote monitoring of device", "help": "Disable remote monitoring of device.", "label": "Disable", "name": "disable"}]]  # Enable/disable allowing the central management server to rem
    serial_number: NotRequired[str]  # Serial number.
    fmg: NotRequired[str]  # IP address or FQDN of the FortiManager.
    fmg_source_ip: NotRequired[str]  # IPv4 source address that this FortiGate uses when communicat
    fmg_source_ip6: NotRequired[str]  # IPv6 source address that this FortiGate uses when communicat
    local_cert: NotRequired[str]  # Certificate to be used by FGFM protocol.
    ca_cert: NotRequired[str]  # CA certificate to be used by FGFM protocol.
    vdom: NotRequired[str]  # Virtual domain (VDOM) name to use when communicating with Fo
    server_list: NotRequired[list[dict[str, Any]]]  # Additional severs that the FortiGate can use for updates (fo
    fmg_update_port: NotRequired[Literal[{"description": "Use port 8890 to communicate with FortiManager that is acting as a FortiGuard update server", "help": "Use port 8890 to communicate with FortiManager that is acting as a FortiGuard update server.", "label": "8890", "name": "8890"}, {"description": "Use port 443 to communicate with FortiManager that is acting as a FortiGuard update server", "help": "Use port 443 to communicate with FortiManager that is acting as a FortiGuard update server.", "label": "443", "name": "443"}]]  # Port used to communicate with FortiManager that is acting as
    fmg_update_http_header: NotRequired[Literal[{"description": "Enable inclusion of HTTP header in update request", "help": "Enable inclusion of HTTP header in update request.", "label": "Enable", "name": "enable"}, {"description": "Disable inclusion of HTTP header in update request", "help": "Disable inclusion of HTTP header in update request.", "label": "Disable", "name": "disable"}]]  # Enable/disable inclusion of HTTP header in update request.
    include_default_servers: NotRequired[Literal[{"description": "Enable inclusion of public FortiGuard servers in the override server list", "help": "Enable inclusion of public FortiGuard servers in the override server list.", "label": "Enable", "name": "enable"}, {"description": "Disable inclusion of public FortiGuard servers in the override server list", "help": "Disable inclusion of public FortiGuard servers in the override server list.", "label": "Disable", "name": "disable"}]]  # Enable/disable inclusion of public FortiGuard servers in the
    enc_algorithm: NotRequired[Literal[{"description": "High strength algorithms and medium-strength 128-bit key length algorithms", "help": "High strength algorithms and medium-strength 128-bit key length algorithms.", "label": "Default", "name": "default"}, {"description": "128-bit and larger key length algorithms", "help": "128-bit and larger key length algorithms.", "label": "High", "name": "high"}, {"description": "64-bit or 56-bit key length algorithms without export restrictions", "help": "64-bit or 56-bit key length algorithms without export restrictions.", "label": "Low", "name": "low"}]]  # Encryption strength for communications between the FortiGate
    interface_select_method: NotRequired[Literal[{"description": "Set outgoing interface automatically", "help": "Set outgoing interface automatically.", "label": "Auto", "name": "auto"}, {"description": "Set outgoing interface by SD-WAN or policy routing rules", "help": "Set outgoing interface by SD-WAN or policy routing rules.", "label": "Sdwan", "name": "sdwan"}, {"description": "Set outgoing interface manually", "help": "Set outgoing interface manually.", "label": "Specify", "name": "specify"}]]  # Specify how to select outgoing interface to reach server.
    interface: str  # Specify outgoing interface to reach server.
    vrf_select: NotRequired[int]  # VRF ID used for connection to server.


class CentralManagement:
    """
    Configure central management.
    
    Path: system/central_management
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
        payload_dict: CentralManagementPayload | None = ...,
        mode: Literal[{"description": "Manage and configure this FortiGate from FortiManager", "help": "Manage and configure this FortiGate from FortiManager.", "label": "Normal", "name": "normal"}, {"description": "Manage and configure this FortiGate locally and back up its configuration to FortiManager", "help": "Manage and configure this FortiGate locally and back up its configuration to FortiManager.", "label": "Backup", "name": "backup"}] | None = ...,
        type: Literal[{"description": "FortiManager", "help": "FortiManager.", "label": "Fortimanager", "name": "fortimanager"}, {"description": "Central management of this FortiGate using FortiCloud", "help": "Central management of this FortiGate using FortiCloud.", "label": "Fortiguard", "name": "fortiguard"}, {"description": "No central management", "help": "No central management.", "label": "None", "name": "none"}] | None = ...,
        fortigate_cloud_sso_default_profile: str | None = ...,
        schedule_config_restore: Literal[{"description": "Enable scheduled configuration restore", "help": "Enable scheduled configuration restore.", "label": "Enable", "name": "enable"}, {"description": "Disable scheduled configuration restore", "help": "Disable scheduled configuration restore.", "label": "Disable", "name": "disable"}] | None = ...,
        schedule_script_restore: Literal[{"description": "Enable scheduled script restore", "help": "Enable scheduled script restore.", "label": "Enable", "name": "enable"}, {"description": "Disable scheduled script restore", "help": "Disable scheduled script restore.", "label": "Disable", "name": "disable"}] | None = ...,
        allow_push_configuration: Literal[{"description": "Enable push configuration", "help": "Enable push configuration.", "label": "Enable", "name": "enable"}, {"description": "Disable push configuration", "help": "Disable push configuration.", "label": "Disable", "name": "disable"}] | None = ...,
        allow_push_firmware: Literal[{"description": "Enable push firmware", "help": "Enable push firmware.", "label": "Enable", "name": "enable"}, {"description": "Disable push firmware", "help": "Disable push firmware.", "label": "Disable", "name": "disable"}] | None = ...,
        allow_remote_firmware_upgrade: Literal[{"description": "Enable remote firmware upgrade", "help": "Enable remote firmware upgrade.", "label": "Enable", "name": "enable"}, {"description": "Disable remote firmware upgrade", "help": "Disable remote firmware upgrade.", "label": "Disable", "name": "disable"}] | None = ...,
        allow_monitor: Literal[{"description": "Enable remote monitoring of device", "help": "Enable remote monitoring of device.", "label": "Enable", "name": "enable"}, {"description": "Disable remote monitoring of device", "help": "Disable remote monitoring of device.", "label": "Disable", "name": "disable"}] | None = ...,
        serial_number: str | None = ...,
        fmg: str | None = ...,
        fmg_source_ip: str | None = ...,
        fmg_source_ip6: str | None = ...,
        local_cert: str | None = ...,
        ca_cert: str | None = ...,
        server_list: list[dict[str, Any]] | None = ...,
        fmg_update_port: Literal[{"description": "Use port 8890 to communicate with FortiManager that is acting as a FortiGuard update server", "help": "Use port 8890 to communicate with FortiManager that is acting as a FortiGuard update server.", "label": "8890", "name": "8890"}, {"description": "Use port 443 to communicate with FortiManager that is acting as a FortiGuard update server", "help": "Use port 443 to communicate with FortiManager that is acting as a FortiGuard update server.", "label": "443", "name": "443"}] | None = ...,
        fmg_update_http_header: Literal[{"description": "Enable inclusion of HTTP header in update request", "help": "Enable inclusion of HTTP header in update request.", "label": "Enable", "name": "enable"}, {"description": "Disable inclusion of HTTP header in update request", "help": "Disable inclusion of HTTP header in update request.", "label": "Disable", "name": "disable"}] | None = ...,
        include_default_servers: Literal[{"description": "Enable inclusion of public FortiGuard servers in the override server list", "help": "Enable inclusion of public FortiGuard servers in the override server list.", "label": "Enable", "name": "enable"}, {"description": "Disable inclusion of public FortiGuard servers in the override server list", "help": "Disable inclusion of public FortiGuard servers in the override server list.", "label": "Disable", "name": "disable"}] | None = ...,
        enc_algorithm: Literal[{"description": "High strength algorithms and medium-strength 128-bit key length algorithms", "help": "High strength algorithms and medium-strength 128-bit key length algorithms.", "label": "Default", "name": "default"}, {"description": "128-bit and larger key length algorithms", "help": "128-bit and larger key length algorithms.", "label": "High", "name": "high"}, {"description": "64-bit or 56-bit key length algorithms without export restrictions", "help": "64-bit or 56-bit key length algorithms without export restrictions.", "label": "Low", "name": "low"}] | None = ...,
        interface_select_method: Literal[{"description": "Set outgoing interface automatically", "help": "Set outgoing interface automatically.", "label": "Auto", "name": "auto"}, {"description": "Set outgoing interface by SD-WAN or policy routing rules", "help": "Set outgoing interface by SD-WAN or policy routing rules.", "label": "Sdwan", "name": "sdwan"}, {"description": "Set outgoing interface manually", "help": "Set outgoing interface manually.", "label": "Specify", "name": "specify"}] | None = ...,
        interface: str | None = ...,
        vrf_select: int | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: CentralManagementPayload | None = ...,
        mode: Literal[{"description": "Manage and configure this FortiGate from FortiManager", "help": "Manage and configure this FortiGate from FortiManager.", "label": "Normal", "name": "normal"}, {"description": "Manage and configure this FortiGate locally and back up its configuration to FortiManager", "help": "Manage and configure this FortiGate locally and back up its configuration to FortiManager.", "label": "Backup", "name": "backup"}] | None = ...,
        type: Literal[{"description": "FortiManager", "help": "FortiManager.", "label": "Fortimanager", "name": "fortimanager"}, {"description": "Central management of this FortiGate using FortiCloud", "help": "Central management of this FortiGate using FortiCloud.", "label": "Fortiguard", "name": "fortiguard"}, {"description": "No central management", "help": "No central management.", "label": "None", "name": "none"}] | None = ...,
        fortigate_cloud_sso_default_profile: str | None = ...,
        schedule_config_restore: Literal[{"description": "Enable scheduled configuration restore", "help": "Enable scheduled configuration restore.", "label": "Enable", "name": "enable"}, {"description": "Disable scheduled configuration restore", "help": "Disable scheduled configuration restore.", "label": "Disable", "name": "disable"}] | None = ...,
        schedule_script_restore: Literal[{"description": "Enable scheduled script restore", "help": "Enable scheduled script restore.", "label": "Enable", "name": "enable"}, {"description": "Disable scheduled script restore", "help": "Disable scheduled script restore.", "label": "Disable", "name": "disable"}] | None = ...,
        allow_push_configuration: Literal[{"description": "Enable push configuration", "help": "Enable push configuration.", "label": "Enable", "name": "enable"}, {"description": "Disable push configuration", "help": "Disable push configuration.", "label": "Disable", "name": "disable"}] | None = ...,
        allow_push_firmware: Literal[{"description": "Enable push firmware", "help": "Enable push firmware.", "label": "Enable", "name": "enable"}, {"description": "Disable push firmware", "help": "Disable push firmware.", "label": "Disable", "name": "disable"}] | None = ...,
        allow_remote_firmware_upgrade: Literal[{"description": "Enable remote firmware upgrade", "help": "Enable remote firmware upgrade.", "label": "Enable", "name": "enable"}, {"description": "Disable remote firmware upgrade", "help": "Disable remote firmware upgrade.", "label": "Disable", "name": "disable"}] | None = ...,
        allow_monitor: Literal[{"description": "Enable remote monitoring of device", "help": "Enable remote monitoring of device.", "label": "Enable", "name": "enable"}, {"description": "Disable remote monitoring of device", "help": "Disable remote monitoring of device.", "label": "Disable", "name": "disable"}] | None = ...,
        serial_number: str | None = ...,
        fmg: str | None = ...,
        fmg_source_ip: str | None = ...,
        fmg_source_ip6: str | None = ...,
        local_cert: str | None = ...,
        ca_cert: str | None = ...,
        server_list: list[dict[str, Any]] | None = ...,
        fmg_update_port: Literal[{"description": "Use port 8890 to communicate with FortiManager that is acting as a FortiGuard update server", "help": "Use port 8890 to communicate with FortiManager that is acting as a FortiGuard update server.", "label": "8890", "name": "8890"}, {"description": "Use port 443 to communicate with FortiManager that is acting as a FortiGuard update server", "help": "Use port 443 to communicate with FortiManager that is acting as a FortiGuard update server.", "label": "443", "name": "443"}] | None = ...,
        fmg_update_http_header: Literal[{"description": "Enable inclusion of HTTP header in update request", "help": "Enable inclusion of HTTP header in update request.", "label": "Enable", "name": "enable"}, {"description": "Disable inclusion of HTTP header in update request", "help": "Disable inclusion of HTTP header in update request.", "label": "Disable", "name": "disable"}] | None = ...,
        include_default_servers: Literal[{"description": "Enable inclusion of public FortiGuard servers in the override server list", "help": "Enable inclusion of public FortiGuard servers in the override server list.", "label": "Enable", "name": "enable"}, {"description": "Disable inclusion of public FortiGuard servers in the override server list", "help": "Disable inclusion of public FortiGuard servers in the override server list.", "label": "Disable", "name": "disable"}] | None = ...,
        enc_algorithm: Literal[{"description": "High strength algorithms and medium-strength 128-bit key length algorithms", "help": "High strength algorithms and medium-strength 128-bit key length algorithms.", "label": "Default", "name": "default"}, {"description": "128-bit and larger key length algorithms", "help": "128-bit and larger key length algorithms.", "label": "High", "name": "high"}, {"description": "64-bit or 56-bit key length algorithms without export restrictions", "help": "64-bit or 56-bit key length algorithms without export restrictions.", "label": "Low", "name": "low"}] | None = ...,
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
        payload_dict: CentralManagementPayload | None = ...,
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
    "CentralManagement",
    "CentralManagementPayload",
]