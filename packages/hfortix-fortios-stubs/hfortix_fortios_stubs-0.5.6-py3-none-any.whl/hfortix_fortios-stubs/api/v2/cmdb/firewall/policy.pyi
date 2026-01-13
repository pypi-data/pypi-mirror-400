from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class PolicyPayload(TypedDict, total=False):
    """
    Type hints for firewall/policy payload fields.
    
    Configure IPv4/IPv6 policies.
    
    **Related Resources:**

    Dependencies (resources this endpoint references):
        - :class:`~.antivirus.profile.ProfileEndpoint` (via: av-profile)
        - :class:`~.application.list.ListEndpoint` (via: application-list)
        - :class:`~.casb.profile.ProfileEndpoint` (via: casb-profile)
        - :class:`~.diameter-filter.profile.ProfileEndpoint` (via: diameter-filter-profile)
        - :class:`~.dlp.profile.ProfileEndpoint` (via: dlp-profile)
        - :class:`~.dnsfilter.profile.ProfileEndpoint` (via: dnsfilter-profile)
        - :class:`~.emailfilter.profile.ProfileEndpoint` (via: emailfilter-profile)
        - :class:`~.file-filter.profile.ProfileEndpoint` (via: file-filter-profile)
        - :class:`~.firewall.decrypted-traffic-mirror.DecryptedTrafficMirrorEndpoint` (via: decrypted-traffic-mirror)
        - :class:`~.firewall.identity-based-route.IdentityBasedRouteEndpoint` (via: identity-based-route)
        - ... and 28 more dependencies

    **Usage:**
        payload: PolicyPayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    policyid: NotRequired[int]  # Policy ID (0 - 4294967294).
    status: NotRequired[Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]]  # Enable or disable this policy.
    name: NotRequired[str]  # Policy name.
    uuid: NotRequired[str]  # Universally Unique Identifier (UUID; automatically assigned 
    srcintf: list[dict[str, Any]]  # Incoming (ingress) interface.
    dstintf: list[dict[str, Any]]  # Outgoing (egress) interface.
    action: NotRequired[Literal[{"description": "Allows session that match the firewall policy", "help": "Allows session that match the firewall policy.", "label": "Accept", "name": "accept"}, {"description": "Blocks sessions that match the firewall policy", "help": "Blocks sessions that match the firewall policy.", "label": "Deny", "name": "deny"}, {"description": "Firewall policy becomes a policy-based IPsec VPN policy", "help": "Firewall policy becomes a policy-based IPsec VPN policy.", "label": "Ipsec", "name": "ipsec"}]]  # Policy action (accept/deny/ipsec).
    nat64: NotRequired[Literal[{"description": "Enable NAT64", "help": "Enable NAT64.", "label": "Enable", "name": "enable"}, {"description": "Disable NAT64", "help": "Disable NAT64.", "label": "Disable", "name": "disable"}]]  # Enable/disable NAT64.
    nat46: NotRequired[Literal[{"description": "Enable NAT46", "help": "Enable NAT46.", "label": "Enable", "name": "enable"}, {"description": "Disable NAT46", "help": "Disable NAT46.", "label": "Disable", "name": "disable"}]]  # Enable/disable NAT46.
    ztna_status: NotRequired[Literal[{"description": "Enable zero trust network access", "help": "Enable zero trust network access.", "label": "Enable", "name": "enable"}, {"description": "Disable zero trust network access", "help": "Disable zero trust network access.", "label": "Disable", "name": "disable"}]]  # Enable/disable zero trust access.
    ztna_device_ownership: NotRequired[Literal[{"description": "Enable ZTNA device ownership check", "help": "Enable ZTNA device ownership check.", "label": "Enable", "name": "enable"}, {"description": "Disable ZTNA device ownership check", "help": "Disable ZTNA device ownership check.", "label": "Disable", "name": "disable"}]]  # Enable/disable zero trust device ownership.
    srcaddr: NotRequired[list[dict[str, Any]]]  # Source IPv4 address and address group names.
    dstaddr: NotRequired[list[dict[str, Any]]]  # Destination IPv4 address and address group names.
    srcaddr6: NotRequired[list[dict[str, Any]]]  # Source IPv6 address name and address group names.
    dstaddr6: NotRequired[list[dict[str, Any]]]  # Destination IPv6 address name and address group names.
    ztna_ems_tag: NotRequired[list[dict[str, Any]]]  # Source ztna-ems-tag names.
    ztna_ems_tag_secondary: NotRequired[list[dict[str, Any]]]  # Source ztna-ems-tag-secondary names.
    ztna_tags_match_logic: NotRequired[Literal[{"description": "Match ZTNA tags using a logical OR operator", "help": "Match ZTNA tags using a logical OR operator.", "label": "Or", "name": "or"}, {"description": "Match ZTNA tags using a logical AND operator", "help": "Match ZTNA tags using a logical AND operator.", "label": "And", "name": "and"}]]  # ZTNA tag matching logic.
    ztna_geo_tag: NotRequired[list[dict[str, Any]]]  # Source ztna-geo-tag names.
    internet_service: NotRequired[Literal[{"description": "Enable use of Internet Services in policy", "help": "Enable use of Internet Services in policy.", "label": "Enable", "name": "enable"}, {"description": "Disable use of Internet Services in policy", "help": "Disable use of Internet Services in policy.", "label": "Disable", "name": "disable"}]]  # Enable/disable use of Internet Services for this policy. If 
    internet_service_name: NotRequired[list[dict[str, Any]]]  # Internet Service name.
    internet_service_group: NotRequired[list[dict[str, Any]]]  # Internet Service group name.
    internet_service_custom: NotRequired[list[dict[str, Any]]]  # Custom Internet Service name.
    network_service_dynamic: NotRequired[list[dict[str, Any]]]  # Dynamic Network Service name.
    internet_service_custom_group: NotRequired[list[dict[str, Any]]]  # Custom Internet Service group name.
    internet_service_src: NotRequired[Literal[{"description": "Enable use of Internet Services source in policy", "help": "Enable use of Internet Services source in policy.", "label": "Enable", "name": "enable"}, {"description": "Disable use of Internet Services source in policy", "help": "Disable use of Internet Services source in policy.", "label": "Disable", "name": "disable"}]]  # Enable/disable use of Internet Services in source for this p
    internet_service_src_name: NotRequired[list[dict[str, Any]]]  # Internet Service source name.
    internet_service_src_group: NotRequired[list[dict[str, Any]]]  # Internet Service source group name.
    internet_service_src_custom: NotRequired[list[dict[str, Any]]]  # Custom Internet Service source name.
    network_service_src_dynamic: NotRequired[list[dict[str, Any]]]  # Dynamic Network Service source name.
    internet_service_src_custom_group: NotRequired[list[dict[str, Any]]]  # Custom Internet Service source group name.
    reputation_minimum: NotRequired[int]  # Minimum Reputation to take action.
    reputation_direction: NotRequired[Literal[{"description": "Check reputation for source address", "help": "Check reputation for source address.", "label": "Source", "name": "source"}, {"description": "Check reputation for destination address", "help": "Check reputation for destination address.", "label": "Destination", "name": "destination"}]]  # Direction of the initial traffic for reputation to take effe
    src_vendor_mac: NotRequired[list[dict[str, Any]]]  # Vendor MAC source ID.
    internet_service6: NotRequired[Literal[{"description": "Enable use of IPv6 Internet Services in policy", "help": "Enable use of IPv6 Internet Services in policy.", "label": "Enable", "name": "enable"}, {"description": "Disable use of IPv6 Internet Services in policy", "help": "Disable use of IPv6 Internet Services in policy.", "label": "Disable", "name": "disable"}]]  # Enable/disable use of IPv6 Internet Services for this policy
    internet_service6_name: NotRequired[list[dict[str, Any]]]  # IPv6 Internet Service name.
    internet_service6_group: NotRequired[list[dict[str, Any]]]  # Internet Service group name.
    internet_service6_custom: NotRequired[list[dict[str, Any]]]  # Custom IPv6 Internet Service name.
    internet_service6_custom_group: NotRequired[list[dict[str, Any]]]  # Custom Internet Service6 group name.
    internet_service6_src: NotRequired[Literal[{"description": "Enable use of IPv6 Internet Services source in policy", "help": "Enable use of IPv6 Internet Services source in policy.", "label": "Enable", "name": "enable"}, {"description": "Disable use of IPv6 Internet Services source in policy", "help": "Disable use of IPv6 Internet Services source in policy.", "label": "Disable", "name": "disable"}]]  # Enable/disable use of IPv6 Internet Services in source for t
    internet_service6_src_name: NotRequired[list[dict[str, Any]]]  # IPv6 Internet Service source name.
    internet_service6_src_group: NotRequired[list[dict[str, Any]]]  # Internet Service6 source group name.
    internet_service6_src_custom: NotRequired[list[dict[str, Any]]]  # Custom IPv6 Internet Service source name.
    internet_service6_src_custom_group: NotRequired[list[dict[str, Any]]]  # Custom Internet Service6 source group name.
    reputation_minimum6: NotRequired[int]  # IPv6 Minimum Reputation to take action.
    reputation_direction6: NotRequired[Literal[{"description": "Check reputation for IPv6 source address", "help": "Check reputation for IPv6 source address.", "label": "Source", "name": "source"}, {"description": "Check reputation for IPv6 destination address", "help": "Check reputation for IPv6 destination address.", "label": "Destination", "name": "destination"}]]  # Direction of the initial traffic for IPv6 reputation to take
    rtp_nat: NotRequired[Literal[{"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}, {"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}]]  # Enable Real Time Protocol (RTP) NAT.
    rtp_addr: list[dict[str, Any]]  # Address names if this is an RTP NAT policy.
    send_deny_packet: NotRequired[Literal[{"description": "Disable deny-packet sending", "help": "Disable deny-packet sending.", "label": "Disable", "name": "disable"}, {"description": "Enable deny-packet sending", "help": "Enable deny-packet sending.", "label": "Enable", "name": "enable"}]]  # Enable to send a reply when a session is denied or blocked b
    firewall_session_dirty: NotRequired[Literal[{"description": "Flush all current sessions accepted by this policy", "help": "Flush all current sessions accepted by this policy. These sessions must be started and re-matched with policies.", "label": "Check All", "name": "check-all"}, {"description": "Continue to allow sessions already accepted by this policy", "help": "Continue to allow sessions already accepted by this policy.", "label": "Check New", "name": "check-new"}]]  # How to handle sessions if the configuration of this firewall
    schedule: str  # Schedule name.
    schedule_timeout: NotRequired[Literal[{"description": "Enable schedule timeout", "help": "Enable schedule timeout.", "label": "Enable", "name": "enable"}, {"description": "Disable schedule timeout", "help": "Disable schedule timeout.", "label": "Disable", "name": "disable"}]]  # Enable to force current sessions to end when the schedule ob
    policy_expiry: NotRequired[Literal[{"description": "Enable policy expiry", "help": "Enable policy expiry.", "label": "Enable", "name": "enable"}, {"description": "Disable polcy expiry", "help": "Disable polcy expiry.", "label": "Disable", "name": "disable"}]]  # Enable/disable policy expiry.
    policy_expiry_date: NotRequired[str]  # Policy expiry date (YYYY-MM-DD HH:MM:SS).
    policy_expiry_date_utc: NotRequired[str]  # Policy expiry date and time, in epoch format.
    service: NotRequired[list[dict[str, Any]]]  # Service and service group names.
    tos_mask: NotRequired[str]  # Non-zero bit positions are used for comparison while zero bi
    tos: NotRequired[str]  # ToS (Type of Service) value used for comparison.
    tos_negate: NotRequired[Literal[{"description": "Enable TOS match negate", "help": "Enable TOS match negate.", "label": "Enable", "name": "enable"}, {"description": "Disable TOS match negate", "help": "Disable TOS match negate.", "label": "Disable", "name": "disable"}]]  # Enable negated TOS match.
    anti_replay: NotRequired[Literal[{"description": "Enable anti-replay check", "help": "Enable anti-replay check.", "label": "Enable", "name": "enable"}, {"description": "Disable anti-replay check", "help": "Disable anti-replay check.", "label": "Disable", "name": "disable"}]]  # Enable/disable anti-replay check.
    tcp_session_without_syn: NotRequired[Literal[{"description": "Enable TCP session without SYN", "help": "Enable TCP session without SYN.", "label": "All", "name": "all"}, {"description": "Enable TCP session data only", "help": "Enable TCP session data only.", "label": "Data Only", "name": "data-only"}, {"description": "Disable TCP session without SYN", "help": "Disable TCP session without SYN.", "label": "Disable", "name": "disable"}]]  # Enable/disable creation of TCP session without SYN flag.
    geoip_anycast: NotRequired[Literal[{"description": "Enable recognition of anycast IP addresses using the geography IP database", "help": "Enable recognition of anycast IP addresses using the geography IP database.", "label": "Enable", "name": "enable"}, {"description": "Disable recognition of anycast IP addresses using the geography IP database", "help": "Disable recognition of anycast IP addresses using the geography IP database.", "label": "Disable", "name": "disable"}]]  # Enable/disable recognition of anycast IP addresses using the
    geoip_match: NotRequired[Literal[{"description": "Match geography address to its physical location using the geography IP database", "help": "Match geography address to its physical location using the geography IP database.", "label": "Physical Location", "name": "physical-location"}, {"description": "Match geography address to its registered location using the geography IP database", "help": "Match geography address to its registered location using the geography IP database.", "label": "Registered Location", "name": "registered-location"}]]  # Match geography address based either on its physical locatio
    dynamic_shaping: NotRequired[Literal[{"description": "Enable dynamic RADIUS defined traffic shaping", "help": "Enable dynamic RADIUS defined traffic shaping.", "label": "Enable", "name": "enable"}, {"description": "Disable dynamic RADIUS defined traffic shaping", "help": "Disable dynamic RADIUS defined traffic shaping.", "label": "Disable", "name": "disable"}]]  # Enable/disable dynamic RADIUS defined traffic shaping.
    passive_wan_health_measurement: NotRequired[Literal[{"description": "Enable Passive WAN health measurement", "help": "Enable Passive WAN health measurement.", "label": "Enable", "name": "enable"}, {"description": "Disable Passive WAN health measurement", "help": "Disable Passive WAN health measurement.", "label": "Disable", "name": "disable"}]]  # Enable/disable passive WAN health measurement. When enabled,
    app_monitor: NotRequired[Literal[{"description": "Enable TCP metrics in session logs", "help": "Enable TCP metrics in session logs.", "label": "Enable", "name": "enable"}, {"description": "Disable TCP metrics in session logs", "help": "Disable TCP metrics in session logs.", "label": "Disable", "name": "disable"}]]  # Enable/disable application TCP metrics in session logs.When 
    utm_status: NotRequired[Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]]  # Enable to add one or more security profiles (AV, IPS, etc.) 
    inspection_mode: NotRequired[Literal[{"description": "Proxy based inspection", "help": "Proxy based inspection.", "label": "Proxy", "name": "proxy"}, {"description": "Flow based inspection", "help": "Flow based inspection.", "label": "Flow", "name": "flow"}]]  # Policy inspection mode (Flow/proxy). Default is Flow mode.
    http_policy_redirect: NotRequired[Literal[{"description": "Enable HTTP(S) policy redirect", "help": "Enable HTTP(S) policy redirect.", "label": "Enable", "name": "enable"}, {"description": "Disable HTTP(S) policy redirect", "help": "Disable HTTP(S) policy redirect.", "label": "Disable", "name": "disable"}, {"description": "Enable HTTP(S) policy redirect (for preserving old behavior, not recommended for new setups)", "help": "Enable HTTP(S) policy redirect (for preserving old behavior, not recommended for new setups).", "label": "Legacy", "name": "legacy"}]]  # Redirect HTTP(S) traffic to matching transparent web proxy p
    ssh_policy_redirect: NotRequired[Literal[{"description": "Enable SSH policy redirect", "help": "Enable SSH policy redirect.", "label": "Enable", "name": "enable"}, {"description": "Disable SSH policy redirect", "help": "Disable SSH policy redirect.", "label": "Disable", "name": "disable"}]]  # Redirect SSH traffic to matching transparent proxy policy.
    ztna_policy_redirect: NotRequired[Literal[{"description": "Enable ZTNA proxy-policy redirect", "help": "Enable ZTNA proxy-policy redirect.", "label": "Enable", "name": "enable"}, {"description": "Disable ZTNA proxy-policy redirect", "help": "Disable ZTNA proxy-policy redirect.", "label": "Disable", "name": "disable"}]]  # Redirect ZTNA traffic to matching Access-Proxy proxy-policy.
    webproxy_profile: NotRequired[str]  # Webproxy profile name.
    profile_type: NotRequired[Literal[{"description": "Do not allow security profile groups", "help": "Do not allow security profile groups.", "label": "Single", "name": "single"}, {"description": "Allow security profile groups", "help": "Allow security profile groups.", "label": "Group", "name": "group"}]]  # Determine whether the firewall policy allows security profil
    profile_group: NotRequired[str]  # Name of profile group.
    profile_protocol_options: NotRequired[str]  # Name of an existing Protocol options profile.
    ssl_ssh_profile: NotRequired[str]  # Name of an existing SSL SSH profile.
    av_profile: NotRequired[str]  # Name of an existing Antivirus profile.
    webfilter_profile: NotRequired[str]  # Name of an existing Web filter profile.
    dnsfilter_profile: NotRequired[str]  # Name of an existing DNS filter profile.
    emailfilter_profile: NotRequired[str]  # Name of an existing email filter profile.
    dlp_profile: NotRequired[str]  # Name of an existing DLP profile.
    file_filter_profile: NotRequired[str]  # Name of an existing file-filter profile.
    ips_sensor: NotRequired[str]  # Name of an existing IPS sensor.
    application_list: NotRequired[str]  # Name of an existing Application list.
    voip_profile: NotRequired[str]  # Name of an existing VoIP (voipd) profile.
    ips_voip_filter: NotRequired[str]  # Name of an existing VoIP (ips) profile.
    sctp_filter_profile: NotRequired[str]  # Name of an existing SCTP filter profile.
    diameter_filter_profile: NotRequired[str]  # Name of an existing Diameter filter profile.
    virtual_patch_profile: NotRequired[str]  # Name of an existing virtual-patch profile.
    icap_profile: NotRequired[str]  # Name of an existing ICAP profile.
    videofilter_profile: NotRequired[str]  # Name of an existing VideoFilter profile.
    waf_profile: NotRequired[str]  # Name of an existing Web application firewall profile.
    ssh_filter_profile: NotRequired[str]  # Name of an existing SSH filter profile.
    casb_profile: NotRequired[str]  # Name of an existing CASB profile.
    logtraffic: NotRequired[Literal[{"description": "Log all sessions accepted or denied by this policy", "help": "Log all sessions accepted or denied by this policy.", "label": "All", "name": "all"}, {"description": "Log traffic that has a security profile applied to it", "help": "Log traffic that has a security profile applied to it.", "label": "Utm", "name": "utm"}, {"description": "Disable all logging for this policy", "help": "Disable all logging for this policy.", "label": "Disable", "name": "disable"}]]  # Enable or disable logging. Log all sessions or security prof
    logtraffic_start: NotRequired[Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]]  # Record logs when a session starts.
    log_http_transaction: NotRequired[Literal[{"description": "Enable HTTP transaction log", "help": "Enable HTTP transaction log.", "label": "Enable", "name": "enable"}, {"description": "Disable HTTP transaction log", "help": "Disable HTTP transaction log.", "label": "Disable", "name": "disable"}]]  # Enable/disable HTTP transaction log.
    capture_packet: NotRequired[Literal[{"description": "Enable capture packets", "help": "Enable capture packets.", "label": "Enable", "name": "enable"}, {"description": "Disable capture packets", "help": "Disable capture packets.", "label": "Disable", "name": "disable"}]]  # Enable/disable capture packets.
    auto_asic_offload: NotRequired[Literal[{"description": "Enable auto ASIC offloading", "help": "Enable auto ASIC offloading.", "label": "Enable", "name": "enable"}, {"description": "Disable ASIC offloading", "help": "Disable ASIC offloading.", "label": "Disable", "name": "disable"}]]  # Enable/disable policy traffic ASIC offloading.
    wanopt: NotRequired[Literal[{"help": "Enable setting.", "label": "Enable", "name": "enable"}, {"help": "Disable setting.", "label": "Disable", "name": "disable"}]]  # Enable/disable WAN optimization.
    wanopt_detection: NotRequired[Literal[{"help": "Active WAN optimization peer auto-detection.", "label": "Active", "name": "active"}, {"help": "Passive WAN optimization peer auto-detection.", "label": "Passive", "name": "passive"}, {"help": "Turn off WAN optimization peer auto-detection.", "label": "Off", "name": "off"}]]  # WAN optimization auto-detection mode.
    wanopt_passive_opt: NotRequired[Literal[{"help": "Allow client side WAN opt peer to decide.", "label": "Default", "name": "default"}, {"help": "Use address of client to connect to server.", "label": "Transparent", "name": "transparent"}, {"help": "Use local FortiGate address to connect to server.", "label": "Non Transparent", "name": "non-transparent"}]]  # WAN optimization passive mode options. This option decides w
    wanopt_profile: str  # WAN optimization profile.
    wanopt_peer: str  # WAN optimization peer.
    webcache: NotRequired[Literal[{"help": "Enable setting.", "label": "Enable", "name": "enable"}, {"help": "Disable setting.", "label": "Disable", "name": "disable"}]]  # Enable/disable web cache.
    webcache_https: NotRequired[Literal[{"help": "Disable web cache for HTTPS.", "label": "Disable", "name": "disable"}, {"help": "Enable web cache for HTTPS.", "label": "Enable", "name": "enable"}]]  # Enable/disable web cache for HTTPS.
    webproxy_forward_server: NotRequired[str]  # Webproxy forward server name.
    traffic_shaper: NotRequired[str]  # Traffic shaper.
    traffic_shaper_reverse: NotRequired[str]  # Reverse traffic shaper.
    per_ip_shaper: NotRequired[str]  # Per-IP traffic shaper.
    nat: NotRequired[Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]]  # Enable/disable source NAT.
    pcp_outbound: NotRequired[Literal[{"description": "Enable PCP outbound SNAT", "help": "Enable PCP outbound SNAT.", "label": "Enable", "name": "enable"}, {"description": "Disable PCP outbound SNAT", "help": "Disable PCP outbound SNAT.", "label": "Disable", "name": "disable"}]]  # Enable/disable PCP outbound SNAT.
    pcp_inbound: NotRequired[Literal[{"description": "Enable PCP inbound DNAT", "help": "Enable PCP inbound DNAT.", "label": "Enable", "name": "enable"}, {"description": "Disable PCP inbound DNAT", "help": "Disable PCP inbound DNAT.", "label": "Disable", "name": "disable"}]]  # Enable/disable PCP inbound DNAT.
    pcp_poolname: NotRequired[list[dict[str, Any]]]  # PCP pool names.
    permit_any_host: NotRequired[Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]]  # Enable/disable fullcone NAT. Accept UDP packets from any hos
    permit_stun_host: NotRequired[Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]]  # Accept UDP packets from any Session Traversal Utilities for 
    fixedport: NotRequired[Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]]  # Enable to prevent source NAT from changing a session's sourc
    port_preserve: NotRequired[Literal[{"description": "Use the original source port if it has not been used", "help": "Use the original source port if it has not been used.", "label": "Enable", "name": "enable"}, {"description": "Source NAT always changes the source port", "help": "Source NAT always changes the source port.", "label": "Disable", "name": "disable"}]]  # Enable/disable preservation of the original source port from
    port_random: NotRequired[Literal[{"description": "Enable random source port selection for source NAT", "help": "Enable random source port selection for source NAT.", "label": "Enable", "name": "enable"}, {"description": "Disable random source port selection for source NAT", "help": "Disable random source port selection for source NAT.", "label": "Disable", "name": "disable"}]]  # Enable/disable random source port selection for source NAT.
    ippool: NotRequired[Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]]  # Enable to use IP Pools for source NAT.
    poolname: NotRequired[list[dict[str, Any]]]  # IP Pool names.
    poolname6: NotRequired[list[dict[str, Any]]]  # IPv6 pool names.
    session_ttl: NotRequired[str]  # TTL in seconds for sessions accepted by this policy (0 means
    vlan_cos_fwd: NotRequired[int]  # VLAN forward direction user priority: 255 passthrough, 0 low
    vlan_cos_rev: NotRequired[int]  # VLAN reverse direction user priority: 255 passthrough, 0 low
    inbound: NotRequired[Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]]  # Policy-based IPsec VPN: only traffic from the remote network
    outbound: NotRequired[Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]]  # Policy-based IPsec VPN: only traffic from the internal netwo
    natinbound: NotRequired[Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]]  # Policy-based IPsec VPN: apply destination NAT to inbound tra
    natoutbound: NotRequired[Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]]  # Policy-based IPsec VPN: apply source NAT to outbound traffic
    fec: NotRequired[Literal[{"description": "Enable Forward Error Correction", "help": "Enable Forward Error Correction.", "label": "Enable", "name": "enable"}, {"description": "Disable Forward Error Correction", "help": "Disable Forward Error Correction.", "label": "Disable", "name": "disable"}]]  # Enable/disable Forward Error Correction on traffic matching 
    wccp: NotRequired[Literal[{"description": "Enable WCCP setting", "help": "Enable WCCP setting.", "label": "Enable", "name": "enable"}, {"description": "Disable WCCP setting", "help": "Disable WCCP setting.", "label": "Disable", "name": "disable"}]]  # Enable/disable forwarding traffic matching this policy to a 
    ntlm: NotRequired[Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]]  # Enable/disable NTLM authentication.
    ntlm_guest: NotRequired[Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]]  # Enable/disable NTLM guest user access.
    ntlm_enabled_browsers: NotRequired[list[dict[str, Any]]]  # HTTP-User-Agent value of supported browsers.
    fsso_agent_for_ntlm: NotRequired[str]  # FSSO agent to use for NTLM authentication.
    groups: NotRequired[list[dict[str, Any]]]  # Names of user groups that can authenticate with this policy.
    users: NotRequired[list[dict[str, Any]]]  # Names of individual users that can authenticate with this po
    fsso_groups: NotRequired[list[dict[str, Any]]]  # Names of FSSO groups.
    auth_path: NotRequired[Literal[{"description": "Enable authentication-based routing", "help": "Enable authentication-based routing.", "label": "Enable", "name": "enable"}, {"description": "Disable authentication-based routing", "help": "Disable authentication-based routing.", "label": "Disable", "name": "disable"}]]  # Enable/disable authentication-based routing.
    disclaimer: NotRequired[Literal[{"description": "Enable user authentication disclaimer", "help": "Enable user authentication disclaimer.", "label": "Enable", "name": "enable"}, {"description": "Disable user authentication disclaimer", "help": "Disable user authentication disclaimer.", "label": "Disable", "name": "disable"}]]  # Enable/disable user authentication disclaimer.
    email_collect: NotRequired[Literal[{"description": "Enable email collection", "help": "Enable email collection.", "label": "Enable", "name": "enable"}, {"description": "Disable email collection", "help": "Disable email collection.", "label": "Disable", "name": "disable"}]]  # Enable/disable email collection.
    vpntunnel: str  # Policy-based IPsec VPN: name of the IPsec VPN Phase 1.
    natip: NotRequired[str]  # Policy-based IPsec VPN: source NAT IP address for outgoing t
    match_vip: NotRequired[Literal[{"description": "Match DNATed packet", "help": "Match DNATed packet.", "label": "Enable", "name": "enable"}, {"description": "Do not match DNATed packet", "help": "Do not match DNATed packet.", "label": "Disable", "name": "disable"}]]  # Enable to match packets that have had their destination addr
    match_vip_only: NotRequired[Literal[{"description": "Enable matching of only those packets that have had their destination addresses changed by a VIP", "help": "Enable matching of only those packets that have had their destination addresses changed by a VIP.", "label": "Enable", "name": "enable"}, {"description": "Disable matching of only those packets that have had their destination addresses changed by a VIP", "help": "Disable matching of only those packets that have had their destination addresses changed by a VIP.", "label": "Disable", "name": "disable"}]]  # Enable/disable matching of only those packets that have had 
    diffserv_copy: NotRequired[Literal[{"description": "Enable DSCP copy", "help": "Enable DSCP copy.", "label": "Enable", "name": "enable"}, {"description": "Disable DSCP copy", "help": "Disable DSCP copy.", "label": "Disable", "name": "disable"}]]  # Enable to copy packet's DiffServ values from session's origi
    diffserv_forward: NotRequired[Literal[{"description": "Enable setting forward (original) traffic Diffserv", "help": "Enable setting forward (original) traffic Diffserv.", "label": "Enable", "name": "enable"}, {"description": "Disable setting forward (original) traffic Diffserv", "help": "Disable setting forward (original) traffic Diffserv.", "label": "Disable", "name": "disable"}]]  # Enable to change packet's DiffServ values to the specified d
    diffserv_reverse: NotRequired[Literal[{"description": "Enable setting reverse (reply) traffic DiffServ", "help": "Enable setting reverse (reply) traffic DiffServ.", "label": "Enable", "name": "enable"}, {"description": "Disable setting reverse (reply) traffic DiffServ", "help": "Disable setting reverse (reply) traffic DiffServ.", "label": "Disable", "name": "disable"}]]  # Enable to change packet's reverse (reply) DiffServ values to
    diffservcode_forward: NotRequired[str]  # Change packet's DiffServ to this value.
    diffservcode_rev: NotRequired[str]  # Change packet's reverse (reply) DiffServ to this value.
    tcp_mss_sender: NotRequired[int]  # Sender TCP maximum segment size (MSS).
    tcp_mss_receiver: NotRequired[int]  # Receiver TCP maximum segment size (MSS).
    comments: NotRequired[str]  # Comment.
    auth_cert: NotRequired[str]  # HTTPS server certificate for policy authentication.
    auth_redirect_addr: NotRequired[str]  # HTTP-to-HTTPS redirect address for firewall authentication.
    redirect_url: NotRequired[str]  # URL users are directed to after seeing and accepting the dis
    identity_based_route: NotRequired[str]  # Name of identity-based routing rule.
    block_notification: NotRequired[Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]]  # Enable/disable block notification.
    custom_log_fields: NotRequired[list[dict[str, Any]]]  # Custom fields to append to log messages for this policy.
    replacemsg_override_group: NotRequired[str]  # Override the default replacement message group for this poli
    srcaddr_negate: NotRequired[Literal[{"description": "Enable source address negate", "help": "Enable source address negate.", "label": "Enable", "name": "enable"}, {"description": "Disable source address negate", "help": "Disable source address negate.", "label": "Disable", "name": "disable"}]]  # When enabled srcaddr specifies what the source address must 
    srcaddr6_negate: NotRequired[Literal[{"description": "Enable IPv6 source address negate", "help": "Enable IPv6 source address negate.", "label": "Enable", "name": "enable"}, {"description": "Disable IPv6 source address negate", "help": "Disable IPv6 source address negate.", "label": "Disable", "name": "disable"}]]  # When enabled srcaddr6 specifies what the source address must
    dstaddr_negate: NotRequired[Literal[{"description": "Enable destination address negate", "help": "Enable destination address negate.", "label": "Enable", "name": "enable"}, {"description": "Disable destination address negate", "help": "Disable destination address negate.", "label": "Disable", "name": "disable"}]]  # When enabled dstaddr specifies what the destination address 
    dstaddr6_negate: NotRequired[Literal[{"description": "Enable IPv6 destination address negate", "help": "Enable IPv6 destination address negate.", "label": "Enable", "name": "enable"}, {"description": "Disable IPv6 destination address negate", "help": "Disable IPv6 destination address negate.", "label": "Disable", "name": "disable"}]]  # When enabled dstaddr6 specifies what the destination address
    ztna_ems_tag_negate: NotRequired[Literal[{"description": "Enable ZTNA EMS tags negate", "help": "Enable ZTNA EMS tags negate.", "label": "Enable", "name": "enable"}, {"description": "Disable ZTNA EMS tags negate", "help": "Disable ZTNA EMS tags negate.", "label": "Disable", "name": "disable"}]]  # When enabled ztna-ems-tag specifies what the tags must NOT b
    service_negate: NotRequired[Literal[{"description": "Enable negated service match", "help": "Enable negated service match.", "label": "Enable", "name": "enable"}, {"description": "Disable negated service match", "help": "Disable negated service match.", "label": "Disable", "name": "disable"}]]  # When enabled service specifies what the service must NOT be.
    internet_service_negate: NotRequired[Literal[{"description": "Enable negated Internet Service match", "help": "Enable negated Internet Service match.", "label": "Enable", "name": "enable"}, {"description": "Disable negated Internet Service match", "help": "Disable negated Internet Service match.", "label": "Disable", "name": "disable"}]]  # When enabled internet-service specifies what the service mus
    internet_service_src_negate: NotRequired[Literal[{"description": "Enable negated Internet Service source match", "help": "Enable negated Internet Service source match.", "label": "Enable", "name": "enable"}, {"description": "Disable negated Internet Service source match", "help": "Disable negated Internet Service source match.", "label": "Disable", "name": "disable"}]]  # When enabled internet-service-src specifies what the service
    internet_service6_negate: NotRequired[Literal[{"description": "Enable negated IPv6 Internet Service match", "help": "Enable negated IPv6 Internet Service match.", "label": "Enable", "name": "enable"}, {"description": "Disable negated IPv6 Internet Service match", "help": "Disable negated IPv6 Internet Service match.", "label": "Disable", "name": "disable"}]]  # When enabled internet-service6 specifies what the service mu
    internet_service6_src_negate: NotRequired[Literal[{"description": "Enable negated IPv6 Internet Service source match", "help": "Enable negated IPv6 Internet Service source match.", "label": "Enable", "name": "enable"}, {"description": "Disable negated IPv6 Internet Service source match", "help": "Disable negated IPv6 Internet Service source match.", "label": "Disable", "name": "disable"}]]  # When enabled internet-service6-src specifies what the servic
    timeout_send_rst: NotRequired[Literal[{"description": "Enable sending of RST packet upon TCP session expiration", "help": "Enable sending of RST packet upon TCP session expiration.", "label": "Enable", "name": "enable"}, {"description": "Disable sending of RST packet upon TCP session expiration", "help": "Disable sending of RST packet upon TCP session expiration.", "label": "Disable", "name": "disable"}]]  # Enable/disable sending RST packets when TCP sessions expire.
    captive_portal_exempt: NotRequired[Literal[{"description": "Enable exemption of captive portal", "help": "Enable exemption of captive portal.", "label": "Enable", "name": "enable"}, {"description": "Disable exemption of captive portal", "help": "Disable exemption of captive portal.", "label": "Disable", "name": "disable"}]]  # Enable to exempt some users from the captive portal.
    decrypted_traffic_mirror: NotRequired[str]  # Decrypted traffic mirror.
    dsri: NotRequired[Literal[{"description": "Enable DSRI", "help": "Enable DSRI.", "label": "Enable", "name": "enable"}, {"description": "Disable DSRI", "help": "Disable DSRI.", "label": "Disable", "name": "disable"}]]  # Enable DSRI to ignore HTTP server responses.
    radius_mac_auth_bypass: NotRequired[Literal[{"description": "Enable MAC authentication bypass", "help": "Enable MAC authentication bypass.", "label": "Enable", "name": "enable"}, {"description": "Disable MAC authentication bypass", "help": "Disable MAC authentication bypass.", "label": "Disable", "name": "disable"}]]  # Enable MAC authentication bypass. The bypassed MAC address m
    radius_ip_auth_bypass: NotRequired[Literal[{"description": "Enable IP authentication bypass", "help": "Enable IP authentication bypass.", "label": "Enable", "name": "enable"}, {"description": "Disable IP authentication bypass", "help": "Disable IP authentication bypass.", "label": "Disable", "name": "disable"}]]  # Enable IP authentication bypass. The bypassed IP address mus
    delay_tcp_npu_session: NotRequired[Literal[{"description": "Enable TCP NPU session delay in order to guarantee packet order of 3-way handshake", "help": "Enable TCP NPU session delay in order to guarantee packet order of 3-way handshake.", "label": "Enable", "name": "enable"}, {"description": "Disable TCP NPU session delay in order to guarantee packet order of 3-way handshake", "help": "Disable TCP NPU session delay in order to guarantee packet order of 3-way handshake.", "label": "Disable", "name": "disable"}]]  # Enable TCP NPU session delay to guarantee packet order of 3-
    vlan_filter: NotRequired[str]  # VLAN ranges to allow
    sgt_check: NotRequired[Literal[{"description": "Enable SGT check", "help": "Enable SGT check.", "label": "Enable", "name": "enable"}, {"description": "Disable SGT check", "help": "Disable SGT check.", "label": "Disable", "name": "disable"}]]  # Enable/disable security group tags (SGT) check.
    sgt: NotRequired[list[dict[str, Any]]]  # Security group tags.
    internet_service_fortiguard: NotRequired[list[dict[str, Any]]]  # FortiGuard Internet Service name.
    internet_service_src_fortiguard: NotRequired[list[dict[str, Any]]]  # FortiGuard Internet Service source name.
    internet_service6_fortiguard: NotRequired[list[dict[str, Any]]]  # FortiGuard IPv6 Internet Service name.
    internet_service6_src_fortiguard: NotRequired[list[dict[str, Any]]]  # FortiGuard IPv6 Internet Service source name.


class Policy:
    """
    Configure IPv4/IPv6 policies.
    
    Path: firewall/policy
    Category: cmdb
    Primary Key: policyid
    """
    
    # Overloads for get() with response_mode="object"
    @overload
    def get(
        self,
        policyid: int | None = ...,
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
        policyid: int,
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
        policyid: int | None = ...,
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
        policyid: int | None = ...,
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
        policyid: int | None = ...,
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
        payload_dict: PolicyPayload | None = ...,
        policyid: int | None = ...,
        status: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        name: str | None = ...,
        uuid: str | None = ...,
        srcintf: list[dict[str, Any]] | None = ...,
        dstintf: list[dict[str, Any]] | None = ...,
        action: Literal[{"description": "Allows session that match the firewall policy", "help": "Allows session that match the firewall policy.", "label": "Accept", "name": "accept"}, {"description": "Blocks sessions that match the firewall policy", "help": "Blocks sessions that match the firewall policy.", "label": "Deny", "name": "deny"}, {"description": "Firewall policy becomes a policy-based IPsec VPN policy", "help": "Firewall policy becomes a policy-based IPsec VPN policy.", "label": "Ipsec", "name": "ipsec"}] | None = ...,
        nat64: Literal[{"description": "Enable NAT64", "help": "Enable NAT64.", "label": "Enable", "name": "enable"}, {"description": "Disable NAT64", "help": "Disable NAT64.", "label": "Disable", "name": "disable"}] | None = ...,
        nat46: Literal[{"description": "Enable NAT46", "help": "Enable NAT46.", "label": "Enable", "name": "enable"}, {"description": "Disable NAT46", "help": "Disable NAT46.", "label": "Disable", "name": "disable"}] | None = ...,
        ztna_status: Literal[{"description": "Enable zero trust network access", "help": "Enable zero trust network access.", "label": "Enable", "name": "enable"}, {"description": "Disable zero trust network access", "help": "Disable zero trust network access.", "label": "Disable", "name": "disable"}] | None = ...,
        ztna_device_ownership: Literal[{"description": "Enable ZTNA device ownership check", "help": "Enable ZTNA device ownership check.", "label": "Enable", "name": "enable"}, {"description": "Disable ZTNA device ownership check", "help": "Disable ZTNA device ownership check.", "label": "Disable", "name": "disable"}] | None = ...,
        srcaddr: list[dict[str, Any]] | None = ...,
        dstaddr: list[dict[str, Any]] | None = ...,
        srcaddr6: list[dict[str, Any]] | None = ...,
        dstaddr6: list[dict[str, Any]] | None = ...,
        ztna_ems_tag: list[dict[str, Any]] | None = ...,
        ztna_ems_tag_secondary: list[dict[str, Any]] | None = ...,
        ztna_tags_match_logic: Literal[{"description": "Match ZTNA tags using a logical OR operator", "help": "Match ZTNA tags using a logical OR operator.", "label": "Or", "name": "or"}, {"description": "Match ZTNA tags using a logical AND operator", "help": "Match ZTNA tags using a logical AND operator.", "label": "And", "name": "and"}] | None = ...,
        ztna_geo_tag: list[dict[str, Any]] | None = ...,
        internet_service: Literal[{"description": "Enable use of Internet Services in policy", "help": "Enable use of Internet Services in policy.", "label": "Enable", "name": "enable"}, {"description": "Disable use of Internet Services in policy", "help": "Disable use of Internet Services in policy.", "label": "Disable", "name": "disable"}] | None = ...,
        internet_service_name: list[dict[str, Any]] | None = ...,
        internet_service_group: list[dict[str, Any]] | None = ...,
        internet_service_custom: list[dict[str, Any]] | None = ...,
        network_service_dynamic: list[dict[str, Any]] | None = ...,
        internet_service_custom_group: list[dict[str, Any]] | None = ...,
        internet_service_src: Literal[{"description": "Enable use of Internet Services source in policy", "help": "Enable use of Internet Services source in policy.", "label": "Enable", "name": "enable"}, {"description": "Disable use of Internet Services source in policy", "help": "Disable use of Internet Services source in policy.", "label": "Disable", "name": "disable"}] | None = ...,
        internet_service_src_name: list[dict[str, Any]] | None = ...,
        internet_service_src_group: list[dict[str, Any]] | None = ...,
        internet_service_src_custom: list[dict[str, Any]] | None = ...,
        network_service_src_dynamic: list[dict[str, Any]] | None = ...,
        internet_service_src_custom_group: list[dict[str, Any]] | None = ...,
        reputation_minimum: int | None = ...,
        reputation_direction: Literal[{"description": "Check reputation for source address", "help": "Check reputation for source address.", "label": "Source", "name": "source"}, {"description": "Check reputation for destination address", "help": "Check reputation for destination address.", "label": "Destination", "name": "destination"}] | None = ...,
        src_vendor_mac: list[dict[str, Any]] | None = ...,
        internet_service6: Literal[{"description": "Enable use of IPv6 Internet Services in policy", "help": "Enable use of IPv6 Internet Services in policy.", "label": "Enable", "name": "enable"}, {"description": "Disable use of IPv6 Internet Services in policy", "help": "Disable use of IPv6 Internet Services in policy.", "label": "Disable", "name": "disable"}] | None = ...,
        internet_service6_name: list[dict[str, Any]] | None = ...,
        internet_service6_group: list[dict[str, Any]] | None = ...,
        internet_service6_custom: list[dict[str, Any]] | None = ...,
        internet_service6_custom_group: list[dict[str, Any]] | None = ...,
        internet_service6_src: Literal[{"description": "Enable use of IPv6 Internet Services source in policy", "help": "Enable use of IPv6 Internet Services source in policy.", "label": "Enable", "name": "enable"}, {"description": "Disable use of IPv6 Internet Services source in policy", "help": "Disable use of IPv6 Internet Services source in policy.", "label": "Disable", "name": "disable"}] | None = ...,
        internet_service6_src_name: list[dict[str, Any]] | None = ...,
        internet_service6_src_group: list[dict[str, Any]] | None = ...,
        internet_service6_src_custom: list[dict[str, Any]] | None = ...,
        internet_service6_src_custom_group: list[dict[str, Any]] | None = ...,
        reputation_minimum6: int | None = ...,
        reputation_direction6: Literal[{"description": "Check reputation for IPv6 source address", "help": "Check reputation for IPv6 source address.", "label": "Source", "name": "source"}, {"description": "Check reputation for IPv6 destination address", "help": "Check reputation for IPv6 destination address.", "label": "Destination", "name": "destination"}] | None = ...,
        rtp_nat: Literal[{"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}, {"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}] | None = ...,
        rtp_addr: list[dict[str, Any]] | None = ...,
        send_deny_packet: Literal[{"description": "Disable deny-packet sending", "help": "Disable deny-packet sending.", "label": "Disable", "name": "disable"}, {"description": "Enable deny-packet sending", "help": "Enable deny-packet sending.", "label": "Enable", "name": "enable"}] | None = ...,
        firewall_session_dirty: Literal[{"description": "Flush all current sessions accepted by this policy", "help": "Flush all current sessions accepted by this policy. These sessions must be started and re-matched with policies.", "label": "Check All", "name": "check-all"}, {"description": "Continue to allow sessions already accepted by this policy", "help": "Continue to allow sessions already accepted by this policy.", "label": "Check New", "name": "check-new"}] | None = ...,
        schedule: str | None = ...,
        schedule_timeout: Literal[{"description": "Enable schedule timeout", "help": "Enable schedule timeout.", "label": "Enable", "name": "enable"}, {"description": "Disable schedule timeout", "help": "Disable schedule timeout.", "label": "Disable", "name": "disable"}] | None = ...,
        policy_expiry: Literal[{"description": "Enable policy expiry", "help": "Enable policy expiry.", "label": "Enable", "name": "enable"}, {"description": "Disable polcy expiry", "help": "Disable polcy expiry.", "label": "Disable", "name": "disable"}] | None = ...,
        policy_expiry_date: str | None = ...,
        policy_expiry_date_utc: str | None = ...,
        service: list[dict[str, Any]] | None = ...,
        tos_mask: str | None = ...,
        tos: str | None = ...,
        tos_negate: Literal[{"description": "Enable TOS match negate", "help": "Enable TOS match negate.", "label": "Enable", "name": "enable"}, {"description": "Disable TOS match negate", "help": "Disable TOS match negate.", "label": "Disable", "name": "disable"}] | None = ...,
        anti_replay: Literal[{"description": "Enable anti-replay check", "help": "Enable anti-replay check.", "label": "Enable", "name": "enable"}, {"description": "Disable anti-replay check", "help": "Disable anti-replay check.", "label": "Disable", "name": "disable"}] | None = ...,
        tcp_session_without_syn: Literal[{"description": "Enable TCP session without SYN", "help": "Enable TCP session without SYN.", "label": "All", "name": "all"}, {"description": "Enable TCP session data only", "help": "Enable TCP session data only.", "label": "Data Only", "name": "data-only"}, {"description": "Disable TCP session without SYN", "help": "Disable TCP session without SYN.", "label": "Disable", "name": "disable"}] | None = ...,
        geoip_anycast: Literal[{"description": "Enable recognition of anycast IP addresses using the geography IP database", "help": "Enable recognition of anycast IP addresses using the geography IP database.", "label": "Enable", "name": "enable"}, {"description": "Disable recognition of anycast IP addresses using the geography IP database", "help": "Disable recognition of anycast IP addresses using the geography IP database.", "label": "Disable", "name": "disable"}] | None = ...,
        geoip_match: Literal[{"description": "Match geography address to its physical location using the geography IP database", "help": "Match geography address to its physical location using the geography IP database.", "label": "Physical Location", "name": "physical-location"}, {"description": "Match geography address to its registered location using the geography IP database", "help": "Match geography address to its registered location using the geography IP database.", "label": "Registered Location", "name": "registered-location"}] | None = ...,
        dynamic_shaping: Literal[{"description": "Enable dynamic RADIUS defined traffic shaping", "help": "Enable dynamic RADIUS defined traffic shaping.", "label": "Enable", "name": "enable"}, {"description": "Disable dynamic RADIUS defined traffic shaping", "help": "Disable dynamic RADIUS defined traffic shaping.", "label": "Disable", "name": "disable"}] | None = ...,
        passive_wan_health_measurement: Literal[{"description": "Enable Passive WAN health measurement", "help": "Enable Passive WAN health measurement.", "label": "Enable", "name": "enable"}, {"description": "Disable Passive WAN health measurement", "help": "Disable Passive WAN health measurement.", "label": "Disable", "name": "disable"}] | None = ...,
        app_monitor: Literal[{"description": "Enable TCP metrics in session logs", "help": "Enable TCP metrics in session logs.", "label": "Enable", "name": "enable"}, {"description": "Disable TCP metrics in session logs", "help": "Disable TCP metrics in session logs.", "label": "Disable", "name": "disable"}] | None = ...,
        utm_status: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        inspection_mode: Literal[{"description": "Proxy based inspection", "help": "Proxy based inspection.", "label": "Proxy", "name": "proxy"}, {"description": "Flow based inspection", "help": "Flow based inspection.", "label": "Flow", "name": "flow"}] | None = ...,
        http_policy_redirect: Literal[{"description": "Enable HTTP(S) policy redirect", "help": "Enable HTTP(S) policy redirect.", "label": "Enable", "name": "enable"}, {"description": "Disable HTTP(S) policy redirect", "help": "Disable HTTP(S) policy redirect.", "label": "Disable", "name": "disable"}, {"description": "Enable HTTP(S) policy redirect (for preserving old behavior, not recommended for new setups)", "help": "Enable HTTP(S) policy redirect (for preserving old behavior, not recommended for new setups).", "label": "Legacy", "name": "legacy"}] | None = ...,
        ssh_policy_redirect: Literal[{"description": "Enable SSH policy redirect", "help": "Enable SSH policy redirect.", "label": "Enable", "name": "enable"}, {"description": "Disable SSH policy redirect", "help": "Disable SSH policy redirect.", "label": "Disable", "name": "disable"}] | None = ...,
        ztna_policy_redirect: Literal[{"description": "Enable ZTNA proxy-policy redirect", "help": "Enable ZTNA proxy-policy redirect.", "label": "Enable", "name": "enable"}, {"description": "Disable ZTNA proxy-policy redirect", "help": "Disable ZTNA proxy-policy redirect.", "label": "Disable", "name": "disable"}] | None = ...,
        webproxy_profile: str | None = ...,
        profile_type: Literal[{"description": "Do not allow security profile groups", "help": "Do not allow security profile groups.", "label": "Single", "name": "single"}, {"description": "Allow security profile groups", "help": "Allow security profile groups.", "label": "Group", "name": "group"}] | None = ...,
        profile_group: str | None = ...,
        profile_protocol_options: str | None = ...,
        ssl_ssh_profile: str | None = ...,
        av_profile: str | None = ...,
        webfilter_profile: str | None = ...,
        dnsfilter_profile: str | None = ...,
        emailfilter_profile: str | None = ...,
        dlp_profile: str | None = ...,
        file_filter_profile: str | None = ...,
        ips_sensor: str | None = ...,
        application_list: str | None = ...,
        voip_profile: str | None = ...,
        ips_voip_filter: str | None = ...,
        sctp_filter_profile: str | None = ...,
        diameter_filter_profile: str | None = ...,
        virtual_patch_profile: str | None = ...,
        icap_profile: str | None = ...,
        videofilter_profile: str | None = ...,
        waf_profile: str | None = ...,
        ssh_filter_profile: str | None = ...,
        casb_profile: str | None = ...,
        logtraffic: Literal[{"description": "Log all sessions accepted or denied by this policy", "help": "Log all sessions accepted or denied by this policy.", "label": "All", "name": "all"}, {"description": "Log traffic that has a security profile applied to it", "help": "Log traffic that has a security profile applied to it.", "label": "Utm", "name": "utm"}, {"description": "Disable all logging for this policy", "help": "Disable all logging for this policy.", "label": "Disable", "name": "disable"}] | None = ...,
        logtraffic_start: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        log_http_transaction: Literal[{"description": "Enable HTTP transaction log", "help": "Enable HTTP transaction log.", "label": "Enable", "name": "enable"}, {"description": "Disable HTTP transaction log", "help": "Disable HTTP transaction log.", "label": "Disable", "name": "disable"}] | None = ...,
        capture_packet: Literal[{"description": "Enable capture packets", "help": "Enable capture packets.", "label": "Enable", "name": "enable"}, {"description": "Disable capture packets", "help": "Disable capture packets.", "label": "Disable", "name": "disable"}] | None = ...,
        auto_asic_offload: Literal[{"description": "Enable auto ASIC offloading", "help": "Enable auto ASIC offloading.", "label": "Enable", "name": "enable"}, {"description": "Disable ASIC offloading", "help": "Disable ASIC offloading.", "label": "Disable", "name": "disable"}] | None = ...,
        wanopt: Literal[{"help": "Enable setting.", "label": "Enable", "name": "enable"}, {"help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        wanopt_detection: Literal[{"help": "Active WAN optimization peer auto-detection.", "label": "Active", "name": "active"}, {"help": "Passive WAN optimization peer auto-detection.", "label": "Passive", "name": "passive"}, {"help": "Turn off WAN optimization peer auto-detection.", "label": "Off", "name": "off"}] | None = ...,
        wanopt_passive_opt: Literal[{"help": "Allow client side WAN opt peer to decide.", "label": "Default", "name": "default"}, {"help": "Use address of client to connect to server.", "label": "Transparent", "name": "transparent"}, {"help": "Use local FortiGate address to connect to server.", "label": "Non Transparent", "name": "non-transparent"}] | None = ...,
        wanopt_profile: str | None = ...,
        wanopt_peer: str | None = ...,
        webcache: Literal[{"help": "Enable setting.", "label": "Enable", "name": "enable"}, {"help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        webcache_https: Literal[{"help": "Disable web cache for HTTPS.", "label": "Disable", "name": "disable"}, {"help": "Enable web cache for HTTPS.", "label": "Enable", "name": "enable"}] | None = ...,
        webproxy_forward_server: str | None = ...,
        traffic_shaper: str | None = ...,
        traffic_shaper_reverse: str | None = ...,
        per_ip_shaper: str | None = ...,
        nat: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        pcp_outbound: Literal[{"description": "Enable PCP outbound SNAT", "help": "Enable PCP outbound SNAT.", "label": "Enable", "name": "enable"}, {"description": "Disable PCP outbound SNAT", "help": "Disable PCP outbound SNAT.", "label": "Disable", "name": "disable"}] | None = ...,
        pcp_inbound: Literal[{"description": "Enable PCP inbound DNAT", "help": "Enable PCP inbound DNAT.", "label": "Enable", "name": "enable"}, {"description": "Disable PCP inbound DNAT", "help": "Disable PCP inbound DNAT.", "label": "Disable", "name": "disable"}] | None = ...,
        pcp_poolname: list[dict[str, Any]] | None = ...,
        permit_any_host: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        permit_stun_host: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        fixedport: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        port_preserve: Literal[{"description": "Use the original source port if it has not been used", "help": "Use the original source port if it has not been used.", "label": "Enable", "name": "enable"}, {"description": "Source NAT always changes the source port", "help": "Source NAT always changes the source port.", "label": "Disable", "name": "disable"}] | None = ...,
        port_random: Literal[{"description": "Enable random source port selection for source NAT", "help": "Enable random source port selection for source NAT.", "label": "Enable", "name": "enable"}, {"description": "Disable random source port selection for source NAT", "help": "Disable random source port selection for source NAT.", "label": "Disable", "name": "disable"}] | None = ...,
        ippool: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        poolname: list[dict[str, Any]] | None = ...,
        poolname6: list[dict[str, Any]] | None = ...,
        session_ttl: str | None = ...,
        vlan_cos_fwd: int | None = ...,
        vlan_cos_rev: int | None = ...,
        inbound: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        outbound: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        natinbound: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        natoutbound: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        fec: Literal[{"description": "Enable Forward Error Correction", "help": "Enable Forward Error Correction.", "label": "Enable", "name": "enable"}, {"description": "Disable Forward Error Correction", "help": "Disable Forward Error Correction.", "label": "Disable", "name": "disable"}] | None = ...,
        wccp: Literal[{"description": "Enable WCCP setting", "help": "Enable WCCP setting.", "label": "Enable", "name": "enable"}, {"description": "Disable WCCP setting", "help": "Disable WCCP setting.", "label": "Disable", "name": "disable"}] | None = ...,
        ntlm: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        ntlm_guest: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        ntlm_enabled_browsers: list[dict[str, Any]] | None = ...,
        fsso_agent_for_ntlm: str | None = ...,
        groups: list[dict[str, Any]] | None = ...,
        users: list[dict[str, Any]] | None = ...,
        fsso_groups: list[dict[str, Any]] | None = ...,
        auth_path: Literal[{"description": "Enable authentication-based routing", "help": "Enable authentication-based routing.", "label": "Enable", "name": "enable"}, {"description": "Disable authentication-based routing", "help": "Disable authentication-based routing.", "label": "Disable", "name": "disable"}] | None = ...,
        disclaimer: Literal[{"description": "Enable user authentication disclaimer", "help": "Enable user authentication disclaimer.", "label": "Enable", "name": "enable"}, {"description": "Disable user authentication disclaimer", "help": "Disable user authentication disclaimer.", "label": "Disable", "name": "disable"}] | None = ...,
        email_collect: Literal[{"description": "Enable email collection", "help": "Enable email collection.", "label": "Enable", "name": "enable"}, {"description": "Disable email collection", "help": "Disable email collection.", "label": "Disable", "name": "disable"}] | None = ...,
        vpntunnel: str | None = ...,
        natip: str | None = ...,
        match_vip: Literal[{"description": "Match DNATed packet", "help": "Match DNATed packet.", "label": "Enable", "name": "enable"}, {"description": "Do not match DNATed packet", "help": "Do not match DNATed packet.", "label": "Disable", "name": "disable"}] | None = ...,
        match_vip_only: Literal[{"description": "Enable matching of only those packets that have had their destination addresses changed by a VIP", "help": "Enable matching of only those packets that have had their destination addresses changed by a VIP.", "label": "Enable", "name": "enable"}, {"description": "Disable matching of only those packets that have had their destination addresses changed by a VIP", "help": "Disable matching of only those packets that have had their destination addresses changed by a VIP.", "label": "Disable", "name": "disable"}] | None = ...,
        diffserv_copy: Literal[{"description": "Enable DSCP copy", "help": "Enable DSCP copy.", "label": "Enable", "name": "enable"}, {"description": "Disable DSCP copy", "help": "Disable DSCP copy.", "label": "Disable", "name": "disable"}] | None = ...,
        diffserv_forward: Literal[{"description": "Enable setting forward (original) traffic Diffserv", "help": "Enable setting forward (original) traffic Diffserv.", "label": "Enable", "name": "enable"}, {"description": "Disable setting forward (original) traffic Diffserv", "help": "Disable setting forward (original) traffic Diffserv.", "label": "Disable", "name": "disable"}] | None = ...,
        diffserv_reverse: Literal[{"description": "Enable setting reverse (reply) traffic DiffServ", "help": "Enable setting reverse (reply) traffic DiffServ.", "label": "Enable", "name": "enable"}, {"description": "Disable setting reverse (reply) traffic DiffServ", "help": "Disable setting reverse (reply) traffic DiffServ.", "label": "Disable", "name": "disable"}] | None = ...,
        diffservcode_forward: str | None = ...,
        diffservcode_rev: str | None = ...,
        tcp_mss_sender: int | None = ...,
        tcp_mss_receiver: int | None = ...,
        comments: str | None = ...,
        auth_cert: str | None = ...,
        auth_redirect_addr: str | None = ...,
        redirect_url: str | None = ...,
        identity_based_route: str | None = ...,
        block_notification: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        custom_log_fields: list[dict[str, Any]] | None = ...,
        replacemsg_override_group: str | None = ...,
        srcaddr_negate: Literal[{"description": "Enable source address negate", "help": "Enable source address negate.", "label": "Enable", "name": "enable"}, {"description": "Disable source address negate", "help": "Disable source address negate.", "label": "Disable", "name": "disable"}] | None = ...,
        srcaddr6_negate: Literal[{"description": "Enable IPv6 source address negate", "help": "Enable IPv6 source address negate.", "label": "Enable", "name": "enable"}, {"description": "Disable IPv6 source address negate", "help": "Disable IPv6 source address negate.", "label": "Disable", "name": "disable"}] | None = ...,
        dstaddr_negate: Literal[{"description": "Enable destination address negate", "help": "Enable destination address negate.", "label": "Enable", "name": "enable"}, {"description": "Disable destination address negate", "help": "Disable destination address negate.", "label": "Disable", "name": "disable"}] | None = ...,
        dstaddr6_negate: Literal[{"description": "Enable IPv6 destination address negate", "help": "Enable IPv6 destination address negate.", "label": "Enable", "name": "enable"}, {"description": "Disable IPv6 destination address negate", "help": "Disable IPv6 destination address negate.", "label": "Disable", "name": "disable"}] | None = ...,
        ztna_ems_tag_negate: Literal[{"description": "Enable ZTNA EMS tags negate", "help": "Enable ZTNA EMS tags negate.", "label": "Enable", "name": "enable"}, {"description": "Disable ZTNA EMS tags negate", "help": "Disable ZTNA EMS tags negate.", "label": "Disable", "name": "disable"}] | None = ...,
        service_negate: Literal[{"description": "Enable negated service match", "help": "Enable negated service match.", "label": "Enable", "name": "enable"}, {"description": "Disable negated service match", "help": "Disable negated service match.", "label": "Disable", "name": "disable"}] | None = ...,
        internet_service_negate: Literal[{"description": "Enable negated Internet Service match", "help": "Enable negated Internet Service match.", "label": "Enable", "name": "enable"}, {"description": "Disable negated Internet Service match", "help": "Disable negated Internet Service match.", "label": "Disable", "name": "disable"}] | None = ...,
        internet_service_src_negate: Literal[{"description": "Enable negated Internet Service source match", "help": "Enable negated Internet Service source match.", "label": "Enable", "name": "enable"}, {"description": "Disable negated Internet Service source match", "help": "Disable negated Internet Service source match.", "label": "Disable", "name": "disable"}] | None = ...,
        internet_service6_negate: Literal[{"description": "Enable negated IPv6 Internet Service match", "help": "Enable negated IPv6 Internet Service match.", "label": "Enable", "name": "enable"}, {"description": "Disable negated IPv6 Internet Service match", "help": "Disable negated IPv6 Internet Service match.", "label": "Disable", "name": "disable"}] | None = ...,
        internet_service6_src_negate: Literal[{"description": "Enable negated IPv6 Internet Service source match", "help": "Enable negated IPv6 Internet Service source match.", "label": "Enable", "name": "enable"}, {"description": "Disable negated IPv6 Internet Service source match", "help": "Disable negated IPv6 Internet Service source match.", "label": "Disable", "name": "disable"}] | None = ...,
        timeout_send_rst: Literal[{"description": "Enable sending of RST packet upon TCP session expiration", "help": "Enable sending of RST packet upon TCP session expiration.", "label": "Enable", "name": "enable"}, {"description": "Disable sending of RST packet upon TCP session expiration", "help": "Disable sending of RST packet upon TCP session expiration.", "label": "Disable", "name": "disable"}] | None = ...,
        captive_portal_exempt: Literal[{"description": "Enable exemption of captive portal", "help": "Enable exemption of captive portal.", "label": "Enable", "name": "enable"}, {"description": "Disable exemption of captive portal", "help": "Disable exemption of captive portal.", "label": "Disable", "name": "disable"}] | None = ...,
        decrypted_traffic_mirror: str | None = ...,
        dsri: Literal[{"description": "Enable DSRI", "help": "Enable DSRI.", "label": "Enable", "name": "enable"}, {"description": "Disable DSRI", "help": "Disable DSRI.", "label": "Disable", "name": "disable"}] | None = ...,
        radius_mac_auth_bypass: Literal[{"description": "Enable MAC authentication bypass", "help": "Enable MAC authentication bypass.", "label": "Enable", "name": "enable"}, {"description": "Disable MAC authentication bypass", "help": "Disable MAC authentication bypass.", "label": "Disable", "name": "disable"}] | None = ...,
        radius_ip_auth_bypass: Literal[{"description": "Enable IP authentication bypass", "help": "Enable IP authentication bypass.", "label": "Enable", "name": "enable"}, {"description": "Disable IP authentication bypass", "help": "Disable IP authentication bypass.", "label": "Disable", "name": "disable"}] | None = ...,
        delay_tcp_npu_session: Literal[{"description": "Enable TCP NPU session delay in order to guarantee packet order of 3-way handshake", "help": "Enable TCP NPU session delay in order to guarantee packet order of 3-way handshake.", "label": "Enable", "name": "enable"}, {"description": "Disable TCP NPU session delay in order to guarantee packet order of 3-way handshake", "help": "Disable TCP NPU session delay in order to guarantee packet order of 3-way handshake.", "label": "Disable", "name": "disable"}] | None = ...,
        vlan_filter: str | None = ...,
        sgt_check: Literal[{"description": "Enable SGT check", "help": "Enable SGT check.", "label": "Enable", "name": "enable"}, {"description": "Disable SGT check", "help": "Disable SGT check.", "label": "Disable", "name": "disable"}] | None = ...,
        sgt: list[dict[str, Any]] | None = ...,
        internet_service_fortiguard: list[dict[str, Any]] | None = ...,
        internet_service_src_fortiguard: list[dict[str, Any]] | None = ...,
        internet_service6_fortiguard: list[dict[str, Any]] | None = ...,
        internet_service6_src_fortiguard: list[dict[str, Any]] | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: PolicyPayload | None = ...,
        policyid: int | None = ...,
        status: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        name: str | None = ...,
        uuid: str | None = ...,
        srcintf: list[dict[str, Any]] | None = ...,
        dstintf: list[dict[str, Any]] | None = ...,
        action: Literal[{"description": "Allows session that match the firewall policy", "help": "Allows session that match the firewall policy.", "label": "Accept", "name": "accept"}, {"description": "Blocks sessions that match the firewall policy", "help": "Blocks sessions that match the firewall policy.", "label": "Deny", "name": "deny"}, {"description": "Firewall policy becomes a policy-based IPsec VPN policy", "help": "Firewall policy becomes a policy-based IPsec VPN policy.", "label": "Ipsec", "name": "ipsec"}] | None = ...,
        nat64: Literal[{"description": "Enable NAT64", "help": "Enable NAT64.", "label": "Enable", "name": "enable"}, {"description": "Disable NAT64", "help": "Disable NAT64.", "label": "Disable", "name": "disable"}] | None = ...,
        nat46: Literal[{"description": "Enable NAT46", "help": "Enable NAT46.", "label": "Enable", "name": "enable"}, {"description": "Disable NAT46", "help": "Disable NAT46.", "label": "Disable", "name": "disable"}] | None = ...,
        ztna_status: Literal[{"description": "Enable zero trust network access", "help": "Enable zero trust network access.", "label": "Enable", "name": "enable"}, {"description": "Disable zero trust network access", "help": "Disable zero trust network access.", "label": "Disable", "name": "disable"}] | None = ...,
        ztna_device_ownership: Literal[{"description": "Enable ZTNA device ownership check", "help": "Enable ZTNA device ownership check.", "label": "Enable", "name": "enable"}, {"description": "Disable ZTNA device ownership check", "help": "Disable ZTNA device ownership check.", "label": "Disable", "name": "disable"}] | None = ...,
        srcaddr: list[dict[str, Any]] | None = ...,
        dstaddr: list[dict[str, Any]] | None = ...,
        srcaddr6: list[dict[str, Any]] | None = ...,
        dstaddr6: list[dict[str, Any]] | None = ...,
        ztna_ems_tag: list[dict[str, Any]] | None = ...,
        ztna_ems_tag_secondary: list[dict[str, Any]] | None = ...,
        ztna_tags_match_logic: Literal[{"description": "Match ZTNA tags using a logical OR operator", "help": "Match ZTNA tags using a logical OR operator.", "label": "Or", "name": "or"}, {"description": "Match ZTNA tags using a logical AND operator", "help": "Match ZTNA tags using a logical AND operator.", "label": "And", "name": "and"}] | None = ...,
        ztna_geo_tag: list[dict[str, Any]] | None = ...,
        internet_service: Literal[{"description": "Enable use of Internet Services in policy", "help": "Enable use of Internet Services in policy.", "label": "Enable", "name": "enable"}, {"description": "Disable use of Internet Services in policy", "help": "Disable use of Internet Services in policy.", "label": "Disable", "name": "disable"}] | None = ...,
        internet_service_name: list[dict[str, Any]] | None = ...,
        internet_service_group: list[dict[str, Any]] | None = ...,
        internet_service_custom: list[dict[str, Any]] | None = ...,
        network_service_dynamic: list[dict[str, Any]] | None = ...,
        internet_service_custom_group: list[dict[str, Any]] | None = ...,
        internet_service_src: Literal[{"description": "Enable use of Internet Services source in policy", "help": "Enable use of Internet Services source in policy.", "label": "Enable", "name": "enable"}, {"description": "Disable use of Internet Services source in policy", "help": "Disable use of Internet Services source in policy.", "label": "Disable", "name": "disable"}] | None = ...,
        internet_service_src_name: list[dict[str, Any]] | None = ...,
        internet_service_src_group: list[dict[str, Any]] | None = ...,
        internet_service_src_custom: list[dict[str, Any]] | None = ...,
        network_service_src_dynamic: list[dict[str, Any]] | None = ...,
        internet_service_src_custom_group: list[dict[str, Any]] | None = ...,
        reputation_minimum: int | None = ...,
        reputation_direction: Literal[{"description": "Check reputation for source address", "help": "Check reputation for source address.", "label": "Source", "name": "source"}, {"description": "Check reputation for destination address", "help": "Check reputation for destination address.", "label": "Destination", "name": "destination"}] | None = ...,
        src_vendor_mac: list[dict[str, Any]] | None = ...,
        internet_service6: Literal[{"description": "Enable use of IPv6 Internet Services in policy", "help": "Enable use of IPv6 Internet Services in policy.", "label": "Enable", "name": "enable"}, {"description": "Disable use of IPv6 Internet Services in policy", "help": "Disable use of IPv6 Internet Services in policy.", "label": "Disable", "name": "disable"}] | None = ...,
        internet_service6_name: list[dict[str, Any]] | None = ...,
        internet_service6_group: list[dict[str, Any]] | None = ...,
        internet_service6_custom: list[dict[str, Any]] | None = ...,
        internet_service6_custom_group: list[dict[str, Any]] | None = ...,
        internet_service6_src: Literal[{"description": "Enable use of IPv6 Internet Services source in policy", "help": "Enable use of IPv6 Internet Services source in policy.", "label": "Enable", "name": "enable"}, {"description": "Disable use of IPv6 Internet Services source in policy", "help": "Disable use of IPv6 Internet Services source in policy.", "label": "Disable", "name": "disable"}] | None = ...,
        internet_service6_src_name: list[dict[str, Any]] | None = ...,
        internet_service6_src_group: list[dict[str, Any]] | None = ...,
        internet_service6_src_custom: list[dict[str, Any]] | None = ...,
        internet_service6_src_custom_group: list[dict[str, Any]] | None = ...,
        reputation_minimum6: int | None = ...,
        reputation_direction6: Literal[{"description": "Check reputation for IPv6 source address", "help": "Check reputation for IPv6 source address.", "label": "Source", "name": "source"}, {"description": "Check reputation for IPv6 destination address", "help": "Check reputation for IPv6 destination address.", "label": "Destination", "name": "destination"}] | None = ...,
        rtp_nat: Literal[{"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}, {"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}] | None = ...,
        rtp_addr: list[dict[str, Any]] | None = ...,
        send_deny_packet: Literal[{"description": "Disable deny-packet sending", "help": "Disable deny-packet sending.", "label": "Disable", "name": "disable"}, {"description": "Enable deny-packet sending", "help": "Enable deny-packet sending.", "label": "Enable", "name": "enable"}] | None = ...,
        firewall_session_dirty: Literal[{"description": "Flush all current sessions accepted by this policy", "help": "Flush all current sessions accepted by this policy. These sessions must be started and re-matched with policies.", "label": "Check All", "name": "check-all"}, {"description": "Continue to allow sessions already accepted by this policy", "help": "Continue to allow sessions already accepted by this policy.", "label": "Check New", "name": "check-new"}] | None = ...,
        schedule: str | None = ...,
        schedule_timeout: Literal[{"description": "Enable schedule timeout", "help": "Enable schedule timeout.", "label": "Enable", "name": "enable"}, {"description": "Disable schedule timeout", "help": "Disable schedule timeout.", "label": "Disable", "name": "disable"}] | None = ...,
        policy_expiry: Literal[{"description": "Enable policy expiry", "help": "Enable policy expiry.", "label": "Enable", "name": "enable"}, {"description": "Disable polcy expiry", "help": "Disable polcy expiry.", "label": "Disable", "name": "disable"}] | None = ...,
        policy_expiry_date: str | None = ...,
        policy_expiry_date_utc: str | None = ...,
        service: list[dict[str, Any]] | None = ...,
        tos_mask: str | None = ...,
        tos: str | None = ...,
        tos_negate: Literal[{"description": "Enable TOS match negate", "help": "Enable TOS match negate.", "label": "Enable", "name": "enable"}, {"description": "Disable TOS match negate", "help": "Disable TOS match negate.", "label": "Disable", "name": "disable"}] | None = ...,
        anti_replay: Literal[{"description": "Enable anti-replay check", "help": "Enable anti-replay check.", "label": "Enable", "name": "enable"}, {"description": "Disable anti-replay check", "help": "Disable anti-replay check.", "label": "Disable", "name": "disable"}] | None = ...,
        tcp_session_without_syn: Literal[{"description": "Enable TCP session without SYN", "help": "Enable TCP session without SYN.", "label": "All", "name": "all"}, {"description": "Enable TCP session data only", "help": "Enable TCP session data only.", "label": "Data Only", "name": "data-only"}, {"description": "Disable TCP session without SYN", "help": "Disable TCP session without SYN.", "label": "Disable", "name": "disable"}] | None = ...,
        geoip_anycast: Literal[{"description": "Enable recognition of anycast IP addresses using the geography IP database", "help": "Enable recognition of anycast IP addresses using the geography IP database.", "label": "Enable", "name": "enable"}, {"description": "Disable recognition of anycast IP addresses using the geography IP database", "help": "Disable recognition of anycast IP addresses using the geography IP database.", "label": "Disable", "name": "disable"}] | None = ...,
        geoip_match: Literal[{"description": "Match geography address to its physical location using the geography IP database", "help": "Match geography address to its physical location using the geography IP database.", "label": "Physical Location", "name": "physical-location"}, {"description": "Match geography address to its registered location using the geography IP database", "help": "Match geography address to its registered location using the geography IP database.", "label": "Registered Location", "name": "registered-location"}] | None = ...,
        dynamic_shaping: Literal[{"description": "Enable dynamic RADIUS defined traffic shaping", "help": "Enable dynamic RADIUS defined traffic shaping.", "label": "Enable", "name": "enable"}, {"description": "Disable dynamic RADIUS defined traffic shaping", "help": "Disable dynamic RADIUS defined traffic shaping.", "label": "Disable", "name": "disable"}] | None = ...,
        passive_wan_health_measurement: Literal[{"description": "Enable Passive WAN health measurement", "help": "Enable Passive WAN health measurement.", "label": "Enable", "name": "enable"}, {"description": "Disable Passive WAN health measurement", "help": "Disable Passive WAN health measurement.", "label": "Disable", "name": "disable"}] | None = ...,
        app_monitor: Literal[{"description": "Enable TCP metrics in session logs", "help": "Enable TCP metrics in session logs.", "label": "Enable", "name": "enable"}, {"description": "Disable TCP metrics in session logs", "help": "Disable TCP metrics in session logs.", "label": "Disable", "name": "disable"}] | None = ...,
        utm_status: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        inspection_mode: Literal[{"description": "Proxy based inspection", "help": "Proxy based inspection.", "label": "Proxy", "name": "proxy"}, {"description": "Flow based inspection", "help": "Flow based inspection.", "label": "Flow", "name": "flow"}] | None = ...,
        http_policy_redirect: Literal[{"description": "Enable HTTP(S) policy redirect", "help": "Enable HTTP(S) policy redirect.", "label": "Enable", "name": "enable"}, {"description": "Disable HTTP(S) policy redirect", "help": "Disable HTTP(S) policy redirect.", "label": "Disable", "name": "disable"}, {"description": "Enable HTTP(S) policy redirect (for preserving old behavior, not recommended for new setups)", "help": "Enable HTTP(S) policy redirect (for preserving old behavior, not recommended for new setups).", "label": "Legacy", "name": "legacy"}] | None = ...,
        ssh_policy_redirect: Literal[{"description": "Enable SSH policy redirect", "help": "Enable SSH policy redirect.", "label": "Enable", "name": "enable"}, {"description": "Disable SSH policy redirect", "help": "Disable SSH policy redirect.", "label": "Disable", "name": "disable"}] | None = ...,
        ztna_policy_redirect: Literal[{"description": "Enable ZTNA proxy-policy redirect", "help": "Enable ZTNA proxy-policy redirect.", "label": "Enable", "name": "enable"}, {"description": "Disable ZTNA proxy-policy redirect", "help": "Disable ZTNA proxy-policy redirect.", "label": "Disable", "name": "disable"}] | None = ...,
        webproxy_profile: str | None = ...,
        profile_type: Literal[{"description": "Do not allow security profile groups", "help": "Do not allow security profile groups.", "label": "Single", "name": "single"}, {"description": "Allow security profile groups", "help": "Allow security profile groups.", "label": "Group", "name": "group"}] | None = ...,
        profile_group: str | None = ...,
        profile_protocol_options: str | None = ...,
        ssl_ssh_profile: str | None = ...,
        av_profile: str | None = ...,
        webfilter_profile: str | None = ...,
        dnsfilter_profile: str | None = ...,
        emailfilter_profile: str | None = ...,
        dlp_profile: str | None = ...,
        file_filter_profile: str | None = ...,
        ips_sensor: str | None = ...,
        application_list: str | None = ...,
        voip_profile: str | None = ...,
        ips_voip_filter: str | None = ...,
        sctp_filter_profile: str | None = ...,
        diameter_filter_profile: str | None = ...,
        virtual_patch_profile: str | None = ...,
        icap_profile: str | None = ...,
        videofilter_profile: str | None = ...,
        waf_profile: str | None = ...,
        ssh_filter_profile: str | None = ...,
        casb_profile: str | None = ...,
        logtraffic: Literal[{"description": "Log all sessions accepted or denied by this policy", "help": "Log all sessions accepted or denied by this policy.", "label": "All", "name": "all"}, {"description": "Log traffic that has a security profile applied to it", "help": "Log traffic that has a security profile applied to it.", "label": "Utm", "name": "utm"}, {"description": "Disable all logging for this policy", "help": "Disable all logging for this policy.", "label": "Disable", "name": "disable"}] | None = ...,
        logtraffic_start: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        log_http_transaction: Literal[{"description": "Enable HTTP transaction log", "help": "Enable HTTP transaction log.", "label": "Enable", "name": "enable"}, {"description": "Disable HTTP transaction log", "help": "Disable HTTP transaction log.", "label": "Disable", "name": "disable"}] | None = ...,
        capture_packet: Literal[{"description": "Enable capture packets", "help": "Enable capture packets.", "label": "Enable", "name": "enable"}, {"description": "Disable capture packets", "help": "Disable capture packets.", "label": "Disable", "name": "disable"}] | None = ...,
        auto_asic_offload: Literal[{"description": "Enable auto ASIC offloading", "help": "Enable auto ASIC offloading.", "label": "Enable", "name": "enable"}, {"description": "Disable ASIC offloading", "help": "Disable ASIC offloading.", "label": "Disable", "name": "disable"}] | None = ...,
        wanopt: Literal[{"help": "Enable setting.", "label": "Enable", "name": "enable"}, {"help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        wanopt_detection: Literal[{"help": "Active WAN optimization peer auto-detection.", "label": "Active", "name": "active"}, {"help": "Passive WAN optimization peer auto-detection.", "label": "Passive", "name": "passive"}, {"help": "Turn off WAN optimization peer auto-detection.", "label": "Off", "name": "off"}] | None = ...,
        wanopt_passive_opt: Literal[{"help": "Allow client side WAN opt peer to decide.", "label": "Default", "name": "default"}, {"help": "Use address of client to connect to server.", "label": "Transparent", "name": "transparent"}, {"help": "Use local FortiGate address to connect to server.", "label": "Non Transparent", "name": "non-transparent"}] | None = ...,
        wanopt_profile: str | None = ...,
        wanopt_peer: str | None = ...,
        webcache: Literal[{"help": "Enable setting.", "label": "Enable", "name": "enable"}, {"help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        webcache_https: Literal[{"help": "Disable web cache for HTTPS.", "label": "Disable", "name": "disable"}, {"help": "Enable web cache for HTTPS.", "label": "Enable", "name": "enable"}] | None = ...,
        webproxy_forward_server: str | None = ...,
        traffic_shaper: str | None = ...,
        traffic_shaper_reverse: str | None = ...,
        per_ip_shaper: str | None = ...,
        nat: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        pcp_outbound: Literal[{"description": "Enable PCP outbound SNAT", "help": "Enable PCP outbound SNAT.", "label": "Enable", "name": "enable"}, {"description": "Disable PCP outbound SNAT", "help": "Disable PCP outbound SNAT.", "label": "Disable", "name": "disable"}] | None = ...,
        pcp_inbound: Literal[{"description": "Enable PCP inbound DNAT", "help": "Enable PCP inbound DNAT.", "label": "Enable", "name": "enable"}, {"description": "Disable PCP inbound DNAT", "help": "Disable PCP inbound DNAT.", "label": "Disable", "name": "disable"}] | None = ...,
        pcp_poolname: list[dict[str, Any]] | None = ...,
        permit_any_host: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        permit_stun_host: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        fixedport: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        port_preserve: Literal[{"description": "Use the original source port if it has not been used", "help": "Use the original source port if it has not been used.", "label": "Enable", "name": "enable"}, {"description": "Source NAT always changes the source port", "help": "Source NAT always changes the source port.", "label": "Disable", "name": "disable"}] | None = ...,
        port_random: Literal[{"description": "Enable random source port selection for source NAT", "help": "Enable random source port selection for source NAT.", "label": "Enable", "name": "enable"}, {"description": "Disable random source port selection for source NAT", "help": "Disable random source port selection for source NAT.", "label": "Disable", "name": "disable"}] | None = ...,
        ippool: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        poolname: list[dict[str, Any]] | None = ...,
        poolname6: list[dict[str, Any]] | None = ...,
        session_ttl: str | None = ...,
        vlan_cos_fwd: int | None = ...,
        vlan_cos_rev: int | None = ...,
        inbound: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        outbound: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        natinbound: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        natoutbound: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        fec: Literal[{"description": "Enable Forward Error Correction", "help": "Enable Forward Error Correction.", "label": "Enable", "name": "enable"}, {"description": "Disable Forward Error Correction", "help": "Disable Forward Error Correction.", "label": "Disable", "name": "disable"}] | None = ...,
        wccp: Literal[{"description": "Enable WCCP setting", "help": "Enable WCCP setting.", "label": "Enable", "name": "enable"}, {"description": "Disable WCCP setting", "help": "Disable WCCP setting.", "label": "Disable", "name": "disable"}] | None = ...,
        ntlm: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        ntlm_guest: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        ntlm_enabled_browsers: list[dict[str, Any]] | None = ...,
        fsso_agent_for_ntlm: str | None = ...,
        groups: list[dict[str, Any]] | None = ...,
        users: list[dict[str, Any]] | None = ...,
        fsso_groups: list[dict[str, Any]] | None = ...,
        auth_path: Literal[{"description": "Enable authentication-based routing", "help": "Enable authentication-based routing.", "label": "Enable", "name": "enable"}, {"description": "Disable authentication-based routing", "help": "Disable authentication-based routing.", "label": "Disable", "name": "disable"}] | None = ...,
        disclaimer: Literal[{"description": "Enable user authentication disclaimer", "help": "Enable user authentication disclaimer.", "label": "Enable", "name": "enable"}, {"description": "Disable user authentication disclaimer", "help": "Disable user authentication disclaimer.", "label": "Disable", "name": "disable"}] | None = ...,
        email_collect: Literal[{"description": "Enable email collection", "help": "Enable email collection.", "label": "Enable", "name": "enable"}, {"description": "Disable email collection", "help": "Disable email collection.", "label": "Disable", "name": "disable"}] | None = ...,
        vpntunnel: str | None = ...,
        natip: str | None = ...,
        match_vip: Literal[{"description": "Match DNATed packet", "help": "Match DNATed packet.", "label": "Enable", "name": "enable"}, {"description": "Do not match DNATed packet", "help": "Do not match DNATed packet.", "label": "Disable", "name": "disable"}] | None = ...,
        match_vip_only: Literal[{"description": "Enable matching of only those packets that have had their destination addresses changed by a VIP", "help": "Enable matching of only those packets that have had their destination addresses changed by a VIP.", "label": "Enable", "name": "enable"}, {"description": "Disable matching of only those packets that have had their destination addresses changed by a VIP", "help": "Disable matching of only those packets that have had their destination addresses changed by a VIP.", "label": "Disable", "name": "disable"}] | None = ...,
        diffserv_copy: Literal[{"description": "Enable DSCP copy", "help": "Enable DSCP copy.", "label": "Enable", "name": "enable"}, {"description": "Disable DSCP copy", "help": "Disable DSCP copy.", "label": "Disable", "name": "disable"}] | None = ...,
        diffserv_forward: Literal[{"description": "Enable setting forward (original) traffic Diffserv", "help": "Enable setting forward (original) traffic Diffserv.", "label": "Enable", "name": "enable"}, {"description": "Disable setting forward (original) traffic Diffserv", "help": "Disable setting forward (original) traffic Diffserv.", "label": "Disable", "name": "disable"}] | None = ...,
        diffserv_reverse: Literal[{"description": "Enable setting reverse (reply) traffic DiffServ", "help": "Enable setting reverse (reply) traffic DiffServ.", "label": "Enable", "name": "enable"}, {"description": "Disable setting reverse (reply) traffic DiffServ", "help": "Disable setting reverse (reply) traffic DiffServ.", "label": "Disable", "name": "disable"}] | None = ...,
        diffservcode_forward: str | None = ...,
        diffservcode_rev: str | None = ...,
        tcp_mss_sender: int | None = ...,
        tcp_mss_receiver: int | None = ...,
        comments: str | None = ...,
        auth_cert: str | None = ...,
        auth_redirect_addr: str | None = ...,
        redirect_url: str | None = ...,
        identity_based_route: str | None = ...,
        block_notification: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}] | None = ...,
        custom_log_fields: list[dict[str, Any]] | None = ...,
        replacemsg_override_group: str | None = ...,
        srcaddr_negate: Literal[{"description": "Enable source address negate", "help": "Enable source address negate.", "label": "Enable", "name": "enable"}, {"description": "Disable source address negate", "help": "Disable source address negate.", "label": "Disable", "name": "disable"}] | None = ...,
        srcaddr6_negate: Literal[{"description": "Enable IPv6 source address negate", "help": "Enable IPv6 source address negate.", "label": "Enable", "name": "enable"}, {"description": "Disable IPv6 source address negate", "help": "Disable IPv6 source address negate.", "label": "Disable", "name": "disable"}] | None = ...,
        dstaddr_negate: Literal[{"description": "Enable destination address negate", "help": "Enable destination address negate.", "label": "Enable", "name": "enable"}, {"description": "Disable destination address negate", "help": "Disable destination address negate.", "label": "Disable", "name": "disable"}] | None = ...,
        dstaddr6_negate: Literal[{"description": "Enable IPv6 destination address negate", "help": "Enable IPv6 destination address negate.", "label": "Enable", "name": "enable"}, {"description": "Disable IPv6 destination address negate", "help": "Disable IPv6 destination address negate.", "label": "Disable", "name": "disable"}] | None = ...,
        ztna_ems_tag_negate: Literal[{"description": "Enable ZTNA EMS tags negate", "help": "Enable ZTNA EMS tags negate.", "label": "Enable", "name": "enable"}, {"description": "Disable ZTNA EMS tags negate", "help": "Disable ZTNA EMS tags negate.", "label": "Disable", "name": "disable"}] | None = ...,
        service_negate: Literal[{"description": "Enable negated service match", "help": "Enable negated service match.", "label": "Enable", "name": "enable"}, {"description": "Disable negated service match", "help": "Disable negated service match.", "label": "Disable", "name": "disable"}] | None = ...,
        internet_service_negate: Literal[{"description": "Enable negated Internet Service match", "help": "Enable negated Internet Service match.", "label": "Enable", "name": "enable"}, {"description": "Disable negated Internet Service match", "help": "Disable negated Internet Service match.", "label": "Disable", "name": "disable"}] | None = ...,
        internet_service_src_negate: Literal[{"description": "Enable negated Internet Service source match", "help": "Enable negated Internet Service source match.", "label": "Enable", "name": "enable"}, {"description": "Disable negated Internet Service source match", "help": "Disable negated Internet Service source match.", "label": "Disable", "name": "disable"}] | None = ...,
        internet_service6_negate: Literal[{"description": "Enable negated IPv6 Internet Service match", "help": "Enable negated IPv6 Internet Service match.", "label": "Enable", "name": "enable"}, {"description": "Disable negated IPv6 Internet Service match", "help": "Disable negated IPv6 Internet Service match.", "label": "Disable", "name": "disable"}] | None = ...,
        internet_service6_src_negate: Literal[{"description": "Enable negated IPv6 Internet Service source match", "help": "Enable negated IPv6 Internet Service source match.", "label": "Enable", "name": "enable"}, {"description": "Disable negated IPv6 Internet Service source match", "help": "Disable negated IPv6 Internet Service source match.", "label": "Disable", "name": "disable"}] | None = ...,
        timeout_send_rst: Literal[{"description": "Enable sending of RST packet upon TCP session expiration", "help": "Enable sending of RST packet upon TCP session expiration.", "label": "Enable", "name": "enable"}, {"description": "Disable sending of RST packet upon TCP session expiration", "help": "Disable sending of RST packet upon TCP session expiration.", "label": "Disable", "name": "disable"}] | None = ...,
        captive_portal_exempt: Literal[{"description": "Enable exemption of captive portal", "help": "Enable exemption of captive portal.", "label": "Enable", "name": "enable"}, {"description": "Disable exemption of captive portal", "help": "Disable exemption of captive portal.", "label": "Disable", "name": "disable"}] | None = ...,
        decrypted_traffic_mirror: str | None = ...,
        dsri: Literal[{"description": "Enable DSRI", "help": "Enable DSRI.", "label": "Enable", "name": "enable"}, {"description": "Disable DSRI", "help": "Disable DSRI.", "label": "Disable", "name": "disable"}] | None = ...,
        radius_mac_auth_bypass: Literal[{"description": "Enable MAC authentication bypass", "help": "Enable MAC authentication bypass.", "label": "Enable", "name": "enable"}, {"description": "Disable MAC authentication bypass", "help": "Disable MAC authentication bypass.", "label": "Disable", "name": "disable"}] | None = ...,
        radius_ip_auth_bypass: Literal[{"description": "Enable IP authentication bypass", "help": "Enable IP authentication bypass.", "label": "Enable", "name": "enable"}, {"description": "Disable IP authentication bypass", "help": "Disable IP authentication bypass.", "label": "Disable", "name": "disable"}] | None = ...,
        delay_tcp_npu_session: Literal[{"description": "Enable TCP NPU session delay in order to guarantee packet order of 3-way handshake", "help": "Enable TCP NPU session delay in order to guarantee packet order of 3-way handshake.", "label": "Enable", "name": "enable"}, {"description": "Disable TCP NPU session delay in order to guarantee packet order of 3-way handshake", "help": "Disable TCP NPU session delay in order to guarantee packet order of 3-way handshake.", "label": "Disable", "name": "disable"}] | None = ...,
        vlan_filter: str | None = ...,
        sgt_check: Literal[{"description": "Enable SGT check", "help": "Enable SGT check.", "label": "Enable", "name": "enable"}, {"description": "Disable SGT check", "help": "Disable SGT check.", "label": "Disable", "name": "disable"}] | None = ...,
        sgt: list[dict[str, Any]] | None = ...,
        internet_service_fortiguard: list[dict[str, Any]] | None = ...,
        internet_service_src_fortiguard: list[dict[str, Any]] | None = ...,
        internet_service6_fortiguard: list[dict[str, Any]] | None = ...,
        internet_service6_src_fortiguard: list[dict[str, Any]] | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def delete(
        self,
        policyid: int | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def exists(
        self,
        policyid: int,
        vdom: str | bool | None = ...,
    ) -> Union[bool, Coroutine[Any, Any, bool]]: ...
    
    def set(
        self,
        payload_dict: PolicyPayload | None = ...,
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
    "Policy",
    "PolicyPayload",
]