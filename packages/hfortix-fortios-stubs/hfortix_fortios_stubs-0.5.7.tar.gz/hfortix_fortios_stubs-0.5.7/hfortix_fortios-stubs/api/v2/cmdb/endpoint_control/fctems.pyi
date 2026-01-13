from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class FctemsPayload(TypedDict, total=False):
    """
    Type hints for endpoint_control/fctems payload fields.
    
    Configure FortiClient Enterprise Management Server (EMS) entries.
    
    **Related Resources:**

    Dependencies (resources this endpoint references):
        - :class:`~.certificate.ca.CaEndpoint` (via: verifying-ca)
        - :class:`~.system.interface.InterfaceEndpoint` (via: interface)
        - :class:`~.vpn.certificate.ca.CaEndpoint` (via: verifying-ca)

    **Usage:**
        payload: FctemsPayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    ems_id: NotRequired[int]  # EMS ID in order (1 - 7).
    status: NotRequired[Literal[{"description": "Enable EMS configuration and operation", "help": "Enable EMS configuration and operation.", "label": "Enable", "name": "enable"}, {"description": "Disable EMS configuration and operation", "help": "Disable EMS configuration and operation.", "label": "Disable", "name": "disable"}]]  # Enable or disable this EMS configuration.
    name: NotRequired[str]  # FortiClient Enterprise Management Server (EMS) name.
    dirty_reason: NotRequired[Literal[{"description": "FortiClient EMS entry not dirty", "help": "FortiClient EMS entry not dirty.", "label": "None", "name": "none"}, {"description": "FortiClient EMS entry dirty because EMS SN is mismatched with configured SN", "help": "FortiClient EMS entry dirty because EMS SN is mismatched with configured SN.", "label": "Mismatched Ems Sn", "name": "mismatched-ems-sn"}]]  # Dirty Reason for FortiClient EMS.
    fortinetone_cloud_authentication: NotRequired[Literal[{"description": "Enable authentication of FortiClient EMS Cloud through FortiCloud account", "help": "Enable authentication of FortiClient EMS Cloud through FortiCloud account.", "label": "Enable", "name": "enable"}, {"description": "Disable authentication of FortiClient EMS Cloud through FortiCloud account", "help": "Disable authentication of FortiClient EMS Cloud through FortiCloud account.", "label": "Disable", "name": "disable"}]]  # Enable/disable authentication of FortiClient EMS Cloud throu
    cloud_authentication_access_key: NotRequired[str]  # FortiClient EMS Cloud multitenancy access key
    server: NotRequired[str]  # FortiClient EMS FQDN or IPv4 address.
    https_port: NotRequired[int]  # FortiClient EMS HTTPS access port number. (1 - 65535, defaul
    serial_number: NotRequired[str]  # EMS Serial Number.
    tenant_id: NotRequired[str]  # EMS Tenant ID.
    source_ip: NotRequired[str]  # REST API call source IP.
    pull_sysinfo: NotRequired[Literal[{"description": "Enable pulling FortiClient user SysInfo from EMS", "help": "Enable pulling FortiClient user SysInfo from EMS.", "label": "Enable", "name": "enable"}, {"description": "Disable pulling FortiClient user SysInfo from EMS", "help": "Disable pulling FortiClient user SysInfo from EMS.", "label": "Disable", "name": "disable"}]]  # Enable/disable pulling SysInfo from EMS.
    pull_vulnerabilities: NotRequired[Literal[{"description": "Enable pulling client vulnerabilities from EMS", "help": "Enable pulling client vulnerabilities from EMS.", "label": "Enable", "name": "enable"}, {"description": "Disable pulling client vulnerabilities from EMS", "help": "Disable pulling client vulnerabilities from EMS.", "label": "Disable", "name": "disable"}]]  # Enable/disable pulling vulnerabilities from EMS.
    pull_tags: NotRequired[Literal[{"description": "Enable pulling FortiClient user tags from EMS", "help": "Enable pulling FortiClient user tags from EMS.", "label": "Enable", "name": "enable"}, {"description": "Disable pulling FortiClient user tags from EMS", "help": "Disable pulling FortiClient user tags from EMS.", "label": "Disable", "name": "disable"}]]  # Enable/disable pulling FortiClient user tags from EMS.
    pull_malware_hash: NotRequired[Literal[{"description": "Enable pulling FortiClient malware hash from EMS", "help": "Enable pulling FortiClient malware hash from EMS.", "label": "Enable", "name": "enable"}, {"description": "Disable pulling FortiClient malware hash from EMS", "help": "Disable pulling FortiClient malware hash from EMS.", "label": "Disable", "name": "disable"}]]  # Enable/disable pulling FortiClient malware hash from EMS.
    capabilities: NotRequired[Literal[{"description": "Allow this FortiGate unit to load the authentication page provided by EMS to authenticate itself with EMS", "help": "Allow this FortiGate unit to load the authentication page provided by EMS to authenticate itself with EMS.", "label": "Fabric Auth", "name": "fabric-auth"}, {"description": "Allow silent approval of non-root or FortiGate HA clusters on EMS in the Security Fabric", "help": "Allow silent approval of non-root or FortiGate HA clusters on EMS in the Security Fabric.", "label": "Silent Approval", "name": "silent-approval"}, {"description": "Enable/disable websockets for this FortiGate unit", "help": "Enable/disable websockets for this FortiGate unit. Override behavior using websocket-override.", "label": "Websocket", "name": "websocket"}, {"description": "Allow this FortiGate unit to request malware hash notifications over websocket", "help": "Allow this FortiGate unit to request malware hash notifications over websocket.", "label": "Websocket Malware", "name": "websocket-malware"}, {"description": "Enable/disable syncing deep inspection certificates with EMS", "help": "Enable/disable syncing deep inspection certificates with EMS.", "label": "Push Ca Certs", "name": "push-ca-certs"}, {"description": "Can recieve tag information from New Common Tags API from EMS", "help": "Can recieve tag information from New Common Tags API from EMS.", "label": "Common Tags Api", "name": "common-tags-api"}, {"description": "Allow this FortiGate to retrieve Tenant-ID from EMS", "help": "Allow this FortiGate to retrieve Tenant-ID from EMS.", "label": "Tenant Id", "name": "tenant-id"}, {"description": "Allow this FortiGate to retrieve avatars from EMS by fingerprint", "help": "Allow this FortiGate to retrieve avatars from EMS by fingerprint.", "label": "Client Avatars", "name": "client-avatars"}, {"description": "Allow this FortiGate to create a vdom connector to EMS", "help": "Allow this FortiGate to create a vdom connector to EMS.", "label": "Single Vdom Connector", "name": "single-vdom-connector"}, {"description": "Allow this FortiGate to send additional info to EMS", "help": "Allow this FortiGate to send additional info to EMS.", "label": "Fgt Sysinfo Api", "name": "fgt-sysinfo-api"}, {"description": "Allow this FortiGate to send vdom\u0027s ZTNA server information to EMS", "help": "Allow this FortiGate to send vdom\u0027s ZTNA server information to EMS.", "label": "Ztna Server Info", "name": "ztna-server-info"}, {"description": "Allow this FortiGate to send used tags information to EMS", "help": "Allow this FortiGate to send used tags information to EMS.", "label": "Used Tags", "name": "used-tags"}]]  # List of EMS capabilities.
    call_timeout: NotRequired[int]  # FortiClient EMS call timeout in seconds (1 - 180 seconds, de
    out_of_sync_threshold: NotRequired[int]  # Outdated resource threshold in seconds (10 - 3600, default =
    send_tags_to_all_vdoms: NotRequired[Literal[{"help": "Enable sending tags to all vdoms.", "label": "Enable", "name": "enable"}, {"description": "Disable sending tags to all vdoms", "help": "Disable sending tags to all vdoms.", "label": "Disable", "name": "disable"}]]  # Relax restrictions on tags to send all EMS tags to all VDOMs
    websocket_override: NotRequired[Literal[{"description": "Do not override the WebSocket connection", "help": "Do not override the WebSocket connection. Connect to WebSocket of this EMS server if it is capable (default).", "label": "Enable", "name": "enable"}, {"description": "Override the WebSocket connection", "help": "Override the WebSocket connection. Do not connect to WebSocket even if EMS is capable of a WebSocket connection.", "label": "Disable", "name": "disable"}]]  # Enable/disable override behavior for how this FortiGate unit
    interface_select_method: NotRequired[Literal[{"description": "Set outgoing interface automatically", "help": "Set outgoing interface automatically.", "label": "Auto", "name": "auto"}, {"description": "Set outgoing interface by SD-WAN or policy routing rules", "help": "Set outgoing interface by SD-WAN or policy routing rules.", "label": "Sdwan", "name": "sdwan"}, {"description": "Set outgoing interface manually", "help": "Set outgoing interface manually.", "label": "Specify", "name": "specify"}]]  # Specify how to select outgoing interface to reach server.
    interface: str  # Specify outgoing interface to reach server.
    trust_ca_cn: NotRequired[Literal[{"description": "Trust EMS certificate CA \u0026 CN to automatically renew certificate", "help": "Trust EMS certificate CA \u0026 CN to automatically renew certificate.", "label": "Enable", "name": "enable"}, {"description": "Do not trust EMS certificate CA \u0026 CN to automatically renew certificate", "help": "Do not trust EMS certificate CA \u0026 CN to automatically renew certificate.", "label": "Disable", "name": "disable"}]]  # Enable/disable trust of the EMS certificate issuer(CA) and c
    verifying_ca: NotRequired[str]  # Lowest CA cert on Fortigate in verified EMS cert chain.


class Fctems:
    """
    Configure FortiClient Enterprise Management Server (EMS) entries.
    
    Path: endpoint_control/fctems
    Category: cmdb
    Primary Key: ems-id
    """
    
    # Overloads for get() with response_mode="object"
    @overload
    def get(
        self,
        ems_id: int | None = ...,
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
        ems_id: int,
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
        ems_id: int | None = ...,
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
        ems_id: int | None = ...,
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
        ems_id: int | None = ...,
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
        payload_dict: FctemsPayload | None = ...,
        ems_id: int | None = ...,
        status: Literal[{"description": "Enable EMS configuration and operation", "help": "Enable EMS configuration and operation.", "label": "Enable", "name": "enable"}, {"description": "Disable EMS configuration and operation", "help": "Disable EMS configuration and operation.", "label": "Disable", "name": "disable"}] | None = ...,
        name: str | None = ...,
        dirty_reason: Literal[{"description": "FortiClient EMS entry not dirty", "help": "FortiClient EMS entry not dirty.", "label": "None", "name": "none"}, {"description": "FortiClient EMS entry dirty because EMS SN is mismatched with configured SN", "help": "FortiClient EMS entry dirty because EMS SN is mismatched with configured SN.", "label": "Mismatched Ems Sn", "name": "mismatched-ems-sn"}] | None = ...,
        fortinetone_cloud_authentication: Literal[{"description": "Enable authentication of FortiClient EMS Cloud through FortiCloud account", "help": "Enable authentication of FortiClient EMS Cloud through FortiCloud account.", "label": "Enable", "name": "enable"}, {"description": "Disable authentication of FortiClient EMS Cloud through FortiCloud account", "help": "Disable authentication of FortiClient EMS Cloud through FortiCloud account.", "label": "Disable", "name": "disable"}] | None = ...,
        cloud_authentication_access_key: str | None = ...,
        server: str | None = ...,
        https_port: int | None = ...,
        serial_number: str | None = ...,
        tenant_id: str | None = ...,
        source_ip: str | None = ...,
        pull_sysinfo: Literal[{"description": "Enable pulling FortiClient user SysInfo from EMS", "help": "Enable pulling FortiClient user SysInfo from EMS.", "label": "Enable", "name": "enable"}, {"description": "Disable pulling FortiClient user SysInfo from EMS", "help": "Disable pulling FortiClient user SysInfo from EMS.", "label": "Disable", "name": "disable"}] | None = ...,
        pull_vulnerabilities: Literal[{"description": "Enable pulling client vulnerabilities from EMS", "help": "Enable pulling client vulnerabilities from EMS.", "label": "Enable", "name": "enable"}, {"description": "Disable pulling client vulnerabilities from EMS", "help": "Disable pulling client vulnerabilities from EMS.", "label": "Disable", "name": "disable"}] | None = ...,
        pull_tags: Literal[{"description": "Enable pulling FortiClient user tags from EMS", "help": "Enable pulling FortiClient user tags from EMS.", "label": "Enable", "name": "enable"}, {"description": "Disable pulling FortiClient user tags from EMS", "help": "Disable pulling FortiClient user tags from EMS.", "label": "Disable", "name": "disable"}] | None = ...,
        pull_malware_hash: Literal[{"description": "Enable pulling FortiClient malware hash from EMS", "help": "Enable pulling FortiClient malware hash from EMS.", "label": "Enable", "name": "enable"}, {"description": "Disable pulling FortiClient malware hash from EMS", "help": "Disable pulling FortiClient malware hash from EMS.", "label": "Disable", "name": "disable"}] | None = ...,
        capabilities: Literal[{"description": "Allow this FortiGate unit to load the authentication page provided by EMS to authenticate itself with EMS", "help": "Allow this FortiGate unit to load the authentication page provided by EMS to authenticate itself with EMS.", "label": "Fabric Auth", "name": "fabric-auth"}, {"description": "Allow silent approval of non-root or FortiGate HA clusters on EMS in the Security Fabric", "help": "Allow silent approval of non-root or FortiGate HA clusters on EMS in the Security Fabric.", "label": "Silent Approval", "name": "silent-approval"}, {"description": "Enable/disable websockets for this FortiGate unit", "help": "Enable/disable websockets for this FortiGate unit. Override behavior using websocket-override.", "label": "Websocket", "name": "websocket"}, {"description": "Allow this FortiGate unit to request malware hash notifications over websocket", "help": "Allow this FortiGate unit to request malware hash notifications over websocket.", "label": "Websocket Malware", "name": "websocket-malware"}, {"description": "Enable/disable syncing deep inspection certificates with EMS", "help": "Enable/disable syncing deep inspection certificates with EMS.", "label": "Push Ca Certs", "name": "push-ca-certs"}, {"description": "Can recieve tag information from New Common Tags API from EMS", "help": "Can recieve tag information from New Common Tags API from EMS.", "label": "Common Tags Api", "name": "common-tags-api"}, {"description": "Allow this FortiGate to retrieve Tenant-ID from EMS", "help": "Allow this FortiGate to retrieve Tenant-ID from EMS.", "label": "Tenant Id", "name": "tenant-id"}, {"description": "Allow this FortiGate to retrieve avatars from EMS by fingerprint", "help": "Allow this FortiGate to retrieve avatars from EMS by fingerprint.", "label": "Client Avatars", "name": "client-avatars"}, {"description": "Allow this FortiGate to create a vdom connector to EMS", "help": "Allow this FortiGate to create a vdom connector to EMS.", "label": "Single Vdom Connector", "name": "single-vdom-connector"}, {"description": "Allow this FortiGate to send additional info to EMS", "help": "Allow this FortiGate to send additional info to EMS.", "label": "Fgt Sysinfo Api", "name": "fgt-sysinfo-api"}, {"description": "Allow this FortiGate to send vdom\u0027s ZTNA server information to EMS", "help": "Allow this FortiGate to send vdom\u0027s ZTNA server information to EMS.", "label": "Ztna Server Info", "name": "ztna-server-info"}, {"description": "Allow this FortiGate to send used tags information to EMS", "help": "Allow this FortiGate to send used tags information to EMS.", "label": "Used Tags", "name": "used-tags"}] | None = ...,
        call_timeout: int | None = ...,
        out_of_sync_threshold: int | None = ...,
        send_tags_to_all_vdoms: Literal[{"help": "Enable sending tags to all vdoms.", "label": "Enable", "name": "enable"}, {"description": "Disable sending tags to all vdoms", "help": "Disable sending tags to all vdoms.", "label": "Disable", "name": "disable"}] | None = ...,
        websocket_override: Literal[{"description": "Do not override the WebSocket connection", "help": "Do not override the WebSocket connection. Connect to WebSocket of this EMS server if it is capable (default).", "label": "Enable", "name": "enable"}, {"description": "Override the WebSocket connection", "help": "Override the WebSocket connection. Do not connect to WebSocket even if EMS is capable of a WebSocket connection.", "label": "Disable", "name": "disable"}] | None = ...,
        interface_select_method: Literal[{"description": "Set outgoing interface automatically", "help": "Set outgoing interface automatically.", "label": "Auto", "name": "auto"}, {"description": "Set outgoing interface by SD-WAN or policy routing rules", "help": "Set outgoing interface by SD-WAN or policy routing rules.", "label": "Sdwan", "name": "sdwan"}, {"description": "Set outgoing interface manually", "help": "Set outgoing interface manually.", "label": "Specify", "name": "specify"}] | None = ...,
        interface: str | None = ...,
        trust_ca_cn: Literal[{"description": "Trust EMS certificate CA \u0026 CN to automatically renew certificate", "help": "Trust EMS certificate CA \u0026 CN to automatically renew certificate.", "label": "Enable", "name": "enable"}, {"description": "Do not trust EMS certificate CA \u0026 CN to automatically renew certificate", "help": "Do not trust EMS certificate CA \u0026 CN to automatically renew certificate.", "label": "Disable", "name": "disable"}] | None = ...,
        verifying_ca: str | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: FctemsPayload | None = ...,
        ems_id: int | None = ...,
        status: Literal[{"description": "Enable EMS configuration and operation", "help": "Enable EMS configuration and operation.", "label": "Enable", "name": "enable"}, {"description": "Disable EMS configuration and operation", "help": "Disable EMS configuration and operation.", "label": "Disable", "name": "disable"}] | None = ...,
        name: str | None = ...,
        dirty_reason: Literal[{"description": "FortiClient EMS entry not dirty", "help": "FortiClient EMS entry not dirty.", "label": "None", "name": "none"}, {"description": "FortiClient EMS entry dirty because EMS SN is mismatched with configured SN", "help": "FortiClient EMS entry dirty because EMS SN is mismatched with configured SN.", "label": "Mismatched Ems Sn", "name": "mismatched-ems-sn"}] | None = ...,
        fortinetone_cloud_authentication: Literal[{"description": "Enable authentication of FortiClient EMS Cloud through FortiCloud account", "help": "Enable authentication of FortiClient EMS Cloud through FortiCloud account.", "label": "Enable", "name": "enable"}, {"description": "Disable authentication of FortiClient EMS Cloud through FortiCloud account", "help": "Disable authentication of FortiClient EMS Cloud through FortiCloud account.", "label": "Disable", "name": "disable"}] | None = ...,
        cloud_authentication_access_key: str | None = ...,
        server: str | None = ...,
        https_port: int | None = ...,
        serial_number: str | None = ...,
        tenant_id: str | None = ...,
        source_ip: str | None = ...,
        pull_sysinfo: Literal[{"description": "Enable pulling FortiClient user SysInfo from EMS", "help": "Enable pulling FortiClient user SysInfo from EMS.", "label": "Enable", "name": "enable"}, {"description": "Disable pulling FortiClient user SysInfo from EMS", "help": "Disable pulling FortiClient user SysInfo from EMS.", "label": "Disable", "name": "disable"}] | None = ...,
        pull_vulnerabilities: Literal[{"description": "Enable pulling client vulnerabilities from EMS", "help": "Enable pulling client vulnerabilities from EMS.", "label": "Enable", "name": "enable"}, {"description": "Disable pulling client vulnerabilities from EMS", "help": "Disable pulling client vulnerabilities from EMS.", "label": "Disable", "name": "disable"}] | None = ...,
        pull_tags: Literal[{"description": "Enable pulling FortiClient user tags from EMS", "help": "Enable pulling FortiClient user tags from EMS.", "label": "Enable", "name": "enable"}, {"description": "Disable pulling FortiClient user tags from EMS", "help": "Disable pulling FortiClient user tags from EMS.", "label": "Disable", "name": "disable"}] | None = ...,
        pull_malware_hash: Literal[{"description": "Enable pulling FortiClient malware hash from EMS", "help": "Enable pulling FortiClient malware hash from EMS.", "label": "Enable", "name": "enable"}, {"description": "Disable pulling FortiClient malware hash from EMS", "help": "Disable pulling FortiClient malware hash from EMS.", "label": "Disable", "name": "disable"}] | None = ...,
        capabilities: Literal[{"description": "Allow this FortiGate unit to load the authentication page provided by EMS to authenticate itself with EMS", "help": "Allow this FortiGate unit to load the authentication page provided by EMS to authenticate itself with EMS.", "label": "Fabric Auth", "name": "fabric-auth"}, {"description": "Allow silent approval of non-root or FortiGate HA clusters on EMS in the Security Fabric", "help": "Allow silent approval of non-root or FortiGate HA clusters on EMS in the Security Fabric.", "label": "Silent Approval", "name": "silent-approval"}, {"description": "Enable/disable websockets for this FortiGate unit", "help": "Enable/disable websockets for this FortiGate unit. Override behavior using websocket-override.", "label": "Websocket", "name": "websocket"}, {"description": "Allow this FortiGate unit to request malware hash notifications over websocket", "help": "Allow this FortiGate unit to request malware hash notifications over websocket.", "label": "Websocket Malware", "name": "websocket-malware"}, {"description": "Enable/disable syncing deep inspection certificates with EMS", "help": "Enable/disable syncing deep inspection certificates with EMS.", "label": "Push Ca Certs", "name": "push-ca-certs"}, {"description": "Can recieve tag information from New Common Tags API from EMS", "help": "Can recieve tag information from New Common Tags API from EMS.", "label": "Common Tags Api", "name": "common-tags-api"}, {"description": "Allow this FortiGate to retrieve Tenant-ID from EMS", "help": "Allow this FortiGate to retrieve Tenant-ID from EMS.", "label": "Tenant Id", "name": "tenant-id"}, {"description": "Allow this FortiGate to retrieve avatars from EMS by fingerprint", "help": "Allow this FortiGate to retrieve avatars from EMS by fingerprint.", "label": "Client Avatars", "name": "client-avatars"}, {"description": "Allow this FortiGate to create a vdom connector to EMS", "help": "Allow this FortiGate to create a vdom connector to EMS.", "label": "Single Vdom Connector", "name": "single-vdom-connector"}, {"description": "Allow this FortiGate to send additional info to EMS", "help": "Allow this FortiGate to send additional info to EMS.", "label": "Fgt Sysinfo Api", "name": "fgt-sysinfo-api"}, {"description": "Allow this FortiGate to send vdom\u0027s ZTNA server information to EMS", "help": "Allow this FortiGate to send vdom\u0027s ZTNA server information to EMS.", "label": "Ztna Server Info", "name": "ztna-server-info"}, {"description": "Allow this FortiGate to send used tags information to EMS", "help": "Allow this FortiGate to send used tags information to EMS.", "label": "Used Tags", "name": "used-tags"}] | None = ...,
        call_timeout: int | None = ...,
        out_of_sync_threshold: int | None = ...,
        send_tags_to_all_vdoms: Literal[{"help": "Enable sending tags to all vdoms.", "label": "Enable", "name": "enable"}, {"description": "Disable sending tags to all vdoms", "help": "Disable sending tags to all vdoms.", "label": "Disable", "name": "disable"}] | None = ...,
        websocket_override: Literal[{"description": "Do not override the WebSocket connection", "help": "Do not override the WebSocket connection. Connect to WebSocket of this EMS server if it is capable (default).", "label": "Enable", "name": "enable"}, {"description": "Override the WebSocket connection", "help": "Override the WebSocket connection. Do not connect to WebSocket even if EMS is capable of a WebSocket connection.", "label": "Disable", "name": "disable"}] | None = ...,
        interface_select_method: Literal[{"description": "Set outgoing interface automatically", "help": "Set outgoing interface automatically.", "label": "Auto", "name": "auto"}, {"description": "Set outgoing interface by SD-WAN or policy routing rules", "help": "Set outgoing interface by SD-WAN or policy routing rules.", "label": "Sdwan", "name": "sdwan"}, {"description": "Set outgoing interface manually", "help": "Set outgoing interface manually.", "label": "Specify", "name": "specify"}] | None = ...,
        interface: str | None = ...,
        trust_ca_cn: Literal[{"description": "Trust EMS certificate CA \u0026 CN to automatically renew certificate", "help": "Trust EMS certificate CA \u0026 CN to automatically renew certificate.", "label": "Enable", "name": "enable"}, {"description": "Do not trust EMS certificate CA \u0026 CN to automatically renew certificate", "help": "Do not trust EMS certificate CA \u0026 CN to automatically renew certificate.", "label": "Disable", "name": "disable"}] | None = ...,
        verifying_ca: str | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def delete(
        self,
        ems_id: int | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def exists(
        self,
        ems_id: int,
        vdom: str | bool | None = ...,
    ) -> Union[bool, Coroutine[Any, Any, bool]]: ...
    
    def set(
        self,
        payload_dict: FctemsPayload | None = ...,
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
    "Fctems",
    "FctemsPayload",
]