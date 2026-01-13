from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class CsfPayload(TypedDict, total=False):
    """
    Type hints for system/csf payload fields.
    
    Add this FortiGate to a Security Fabric or set up a new Security Fabric on this FortiGate.
    
    **Related Resources:**

    Dependencies (resources this endpoint references):
        - :class:`~.certificate.local.LocalEndpoint` (via: certificate)
        - :class:`~.system.accprofile.AccprofileEndpoint` (via: downstream-accprofile)
        - :class:`~.system.interface.InterfaceEndpoint` (via: upstream-interface)

    **Usage:**
        payload: CsfPayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    status: Literal[{"description": "Enable Security Fabric", "help": "Enable Security Fabric.", "label": "Enable", "name": "enable"}, {"description": "Disable Security Fabric", "help": "Disable Security Fabric.", "label": "Disable", "name": "disable"}]  # Enable/disable Security Fabric.
    uid: NotRequired[str]  # Unique ID of the current CSF node
    upstream: NotRequired[str]  # IP/FQDN of the FortiGate upstream from this FortiGate in the
    source_ip: NotRequired[str]  # Source IP address for communication with the upstream FortiG
    upstream_interface_select_method: NotRequired[Literal[{"description": "Set outgoing interface automatically", "help": "Set outgoing interface automatically.", "label": "Auto", "name": "auto"}, {"description": "Set outgoing interface by SD-WAN or policy routing rules", "help": "Set outgoing interface by SD-WAN or policy routing rules.", "label": "Sdwan", "name": "sdwan"}, {"description": "Set outgoing interface manually", "help": "Set outgoing interface manually.", "label": "Specify", "name": "specify"}]]  # Specify how to select outgoing interface to reach server.
    upstream_interface: str  # Specify outgoing interface to reach server.
    upstream_port: NotRequired[int]  # The port number to use to communicate with the FortiGate ups
    group_name: NotRequired[str]  # Security Fabric group name. All FortiGates in a Security Fab
    group_password: NotRequired[str]  # Security Fabric group password. For legacy authentication, f
    accept_auth_by_cert: NotRequired[Literal[{"description": "Do not accept SSL connections with unknown certificates", "help": "Do not accept SSL connections with unknown certificates.", "label": "Disable", "name": "disable"}, {"description": "Accept SSL connections without automatic certificate verification", "help": "Accept SSL connections without automatic certificate verification.", "label": "Enable", "name": "enable"}]]  # Accept connections with unknown certificates and ask admin f
    log_unification: NotRequired[Literal[{"description": "Disable broadcast of discovery messages for log unification", "help": "Disable broadcast of discovery messages for log unification.", "label": "Disable", "name": "disable"}, {"description": "Enable broadcast of discovery messages for log unification", "help": "Enable broadcast of discovery messages for log unification.", "label": "Enable", "name": "enable"}]]  # Enable/disable broadcast of discovery messages for log unifi
    authorization_request_type: NotRequired[Literal[{"description": "Request verification by serial number", "help": "Request verification by serial number.", "label": "Serial", "name": "serial"}, {"description": "Request verification by certificate", "help": "Request verification by certificate.", "label": "Certificate", "name": "certificate"}]]  # Authorization request type.
    certificate: NotRequired[str]  # Certificate.
    fabric_workers: NotRequired[int]  # Number of worker processes for Security Fabric daemon.
    downstream_access: NotRequired[Literal[{"description": "Enable downstream device access to this device\u0027s configuration and data", "help": "Enable downstream device access to this device\u0027s configuration and data.", "label": "Enable", "name": "enable"}, {"description": "Disable downstream device access to this device\u0027s configuration and data", "help": "Disable downstream device access to this device\u0027s configuration and data.", "label": "Disable", "name": "disable"}]]  # Enable/disable downstream device access to this device's con
    legacy_authentication: NotRequired[Literal[{"description": "Do not accept legacy authentication requests", "help": "Do not accept legacy authentication requests.", "label": "Disable", "name": "disable"}, {"description": "Accept legacy authentication requests", "help": "Accept legacy authentication requests.", "label": "Enable", "name": "enable"}]]  # Enable/disable legacy authentication.
    downstream_accprofile: str  # Default access profile for requests from downstream devices.
    configuration_sync: Literal[{"description": "Synchronize configuration for IPAM, FortiAnalyzer, FortiSandbox, and Central Management to root node", "help": "Synchronize configuration for IPAM, FortiAnalyzer, FortiSandbox, and Central Management to root node.", "label": "Default", "name": "default"}, {"description": "Do not synchronize configuration with root node", "help": "Do not synchronize configuration with root node.", "label": "Local", "name": "local"}]  # Configuration sync mode.
    fabric_object_unification: NotRequired[Literal[{"description": "Global CMDB objects will be synchronized in Security Fabric", "help": "Global CMDB objects will be synchronized in Security Fabric.", "label": "Default", "name": "default"}, {"description": "Global CMDB objects will not be synchronized to and from this device", "help": "Global CMDB objects will not be synchronized to and from this device.", "label": "Local", "name": "local"}]]  # Fabric CMDB Object Unification.
    saml_configuration_sync: NotRequired[Literal[{"description": "SAML setting for fabric members is created by fabric root", "help": "SAML setting for fabric members is created by fabric root.", "label": "Default", "name": "default"}, {"description": "Do not apply SAML configuration generated by root", "help": "Do not apply SAML configuration generated by root.", "label": "Local", "name": "local"}]]  # SAML setting configuration synchronization.
    trusted_list: NotRequired[list[dict[str, Any]]]  # Pre-authorized and blocked security fabric nodes.
    fabric_connector: NotRequired[list[dict[str, Any]]]  # Fabric connector configuration.
    forticloud_account_enforcement: NotRequired[Literal[{"description": "Enable FortiCloud account ID matching for Security Fabric", "help": "Enable FortiCloud account ID matching for Security Fabric.", "label": "Enable", "name": "enable"}, {"description": "Disable FortiCloud accound ID matching for Security Fabric", "help": "Disable FortiCloud accound ID matching for Security Fabric.", "label": "Disable", "name": "disable"}]]  # Fabric FortiCloud account unification.
    file_mgmt: NotRequired[Literal[{"description": "Enable daemon file management", "help": "Enable daemon file management.", "label": "Enable", "name": "enable"}, {"description": "Disable daemon file management", "help": "Disable daemon file management.", "label": "Disable", "name": "disable"}]]  # Enable/disable Security Fabric daemon file management.
    file_quota: NotRequired[int]  # Maximum amount of memory that can be used by the daemon file
    file_quota_warning: NotRequired[int]  # Warn when the set percentage of quota has been used.


class Csf:
    """
    Add this FortiGate to a Security Fabric or set up a new Security Fabric on this FortiGate.
    
    Path: system/csf
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
        payload_dict: CsfPayload | None = ...,
        status: Literal[{"description": "Enable Security Fabric", "help": "Enable Security Fabric.", "label": "Enable", "name": "enable"}, {"description": "Disable Security Fabric", "help": "Disable Security Fabric.", "label": "Disable", "name": "disable"}] | None = ...,
        uid: str | None = ...,
        upstream: str | None = ...,
        source_ip: str | None = ...,
        upstream_interface_select_method: Literal[{"description": "Set outgoing interface automatically", "help": "Set outgoing interface automatically.", "label": "Auto", "name": "auto"}, {"description": "Set outgoing interface by SD-WAN or policy routing rules", "help": "Set outgoing interface by SD-WAN or policy routing rules.", "label": "Sdwan", "name": "sdwan"}, {"description": "Set outgoing interface manually", "help": "Set outgoing interface manually.", "label": "Specify", "name": "specify"}] | None = ...,
        upstream_interface: str | None = ...,
        upstream_port: int | None = ...,
        group_name: str | None = ...,
        group_password: str | None = ...,
        accept_auth_by_cert: Literal[{"description": "Do not accept SSL connections with unknown certificates", "help": "Do not accept SSL connections with unknown certificates.", "label": "Disable", "name": "disable"}, {"description": "Accept SSL connections without automatic certificate verification", "help": "Accept SSL connections without automatic certificate verification.", "label": "Enable", "name": "enable"}] | None = ...,
        log_unification: Literal[{"description": "Disable broadcast of discovery messages for log unification", "help": "Disable broadcast of discovery messages for log unification.", "label": "Disable", "name": "disable"}, {"description": "Enable broadcast of discovery messages for log unification", "help": "Enable broadcast of discovery messages for log unification.", "label": "Enable", "name": "enable"}] | None = ...,
        authorization_request_type: Literal[{"description": "Request verification by serial number", "help": "Request verification by serial number.", "label": "Serial", "name": "serial"}, {"description": "Request verification by certificate", "help": "Request verification by certificate.", "label": "Certificate", "name": "certificate"}] | None = ...,
        certificate: str | None = ...,
        fabric_workers: int | None = ...,
        downstream_access: Literal[{"description": "Enable downstream device access to this device\u0027s configuration and data", "help": "Enable downstream device access to this device\u0027s configuration and data.", "label": "Enable", "name": "enable"}, {"description": "Disable downstream device access to this device\u0027s configuration and data", "help": "Disable downstream device access to this device\u0027s configuration and data.", "label": "Disable", "name": "disable"}] | None = ...,
        legacy_authentication: Literal[{"description": "Do not accept legacy authentication requests", "help": "Do not accept legacy authentication requests.", "label": "Disable", "name": "disable"}, {"description": "Accept legacy authentication requests", "help": "Accept legacy authentication requests.", "label": "Enable", "name": "enable"}] | None = ...,
        downstream_accprofile: str | None = ...,
        configuration_sync: Literal[{"description": "Synchronize configuration for IPAM, FortiAnalyzer, FortiSandbox, and Central Management to root node", "help": "Synchronize configuration for IPAM, FortiAnalyzer, FortiSandbox, and Central Management to root node.", "label": "Default", "name": "default"}, {"description": "Do not synchronize configuration with root node", "help": "Do not synchronize configuration with root node.", "label": "Local", "name": "local"}] | None = ...,
        fabric_object_unification: Literal[{"description": "Global CMDB objects will be synchronized in Security Fabric", "help": "Global CMDB objects will be synchronized in Security Fabric.", "label": "Default", "name": "default"}, {"description": "Global CMDB objects will not be synchronized to and from this device", "help": "Global CMDB objects will not be synchronized to and from this device.", "label": "Local", "name": "local"}] | None = ...,
        saml_configuration_sync: Literal[{"description": "SAML setting for fabric members is created by fabric root", "help": "SAML setting for fabric members is created by fabric root.", "label": "Default", "name": "default"}, {"description": "Do not apply SAML configuration generated by root", "help": "Do not apply SAML configuration generated by root.", "label": "Local", "name": "local"}] | None = ...,
        trusted_list: list[dict[str, Any]] | None = ...,
        fabric_connector: list[dict[str, Any]] | None = ...,
        forticloud_account_enforcement: Literal[{"description": "Enable FortiCloud account ID matching for Security Fabric", "help": "Enable FortiCloud account ID matching for Security Fabric.", "label": "Enable", "name": "enable"}, {"description": "Disable FortiCloud accound ID matching for Security Fabric", "help": "Disable FortiCloud accound ID matching for Security Fabric.", "label": "Disable", "name": "disable"}] | None = ...,
        file_mgmt: Literal[{"description": "Enable daemon file management", "help": "Enable daemon file management.", "label": "Enable", "name": "enable"}, {"description": "Disable daemon file management", "help": "Disable daemon file management.", "label": "Disable", "name": "disable"}] | None = ...,
        file_quota: int | None = ...,
        file_quota_warning: int | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: CsfPayload | None = ...,
        status: Literal[{"description": "Enable Security Fabric", "help": "Enable Security Fabric.", "label": "Enable", "name": "enable"}, {"description": "Disable Security Fabric", "help": "Disable Security Fabric.", "label": "Disable", "name": "disable"}] | None = ...,
        uid: str | None = ...,
        upstream: str | None = ...,
        source_ip: str | None = ...,
        upstream_interface_select_method: Literal[{"description": "Set outgoing interface automatically", "help": "Set outgoing interface automatically.", "label": "Auto", "name": "auto"}, {"description": "Set outgoing interface by SD-WAN or policy routing rules", "help": "Set outgoing interface by SD-WAN or policy routing rules.", "label": "Sdwan", "name": "sdwan"}, {"description": "Set outgoing interface manually", "help": "Set outgoing interface manually.", "label": "Specify", "name": "specify"}] | None = ...,
        upstream_interface: str | None = ...,
        upstream_port: int | None = ...,
        group_name: str | None = ...,
        group_password: str | None = ...,
        accept_auth_by_cert: Literal[{"description": "Do not accept SSL connections with unknown certificates", "help": "Do not accept SSL connections with unknown certificates.", "label": "Disable", "name": "disable"}, {"description": "Accept SSL connections without automatic certificate verification", "help": "Accept SSL connections without automatic certificate verification.", "label": "Enable", "name": "enable"}] | None = ...,
        log_unification: Literal[{"description": "Disable broadcast of discovery messages for log unification", "help": "Disable broadcast of discovery messages for log unification.", "label": "Disable", "name": "disable"}, {"description": "Enable broadcast of discovery messages for log unification", "help": "Enable broadcast of discovery messages for log unification.", "label": "Enable", "name": "enable"}] | None = ...,
        authorization_request_type: Literal[{"description": "Request verification by serial number", "help": "Request verification by serial number.", "label": "Serial", "name": "serial"}, {"description": "Request verification by certificate", "help": "Request verification by certificate.", "label": "Certificate", "name": "certificate"}] | None = ...,
        certificate: str | None = ...,
        fabric_workers: int | None = ...,
        downstream_access: Literal[{"description": "Enable downstream device access to this device\u0027s configuration and data", "help": "Enable downstream device access to this device\u0027s configuration and data.", "label": "Enable", "name": "enable"}, {"description": "Disable downstream device access to this device\u0027s configuration and data", "help": "Disable downstream device access to this device\u0027s configuration and data.", "label": "Disable", "name": "disable"}] | None = ...,
        legacy_authentication: Literal[{"description": "Do not accept legacy authentication requests", "help": "Do not accept legacy authentication requests.", "label": "Disable", "name": "disable"}, {"description": "Accept legacy authentication requests", "help": "Accept legacy authentication requests.", "label": "Enable", "name": "enable"}] | None = ...,
        downstream_accprofile: str | None = ...,
        configuration_sync: Literal[{"description": "Synchronize configuration for IPAM, FortiAnalyzer, FortiSandbox, and Central Management to root node", "help": "Synchronize configuration for IPAM, FortiAnalyzer, FortiSandbox, and Central Management to root node.", "label": "Default", "name": "default"}, {"description": "Do not synchronize configuration with root node", "help": "Do not synchronize configuration with root node.", "label": "Local", "name": "local"}] | None = ...,
        fabric_object_unification: Literal[{"description": "Global CMDB objects will be synchronized in Security Fabric", "help": "Global CMDB objects will be synchronized in Security Fabric.", "label": "Default", "name": "default"}, {"description": "Global CMDB objects will not be synchronized to and from this device", "help": "Global CMDB objects will not be synchronized to and from this device.", "label": "Local", "name": "local"}] | None = ...,
        saml_configuration_sync: Literal[{"description": "SAML setting for fabric members is created by fabric root", "help": "SAML setting for fabric members is created by fabric root.", "label": "Default", "name": "default"}, {"description": "Do not apply SAML configuration generated by root", "help": "Do not apply SAML configuration generated by root.", "label": "Local", "name": "local"}] | None = ...,
        trusted_list: list[dict[str, Any]] | None = ...,
        fabric_connector: list[dict[str, Any]] | None = ...,
        forticloud_account_enforcement: Literal[{"description": "Enable FortiCloud account ID matching for Security Fabric", "help": "Enable FortiCloud account ID matching for Security Fabric.", "label": "Enable", "name": "enable"}, {"description": "Disable FortiCloud accound ID matching for Security Fabric", "help": "Disable FortiCloud accound ID matching for Security Fabric.", "label": "Disable", "name": "disable"}] | None = ...,
        file_mgmt: Literal[{"description": "Enable daemon file management", "help": "Enable daemon file management.", "label": "Enable", "name": "enable"}, {"description": "Disable daemon file management", "help": "Disable daemon file management.", "label": "Disable", "name": "disable"}] | None = ...,
        file_quota: int | None = ...,
        file_quota_warning: int | None = ...,
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
        payload_dict: CsfPayload | None = ...,
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
    "Csf",
    "CsfPayload",
]