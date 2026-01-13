from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_OBJECT: Literal[{"help": "log.fortianalyzer.setting", "label": "Log.Fortianalyzer.Setting", "name": "log.fortianalyzer.setting"}, {"help": "log.fortianalyzer.override-setting", "label": "Log.Fortianalyzer.Override Setting", "name": "log.fortianalyzer.override-setting"}, {"help": "log.fortianalyzer2.setting", "label": "Log.Fortianalyzer2.Setting", "name": "log.fortianalyzer2.setting"}, {"help": "log.fortianalyzer2.override-setting", "label": "Log.Fortianalyzer2.Override Setting", "name": "log.fortianalyzer2.override-setting"}, {"help": "log.fortianalyzer3.setting", "label": "Log.Fortianalyzer3.Setting", "name": "log.fortianalyzer3.setting"}, {"help": "log.fortianalyzer3.override-setting", "label": "Log.Fortianalyzer3.Override Setting", "name": "log.fortianalyzer3.override-setting"}, {"help": "log.fortianalyzer-cloud.setting", "label": "Log.Fortianalyzer Cloud.Setting", "name": "log.fortianalyzer-cloud.setting"}, {"help": "log.fortianalyzer-cloud.override-setting", "label": "Log.Fortianalyzer Cloud.Override Setting", "name": "log.fortianalyzer-cloud.override-setting"}, {"help": "log.syslogd.setting", "label": "Log.Syslogd.Setting", "name": "log.syslogd.setting"}, {"help": "log.syslogd.override-setting", "label": "Log.Syslogd.Override Setting", "name": "log.syslogd.override-setting"}, {"help": "log.syslogd2.setting", "label": "Log.Syslogd2.Setting", "name": "log.syslogd2.setting"}, {"help": "log.syslogd2.override-setting", "label": "Log.Syslogd2.Override Setting", "name": "log.syslogd2.override-setting"}, {"help": "log.syslogd3.setting", "label": "Log.Syslogd3.Setting", "name": "log.syslogd3.setting"}, {"help": "log.syslogd3.override-setting", "label": "Log.Syslogd3.Override Setting", "name": "log.syslogd3.override-setting"}, {"help": "log.syslogd4.setting", "label": "Log.Syslogd4.Setting", "name": "log.syslogd4.setting"}, {"help": "log.syslogd4.override-setting", "label": "Log.Syslogd4.Override Setting", "name": "log.syslogd4.override-setting"}, {"help": "system.gre-tunnel", "label": "System.Gre Tunnel", "name": "system.gre-tunnel"}, {"help": "system.central-management", "label": "System.Central Management", "name": "system.central-management"}, {"help": "system.csf", "label": "System.Csf", "name": "system.csf"}, {"help": "user.radius", "label": "User.Radius", "name": "user.radius"}, {"help": "system.interface", "label": "System.Interface", "name": "system.interface"}, {"help": "vpn.ipsec.phase1-interface", "label": "Vpn.Ipsec.Phase1 Interface", "name": "vpn.ipsec.phase1-interface"}, {"help": "vpn.ipsec.phase2-interface", "label": "Vpn.Ipsec.Phase2 Interface", "name": "vpn.ipsec.phase2-interface"}, {"help": "router.bgp", "label": "Router.Bgp", "name": "router.bgp"}, {"help": "router.route-map", "label": "Router.Route Map", "name": "router.route-map"}, {"help": "router.prefix-list", "label": "Router.Prefix List", "name": "router.prefix-list"}, {"help": "firewall.ippool", "label": "Firewall.Ippool", "name": "firewall.ippool"}, {"help": "firewall.ippool6", "label": "Firewall.Ippool6", "name": "firewall.ippool6"}, {"help": "router.static", "label": "Router.Static", "name": "router.static"}, {"help": "router.static6", "label": "Router.Static6", "name": "router.static6"}, {"help": "firewall.vip", "label": "Firewall.Vip", "name": "firewall.vip"}, {"help": "firewall.vip6", "label": "Firewall.Vip6", "name": "firewall.vip6"}, {"help": "system.sdwan", "label": "System.Sdwan", "name": "system.sdwan"}, {"help": "system.saml", "label": "System.Saml", "name": "system.saml"}, {"help": "router.policy", "label": "Router.Policy", "name": "router.policy"}, {"help": "router.policy6", "label": "Router.Policy6", "name": "router.policy6"}, {"help": "log.syslogd.setting", "label": "Log.Syslogd.Setting", "name": "log.syslogd.setting"}, {"help": "log.syslogd.override-setting", "label": "Log.Syslogd.Override Setting", "name": "log.syslogd.override-setting"}, {"help": "firewall.address", "label": "Firewall.Address", "name": "firewall.address"}]
VALID_BODY_SCOPE: Literal[{"description": "Object configuration independent for all VDOMs", "help": "Object configuration independent for all VDOMs.", "label": "All", "name": "all"}, {"description": "Object configuration independent for the listed VDOMs", "help": "Object configuration independent for the listed VDOMs. Other VDOMs use the global configuration.", "label": "Inclusive", "name": "inclusive"}, {"description": "Use the global object configuration for the listed VDOMs", "help": "Use the global object configuration for the listed VDOMs. Other VDOMs can be configured independently.", "label": "Exclusive", "name": "exclusive"}]

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
    "VALID_BODY_OBJECT",
    "VALID_BODY_SCOPE",
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