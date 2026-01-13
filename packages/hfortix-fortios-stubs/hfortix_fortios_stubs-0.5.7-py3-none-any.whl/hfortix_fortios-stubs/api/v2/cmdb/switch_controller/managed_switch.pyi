from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class ManagedSwitchPayload(TypedDict, total=False):
    """
    Type hints for switch_controller/managed_switch payload fields.
    
    Configure FortiSwitch devices that are managed by this FortiGate.
    
    **Related Resources:**

    Dependencies (resources this endpoint references):
        - :class:`~.switch-controller.ptp.profile.ProfileEndpoint` (via: ptp-profile)
        - :class:`~.switch-controller.security-policy.local-access.LocalAccessEndpoint` (via: access-profile)
        - :class:`~.switch-controller.switch-profile.SwitchProfileEndpoint` (via: switch-profile)
        - :class:`~.system.interface.InterfaceEndpoint` (via: fsw-wan1-peer)

    **Usage:**
        payload: ManagedSwitchPayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    switch_id: str  # Managed-switch name.
    sn: str  # Managed-switch serial number.
    description: NotRequired[str]  # Description.
    switch_profile: NotRequired[str]  # FortiSwitch profile.
    access_profile: NotRequired[str]  # FortiSwitch access profile.
    purdue_level: NotRequired[Literal[{"description": "Level 1 - Basic Control    1", "help": "Level 1 - Basic Control", "label": "1", "name": "1"}, {"help": "Level 1.5", "label": "1.5", "name": "1.5"}, {"help": "Level 2 - Area Supervisory Control", "label": "2", "name": "2"}, {"help": "Level 2.5", "label": "2.5", "name": "2.5"}, {"help": "Level 3 - Operations \u0026 Control", "label": "3", "name": "3"}, {"help": "Level 3.5", "label": "3.5", "name": "3.5"}, {"help": "Level 4 - Business Planning \u0026 Logistics", "label": "4", "name": "4"}, {"description": "Level 5", "help": "Level 5 - Enterprise Network", "label": "5", "name": "5"}, {"help": "Level 5.5", "label": "5.5", "name": "5.5"}]]  # Purdue Level of this FortiSwitch.
    fsw_wan1_peer: str  # FortiSwitch WAN1 peer port.
    fsw_wan1_admin: NotRequired[Literal[{"description": "Link waiting to be authorized", "help": "Link waiting to be authorized.", "label": "Discovered", "name": "discovered"}, {"description": "Link unauthorized", "help": "Link unauthorized.", "label": "Disable", "name": "disable"}, {"description": "Link authorized", "help": "Link authorized.", "label": "Enable", "name": "enable"}]]  # FortiSwitch WAN1 admin status; enable to authorize the Forti
    poe_pre_standard_detection: NotRequired[Literal[{"description": "Enable PoE pre-standard detection", "help": "Enable PoE pre-standard detection.", "label": "Enable", "name": "enable"}, {"description": "Disable PoE pre-standard detection", "help": "Disable PoE pre-standard detection.", "label": "Disable", "name": "disable"}]]  # Enable/disable PoE pre-standard detection.
    dhcp_server_access_list: NotRequired[Literal[{"description": "Use global setting for DHCP snooping server access list", "help": "Use global setting for DHCP snooping server access list.", "label": "Global", "name": "global"}, {"description": "Override global setting and enable DHCP server access list", "help": "Override global setting and enable DHCP server access list.", "label": "Enable", "name": "enable"}, {"description": "Override global setting and disable DHCP server access list", "help": "Override global setting and disable DHCP server access list.", "label": "Disable", "name": "disable"}]]  # DHCP snooping server access list.
    poe_detection_type: NotRequired[int]  # PoE detection type for FortiSwitch.
    max_poe_budget: NotRequired[int]  # Max PoE budget for FortiSwitch.
    directly_connected: NotRequired[int]  # Directly connected FortiSwitch.
    version: NotRequired[int]  # FortiSwitch version.
    max_allowed_trunk_members: NotRequired[int]  # FortiSwitch maximum allowed trunk members.
    pre_provisioned: NotRequired[int]  # Pre-provisioned managed switch.
    l3_discovered: NotRequired[int]  # Layer 3 management discovered.
    mgmt_mode: NotRequired[int]  # FortiLink management mode.
    tunnel_discovered: NotRequired[int]  # SOCKS tunnel management discovered.
    tdr_supported: NotRequired[str]  # TDR supported.
    dynamic_capability: NotRequired[str]  # List of features this FortiSwitch supports (not configurable
    switch_device_tag: NotRequired[str]  # User definable label/tag.
    switch_dhcp_opt43_key: NotRequired[str]  # DHCP option43 key.
    mclag_igmp_snooping_aware: NotRequired[Literal[{"description": "Enable MCLAG IGMP-snooping awareness", "help": "Enable MCLAG IGMP-snooping awareness.", "label": "Enable", "name": "enable"}, {"description": "Disable MCLAG IGMP-snooping awareness", "help": "Disable MCLAG IGMP-snooping awareness.", "label": "Disable", "name": "disable"}]]  # Enable/disable MCLAG IGMP-snooping awareness.
    dynamically_discovered: NotRequired[int]  # Dynamically discovered FortiSwitch.
    ptp_status: NotRequired[Literal[{"description": "Disable PTP profile", "help": "Disable PTP profile.", "label": "Disable", "name": "disable"}, {"description": "Enable PTP profile", "help": "Enable PTP profile.", "label": "Enable", "name": "enable"}]]  # Enable/disable PTP profile on this FortiSwitch.
    ptp_profile: NotRequired[str]  # PTP profile configuration.
    radius_nas_ip_override: NotRequired[Literal[{"description": "Disable radius-nas-ip-override", "help": "Disable radius-nas-ip-override.", "label": "Disable", "name": "disable"}, {"description": "Enable radius-nas-ip-override", "help": "Enable radius-nas-ip-override.", "label": "Enable", "name": "enable"}]]  # Use locally defined NAS-IP.
    radius_nas_ip: str  # NAS-IP address.
    route_offload: NotRequired[Literal[{"description": "Disable route offload", "help": "Disable route offload.", "label": "Disable", "name": "disable"}, {"description": "Enable route offload", "help": "Enable route offload.", "label": "Enable", "name": "enable"}]]  # Enable/disable route offload on this FortiSwitch.
    route_offload_mclag: NotRequired[Literal[{"description": "Disable route offload MCLAG", "help": "Disable route offload MCLAG.", "label": "Disable", "name": "disable"}, {"description": "Enable route offload MCLAG", "help": "Enable route offload MCLAG.", "label": "Enable", "name": "enable"}]]  # Enable/disable route offload MCLAG on this FortiSwitch.
    route_offload_router: NotRequired[list[dict[str, Any]]]  # Configure route offload MCLAG IP address.
    vlan: NotRequired[list[dict[str, Any]]]  # Configure VLAN assignment priority.
    type: NotRequired[Literal[{"description": "Switch is of type virtual", "help": "Switch is of type virtual.", "label": "Virtual", "name": "virtual"}, {"description": "Switch is of type physical", "help": "Switch is of type physical.", "label": "Physical", "name": "physical"}]]  # Indication of switch type, physical or virtual.
    owner_vdom: NotRequired[str]  # VDOM which owner of port belongs to.
    flow_identity: NotRequired[str]  # Flow-tracking netflow ipfix switch identity in hex format(00
    staged_image_version: NotRequired[str]  # Staged image version for FortiSwitch.
    delayed_restart_trigger: NotRequired[int]  # Delayed restart triggered for this FortiSwitch.
    firmware_provision: NotRequired[Literal[{"description": "Enable firmware-provision", "help": "Enable firmware-provision.", "label": "Enable", "name": "enable"}, {"description": "Disable firmware-provision", "help": "Disable firmware-provision.", "label": "Disable", "name": "disable"}]]  # Enable/disable provisioning of firmware to FortiSwitches on 
    firmware_provision_version: NotRequired[str]  # Firmware version to provision to this FortiSwitch on bootup 
    firmware_provision_latest: NotRequired[Literal[{"description": "Do not automatically provision the latest available firmware", "help": "Do not automatically provision the latest available firmware.", "label": "Disable", "name": "disable"}, {"description": "Automatically attempt a one-time upgrade to the latest available firmware version", "help": "Automatically attempt a one-time upgrade to the latest available firmware version.", "label": "Once", "name": "once"}]]  # Enable/disable one-time automatic provisioning of the latest
    ports: NotRequired[list[dict[str, Any]]]  # Managed-switch port list.
    ip_source_guard: NotRequired[list[dict[str, Any]]]  # IP source guard.
    stp_settings: NotRequired[str]  # Configuration method to edit Spanning Tree Protocol (STP) se
    stp_instance: NotRequired[list[dict[str, Any]]]  # Configuration method to edit Spanning Tree Protocol (STP) in
    override_snmp_sysinfo: NotRequired[Literal[{"description": "Use the global SNMP system information", "help": "Use the global SNMP system information.", "label": "Disable", "name": "disable"}, {"description": "Override the global SNMP system information", "help": "Override the global SNMP system information.", "label": "Enable", "name": "enable"}]]  # Enable/disable overriding the global SNMP system information
    snmp_sysinfo: NotRequired[str]  # Configuration method to edit Simple Network Management Proto
    override_snmp_trap_threshold: NotRequired[Literal[{"description": "Override the global SNMP trap threshold values", "help": "Override the global SNMP trap threshold values.", "label": "Enable", "name": "enable"}, {"description": "Use the global SNMP trap threshold values", "help": "Use the global SNMP trap threshold values.", "label": "Disable", "name": "disable"}]]  # Enable/disable overriding the global SNMP trap threshold val
    snmp_trap_threshold: NotRequired[str]  # Configuration method to edit Simple Network Management Proto
    override_snmp_community: NotRequired[Literal[{"description": "Override the global SNMP communities", "help": "Override the global SNMP communities.", "label": "Enable", "name": "enable"}, {"description": "Use the global SNMP communities", "help": "Use the global SNMP communities.", "label": "Disable", "name": "disable"}]]  # Enable/disable overriding the global SNMP communities.
    snmp_community: NotRequired[list[dict[str, Any]]]  # Configuration method to edit Simple Network Management Proto
    override_snmp_user: NotRequired[Literal[{"description": "Override the global SNMPv3 users", "help": "Override the global SNMPv3 users.", "label": "Enable", "name": "enable"}, {"description": "Use the global SNMPv3 users", "help": "Use the global SNMPv3 users.", "label": "Disable", "name": "disable"}]]  # Enable/disable overriding the global SNMP users.
    snmp_user: NotRequired[list[dict[str, Any]]]  # Configuration method to edit Simple Network Management Proto
    qos_drop_policy: NotRequired[Literal[{"description": "Taildrop policy", "help": "Taildrop policy.", "label": "Taildrop", "name": "taildrop"}, {"description": "Random early detection drop policy", "help": "Random early detection drop policy.", "label": "Random Early Detection", "name": "random-early-detection"}]]  # Set QoS drop-policy.
    qos_red_probability: NotRequired[int]  # Set QoS RED/WRED drop probability.
    switch_log: NotRequired[str]  # Configuration method to edit FortiSwitch logging settings (l
    remote_log: NotRequired[list[dict[str, Any]]]  # Configure logging by FortiSwitch device to a remote syslog s
    storm_control: NotRequired[str]  # Configuration method to edit FortiSwitch storm control for m
    mirror: NotRequired[list[dict[str, Any]]]  # Configuration method to edit FortiSwitch packet mirror.
    static_mac: NotRequired[list[dict[str, Any]]]  # Configuration method to edit FortiSwitch Static and Sticky M
    custom_command: NotRequired[list[dict[str, Any]]]  # Configuration method to edit FortiSwitch commands to be push
    dhcp_snooping_static_client: NotRequired[list[dict[str, Any]]]  # Configure FortiSwitch DHCP snooping static clients.
    igmp_snooping: NotRequired[str]  # Configure FortiSwitch IGMP snooping global settings.
    x802_1X_settings: NotRequired[str]  # Configuration method to edit FortiSwitch 802.1X global setti
    router_vrf: NotRequired[list[dict[str, Any]]]  # Configure VRF.
    system_interface: NotRequired[list[dict[str, Any]]]  # Configure system interface on FortiSwitch.
    router_static: NotRequired[list[dict[str, Any]]]  # Configure static routes.
    system_dhcp_server: NotRequired[list[dict[str, Any]]]  # Configure DHCP servers.


class ManagedSwitch:
    """
    Configure FortiSwitch devices that are managed by this FortiGate.
    
    Path: switch_controller/managed_switch
    Category: cmdb
    Primary Key: switch-id
    """
    
    # Overloads for get() with response_mode="object"
    @overload
    def get(
        self,
        switch_id: str | None = ...,
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
        switch_id: str,
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
        switch_id: str | None = ...,
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
        switch_id: str | None = ...,
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
        switch_id: str | None = ...,
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
        payload_dict: ManagedSwitchPayload | None = ...,
        switch_id: str | None = ...,
        sn: str | None = ...,
        description: str | None = ...,
        switch_profile: str | None = ...,
        access_profile: str | None = ...,
        purdue_level: Literal[{"description": "Level 1 - Basic Control    1", "help": "Level 1 - Basic Control", "label": "1", "name": "1"}, {"help": "Level 1.5", "label": "1.5", "name": "1.5"}, {"help": "Level 2 - Area Supervisory Control", "label": "2", "name": "2"}, {"help": "Level 2.5", "label": "2.5", "name": "2.5"}, {"help": "Level 3 - Operations \u0026 Control", "label": "3", "name": "3"}, {"help": "Level 3.5", "label": "3.5", "name": "3.5"}, {"help": "Level 4 - Business Planning \u0026 Logistics", "label": "4", "name": "4"}, {"description": "Level 5", "help": "Level 5 - Enterprise Network", "label": "5", "name": "5"}, {"help": "Level 5.5", "label": "5.5", "name": "5.5"}] | None = ...,
        fsw_wan1_peer: str | None = ...,
        fsw_wan1_admin: Literal[{"description": "Link waiting to be authorized", "help": "Link waiting to be authorized.", "label": "Discovered", "name": "discovered"}, {"description": "Link unauthorized", "help": "Link unauthorized.", "label": "Disable", "name": "disable"}, {"description": "Link authorized", "help": "Link authorized.", "label": "Enable", "name": "enable"}] | None = ...,
        poe_pre_standard_detection: Literal[{"description": "Enable PoE pre-standard detection", "help": "Enable PoE pre-standard detection.", "label": "Enable", "name": "enable"}, {"description": "Disable PoE pre-standard detection", "help": "Disable PoE pre-standard detection.", "label": "Disable", "name": "disable"}] | None = ...,
        dhcp_server_access_list: Literal[{"description": "Use global setting for DHCP snooping server access list", "help": "Use global setting for DHCP snooping server access list.", "label": "Global", "name": "global"}, {"description": "Override global setting and enable DHCP server access list", "help": "Override global setting and enable DHCP server access list.", "label": "Enable", "name": "enable"}, {"description": "Override global setting and disable DHCP server access list", "help": "Override global setting and disable DHCP server access list.", "label": "Disable", "name": "disable"}] | None = ...,
        poe_detection_type: int | None = ...,
        max_poe_budget: int | None = ...,
        directly_connected: int | None = ...,
        version: int | None = ...,
        max_allowed_trunk_members: int | None = ...,
        pre_provisioned: int | None = ...,
        l3_discovered: int | None = ...,
        mgmt_mode: int | None = ...,
        tunnel_discovered: int | None = ...,
        tdr_supported: str | None = ...,
        dynamic_capability: str | None = ...,
        switch_device_tag: str | None = ...,
        switch_dhcp_opt43_key: str | None = ...,
        mclag_igmp_snooping_aware: Literal[{"description": "Enable MCLAG IGMP-snooping awareness", "help": "Enable MCLAG IGMP-snooping awareness.", "label": "Enable", "name": "enable"}, {"description": "Disable MCLAG IGMP-snooping awareness", "help": "Disable MCLAG IGMP-snooping awareness.", "label": "Disable", "name": "disable"}] | None = ...,
        dynamically_discovered: int | None = ...,
        ptp_status: Literal[{"description": "Disable PTP profile", "help": "Disable PTP profile.", "label": "Disable", "name": "disable"}, {"description": "Enable PTP profile", "help": "Enable PTP profile.", "label": "Enable", "name": "enable"}] | None = ...,
        ptp_profile: str | None = ...,
        radius_nas_ip_override: Literal[{"description": "Disable radius-nas-ip-override", "help": "Disable radius-nas-ip-override.", "label": "Disable", "name": "disable"}, {"description": "Enable radius-nas-ip-override", "help": "Enable radius-nas-ip-override.", "label": "Enable", "name": "enable"}] | None = ...,
        radius_nas_ip: str | None = ...,
        route_offload: Literal[{"description": "Disable route offload", "help": "Disable route offload.", "label": "Disable", "name": "disable"}, {"description": "Enable route offload", "help": "Enable route offload.", "label": "Enable", "name": "enable"}] | None = ...,
        route_offload_mclag: Literal[{"description": "Disable route offload MCLAG", "help": "Disable route offload MCLAG.", "label": "Disable", "name": "disable"}, {"description": "Enable route offload MCLAG", "help": "Enable route offload MCLAG.", "label": "Enable", "name": "enable"}] | None = ...,
        route_offload_router: list[dict[str, Any]] | None = ...,
        vlan: list[dict[str, Any]] | None = ...,
        type: Literal[{"description": "Switch is of type virtual", "help": "Switch is of type virtual.", "label": "Virtual", "name": "virtual"}, {"description": "Switch is of type physical", "help": "Switch is of type physical.", "label": "Physical", "name": "physical"}] | None = ...,
        owner_vdom: str | None = ...,
        flow_identity: str | None = ...,
        staged_image_version: str | None = ...,
        delayed_restart_trigger: int | None = ...,
        firmware_provision: Literal[{"description": "Enable firmware-provision", "help": "Enable firmware-provision.", "label": "Enable", "name": "enable"}, {"description": "Disable firmware-provision", "help": "Disable firmware-provision.", "label": "Disable", "name": "disable"}] | None = ...,
        firmware_provision_version: str | None = ...,
        firmware_provision_latest: Literal[{"description": "Do not automatically provision the latest available firmware", "help": "Do not automatically provision the latest available firmware.", "label": "Disable", "name": "disable"}, {"description": "Automatically attempt a one-time upgrade to the latest available firmware version", "help": "Automatically attempt a one-time upgrade to the latest available firmware version.", "label": "Once", "name": "once"}] | None = ...,
        ports: list[dict[str, Any]] | None = ...,
        ip_source_guard: list[dict[str, Any]] | None = ...,
        stp_settings: str | None = ...,
        stp_instance: list[dict[str, Any]] | None = ...,
        override_snmp_sysinfo: Literal[{"description": "Use the global SNMP system information", "help": "Use the global SNMP system information.", "label": "Disable", "name": "disable"}, {"description": "Override the global SNMP system information", "help": "Override the global SNMP system information.", "label": "Enable", "name": "enable"}] | None = ...,
        snmp_sysinfo: str | None = ...,
        override_snmp_trap_threshold: Literal[{"description": "Override the global SNMP trap threshold values", "help": "Override the global SNMP trap threshold values.", "label": "Enable", "name": "enable"}, {"description": "Use the global SNMP trap threshold values", "help": "Use the global SNMP trap threshold values.", "label": "Disable", "name": "disable"}] | None = ...,
        snmp_trap_threshold: str | None = ...,
        override_snmp_community: Literal[{"description": "Override the global SNMP communities", "help": "Override the global SNMP communities.", "label": "Enable", "name": "enable"}, {"description": "Use the global SNMP communities", "help": "Use the global SNMP communities.", "label": "Disable", "name": "disable"}] | None = ...,
        snmp_community: list[dict[str, Any]] | None = ...,
        override_snmp_user: Literal[{"description": "Override the global SNMPv3 users", "help": "Override the global SNMPv3 users.", "label": "Enable", "name": "enable"}, {"description": "Use the global SNMPv3 users", "help": "Use the global SNMPv3 users.", "label": "Disable", "name": "disable"}] | None = ...,
        snmp_user: list[dict[str, Any]] | None = ...,
        qos_drop_policy: Literal[{"description": "Taildrop policy", "help": "Taildrop policy.", "label": "Taildrop", "name": "taildrop"}, {"description": "Random early detection drop policy", "help": "Random early detection drop policy.", "label": "Random Early Detection", "name": "random-early-detection"}] | None = ...,
        qos_red_probability: int | None = ...,
        switch_log: str | None = ...,
        remote_log: list[dict[str, Any]] | None = ...,
        storm_control: str | None = ...,
        mirror: list[dict[str, Any]] | None = ...,
        static_mac: list[dict[str, Any]] | None = ...,
        custom_command: list[dict[str, Any]] | None = ...,
        dhcp_snooping_static_client: list[dict[str, Any]] | None = ...,
        igmp_snooping: str | None = ...,
        x802_1X_settings: str | None = ...,
        router_vrf: list[dict[str, Any]] | None = ...,
        system_interface: list[dict[str, Any]] | None = ...,
        router_static: list[dict[str, Any]] | None = ...,
        system_dhcp_server: list[dict[str, Any]] | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: ManagedSwitchPayload | None = ...,
        switch_id: str | None = ...,
        sn: str | None = ...,
        description: str | None = ...,
        switch_profile: str | None = ...,
        access_profile: str | None = ...,
        purdue_level: Literal[{"description": "Level 1 - Basic Control    1", "help": "Level 1 - Basic Control", "label": "1", "name": "1"}, {"help": "Level 1.5", "label": "1.5", "name": "1.5"}, {"help": "Level 2 - Area Supervisory Control", "label": "2", "name": "2"}, {"help": "Level 2.5", "label": "2.5", "name": "2.5"}, {"help": "Level 3 - Operations \u0026 Control", "label": "3", "name": "3"}, {"help": "Level 3.5", "label": "3.5", "name": "3.5"}, {"help": "Level 4 - Business Planning \u0026 Logistics", "label": "4", "name": "4"}, {"description": "Level 5", "help": "Level 5 - Enterprise Network", "label": "5", "name": "5"}, {"help": "Level 5.5", "label": "5.5", "name": "5.5"}] | None = ...,
        fsw_wan1_peer: str | None = ...,
        fsw_wan1_admin: Literal[{"description": "Link waiting to be authorized", "help": "Link waiting to be authorized.", "label": "Discovered", "name": "discovered"}, {"description": "Link unauthorized", "help": "Link unauthorized.", "label": "Disable", "name": "disable"}, {"description": "Link authorized", "help": "Link authorized.", "label": "Enable", "name": "enable"}] | None = ...,
        poe_pre_standard_detection: Literal[{"description": "Enable PoE pre-standard detection", "help": "Enable PoE pre-standard detection.", "label": "Enable", "name": "enable"}, {"description": "Disable PoE pre-standard detection", "help": "Disable PoE pre-standard detection.", "label": "Disable", "name": "disable"}] | None = ...,
        dhcp_server_access_list: Literal[{"description": "Use global setting for DHCP snooping server access list", "help": "Use global setting for DHCP snooping server access list.", "label": "Global", "name": "global"}, {"description": "Override global setting and enable DHCP server access list", "help": "Override global setting and enable DHCP server access list.", "label": "Enable", "name": "enable"}, {"description": "Override global setting and disable DHCP server access list", "help": "Override global setting and disable DHCP server access list.", "label": "Disable", "name": "disable"}] | None = ...,
        poe_detection_type: int | None = ...,
        max_poe_budget: int | None = ...,
        directly_connected: int | None = ...,
        version: int | None = ...,
        max_allowed_trunk_members: int | None = ...,
        pre_provisioned: int | None = ...,
        l3_discovered: int | None = ...,
        mgmt_mode: int | None = ...,
        tunnel_discovered: int | None = ...,
        tdr_supported: str | None = ...,
        dynamic_capability: str | None = ...,
        switch_device_tag: str | None = ...,
        switch_dhcp_opt43_key: str | None = ...,
        mclag_igmp_snooping_aware: Literal[{"description": "Enable MCLAG IGMP-snooping awareness", "help": "Enable MCLAG IGMP-snooping awareness.", "label": "Enable", "name": "enable"}, {"description": "Disable MCLAG IGMP-snooping awareness", "help": "Disable MCLAG IGMP-snooping awareness.", "label": "Disable", "name": "disable"}] | None = ...,
        dynamically_discovered: int | None = ...,
        ptp_status: Literal[{"description": "Disable PTP profile", "help": "Disable PTP profile.", "label": "Disable", "name": "disable"}, {"description": "Enable PTP profile", "help": "Enable PTP profile.", "label": "Enable", "name": "enable"}] | None = ...,
        ptp_profile: str | None = ...,
        radius_nas_ip_override: Literal[{"description": "Disable radius-nas-ip-override", "help": "Disable radius-nas-ip-override.", "label": "Disable", "name": "disable"}, {"description": "Enable radius-nas-ip-override", "help": "Enable radius-nas-ip-override.", "label": "Enable", "name": "enable"}] | None = ...,
        radius_nas_ip: str | None = ...,
        route_offload: Literal[{"description": "Disable route offload", "help": "Disable route offload.", "label": "Disable", "name": "disable"}, {"description": "Enable route offload", "help": "Enable route offload.", "label": "Enable", "name": "enable"}] | None = ...,
        route_offload_mclag: Literal[{"description": "Disable route offload MCLAG", "help": "Disable route offload MCLAG.", "label": "Disable", "name": "disable"}, {"description": "Enable route offload MCLAG", "help": "Enable route offload MCLAG.", "label": "Enable", "name": "enable"}] | None = ...,
        route_offload_router: list[dict[str, Any]] | None = ...,
        vlan: list[dict[str, Any]] | None = ...,
        type: Literal[{"description": "Switch is of type virtual", "help": "Switch is of type virtual.", "label": "Virtual", "name": "virtual"}, {"description": "Switch is of type physical", "help": "Switch is of type physical.", "label": "Physical", "name": "physical"}] | None = ...,
        owner_vdom: str | None = ...,
        flow_identity: str | None = ...,
        staged_image_version: str | None = ...,
        delayed_restart_trigger: int | None = ...,
        firmware_provision: Literal[{"description": "Enable firmware-provision", "help": "Enable firmware-provision.", "label": "Enable", "name": "enable"}, {"description": "Disable firmware-provision", "help": "Disable firmware-provision.", "label": "Disable", "name": "disable"}] | None = ...,
        firmware_provision_version: str | None = ...,
        firmware_provision_latest: Literal[{"description": "Do not automatically provision the latest available firmware", "help": "Do not automatically provision the latest available firmware.", "label": "Disable", "name": "disable"}, {"description": "Automatically attempt a one-time upgrade to the latest available firmware version", "help": "Automatically attempt a one-time upgrade to the latest available firmware version.", "label": "Once", "name": "once"}] | None = ...,
        ports: list[dict[str, Any]] | None = ...,
        ip_source_guard: list[dict[str, Any]] | None = ...,
        stp_settings: str | None = ...,
        stp_instance: list[dict[str, Any]] | None = ...,
        override_snmp_sysinfo: Literal[{"description": "Use the global SNMP system information", "help": "Use the global SNMP system information.", "label": "Disable", "name": "disable"}, {"description": "Override the global SNMP system information", "help": "Override the global SNMP system information.", "label": "Enable", "name": "enable"}] | None = ...,
        snmp_sysinfo: str | None = ...,
        override_snmp_trap_threshold: Literal[{"description": "Override the global SNMP trap threshold values", "help": "Override the global SNMP trap threshold values.", "label": "Enable", "name": "enable"}, {"description": "Use the global SNMP trap threshold values", "help": "Use the global SNMP trap threshold values.", "label": "Disable", "name": "disable"}] | None = ...,
        snmp_trap_threshold: str | None = ...,
        override_snmp_community: Literal[{"description": "Override the global SNMP communities", "help": "Override the global SNMP communities.", "label": "Enable", "name": "enable"}, {"description": "Use the global SNMP communities", "help": "Use the global SNMP communities.", "label": "Disable", "name": "disable"}] | None = ...,
        snmp_community: list[dict[str, Any]] | None = ...,
        override_snmp_user: Literal[{"description": "Override the global SNMPv3 users", "help": "Override the global SNMPv3 users.", "label": "Enable", "name": "enable"}, {"description": "Use the global SNMPv3 users", "help": "Use the global SNMPv3 users.", "label": "Disable", "name": "disable"}] | None = ...,
        snmp_user: list[dict[str, Any]] | None = ...,
        qos_drop_policy: Literal[{"description": "Taildrop policy", "help": "Taildrop policy.", "label": "Taildrop", "name": "taildrop"}, {"description": "Random early detection drop policy", "help": "Random early detection drop policy.", "label": "Random Early Detection", "name": "random-early-detection"}] | None = ...,
        qos_red_probability: int | None = ...,
        switch_log: str | None = ...,
        remote_log: list[dict[str, Any]] | None = ...,
        storm_control: str | None = ...,
        mirror: list[dict[str, Any]] | None = ...,
        static_mac: list[dict[str, Any]] | None = ...,
        custom_command: list[dict[str, Any]] | None = ...,
        dhcp_snooping_static_client: list[dict[str, Any]] | None = ...,
        igmp_snooping: str | None = ...,
        x802_1X_settings: str | None = ...,
        router_vrf: list[dict[str, Any]] | None = ...,
        system_interface: list[dict[str, Any]] | None = ...,
        router_static: list[dict[str, Any]] | None = ...,
        system_dhcp_server: list[dict[str, Any]] | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def delete(
        self,
        switch_id: str | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def exists(
        self,
        switch_id: str,
        vdom: str | bool | None = ...,
    ) -> Union[bool, Coroutine[Any, Any, bool]]: ...
    
    def set(
        self,
        payload_dict: ManagedSwitchPayload | None = ...,
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
    "ManagedSwitch",
    "ManagedSwitchPayload",
]