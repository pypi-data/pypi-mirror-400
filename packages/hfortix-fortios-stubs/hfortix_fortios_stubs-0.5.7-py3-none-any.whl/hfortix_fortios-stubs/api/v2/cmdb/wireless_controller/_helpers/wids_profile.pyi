from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_SENSOR_MODE: Literal[{"description": "Disable the scan", "help": "Disable the scan.", "label": "Disable", "name": "disable"}, {"description": "Enable the scan and monitor foreign channels", "help": "Enable the scan and monitor foreign channels. Foreign channels are all other available channels than the current operating channel.", "label": "Foreign", "name": "foreign"}, {"description": "Enable the scan and monitor both foreign and home channels", "help": "Enable the scan and monitor both foreign and home channels. Select this option to monitor all WiFi channels.", "label": "Both", "name": "both"}]
VALID_BODY_AP_SCAN: Literal[{"description": "Disable rogue AP detection", "help": "Disable rogue AP detection.", "label": "Disable", "name": "disable"}, {"description": "Enable rogue AP detection", "help": "Enable rogue AP detection.", "label": "Enable", "name": "enable"}]
VALID_BODY_AP_SCAN_PASSIVE: Literal[{"description": "Passive scanning on all channels", "help": "Passive scanning on all channels.", "label": "Enable", "name": "enable"}, {"description": "Passive scanning only on DFS channels", "help": "Passive scanning only on DFS channels.", "label": "Disable", "name": "disable"}]
VALID_BODY_AP_AUTO_SUPPRESS: Literal[{"description": "Enable on-wire rogue AP auto-suppression", "help": "Enable on-wire rogue AP auto-suppression.", "label": "Enable", "name": "enable"}, {"description": "Disable on-wire rogue AP auto-suppression", "help": "Disable on-wire rogue AP auto-suppression.", "label": "Disable", "name": "disable"}]
VALID_BODY_WIRELESS_BRIDGE: Literal[{"description": "Enable wireless bridge detection", "help": "Enable wireless bridge detection.", "label": "Enable", "name": "enable"}, {"description": "Disable wireless bridge detection", "help": "Disable wireless bridge detection.", "label": "Disable", "name": "disable"}]
VALID_BODY_DEAUTH_BROADCAST: Literal[{"description": "Enable broadcast de-authentication detection", "help": "Enable broadcast de-authentication detection.", "label": "Enable", "name": "enable"}, {"description": "Disable broadcast de-authentication detection", "help": "Disable broadcast de-authentication detection.", "label": "Disable", "name": "disable"}]
VALID_BODY_NULL_SSID_PROBE_RESP: Literal[{"description": "Enable null SSID probe resp detection", "help": "Enable null SSID probe resp detection.", "label": "Enable", "name": "enable"}, {"description": "Disable null SSID probe resp detection", "help": "Disable null SSID probe resp detection.", "label": "Disable", "name": "disable"}]
VALID_BODY_LONG_DURATION_ATTACK: Literal[{"description": "Enable long duration attack detection", "help": "Enable long duration attack detection.", "label": "Enable", "name": "enable"}, {"description": "Disable long duration attack detection", "help": "Disable long duration attack detection.", "label": "Disable", "name": "disable"}]
VALID_BODY_INVALID_MAC_OUI: Literal[{"description": "Enable invalid MAC OUI detection", "help": "Enable invalid MAC OUI detection.", "label": "Enable", "name": "enable"}, {"description": "Disable invalid MAC OUI detection", "help": "Disable invalid MAC OUI detection.", "label": "Disable", "name": "disable"}]
VALID_BODY_WEAK_WEP_IV: Literal[{"description": "Enable weak WEP IV detection", "help": "Enable weak WEP IV detection.", "label": "Enable", "name": "enable"}, {"description": "Disable weak WEP IV detection", "help": "Disable weak WEP IV detection.", "label": "Disable", "name": "disable"}]
VALID_BODY_AUTH_FRAME_FLOOD: Literal[{"description": "Enable authentication frame flooding detection", "help": "Enable authentication frame flooding detection.", "label": "Enable", "name": "enable"}, {"description": "Disable authentication frame flooding detection", "help": "Disable authentication frame flooding detection.", "label": "Disable", "name": "disable"}]
VALID_BODY_ASSOC_FRAME_FLOOD: Literal[{"description": "Enable association frame flooding detection", "help": "Enable association frame flooding detection.", "label": "Enable", "name": "enable"}, {"description": "Disable association frame flooding detection", "help": "Disable association frame flooding detection.", "label": "Disable", "name": "disable"}]
VALID_BODY_REASSOC_FLOOD: Literal[{"description": "Enable reassociation flood detection", "help": "Enable reassociation flood detection.", "label": "Enable", "name": "enable"}, {"description": "Disable reassociation flood detection", "help": "Disable reassociation flood detection.", "label": "Disable", "name": "disable"}]
VALID_BODY_PROBE_FLOOD: Literal[{"description": "Enable probe flood detection", "help": "Enable probe flood detection.", "label": "Enable", "name": "enable"}, {"description": "Disable probe flood detection", "help": "Disable probe flood detection.", "label": "Disable", "name": "disable"}]
VALID_BODY_BCN_FLOOD: Literal[{"description": "Enable bcn flood detection", "help": "Enable bcn flood detection.", "label": "Enable", "name": "enable"}, {"description": "Disable bcn flood detection", "help": "Disable bcn flood detection.", "label": "Disable", "name": "disable"}]
VALID_BODY_RTS_FLOOD: Literal[{"description": "Enable rts flood detection", "help": "Enable rts flood detection.", "label": "Enable", "name": "enable"}, {"description": "Disable rts flood detection", "help": "Disable rts flood detection.", "label": "Disable", "name": "disable"}]
VALID_BODY_CTS_FLOOD: Literal[{"description": "Enable cts flood detection", "help": "Enable cts flood detection.", "label": "Enable", "name": "enable"}, {"description": "Disable cts flood detection", "help": "Disable cts flood detection.", "label": "Disable", "name": "disable"}]
VALID_BODY_CLIENT_FLOOD: Literal[{"description": "Enable client flood detection", "help": "Enable client flood detection.", "label": "Enable", "name": "enable"}, {"description": "Disable client flood detection", "help": "Disable client flood detection.", "label": "Disable", "name": "disable"}]
VALID_BODY_BLOCK_ACK_FLOOD: Literal[{"description": "Enable block_ack flood detection", "help": "Enable block_ack flood detection.", "label": "Enable", "name": "enable"}, {"description": "Disable block_ack flood detection", "help": "Disable block_ack flood detection.", "label": "Disable", "name": "disable"}]
VALID_BODY_PSPOLL_FLOOD: Literal[{"description": "Enable pspoll flood detection", "help": "Enable pspoll flood detection.", "label": "Enable", "name": "enable"}, {"description": "Disable pspoll flood detection", "help": "Disable pspoll flood detection.", "label": "Disable", "name": "disable"}]
VALID_BODY_NETSTUMBLER: Literal[{"description": "Enable netstumbler detection", "help": "Enable netstumbler detection.", "label": "Enable", "name": "enable"}, {"description": "Disable netstumbler detection", "help": "Disable netstumbler detection.", "label": "Disable", "name": "disable"}]
VALID_BODY_WELLENREITER: Literal[{"description": "Enable wellenreiter detection", "help": "Enable wellenreiter detection.", "label": "Enable", "name": "enable"}, {"description": "Disable wellenreiter detection", "help": "Disable wellenreiter detection.", "label": "Disable", "name": "disable"}]
VALID_BODY_SPOOFED_DEAUTH: Literal[{"description": "Enable spoofed de-authentication attack detection", "help": "Enable spoofed de-authentication attack detection.", "label": "Enable", "name": "enable"}, {"description": "Disable spoofed de-authentication attack detection", "help": "Disable spoofed de-authentication attack detection.", "label": "Disable", "name": "disable"}]
VALID_BODY_ASLEAP_ATTACK: Literal[{"description": "Enable asleap attack detection", "help": "Enable asleap attack detection.", "label": "Enable", "name": "enable"}, {"description": "Disable asleap attack detection", "help": "Disable asleap attack detection.", "label": "Disable", "name": "disable"}]
VALID_BODY_EAPOL_START_FLOOD: Literal[{"description": "Enable EAPOL-Start flooding detection", "help": "Enable EAPOL-Start flooding detection.", "label": "Enable", "name": "enable"}, {"description": "Disable EAPOL-Start flooding detection", "help": "Disable EAPOL-Start flooding detection.", "label": "Disable", "name": "disable"}]
VALID_BODY_EAPOL_LOGOFF_FLOOD: Literal[{"description": "Enable EAPOL-Logoff flooding detection", "help": "Enable EAPOL-Logoff flooding detection.", "label": "Enable", "name": "enable"}, {"description": "Disable EAPOL-Logoff flooding detection", "help": "Disable EAPOL-Logoff flooding detection.", "label": "Disable", "name": "disable"}]
VALID_BODY_EAPOL_SUCC_FLOOD: Literal[{"description": "Enable EAPOL-Success flooding detection", "help": "Enable EAPOL-Success flooding detection.", "label": "Enable", "name": "enable"}, {"description": "Disable EAPOL-Success flooding detection", "help": "Disable EAPOL-Success flooding detection.", "label": "Disable", "name": "disable"}]
VALID_BODY_EAPOL_FAIL_FLOOD: Literal[{"description": "Enable EAPOL-Failure flooding detection", "help": "Enable EAPOL-Failure flooding detection.", "label": "Enable", "name": "enable"}, {"description": "Disable EAPOL-Failure flooding detection", "help": "Disable EAPOL-Failure flooding detection.", "label": "Disable", "name": "disable"}]
VALID_BODY_EAPOL_PRE_SUCC_FLOOD: Literal[{"description": "Enable premature EAPOL-Success flooding detection", "help": "Enable premature EAPOL-Success flooding detection.", "label": "Enable", "name": "enable"}, {"description": "Disable premature EAPOL-Success flooding detection", "help": "Disable premature EAPOL-Success flooding detection.", "label": "Disable", "name": "disable"}]
VALID_BODY_EAPOL_PRE_FAIL_FLOOD: Literal[{"description": "Enable premature EAPOL-Failure flooding detection", "help": "Enable premature EAPOL-Failure flooding detection.", "label": "Enable", "name": "enable"}, {"description": "Disable premature EAPOL-Failure flooding detection", "help": "Disable premature EAPOL-Failure flooding detection.", "label": "Disable", "name": "disable"}]
VALID_BODY_WINDOWS_BRIDGE: Literal[{"description": "Enable windows bridge detection", "help": "Enable windows bridge detection.", "label": "Enable", "name": "enable"}, {"description": "Disable windows bridge detection", "help": "Disable windows bridge detection.", "label": "Disable", "name": "disable"}]
VALID_BODY_DISASSOC_BROADCAST: Literal[{"description": "Enable broadcast dis-association detection", "help": "Enable broadcast dis-association detection.", "label": "Enable", "name": "enable"}, {"description": "Disable broadcast dis-association detection", "help": "Disable broadcast dis-association detection.", "label": "Disable", "name": "disable"}]
VALID_BODY_AP_SPOOFING: Literal[{"description": "Enable AP spoofing detection", "help": "Enable AP spoofing detection.", "label": "Enable", "name": "enable"}, {"description": "Disable AP spoofing detection", "help": "Disable AP spoofing detection.", "label": "Disable", "name": "disable"}]
VALID_BODY_CHAN_BASED_MITM: Literal[{"description": "Enable channel based mitm detection", "help": "Enable channel based mitm detection.", "label": "Enable", "name": "enable"}, {"description": "Disable channel based mitm detection", "help": "Disable channel based mitm detection.", "label": "Disable", "name": "disable"}]
VALID_BODY_ADHOC_VALID_SSID: Literal[{"description": "Enable adhoc using valid SSID detection", "help": "Enable adhoc using valid SSID detection.", "label": "Enable", "name": "enable"}, {"description": "Disable adhoc using valid SSID detection", "help": "Disable adhoc using valid SSID detection.", "label": "Disable", "name": "disable"}]
VALID_BODY_ADHOC_NETWORK: Literal[{"description": "Enable adhoc network detection", "help": "Enable adhoc network detection.", "label": "Enable", "name": "enable"}, {"description": "Disable adhoc network detection", "help": "Disable adhoc network detection.", "label": "Disable", "name": "disable"}]
VALID_BODY_EAPOL_KEY_OVERFLOW: Literal[{"description": "Enable overflow EAPOL key detection", "help": "Enable overflow EAPOL key detection.", "label": "Enable", "name": "enable"}, {"description": "Disable overflow EAPOL key detection", "help": "Disable overflow EAPOL key detection.", "label": "Disable", "name": "disable"}]
VALID_BODY_AP_IMPERSONATION: Literal[{"description": "Enable AP impersonation detection", "help": "Enable AP impersonation detection.", "label": "Enable", "name": "enable"}, {"description": "Disable AP impersonation detection", "help": "Disable AP impersonation detection.", "label": "Disable", "name": "disable"}]
VALID_BODY_INVALID_ADDR_COMBINATION: Literal[{"description": "Enable invalid address combination detection", "help": "Enable invalid address combination detection.", "label": "Enable", "name": "enable"}, {"description": "Disable invalid address combination detection", "help": "Disable invalid address combination detection.", "label": "Disable", "name": "disable"}]
VALID_BODY_BEACON_WRONG_CHANNEL: Literal[{"description": "Enable beacon wrong channel detection", "help": "Enable beacon wrong channel detection.", "label": "Enable", "name": "enable"}, {"description": "Disable beacon wrong channel detection", "help": "Disable beacon wrong channel detection.", "label": "Disable", "name": "disable"}]
VALID_BODY_HT_GREENFIELD: Literal[{"description": "Enable HT greenfield detection", "help": "Enable HT greenfield detection.", "label": "Enable", "name": "enable"}, {"description": "Disable HT greenfield detection", "help": "Disable HT greenfield detection.", "label": "Disable", "name": "disable"}]
VALID_BODY_OVERFLOW_IE: Literal[{"description": "Enable overflow IE detection", "help": "Enable overflow IE detection.", "label": "Enable", "name": "enable"}, {"description": "Disable overflow IE detection", "help": "Disable overflow IE detection.", "label": "Disable", "name": "disable"}]
VALID_BODY_MALFORMED_HT_IE: Literal[{"description": "Enable malformed HT IE detection", "help": "Enable malformed HT IE detection.", "label": "Enable", "name": "enable"}, {"description": "Disable malformed HT IE detection", "help": "Disable malformed HT IE detection.", "label": "Disable", "name": "disable"}]
VALID_BODY_MALFORMED_AUTH: Literal[{"description": "Enable malformed auth frame detection", "help": "Enable malformed auth frame detection.", "label": "Enable", "name": "enable"}, {"description": "Disable malformed auth frame detection", "help": "Disable malformed auth frame detection.", "label": "Disable", "name": "disable"}]
VALID_BODY_MALFORMED_ASSOCIATION: Literal[{"description": "Enable malformed association request detection", "help": "Enable malformed association request detection.", "label": "Enable", "name": "enable"}, {"description": "Disable malformed association request detection", "help": "Disable malformed association request detection.", "label": "Disable", "name": "disable"}]
VALID_BODY_HT_40MHZ_INTOLERANCE: Literal[{"description": "Enable HT 40 MHz intolerance detection", "help": "Enable HT 40 MHz intolerance detection.", "label": "Enable", "name": "enable"}, {"description": "Disable HT 40 MHz intolerance detection", "help": "Disable HT 40 MHz intolerance detection.", "label": "Disable", "name": "disable"}]
VALID_BODY_VALID_SSID_MISUSE: Literal[{"description": "Enable valid SSID misuse detection", "help": "Enable valid SSID misuse detection.", "label": "Enable", "name": "enable"}, {"description": "Disable valid SSID misuse detection", "help": "Disable valid SSID misuse detection.", "label": "Disable", "name": "disable"}]
VALID_BODY_VALID_CLIENT_MISASSOCIATION: Literal[{"description": "Enable valid client misassociation detection", "help": "Enable valid client misassociation detection.", "label": "Enable", "name": "enable"}, {"description": "Disable valid client misassociation detection", "help": "Disable valid client misassociation detection.", "label": "Disable", "name": "disable"}]
VALID_BODY_HOTSPOTTER_ATTACK: Literal[{"description": "Enable hotspotter attack detection", "help": "Enable hotspotter attack detection.", "label": "Enable", "name": "enable"}, {"description": "Disable hotspotter attack detection", "help": "Disable hotspotter attack detection.", "label": "Disable", "name": "disable"}]
VALID_BODY_PWSAVE_DOS_ATTACK: Literal[{"description": "Enable power save DOS attack detection", "help": "Enable power save DOS attack detection.", "label": "Enable", "name": "enable"}, {"description": "Disable power save DOS attack detection", "help": "Disable power save DOS attack detection.", "label": "Disable", "name": "disable"}]
VALID_BODY_OMERTA_ATTACK: Literal[{"description": "Enable omerta attack detection", "help": "Enable omerta attack detection.", "label": "Enable", "name": "enable"}, {"description": "Disable omerta attack detection", "help": "Disable omerta attack detection.", "label": "Disable", "name": "disable"}]
VALID_BODY_DISCONNECT_STATION: Literal[{"description": "Enable disconnect station detection", "help": "Enable disconnect station detection.", "label": "Enable", "name": "enable"}, {"description": "Disable disconnect station detection", "help": "Disable disconnect station detection.", "label": "Disable", "name": "disable"}]
VALID_BODY_UNENCRYPTED_VALID: Literal[{"description": "Enable unencrypted valid detection", "help": "Enable unencrypted valid detection.", "label": "Enable", "name": "enable"}, {"description": "Disable unencrypted valid detection", "help": "Disable unencrypted valid detection.", "label": "Disable", "name": "disable"}]
VALID_BODY_FATA_JACK: Literal[{"description": "Enable FATA-Jack detection", "help": "Enable FATA-Jack detection.", "label": "Enable", "name": "enable"}, {"description": "Disable FATA-Jack detection", "help": "Disable FATA-Jack detection.", "label": "Disable", "name": "disable"}]
VALID_BODY_RISKY_ENCRYPTION: Literal[{"description": "Enable Risky Encryption detection", "help": "Enable Risky Encryption detection.", "label": "Enable", "name": "enable"}, {"description": "Disable Risky Encryption detection", "help": "Disable Risky Encryption detection.", "label": "Disable", "name": "disable"}]
VALID_BODY_FUZZED_BEACON: Literal[{"description": "Enable fuzzed beacon detection", "help": "Enable fuzzed beacon detection.", "label": "Enable", "name": "enable"}, {"description": "Disable fuzzed beacon detection", "help": "Disable fuzzed beacon detection.", "label": "Disable", "name": "disable"}]
VALID_BODY_FUZZED_PROBE_REQUEST: Literal[{"description": "Enable fuzzed probe request detection", "help": "Enable fuzzed probe request detection.", "label": "Enable", "name": "enable"}, {"description": "Disable fuzzed probe request detection", "help": "Disable fuzzed probe request detection.", "label": "Disable", "name": "disable"}]
VALID_BODY_FUZZED_PROBE_RESPONSE: Literal[{"description": "Enable fuzzed probe response detection", "help": "Enable fuzzed probe response detection.", "label": "Enable", "name": "enable"}, {"description": "Disable fuzzed probe response detection", "help": "Disable fuzzed probe response detection.", "label": "Disable", "name": "disable"}]
VALID_BODY_AIR_JACK: Literal[{"description": "Enable AirJack detection", "help": "Enable AirJack detection.", "label": "Enable", "name": "enable"}, {"description": "Disable AirJack detection", "help": "Disable AirJack detection.", "label": "Disable", "name": "disable"}]
VALID_BODY_WPA_FT_ATTACK: Literal[{"description": "Enable WPA FT attack detection", "help": "Enable WPA FT attack detection.", "label": "Enable", "name": "enable"}, {"description": "Disable WPA FT attack detection", "help": "Disable WPA FT attack detection.", "label": "Disable", "name": "disable"}]

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
    "VALID_BODY_SENSOR_MODE",
    "VALID_BODY_AP_SCAN",
    "VALID_BODY_AP_SCAN_PASSIVE",
    "VALID_BODY_AP_AUTO_SUPPRESS",
    "VALID_BODY_WIRELESS_BRIDGE",
    "VALID_BODY_DEAUTH_BROADCAST",
    "VALID_BODY_NULL_SSID_PROBE_RESP",
    "VALID_BODY_LONG_DURATION_ATTACK",
    "VALID_BODY_INVALID_MAC_OUI",
    "VALID_BODY_WEAK_WEP_IV",
    "VALID_BODY_AUTH_FRAME_FLOOD",
    "VALID_BODY_ASSOC_FRAME_FLOOD",
    "VALID_BODY_REASSOC_FLOOD",
    "VALID_BODY_PROBE_FLOOD",
    "VALID_BODY_BCN_FLOOD",
    "VALID_BODY_RTS_FLOOD",
    "VALID_BODY_CTS_FLOOD",
    "VALID_BODY_CLIENT_FLOOD",
    "VALID_BODY_BLOCK_ACK_FLOOD",
    "VALID_BODY_PSPOLL_FLOOD",
    "VALID_BODY_NETSTUMBLER",
    "VALID_BODY_WELLENREITER",
    "VALID_BODY_SPOOFED_DEAUTH",
    "VALID_BODY_ASLEAP_ATTACK",
    "VALID_BODY_EAPOL_START_FLOOD",
    "VALID_BODY_EAPOL_LOGOFF_FLOOD",
    "VALID_BODY_EAPOL_SUCC_FLOOD",
    "VALID_BODY_EAPOL_FAIL_FLOOD",
    "VALID_BODY_EAPOL_PRE_SUCC_FLOOD",
    "VALID_BODY_EAPOL_PRE_FAIL_FLOOD",
    "VALID_BODY_WINDOWS_BRIDGE",
    "VALID_BODY_DISASSOC_BROADCAST",
    "VALID_BODY_AP_SPOOFING",
    "VALID_BODY_CHAN_BASED_MITM",
    "VALID_BODY_ADHOC_VALID_SSID",
    "VALID_BODY_ADHOC_NETWORK",
    "VALID_BODY_EAPOL_KEY_OVERFLOW",
    "VALID_BODY_AP_IMPERSONATION",
    "VALID_BODY_INVALID_ADDR_COMBINATION",
    "VALID_BODY_BEACON_WRONG_CHANNEL",
    "VALID_BODY_HT_GREENFIELD",
    "VALID_BODY_OVERFLOW_IE",
    "VALID_BODY_MALFORMED_HT_IE",
    "VALID_BODY_MALFORMED_AUTH",
    "VALID_BODY_MALFORMED_ASSOCIATION",
    "VALID_BODY_HT_40MHZ_INTOLERANCE",
    "VALID_BODY_VALID_SSID_MISUSE",
    "VALID_BODY_VALID_CLIENT_MISASSOCIATION",
    "VALID_BODY_HOTSPOTTER_ATTACK",
    "VALID_BODY_PWSAVE_DOS_ATTACK",
    "VALID_BODY_OMERTA_ATTACK",
    "VALID_BODY_DISCONNECT_STATION",
    "VALID_BODY_UNENCRYPTED_VALID",
    "VALID_BODY_FATA_JACK",
    "VALID_BODY_RISKY_ENCRYPTION",
    "VALID_BODY_FUZZED_BEACON",
    "VALID_BODY_FUZZED_PROBE_REQUEST",
    "VALID_BODY_FUZZED_PROBE_RESPONSE",
    "VALID_BODY_AIR_JACK",
    "VALID_BODY_WPA_FT_ATTACK",
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