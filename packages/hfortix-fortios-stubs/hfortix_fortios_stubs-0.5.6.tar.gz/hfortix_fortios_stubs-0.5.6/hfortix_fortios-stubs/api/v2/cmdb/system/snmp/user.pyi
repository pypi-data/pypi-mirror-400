from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class UserPayload(TypedDict, total=False):
    """
    Type hints for system/snmp/user payload fields.
    
    SNMP user configuration.
    
    **Related Resources:**

    Dependencies (resources this endpoint references):
        - :class:`~.system.interface.InterfaceEndpoint` (via: interface)
        - :class:`~.system.snmp.mib-view.MibViewEndpoint` (via: mib-view)

    **Usage:**
        payload: UserPayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    name: str  # SNMP user name.
    status: NotRequired[Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]]  # Enable/disable this SNMP user.
    trap_status: NotRequired[Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]]  # Enable/disable traps for this SNMP user.
    trap_lport: NotRequired[int]  # SNMPv3 local trap port (default = 162).
    trap_rport: NotRequired[int]  # SNMPv3 trap remote port (default = 162).
    queries: NotRequired[Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]]  # Enable/disable SNMP queries for this user.
    query_port: NotRequired[int]  # SNMPv3 query port (default = 161).
    notify_hosts: NotRequired[list[dict[str, Any]]]  # SNMP managers to send notifications (traps) to.
    notify_hosts6: NotRequired[list[dict[str, Any]]]  # IPv6 SNMP managers to send notifications (traps) to.
    source_ip: NotRequired[str]  # Source IP for SNMP trap.
    source_ipv6: NotRequired[str]  # Source IPv6 for SNMP trap.
    ha_direct: NotRequired[Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]]  # Enable/disable direct management of HA cluster members.
    events: NotRequired[Literal[{"description": "Send a trap when CPU usage is high", "help": "Send a trap when CPU usage is high.", "label": "Cpu High", "name": "cpu-high"}, {"description": "Send a trap when used memory is high, free memory is low, or freeable memory is high", "help": "Send a trap when used memory is high, free memory is low, or freeable memory is high.", "label": "Mem Low", "name": "mem-low"}, {"description": "Send a trap when log disk space becomes low", "help": "Send a trap when log disk space becomes low.", "label": "Log Full", "name": "log-full"}, {"description": "Send a trap when an interface IP address is changed", "help": "Send a trap when an interface IP address is changed.", "label": "Intf Ip", "name": "intf-ip"}, {"description": "Send a trap when a VPN tunnel comes up", "help": "Send a trap when a VPN tunnel comes up.", "label": "Vpn Tun Up", "name": "vpn-tun-up"}, {"description": "Send a trap when a VPN tunnel goes down", "help": "Send a trap when a VPN tunnel goes down.", "label": "Vpn Tun Down", "name": "vpn-tun-down"}, {"description": "Send a trap after an HA failover when the backup unit has taken over", "help": "Send a trap after an HA failover when the backup unit has taken over.", "label": "Ha Switch", "name": "ha-switch"}, {"description": "Send a trap when HA heartbeats are not received", "help": "Send a trap when HA heartbeats are not received.", "label": "Ha Hb Failure", "name": "ha-hb-failure"}, {"description": "Send a trap when IPS detects an attack", "help": "Send a trap when IPS detects an attack.", "label": "Ips Signature", "name": "ips-signature"}, {"description": "Send a trap when IPS finds an anomaly", "help": "Send a trap when IPS finds an anomaly.", "label": "Ips Anomaly", "name": "ips-anomaly"}, {"description": "Send a trap when AntiVirus finds a virus", "help": "Send a trap when AntiVirus finds a virus.", "label": "Av Virus", "name": "av-virus"}, {"description": "Send a trap when AntiVirus finds an oversized file", "help": "Send a trap when AntiVirus finds an oversized file.", "label": "Av Oversize", "name": "av-oversize"}, {"description": "Send a trap when AntiVirus finds file matching pattern", "help": "Send a trap when AntiVirus finds file matching pattern.", "label": "Av Pattern", "name": "av-pattern"}, {"description": "Send a trap when AntiVirus finds a fragmented file", "help": "Send a trap when AntiVirus finds a fragmented file.", "label": "Av Fragmented", "name": "av-fragmented"}, {"description": "Send a trap when FortiManager interface changes", "help": "Send a trap when FortiManager interface changes. Send a FortiManager trap.", "label": "Fm If Change", "name": "fm-if-change"}, {"description": "Send a trap when a configuration change is made by a FortiGate administrator and the FortiGate is managed by FortiManager", "help": "Send a trap when a configuration change is made by a FortiGate administrator and the FortiGate is managed by FortiManager.", "label": "Fm Conf Change", "name": "fm-conf-change"}, {"description": "Send a trap when a BGP FSM transitions to the established state", "help": "Send a trap when a BGP FSM transitions to the established state.", "label": "Bgp Established", "name": "bgp-established"}, {"description": "Send a trap when a BGP FSM goes from a high numbered state to a lower numbered state", "help": "Send a trap when a BGP FSM goes from a high numbered state to a lower numbered state.", "label": "Bgp Backward Transition", "name": "bgp-backward-transition"}, {"description": "Send a trap when an HA cluster member goes up", "help": "Send a trap when an HA cluster member goes up.", "label": "Ha Member Up", "name": "ha-member-up"}, {"description": "Send a trap when an HA cluster member goes down", "help": "Send a trap when an HA cluster member goes down.", "label": "Ha Member Down", "name": "ha-member-down"}, {"description": "Send a trap when an entity MIB change occurs (RFC4133)", "help": "Send a trap when an entity MIB change occurs (RFC4133).", "label": "Ent Conf Change", "name": "ent-conf-change"}, {"description": "Send a trap when the FortiGate enters conserve mode", "help": "Send a trap when the FortiGate enters conserve mode.", "label": "Av Conserve", "name": "av-conserve"}, {"description": "Send a trap when the FortiGate enters bypass mode", "help": "Send a trap when the FortiGate enters bypass mode.", "label": "Av Bypass", "name": "av-bypass"}, {"description": "Send a trap when AntiVirus passes an oversized file", "help": "Send a trap when AntiVirus passes an oversized file.", "label": "Av Oversize Passed", "name": "av-oversize-passed"}, {"description": "Send a trap when AntiVirus blocks an oversized file", "help": "Send a trap when AntiVirus blocks an oversized file.", "label": "Av Oversize Blocked", "name": "av-oversize-blocked"}, {"description": "Send a trap when the IPS signature database or engine is updated", "help": "Send a trap when the IPS signature database or engine is updated.", "label": "Ips Pkg Update", "name": "ips-pkg-update"}, {"description": "Send a trap when the IPS network buffer is full", "help": "Send a trap when the IPS network buffer is full.", "label": "Ips Fail Open", "name": "ips-fail-open"}, {"description": "Send a trap when a FortiAnalyzer disconnects from the FortiGate", "help": "Send a trap when a FortiAnalyzer disconnects from the FortiGate.", "label": "Faz Disconnect", "name": "faz-disconnect"}, {"description": "Send a trap when Fortianalyzer main server failover and alternate server take over, or alternate server failover and main server take over", "help": "Send a trap when Fortianalyzer main server failover and alternate server take over, or alternate server failover and main server take over.", "label": "Faz", "name": "faz"}, {"description": "Send a trap when a managed FortiAP comes up", "help": "Send a trap when a managed FortiAP comes up.", "label": "Wc Ap Up", "name": "wc-ap-up"}, {"description": "Send a trap when a managed FortiAP goes down", "help": "Send a trap when a managed FortiAP goes down.", "label": "Wc Ap Down", "name": "wc-ap-down"}, {"description": "Send a trap when a FortiSwitch controller session comes up", "help": "Send a trap when a FortiSwitch controller session comes up.", "label": "Fswctl Session Up", "name": "fswctl-session-up"}, {"description": "Send a trap when a FortiSwitch controller session goes down", "help": "Send a trap when a FortiSwitch controller session goes down.", "label": "Fswctl Session Down", "name": "fswctl-session-down"}, {"description": "Send a trap when a server load balance real server goes down", "help": "Send a trap when a server load balance real server goes down.", "label": "Load Balance Real Server Down", "name": "load-balance-real-server-down"}, {"description": "Send a trap when a new device is found", "help": "Send a trap when a new device is found.", "label": "Device New", "name": "device-new"}, {"description": "Send a trap when per-CPU usage is high", "help": "Send a trap when per-CPU usage is high.", "label": "Per Cpu High", "name": "per-cpu-high"}, {"description": "Send a trap when the DHCP server exhausts the IP pool, an IP address already is in use, or a DHCP client interface received a DHCP-NAK", "help": "Send a trap when the DHCP server exhausts the IP pool, an IP address already is in use, or a DHCP client interface received a DHCP-NAK.", "label": "Dhcp", "name": "dhcp"}, {"description": "Send a trap about ippool usage", "help": "Send a trap about ippool usage.", "label": "Pool Usage", "name": "pool-usage"}, {"description": "Send a trap for ippool events", "help": "Send a trap for ippool events.", "label": "Ippool", "name": "ippool"}, {"description": "Send a trap for interface event", "help": "Send a trap for interface event.", "label": "Interface", "name": "interface"}, {"description": "Send a trap when there has been a change in the state of a non-virtual OSPF neighbor", "help": "Send a trap when there has been a change in the state of a non-virtual OSPF neighbor.", "label": "Ospf Nbr State Change", "name": "ospf-nbr-state-change"}, {"description": "Send a trap when there has been a change in the state of an OSPF virtual neighbor", "help": "Send a trap when there has been a change in the state of an OSPF virtual neighbor.", "label": "Ospf Virtnbr State Change", "name": "ospf-virtnbr-state-change"}, {"description": "Send a trap for bfd event", "help": "Send a trap for bfd event.", "label": "Bfd", "name": "bfd"}]]  # SNMP notifications (traps) to send.
    mib_view: NotRequired[str]  # SNMP access control MIB view.
    vdoms: NotRequired[list[dict[str, Any]]]  # SNMP access control VDOMs.
    security_level: NotRequired[Literal[{"description": "Message with no authentication and no privacy (encryption)", "help": "Message with no authentication and no privacy (encryption).", "label": "No Auth No Priv", "name": "no-auth-no-priv"}, {"description": "Message with authentication but no privacy (encryption)", "help": "Message with authentication but no privacy (encryption).", "label": "Auth No Priv", "name": "auth-no-priv"}, {"description": "Message with authentication and privacy (encryption)", "help": "Message with authentication and privacy (encryption).", "label": "Auth Priv", "name": "auth-priv"}]]  # Security level for message authentication and encryption.
    auth_proto: NotRequired[Literal[{"description": "HMAC-MD5-96 authentication protocol", "help": "HMAC-MD5-96 authentication protocol.", "label": "Md5", "name": "md5"}, {"description": "HMAC-SHA-96 authentication protocol", "help": "HMAC-SHA-96 authentication protocol.", "label": "Sha", "name": "sha"}, {"description": "HMAC-SHA224 authentication protocol", "help": "HMAC-SHA224 authentication protocol.", "label": "Sha224", "name": "sha224"}, {"description": "HMAC-SHA256 authentication protocol", "help": "HMAC-SHA256 authentication protocol.", "label": "Sha256", "name": "sha256"}, {"description": "HMAC-SHA384 authentication protocol", "help": "HMAC-SHA384 authentication protocol.", "label": "Sha384", "name": "sha384"}, {"description": "HMAC-SHA512 authentication protocol", "help": "HMAC-SHA512 authentication protocol.", "label": "Sha512", "name": "sha512"}]]  # Authentication protocol.
    auth_pwd: str  # Password for authentication protocol.
    priv_proto: NotRequired[Literal[{"description": "CFB128-AES-128 symmetric encryption protocol", "help": "CFB128-AES-128 symmetric encryption protocol.", "label": "Aes", "name": "aes"}, {"description": "CBC-DES symmetric encryption protocol", "help": "CBC-DES symmetric encryption protocol.", "label": "Des", "name": "des"}, {"description": "CFB128-AES-256 symmetric encryption protocol", "help": "CFB128-AES-256 symmetric encryption protocol.", "label": "Aes256", "name": "aes256"}, {"description": "CFB128-AES-256 symmetric encryption protocol compatible with CISCO", "help": "CFB128-AES-256 symmetric encryption protocol compatible with CISCO.", "label": "Aes256Cisco", "name": "aes256cisco"}]]  # Privacy (encryption) protocol.
    priv_pwd: str  # Password for privacy (encryption) protocol.
    interface_select_method: NotRequired[Literal[{"description": "Set outgoing interface automatically", "help": "Set outgoing interface automatically.", "label": "Auto", "name": "auto"}, {"description": "Set outgoing interface by SD-WAN or policy routing rules", "help": "Set outgoing interface by SD-WAN or policy routing rules.", "label": "Sdwan", "name": "sdwan"}, {"description": "Set outgoing interface manually", "help": "Set outgoing interface manually.", "label": "Specify", "name": "specify"}]]  # Specify how to select outgoing interface to reach server.
    interface: str  # Specify outgoing interface to reach server.
    vrf_select: NotRequired[int]  # VRF ID used for connection to server.


class User:
    """
    SNMP user configuration.
    
    Path: system/snmp/user
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
        payload_dict: UserPayload | None = ...,
        name: str | None = ...,
        status: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        trap_status: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        trap_lport: int | None = ...,
        trap_rport: int | None = ...,
        queries: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        query_port: int | None = ...,
        notify_hosts: list[dict[str, Any]] | None = ...,
        notify_hosts6: list[dict[str, Any]] | None = ...,
        source_ip: str | None = ...,
        source_ipv6: str | None = ...,
        ha_direct: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        events: Literal[{"description": "Send a trap when CPU usage is high", "help": "Send a trap when CPU usage is high.", "label": "Cpu High", "name": "cpu-high"}, {"description": "Send a trap when used memory is high, free memory is low, or freeable memory is high", "help": "Send a trap when used memory is high, free memory is low, or freeable memory is high.", "label": "Mem Low", "name": "mem-low"}, {"description": "Send a trap when log disk space becomes low", "help": "Send a trap when log disk space becomes low.", "label": "Log Full", "name": "log-full"}, {"description": "Send a trap when an interface IP address is changed", "help": "Send a trap when an interface IP address is changed.", "label": "Intf Ip", "name": "intf-ip"}, {"description": "Send a trap when a VPN tunnel comes up", "help": "Send a trap when a VPN tunnel comes up.", "label": "Vpn Tun Up", "name": "vpn-tun-up"}, {"description": "Send a trap when a VPN tunnel goes down", "help": "Send a trap when a VPN tunnel goes down.", "label": "Vpn Tun Down", "name": "vpn-tun-down"}, {"description": "Send a trap after an HA failover when the backup unit has taken over", "help": "Send a trap after an HA failover when the backup unit has taken over.", "label": "Ha Switch", "name": "ha-switch"}, {"description": "Send a trap when HA heartbeats are not received", "help": "Send a trap when HA heartbeats are not received.", "label": "Ha Hb Failure", "name": "ha-hb-failure"}, {"description": "Send a trap when IPS detects an attack", "help": "Send a trap when IPS detects an attack.", "label": "Ips Signature", "name": "ips-signature"}, {"description": "Send a trap when IPS finds an anomaly", "help": "Send a trap when IPS finds an anomaly.", "label": "Ips Anomaly", "name": "ips-anomaly"}, {"description": "Send a trap when AntiVirus finds a virus", "help": "Send a trap when AntiVirus finds a virus.", "label": "Av Virus", "name": "av-virus"}, {"description": "Send a trap when AntiVirus finds an oversized file", "help": "Send a trap when AntiVirus finds an oversized file.", "label": "Av Oversize", "name": "av-oversize"}, {"description": "Send a trap when AntiVirus finds file matching pattern", "help": "Send a trap when AntiVirus finds file matching pattern.", "label": "Av Pattern", "name": "av-pattern"}, {"description": "Send a trap when AntiVirus finds a fragmented file", "help": "Send a trap when AntiVirus finds a fragmented file.", "label": "Av Fragmented", "name": "av-fragmented"}, {"description": "Send a trap when FortiManager interface changes", "help": "Send a trap when FortiManager interface changes. Send a FortiManager trap.", "label": "Fm If Change", "name": "fm-if-change"}, {"description": "Send a trap when a configuration change is made by a FortiGate administrator and the FortiGate is managed by FortiManager", "help": "Send a trap when a configuration change is made by a FortiGate administrator and the FortiGate is managed by FortiManager.", "label": "Fm Conf Change", "name": "fm-conf-change"}, {"description": "Send a trap when a BGP FSM transitions to the established state", "help": "Send a trap when a BGP FSM transitions to the established state.", "label": "Bgp Established", "name": "bgp-established"}, {"description": "Send a trap when a BGP FSM goes from a high numbered state to a lower numbered state", "help": "Send a trap when a BGP FSM goes from a high numbered state to a lower numbered state.", "label": "Bgp Backward Transition", "name": "bgp-backward-transition"}, {"description": "Send a trap when an HA cluster member goes up", "help": "Send a trap when an HA cluster member goes up.", "label": "Ha Member Up", "name": "ha-member-up"}, {"description": "Send a trap when an HA cluster member goes down", "help": "Send a trap when an HA cluster member goes down.", "label": "Ha Member Down", "name": "ha-member-down"}, {"description": "Send a trap when an entity MIB change occurs (RFC4133)", "help": "Send a trap when an entity MIB change occurs (RFC4133).", "label": "Ent Conf Change", "name": "ent-conf-change"}, {"description": "Send a trap when the FortiGate enters conserve mode", "help": "Send a trap when the FortiGate enters conserve mode.", "label": "Av Conserve", "name": "av-conserve"}, {"description": "Send a trap when the FortiGate enters bypass mode", "help": "Send a trap when the FortiGate enters bypass mode.", "label": "Av Bypass", "name": "av-bypass"}, {"description": "Send a trap when AntiVirus passes an oversized file", "help": "Send a trap when AntiVirus passes an oversized file.", "label": "Av Oversize Passed", "name": "av-oversize-passed"}, {"description": "Send a trap when AntiVirus blocks an oversized file", "help": "Send a trap when AntiVirus blocks an oversized file.", "label": "Av Oversize Blocked", "name": "av-oversize-blocked"}, {"description": "Send a trap when the IPS signature database or engine is updated", "help": "Send a trap when the IPS signature database or engine is updated.", "label": "Ips Pkg Update", "name": "ips-pkg-update"}, {"description": "Send a trap when the IPS network buffer is full", "help": "Send a trap when the IPS network buffer is full.", "label": "Ips Fail Open", "name": "ips-fail-open"}, {"description": "Send a trap when a FortiAnalyzer disconnects from the FortiGate", "help": "Send a trap when a FortiAnalyzer disconnects from the FortiGate.", "label": "Faz Disconnect", "name": "faz-disconnect"}, {"description": "Send a trap when Fortianalyzer main server failover and alternate server take over, or alternate server failover and main server take over", "help": "Send a trap when Fortianalyzer main server failover and alternate server take over, or alternate server failover and main server take over.", "label": "Faz", "name": "faz"}, {"description": "Send a trap when a managed FortiAP comes up", "help": "Send a trap when a managed FortiAP comes up.", "label": "Wc Ap Up", "name": "wc-ap-up"}, {"description": "Send a trap when a managed FortiAP goes down", "help": "Send a trap when a managed FortiAP goes down.", "label": "Wc Ap Down", "name": "wc-ap-down"}, {"description": "Send a trap when a FortiSwitch controller session comes up", "help": "Send a trap when a FortiSwitch controller session comes up.", "label": "Fswctl Session Up", "name": "fswctl-session-up"}, {"description": "Send a trap when a FortiSwitch controller session goes down", "help": "Send a trap when a FortiSwitch controller session goes down.", "label": "Fswctl Session Down", "name": "fswctl-session-down"}, {"description": "Send a trap when a server load balance real server goes down", "help": "Send a trap when a server load balance real server goes down.", "label": "Load Balance Real Server Down", "name": "load-balance-real-server-down"}, {"description": "Send a trap when a new device is found", "help": "Send a trap when a new device is found.", "label": "Device New", "name": "device-new"}, {"description": "Send a trap when per-CPU usage is high", "help": "Send a trap when per-CPU usage is high.", "label": "Per Cpu High", "name": "per-cpu-high"}, {"description": "Send a trap when the DHCP server exhausts the IP pool, an IP address already is in use, or a DHCP client interface received a DHCP-NAK", "help": "Send a trap when the DHCP server exhausts the IP pool, an IP address already is in use, or a DHCP client interface received a DHCP-NAK.", "label": "Dhcp", "name": "dhcp"}, {"description": "Send a trap about ippool usage", "help": "Send a trap about ippool usage.", "label": "Pool Usage", "name": "pool-usage"}, {"description": "Send a trap for ippool events", "help": "Send a trap for ippool events.", "label": "Ippool", "name": "ippool"}, {"description": "Send a trap for interface event", "help": "Send a trap for interface event.", "label": "Interface", "name": "interface"}, {"description": "Send a trap when there has been a change in the state of a non-virtual OSPF neighbor", "help": "Send a trap when there has been a change in the state of a non-virtual OSPF neighbor.", "label": "Ospf Nbr State Change", "name": "ospf-nbr-state-change"}, {"description": "Send a trap when there has been a change in the state of an OSPF virtual neighbor", "help": "Send a trap when there has been a change in the state of an OSPF virtual neighbor.", "label": "Ospf Virtnbr State Change", "name": "ospf-virtnbr-state-change"}, {"description": "Send a trap for bfd event", "help": "Send a trap for bfd event.", "label": "Bfd", "name": "bfd"}] | None = ...,
        mib_view: str | None = ...,
        vdoms: list[dict[str, Any]] | None = ...,
        security_level: Literal[{"description": "Message with no authentication and no privacy (encryption)", "help": "Message with no authentication and no privacy (encryption).", "label": "No Auth No Priv", "name": "no-auth-no-priv"}, {"description": "Message with authentication but no privacy (encryption)", "help": "Message with authentication but no privacy (encryption).", "label": "Auth No Priv", "name": "auth-no-priv"}, {"description": "Message with authentication and privacy (encryption)", "help": "Message with authentication and privacy (encryption).", "label": "Auth Priv", "name": "auth-priv"}] | None = ...,
        auth_proto: Literal[{"description": "HMAC-MD5-96 authentication protocol", "help": "HMAC-MD5-96 authentication protocol.", "label": "Md5", "name": "md5"}, {"description": "HMAC-SHA-96 authentication protocol", "help": "HMAC-SHA-96 authentication protocol.", "label": "Sha", "name": "sha"}, {"description": "HMAC-SHA224 authentication protocol", "help": "HMAC-SHA224 authentication protocol.", "label": "Sha224", "name": "sha224"}, {"description": "HMAC-SHA256 authentication protocol", "help": "HMAC-SHA256 authentication protocol.", "label": "Sha256", "name": "sha256"}, {"description": "HMAC-SHA384 authentication protocol", "help": "HMAC-SHA384 authentication protocol.", "label": "Sha384", "name": "sha384"}, {"description": "HMAC-SHA512 authentication protocol", "help": "HMAC-SHA512 authentication protocol.", "label": "Sha512", "name": "sha512"}] | None = ...,
        auth_pwd: str | None = ...,
        priv_proto: Literal[{"description": "CFB128-AES-128 symmetric encryption protocol", "help": "CFB128-AES-128 symmetric encryption protocol.", "label": "Aes", "name": "aes"}, {"description": "CBC-DES symmetric encryption protocol", "help": "CBC-DES symmetric encryption protocol.", "label": "Des", "name": "des"}, {"description": "CFB128-AES-256 symmetric encryption protocol", "help": "CFB128-AES-256 symmetric encryption protocol.", "label": "Aes256", "name": "aes256"}, {"description": "CFB128-AES-256 symmetric encryption protocol compatible with CISCO", "help": "CFB128-AES-256 symmetric encryption protocol compatible with CISCO.", "label": "Aes256Cisco", "name": "aes256cisco"}] | None = ...,
        priv_pwd: str | None = ...,
        interface_select_method: Literal[{"description": "Set outgoing interface automatically", "help": "Set outgoing interface automatically.", "label": "Auto", "name": "auto"}, {"description": "Set outgoing interface by SD-WAN or policy routing rules", "help": "Set outgoing interface by SD-WAN or policy routing rules.", "label": "Sdwan", "name": "sdwan"}, {"description": "Set outgoing interface manually", "help": "Set outgoing interface manually.", "label": "Specify", "name": "specify"}] | None = ...,
        interface: str | None = ...,
        vrf_select: int | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: UserPayload | None = ...,
        name: str | None = ...,
        status: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        trap_status: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        trap_lport: int | None = ...,
        trap_rport: int | None = ...,
        queries: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        query_port: int | None = ...,
        notify_hosts: list[dict[str, Any]] | None = ...,
        notify_hosts6: list[dict[str, Any]] | None = ...,
        source_ip: str | None = ...,
        source_ipv6: str | None = ...,
        ha_direct: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        events: Literal[{"description": "Send a trap when CPU usage is high", "help": "Send a trap when CPU usage is high.", "label": "Cpu High", "name": "cpu-high"}, {"description": "Send a trap when used memory is high, free memory is low, or freeable memory is high", "help": "Send a trap when used memory is high, free memory is low, or freeable memory is high.", "label": "Mem Low", "name": "mem-low"}, {"description": "Send a trap when log disk space becomes low", "help": "Send a trap when log disk space becomes low.", "label": "Log Full", "name": "log-full"}, {"description": "Send a trap when an interface IP address is changed", "help": "Send a trap when an interface IP address is changed.", "label": "Intf Ip", "name": "intf-ip"}, {"description": "Send a trap when a VPN tunnel comes up", "help": "Send a trap when a VPN tunnel comes up.", "label": "Vpn Tun Up", "name": "vpn-tun-up"}, {"description": "Send a trap when a VPN tunnel goes down", "help": "Send a trap when a VPN tunnel goes down.", "label": "Vpn Tun Down", "name": "vpn-tun-down"}, {"description": "Send a trap after an HA failover when the backup unit has taken over", "help": "Send a trap after an HA failover when the backup unit has taken over.", "label": "Ha Switch", "name": "ha-switch"}, {"description": "Send a trap when HA heartbeats are not received", "help": "Send a trap when HA heartbeats are not received.", "label": "Ha Hb Failure", "name": "ha-hb-failure"}, {"description": "Send a trap when IPS detects an attack", "help": "Send a trap when IPS detects an attack.", "label": "Ips Signature", "name": "ips-signature"}, {"description": "Send a trap when IPS finds an anomaly", "help": "Send a trap when IPS finds an anomaly.", "label": "Ips Anomaly", "name": "ips-anomaly"}, {"description": "Send a trap when AntiVirus finds a virus", "help": "Send a trap when AntiVirus finds a virus.", "label": "Av Virus", "name": "av-virus"}, {"description": "Send a trap when AntiVirus finds an oversized file", "help": "Send a trap when AntiVirus finds an oversized file.", "label": "Av Oversize", "name": "av-oversize"}, {"description": "Send a trap when AntiVirus finds file matching pattern", "help": "Send a trap when AntiVirus finds file matching pattern.", "label": "Av Pattern", "name": "av-pattern"}, {"description": "Send a trap when AntiVirus finds a fragmented file", "help": "Send a trap when AntiVirus finds a fragmented file.", "label": "Av Fragmented", "name": "av-fragmented"}, {"description": "Send a trap when FortiManager interface changes", "help": "Send a trap when FortiManager interface changes. Send a FortiManager trap.", "label": "Fm If Change", "name": "fm-if-change"}, {"description": "Send a trap when a configuration change is made by a FortiGate administrator and the FortiGate is managed by FortiManager", "help": "Send a trap when a configuration change is made by a FortiGate administrator and the FortiGate is managed by FortiManager.", "label": "Fm Conf Change", "name": "fm-conf-change"}, {"description": "Send a trap when a BGP FSM transitions to the established state", "help": "Send a trap when a BGP FSM transitions to the established state.", "label": "Bgp Established", "name": "bgp-established"}, {"description": "Send a trap when a BGP FSM goes from a high numbered state to a lower numbered state", "help": "Send a trap when a BGP FSM goes from a high numbered state to a lower numbered state.", "label": "Bgp Backward Transition", "name": "bgp-backward-transition"}, {"description": "Send a trap when an HA cluster member goes up", "help": "Send a trap when an HA cluster member goes up.", "label": "Ha Member Up", "name": "ha-member-up"}, {"description": "Send a trap when an HA cluster member goes down", "help": "Send a trap when an HA cluster member goes down.", "label": "Ha Member Down", "name": "ha-member-down"}, {"description": "Send a trap when an entity MIB change occurs (RFC4133)", "help": "Send a trap when an entity MIB change occurs (RFC4133).", "label": "Ent Conf Change", "name": "ent-conf-change"}, {"description": "Send a trap when the FortiGate enters conserve mode", "help": "Send a trap when the FortiGate enters conserve mode.", "label": "Av Conserve", "name": "av-conserve"}, {"description": "Send a trap when the FortiGate enters bypass mode", "help": "Send a trap when the FortiGate enters bypass mode.", "label": "Av Bypass", "name": "av-bypass"}, {"description": "Send a trap when AntiVirus passes an oversized file", "help": "Send a trap when AntiVirus passes an oversized file.", "label": "Av Oversize Passed", "name": "av-oversize-passed"}, {"description": "Send a trap when AntiVirus blocks an oversized file", "help": "Send a trap when AntiVirus blocks an oversized file.", "label": "Av Oversize Blocked", "name": "av-oversize-blocked"}, {"description": "Send a trap when the IPS signature database or engine is updated", "help": "Send a trap when the IPS signature database or engine is updated.", "label": "Ips Pkg Update", "name": "ips-pkg-update"}, {"description": "Send a trap when the IPS network buffer is full", "help": "Send a trap when the IPS network buffer is full.", "label": "Ips Fail Open", "name": "ips-fail-open"}, {"description": "Send a trap when a FortiAnalyzer disconnects from the FortiGate", "help": "Send a trap when a FortiAnalyzer disconnects from the FortiGate.", "label": "Faz Disconnect", "name": "faz-disconnect"}, {"description": "Send a trap when Fortianalyzer main server failover and alternate server take over, or alternate server failover and main server take over", "help": "Send a trap when Fortianalyzer main server failover and alternate server take over, or alternate server failover and main server take over.", "label": "Faz", "name": "faz"}, {"description": "Send a trap when a managed FortiAP comes up", "help": "Send a trap when a managed FortiAP comes up.", "label": "Wc Ap Up", "name": "wc-ap-up"}, {"description": "Send a trap when a managed FortiAP goes down", "help": "Send a trap when a managed FortiAP goes down.", "label": "Wc Ap Down", "name": "wc-ap-down"}, {"description": "Send a trap when a FortiSwitch controller session comes up", "help": "Send a trap when a FortiSwitch controller session comes up.", "label": "Fswctl Session Up", "name": "fswctl-session-up"}, {"description": "Send a trap when a FortiSwitch controller session goes down", "help": "Send a trap when a FortiSwitch controller session goes down.", "label": "Fswctl Session Down", "name": "fswctl-session-down"}, {"description": "Send a trap when a server load balance real server goes down", "help": "Send a trap when a server load balance real server goes down.", "label": "Load Balance Real Server Down", "name": "load-balance-real-server-down"}, {"description": "Send a trap when a new device is found", "help": "Send a trap when a new device is found.", "label": "Device New", "name": "device-new"}, {"description": "Send a trap when per-CPU usage is high", "help": "Send a trap when per-CPU usage is high.", "label": "Per Cpu High", "name": "per-cpu-high"}, {"description": "Send a trap when the DHCP server exhausts the IP pool, an IP address already is in use, or a DHCP client interface received a DHCP-NAK", "help": "Send a trap when the DHCP server exhausts the IP pool, an IP address already is in use, or a DHCP client interface received a DHCP-NAK.", "label": "Dhcp", "name": "dhcp"}, {"description": "Send a trap about ippool usage", "help": "Send a trap about ippool usage.", "label": "Pool Usage", "name": "pool-usage"}, {"description": "Send a trap for ippool events", "help": "Send a trap for ippool events.", "label": "Ippool", "name": "ippool"}, {"description": "Send a trap for interface event", "help": "Send a trap for interface event.", "label": "Interface", "name": "interface"}, {"description": "Send a trap when there has been a change in the state of a non-virtual OSPF neighbor", "help": "Send a trap when there has been a change in the state of a non-virtual OSPF neighbor.", "label": "Ospf Nbr State Change", "name": "ospf-nbr-state-change"}, {"description": "Send a trap when there has been a change in the state of an OSPF virtual neighbor", "help": "Send a trap when there has been a change in the state of an OSPF virtual neighbor.", "label": "Ospf Virtnbr State Change", "name": "ospf-virtnbr-state-change"}, {"description": "Send a trap for bfd event", "help": "Send a trap for bfd event.", "label": "Bfd", "name": "bfd"}] | None = ...,
        mib_view: str | None = ...,
        vdoms: list[dict[str, Any]] | None = ...,
        security_level: Literal[{"description": "Message with no authentication and no privacy (encryption)", "help": "Message with no authentication and no privacy (encryption).", "label": "No Auth No Priv", "name": "no-auth-no-priv"}, {"description": "Message with authentication but no privacy (encryption)", "help": "Message with authentication but no privacy (encryption).", "label": "Auth No Priv", "name": "auth-no-priv"}, {"description": "Message with authentication and privacy (encryption)", "help": "Message with authentication and privacy (encryption).", "label": "Auth Priv", "name": "auth-priv"}] | None = ...,
        auth_proto: Literal[{"description": "HMAC-MD5-96 authentication protocol", "help": "HMAC-MD5-96 authentication protocol.", "label": "Md5", "name": "md5"}, {"description": "HMAC-SHA-96 authentication protocol", "help": "HMAC-SHA-96 authentication protocol.", "label": "Sha", "name": "sha"}, {"description": "HMAC-SHA224 authentication protocol", "help": "HMAC-SHA224 authentication protocol.", "label": "Sha224", "name": "sha224"}, {"description": "HMAC-SHA256 authentication protocol", "help": "HMAC-SHA256 authentication protocol.", "label": "Sha256", "name": "sha256"}, {"description": "HMAC-SHA384 authentication protocol", "help": "HMAC-SHA384 authentication protocol.", "label": "Sha384", "name": "sha384"}, {"description": "HMAC-SHA512 authentication protocol", "help": "HMAC-SHA512 authentication protocol.", "label": "Sha512", "name": "sha512"}] | None = ...,
        auth_pwd: str | None = ...,
        priv_proto: Literal[{"description": "CFB128-AES-128 symmetric encryption protocol", "help": "CFB128-AES-128 symmetric encryption protocol.", "label": "Aes", "name": "aes"}, {"description": "CBC-DES symmetric encryption protocol", "help": "CBC-DES symmetric encryption protocol.", "label": "Des", "name": "des"}, {"description": "CFB128-AES-256 symmetric encryption protocol", "help": "CFB128-AES-256 symmetric encryption protocol.", "label": "Aes256", "name": "aes256"}, {"description": "CFB128-AES-256 symmetric encryption protocol compatible with CISCO", "help": "CFB128-AES-256 symmetric encryption protocol compatible with CISCO.", "label": "Aes256Cisco", "name": "aes256cisco"}] | None = ...,
        priv_pwd: str | None = ...,
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
        payload_dict: UserPayload | None = ...,
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
    "User",
    "UserPayload",
]