from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class FortisandboxPayload(TypedDict, total=False):
    """
    Type hints for system/fortisandbox payload fields.
    
    Configure FortiSandbox.
    
    **Related Resources:**

    Dependencies (resources this endpoint references):
        - :class:`~.system.interface.InterfaceEndpoint` (via: interface)
        - :class:`~.vpn.certificate.ca.CaEndpoint` (via: ca)

    **Usage:**
        payload: FortisandboxPayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    status: NotRequired[Literal[{"description": "Enable FortiSandbox", "help": "Enable FortiSandbox.", "label": "Enable", "name": "enable"}, {"description": "Disable FortiSandbox", "help": "Disable FortiSandbox.", "label": "Disable", "name": "disable"}]]  # Enable/disable FortiSandbox.
    forticloud: NotRequired[Literal[{"description": "Enable FortiSandbox Cloud", "help": "Enable FortiSandbox Cloud.", "label": "Enable", "name": "enable"}, {"description": "Disable FortiSandbox Cloud", "help": "Disable FortiSandbox Cloud.", "label": "Disable", "name": "disable"}]]  # Enable/disable FortiSandbox Cloud.
    inline_scan: NotRequired[Literal[{"help": "Enable FortiSandbox inline scan.", "label": "Enable", "name": "enable"}, {"help": "Disable FortiSandbox inline scan.", "label": "Disable", "name": "disable"}]]  # Enable/disable FortiSandbox inline scan.
    server: str  # Server IP address or FQDN of the remote FortiSandbox.
    source_ip: NotRequired[str]  # Source IP address for communications to FortiSandbox.
    interface_select_method: NotRequired[Literal[{"description": "Set outgoing interface automatically", "help": "Set outgoing interface automatically.", "label": "Auto", "name": "auto"}, {"description": "Set outgoing interface by SD-WAN or policy routing rules", "help": "Set outgoing interface by SD-WAN or policy routing rules.", "label": "Sdwan", "name": "sdwan"}, {"description": "Set outgoing interface manually", "help": "Set outgoing interface manually.", "label": "Specify", "name": "specify"}]]  # Specify how to select outgoing interface to reach server.
    interface: str  # Specify outgoing interface to reach server.
    vrf_select: NotRequired[int]  # VRF ID used for connection to server.
    enc_algorithm: NotRequired[Literal[{"description": "SSL communication with high and medium encryption algorithms", "help": "SSL communication with high and medium encryption algorithms.", "label": "Default", "name": "default"}, {"description": "SSL communication with high encryption algorithms", "help": "SSL communication with high encryption algorithms.", "label": "High", "name": "high"}, {"description": "SSL communication with low encryption algorithms", "help": "SSL communication with low encryption algorithms.", "label": "Low", "name": "low"}]]  # Configure the level of SSL protection for secure communicati
    ssl_min_proto_version: NotRequired[Literal[{"description": "Follow system global setting", "help": "Follow system global setting.", "label": "Default", "name": "default"}, {"description": "SSLv3", "help": "SSLv3.", "label": "Sslv3", "name": "SSLv3"}, {"description": "TLSv1", "help": "TLSv1.", "label": "Tlsv1", "name": "TLSv1"}, {"description": "TLSv1", "help": "TLSv1.1.", "label": "Tlsv1 1", "name": "TLSv1-1"}, {"description": "TLSv1", "help": "TLSv1.2.", "label": "Tlsv1 2", "name": "TLSv1-2"}, {"description": "TLSv1", "help": "TLSv1.3.", "label": "Tlsv1 3", "name": "TLSv1-3"}]]  # Minimum supported protocol version for SSL/TLS connections (
    email: NotRequired[str]  # Notifier email address.
    ca: NotRequired[str]  # The CA that signs remote FortiSandbox certificate, empty for
    cn: NotRequired[str]  # The CN of remote server certificate, case sensitive, empty f
    certificate_verification: NotRequired[Literal[{"description": "Enable identity verification of FortiSandbox by use of certificate", "help": "Enable identity verification of FortiSandbox by use of certificate.", "label": "Enable", "name": "enable"}, {"description": "Disable identity verification of FortiSandbox by use of certificate", "help": "Disable identity verification of FortiSandbox by use of certificate.", "label": "Disable", "name": "disable"}]]  # Enable/disable identity verification of FortiSandbox by use 


class Fortisandbox:
    """
    Configure FortiSandbox.
    
    Path: system/fortisandbox
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
        payload_dict: FortisandboxPayload | None = ...,
        status: Literal[{"description": "Enable FortiSandbox", "help": "Enable FortiSandbox.", "label": "Enable", "name": "enable"}, {"description": "Disable FortiSandbox", "help": "Disable FortiSandbox.", "label": "Disable", "name": "disable"}] | None = ...,
        forticloud: Literal[{"description": "Enable FortiSandbox Cloud", "help": "Enable FortiSandbox Cloud.", "label": "Enable", "name": "enable"}, {"description": "Disable FortiSandbox Cloud", "help": "Disable FortiSandbox Cloud.", "label": "Disable", "name": "disable"}] | None = ...,
        inline_scan: Literal[{"help": "Enable FortiSandbox inline scan.", "label": "Enable", "name": "enable"}, {"help": "Disable FortiSandbox inline scan.", "label": "Disable", "name": "disable"}] | None = ...,
        server: str | None = ...,
        source_ip: str | None = ...,
        interface_select_method: Literal[{"description": "Set outgoing interface automatically", "help": "Set outgoing interface automatically.", "label": "Auto", "name": "auto"}, {"description": "Set outgoing interface by SD-WAN or policy routing rules", "help": "Set outgoing interface by SD-WAN or policy routing rules.", "label": "Sdwan", "name": "sdwan"}, {"description": "Set outgoing interface manually", "help": "Set outgoing interface manually.", "label": "Specify", "name": "specify"}] | None = ...,
        interface: str | None = ...,
        vrf_select: int | None = ...,
        enc_algorithm: Literal[{"description": "SSL communication with high and medium encryption algorithms", "help": "SSL communication with high and medium encryption algorithms.", "label": "Default", "name": "default"}, {"description": "SSL communication with high encryption algorithms", "help": "SSL communication with high encryption algorithms.", "label": "High", "name": "high"}, {"description": "SSL communication with low encryption algorithms", "help": "SSL communication with low encryption algorithms.", "label": "Low", "name": "low"}] | None = ...,
        ssl_min_proto_version: Literal[{"description": "Follow system global setting", "help": "Follow system global setting.", "label": "Default", "name": "default"}, {"description": "SSLv3", "help": "SSLv3.", "label": "Sslv3", "name": "SSLv3"}, {"description": "TLSv1", "help": "TLSv1.", "label": "Tlsv1", "name": "TLSv1"}, {"description": "TLSv1", "help": "TLSv1.1.", "label": "Tlsv1 1", "name": "TLSv1-1"}, {"description": "TLSv1", "help": "TLSv1.2.", "label": "Tlsv1 2", "name": "TLSv1-2"}, {"description": "TLSv1", "help": "TLSv1.3.", "label": "Tlsv1 3", "name": "TLSv1-3"}] | None = ...,
        email: str | None = ...,
        ca: str | None = ...,
        cn: str | None = ...,
        certificate_verification: Literal[{"description": "Enable identity verification of FortiSandbox by use of certificate", "help": "Enable identity verification of FortiSandbox by use of certificate.", "label": "Enable", "name": "enable"}, {"description": "Disable identity verification of FortiSandbox by use of certificate", "help": "Disable identity verification of FortiSandbox by use of certificate.", "label": "Disable", "name": "disable"}] | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: FortisandboxPayload | None = ...,
        status: Literal[{"description": "Enable FortiSandbox", "help": "Enable FortiSandbox.", "label": "Enable", "name": "enable"}, {"description": "Disable FortiSandbox", "help": "Disable FortiSandbox.", "label": "Disable", "name": "disable"}] | None = ...,
        forticloud: Literal[{"description": "Enable FortiSandbox Cloud", "help": "Enable FortiSandbox Cloud.", "label": "Enable", "name": "enable"}, {"description": "Disable FortiSandbox Cloud", "help": "Disable FortiSandbox Cloud.", "label": "Disable", "name": "disable"}] | None = ...,
        inline_scan: Literal[{"help": "Enable FortiSandbox inline scan.", "label": "Enable", "name": "enable"}, {"help": "Disable FortiSandbox inline scan.", "label": "Disable", "name": "disable"}] | None = ...,
        server: str | None = ...,
        source_ip: str | None = ...,
        interface_select_method: Literal[{"description": "Set outgoing interface automatically", "help": "Set outgoing interface automatically.", "label": "Auto", "name": "auto"}, {"description": "Set outgoing interface by SD-WAN or policy routing rules", "help": "Set outgoing interface by SD-WAN or policy routing rules.", "label": "Sdwan", "name": "sdwan"}, {"description": "Set outgoing interface manually", "help": "Set outgoing interface manually.", "label": "Specify", "name": "specify"}] | None = ...,
        interface: str | None = ...,
        vrf_select: int | None = ...,
        enc_algorithm: Literal[{"description": "SSL communication with high and medium encryption algorithms", "help": "SSL communication with high and medium encryption algorithms.", "label": "Default", "name": "default"}, {"description": "SSL communication with high encryption algorithms", "help": "SSL communication with high encryption algorithms.", "label": "High", "name": "high"}, {"description": "SSL communication with low encryption algorithms", "help": "SSL communication with low encryption algorithms.", "label": "Low", "name": "low"}] | None = ...,
        ssl_min_proto_version: Literal[{"description": "Follow system global setting", "help": "Follow system global setting.", "label": "Default", "name": "default"}, {"description": "SSLv3", "help": "SSLv3.", "label": "Sslv3", "name": "SSLv3"}, {"description": "TLSv1", "help": "TLSv1.", "label": "Tlsv1", "name": "TLSv1"}, {"description": "TLSv1", "help": "TLSv1.1.", "label": "Tlsv1 1", "name": "TLSv1-1"}, {"description": "TLSv1", "help": "TLSv1.2.", "label": "Tlsv1 2", "name": "TLSv1-2"}, {"description": "TLSv1", "help": "TLSv1.3.", "label": "Tlsv1 3", "name": "TLSv1-3"}] | None = ...,
        email: str | None = ...,
        ca: str | None = ...,
        cn: str | None = ...,
        certificate_verification: Literal[{"description": "Enable identity verification of FortiSandbox by use of certificate", "help": "Enable identity verification of FortiSandbox by use of certificate.", "label": "Enable", "name": "enable"}, {"description": "Disable identity verification of FortiSandbox by use of certificate", "help": "Disable identity verification of FortiSandbox by use of certificate.", "label": "Disable", "name": "disable"}] | None = ...,
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
        payload_dict: FortisandboxPayload | None = ...,
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
    "Fortisandbox",
    "FortisandboxPayload",
]