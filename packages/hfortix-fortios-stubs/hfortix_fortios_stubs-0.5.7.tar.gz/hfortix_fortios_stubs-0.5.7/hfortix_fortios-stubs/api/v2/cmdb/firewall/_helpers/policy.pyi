from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_STATUS: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]
VALID_BODY_ACTION: Literal[{"description": "Allows session that match the firewall policy", "help": "Allows session that match the firewall policy.", "label": "Accept", "name": "accept"}, {"description": "Blocks sessions that match the firewall policy", "help": "Blocks sessions that match the firewall policy.", "label": "Deny", "name": "deny"}, {"description": "Firewall policy becomes a policy-based IPsec VPN policy", "help": "Firewall policy becomes a policy-based IPsec VPN policy.", "label": "Ipsec", "name": "ipsec"}]
VALID_BODY_NAT64: Literal[{"description": "Enable NAT64", "help": "Enable NAT64.", "label": "Enable", "name": "enable"}, {"description": "Disable NAT64", "help": "Disable NAT64.", "label": "Disable", "name": "disable"}]
VALID_BODY_NAT46: Literal[{"description": "Enable NAT46", "help": "Enable NAT46.", "label": "Enable", "name": "enable"}, {"description": "Disable NAT46", "help": "Disable NAT46.", "label": "Disable", "name": "disable"}]
VALID_BODY_ZTNA_STATUS: Literal[{"description": "Enable zero trust network access", "help": "Enable zero trust network access.", "label": "Enable", "name": "enable"}, {"description": "Disable zero trust network access", "help": "Disable zero trust network access.", "label": "Disable", "name": "disable"}]
VALID_BODY_ZTNA_DEVICE_OWNERSHIP: Literal[{"description": "Enable ZTNA device ownership check", "help": "Enable ZTNA device ownership check.", "label": "Enable", "name": "enable"}, {"description": "Disable ZTNA device ownership check", "help": "Disable ZTNA device ownership check.", "label": "Disable", "name": "disable"}]
VALID_BODY_ZTNA_TAGS_MATCH_LOGIC: Literal[{"description": "Match ZTNA tags using a logical OR operator", "help": "Match ZTNA tags using a logical OR operator.", "label": "Or", "name": "or"}, {"description": "Match ZTNA tags using a logical AND operator", "help": "Match ZTNA tags using a logical AND operator.", "label": "And", "name": "and"}]
VALID_BODY_INTERNET_SERVICE: Literal[{"description": "Enable use of Internet Services in policy", "help": "Enable use of Internet Services in policy.", "label": "Enable", "name": "enable"}, {"description": "Disable use of Internet Services in policy", "help": "Disable use of Internet Services in policy.", "label": "Disable", "name": "disable"}]
VALID_BODY_INTERNET_SERVICE_SRC: Literal[{"description": "Enable use of Internet Services source in policy", "help": "Enable use of Internet Services source in policy.", "label": "Enable", "name": "enable"}, {"description": "Disable use of Internet Services source in policy", "help": "Disable use of Internet Services source in policy.", "label": "Disable", "name": "disable"}]
VALID_BODY_REPUTATION_DIRECTION: Literal[{"description": "Check reputation for source address", "help": "Check reputation for source address.", "label": "Source", "name": "source"}, {"description": "Check reputation for destination address", "help": "Check reputation for destination address.", "label": "Destination", "name": "destination"}]
VALID_BODY_INTERNET_SERVICE6: Literal[{"description": "Enable use of IPv6 Internet Services in policy", "help": "Enable use of IPv6 Internet Services in policy.", "label": "Enable", "name": "enable"}, {"description": "Disable use of IPv6 Internet Services in policy", "help": "Disable use of IPv6 Internet Services in policy.", "label": "Disable", "name": "disable"}]
VALID_BODY_INTERNET_SERVICE6_SRC: Literal[{"description": "Enable use of IPv6 Internet Services source in policy", "help": "Enable use of IPv6 Internet Services source in policy.", "label": "Enable", "name": "enable"}, {"description": "Disable use of IPv6 Internet Services source in policy", "help": "Disable use of IPv6 Internet Services source in policy.", "label": "Disable", "name": "disable"}]
VALID_BODY_REPUTATION_DIRECTION6: Literal[{"description": "Check reputation for IPv6 source address", "help": "Check reputation for IPv6 source address.", "label": "Source", "name": "source"}, {"description": "Check reputation for IPv6 destination address", "help": "Check reputation for IPv6 destination address.", "label": "Destination", "name": "destination"}]
VALID_BODY_RTP_NAT: Literal[{"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}, {"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}]
VALID_BODY_SEND_DENY_PACKET: Literal[{"description": "Disable deny-packet sending", "help": "Disable deny-packet sending.", "label": "Disable", "name": "disable"}, {"description": "Enable deny-packet sending", "help": "Enable deny-packet sending.", "label": "Enable", "name": "enable"}]
VALID_BODY_FIREWALL_SESSION_DIRTY: Literal[{"description": "Flush all current sessions accepted by this policy", "help": "Flush all current sessions accepted by this policy. These sessions must be started and re-matched with policies.", "label": "Check All", "name": "check-all"}, {"description": "Continue to allow sessions already accepted by this policy", "help": "Continue to allow sessions already accepted by this policy.", "label": "Check New", "name": "check-new"}]
VALID_BODY_SCHEDULE_TIMEOUT: Literal[{"description": "Enable schedule timeout", "help": "Enable schedule timeout.", "label": "Enable", "name": "enable"}, {"description": "Disable schedule timeout", "help": "Disable schedule timeout.", "label": "Disable", "name": "disable"}]
VALID_BODY_POLICY_EXPIRY: Literal[{"description": "Enable policy expiry", "help": "Enable policy expiry.", "label": "Enable", "name": "enable"}, {"description": "Disable polcy expiry", "help": "Disable polcy expiry.", "label": "Disable", "name": "disable"}]
VALID_BODY_TOS_NEGATE: Literal[{"description": "Enable TOS match negate", "help": "Enable TOS match negate.", "label": "Enable", "name": "enable"}, {"description": "Disable TOS match negate", "help": "Disable TOS match negate.", "label": "Disable", "name": "disable"}]
VALID_BODY_ANTI_REPLAY: Literal[{"description": "Enable anti-replay check", "help": "Enable anti-replay check.", "label": "Enable", "name": "enable"}, {"description": "Disable anti-replay check", "help": "Disable anti-replay check.", "label": "Disable", "name": "disable"}]
VALID_BODY_TCP_SESSION_WITHOUT_SYN: Literal[{"description": "Enable TCP session without SYN", "help": "Enable TCP session without SYN.", "label": "All", "name": "all"}, {"description": "Enable TCP session data only", "help": "Enable TCP session data only.", "label": "Data Only", "name": "data-only"}, {"description": "Disable TCP session without SYN", "help": "Disable TCP session without SYN.", "label": "Disable", "name": "disable"}]
VALID_BODY_GEOIP_ANYCAST: Literal[{"description": "Enable recognition of anycast IP addresses using the geography IP database", "help": "Enable recognition of anycast IP addresses using the geography IP database.", "label": "Enable", "name": "enable"}, {"description": "Disable recognition of anycast IP addresses using the geography IP database", "help": "Disable recognition of anycast IP addresses using the geography IP database.", "label": "Disable", "name": "disable"}]
VALID_BODY_GEOIP_MATCH: Literal[{"description": "Match geography address to its physical location using the geography IP database", "help": "Match geography address to its physical location using the geography IP database.", "label": "Physical Location", "name": "physical-location"}, {"description": "Match geography address to its registered location using the geography IP database", "help": "Match geography address to its registered location using the geography IP database.", "label": "Registered Location", "name": "registered-location"}]
VALID_BODY_DYNAMIC_SHAPING: Literal[{"description": "Enable dynamic RADIUS defined traffic shaping", "help": "Enable dynamic RADIUS defined traffic shaping.", "label": "Enable", "name": "enable"}, {"description": "Disable dynamic RADIUS defined traffic shaping", "help": "Disable dynamic RADIUS defined traffic shaping.", "label": "Disable", "name": "disable"}]
VALID_BODY_PASSIVE_WAN_HEALTH_MEASUREMENT: Literal[{"description": "Enable Passive WAN health measurement", "help": "Enable Passive WAN health measurement.", "label": "Enable", "name": "enable"}, {"description": "Disable Passive WAN health measurement", "help": "Disable Passive WAN health measurement.", "label": "Disable", "name": "disable"}]
VALID_BODY_APP_MONITOR: Literal[{"description": "Enable TCP metrics in session logs", "help": "Enable TCP metrics in session logs.", "label": "Enable", "name": "enable"}, {"description": "Disable TCP metrics in session logs", "help": "Disable TCP metrics in session logs.", "label": "Disable", "name": "disable"}]
VALID_BODY_UTM_STATUS: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]
VALID_BODY_INSPECTION_MODE: Literal[{"description": "Proxy based inspection", "help": "Proxy based inspection.", "label": "Proxy", "name": "proxy"}, {"description": "Flow based inspection", "help": "Flow based inspection.", "label": "Flow", "name": "flow"}]
VALID_BODY_HTTP_POLICY_REDIRECT: Literal[{"description": "Enable HTTP(S) policy redirect", "help": "Enable HTTP(S) policy redirect.", "label": "Enable", "name": "enable"}, {"description": "Disable HTTP(S) policy redirect", "help": "Disable HTTP(S) policy redirect.", "label": "Disable", "name": "disable"}, {"description": "Enable HTTP(S) policy redirect (for preserving old behavior, not recommended for new setups)", "help": "Enable HTTP(S) policy redirect (for preserving old behavior, not recommended for new setups).", "label": "Legacy", "name": "legacy"}]
VALID_BODY_SSH_POLICY_REDIRECT: Literal[{"description": "Enable SSH policy redirect", "help": "Enable SSH policy redirect.", "label": "Enable", "name": "enable"}, {"description": "Disable SSH policy redirect", "help": "Disable SSH policy redirect.", "label": "Disable", "name": "disable"}]
VALID_BODY_ZTNA_POLICY_REDIRECT: Literal[{"description": "Enable ZTNA proxy-policy redirect", "help": "Enable ZTNA proxy-policy redirect.", "label": "Enable", "name": "enable"}, {"description": "Disable ZTNA proxy-policy redirect", "help": "Disable ZTNA proxy-policy redirect.", "label": "Disable", "name": "disable"}]
VALID_BODY_PROFILE_TYPE: Literal[{"description": "Do not allow security profile groups", "help": "Do not allow security profile groups.", "label": "Single", "name": "single"}, {"description": "Allow security profile groups", "help": "Allow security profile groups.", "label": "Group", "name": "group"}]
VALID_BODY_LOGTRAFFIC: Literal[{"description": "Log all sessions accepted or denied by this policy", "help": "Log all sessions accepted or denied by this policy.", "label": "All", "name": "all"}, {"description": "Log traffic that has a security profile applied to it", "help": "Log traffic that has a security profile applied to it.", "label": "Utm", "name": "utm"}, {"description": "Disable all logging for this policy", "help": "Disable all logging for this policy.", "label": "Disable", "name": "disable"}]
VALID_BODY_LOGTRAFFIC_START: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]
VALID_BODY_LOG_HTTP_TRANSACTION: Literal[{"description": "Enable HTTP transaction log", "help": "Enable HTTP transaction log.", "label": "Enable", "name": "enable"}, {"description": "Disable HTTP transaction log", "help": "Disable HTTP transaction log.", "label": "Disable", "name": "disable"}]
VALID_BODY_CAPTURE_PACKET: Literal[{"description": "Enable capture packets", "help": "Enable capture packets.", "label": "Enable", "name": "enable"}, {"description": "Disable capture packets", "help": "Disable capture packets.", "label": "Disable", "name": "disable"}]
VALID_BODY_AUTO_ASIC_OFFLOAD: Literal[{"description": "Enable auto ASIC offloading", "help": "Enable auto ASIC offloading.", "label": "Enable", "name": "enable"}, {"description": "Disable ASIC offloading", "help": "Disable ASIC offloading.", "label": "Disable", "name": "disable"}]
VALID_BODY_WANOPT: Literal[{"help": "Enable setting.", "label": "Enable", "name": "enable"}, {"help": "Disable setting.", "label": "Disable", "name": "disable"}]
VALID_BODY_WANOPT_DETECTION: Literal[{"help": "Active WAN optimization peer auto-detection.", "label": "Active", "name": "active"}, {"help": "Passive WAN optimization peer auto-detection.", "label": "Passive", "name": "passive"}, {"help": "Turn off WAN optimization peer auto-detection.", "label": "Off", "name": "off"}]
VALID_BODY_WANOPT_PASSIVE_OPT: Literal[{"help": "Allow client side WAN opt peer to decide.", "label": "Default", "name": "default"}, {"help": "Use address of client to connect to server.", "label": "Transparent", "name": "transparent"}, {"help": "Use local FortiGate address to connect to server.", "label": "Non Transparent", "name": "non-transparent"}]
VALID_BODY_WEBCACHE: Literal[{"help": "Enable setting.", "label": "Enable", "name": "enable"}, {"help": "Disable setting.", "label": "Disable", "name": "disable"}]
VALID_BODY_WEBCACHE_HTTPS: Literal[{"help": "Disable web cache for HTTPS.", "label": "Disable", "name": "disable"}, {"help": "Enable web cache for HTTPS.", "label": "Enable", "name": "enable"}]
VALID_BODY_NAT: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]
VALID_BODY_PCP_OUTBOUND: Literal[{"description": "Enable PCP outbound SNAT", "help": "Enable PCP outbound SNAT.", "label": "Enable", "name": "enable"}, {"description": "Disable PCP outbound SNAT", "help": "Disable PCP outbound SNAT.", "label": "Disable", "name": "disable"}]
VALID_BODY_PCP_INBOUND: Literal[{"description": "Enable PCP inbound DNAT", "help": "Enable PCP inbound DNAT.", "label": "Enable", "name": "enable"}, {"description": "Disable PCP inbound DNAT", "help": "Disable PCP inbound DNAT.", "label": "Disable", "name": "disable"}]
VALID_BODY_PERMIT_ANY_HOST: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]
VALID_BODY_PERMIT_STUN_HOST: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]
VALID_BODY_FIXEDPORT: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]
VALID_BODY_PORT_PRESERVE: Literal[{"description": "Use the original source port if it has not been used", "help": "Use the original source port if it has not been used.", "label": "Enable", "name": "enable"}, {"description": "Source NAT always changes the source port", "help": "Source NAT always changes the source port.", "label": "Disable", "name": "disable"}]
VALID_BODY_PORT_RANDOM: Literal[{"description": "Enable random source port selection for source NAT", "help": "Enable random source port selection for source NAT.", "label": "Enable", "name": "enable"}, {"description": "Disable random source port selection for source NAT", "help": "Disable random source port selection for source NAT.", "label": "Disable", "name": "disable"}]
VALID_BODY_IPPOOL: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]
VALID_BODY_INBOUND: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]
VALID_BODY_OUTBOUND: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]
VALID_BODY_NATINBOUND: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]
VALID_BODY_NATOUTBOUND: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]
VALID_BODY_FEC: Literal[{"description": "Enable Forward Error Correction", "help": "Enable Forward Error Correction.", "label": "Enable", "name": "enable"}, {"description": "Disable Forward Error Correction", "help": "Disable Forward Error Correction.", "label": "Disable", "name": "disable"}]
VALID_BODY_WCCP: Literal[{"description": "Enable WCCP setting", "help": "Enable WCCP setting.", "label": "Enable", "name": "enable"}, {"description": "Disable WCCP setting", "help": "Disable WCCP setting.", "label": "Disable", "name": "disable"}]
VALID_BODY_NTLM: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]
VALID_BODY_NTLM_GUEST: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]
VALID_BODY_AUTH_PATH: Literal[{"description": "Enable authentication-based routing", "help": "Enable authentication-based routing.", "label": "Enable", "name": "enable"}, {"description": "Disable authentication-based routing", "help": "Disable authentication-based routing.", "label": "Disable", "name": "disable"}]
VALID_BODY_DISCLAIMER: Literal[{"description": "Enable user authentication disclaimer", "help": "Enable user authentication disclaimer.", "label": "Enable", "name": "enable"}, {"description": "Disable user authentication disclaimer", "help": "Disable user authentication disclaimer.", "label": "Disable", "name": "disable"}]
VALID_BODY_EMAIL_COLLECT: Literal[{"description": "Enable email collection", "help": "Enable email collection.", "label": "Enable", "name": "enable"}, {"description": "Disable email collection", "help": "Disable email collection.", "label": "Disable", "name": "disable"}]
VALID_BODY_MATCH_VIP: Literal[{"description": "Match DNATed packet", "help": "Match DNATed packet.", "label": "Enable", "name": "enable"}, {"description": "Do not match DNATed packet", "help": "Do not match DNATed packet.", "label": "Disable", "name": "disable"}]
VALID_BODY_MATCH_VIP_ONLY: Literal[{"description": "Enable matching of only those packets that have had their destination addresses changed by a VIP", "help": "Enable matching of only those packets that have had their destination addresses changed by a VIP.", "label": "Enable", "name": "enable"}, {"description": "Disable matching of only those packets that have had their destination addresses changed by a VIP", "help": "Disable matching of only those packets that have had their destination addresses changed by a VIP.", "label": "Disable", "name": "disable"}]
VALID_BODY_DIFFSERV_COPY: Literal[{"description": "Enable DSCP copy", "help": "Enable DSCP copy.", "label": "Enable", "name": "enable"}, {"description": "Disable DSCP copy", "help": "Disable DSCP copy.", "label": "Disable", "name": "disable"}]
VALID_BODY_DIFFSERV_FORWARD: Literal[{"description": "Enable setting forward (original) traffic Diffserv", "help": "Enable setting forward (original) traffic Diffserv.", "label": "Enable", "name": "enable"}, {"description": "Disable setting forward (original) traffic Diffserv", "help": "Disable setting forward (original) traffic Diffserv.", "label": "Disable", "name": "disable"}]
VALID_BODY_DIFFSERV_REVERSE: Literal[{"description": "Enable setting reverse (reply) traffic DiffServ", "help": "Enable setting reverse (reply) traffic DiffServ.", "label": "Enable", "name": "enable"}, {"description": "Disable setting reverse (reply) traffic DiffServ", "help": "Disable setting reverse (reply) traffic DiffServ.", "label": "Disable", "name": "disable"}]
VALID_BODY_BLOCK_NOTIFICATION: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]
VALID_BODY_SRCADDR_NEGATE: Literal[{"description": "Enable source address negate", "help": "Enable source address negate.", "label": "Enable", "name": "enable"}, {"description": "Disable source address negate", "help": "Disable source address negate.", "label": "Disable", "name": "disable"}]
VALID_BODY_SRCADDR6_NEGATE: Literal[{"description": "Enable IPv6 source address negate", "help": "Enable IPv6 source address negate.", "label": "Enable", "name": "enable"}, {"description": "Disable IPv6 source address negate", "help": "Disable IPv6 source address negate.", "label": "Disable", "name": "disable"}]
VALID_BODY_DSTADDR_NEGATE: Literal[{"description": "Enable destination address negate", "help": "Enable destination address negate.", "label": "Enable", "name": "enable"}, {"description": "Disable destination address negate", "help": "Disable destination address negate.", "label": "Disable", "name": "disable"}]
VALID_BODY_DSTADDR6_NEGATE: Literal[{"description": "Enable IPv6 destination address negate", "help": "Enable IPv6 destination address negate.", "label": "Enable", "name": "enable"}, {"description": "Disable IPv6 destination address negate", "help": "Disable IPv6 destination address negate.", "label": "Disable", "name": "disable"}]
VALID_BODY_ZTNA_EMS_TAG_NEGATE: Literal[{"description": "Enable ZTNA EMS tags negate", "help": "Enable ZTNA EMS tags negate.", "label": "Enable", "name": "enable"}, {"description": "Disable ZTNA EMS tags negate", "help": "Disable ZTNA EMS tags negate.", "label": "Disable", "name": "disable"}]
VALID_BODY_SERVICE_NEGATE: Literal[{"description": "Enable negated service match", "help": "Enable negated service match.", "label": "Enable", "name": "enable"}, {"description": "Disable negated service match", "help": "Disable negated service match.", "label": "Disable", "name": "disable"}]
VALID_BODY_INTERNET_SERVICE_NEGATE: Literal[{"description": "Enable negated Internet Service match", "help": "Enable negated Internet Service match.", "label": "Enable", "name": "enable"}, {"description": "Disable negated Internet Service match", "help": "Disable negated Internet Service match.", "label": "Disable", "name": "disable"}]
VALID_BODY_INTERNET_SERVICE_SRC_NEGATE: Literal[{"description": "Enable negated Internet Service source match", "help": "Enable negated Internet Service source match.", "label": "Enable", "name": "enable"}, {"description": "Disable negated Internet Service source match", "help": "Disable negated Internet Service source match.", "label": "Disable", "name": "disable"}]
VALID_BODY_INTERNET_SERVICE6_NEGATE: Literal[{"description": "Enable negated IPv6 Internet Service match", "help": "Enable negated IPv6 Internet Service match.", "label": "Enable", "name": "enable"}, {"description": "Disable negated IPv6 Internet Service match", "help": "Disable negated IPv6 Internet Service match.", "label": "Disable", "name": "disable"}]
VALID_BODY_INTERNET_SERVICE6_SRC_NEGATE: Literal[{"description": "Enable negated IPv6 Internet Service source match", "help": "Enable negated IPv6 Internet Service source match.", "label": "Enable", "name": "enable"}, {"description": "Disable negated IPv6 Internet Service source match", "help": "Disable negated IPv6 Internet Service source match.", "label": "Disable", "name": "disable"}]
VALID_BODY_TIMEOUT_SEND_RST: Literal[{"description": "Enable sending of RST packet upon TCP session expiration", "help": "Enable sending of RST packet upon TCP session expiration.", "label": "Enable", "name": "enable"}, {"description": "Disable sending of RST packet upon TCP session expiration", "help": "Disable sending of RST packet upon TCP session expiration.", "label": "Disable", "name": "disable"}]
VALID_BODY_CAPTIVE_PORTAL_EXEMPT: Literal[{"description": "Enable exemption of captive portal", "help": "Enable exemption of captive portal.", "label": "Enable", "name": "enable"}, {"description": "Disable exemption of captive portal", "help": "Disable exemption of captive portal.", "label": "Disable", "name": "disable"}]
VALID_BODY_DSRI: Literal[{"description": "Enable DSRI", "help": "Enable DSRI.", "label": "Enable", "name": "enable"}, {"description": "Disable DSRI", "help": "Disable DSRI.", "label": "Disable", "name": "disable"}]
VALID_BODY_RADIUS_MAC_AUTH_BYPASS: Literal[{"description": "Enable MAC authentication bypass", "help": "Enable MAC authentication bypass.", "label": "Enable", "name": "enable"}, {"description": "Disable MAC authentication bypass", "help": "Disable MAC authentication bypass.", "label": "Disable", "name": "disable"}]
VALID_BODY_RADIUS_IP_AUTH_BYPASS: Literal[{"description": "Enable IP authentication bypass", "help": "Enable IP authentication bypass.", "label": "Enable", "name": "enable"}, {"description": "Disable IP authentication bypass", "help": "Disable IP authentication bypass.", "label": "Disable", "name": "disable"}]
VALID_BODY_DELAY_TCP_NPU_SESSION: Literal[{"description": "Enable TCP NPU session delay in order to guarantee packet order of 3-way handshake", "help": "Enable TCP NPU session delay in order to guarantee packet order of 3-way handshake.", "label": "Enable", "name": "enable"}, {"description": "Disable TCP NPU session delay in order to guarantee packet order of 3-way handshake", "help": "Disable TCP NPU session delay in order to guarantee packet order of 3-way handshake.", "label": "Disable", "name": "disable"}]
VALID_BODY_SGT_CHECK: Literal[{"description": "Enable SGT check", "help": "Enable SGT check.", "label": "Enable", "name": "enable"}, {"description": "Disable SGT check", "help": "Disable SGT check.", "label": "Disable", "name": "disable"}]

# Metadata dictionaries
FIELD_TYPES: dict[str, str]
FIELD_DESCRIPTIONS: dict[str, str]
FIELD_CONSTRAINTS: dict[str, dict[str, Any]]
NESTED_SCHEMAS: dict[str, dict[str, Any]]
FIELDS_WITH_DEFAULTS: dict[str, Any]

# Helper functions
def get_field_type(field_name: str) -> str | None: ...
def get_field_description(field_name: str) -> str | None: ...
def get_field_default(field_name: str) -> Any: ...
def get_field_constraints(field_name: str) -> dict[str, Any]: ...
def get_nested_schema(field_name: str) -> dict[str, Any] | None: ...
def get_field_metadata(field_name: str) -> dict[str, Any]: ...
def validate_field_value(field_name: str, value: Any) -> bool: ...
def get_all_fields() -> list[str]: ...
def get_required_fields() -> list[str]: ...
def get_schema_info() -> dict[str, Any]: ...


__all__ = [
    "VALID_BODY_STATUS",
    "VALID_BODY_ACTION",
    "VALID_BODY_NAT64",
    "VALID_BODY_NAT46",
    "VALID_BODY_ZTNA_STATUS",
    "VALID_BODY_ZTNA_DEVICE_OWNERSHIP",
    "VALID_BODY_ZTNA_TAGS_MATCH_LOGIC",
    "VALID_BODY_INTERNET_SERVICE",
    "VALID_BODY_INTERNET_SERVICE_SRC",
    "VALID_BODY_REPUTATION_DIRECTION",
    "VALID_BODY_INTERNET_SERVICE6",
    "VALID_BODY_INTERNET_SERVICE6_SRC",
    "VALID_BODY_REPUTATION_DIRECTION6",
    "VALID_BODY_RTP_NAT",
    "VALID_BODY_SEND_DENY_PACKET",
    "VALID_BODY_FIREWALL_SESSION_DIRTY",
    "VALID_BODY_SCHEDULE_TIMEOUT",
    "VALID_BODY_POLICY_EXPIRY",
    "VALID_BODY_TOS_NEGATE",
    "VALID_BODY_ANTI_REPLAY",
    "VALID_BODY_TCP_SESSION_WITHOUT_SYN",
    "VALID_BODY_GEOIP_ANYCAST",
    "VALID_BODY_GEOIP_MATCH",
    "VALID_BODY_DYNAMIC_SHAPING",
    "VALID_BODY_PASSIVE_WAN_HEALTH_MEASUREMENT",
    "VALID_BODY_APP_MONITOR",
    "VALID_BODY_UTM_STATUS",
    "VALID_BODY_INSPECTION_MODE",
    "VALID_BODY_HTTP_POLICY_REDIRECT",
    "VALID_BODY_SSH_POLICY_REDIRECT",
    "VALID_BODY_ZTNA_POLICY_REDIRECT",
    "VALID_BODY_PROFILE_TYPE",
    "VALID_BODY_LOGTRAFFIC",
    "VALID_BODY_LOGTRAFFIC_START",
    "VALID_BODY_LOG_HTTP_TRANSACTION",
    "VALID_BODY_CAPTURE_PACKET",
    "VALID_BODY_AUTO_ASIC_OFFLOAD",
    "VALID_BODY_WANOPT",
    "VALID_BODY_WANOPT_DETECTION",
    "VALID_BODY_WANOPT_PASSIVE_OPT",
    "VALID_BODY_WEBCACHE",
    "VALID_BODY_WEBCACHE_HTTPS",
    "VALID_BODY_NAT",
    "VALID_BODY_PCP_OUTBOUND",
    "VALID_BODY_PCP_INBOUND",
    "VALID_BODY_PERMIT_ANY_HOST",
    "VALID_BODY_PERMIT_STUN_HOST",
    "VALID_BODY_FIXEDPORT",
    "VALID_BODY_PORT_PRESERVE",
    "VALID_BODY_PORT_RANDOM",
    "VALID_BODY_IPPOOL",
    "VALID_BODY_INBOUND",
    "VALID_BODY_OUTBOUND",
    "VALID_BODY_NATINBOUND",
    "VALID_BODY_NATOUTBOUND",
    "VALID_BODY_FEC",
    "VALID_BODY_WCCP",
    "VALID_BODY_NTLM",
    "VALID_BODY_NTLM_GUEST",
    "VALID_BODY_AUTH_PATH",
    "VALID_BODY_DISCLAIMER",
    "VALID_BODY_EMAIL_COLLECT",
    "VALID_BODY_MATCH_VIP",
    "VALID_BODY_MATCH_VIP_ONLY",
    "VALID_BODY_DIFFSERV_COPY",
    "VALID_BODY_DIFFSERV_FORWARD",
    "VALID_BODY_DIFFSERV_REVERSE",
    "VALID_BODY_BLOCK_NOTIFICATION",
    "VALID_BODY_SRCADDR_NEGATE",
    "VALID_BODY_SRCADDR6_NEGATE",
    "VALID_BODY_DSTADDR_NEGATE",
    "VALID_BODY_DSTADDR6_NEGATE",
    "VALID_BODY_ZTNA_EMS_TAG_NEGATE",
    "VALID_BODY_SERVICE_NEGATE",
    "VALID_BODY_INTERNET_SERVICE_NEGATE",
    "VALID_BODY_INTERNET_SERVICE_SRC_NEGATE",
    "VALID_BODY_INTERNET_SERVICE6_NEGATE",
    "VALID_BODY_INTERNET_SERVICE6_SRC_NEGATE",
    "VALID_BODY_TIMEOUT_SEND_RST",
    "VALID_BODY_CAPTIVE_PORTAL_EXEMPT",
    "VALID_BODY_DSRI",
    "VALID_BODY_RADIUS_MAC_AUTH_BYPASS",
    "VALID_BODY_RADIUS_IP_AUTH_BYPASS",
    "VALID_BODY_DELAY_TCP_NPU_SESSION",
    "VALID_BODY_SGT_CHECK",
    "FIELD_TYPES",
    "FIELD_DESCRIPTIONS",
    "FIELD_CONSTRAINTS",
    "NESTED_SCHEMAS",
    "FIELDS_WITH_DEFAULTS",
    "get_field_type",
    "get_field_description",
    "get_field_default",
    "get_field_constraints",
    "get_nested_schema",
    "get_field_metadata",
    "validate_field_value",
    "get_all_fields",
    "get_required_fields",
    "get_schema_info",
]