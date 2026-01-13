from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class WtpPayload(TypedDict, total=False):
    """
    Type hints for wireless_controller/wtp payload fields.
    
    Configure Wireless Termination Points (WTPs), that is, FortiAPs or APs to be managed by FortiGate.
    
    **Related Resources:**

    Dependencies (resources this endpoint references):
        - :class:`~.wireless-controller.apcfg-profile.ApcfgProfileEndpoint` (via: apcfg-profile)
        - :class:`~.wireless-controller.bonjour-profile.BonjourProfileEndpoint` (via: bonjour-profile)
        - :class:`~.wireless-controller.region.RegionEndpoint` (via: region)
        - :class:`~.wireless-controller.wtp-profile.WtpProfileEndpoint` (via: wtp-profile)

    **Usage:**
        payload: WtpPayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    wtp_id: str  # WTP ID.
    index: NotRequired[int]  # Index (0 - 4294967295).
    uuid: NotRequired[str]  # Universally Unique Identifier (UUID; automatically assigned 
    admin: NotRequired[Literal[{"description": "FortiGate wireless controller discovers the WTP, AP, or FortiAP though discovery or join request messages", "help": "FortiGate wireless controller discovers the WTP, AP, or FortiAP though discovery or join request messages.", "label": "Discovered", "name": "discovered"}, {"description": "FortiGate wireless controller is configured to not provide service to this WTP", "help": "FortiGate wireless controller is configured to not provide service to this WTP.", "label": "Disable", "name": "disable"}, {"description": "FortiGate wireless controller is configured to provide service to this WTP", "help": "FortiGate wireless controller is configured to provide service to this WTP.", "label": "Enable", "name": "enable"}]]  # Configure how the FortiGate operating as a wireless controll
    name: NotRequired[str]  # WTP, AP or FortiAP configuration name.
    location: NotRequired[str]  # Field for describing the physical location of the WTP, AP or
    comment: NotRequired[str]  # Comment.
    region: NotRequired[str]  # Region name WTP is associated with.
    region_x: NotRequired[str]  # Relative horizontal region coordinate (between 0 and 1).
    region_y: NotRequired[str]  # Relative vertical region coordinate (between 0 and 1).
    firmware_provision: NotRequired[str]  # Firmware version to provision to this FortiAP on bootup (maj
    firmware_provision_latest: NotRequired[Literal[{"description": "Do not automatically provision the latest available firmware", "help": "Do not automatically provision the latest available firmware.", "label": "Disable", "name": "disable"}, {"description": "Automatically attempt a one-time upgrade to the latest available firmware version", "help": "Automatically attempt a one-time upgrade to the latest available firmware version.", "label": "Once", "name": "once"}]]  # Enable/disable one-time automatic provisioning of the latest
    wtp_profile: str  # WTP profile name to apply to this WTP, AP or FortiAP.
    apcfg_profile: NotRequired[str]  # AP local configuration profile name.
    bonjour_profile: NotRequired[str]  # Bonjour profile name.
    ble_major_id: NotRequired[int]  # Override BLE Major ID.
    ble_minor_id: NotRequired[int]  # Override BLE Minor ID.
    override_led_state: NotRequired[Literal[{"description": "Override the WTP profile LED state", "help": "Override the WTP profile LED state.", "label": "Enable", "name": "enable"}, {"description": "Use the WTP profile LED state", "help": "Use the WTP profile LED state.", "label": "Disable", "name": "disable"}]]  # Enable to override the profile LED state setting for this Fo
    led_state: NotRequired[Literal[{"description": "Allow the LEDs on this FortiAP to light", "help": "Allow the LEDs on this FortiAP to light.", "label": "Enable", "name": "enable"}, {"description": "Keep the LEDs on this FortiAP off", "help": "Keep the LEDs on this FortiAP off.", "label": "Disable", "name": "disable"}]]  # Enable to allow the FortiAPs LEDs to light. Disable to keep 
    override_wan_port_mode: NotRequired[Literal[{"description": "Override the WTP profile wan-port-mode", "help": "Override the WTP profile wan-port-mode.", "label": "Enable", "name": "enable"}, {"description": "Use the wan-port-mode in the WTP profile", "help": "Use the wan-port-mode in the WTP profile.", "label": "Disable", "name": "disable"}]]  # Enable/disable overriding the wan-port-mode in the WTP profi
    wan_port_mode: NotRequired[Literal[{"description": "Use the FortiAP WAN port as a LAN port", "help": "Use the FortiAP WAN port as a LAN port.", "label": "Wan Lan", "name": "wan-lan"}, {"description": "Do not use the WAN port as a LAN port", "help": "Do not use the WAN port as a LAN port.", "label": "Wan Only", "name": "wan-only"}]]  # Enable/disable using the FortiAP WAN port as a LAN port.
    override_ip_fragment: NotRequired[Literal[{"description": "Override the WTP profile IP fragment prevention setting", "help": "Override the WTP profile IP fragment prevention setting.", "label": "Enable", "name": "enable"}, {"description": "Use the WTP profile IP fragment prevention setting", "help": "Use the WTP profile IP fragment prevention setting.", "label": "Disable", "name": "disable"}]]  # Enable/disable overriding the WTP profile IP fragment preven
    ip_fragment_preventing: NotRequired[Literal[{"description": "TCP maximum segment size adjustment", "help": "TCP maximum segment size adjustment.", "label": "Tcp Mss Adjust", "name": "tcp-mss-adjust"}, {"description": "Drop packet and send ICMP Destination Unreachable", "help": "Drop packet and send ICMP Destination Unreachable", "label": "Icmp Unreachable", "name": "icmp-unreachable"}]]  # Method(s) by which IP fragmentation is prevented for control
    tun_mtu_uplink: NotRequired[int]  # The maximum transmission unit (MTU) of uplink CAPWAP tunnel 
    tun_mtu_downlink: NotRequired[int]  # The MTU of downlink CAPWAP tunnel (576 - 1500 bytes or 0; 0 
    override_split_tunnel: NotRequired[Literal[{"description": "Override the WTP profile split tunneling setting", "help": "Override the WTP profile split tunneling setting.", "label": "Enable", "name": "enable"}, {"description": "Use the WTP profile split tunneling setting", "help": "Use the WTP profile split tunneling setting.", "label": "Disable", "name": "disable"}]]  # Enable/disable overriding the WTP profile split tunneling se
    split_tunneling_acl_path: NotRequired[Literal[{"description": "Split tunneling ACL list traffic will be tunnel", "help": "Split tunneling ACL list traffic will be tunnel.", "label": "Tunnel", "name": "tunnel"}, {"description": "Split tunneling ACL list traffic will be local NATed", "help": "Split tunneling ACL list traffic will be local NATed.", "label": "Local", "name": "local"}]]  # Split tunneling ACL path is local/tunnel.
    split_tunneling_acl_local_ap_subnet: NotRequired[Literal[{"description": "Enable automatically adding local subnetwork of FortiAP to split-tunneling ACL", "help": "Enable automatically adding local subnetwork of FortiAP to split-tunneling ACL.", "label": "Enable", "name": "enable"}, {"description": "Disable automatically adding local subnetwork of FortiAP to split-tunneling ACL", "help": "Disable automatically adding local subnetwork of FortiAP to split-tunneling ACL.", "label": "Disable", "name": "disable"}]]  # Enable/disable automatically adding local subnetwork of Fort
    split_tunneling_acl: NotRequired[list[dict[str, Any]]]  # Split tunneling ACL filter list.
    override_lan: NotRequired[Literal[{"description": "Override the WTP profile LAN port setting", "help": "Override the WTP profile LAN port setting.", "label": "Enable", "name": "enable"}, {"description": "Use the WTP profile LAN port setting", "help": "Use the WTP profile LAN port setting.", "label": "Disable", "name": "disable"}]]  # Enable to override the WTP profile LAN port setting.
    lan: NotRequired[str]  # WTP LAN port mapping.
    override_allowaccess: NotRequired[Literal[{"description": "Override the WTP profile management access configuration", "help": "Override the WTP profile management access configuration.", "label": "Enable", "name": "enable"}, {"description": "Use the WTP profile management access configuration", "help": "Use the WTP profile management access configuration.", "label": "Disable", "name": "disable"}]]  # Enable to override the WTP profile management access configu
    allowaccess: NotRequired[Literal[{"description": "HTTPS access", "help": "HTTPS access.", "label": "Https", "name": "https"}, {"description": "SSH access", "help": "SSH access.", "label": "Ssh", "name": "ssh"}, {"description": "SNMP access", "help": "SNMP access.", "label": "Snmp", "name": "snmp"}]]  # Control management access to the managed WTP, FortiAP, or AP
    override_login_passwd_change: NotRequired[Literal[{"description": "Override the WTP profile login-password (administrator password) setting", "help": "Override the WTP profile login-password (administrator password) setting.", "label": "Enable", "name": "enable"}, {"description": "Use the the WTP profile login-password (administrator password) setting", "help": "Use the the WTP profile login-password (administrator password) setting.", "label": "Disable", "name": "disable"}]]  # Enable to override the WTP profile login-password (administr
    login_passwd_change: NotRequired[Literal[{"description": "Change the managed WTP, FortiAP or AP\u0027s administrator password", "help": "Change the managed WTP, FortiAP or AP\u0027s administrator password. Use the login-password option to set the password.", "label": "Yes", "name": "yes"}, {"description": "Keep the managed WTP, FortiAP or AP\u0027s administrator password set to the factory default", "help": "Keep the managed WTP, FortiAP or AP\u0027s administrator password set to the factory default.", "label": "Default", "name": "default"}, {"description": "Do not change the managed WTP, FortiAP or AP\u0027s administrator password", "help": "Do not change the managed WTP, FortiAP or AP\u0027s administrator password.", "label": "No", "name": "no"}]]  # Change or reset the administrator password of a managed WTP,
    login_passwd: NotRequired[str]  # Set the managed WTP, FortiAP, or AP's administrator password
    override_default_mesh_root: NotRequired[Literal[{"description": "Override the WTP profile default mesh root SSID setting", "help": "Override the WTP profile default mesh root SSID setting.", "label": "Enable", "name": "enable"}, {"description": "Use the WTP profile default mesh root SSID setting", "help": "Use the WTP profile default mesh root SSID setting.", "label": "Disable", "name": "disable"}]]  # Enable to override the WTP profile default mesh root SSID se
    default_mesh_root: NotRequired[Literal[{"description": "Enable default mesh root SSID if it is not included by radio\u0027s SSID configuration", "help": "Enable default mesh root SSID if it is not included by radio\u0027s SSID configuration.", "label": "Enable", "name": "enable"}, {"description": "Do not enable default mesh root SSID if it is not included by radio\u0027s SSID configuration", "help": "Do not enable default mesh root SSID if it is not included by radio\u0027s SSID configuration.", "label": "Disable", "name": "disable"}]]  # Configure default mesh root SSID when it is not included by 
    radio_1: NotRequired[str]  # Configuration options for radio 1.
    radio_2: NotRequired[str]  # Configuration options for radio 2.
    radio_3: NotRequired[str]  # Configuration options for radio 3.
    radio_4: NotRequired[str]  # Configuration options for radio 4.
    image_download: NotRequired[Literal[{"description": "Enable WTP image download at join time", "help": "Enable WTP image download at join time.", "label": "Enable", "name": "enable"}, {"description": "Disable WTP image download at join time", "help": "Disable WTP image download at join time.", "label": "Disable", "name": "disable"}]]  # Enable/disable WTP image download.
    mesh_bridge_enable: NotRequired[Literal[{"description": "Use mesh Ethernet bridge local setting on the WTP", "help": "Use mesh Ethernet bridge local setting on the WTP.", "label": "Default", "name": "default"}, {"description": "Turn on mesh Ethernet bridge on the WTP", "help": "Turn on mesh Ethernet bridge on the WTP.", "label": "Enable", "name": "enable"}, {"description": "Turn off mesh Ethernet bridge on the WTP", "help": "Turn off mesh Ethernet bridge on the WTP.", "label": "Disable", "name": "disable"}]]  # Enable/disable mesh Ethernet bridge when WTP is configured a
    purdue_level: NotRequired[Literal[{"description": "Level 1 - Basic Control    1", "help": "Level 1 - Basic Control", "label": "1", "name": "1"}, {"help": "Level 1.5", "label": "1.5", "name": "1.5"}, {"help": "Level 2 - Area Supervisory Control", "label": "2", "name": "2"}, {"help": "Level 2.5", "label": "2.5", "name": "2.5"}, {"help": "Level 3 - Operations \u0026 Control", "label": "3", "name": "3"}, {"help": "Level 3.5", "label": "3.5", "name": "3.5"}, {"help": "Level 4 - Business Planning \u0026 Logistics", "label": "4", "name": "4"}, {"description": "Level 5", "help": "Level 5 - Enterprise Network", "label": "5", "name": "5"}, {"help": "Level 5.5", "label": "5.5", "name": "5.5"}]]  # Purdue Level of this WTP.
    coordinate_latitude: NotRequired[str]  # WTP latitude coordinate.
    coordinate_longitude: NotRequired[str]  # WTP longitude coordinate.


class Wtp:
    """
    Configure Wireless Termination Points (WTPs), that is, FortiAPs or APs to be managed by FortiGate.
    
    Path: wireless_controller/wtp
    Category: cmdb
    Primary Key: wtp-id
    """
    
    # Overloads for get() with response_mode="object"
    @overload
    def get(
        self,
        wtp_id: str | None = ...,
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
        wtp_id: str,
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
        wtp_id: str | None = ...,
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
        wtp_id: str | None = ...,
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
        wtp_id: str | None = ...,
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
        payload_dict: WtpPayload | None = ...,
        wtp_id: str | None = ...,
        index: int | None = ...,
        uuid: str | None = ...,
        admin: Literal[{"description": "FortiGate wireless controller discovers the WTP, AP, or FortiAP though discovery or join request messages", "help": "FortiGate wireless controller discovers the WTP, AP, or FortiAP though discovery or join request messages.", "label": "Discovered", "name": "discovered"}, {"description": "FortiGate wireless controller is configured to not provide service to this WTP", "help": "FortiGate wireless controller is configured to not provide service to this WTP.", "label": "Disable", "name": "disable"}, {"description": "FortiGate wireless controller is configured to provide service to this WTP", "help": "FortiGate wireless controller is configured to provide service to this WTP.", "label": "Enable", "name": "enable"}] | None = ...,
        name: str | None = ...,
        location: str | None = ...,
        comment: str | None = ...,
        region: str | None = ...,
        region_x: str | None = ...,
        region_y: str | None = ...,
        firmware_provision: str | None = ...,
        firmware_provision_latest: Literal[{"description": "Do not automatically provision the latest available firmware", "help": "Do not automatically provision the latest available firmware.", "label": "Disable", "name": "disable"}, {"description": "Automatically attempt a one-time upgrade to the latest available firmware version", "help": "Automatically attempt a one-time upgrade to the latest available firmware version.", "label": "Once", "name": "once"}] | None = ...,
        wtp_profile: str | None = ...,
        apcfg_profile: str | None = ...,
        bonjour_profile: str | None = ...,
        ble_major_id: int | None = ...,
        ble_minor_id: int | None = ...,
        override_led_state: Literal[{"description": "Override the WTP profile LED state", "help": "Override the WTP profile LED state.", "label": "Enable", "name": "enable"}, {"description": "Use the WTP profile LED state", "help": "Use the WTP profile LED state.", "label": "Disable", "name": "disable"}] | None = ...,
        led_state: Literal[{"description": "Allow the LEDs on this FortiAP to light", "help": "Allow the LEDs on this FortiAP to light.", "label": "Enable", "name": "enable"}, {"description": "Keep the LEDs on this FortiAP off", "help": "Keep the LEDs on this FortiAP off.", "label": "Disable", "name": "disable"}] | None = ...,
        override_wan_port_mode: Literal[{"description": "Override the WTP profile wan-port-mode", "help": "Override the WTP profile wan-port-mode.", "label": "Enable", "name": "enable"}, {"description": "Use the wan-port-mode in the WTP profile", "help": "Use the wan-port-mode in the WTP profile.", "label": "Disable", "name": "disable"}] | None = ...,
        wan_port_mode: Literal[{"description": "Use the FortiAP WAN port as a LAN port", "help": "Use the FortiAP WAN port as a LAN port.", "label": "Wan Lan", "name": "wan-lan"}, {"description": "Do not use the WAN port as a LAN port", "help": "Do not use the WAN port as a LAN port.", "label": "Wan Only", "name": "wan-only"}] | None = ...,
        override_ip_fragment: Literal[{"description": "Override the WTP profile IP fragment prevention setting", "help": "Override the WTP profile IP fragment prevention setting.", "label": "Enable", "name": "enable"}, {"description": "Use the WTP profile IP fragment prevention setting", "help": "Use the WTP profile IP fragment prevention setting.", "label": "Disable", "name": "disable"}] | None = ...,
        ip_fragment_preventing: Literal[{"description": "TCP maximum segment size adjustment", "help": "TCP maximum segment size adjustment.", "label": "Tcp Mss Adjust", "name": "tcp-mss-adjust"}, {"description": "Drop packet and send ICMP Destination Unreachable", "help": "Drop packet and send ICMP Destination Unreachable", "label": "Icmp Unreachable", "name": "icmp-unreachable"}] | None = ...,
        tun_mtu_uplink: int | None = ...,
        tun_mtu_downlink: int | None = ...,
        override_split_tunnel: Literal[{"description": "Override the WTP profile split tunneling setting", "help": "Override the WTP profile split tunneling setting.", "label": "Enable", "name": "enable"}, {"description": "Use the WTP profile split tunneling setting", "help": "Use the WTP profile split tunneling setting.", "label": "Disable", "name": "disable"}] | None = ...,
        split_tunneling_acl_path: Literal[{"description": "Split tunneling ACL list traffic will be tunnel", "help": "Split tunneling ACL list traffic will be tunnel.", "label": "Tunnel", "name": "tunnel"}, {"description": "Split tunneling ACL list traffic will be local NATed", "help": "Split tunneling ACL list traffic will be local NATed.", "label": "Local", "name": "local"}] | None = ...,
        split_tunneling_acl_local_ap_subnet: Literal[{"description": "Enable automatically adding local subnetwork of FortiAP to split-tunneling ACL", "help": "Enable automatically adding local subnetwork of FortiAP to split-tunneling ACL.", "label": "Enable", "name": "enable"}, {"description": "Disable automatically adding local subnetwork of FortiAP to split-tunneling ACL", "help": "Disable automatically adding local subnetwork of FortiAP to split-tunneling ACL.", "label": "Disable", "name": "disable"}] | None = ...,
        split_tunneling_acl: list[dict[str, Any]] | None = ...,
        override_lan: Literal[{"description": "Override the WTP profile LAN port setting", "help": "Override the WTP profile LAN port setting.", "label": "Enable", "name": "enable"}, {"description": "Use the WTP profile LAN port setting", "help": "Use the WTP profile LAN port setting.", "label": "Disable", "name": "disable"}] | None = ...,
        lan: str | None = ...,
        override_allowaccess: Literal[{"description": "Override the WTP profile management access configuration", "help": "Override the WTP profile management access configuration.", "label": "Enable", "name": "enable"}, {"description": "Use the WTP profile management access configuration", "help": "Use the WTP profile management access configuration.", "label": "Disable", "name": "disable"}] | None = ...,
        allowaccess: Literal[{"description": "HTTPS access", "help": "HTTPS access.", "label": "Https", "name": "https"}, {"description": "SSH access", "help": "SSH access.", "label": "Ssh", "name": "ssh"}, {"description": "SNMP access", "help": "SNMP access.", "label": "Snmp", "name": "snmp"}] | None = ...,
        override_login_passwd_change: Literal[{"description": "Override the WTP profile login-password (administrator password) setting", "help": "Override the WTP profile login-password (administrator password) setting.", "label": "Enable", "name": "enable"}, {"description": "Use the the WTP profile login-password (administrator password) setting", "help": "Use the the WTP profile login-password (administrator password) setting.", "label": "Disable", "name": "disable"}] | None = ...,
        login_passwd_change: Literal[{"description": "Change the managed WTP, FortiAP or AP\u0027s administrator password", "help": "Change the managed WTP, FortiAP or AP\u0027s administrator password. Use the login-password option to set the password.", "label": "Yes", "name": "yes"}, {"description": "Keep the managed WTP, FortiAP or AP\u0027s administrator password set to the factory default", "help": "Keep the managed WTP, FortiAP or AP\u0027s administrator password set to the factory default.", "label": "Default", "name": "default"}, {"description": "Do not change the managed WTP, FortiAP or AP\u0027s administrator password", "help": "Do not change the managed WTP, FortiAP or AP\u0027s administrator password.", "label": "No", "name": "no"}] | None = ...,
        login_passwd: str | None = ...,
        override_default_mesh_root: Literal[{"description": "Override the WTP profile default mesh root SSID setting", "help": "Override the WTP profile default mesh root SSID setting.", "label": "Enable", "name": "enable"}, {"description": "Use the WTP profile default mesh root SSID setting", "help": "Use the WTP profile default mesh root SSID setting.", "label": "Disable", "name": "disable"}] | None = ...,
        default_mesh_root: Literal[{"description": "Enable default mesh root SSID if it is not included by radio\u0027s SSID configuration", "help": "Enable default mesh root SSID if it is not included by radio\u0027s SSID configuration.", "label": "Enable", "name": "enable"}, {"description": "Do not enable default mesh root SSID if it is not included by radio\u0027s SSID configuration", "help": "Do not enable default mesh root SSID if it is not included by radio\u0027s SSID configuration.", "label": "Disable", "name": "disable"}] | None = ...,
        radio_1: str | None = ...,
        radio_2: str | None = ...,
        radio_3: str | None = ...,
        radio_4: str | None = ...,
        image_download: Literal[{"description": "Enable WTP image download at join time", "help": "Enable WTP image download at join time.", "label": "Enable", "name": "enable"}, {"description": "Disable WTP image download at join time", "help": "Disable WTP image download at join time.", "label": "Disable", "name": "disable"}] | None = ...,
        mesh_bridge_enable: Literal[{"description": "Use mesh Ethernet bridge local setting on the WTP", "help": "Use mesh Ethernet bridge local setting on the WTP.", "label": "Default", "name": "default"}, {"description": "Turn on mesh Ethernet bridge on the WTP", "help": "Turn on mesh Ethernet bridge on the WTP.", "label": "Enable", "name": "enable"}, {"description": "Turn off mesh Ethernet bridge on the WTP", "help": "Turn off mesh Ethernet bridge on the WTP.", "label": "Disable", "name": "disable"}] | None = ...,
        purdue_level: Literal[{"description": "Level 1 - Basic Control    1", "help": "Level 1 - Basic Control", "label": "1", "name": "1"}, {"help": "Level 1.5", "label": "1.5", "name": "1.5"}, {"help": "Level 2 - Area Supervisory Control", "label": "2", "name": "2"}, {"help": "Level 2.5", "label": "2.5", "name": "2.5"}, {"help": "Level 3 - Operations \u0026 Control", "label": "3", "name": "3"}, {"help": "Level 3.5", "label": "3.5", "name": "3.5"}, {"help": "Level 4 - Business Planning \u0026 Logistics", "label": "4", "name": "4"}, {"description": "Level 5", "help": "Level 5 - Enterprise Network", "label": "5", "name": "5"}, {"help": "Level 5.5", "label": "5.5", "name": "5.5"}] | None = ...,
        coordinate_latitude: str | None = ...,
        coordinate_longitude: str | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: WtpPayload | None = ...,
        wtp_id: str | None = ...,
        index: int | None = ...,
        uuid: str | None = ...,
        admin: Literal[{"description": "FortiGate wireless controller discovers the WTP, AP, or FortiAP though discovery or join request messages", "help": "FortiGate wireless controller discovers the WTP, AP, or FortiAP though discovery or join request messages.", "label": "Discovered", "name": "discovered"}, {"description": "FortiGate wireless controller is configured to not provide service to this WTP", "help": "FortiGate wireless controller is configured to not provide service to this WTP.", "label": "Disable", "name": "disable"}, {"description": "FortiGate wireless controller is configured to provide service to this WTP", "help": "FortiGate wireless controller is configured to provide service to this WTP.", "label": "Enable", "name": "enable"}] | None = ...,
        name: str | None = ...,
        location: str | None = ...,
        comment: str | None = ...,
        region: str | None = ...,
        region_x: str | None = ...,
        region_y: str | None = ...,
        firmware_provision: str | None = ...,
        firmware_provision_latest: Literal[{"description": "Do not automatically provision the latest available firmware", "help": "Do not automatically provision the latest available firmware.", "label": "Disable", "name": "disable"}, {"description": "Automatically attempt a one-time upgrade to the latest available firmware version", "help": "Automatically attempt a one-time upgrade to the latest available firmware version.", "label": "Once", "name": "once"}] | None = ...,
        wtp_profile: str | None = ...,
        apcfg_profile: str | None = ...,
        bonjour_profile: str | None = ...,
        ble_major_id: int | None = ...,
        ble_minor_id: int | None = ...,
        override_led_state: Literal[{"description": "Override the WTP profile LED state", "help": "Override the WTP profile LED state.", "label": "Enable", "name": "enable"}, {"description": "Use the WTP profile LED state", "help": "Use the WTP profile LED state.", "label": "Disable", "name": "disable"}] | None = ...,
        led_state: Literal[{"description": "Allow the LEDs on this FortiAP to light", "help": "Allow the LEDs on this FortiAP to light.", "label": "Enable", "name": "enable"}, {"description": "Keep the LEDs on this FortiAP off", "help": "Keep the LEDs on this FortiAP off.", "label": "Disable", "name": "disable"}] | None = ...,
        override_wan_port_mode: Literal[{"description": "Override the WTP profile wan-port-mode", "help": "Override the WTP profile wan-port-mode.", "label": "Enable", "name": "enable"}, {"description": "Use the wan-port-mode in the WTP profile", "help": "Use the wan-port-mode in the WTP profile.", "label": "Disable", "name": "disable"}] | None = ...,
        wan_port_mode: Literal[{"description": "Use the FortiAP WAN port as a LAN port", "help": "Use the FortiAP WAN port as a LAN port.", "label": "Wan Lan", "name": "wan-lan"}, {"description": "Do not use the WAN port as a LAN port", "help": "Do not use the WAN port as a LAN port.", "label": "Wan Only", "name": "wan-only"}] | None = ...,
        override_ip_fragment: Literal[{"description": "Override the WTP profile IP fragment prevention setting", "help": "Override the WTP profile IP fragment prevention setting.", "label": "Enable", "name": "enable"}, {"description": "Use the WTP profile IP fragment prevention setting", "help": "Use the WTP profile IP fragment prevention setting.", "label": "Disable", "name": "disable"}] | None = ...,
        ip_fragment_preventing: Literal[{"description": "TCP maximum segment size adjustment", "help": "TCP maximum segment size adjustment.", "label": "Tcp Mss Adjust", "name": "tcp-mss-adjust"}, {"description": "Drop packet and send ICMP Destination Unreachable", "help": "Drop packet and send ICMP Destination Unreachable", "label": "Icmp Unreachable", "name": "icmp-unreachable"}] | None = ...,
        tun_mtu_uplink: int | None = ...,
        tun_mtu_downlink: int | None = ...,
        override_split_tunnel: Literal[{"description": "Override the WTP profile split tunneling setting", "help": "Override the WTP profile split tunneling setting.", "label": "Enable", "name": "enable"}, {"description": "Use the WTP profile split tunneling setting", "help": "Use the WTP profile split tunneling setting.", "label": "Disable", "name": "disable"}] | None = ...,
        split_tunneling_acl_path: Literal[{"description": "Split tunneling ACL list traffic will be tunnel", "help": "Split tunneling ACL list traffic will be tunnel.", "label": "Tunnel", "name": "tunnel"}, {"description": "Split tunneling ACL list traffic will be local NATed", "help": "Split tunneling ACL list traffic will be local NATed.", "label": "Local", "name": "local"}] | None = ...,
        split_tunneling_acl_local_ap_subnet: Literal[{"description": "Enable automatically adding local subnetwork of FortiAP to split-tunneling ACL", "help": "Enable automatically adding local subnetwork of FortiAP to split-tunneling ACL.", "label": "Enable", "name": "enable"}, {"description": "Disable automatically adding local subnetwork of FortiAP to split-tunneling ACL", "help": "Disable automatically adding local subnetwork of FortiAP to split-tunneling ACL.", "label": "Disable", "name": "disable"}] | None = ...,
        split_tunneling_acl: list[dict[str, Any]] | None = ...,
        override_lan: Literal[{"description": "Override the WTP profile LAN port setting", "help": "Override the WTP profile LAN port setting.", "label": "Enable", "name": "enable"}, {"description": "Use the WTP profile LAN port setting", "help": "Use the WTP profile LAN port setting.", "label": "Disable", "name": "disable"}] | None = ...,
        lan: str | None = ...,
        override_allowaccess: Literal[{"description": "Override the WTP profile management access configuration", "help": "Override the WTP profile management access configuration.", "label": "Enable", "name": "enable"}, {"description": "Use the WTP profile management access configuration", "help": "Use the WTP profile management access configuration.", "label": "Disable", "name": "disable"}] | None = ...,
        allowaccess: Literal[{"description": "HTTPS access", "help": "HTTPS access.", "label": "Https", "name": "https"}, {"description": "SSH access", "help": "SSH access.", "label": "Ssh", "name": "ssh"}, {"description": "SNMP access", "help": "SNMP access.", "label": "Snmp", "name": "snmp"}] | None = ...,
        override_login_passwd_change: Literal[{"description": "Override the WTP profile login-password (administrator password) setting", "help": "Override the WTP profile login-password (administrator password) setting.", "label": "Enable", "name": "enable"}, {"description": "Use the the WTP profile login-password (administrator password) setting", "help": "Use the the WTP profile login-password (administrator password) setting.", "label": "Disable", "name": "disable"}] | None = ...,
        login_passwd_change: Literal[{"description": "Change the managed WTP, FortiAP or AP\u0027s administrator password", "help": "Change the managed WTP, FortiAP or AP\u0027s administrator password. Use the login-password option to set the password.", "label": "Yes", "name": "yes"}, {"description": "Keep the managed WTP, FortiAP or AP\u0027s administrator password set to the factory default", "help": "Keep the managed WTP, FortiAP or AP\u0027s administrator password set to the factory default.", "label": "Default", "name": "default"}, {"description": "Do not change the managed WTP, FortiAP or AP\u0027s administrator password", "help": "Do not change the managed WTP, FortiAP or AP\u0027s administrator password.", "label": "No", "name": "no"}] | None = ...,
        login_passwd: str | None = ...,
        override_default_mesh_root: Literal[{"description": "Override the WTP profile default mesh root SSID setting", "help": "Override the WTP profile default mesh root SSID setting.", "label": "Enable", "name": "enable"}, {"description": "Use the WTP profile default mesh root SSID setting", "help": "Use the WTP profile default mesh root SSID setting.", "label": "Disable", "name": "disable"}] | None = ...,
        default_mesh_root: Literal[{"description": "Enable default mesh root SSID if it is not included by radio\u0027s SSID configuration", "help": "Enable default mesh root SSID if it is not included by radio\u0027s SSID configuration.", "label": "Enable", "name": "enable"}, {"description": "Do not enable default mesh root SSID if it is not included by radio\u0027s SSID configuration", "help": "Do not enable default mesh root SSID if it is not included by radio\u0027s SSID configuration.", "label": "Disable", "name": "disable"}] | None = ...,
        radio_1: str | None = ...,
        radio_2: str | None = ...,
        radio_3: str | None = ...,
        radio_4: str | None = ...,
        image_download: Literal[{"description": "Enable WTP image download at join time", "help": "Enable WTP image download at join time.", "label": "Enable", "name": "enable"}, {"description": "Disable WTP image download at join time", "help": "Disable WTP image download at join time.", "label": "Disable", "name": "disable"}] | None = ...,
        mesh_bridge_enable: Literal[{"description": "Use mesh Ethernet bridge local setting on the WTP", "help": "Use mesh Ethernet bridge local setting on the WTP.", "label": "Default", "name": "default"}, {"description": "Turn on mesh Ethernet bridge on the WTP", "help": "Turn on mesh Ethernet bridge on the WTP.", "label": "Enable", "name": "enable"}, {"description": "Turn off mesh Ethernet bridge on the WTP", "help": "Turn off mesh Ethernet bridge on the WTP.", "label": "Disable", "name": "disable"}] | None = ...,
        purdue_level: Literal[{"description": "Level 1 - Basic Control    1", "help": "Level 1 - Basic Control", "label": "1", "name": "1"}, {"help": "Level 1.5", "label": "1.5", "name": "1.5"}, {"help": "Level 2 - Area Supervisory Control", "label": "2", "name": "2"}, {"help": "Level 2.5", "label": "2.5", "name": "2.5"}, {"help": "Level 3 - Operations \u0026 Control", "label": "3", "name": "3"}, {"help": "Level 3.5", "label": "3.5", "name": "3.5"}, {"help": "Level 4 - Business Planning \u0026 Logistics", "label": "4", "name": "4"}, {"description": "Level 5", "help": "Level 5 - Enterprise Network", "label": "5", "name": "5"}, {"help": "Level 5.5", "label": "5.5", "name": "5.5"}] | None = ...,
        coordinate_latitude: str | None = ...,
        coordinate_longitude: str | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def delete(
        self,
        wtp_id: str | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def exists(
        self,
        wtp_id: str,
        vdom: str | bool | None = ...,
    ) -> Union[bool, Coroutine[Any, Any, bool]]: ...
    
    def set(
        self,
        payload_dict: WtpPayload | None = ...,
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
    "Wtp",
    "WtpPayload",
]