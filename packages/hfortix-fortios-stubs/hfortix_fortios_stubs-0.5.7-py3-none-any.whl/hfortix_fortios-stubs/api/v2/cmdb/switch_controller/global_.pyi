from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class GlobalPayload(TypedDict, total=False):
    """
    Type hints for switch_controller/global_ payload fields.
    
    Configure FortiSwitch global settings.
    
    **Related Resources:**

    Dependencies (resources this endpoint references):
        - :class:`~.system.interface.InterfaceEndpoint` (via: default-virtual-switch-vlan)

    **Usage:**
        payload: GlobalPayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    mac_aging_interval: NotRequired[int]  # Time after which an inactive MAC is aged out (10 - 1000000 s
    https_image_push: NotRequired[Literal[{"description": "Enable image push to FortiSwitch using HTTPS", "help": "Enable image push to FortiSwitch using HTTPS.", "label": "Enable", "name": "enable"}, {"description": "Disable image push to FortiSwitch using HTTPS", "help": "Disable image push to FortiSwitch using HTTPS.", "label": "Disable", "name": "disable"}]]  # Enable/disable image push to FortiSwitch using HTTPS.
    vlan_all_mode: NotRequired[Literal[{"description": "Include all possible VLANs (1-4093)", "help": "Include all possible VLANs (1-4093).", "label": "All", "name": "all"}, {"description": "Include user defined VLANs", "help": "Include user defined VLANs.", "label": "Defined", "name": "defined"}]]  # VLAN configuration mode, user-defined-vlans or all-possible-
    vlan_optimization: NotRequired[Literal[{"description": "Enable VLAN optimization (only VLANs necessary on or along path between destinations) on FortiSwitch units for auto-generated trunks", "help": "Enable VLAN optimization (only VLANs necessary on or along path between destinations) on FortiSwitch units for auto-generated trunks.", "label": "Prune", "name": "prune"}, {"description": "Enable VLAN optimization (only VLANs created on Fortilink interface) on FortiSwitch units for auto-generated trunks", "help": "Enable VLAN optimization (only VLANs created on Fortilink interface) on FortiSwitch units for auto-generated trunks.", "label": "Configured", "name": "configured"}, {"description": "Disable VLAN optimization on FortiSwitch units for auto-generated trunks", "help": "Disable VLAN optimization on FortiSwitch units for auto-generated trunks.", "label": "None", "name": "none"}]]  # FortiLink VLAN optimization.
    vlan_identity: NotRequired[Literal[{"description": "Configure the VLAN description to that of the FortiOS interface description if available; otherwise use the interface name", "help": "Configure the VLAN description to that of the FortiOS interface description if available; otherwise use the interface name.", "label": "Description", "name": "description"}, {"description": "Configure the VLAN description to that of the FortiOS interface name", "help": "Configure the VLAN description to that of the FortiOS interface name.", "label": "Name", "name": "name"}]]  # Identity of the VLAN. Commonly used for RADIUS Tunnel-Privat
    disable_discovery: NotRequired[list[dict[str, Any]]]  # Prevent this FortiSwitch from discovering.
    mac_retention_period: NotRequired[int]  # Time in hours after which an inactive MAC is removed from cl
    default_virtual_switch_vlan: NotRequired[str]  # Default VLAN for ports when added to the virtual-switch.
    dhcp_server_access_list: NotRequired[Literal[{"description": "Enable DHCP server access list", "help": "Enable DHCP server access list.", "label": "Enable", "name": "enable"}, {"description": "Disable DHCP server access list", "help": "Disable DHCP server access list.", "label": "Disable", "name": "disable"}]]  # Enable/disable DHCP snooping server access list.
    dhcp_option82_format: NotRequired[Literal[{"description": "Allow user to choose values for circuit-id and remote-id", "help": "Allow user to choose values for circuit-id and remote-id.\n\t  Format:  cid= [hostname,interface,mode,vlan,description] rid=[hostname,xx:xx:xx:xx:xx:xx,ip]\n", "label": "Ascii", "name": "ascii"}, {"help": "Generate predefine fixed format for circuit-id and remote.\n\tFormat: cid=hostname-[\u003cvlan:16\u003e\u003cmod:8\u003e\u003cport:8\u003e].32bit, rid= [mac(0..6)].48bit\n", "label": "Legacy", "name": "legacy"}]]  # DHCP option-82 format string.
    dhcp_option82_circuit_id: NotRequired[Literal[{"description": "Interface name", "help": "Interface name.", "label": "Intfname", "name": "intfname"}, {"description": "VLAN name", "help": "VLAN name.", "label": "Vlan", "name": "vlan"}, {"description": "Hostname", "help": "Hostname.", "label": "Hostname", "name": "hostname"}, {"description": "Mode", "help": "Mode.", "label": "Mode", "name": "mode"}, {"description": "Description", "help": "Description.", "label": "Description", "name": "description"}]]  # List the parameters to be included to inform about client id
    dhcp_option82_remote_id: NotRequired[Literal[{"description": "MAC address", "help": "MAC address.", "label": "Mac", "name": "mac"}, {"description": "Hostname", "help": "Hostname.", "label": "Hostname", "name": "hostname"}, {"description": "IP address", "help": "IP address.", "label": "Ip", "name": "ip"}]]  # List the parameters to be included to inform about client id
    dhcp_snoop_client_req: NotRequired[Literal[{"description": "Broadcast packets on trusted ports in the VLAN", "help": "Broadcast packets on trusted ports in the VLAN.", "label": "Drop Untrusted", "name": "drop-untrusted"}, {"description": "Broadcast packets on all ports in the VLAN", "help": "Broadcast packets on all ports in the VLAN.", "label": "Forward Untrusted", "name": "forward-untrusted"}]]  # Client DHCP packet broadcast mode.
    dhcp_snoop_client_db_exp: NotRequired[int]  # Expiry time for DHCP snooping server database entries (300 -
    dhcp_snoop_db_per_port_learn_limit: NotRequired[int]  # Per Interface dhcp-server entries learn limit (0 - 1024, def
    log_mac_limit_violations: NotRequired[Literal[{"description": "Enable Learn Limit Violation", "help": "Enable Learn Limit Violation.", "label": "Enable", "name": "enable"}, {"description": "Disable Learn Limit Violation", "help": "Disable Learn Limit Violation.", "label": "Disable", "name": "disable"}]]  # Enable/disable logs for Learning Limit Violations.
    mac_violation_timer: NotRequired[int]  # Set timeout for Learning Limit Violations (0 = disabled).
    sn_dns_resolution: NotRequired[Literal[{"description": "Enable DNS resolution of the FortiSwitch unit\u0027s IP address with switch name", "help": "Enable DNS resolution of the FortiSwitch unit\u0027s IP address with switch name.", "label": "Enable", "name": "enable"}, {"description": "Disable DNS resolution of the FortiSwitch unit\u0027s IP address with switch name", "help": "Disable DNS resolution of the FortiSwitch unit\u0027s IP address with switch name.", "label": "Disable", "name": "disable"}]]  # Enable/disable DNS resolution of the FortiSwitch unit's IP a
    mac_event_logging: NotRequired[Literal[{"description": "Enable MAC address event logging", "help": "Enable MAC address event logging.", "label": "Enable", "name": "enable"}, {"description": "Disable MAC address event logging", "help": "Disable MAC address event logging.", "label": "Disable", "name": "disable"}]]  # Enable/disable MAC address event logging.
    bounce_quarantined_link: NotRequired[Literal[{"description": "Disable bouncing (administratively bring the link down, up) of a switch port where a quarantined device was seen last", "help": "Disable bouncing (administratively bring the link down, up) of a switch port where a quarantined device was seen last.", "label": "Disable", "name": "disable"}, {"description": "Enable bouncing (administratively bring the link down, up) of a switch port where a quarantined device was seen last", "help": "Enable bouncing (administratively bring the link down, up) of a switch port where a quarantined device was seen last.", "label": "Enable", "name": "enable"}]]  # Enable/disable bouncing (administratively bring the link dow
    quarantine_mode: NotRequired[Literal[{"description": "Quarantined device traffic is sent to FortiGate on a separate quarantine VLAN", "help": "Quarantined device traffic is sent to FortiGate on a separate quarantine VLAN.", "label": "By Vlan", "name": "by-vlan"}, {"description": "Quarantined device traffic is redirected only to the FortiGate on the received VLAN", "help": "Quarantined device traffic is redirected only to the FortiGate on the received VLAN.", "label": "By Redirect", "name": "by-redirect"}]]  # Quarantine mode.
    update_user_device: NotRequired[Literal[{"description": "Update MAC address from switch-controller mac-cache", "help": "Update MAC address from switch-controller mac-cache.", "label": "Mac Cache", "name": "mac-cache"}, {"description": "Update from FortiSwitch LLDP neighbor database", "help": "Update from FortiSwitch LLDP neighbor database.", "label": "Lldp", "name": "lldp"}, {"description": "Update from FortiSwitch DHCP snooping client and server databases", "help": "Update from FortiSwitch DHCP snooping client and server databases.", "label": "Dhcp Snooping", "name": "dhcp-snooping"}, {"description": "Update from FortiSwitch Network-monitor Layer 2 tracking database", "help": "Update from FortiSwitch Network-monitor Layer 2 tracking database.", "label": "L2 Db", "name": "l2-db"}, {"description": "Update from FortiSwitch Network-monitor Layer 3 tracking database", "help": "Update from FortiSwitch Network-monitor Layer 3 tracking database.", "label": "L3 Db", "name": "l3-db"}]]  # Control which sources update the device user list.
    custom_command: NotRequired[list[dict[str, Any]]]  # List of custom commands to be pushed to all FortiSwitches in
    fips_enforce: NotRequired[Literal[{"description": "Disable enforcement of FIPS on managed FortiSwitch devices", "help": "Disable enforcement of FIPS on managed FortiSwitch devices.", "label": "Disable", "name": "disable"}, {"description": "Enable enforcement of FIPS on managed FortiSwitch devices", "help": "Enable enforcement of FIPS on managed FortiSwitch devices.", "label": "Enable", "name": "enable"}]]  # Enable/disable enforcement of FIPS on managed FortiSwitch de
    firmware_provision_on_authorization: NotRequired[Literal[{"description": "Enable firmware provision on authorization", "help": "Enable firmware provision on authorization.", "label": "Enable", "name": "enable"}, {"description": "Disable firmware provision on authorization", "help": "Disable firmware provision on authorization.", "label": "Disable", "name": "disable"}]]  # Enable/disable automatic provisioning of latest firmware on 
    switch_on_deauth: NotRequired[Literal[{"description": "No-operation on the managed FortiSwitch on deauthorization", "help": "No-operation on the managed FortiSwitch on deauthorization.", "label": "No Op", "name": "no-op"}, {"description": "Factory-reset the managed FortiSwitch on deauthorization", "help": "Factory-reset the managed FortiSwitch on deauthorization.", "label": "Factory Reset", "name": "factory-reset"}]]  # No-operation/Factory-reset the managed FortiSwitch on deauth
    firewall_auth_user_hold_period: NotRequired[int]  # Time period in minutes to hold firewall authenticated MAC us


class Global:
    """
    Configure FortiSwitch global settings.
    
    Path: switch_controller/global_
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
        payload_dict: GlobalPayload | None = ...,
        mac_aging_interval: int | None = ...,
        https_image_push: Literal[{"description": "Enable image push to FortiSwitch using HTTPS", "help": "Enable image push to FortiSwitch using HTTPS.", "label": "Enable", "name": "enable"}, {"description": "Disable image push to FortiSwitch using HTTPS", "help": "Disable image push to FortiSwitch using HTTPS.", "label": "Disable", "name": "disable"}] | None = ...,
        vlan_all_mode: Literal[{"description": "Include all possible VLANs (1-4093)", "help": "Include all possible VLANs (1-4093).", "label": "All", "name": "all"}, {"description": "Include user defined VLANs", "help": "Include user defined VLANs.", "label": "Defined", "name": "defined"}] | None = ...,
        vlan_optimization: Literal[{"description": "Enable VLAN optimization (only VLANs necessary on or along path between destinations) on FortiSwitch units for auto-generated trunks", "help": "Enable VLAN optimization (only VLANs necessary on or along path between destinations) on FortiSwitch units for auto-generated trunks.", "label": "Prune", "name": "prune"}, {"description": "Enable VLAN optimization (only VLANs created on Fortilink interface) on FortiSwitch units for auto-generated trunks", "help": "Enable VLAN optimization (only VLANs created on Fortilink interface) on FortiSwitch units for auto-generated trunks.", "label": "Configured", "name": "configured"}, {"description": "Disable VLAN optimization on FortiSwitch units for auto-generated trunks", "help": "Disable VLAN optimization on FortiSwitch units for auto-generated trunks.", "label": "None", "name": "none"}] | None = ...,
        vlan_identity: Literal[{"description": "Configure the VLAN description to that of the FortiOS interface description if available; otherwise use the interface name", "help": "Configure the VLAN description to that of the FortiOS interface description if available; otherwise use the interface name.", "label": "Description", "name": "description"}, {"description": "Configure the VLAN description to that of the FortiOS interface name", "help": "Configure the VLAN description to that of the FortiOS interface name.", "label": "Name", "name": "name"}] | None = ...,
        disable_discovery: list[dict[str, Any]] | None = ...,
        mac_retention_period: int | None = ...,
        default_virtual_switch_vlan: str | None = ...,
        dhcp_server_access_list: Literal[{"description": "Enable DHCP server access list", "help": "Enable DHCP server access list.", "label": "Enable", "name": "enable"}, {"description": "Disable DHCP server access list", "help": "Disable DHCP server access list.", "label": "Disable", "name": "disable"}] | None = ...,
        dhcp_option82_format: Literal[{"description": "Allow user to choose values for circuit-id and remote-id", "help": "Allow user to choose values for circuit-id and remote-id.\n\t  Format:  cid= [hostname,interface,mode,vlan,description] rid=[hostname,xx:xx:xx:xx:xx:xx,ip]\n", "label": "Ascii", "name": "ascii"}, {"help": "Generate predefine fixed format for circuit-id and remote.\n\tFormat: cid=hostname-[\u003cvlan:16\u003e\u003cmod:8\u003e\u003cport:8\u003e].32bit, rid= [mac(0..6)].48bit\n", "label": "Legacy", "name": "legacy"}] | None = ...,
        dhcp_option82_circuit_id: Literal[{"description": "Interface name", "help": "Interface name.", "label": "Intfname", "name": "intfname"}, {"description": "VLAN name", "help": "VLAN name.", "label": "Vlan", "name": "vlan"}, {"description": "Hostname", "help": "Hostname.", "label": "Hostname", "name": "hostname"}, {"description": "Mode", "help": "Mode.", "label": "Mode", "name": "mode"}, {"description": "Description", "help": "Description.", "label": "Description", "name": "description"}] | None = ...,
        dhcp_option82_remote_id: Literal[{"description": "MAC address", "help": "MAC address.", "label": "Mac", "name": "mac"}, {"description": "Hostname", "help": "Hostname.", "label": "Hostname", "name": "hostname"}, {"description": "IP address", "help": "IP address.", "label": "Ip", "name": "ip"}] | None = ...,
        dhcp_snoop_client_req: Literal[{"description": "Broadcast packets on trusted ports in the VLAN", "help": "Broadcast packets on trusted ports in the VLAN.", "label": "Drop Untrusted", "name": "drop-untrusted"}, {"description": "Broadcast packets on all ports in the VLAN", "help": "Broadcast packets on all ports in the VLAN.", "label": "Forward Untrusted", "name": "forward-untrusted"}] | None = ...,
        dhcp_snoop_client_db_exp: int | None = ...,
        dhcp_snoop_db_per_port_learn_limit: int | None = ...,
        log_mac_limit_violations: Literal[{"description": "Enable Learn Limit Violation", "help": "Enable Learn Limit Violation.", "label": "Enable", "name": "enable"}, {"description": "Disable Learn Limit Violation", "help": "Disable Learn Limit Violation.", "label": "Disable", "name": "disable"}] | None = ...,
        mac_violation_timer: int | None = ...,
        sn_dns_resolution: Literal[{"description": "Enable DNS resolution of the FortiSwitch unit\u0027s IP address with switch name", "help": "Enable DNS resolution of the FortiSwitch unit\u0027s IP address with switch name.", "label": "Enable", "name": "enable"}, {"description": "Disable DNS resolution of the FortiSwitch unit\u0027s IP address with switch name", "help": "Disable DNS resolution of the FortiSwitch unit\u0027s IP address with switch name.", "label": "Disable", "name": "disable"}] | None = ...,
        mac_event_logging: Literal[{"description": "Enable MAC address event logging", "help": "Enable MAC address event logging.", "label": "Enable", "name": "enable"}, {"description": "Disable MAC address event logging", "help": "Disable MAC address event logging.", "label": "Disable", "name": "disable"}] | None = ...,
        bounce_quarantined_link: Literal[{"description": "Disable bouncing (administratively bring the link down, up) of a switch port where a quarantined device was seen last", "help": "Disable bouncing (administratively bring the link down, up) of a switch port where a quarantined device was seen last.", "label": "Disable", "name": "disable"}, {"description": "Enable bouncing (administratively bring the link down, up) of a switch port where a quarantined device was seen last", "help": "Enable bouncing (administratively bring the link down, up) of a switch port where a quarantined device was seen last.", "label": "Enable", "name": "enable"}] | None = ...,
        quarantine_mode: Literal[{"description": "Quarantined device traffic is sent to FortiGate on a separate quarantine VLAN", "help": "Quarantined device traffic is sent to FortiGate on a separate quarantine VLAN.", "label": "By Vlan", "name": "by-vlan"}, {"description": "Quarantined device traffic is redirected only to the FortiGate on the received VLAN", "help": "Quarantined device traffic is redirected only to the FortiGate on the received VLAN.", "label": "By Redirect", "name": "by-redirect"}] | None = ...,
        update_user_device: Literal[{"description": "Update MAC address from switch-controller mac-cache", "help": "Update MAC address from switch-controller mac-cache.", "label": "Mac Cache", "name": "mac-cache"}, {"description": "Update from FortiSwitch LLDP neighbor database", "help": "Update from FortiSwitch LLDP neighbor database.", "label": "Lldp", "name": "lldp"}, {"description": "Update from FortiSwitch DHCP snooping client and server databases", "help": "Update from FortiSwitch DHCP snooping client and server databases.", "label": "Dhcp Snooping", "name": "dhcp-snooping"}, {"description": "Update from FortiSwitch Network-monitor Layer 2 tracking database", "help": "Update from FortiSwitch Network-monitor Layer 2 tracking database.", "label": "L2 Db", "name": "l2-db"}, {"description": "Update from FortiSwitch Network-monitor Layer 3 tracking database", "help": "Update from FortiSwitch Network-monitor Layer 3 tracking database.", "label": "L3 Db", "name": "l3-db"}] | None = ...,
        custom_command: list[dict[str, Any]] | None = ...,
        fips_enforce: Literal[{"description": "Disable enforcement of FIPS on managed FortiSwitch devices", "help": "Disable enforcement of FIPS on managed FortiSwitch devices.", "label": "Disable", "name": "disable"}, {"description": "Enable enforcement of FIPS on managed FortiSwitch devices", "help": "Enable enforcement of FIPS on managed FortiSwitch devices.", "label": "Enable", "name": "enable"}] | None = ...,
        firmware_provision_on_authorization: Literal[{"description": "Enable firmware provision on authorization", "help": "Enable firmware provision on authorization.", "label": "Enable", "name": "enable"}, {"description": "Disable firmware provision on authorization", "help": "Disable firmware provision on authorization.", "label": "Disable", "name": "disable"}] | None = ...,
        switch_on_deauth: Literal[{"description": "No-operation on the managed FortiSwitch on deauthorization", "help": "No-operation on the managed FortiSwitch on deauthorization.", "label": "No Op", "name": "no-op"}, {"description": "Factory-reset the managed FortiSwitch on deauthorization", "help": "Factory-reset the managed FortiSwitch on deauthorization.", "label": "Factory Reset", "name": "factory-reset"}] | None = ...,
        firewall_auth_user_hold_period: int | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: GlobalPayload | None = ...,
        mac_aging_interval: int | None = ...,
        https_image_push: Literal[{"description": "Enable image push to FortiSwitch using HTTPS", "help": "Enable image push to FortiSwitch using HTTPS.", "label": "Enable", "name": "enable"}, {"description": "Disable image push to FortiSwitch using HTTPS", "help": "Disable image push to FortiSwitch using HTTPS.", "label": "Disable", "name": "disable"}] | None = ...,
        vlan_all_mode: Literal[{"description": "Include all possible VLANs (1-4093)", "help": "Include all possible VLANs (1-4093).", "label": "All", "name": "all"}, {"description": "Include user defined VLANs", "help": "Include user defined VLANs.", "label": "Defined", "name": "defined"}] | None = ...,
        vlan_optimization: Literal[{"description": "Enable VLAN optimization (only VLANs necessary on or along path between destinations) on FortiSwitch units for auto-generated trunks", "help": "Enable VLAN optimization (only VLANs necessary on or along path between destinations) on FortiSwitch units for auto-generated trunks.", "label": "Prune", "name": "prune"}, {"description": "Enable VLAN optimization (only VLANs created on Fortilink interface) on FortiSwitch units for auto-generated trunks", "help": "Enable VLAN optimization (only VLANs created on Fortilink interface) on FortiSwitch units for auto-generated trunks.", "label": "Configured", "name": "configured"}, {"description": "Disable VLAN optimization on FortiSwitch units for auto-generated trunks", "help": "Disable VLAN optimization on FortiSwitch units for auto-generated trunks.", "label": "None", "name": "none"}] | None = ...,
        vlan_identity: Literal[{"description": "Configure the VLAN description to that of the FortiOS interface description if available; otherwise use the interface name", "help": "Configure the VLAN description to that of the FortiOS interface description if available; otherwise use the interface name.", "label": "Description", "name": "description"}, {"description": "Configure the VLAN description to that of the FortiOS interface name", "help": "Configure the VLAN description to that of the FortiOS interface name.", "label": "Name", "name": "name"}] | None = ...,
        disable_discovery: list[dict[str, Any]] | None = ...,
        mac_retention_period: int | None = ...,
        default_virtual_switch_vlan: str | None = ...,
        dhcp_server_access_list: Literal[{"description": "Enable DHCP server access list", "help": "Enable DHCP server access list.", "label": "Enable", "name": "enable"}, {"description": "Disable DHCP server access list", "help": "Disable DHCP server access list.", "label": "Disable", "name": "disable"}] | None = ...,
        dhcp_option82_format: Literal[{"description": "Allow user to choose values for circuit-id and remote-id", "help": "Allow user to choose values for circuit-id and remote-id.\n\t  Format:  cid= [hostname,interface,mode,vlan,description] rid=[hostname,xx:xx:xx:xx:xx:xx,ip]\n", "label": "Ascii", "name": "ascii"}, {"help": "Generate predefine fixed format for circuit-id and remote.\n\tFormat: cid=hostname-[\u003cvlan:16\u003e\u003cmod:8\u003e\u003cport:8\u003e].32bit, rid= [mac(0..6)].48bit\n", "label": "Legacy", "name": "legacy"}] | None = ...,
        dhcp_option82_circuit_id: Literal[{"description": "Interface name", "help": "Interface name.", "label": "Intfname", "name": "intfname"}, {"description": "VLAN name", "help": "VLAN name.", "label": "Vlan", "name": "vlan"}, {"description": "Hostname", "help": "Hostname.", "label": "Hostname", "name": "hostname"}, {"description": "Mode", "help": "Mode.", "label": "Mode", "name": "mode"}, {"description": "Description", "help": "Description.", "label": "Description", "name": "description"}] | None = ...,
        dhcp_option82_remote_id: Literal[{"description": "MAC address", "help": "MAC address.", "label": "Mac", "name": "mac"}, {"description": "Hostname", "help": "Hostname.", "label": "Hostname", "name": "hostname"}, {"description": "IP address", "help": "IP address.", "label": "Ip", "name": "ip"}] | None = ...,
        dhcp_snoop_client_req: Literal[{"description": "Broadcast packets on trusted ports in the VLAN", "help": "Broadcast packets on trusted ports in the VLAN.", "label": "Drop Untrusted", "name": "drop-untrusted"}, {"description": "Broadcast packets on all ports in the VLAN", "help": "Broadcast packets on all ports in the VLAN.", "label": "Forward Untrusted", "name": "forward-untrusted"}] | None = ...,
        dhcp_snoop_client_db_exp: int | None = ...,
        dhcp_snoop_db_per_port_learn_limit: int | None = ...,
        log_mac_limit_violations: Literal[{"description": "Enable Learn Limit Violation", "help": "Enable Learn Limit Violation.", "label": "Enable", "name": "enable"}, {"description": "Disable Learn Limit Violation", "help": "Disable Learn Limit Violation.", "label": "Disable", "name": "disable"}] | None = ...,
        mac_violation_timer: int | None = ...,
        sn_dns_resolution: Literal[{"description": "Enable DNS resolution of the FortiSwitch unit\u0027s IP address with switch name", "help": "Enable DNS resolution of the FortiSwitch unit\u0027s IP address with switch name.", "label": "Enable", "name": "enable"}, {"description": "Disable DNS resolution of the FortiSwitch unit\u0027s IP address with switch name", "help": "Disable DNS resolution of the FortiSwitch unit\u0027s IP address with switch name.", "label": "Disable", "name": "disable"}] | None = ...,
        mac_event_logging: Literal[{"description": "Enable MAC address event logging", "help": "Enable MAC address event logging.", "label": "Enable", "name": "enable"}, {"description": "Disable MAC address event logging", "help": "Disable MAC address event logging.", "label": "Disable", "name": "disable"}] | None = ...,
        bounce_quarantined_link: Literal[{"description": "Disable bouncing (administratively bring the link down, up) of a switch port where a quarantined device was seen last", "help": "Disable bouncing (administratively bring the link down, up) of a switch port where a quarantined device was seen last.", "label": "Disable", "name": "disable"}, {"description": "Enable bouncing (administratively bring the link down, up) of a switch port where a quarantined device was seen last", "help": "Enable bouncing (administratively bring the link down, up) of a switch port where a quarantined device was seen last.", "label": "Enable", "name": "enable"}] | None = ...,
        quarantine_mode: Literal[{"description": "Quarantined device traffic is sent to FortiGate on a separate quarantine VLAN", "help": "Quarantined device traffic is sent to FortiGate on a separate quarantine VLAN.", "label": "By Vlan", "name": "by-vlan"}, {"description": "Quarantined device traffic is redirected only to the FortiGate on the received VLAN", "help": "Quarantined device traffic is redirected only to the FortiGate on the received VLAN.", "label": "By Redirect", "name": "by-redirect"}] | None = ...,
        update_user_device: Literal[{"description": "Update MAC address from switch-controller mac-cache", "help": "Update MAC address from switch-controller mac-cache.", "label": "Mac Cache", "name": "mac-cache"}, {"description": "Update from FortiSwitch LLDP neighbor database", "help": "Update from FortiSwitch LLDP neighbor database.", "label": "Lldp", "name": "lldp"}, {"description": "Update from FortiSwitch DHCP snooping client and server databases", "help": "Update from FortiSwitch DHCP snooping client and server databases.", "label": "Dhcp Snooping", "name": "dhcp-snooping"}, {"description": "Update from FortiSwitch Network-monitor Layer 2 tracking database", "help": "Update from FortiSwitch Network-monitor Layer 2 tracking database.", "label": "L2 Db", "name": "l2-db"}, {"description": "Update from FortiSwitch Network-monitor Layer 3 tracking database", "help": "Update from FortiSwitch Network-monitor Layer 3 tracking database.", "label": "L3 Db", "name": "l3-db"}] | None = ...,
        custom_command: list[dict[str, Any]] | None = ...,
        fips_enforce: Literal[{"description": "Disable enforcement of FIPS on managed FortiSwitch devices", "help": "Disable enforcement of FIPS on managed FortiSwitch devices.", "label": "Disable", "name": "disable"}, {"description": "Enable enforcement of FIPS on managed FortiSwitch devices", "help": "Enable enforcement of FIPS on managed FortiSwitch devices.", "label": "Enable", "name": "enable"}] | None = ...,
        firmware_provision_on_authorization: Literal[{"description": "Enable firmware provision on authorization", "help": "Enable firmware provision on authorization.", "label": "Enable", "name": "enable"}, {"description": "Disable firmware provision on authorization", "help": "Disable firmware provision on authorization.", "label": "Disable", "name": "disable"}] | None = ...,
        switch_on_deauth: Literal[{"description": "No-operation on the managed FortiSwitch on deauthorization", "help": "No-operation on the managed FortiSwitch on deauthorization.", "label": "No Op", "name": "no-op"}, {"description": "Factory-reset the managed FortiSwitch on deauthorization", "help": "Factory-reset the managed FortiSwitch on deauthorization.", "label": "Factory Reset", "name": "factory-reset"}] | None = ...,
        firewall_auth_user_hold_period: int | None = ...,
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
        payload_dict: GlobalPayload | None = ...,
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
    "Global",
    "GlobalPayload",
]