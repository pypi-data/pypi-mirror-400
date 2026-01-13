from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_VDOM_TYPE: Literal[{"description": "Change to traffic VDOM    lan-extension:Change to lan-extension VDOM    admin:Change to admin VDOM", "help": "Change to traffic VDOM", "label": "Traffic", "name": "traffic"}, {"help": "Change to lan-extension VDOM", "label": "Lan Extension", "name": "lan-extension"}, {"help": "Change to admin VDOM", "label": "Admin", "name": "admin"}]
VALID_BODY_OPMODE: Literal[{"description": "Change to NAT mode", "help": "Change to NAT mode.", "label": "Nat", "name": "nat"}, {"description": "Change to transparent mode", "help": "Change to transparent mode.", "label": "Transparent", "name": "transparent"}]
VALID_BODY_NGFW_MODE: Literal[{"description": "Application and web-filtering are configured using profiles applied to policy entries", "help": "Application and web-filtering are configured using profiles applied to policy entries.", "label": "Profile Based", "name": "profile-based"}, {"description": "Application and web-filtering are configured as policy match conditions", "help": "Application and web-filtering are configured as policy match conditions.", "label": "Policy Based", "name": "policy-based"}]
VALID_BODY_HTTP_EXTERNAL_DEST: Literal[{"description": "Offload HTTP traffic to FortiWeb for Web Application Firewall inspection", "help": "Offload HTTP traffic to FortiWeb for Web Application Firewall inspection.", "label": "Fortiweb", "name": "fortiweb"}, {"description": "Offload HTTP traffic to FortiCache for external web caching and WAN optimization", "help": "Offload HTTP traffic to FortiCache for external web caching and WAN optimization.", "label": "Forticache", "name": "forticache"}]
VALID_BODY_FIREWALL_SESSION_DIRTY: Literal[{"description": "All sessions affected by a firewall policy change are flushed from the session table", "help": "All sessions affected by a firewall policy change are flushed from the session table. When new packets are received they are re-evaluated by stateful inspection and re-added to the session table.", "label": "Check All", "name": "check-all"}, {"description": "Established sessions for changed firewall policies continue without being affected by the policy configuration change", "help": "Established sessions for changed firewall policies continue without being affected by the policy configuration change. New sessions are evaluated according to the new firewall policy configuration.", "label": "Check New", "name": "check-new"}, {"description": "Sessions are managed individually depending on the firewall policy", "help": "Sessions are managed individually depending on the firewall policy. Some sessions may restart. Some may continue.", "label": "Check Policy Option", "name": "check-policy-option"}]
VALID_BODY_BFD: Literal[{"description": "Enable Bi-directional Forwarding Detection (BFD) on all interfaces", "help": "Enable Bi-directional Forwarding Detection (BFD) on all interfaces.", "label": "Enable", "name": "enable"}, {"description": "Disable Bi-directional Forwarding Detection (BFD) on all interfaces", "help": "Disable Bi-directional Forwarding Detection (BFD) on all interfaces.", "label": "Disable", "name": "disable"}]
VALID_BODY_BFD_DONT_ENFORCE_SRC_PORT: Literal[{"description": "Enable verifying the source port of BFD Packets", "help": "Enable verifying the source port of BFD Packets.", "label": "Enable", "name": "enable"}, {"description": "Disable verifying the source port of BFD Packets", "help": "Disable verifying the source port of BFD Packets.", "label": "Disable", "name": "disable"}]
VALID_BODY_UTF8_SPAM_TAGGING: Literal[{"description": "Convert antispam tags to UTF-8", "help": "Convert antispam tags to UTF-8.", "label": "Enable", "name": "enable"}, {"description": "Do not convert antispam tags", "help": "Do not convert antispam tags.", "label": "Disable", "name": "disable"}]
VALID_BODY_WCCP_CACHE_ENGINE: Literal[{"description": "Enable WCCP cache engine", "help": "Enable WCCP cache engine.", "label": "Enable", "name": "enable"}, {"description": "Disable WCCP cache engine", "help": "Disable WCCP cache engine.", "label": "Disable", "name": "disable"}]
VALID_BODY_VPN_STATS_LOG: Literal[{"description": "IPsec", "help": "IPsec.", "label": "Ipsec", "name": "ipsec"}, {"description": "PPTP", "help": "PPTP.", "label": "Pptp", "name": "pptp"}, {"description": "L2TP", "help": "L2TP.", "label": "L2Tp", "name": "l2tp"}, {"help": "SSL.", "label": "Ssl", "name": "ssl"}]
VALID_BODY_V4_ECMP_MODE: Literal[{"description": "Select next hop based on source IP", "help": "Select next hop based on source IP.", "label": "Source Ip Based", "name": "source-ip-based"}, {"description": "Select next hop based on weight", "help": "Select next hop based on weight.", "label": "Weight Based", "name": "weight-based"}, {"description": "Select next hop based on usage", "help": "Select next hop based on usage.", "label": "Usage Based", "name": "usage-based"}, {"description": "Select next hop based on both source and destination IPs", "help": "Select next hop based on both source and destination IPs.", "label": "Source Dest Ip Based", "name": "source-dest-ip-based"}]
VALID_BODY_FW_SESSION_HAIRPIN: Literal[{"description": "Perform a policy check every time", "help": "Perform a policy check every time.", "label": "Enable", "name": "enable"}, {"description": "Perform a policy check only the first time the session is received", "help": "Perform a policy check only the first time the session is received.", "label": "Disable", "name": "disable"}]
VALID_BODY_PRP_TRAILER_ACTION: Literal[{"description": "Try to keep PRP trailer", "help": "Try to keep PRP trailer.", "label": "Enable", "name": "enable"}, {"description": "Trim PRP trailer", "help": "Trim PRP trailer.", "label": "Disable", "name": "disable"}]
VALID_BODY_SNAT_HAIRPIN_TRAFFIC: Literal[{"description": "Enable SNAT for VIP hairpin traffic", "help": "Enable SNAT for VIP hairpin traffic.", "label": "Enable", "name": "enable"}, {"description": "Disable SNAT for VIP hairpin traffic", "help": "Disable SNAT for VIP hairpin traffic.", "label": "Disable", "name": "disable"}]
VALID_BODY_DHCP_PROXY: Literal[{"description": "Enable the DHCP proxy", "help": "Enable the DHCP proxy.", "label": "Enable", "name": "enable"}, {"description": "Disable the DHCP proxy", "help": "Disable the DHCP proxy.", "label": "Disable", "name": "disable"}]
VALID_BODY_DHCP_PROXY_INTERFACE_SELECT_METHOD: Literal[{"description": "Set outgoing interface automatically", "help": "Set outgoing interface automatically.", "label": "Auto", "name": "auto"}, {"description": "Set outgoing interface by SD-WAN or policy routing rules", "help": "Set outgoing interface by SD-WAN or policy routing rules.", "label": "Sdwan", "name": "sdwan"}, {"description": "Set outgoing interface manually", "help": "Set outgoing interface manually.", "label": "Specify", "name": "specify"}]
VALID_BODY_CENTRAL_NAT: Literal[{"description": "Enable central NAT", "help": "Enable central NAT.", "label": "Enable", "name": "enable"}, {"description": "Disable central NAT", "help": "Disable central NAT.", "label": "Disable", "name": "disable"}]
VALID_BODY_LLDP_RECEPTION: Literal[{"description": "Enable LLDP reception for this VDOM", "help": "Enable LLDP reception for this VDOM.", "label": "Enable", "name": "enable"}, {"description": "Disable LLDP reception for this VDOM", "help": "Disable LLDP reception for this VDOM.", "label": "Disable", "name": "disable"}, {"description": "Use the global LLDP reception configuration for this VDOM", "help": "Use the global LLDP reception configuration for this VDOM.", "label": "Global", "name": "global"}]
VALID_BODY_LLDP_TRANSMISSION: Literal[{"description": "Enable LLDP transmission for this VDOM", "help": "Enable LLDP transmission for this VDOM.", "label": "Enable", "name": "enable"}, {"description": "Disable LLDP transmission for this VDOM", "help": "Disable LLDP transmission for this VDOM.", "label": "Disable", "name": "disable"}, {"description": "Use the global LLDP transmission configuration for this VDOM", "help": "Use the global LLDP transmission configuration for this VDOM.", "label": "Global", "name": "global"}]
VALID_BODY_LINK_DOWN_ACCESS: Literal[{"description": "Allow link down access traffic", "help": "Allow link down access traffic.", "label": "Enable", "name": "enable"}, {"description": "Block link down access traffic", "help": "Block link down access traffic.", "label": "Disable", "name": "disable"}]
VALID_BODY_NAT46_GENERATE_IPV6_FRAGMENT_HEADER: Literal[{"description": "Enable NAT46 IPv6 fragment header generation", "help": "Enable NAT46 IPv6 fragment header generation.", "label": "Enable", "name": "enable"}, {"description": "Disable NAT46 IPv6 fragment header generation", "help": "Disable NAT46 IPv6 fragment header generation.", "label": "Disable", "name": "disable"}]
VALID_BODY_NAT46_FORCE_IPV4_PACKET_FORWARDING: Literal[{"description": "Enable mandatory IPv4 packet forwarding when IPv4 DF is set to 1", "help": "Enable mandatory IPv4 packet forwarding when IPv4 DF is set to 1.", "label": "Enable", "name": "enable"}, {"description": "Disable mandatory IPv4 packet forwarding when IPv4 DF is set to 1", "help": "Disable mandatory IPv4 packet forwarding when IPv4 DF is set to 1.", "label": "Disable", "name": "disable"}]
VALID_BODY_NAT64_FORCE_IPV6_PACKET_FORWARDING: Literal[{"description": "Enable mandatory IPv6 packet forwarding    disable:Disable mandatory IPv6 packet forwarding", "help": "Enable mandatory IPv6 packet forwarding", "label": "Enable", "name": "enable"}, {"help": "Disable mandatory IPv6 packet forwarding", "label": "Disable", "name": "disable"}]
VALID_BODY_DETECT_UNKNOWN_ESP: Literal[{"description": "Enable detection of unknown ESP packets and drop the ESP packet if it\u0027s unknown", "help": "Enable detection of unknown ESP packets and drop the ESP packet if it\u0027s unknown.", "label": "Enable", "name": "enable"}, {"description": "Disable detection of unknown ESP packets", "help": "Disable detection of unknown ESP packets.", "label": "Disable", "name": "disable"}]
VALID_BODY_INTREE_SES_BEST_ROUTE: Literal[{"description": "Force the intree session to always use the best route", "help": "Force the intree session to always use the best route.", "label": "Force", "name": "force"}, {"description": "Don\u0027t force the intree session to always use the best route", "help": "Don\u0027t force the intree session to always use the best route.", "label": "Disable", "name": "disable"}]
VALID_BODY_AUXILIARY_SESSION: Literal[{"description": "Enable auxiliary session for this VDOM", "help": "Enable auxiliary session for this VDOM.", "label": "Enable", "name": "enable"}, {"description": "Disable auxiliary session for this VDOM", "help": "Disable auxiliary session for this VDOM.", "label": "Disable", "name": "disable"}]
VALID_BODY_ASYMROUTE: Literal[{"description": "Enable IPv4 asymmetric routing", "help": "Enable IPv4 asymmetric routing.", "label": "Enable", "name": "enable"}, {"description": "Disable IPv4 asymmetric routing", "help": "Disable IPv4 asymmetric routing.", "label": "Disable", "name": "disable"}]
VALID_BODY_ASYMROUTE_ICMP: Literal[{"description": "Enable ICMP asymmetric routing", "help": "Enable ICMP asymmetric routing.", "label": "Enable", "name": "enable"}, {"description": "Disable ICMP asymmetric routing", "help": "Disable ICMP asymmetric routing.", "label": "Disable", "name": "disable"}]
VALID_BODY_TCP_SESSION_WITHOUT_SYN: Literal[{"description": "Allow TCP session without SYN flags", "help": "Allow TCP session without SYN flags.", "label": "Enable", "name": "enable"}, {"description": "Do not allow TCP session without SYN flags", "help": "Do not allow TCP session without SYN flags.", "label": "Disable", "name": "disable"}]
VALID_BODY_SES_DENIED_TRAFFIC: Literal[{"description": "Include denied sessions in the session table", "help": "Include denied sessions in the session table.", "label": "Enable", "name": "enable"}, {"description": "Do not add denied sessions to the session table", "help": "Do not add denied sessions to the session table.", "label": "Disable", "name": "disable"}]
VALID_BODY_SES_DENIED_MULTICAST_TRAFFIC: Literal[{"description": "Include denied multicast sessions in the session table", "help": "Include denied multicast sessions in the session table.", "label": "Enable", "name": "enable"}, {"description": "Do not add denied multicast sessions to the session table", "help": "Do not add denied multicast sessions to the session table.", "label": "Disable", "name": "disable"}]
VALID_BODY_STRICT_SRC_CHECK: Literal[{"description": "Enable strict source verification", "help": "Enable strict source verification.", "label": "Enable", "name": "enable"}, {"description": "Disable strict source verification", "help": "Disable strict source verification.", "label": "Disable", "name": "disable"}]
VALID_BODY_ALLOW_LINKDOWN_PATH: Literal[{"description": "Allow link down path", "help": "Allow link down path.", "label": "Enable", "name": "enable"}, {"description": "Do not allow link down path", "help": "Do not allow link down path.", "label": "Disable", "name": "disable"}]
VALID_BODY_ASYMROUTE6: Literal[{"description": "Enable asymmetric IPv6 routing", "help": "Enable asymmetric IPv6 routing.", "label": "Enable", "name": "enable"}, {"description": "Disable asymmetric IPv6 routing", "help": "Disable asymmetric IPv6 routing.", "label": "Disable", "name": "disable"}]
VALID_BODY_ASYMROUTE6_ICMP: Literal[{"description": "Enable asymmetric ICMPv6 routing", "help": "Enable asymmetric ICMPv6 routing.", "label": "Enable", "name": "enable"}, {"description": "Disable asymmetric ICMPv6 routing", "help": "Disable asymmetric ICMPv6 routing.", "label": "Disable", "name": "disable"}]
VALID_BODY_SCTP_SESSION_WITHOUT_INIT: Literal[{"description": "Enable SCTP session creation without SCTP INIT", "help": "Enable SCTP session creation without SCTP INIT.", "label": "Enable", "name": "enable"}, {"description": "Disable SCTP session creation without SCTP INIT", "help": "Disable SCTP session creation without SCTP INIT.", "label": "Disable", "name": "disable"}]
VALID_BODY_SIP_EXPECTATION: Literal[{"description": "Allow SIP session helper to create an expectation for port 5060", "help": "Allow SIP session helper to create an expectation for port 5060.", "label": "Enable", "name": "enable"}, {"description": "Prevent SIP session helper from creating an expectation for port 5060", "help": "Prevent SIP session helper from creating an expectation for port 5060.", "label": "Disable", "name": "disable"}]
VALID_BODY_SIP_NAT_TRACE: Literal[{"description": "Record the original SIP source IP address when NAT is used", "help": "Record the original SIP source IP address when NAT is used.", "label": "Enable", "name": "enable"}, {"description": "Do not record the original SIP source IP address when NAT is used", "help": "Do not record the original SIP source IP address when NAT is used.", "label": "Disable", "name": "disable"}]
VALID_BODY_H323_DIRECT_MODEL: Literal[{"description": "Disable H323 direct model", "help": "Disable H323 direct model.", "label": "Disable", "name": "disable"}, {"description": "Enable H323 direct model", "help": "Enable H323 direct model.", "label": "Enable", "name": "enable"}]
VALID_BODY_STATUS: Literal[{"description": "Enable this VDOM", "help": "Enable this VDOM.", "label": "Enable", "name": "enable"}, {"description": "Disable this VDOM", "help": "Disable this VDOM.", "label": "Disable", "name": "disable"}]
VALID_BODY_MULTICAST_FORWARD: Literal[{"description": "Enable multicast forwarding", "help": "Enable multicast forwarding.", "label": "Enable", "name": "enable"}, {"description": "Disable multicast forwarding", "help": "Disable multicast forwarding.", "label": "Disable", "name": "disable"}]
VALID_BODY_MULTICAST_TTL_NOTCHANGE: Literal[{"description": "The multicast TTL is not changed", "help": "The multicast TTL is not changed.", "label": "Enable", "name": "enable"}, {"description": "The multicast TTL may be changed", "help": "The multicast TTL may be changed.", "label": "Disable", "name": "disable"}]
VALID_BODY_MULTICAST_SKIP_POLICY: Literal[{"description": "Allowing multicast traffic through the FortiGate without creating a multicast firewall policy", "help": "Allowing multicast traffic through the FortiGate without creating a multicast firewall policy.", "label": "Enable", "name": "enable"}, {"description": "Require a multicast policy to allow multicast traffic to pass through the FortiGate", "help": "Require a multicast policy to allow multicast traffic to pass through the FortiGate.", "label": "Disable", "name": "disable"}]
VALID_BODY_ALLOW_SUBNET_OVERLAP: Literal[{"description": "Enable overlapping subnets", "help": "Enable overlapping subnets.", "label": "Enable", "name": "enable"}, {"description": "Disable overlapping subnets", "help": "Disable overlapping subnets.", "label": "Disable", "name": "disable"}]
VALID_BODY_DENY_TCP_WITH_ICMP: Literal[{"description": "Deny TCP with ICMP", "help": "Deny TCP with ICMP.", "label": "Enable", "name": "enable"}, {"description": "Disable denying TCP with ICMP", "help": "Disable denying TCP with ICMP.", "label": "Disable", "name": "disable"}]
VALID_BODY_EMAIL_PORTAL_CHECK_DNS: Literal[{"description": "Disable email address checking with DNS", "help": "Disable email address checking with DNS.", "label": "Disable", "name": "disable"}, {"description": "Enable email address checking with DNS", "help": "Enable email address checking with DNS.", "label": "Enable", "name": "enable"}]
VALID_BODY_DEFAULT_VOIP_ALG_MODE: Literal[{"description": "Use a default proxy-based VoIP ALG", "help": "Use a default proxy-based VoIP ALG.", "label": "Proxy Based", "name": "proxy-based"}, {"description": "Use the SIP session helper", "help": "Use the SIP session helper.", "label": "Kernel Helper Based", "name": "kernel-helper-based"}]
VALID_BODY_GUI_ICAP: Literal[{"description": "Enable ICAP on the GUI", "help": "Enable ICAP on the GUI.", "label": "Enable", "name": "enable"}, {"description": "Disable ICAP on the GUI", "help": "Disable ICAP on the GUI.", "label": "Disable", "name": "disable"}]
VALID_BODY_GUI_IMPLICIT_POLICY: Literal[{"description": "Enable implicit firewall policies on the GUI", "help": "Enable implicit firewall policies on the GUI.", "label": "Enable", "name": "enable"}, {"description": "Disable implicit firewall policies on the GUI", "help": "Disable implicit firewall policies on the GUI.", "label": "Disable", "name": "disable"}]
VALID_BODY_GUI_DNS_DATABASE: Literal[{"description": "Enable DNS database settings on the GUI", "help": "Enable DNS database settings on the GUI.", "label": "Enable", "name": "enable"}, {"description": "Disable DNS database settings on the GUI", "help": "Disable DNS database settings on the GUI.", "label": "Disable", "name": "disable"}]
VALID_BODY_GUI_LOAD_BALANCE: Literal[{"description": "Enable server load balancing on the GUI", "help": "Enable server load balancing on the GUI.", "label": "Enable", "name": "enable"}, {"description": "Disable server load balancing on the GUI", "help": "Disable server load balancing on the GUI.", "label": "Disable", "name": "disable"}]
VALID_BODY_GUI_MULTICAST_POLICY: Literal[{"description": "Enable multicast firewall policies on the GUI", "help": "Enable multicast firewall policies on the GUI.", "label": "Enable", "name": "enable"}, {"description": "Disable multicast firewall policies on the GUI", "help": "Disable multicast firewall policies on the GUI.", "label": "Disable", "name": "disable"}]
VALID_BODY_GUI_DOS_POLICY: Literal[{"description": "Enable DoS policies on the GUI", "help": "Enable DoS policies on the GUI.", "label": "Enable", "name": "enable"}, {"description": "Disable DoS policies on the GUI", "help": "Disable DoS policies on the GUI.", "label": "Disable", "name": "disable"}]
VALID_BODY_GUI_OBJECT_COLORS: Literal[{"description": "Enable object colors on the GUI", "help": "Enable object colors on the GUI.", "label": "Enable", "name": "enable"}, {"description": "Disable object colors on the GUI", "help": "Disable object colors on the GUI.", "label": "Disable", "name": "disable"}]
VALID_BODY_GUI_ROUTE_TAG_ADDRESS_CREATION: Literal[{"description": "Enable route-tag addresses on the GUI", "help": "Enable route-tag addresses on the GUI.", "label": "Enable", "name": "enable"}, {"description": "Disable route-tag addresses on the GUI", "help": "Disable route-tag addresses on the GUI.", "label": "Disable", "name": "disable"}]
VALID_BODY_GUI_VOIP_PROFILE: Literal[{"description": "Enable VoIP profiles on the GUI", "help": "Enable VoIP profiles on the GUI.", "label": "Enable", "name": "enable"}, {"description": "Disable VoIP profiles on the GUI", "help": "Disable VoIP profiles on the GUI.", "label": "Disable", "name": "disable"}]
VALID_BODY_GUI_AP_PROFILE: Literal[{"description": "Enable FortiAP profiles on the GUI", "help": "Enable FortiAP profiles on the GUI.", "label": "Enable", "name": "enable"}, {"description": "Disable FortiAP profiles on the GUI", "help": "Disable FortiAP profiles on the GUI.", "label": "Disable", "name": "disable"}]
VALID_BODY_GUI_SECURITY_PROFILE_GROUP: Literal[{"description": "Enable Security Profile Groups on the GUI", "help": "Enable Security Profile Groups on the GUI.", "label": "Enable", "name": "enable"}, {"description": "Disable Security Profile Groups on the GUI", "help": "Disable Security Profile Groups on the GUI.", "label": "Disable", "name": "disable"}]
VALID_BODY_GUI_LOCAL_IN_POLICY: Literal[{"description": "Enable Local-In policies on the GUI", "help": "Enable Local-In policies on the GUI.", "label": "Enable", "name": "enable"}, {"description": "Disable Local-In policies on the GUI", "help": "Disable Local-In policies on the GUI.", "label": "Disable", "name": "disable"}]
VALID_BODY_GUI_WANOPT_CACHE: Literal[{"help": "Enable WAN Optimization and Web Caching on the GUI.", "label": "Enable", "name": "enable"}, {"help": "Disable WAN Optimization and Web Caching on the GUI.", "label": "Disable", "name": "disable"}]
VALID_BODY_GUI_EXPLICIT_PROXY: Literal[{"description": "Enable the explicit proxy on the GUI", "help": "Enable the explicit proxy on the GUI.", "label": "Enable", "name": "enable"}, {"description": "Disable the explicit proxy on the GUI", "help": "Disable the explicit proxy on the GUI.", "label": "Disable", "name": "disable"}]
VALID_BODY_GUI_DYNAMIC_ROUTING: Literal[{"description": "Enable dynamic routing on the GUI", "help": "Enable dynamic routing on the GUI.", "label": "Enable", "name": "enable"}, {"description": "Disable dynamic routing on the GUI", "help": "Disable dynamic routing on the GUI.", "label": "Disable", "name": "disable"}]
VALID_BODY_GUI_SSLVPN_PERSONAL_BOOKMARKS: Literal[{"help": "Enable SSL-VPN personal bookmark management on the GUI.", "label": "Enable", "name": "enable"}, {"help": "Disable SSL-VPN personal bookmark management on the GUI.", "label": "Disable", "name": "disable"}]
VALID_BODY_GUI_SSLVPN_REALMS: Literal[{"help": "Enable SSL-VPN realms on the GUI.", "label": "Enable", "name": "enable"}, {"help": "Disable SSL-VPN realms on the GUI.", "label": "Disable", "name": "disable"}]
VALID_BODY_GUI_POLICY_BASED_IPSEC: Literal[{"description": "Enable policy-based IPsec VPN on the GUI", "help": "Enable policy-based IPsec VPN on the GUI.", "label": "Enable", "name": "enable"}, {"description": "Disable policy-based IPsec VPN on the GUI", "help": "Disable policy-based IPsec VPN on the GUI.", "label": "Disable", "name": "disable"}]
VALID_BODY_GUI_THREAT_WEIGHT: Literal[{"description": "Enable threat weight on the GUI", "help": "Enable threat weight on the GUI.", "label": "Enable", "name": "enable"}, {"description": "Disable threat weight on the GUI", "help": "Disable threat weight on the GUI.", "label": "Disable", "name": "disable"}]
VALID_BODY_GUI_SPAMFILTER: Literal[{"description": "Enable Antispam on the GUI", "help": "Enable Antispam on the GUI.", "label": "Enable", "name": "enable"}, {"description": "Disable Antispam on the GUI", "help": "Disable Antispam on the GUI.", "label": "Disable", "name": "disable"}]
VALID_BODY_GUI_FILE_FILTER: Literal[{"description": "Enable File-filter on the GUI", "help": "Enable File-filter on the GUI.", "label": "Enable", "name": "enable"}, {"description": "Disable File-filter on the GUI", "help": "Disable File-filter on the GUI.", "label": "Disable", "name": "disable"}]
VALID_BODY_GUI_APPLICATION_CONTROL: Literal[{"description": "Enable application control on the GUI", "help": "Enable application control on the GUI.", "label": "Enable", "name": "enable"}, {"description": "Disable application control on the GUI", "help": "Disable application control on the GUI.", "label": "Disable", "name": "disable"}]
VALID_BODY_GUI_IPS: Literal[{"description": "Enable IPS on the GUI", "help": "Enable IPS on the GUI.", "label": "Enable", "name": "enable"}, {"description": "Disable IPS on the GUI", "help": "Disable IPS on the GUI.", "label": "Disable", "name": "disable"}]
VALID_BODY_GUI_DHCP_ADVANCED: Literal[{"description": "Enable advanced DHCP options on the GUI", "help": "Enable advanced DHCP options on the GUI.", "label": "Enable", "name": "enable"}, {"description": "Disable advanced DHCP options on the GUI", "help": "Disable advanced DHCP options on the GUI.", "label": "Disable", "name": "disable"}]
VALID_BODY_GUI_VPN: Literal[{"description": "Enable IPsec VPN settings pages on the GUI", "help": "Enable IPsec VPN settings pages on the GUI.", "label": "Enable", "name": "enable"}, {"description": "Disable IPsec VPN settings pages on the GUI", "help": "Disable IPsec VPN settings pages on the GUI.", "label": "Disable", "name": "disable"}]
VALID_BODY_GUI_SSLVPN: Literal[{"help": "Enable SSL-VPN settings pages on the GUI.", "label": "Enable", "name": "enable"}, {"help": "Disable SSL-VPN settings pages on the GUI.", "label": "Disable", "name": "disable"}]
VALID_BODY_GUI_WIRELESS_CONTROLLER: Literal[{"description": "Enable the wireless controller on the GUI", "help": "Enable the wireless controller on the GUI.", "label": "Enable", "name": "enable"}, {"description": "Disable the wireless controller on the GUI", "help": "Disable the wireless controller on the GUI.", "label": "Disable", "name": "disable"}]
VALID_BODY_GUI_ADVANCED_WIRELESS_FEATURES: Literal[{"description": "Enable advanced wireless features in GUI", "help": "Enable advanced wireless features in GUI.", "label": "Enable", "name": "enable"}, {"description": "Disable advanced wireless features in GUI", "help": "Disable advanced wireless features in GUI.", "label": "Disable", "name": "disable"}]
VALID_BODY_GUI_SWITCH_CONTROLLER: Literal[{"description": "Enable the switch controller on the GUI", "help": "Enable the switch controller on the GUI.", "label": "Enable", "name": "enable"}, {"description": "Disable the switch controller on the GUI", "help": "Disable the switch controller on the GUI.", "label": "Disable", "name": "disable"}]
VALID_BODY_GUI_FORTIAP_SPLIT_TUNNELING: Literal[{"description": "Enable FortiAP split tunneling on the GUI", "help": "Enable FortiAP split tunneling on the GUI.", "label": "Enable", "name": "enable"}, {"description": "Disable FortiAP split tunneling on the GUI", "help": "Disable FortiAP split tunneling on the GUI.", "label": "Disable", "name": "disable"}]
VALID_BODY_GUI_WEBFILTER_ADVANCED: Literal[{"description": "Enable advanced web filtering on the GUI", "help": "Enable advanced web filtering on the GUI.", "label": "Enable", "name": "enable"}, {"description": "Disable advanced web filtering on the GUI", "help": "Disable advanced web filtering on the GUI.", "label": "Disable", "name": "disable"}]
VALID_BODY_GUI_TRAFFIC_SHAPING: Literal[{"description": "Enable traffic shaping on the GUI", "help": "Enable traffic shaping on the GUI.", "label": "Enable", "name": "enable"}, {"description": "Disable traffic shaping on the GUI", "help": "Disable traffic shaping on the GUI.", "label": "Disable", "name": "disable"}]
VALID_BODY_GUI_WAN_LOAD_BALANCING: Literal[{"description": "Enable SD-WAN on the GUI", "help": "Enable SD-WAN on the GUI.", "label": "Enable", "name": "enable"}, {"description": "Disable SD-WAN on the GUI", "help": "Disable SD-WAN on the GUI.", "label": "Disable", "name": "disable"}]
VALID_BODY_GUI_ANTIVIRUS: Literal[{"description": "Enable AntiVirus on the GUI", "help": "Enable AntiVirus on the GUI.", "label": "Enable", "name": "enable"}, {"description": "Disable AntiVirus on the GUI", "help": "Disable AntiVirus on the GUI.", "label": "Disable", "name": "disable"}]
VALID_BODY_GUI_WEBFILTER: Literal[{"description": "Enable Web filtering on the GUI", "help": "Enable Web filtering on the GUI.", "label": "Enable", "name": "enable"}, {"description": "Disable Web filtering on the GUI", "help": "Disable Web filtering on the GUI.", "label": "Disable", "name": "disable"}]
VALID_BODY_GUI_VIDEOFILTER: Literal[{"description": "Enable Video filtering on the GUI", "help": "Enable Video filtering on the GUI.", "label": "Enable", "name": "enable"}, {"description": "Disable Video filtering on the GUI", "help": "Disable Video filtering on the GUI.", "label": "Disable", "name": "disable"}]
VALID_BODY_GUI_DNSFILTER: Literal[{"description": "Enable DNS Filtering on the GUI", "help": "Enable DNS Filtering on the GUI.", "label": "Enable", "name": "enable"}, {"description": "Disable DNS Filtering on the GUI", "help": "Disable DNS Filtering on the GUI.", "label": "Disable", "name": "disable"}]
VALID_BODY_GUI_WAF_PROFILE: Literal[{"description": "Enable Web Application Firewall on the GUI", "help": "Enable Web Application Firewall on the GUI.", "label": "Enable", "name": "enable"}, {"description": "Disable Web Application Firewall on the GUI", "help": "Disable Web Application Firewall on the GUI.", "label": "Disable", "name": "disable"}]
VALID_BODY_GUI_DLP_PROFILE: Literal[{"description": "Enable Data Loss Prevention on the GUI", "help": "Enable Data Loss Prevention on the GUI.", "label": "Enable", "name": "enable"}, {"description": "Disable Data Loss Prevention on the GUI", "help": "Disable Data Loss Prevention on the GUI.", "label": "Disable", "name": "disable"}]
VALID_BODY_GUI_DLP_ADVANCED: Literal[{"description": "Enable Show advanced DLP expressions on the GUI", "help": "Enable Show advanced DLP expressions on the GUI.", "label": "Enable", "name": "enable"}, {"description": "Disable Show advanced DLP expressions on the GUI", "help": "Disable Show advanced DLP expressions on the GUI.", "label": "Disable", "name": "disable"}]
VALID_BODY_GUI_VIRTUAL_PATCH_PROFILE: Literal[{"description": "Enable Virtual Patching on the GUI", "help": "Enable Virtual Patching on the GUI.", "label": "Enable", "name": "enable"}, {"description": "Disable Virtual Patching on the GUI", "help": "Disable Virtual Patching on the GUI.", "label": "Disable", "name": "disable"}]
VALID_BODY_GUI_CASB: Literal[{"description": "Enable Inline-CASB on the GUI", "help": "Enable Inline-CASB on the GUI.", "label": "Enable", "name": "enable"}, {"description": "Disable Inline-CASB on the GUI", "help": "Disable Inline-CASB on the GUI.", "label": "Disable", "name": "disable"}]
VALID_BODY_GUI_FORTIEXTENDER_CONTROLLER: Literal[{"description": "Enable FortiExtender on the GUI", "help": "Enable FortiExtender on the GUI.", "label": "Enable", "name": "enable"}, {"description": "Disable FortiExtender on the GUI", "help": "Disable FortiExtender on the GUI.", "label": "Disable", "name": "disable"}]
VALID_BODY_GUI_ADVANCED_POLICY: Literal[{"description": "Enable advanced policy configuration on the GUI", "help": "Enable advanced policy configuration on the GUI.", "label": "Enable", "name": "enable"}, {"description": "Disable advanced policy configuration on the GUI", "help": "Disable advanced policy configuration on the GUI.", "label": "Disable", "name": "disable"}]
VALID_BODY_GUI_ALLOW_UNNAMED_POLICY: Literal[{"description": "Enable the requirement for policy naming on the GUI", "help": "Enable the requirement for policy naming on the GUI.", "label": "Enable", "name": "enable"}, {"description": "Disable the requirement for policy naming on the GUI", "help": "Disable the requirement for policy naming on the GUI.", "label": "Disable", "name": "disable"}]
VALID_BODY_GUI_EMAIL_COLLECTION: Literal[{"description": "Enable email collection on the GUI", "help": "Enable email collection on the GUI.", "label": "Enable", "name": "enable"}, {"description": "Disable email collection on the GUI", "help": "Disable email collection on the GUI.", "label": "Disable", "name": "disable"}]
VALID_BODY_GUI_MULTIPLE_INTERFACE_POLICY: Literal[{"description": "Enable adding multiple interfaces to a policy on the GUI", "help": "Enable adding multiple interfaces to a policy on the GUI.", "label": "Enable", "name": "enable"}, {"description": "Disable adding multiple interfaces to a policy on the GUI", "help": "Disable adding multiple interfaces to a policy on the GUI.", "label": "Disable", "name": "disable"}]
VALID_BODY_GUI_POLICY_DISCLAIMER: Literal[{"description": "Enable policy disclaimer on the GUI", "help": "Enable policy disclaimer on the GUI.", "label": "Enable", "name": "enable"}, {"description": "Disable policy disclaimer on the GUI", "help": "Disable policy disclaimer on the GUI.", "label": "Disable", "name": "disable"}]
VALID_BODY_GUI_ZTNA: Literal[{"description": "Enable Zero Trust Network Access features on the GUI", "help": "Enable Zero Trust Network Access features on the GUI.", "label": "Enable", "name": "enable"}, {"description": "Disable Zero Trust Network Access features on the GUI", "help": "Disable Zero Trust Network Access features on the GUI.", "label": "Disable", "name": "disable"}]
VALID_BODY_GUI_OT: Literal[{"description": "Enable Operational technology features on the GUI", "help": "Enable Operational technology features on the GUI.", "label": "Enable", "name": "enable"}, {"description": "Disable Operational technology features on the GUI", "help": "Disable Operational technology features on the GUI.", "label": "Disable", "name": "disable"}]
VALID_BODY_GUI_DYNAMIC_DEVICE_OS_ID: Literal[{"description": "Enable Create dynamic addresses to manage known devices", "help": "Enable Create dynamic addresses to manage known devices.", "label": "Enable", "name": "enable"}, {"description": "Disable Create dynamic addresses to manage known devices", "help": "Disable Create dynamic addresses to manage known devices.", "label": "Disable", "name": "disable"}]
VALID_BODY_GUI_GTP: Literal[{"help": "Enable Manage general radio packet service (GPRS) protocols on the GUI.", "label": "Enable", "name": "enable"}, {"help": "Disable Manage general radio packet service (GPRS) protocols on the GUI.", "label": "Disable", "name": "disable"}]
VALID_BODY_IKE_SESSION_RESUME: Literal[{"description": "Enable IKEv2 session resumption (RFC 5723)", "help": "Enable IKEv2 session resumption (RFC 5723).", "label": "Enable", "name": "enable"}, {"description": "Disable IKEv2 session resumption (RFC 5723)", "help": "Disable IKEv2 session resumption (RFC 5723).", "label": "Disable", "name": "disable"}]
VALID_BODY_IKE_QUICK_CRASH_DETECT: Literal[{"description": "Enable IKE quick crash detection (RFC 6290)", "help": "Enable IKE quick crash detection (RFC 6290).", "label": "Enable", "name": "enable"}, {"description": "Disable IKE quick crash detection (RFC 6290)", "help": "Disable IKE quick crash detection (RFC 6290).", "label": "Disable", "name": "disable"}]
VALID_BODY_IKE_DN_FORMAT: Literal[{"description": "Format IKE ASN", "help": "Format IKE ASN.1 Distinguished Names with spaces between attribute names and values.", "label": "With Space", "name": "with-space"}, {"description": "Format IKE ASN", "help": "Format IKE ASN.1 Distinguished Names without spaces between attribute names and values.", "label": "No Space", "name": "no-space"}]
VALID_BODY_IKE_POLICY_ROUTE: Literal[{"description": "Enable IKE Policy Based Routing (PBR)", "help": "Enable IKE Policy Based Routing (PBR).", "label": "Enable", "name": "enable"}, {"description": "Disable IKE Policy Based Routing (PBR)", "help": "Disable IKE Policy Based Routing (PBR).", "label": "Disable", "name": "disable"}]
VALID_BODY_IKE_DETAILED_EVENT_LOGS: Literal[{"description": "Generate brief log for IKE events", "help": "Generate brief log for IKE events.", "label": "Disable", "name": "disable"}, {"description": "Generate detail log for IKE events", "help": "Generate detail log for IKE events.", "label": "Enable", "name": "enable"}]
VALID_BODY_BLOCK_LAND_ATTACK: Literal[{"description": "Do not block land attack", "help": "Do not block land attack.", "label": "Disable", "name": "disable"}, {"description": "Block land attack", "help": "Block land attack.", "label": "Enable", "name": "enable"}]
VALID_BODY_DEFAULT_APP_PORT_AS_SERVICE: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]
VALID_BODY_FQDN_SESSION_CHECK: Literal[{"description": "Enable dirty session check caused by FQDN updates", "help": "Enable dirty session check caused by FQDN updates.", "label": "Enable", "name": "enable"}, {"description": "Disable dirty session check caused by FQDN updates", "help": "Disable dirty session check caused by FQDN updates.", "label": "Disable", "name": "disable"}]
VALID_BODY_EXT_RESOURCE_SESSION_CHECK: Literal[{"description": "Enable dirty session check caused by external resource updates", "help": "Enable dirty session check caused by external resource updates.", "label": "Enable", "name": "enable"}, {"description": "Disable dirty session check caused by external resource updates", "help": "Disable dirty session check caused by external resource updates.", "label": "Disable", "name": "disable"}]
VALID_BODY_DYN_ADDR_SESSION_CHECK: Literal[{"description": "Enable dirty session check caused by dynamic address updates", "help": "Enable dirty session check caused by dynamic address updates.", "label": "Enable", "name": "enable"}, {"description": "Disable dirty session check caused by dynamic address updates", "help": "Disable dirty session check caused by dynamic address updates.", "label": "Disable", "name": "disable"}]
VALID_BODY_GUI_ENFORCE_CHANGE_SUMMARY: Literal[{"description": "No change summary requirement", "help": "No change summary requirement.", "label": "Disable", "name": "disable"}, {"description": "Change summary required", "help": "Change summary required.", "label": "Require", "name": "require"}, {"description": "Change summary optional", "help": "Change summary optional.", "label": "Optional", "name": "optional"}]
VALID_BODY_INTERNET_SERVICE_DATABASE_CACHE: Literal[{"description": "Disable Internet Service database caching", "help": "Disable Internet Service database caching.", "label": "Disable", "name": "disable"}, {"description": "Enable Internet Service database caching", "help": "Enable Internet Service database caching.", "label": "Enable", "name": "enable"}]

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
    "VALID_BODY_VDOM_TYPE",
    "VALID_BODY_OPMODE",
    "VALID_BODY_NGFW_MODE",
    "VALID_BODY_HTTP_EXTERNAL_DEST",
    "VALID_BODY_FIREWALL_SESSION_DIRTY",
    "VALID_BODY_BFD",
    "VALID_BODY_BFD_DONT_ENFORCE_SRC_PORT",
    "VALID_BODY_UTF8_SPAM_TAGGING",
    "VALID_BODY_WCCP_CACHE_ENGINE",
    "VALID_BODY_VPN_STATS_LOG",
    "VALID_BODY_V4_ECMP_MODE",
    "VALID_BODY_FW_SESSION_HAIRPIN",
    "VALID_BODY_PRP_TRAILER_ACTION",
    "VALID_BODY_SNAT_HAIRPIN_TRAFFIC",
    "VALID_BODY_DHCP_PROXY",
    "VALID_BODY_DHCP_PROXY_INTERFACE_SELECT_METHOD",
    "VALID_BODY_CENTRAL_NAT",
    "VALID_BODY_LLDP_RECEPTION",
    "VALID_BODY_LLDP_TRANSMISSION",
    "VALID_BODY_LINK_DOWN_ACCESS",
    "VALID_BODY_NAT46_GENERATE_IPV6_FRAGMENT_HEADER",
    "VALID_BODY_NAT46_FORCE_IPV4_PACKET_FORWARDING",
    "VALID_BODY_NAT64_FORCE_IPV6_PACKET_FORWARDING",
    "VALID_BODY_DETECT_UNKNOWN_ESP",
    "VALID_BODY_INTREE_SES_BEST_ROUTE",
    "VALID_BODY_AUXILIARY_SESSION",
    "VALID_BODY_ASYMROUTE",
    "VALID_BODY_ASYMROUTE_ICMP",
    "VALID_BODY_TCP_SESSION_WITHOUT_SYN",
    "VALID_BODY_SES_DENIED_TRAFFIC",
    "VALID_BODY_SES_DENIED_MULTICAST_TRAFFIC",
    "VALID_BODY_STRICT_SRC_CHECK",
    "VALID_BODY_ALLOW_LINKDOWN_PATH",
    "VALID_BODY_ASYMROUTE6",
    "VALID_BODY_ASYMROUTE6_ICMP",
    "VALID_BODY_SCTP_SESSION_WITHOUT_INIT",
    "VALID_BODY_SIP_EXPECTATION",
    "VALID_BODY_SIP_NAT_TRACE",
    "VALID_BODY_H323_DIRECT_MODEL",
    "VALID_BODY_STATUS",
    "VALID_BODY_MULTICAST_FORWARD",
    "VALID_BODY_MULTICAST_TTL_NOTCHANGE",
    "VALID_BODY_MULTICAST_SKIP_POLICY",
    "VALID_BODY_ALLOW_SUBNET_OVERLAP",
    "VALID_BODY_DENY_TCP_WITH_ICMP",
    "VALID_BODY_EMAIL_PORTAL_CHECK_DNS",
    "VALID_BODY_DEFAULT_VOIP_ALG_MODE",
    "VALID_BODY_GUI_ICAP",
    "VALID_BODY_GUI_IMPLICIT_POLICY",
    "VALID_BODY_GUI_DNS_DATABASE",
    "VALID_BODY_GUI_LOAD_BALANCE",
    "VALID_BODY_GUI_MULTICAST_POLICY",
    "VALID_BODY_GUI_DOS_POLICY",
    "VALID_BODY_GUI_OBJECT_COLORS",
    "VALID_BODY_GUI_ROUTE_TAG_ADDRESS_CREATION",
    "VALID_BODY_GUI_VOIP_PROFILE",
    "VALID_BODY_GUI_AP_PROFILE",
    "VALID_BODY_GUI_SECURITY_PROFILE_GROUP",
    "VALID_BODY_GUI_LOCAL_IN_POLICY",
    "VALID_BODY_GUI_WANOPT_CACHE",
    "VALID_BODY_GUI_EXPLICIT_PROXY",
    "VALID_BODY_GUI_DYNAMIC_ROUTING",
    "VALID_BODY_GUI_SSLVPN_PERSONAL_BOOKMARKS",
    "VALID_BODY_GUI_SSLVPN_REALMS",
    "VALID_BODY_GUI_POLICY_BASED_IPSEC",
    "VALID_BODY_GUI_THREAT_WEIGHT",
    "VALID_BODY_GUI_SPAMFILTER",
    "VALID_BODY_GUI_FILE_FILTER",
    "VALID_BODY_GUI_APPLICATION_CONTROL",
    "VALID_BODY_GUI_IPS",
    "VALID_BODY_GUI_DHCP_ADVANCED",
    "VALID_BODY_GUI_VPN",
    "VALID_BODY_GUI_SSLVPN",
    "VALID_BODY_GUI_WIRELESS_CONTROLLER",
    "VALID_BODY_GUI_ADVANCED_WIRELESS_FEATURES",
    "VALID_BODY_GUI_SWITCH_CONTROLLER",
    "VALID_BODY_GUI_FORTIAP_SPLIT_TUNNELING",
    "VALID_BODY_GUI_WEBFILTER_ADVANCED",
    "VALID_BODY_GUI_TRAFFIC_SHAPING",
    "VALID_BODY_GUI_WAN_LOAD_BALANCING",
    "VALID_BODY_GUI_ANTIVIRUS",
    "VALID_BODY_GUI_WEBFILTER",
    "VALID_BODY_GUI_VIDEOFILTER",
    "VALID_BODY_GUI_DNSFILTER",
    "VALID_BODY_GUI_WAF_PROFILE",
    "VALID_BODY_GUI_DLP_PROFILE",
    "VALID_BODY_GUI_DLP_ADVANCED",
    "VALID_BODY_GUI_VIRTUAL_PATCH_PROFILE",
    "VALID_BODY_GUI_CASB",
    "VALID_BODY_GUI_FORTIEXTENDER_CONTROLLER",
    "VALID_BODY_GUI_ADVANCED_POLICY",
    "VALID_BODY_GUI_ALLOW_UNNAMED_POLICY",
    "VALID_BODY_GUI_EMAIL_COLLECTION",
    "VALID_BODY_GUI_MULTIPLE_INTERFACE_POLICY",
    "VALID_BODY_GUI_POLICY_DISCLAIMER",
    "VALID_BODY_GUI_ZTNA",
    "VALID_BODY_GUI_OT",
    "VALID_BODY_GUI_DYNAMIC_DEVICE_OS_ID",
    "VALID_BODY_GUI_GTP",
    "VALID_BODY_IKE_SESSION_RESUME",
    "VALID_BODY_IKE_QUICK_CRASH_DETECT",
    "VALID_BODY_IKE_DN_FORMAT",
    "VALID_BODY_IKE_POLICY_ROUTE",
    "VALID_BODY_IKE_DETAILED_EVENT_LOGS",
    "VALID_BODY_BLOCK_LAND_ATTACK",
    "VALID_BODY_DEFAULT_APP_PORT_AS_SERVICE",
    "VALID_BODY_FQDN_SESSION_CHECK",
    "VALID_BODY_EXT_RESOURCE_SESSION_CHECK",
    "VALID_BODY_DYN_ADDR_SESSION_CHECK",
    "VALID_BODY_GUI_ENFORCE_CHANGE_SUMMARY",
    "VALID_BODY_INTERNET_SERVICE_DATABASE_CACHE",
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