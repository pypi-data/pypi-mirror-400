from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class ExternalResourcePayload(TypedDict, total=False):
    """
    Type hints for system/external_resource payload fields.
    
    Configure external resource.
    
    **Related Resources:**

    Dependencies (resources this endpoint references):
        - :class:`~.system.interface.InterfaceEndpoint` (via: interface, source-ip-interface)
        - :class:`~.vpn.certificate.local.LocalEndpoint` (via: client-cert)

    **Usage:**
        payload: ExternalResourcePayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    name: str  # External resource name.
    uuid: NotRequired[str]  # Universally Unique Identifier (UUID; automatically assigned 
    status: NotRequired[Literal[{"description": "Enable user resource", "help": "Enable user resource.", "label": "Enable", "name": "enable"}, {"description": "Disable user resource", "help": "Disable user resource.", "label": "Disable", "name": "disable"}]]  # Enable/disable user resource.
    type: NotRequired[Literal[{"description": "FortiGuard category", "help": "FortiGuard category.", "label": "Category", "name": "category"}, {"description": "Domain Name", "help": "Domain Name.", "label": "Domain", "name": "domain"}, {"description": "Malware hash", "help": "Malware hash.", "label": "Malware", "name": "malware"}, {"description": "Firewall IP address", "help": "Firewall IP address.", "label": "Address", "name": "address"}, {"description": "Firewall MAC address", "help": "Firewall MAC address.", "label": "Mac Address", "name": "mac-address"}, {"description": "Data file", "help": "Data file.", "label": "Data", "name": "data"}, {"description": "Generic addresses", "help": "Generic addresses.", "label": "Generic Address", "name": "generic-address"}]]  # User resource type.
    namespace: NotRequired[str]  # Generic external connector address namespace.
    object_array_path: NotRequired[str]  # JSON Path to array of generic addresses in resource.
    address_name_field: NotRequired[str]  # JSON Path to address name in generic address entry.
    address_data_field: NotRequired[str]  # JSON Path to address data in generic address entry.
    address_comment_field: NotRequired[str]  # JSON Path to address description in generic address entry.
    update_method: NotRequired[Literal[{"description": "FortiGate unit will pull update from the external resource", "help": "FortiGate unit will pull update from the external resource.", "label": "Feed", "name": "feed"}, {"description": "External Resource update is pushed to the FortiGate unit through the FortiGate unit\u0027s RESTAPI/CLI", "help": "External Resource update is pushed to the FortiGate unit through the FortiGate unit\u0027s RESTAPI/CLI.", "label": "Push", "name": "push"}]]  # External resource update method.
    category: NotRequired[int]  # User resource category.
    username: NotRequired[str]  # HTTP basic authentication user name.
    password: NotRequired[str]  # HTTP basic authentication password.
    client_cert_auth: NotRequired[Literal[{"description": "Enable using client certificate for TLS authentication", "help": "Enable using client certificate for TLS authentication.", "label": "Enable", "name": "enable"}, {"description": "Disable using client certificate for TLS authentication", "help": "Disable using client certificate for TLS authentication.", "label": "Disable", "name": "disable"}]]  # Enable/disable using client certificate for TLS authenticati
    client_cert: NotRequired[str]  # Client certificate name.
    comments: NotRequired[str]  # Comment.
    resource: str  # URL of external resource.
    user_agent: NotRequired[str]  # HTTP User-Agent header (default = 'curl/7.58.0').
    server_identity_check: NotRequired[Literal[{"description": "No certificate verification", "help": "No certificate verification.", "label": "None", "name": "none"}, {"description": "Check server certifcate only", "help": "Check server certifcate only.", "label": "Basic", "name": "basic"}, {"description": "Check server certificate and verify the domain matches in the server certificate", "help": "Check server certificate and verify the domain matches in the server certificate.", "label": "Full", "name": "full"}]]  # Certificate verification option.
    refresh_rate: int  # Time interval to refresh external resource (1 - 43200 min, d
    source_ip: NotRequired[str]  # Source IPv4 address used to communicate with server.
    source_ip_interface: NotRequired[str]  # IPv4 Source interface for communication with the server.
    interface_select_method: NotRequired[Literal[{"description": "Set outgoing interface automatically", "help": "Set outgoing interface automatically.", "label": "Auto", "name": "auto"}, {"description": "Set outgoing interface by SD-WAN or policy routing rules", "help": "Set outgoing interface by SD-WAN or policy routing rules.", "label": "Sdwan", "name": "sdwan"}, {"description": "Set outgoing interface manually", "help": "Set outgoing interface manually.", "label": "Specify", "name": "specify"}]]  # Specify how to select outgoing interface to reach server.
    interface: str  # Specify outgoing interface to reach server.
    vrf_select: NotRequired[int]  # VRF ID used for connection to server.


class ExternalResource:
    """
    Configure external resource.
    
    Path: system/external_resource
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
        payload_dict: ExternalResourcePayload | None = ...,
        name: str | None = ...,
        uuid: str | None = ...,
        status: Literal[{"description": "Enable user resource", "help": "Enable user resource.", "label": "Enable", "name": "enable"}, {"description": "Disable user resource", "help": "Disable user resource.", "label": "Disable", "name": "disable"}] | None = ...,
        type: Literal[{"description": "FortiGuard category", "help": "FortiGuard category.", "label": "Category", "name": "category"}, {"description": "Domain Name", "help": "Domain Name.", "label": "Domain", "name": "domain"}, {"description": "Malware hash", "help": "Malware hash.", "label": "Malware", "name": "malware"}, {"description": "Firewall IP address", "help": "Firewall IP address.", "label": "Address", "name": "address"}, {"description": "Firewall MAC address", "help": "Firewall MAC address.", "label": "Mac Address", "name": "mac-address"}, {"description": "Data file", "help": "Data file.", "label": "Data", "name": "data"}, {"description": "Generic addresses", "help": "Generic addresses.", "label": "Generic Address", "name": "generic-address"}] | None = ...,
        namespace: str | None = ...,
        object_array_path: str | None = ...,
        address_name_field: str | None = ...,
        address_data_field: str | None = ...,
        address_comment_field: str | None = ...,
        update_method: Literal[{"description": "FortiGate unit will pull update from the external resource", "help": "FortiGate unit will pull update from the external resource.", "label": "Feed", "name": "feed"}, {"description": "External Resource update is pushed to the FortiGate unit through the FortiGate unit\u0027s RESTAPI/CLI", "help": "External Resource update is pushed to the FortiGate unit through the FortiGate unit\u0027s RESTAPI/CLI.", "label": "Push", "name": "push"}] | None = ...,
        category: int | None = ...,
        username: str | None = ...,
        password: str | None = ...,
        client_cert_auth: Literal[{"description": "Enable using client certificate for TLS authentication", "help": "Enable using client certificate for TLS authentication.", "label": "Enable", "name": "enable"}, {"description": "Disable using client certificate for TLS authentication", "help": "Disable using client certificate for TLS authentication.", "label": "Disable", "name": "disable"}] | None = ...,
        client_cert: str | None = ...,
        comments: str | None = ...,
        resource: str | None = ...,
        user_agent: str | None = ...,
        server_identity_check: Literal[{"description": "No certificate verification", "help": "No certificate verification.", "label": "None", "name": "none"}, {"description": "Check server certifcate only", "help": "Check server certifcate only.", "label": "Basic", "name": "basic"}, {"description": "Check server certificate and verify the domain matches in the server certificate", "help": "Check server certificate and verify the domain matches in the server certificate.", "label": "Full", "name": "full"}] | None = ...,
        refresh_rate: int | None = ...,
        source_ip: str | None = ...,
        source_ip_interface: str | None = ...,
        interface_select_method: Literal[{"description": "Set outgoing interface automatically", "help": "Set outgoing interface automatically.", "label": "Auto", "name": "auto"}, {"description": "Set outgoing interface by SD-WAN or policy routing rules", "help": "Set outgoing interface by SD-WAN or policy routing rules.", "label": "Sdwan", "name": "sdwan"}, {"description": "Set outgoing interface manually", "help": "Set outgoing interface manually.", "label": "Specify", "name": "specify"}] | None = ...,
        interface: str | None = ...,
        vrf_select: int | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: ExternalResourcePayload | None = ...,
        name: str | None = ...,
        uuid: str | None = ...,
        status: Literal[{"description": "Enable user resource", "help": "Enable user resource.", "label": "Enable", "name": "enable"}, {"description": "Disable user resource", "help": "Disable user resource.", "label": "Disable", "name": "disable"}] | None = ...,
        type: Literal[{"description": "FortiGuard category", "help": "FortiGuard category.", "label": "Category", "name": "category"}, {"description": "Domain Name", "help": "Domain Name.", "label": "Domain", "name": "domain"}, {"description": "Malware hash", "help": "Malware hash.", "label": "Malware", "name": "malware"}, {"description": "Firewall IP address", "help": "Firewall IP address.", "label": "Address", "name": "address"}, {"description": "Firewall MAC address", "help": "Firewall MAC address.", "label": "Mac Address", "name": "mac-address"}, {"description": "Data file", "help": "Data file.", "label": "Data", "name": "data"}, {"description": "Generic addresses", "help": "Generic addresses.", "label": "Generic Address", "name": "generic-address"}] | None = ...,
        namespace: str | None = ...,
        object_array_path: str | None = ...,
        address_name_field: str | None = ...,
        address_data_field: str | None = ...,
        address_comment_field: str | None = ...,
        update_method: Literal[{"description": "FortiGate unit will pull update from the external resource", "help": "FortiGate unit will pull update from the external resource.", "label": "Feed", "name": "feed"}, {"description": "External Resource update is pushed to the FortiGate unit through the FortiGate unit\u0027s RESTAPI/CLI", "help": "External Resource update is pushed to the FortiGate unit through the FortiGate unit\u0027s RESTAPI/CLI.", "label": "Push", "name": "push"}] | None = ...,
        category: int | None = ...,
        username: str | None = ...,
        password: str | None = ...,
        client_cert_auth: Literal[{"description": "Enable using client certificate for TLS authentication", "help": "Enable using client certificate for TLS authentication.", "label": "Enable", "name": "enable"}, {"description": "Disable using client certificate for TLS authentication", "help": "Disable using client certificate for TLS authentication.", "label": "Disable", "name": "disable"}] | None = ...,
        client_cert: str | None = ...,
        comments: str | None = ...,
        resource: str | None = ...,
        user_agent: str | None = ...,
        server_identity_check: Literal[{"description": "No certificate verification", "help": "No certificate verification.", "label": "None", "name": "none"}, {"description": "Check server certifcate only", "help": "Check server certifcate only.", "label": "Basic", "name": "basic"}, {"description": "Check server certificate and verify the domain matches in the server certificate", "help": "Check server certificate and verify the domain matches in the server certificate.", "label": "Full", "name": "full"}] | None = ...,
        refresh_rate: int | None = ...,
        source_ip: str | None = ...,
        source_ip_interface: str | None = ...,
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
        payload_dict: ExternalResourcePayload | None = ...,
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
    "ExternalResource",
    "ExternalResourcePayload",
]