from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class WidsProfilePayload(TypedDict, total=False):
    """
    Type hints for wireless_controller/wids_profile payload fields.
    
    Configure wireless intrusion detection system (WIDS) profiles.
    
    **Usage:**
        payload: WidsProfilePayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    name: NotRequired[str]  # WIDS profile name.
    comment: NotRequired[str]  # Comment.
    sensor_mode: NotRequired[Literal[{"description": "Disable the scan", "help": "Disable the scan.", "label": "Disable", "name": "disable"}, {"description": "Enable the scan and monitor foreign channels", "help": "Enable the scan and monitor foreign channels. Foreign channels are all other available channels than the current operating channel.", "label": "Foreign", "name": "foreign"}, {"description": "Enable the scan and monitor both foreign and home channels", "help": "Enable the scan and monitor both foreign and home channels. Select this option to monitor all WiFi channels.", "label": "Both", "name": "both"}]]  # Scan nearby WiFi stations (default = disable).
    ap_scan: NotRequired[Literal[{"description": "Disable rogue AP detection", "help": "Disable rogue AP detection.", "label": "Disable", "name": "disable"}, {"description": "Enable rogue AP detection", "help": "Enable rogue AP detection.", "label": "Enable", "name": "enable"}]]  # Enable/disable rogue AP detection.
    ap_scan_channel_list_2G_5G: NotRequired[list[dict[str, Any]]]  # Selected ap scan channel list for 2.4G and 5G bands.
    ap_scan_channel_list_6G: NotRequired[list[dict[str, Any]]]  # Selected ap scan channel list for 6G band.
    ap_bgscan_period: NotRequired[int]  # Period between background scans (10 - 3600 sec, default = 60
    ap_bgscan_intv: NotRequired[int]  # Period between successive channel scans (1 - 600 sec, defaul
    ap_bgscan_duration: NotRequired[int]  # Listen time on scanning a channel (10 - 1000 msec, default =
    ap_bgscan_idle: NotRequired[int]  # Wait time for channel inactivity before scanning this channe
    ap_bgscan_report_intv: NotRequired[int]  # Period between background scan reports (15 - 600 sec, defaul
    ap_bgscan_disable_schedules: NotRequired[list[dict[str, Any]]]  # Firewall schedules for turning off FortiAP radio background 
    ap_fgscan_report_intv: NotRequired[int]  # Period between foreground scan reports (15 - 600 sec, defaul
    ap_scan_passive: NotRequired[Literal[{"description": "Passive scanning on all channels", "help": "Passive scanning on all channels.", "label": "Enable", "name": "enable"}, {"description": "Passive scanning only on DFS channels", "help": "Passive scanning only on DFS channels.", "label": "Disable", "name": "disable"}]]  # Enable/disable passive scanning. Enable means do not send pr
    ap_scan_threshold: NotRequired[str]  # Minimum signal level/threshold in dBm required for the AP to
    ap_auto_suppress: NotRequired[Literal[{"description": "Enable on-wire rogue AP auto-suppression", "help": "Enable on-wire rogue AP auto-suppression.", "label": "Enable", "name": "enable"}, {"description": "Disable on-wire rogue AP auto-suppression", "help": "Disable on-wire rogue AP auto-suppression.", "label": "Disable", "name": "disable"}]]  # Enable/disable on-wire rogue AP auto-suppression (default = 
    wireless_bridge: NotRequired[Literal[{"description": "Enable wireless bridge detection", "help": "Enable wireless bridge detection.", "label": "Enable", "name": "enable"}, {"description": "Disable wireless bridge detection", "help": "Disable wireless bridge detection.", "label": "Disable", "name": "disable"}]]  # Enable/disable wireless bridge detection (default = disable)
    deauth_broadcast: NotRequired[Literal[{"description": "Enable broadcast de-authentication detection", "help": "Enable broadcast de-authentication detection.", "label": "Enable", "name": "enable"}, {"description": "Disable broadcast de-authentication detection", "help": "Disable broadcast de-authentication detection.", "label": "Disable", "name": "disable"}]]  # Enable/disable broadcasting de-authentication detection (def
    null_ssid_probe_resp: NotRequired[Literal[{"description": "Enable null SSID probe resp detection", "help": "Enable null SSID probe resp detection.", "label": "Enable", "name": "enable"}, {"description": "Disable null SSID probe resp detection", "help": "Disable null SSID probe resp detection.", "label": "Disable", "name": "disable"}]]  # Enable/disable null SSID probe response detection (default =
    long_duration_attack: NotRequired[Literal[{"description": "Enable long duration attack detection", "help": "Enable long duration attack detection.", "label": "Enable", "name": "enable"}, {"description": "Disable long duration attack detection", "help": "Disable long duration attack detection.", "label": "Disable", "name": "disable"}]]  # Enable/disable long duration attack detection based on user 
    long_duration_thresh: NotRequired[int]  # Threshold value for long duration attack detection (1000 - 3
    invalid_mac_oui: NotRequired[Literal[{"description": "Enable invalid MAC OUI detection", "help": "Enable invalid MAC OUI detection.", "label": "Enable", "name": "enable"}, {"description": "Disable invalid MAC OUI detection", "help": "Disable invalid MAC OUI detection.", "label": "Disable", "name": "disable"}]]  # Enable/disable invalid MAC OUI detection.
    weak_wep_iv: NotRequired[Literal[{"description": "Enable weak WEP IV detection", "help": "Enable weak WEP IV detection.", "label": "Enable", "name": "enable"}, {"description": "Disable weak WEP IV detection", "help": "Disable weak WEP IV detection.", "label": "Disable", "name": "disable"}]]  # Enable/disable weak WEP IV (Initialization Vector) detection
    auth_frame_flood: NotRequired[Literal[{"description": "Enable authentication frame flooding detection", "help": "Enable authentication frame flooding detection.", "label": "Enable", "name": "enable"}, {"description": "Disable authentication frame flooding detection", "help": "Disable authentication frame flooding detection.", "label": "Disable", "name": "disable"}]]  # Enable/disable authentication frame flooding detection (defa
    auth_flood_time: NotRequired[int]  # Number of seconds after which a station is considered not co
    auth_flood_thresh: NotRequired[int]  # The threshold value for authentication frame flooding.
    assoc_frame_flood: NotRequired[Literal[{"description": "Enable association frame flooding detection", "help": "Enable association frame flooding detection.", "label": "Enable", "name": "enable"}, {"description": "Disable association frame flooding detection", "help": "Disable association frame flooding detection.", "label": "Disable", "name": "disable"}]]  # Enable/disable association frame flooding detection (default
    assoc_flood_time: NotRequired[int]  # Number of seconds after which a station is considered not co
    assoc_flood_thresh: NotRequired[int]  # The threshold value for association frame flooding.
    reassoc_flood: NotRequired[Literal[{"description": "Enable reassociation flood detection", "help": "Enable reassociation flood detection.", "label": "Enable", "name": "enable"}, {"description": "Disable reassociation flood detection", "help": "Disable reassociation flood detection.", "label": "Disable", "name": "disable"}]]  # Enable/disable reassociation flood detection (default = disa
    reassoc_flood_time: NotRequired[int]  # Detection Window Period.
    reassoc_flood_thresh: NotRequired[int]  # The threshold value for reassociation flood.
    probe_flood: NotRequired[Literal[{"description": "Enable probe flood detection", "help": "Enable probe flood detection.", "label": "Enable", "name": "enable"}, {"description": "Disable probe flood detection", "help": "Disable probe flood detection.", "label": "Disable", "name": "disable"}]]  # Enable/disable probe flood detection (default = disable).
    probe_flood_time: NotRequired[int]  # Detection Window Period.
    probe_flood_thresh: NotRequired[int]  # The threshold value for probe flood.
    bcn_flood: NotRequired[Literal[{"description": "Enable bcn flood detection", "help": "Enable bcn flood detection.", "label": "Enable", "name": "enable"}, {"description": "Disable bcn flood detection", "help": "Disable bcn flood detection.", "label": "Disable", "name": "disable"}]]  # Enable/disable bcn flood detection (default = disable).
    bcn_flood_time: NotRequired[int]  # Detection Window Period.
    bcn_flood_thresh: NotRequired[int]  # The threshold value for bcn flood.
    rts_flood: NotRequired[Literal[{"description": "Enable rts flood detection", "help": "Enable rts flood detection.", "label": "Enable", "name": "enable"}, {"description": "Disable rts flood detection", "help": "Disable rts flood detection.", "label": "Disable", "name": "disable"}]]  # Enable/disable rts flood detection (default = disable).
    rts_flood_time: NotRequired[int]  # Detection Window Period.
    rts_flood_thresh: NotRequired[int]  # The threshold value for rts flood.
    cts_flood: NotRequired[Literal[{"description": "Enable cts flood detection", "help": "Enable cts flood detection.", "label": "Enable", "name": "enable"}, {"description": "Disable cts flood detection", "help": "Disable cts flood detection.", "label": "Disable", "name": "disable"}]]  # Enable/disable cts flood detection (default = disable).
    cts_flood_time: NotRequired[int]  # Detection Window Period.
    cts_flood_thresh: NotRequired[int]  # The threshold value for cts flood.
    client_flood: NotRequired[Literal[{"description": "Enable client flood detection", "help": "Enable client flood detection.", "label": "Enable", "name": "enable"}, {"description": "Disable client flood detection", "help": "Disable client flood detection.", "label": "Disable", "name": "disable"}]]  # Enable/disable client flood detection (default = disable).
    client_flood_time: NotRequired[int]  # Detection Window Period.
    client_flood_thresh: NotRequired[int]  # The threshold value for client flood.
    block_ack_flood: NotRequired[Literal[{"description": "Enable block_ack flood detection", "help": "Enable block_ack flood detection.", "label": "Enable", "name": "enable"}, {"description": "Disable block_ack flood detection", "help": "Disable block_ack flood detection.", "label": "Disable", "name": "disable"}]]  # Enable/disable block_ack flood detection (default = disable)
    block_ack_flood_time: NotRequired[int]  # Detection Window Period.
    block_ack_flood_thresh: NotRequired[int]  # The threshold value for block_ack flood.
    pspoll_flood: NotRequired[Literal[{"description": "Enable pspoll flood detection", "help": "Enable pspoll flood detection.", "label": "Enable", "name": "enable"}, {"description": "Disable pspoll flood detection", "help": "Disable pspoll flood detection.", "label": "Disable", "name": "disable"}]]  # Enable/disable pspoll flood detection (default = disable).
    pspoll_flood_time: NotRequired[int]  # Detection Window Period.
    pspoll_flood_thresh: NotRequired[int]  # The threshold value for pspoll flood.
    netstumbler: NotRequired[Literal[{"description": "Enable netstumbler detection", "help": "Enable netstumbler detection.", "label": "Enable", "name": "enable"}, {"description": "Disable netstumbler detection", "help": "Disable netstumbler detection.", "label": "Disable", "name": "disable"}]]  # Enable/disable netstumbler detection (default = disable).
    netstumbler_time: NotRequired[int]  # Detection Window Period.
    netstumbler_thresh: NotRequired[int]  # The threshold value for netstumbler.
    wellenreiter: NotRequired[Literal[{"description": "Enable wellenreiter detection", "help": "Enable wellenreiter detection.", "label": "Enable", "name": "enable"}, {"description": "Disable wellenreiter detection", "help": "Disable wellenreiter detection.", "label": "Disable", "name": "disable"}]]  # Enable/disable wellenreiter detection (default = disable).
    wellenreiter_time: NotRequired[int]  # Detection Window Period.
    wellenreiter_thresh: NotRequired[int]  # The threshold value for wellenreiter.
    spoofed_deauth: NotRequired[Literal[{"description": "Enable spoofed de-authentication attack detection", "help": "Enable spoofed de-authentication attack detection.", "label": "Enable", "name": "enable"}, {"description": "Disable spoofed de-authentication attack detection", "help": "Disable spoofed de-authentication attack detection.", "label": "Disable", "name": "disable"}]]  # Enable/disable spoofed de-authentication attack detection (d
    asleap_attack: NotRequired[Literal[{"description": "Enable asleap attack detection", "help": "Enable asleap attack detection.", "label": "Enable", "name": "enable"}, {"description": "Disable asleap attack detection", "help": "Disable asleap attack detection.", "label": "Disable", "name": "disable"}]]  # Enable/disable asleap attack detection (default = disable).
    eapol_start_flood: NotRequired[Literal[{"description": "Enable EAPOL-Start flooding detection", "help": "Enable EAPOL-Start flooding detection.", "label": "Enable", "name": "enable"}, {"description": "Disable EAPOL-Start flooding detection", "help": "Disable EAPOL-Start flooding detection.", "label": "Disable", "name": "disable"}]]  # Enable/disable EAPOL-Start flooding (to AP) detection (defau
    eapol_start_thresh: NotRequired[int]  # The threshold value for EAPOL-Start flooding in specified in
    eapol_start_intv: NotRequired[int]  # The detection interval for EAPOL-Start flooding (1 - 3600 se
    eapol_logoff_flood: NotRequired[Literal[{"description": "Enable EAPOL-Logoff flooding detection", "help": "Enable EAPOL-Logoff flooding detection.", "label": "Enable", "name": "enable"}, {"description": "Disable EAPOL-Logoff flooding detection", "help": "Disable EAPOL-Logoff flooding detection.", "label": "Disable", "name": "disable"}]]  # Enable/disable EAPOL-Logoff flooding (to AP) detection (defa
    eapol_logoff_thresh: NotRequired[int]  # The threshold value for EAPOL-Logoff flooding in specified i
    eapol_logoff_intv: NotRequired[int]  # The detection interval for EAPOL-Logoff flooding (1 - 3600 s
    eapol_succ_flood: NotRequired[Literal[{"description": "Enable EAPOL-Success flooding detection", "help": "Enable EAPOL-Success flooding detection.", "label": "Enable", "name": "enable"}, {"description": "Disable EAPOL-Success flooding detection", "help": "Disable EAPOL-Success flooding detection.", "label": "Disable", "name": "disable"}]]  # Enable/disable EAPOL-Success flooding (to AP) detection (def
    eapol_succ_thresh: NotRequired[int]  # The threshold value for EAPOL-Success flooding in specified 
    eapol_succ_intv: NotRequired[int]  # The detection interval for EAPOL-Success flooding (1 - 3600 
    eapol_fail_flood: NotRequired[Literal[{"description": "Enable EAPOL-Failure flooding detection", "help": "Enable EAPOL-Failure flooding detection.", "label": "Enable", "name": "enable"}, {"description": "Disable EAPOL-Failure flooding detection", "help": "Disable EAPOL-Failure flooding detection.", "label": "Disable", "name": "disable"}]]  # Enable/disable EAPOL-Failure flooding (to AP) detection (def
    eapol_fail_thresh: NotRequired[int]  # The threshold value for EAPOL-Failure flooding in specified 
    eapol_fail_intv: NotRequired[int]  # The detection interval for EAPOL-Failure flooding (1 - 3600 
    eapol_pre_succ_flood: NotRequired[Literal[{"description": "Enable premature EAPOL-Success flooding detection", "help": "Enable premature EAPOL-Success flooding detection.", "label": "Enable", "name": "enable"}, {"description": "Disable premature EAPOL-Success flooding detection", "help": "Disable premature EAPOL-Success flooding detection.", "label": "Disable", "name": "disable"}]]  # Enable/disable premature EAPOL-Success flooding (to STA) det
    eapol_pre_succ_thresh: NotRequired[int]  # The threshold value for premature EAPOL-Success flooding in 
    eapol_pre_succ_intv: NotRequired[int]  # The detection interval for premature EAPOL-Success flooding 
    eapol_pre_fail_flood: NotRequired[Literal[{"description": "Enable premature EAPOL-Failure flooding detection", "help": "Enable premature EAPOL-Failure flooding detection.", "label": "Enable", "name": "enable"}, {"description": "Disable premature EAPOL-Failure flooding detection", "help": "Disable premature EAPOL-Failure flooding detection.", "label": "Disable", "name": "disable"}]]  # Enable/disable premature EAPOL-Failure flooding (to STA) det
    eapol_pre_fail_thresh: NotRequired[int]  # The threshold value for premature EAPOL-Failure flooding in 
    eapol_pre_fail_intv: NotRequired[int]  # The detection interval for premature EAPOL-Failure flooding 
    deauth_unknown_src_thresh: NotRequired[int]  # Threshold value per second to deauth unknown src for DoS att
    windows_bridge: NotRequired[Literal[{"description": "Enable windows bridge detection", "help": "Enable windows bridge detection.", "label": "Enable", "name": "enable"}, {"description": "Disable windows bridge detection", "help": "Disable windows bridge detection.", "label": "Disable", "name": "disable"}]]  # Enable/disable windows bridge detection (default = disable).
    disassoc_broadcast: NotRequired[Literal[{"description": "Enable broadcast dis-association detection", "help": "Enable broadcast dis-association detection.", "label": "Enable", "name": "enable"}, {"description": "Disable broadcast dis-association detection", "help": "Disable broadcast dis-association detection.", "label": "Disable", "name": "disable"}]]  # Enable/disable broadcast dis-association detection (default 
    ap_spoofing: NotRequired[Literal[{"description": "Enable AP spoofing detection", "help": "Enable AP spoofing detection.", "label": "Enable", "name": "enable"}, {"description": "Disable AP spoofing detection", "help": "Disable AP spoofing detection.", "label": "Disable", "name": "disable"}]]  # Enable/disable AP spoofing detection (default = disable).
    chan_based_mitm: NotRequired[Literal[{"description": "Enable channel based mitm detection", "help": "Enable channel based mitm detection.", "label": "Enable", "name": "enable"}, {"description": "Disable channel based mitm detection", "help": "Disable channel based mitm detection.", "label": "Disable", "name": "disable"}]]  # Enable/disable channel based mitm detection (default = disab
    adhoc_valid_ssid: NotRequired[Literal[{"description": "Enable adhoc using valid SSID detection", "help": "Enable adhoc using valid SSID detection.", "label": "Enable", "name": "enable"}, {"description": "Disable adhoc using valid SSID detection", "help": "Disable adhoc using valid SSID detection.", "label": "Disable", "name": "disable"}]]  # Enable/disable adhoc using valid SSID detection (default = d
    adhoc_network: NotRequired[Literal[{"description": "Enable adhoc network detection", "help": "Enable adhoc network detection.", "label": "Enable", "name": "enable"}, {"description": "Disable adhoc network detection", "help": "Disable adhoc network detection.", "label": "Disable", "name": "disable"}]]  # Enable/disable adhoc network detection (default = disable).
    eapol_key_overflow: NotRequired[Literal[{"description": "Enable overflow EAPOL key detection", "help": "Enable overflow EAPOL key detection.", "label": "Enable", "name": "enable"}, {"description": "Disable overflow EAPOL key detection", "help": "Disable overflow EAPOL key detection.", "label": "Disable", "name": "disable"}]]  # Enable/disable overflow EAPOL key detection (default = disab
    ap_impersonation: NotRequired[Literal[{"description": "Enable AP impersonation detection", "help": "Enable AP impersonation detection.", "label": "Enable", "name": "enable"}, {"description": "Disable AP impersonation detection", "help": "Disable AP impersonation detection.", "label": "Disable", "name": "disable"}]]  # Enable/disable AP impersonation detection (default = disable
    invalid_addr_combination: NotRequired[Literal[{"description": "Enable invalid address combination detection", "help": "Enable invalid address combination detection.", "label": "Enable", "name": "enable"}, {"description": "Disable invalid address combination detection", "help": "Disable invalid address combination detection.", "label": "Disable", "name": "disable"}]]  # Enable/disable invalid address combination detection (defaul
    beacon_wrong_channel: NotRequired[Literal[{"description": "Enable beacon wrong channel detection", "help": "Enable beacon wrong channel detection.", "label": "Enable", "name": "enable"}, {"description": "Disable beacon wrong channel detection", "help": "Disable beacon wrong channel detection.", "label": "Disable", "name": "disable"}]]  # Enable/disable beacon wrong channel detection (default = dis
    ht_greenfield: NotRequired[Literal[{"description": "Enable HT greenfield detection", "help": "Enable HT greenfield detection.", "label": "Enable", "name": "enable"}, {"description": "Disable HT greenfield detection", "help": "Disable HT greenfield detection.", "label": "Disable", "name": "disable"}]]  # Enable/disable HT greenfield detection (default = disable).
    overflow_ie: NotRequired[Literal[{"description": "Enable overflow IE detection", "help": "Enable overflow IE detection.", "label": "Enable", "name": "enable"}, {"description": "Disable overflow IE detection", "help": "Disable overflow IE detection.", "label": "Disable", "name": "disable"}]]  # Enable/disable overflow IE detection (default = disable).
    malformed_ht_ie: NotRequired[Literal[{"description": "Enable malformed HT IE detection", "help": "Enable malformed HT IE detection.", "label": "Enable", "name": "enable"}, {"description": "Disable malformed HT IE detection", "help": "Disable malformed HT IE detection.", "label": "Disable", "name": "disable"}]]  # Enable/disable malformed HT IE detection (default = disable)
    malformed_auth: NotRequired[Literal[{"description": "Enable malformed auth frame detection", "help": "Enable malformed auth frame detection.", "label": "Enable", "name": "enable"}, {"description": "Disable malformed auth frame detection", "help": "Disable malformed auth frame detection.", "label": "Disable", "name": "disable"}]]  # Enable/disable malformed auth frame detection (default = dis
    malformed_association: NotRequired[Literal[{"description": "Enable malformed association request detection", "help": "Enable malformed association request detection.", "label": "Enable", "name": "enable"}, {"description": "Disable malformed association request detection", "help": "Disable malformed association request detection.", "label": "Disable", "name": "disable"}]]  # Enable/disable malformed association request detection (defa
    ht_40mhz_intolerance: NotRequired[Literal[{"description": "Enable HT 40 MHz intolerance detection", "help": "Enable HT 40 MHz intolerance detection.", "label": "Enable", "name": "enable"}, {"description": "Disable HT 40 MHz intolerance detection", "help": "Disable HT 40 MHz intolerance detection.", "label": "Disable", "name": "disable"}]]  # Enable/disable HT 40 MHz intolerance detection (default = di
    valid_ssid_misuse: NotRequired[Literal[{"description": "Enable valid SSID misuse detection", "help": "Enable valid SSID misuse detection.", "label": "Enable", "name": "enable"}, {"description": "Disable valid SSID misuse detection", "help": "Disable valid SSID misuse detection.", "label": "Disable", "name": "disable"}]]  # Enable/disable valid SSID misuse detection (default = disabl
    valid_client_misassociation: NotRequired[Literal[{"description": "Enable valid client misassociation detection", "help": "Enable valid client misassociation detection.", "label": "Enable", "name": "enable"}, {"description": "Disable valid client misassociation detection", "help": "Disable valid client misassociation detection.", "label": "Disable", "name": "disable"}]]  # Enable/disable valid client misassociation detection (defaul
    hotspotter_attack: NotRequired[Literal[{"description": "Enable hotspotter attack detection", "help": "Enable hotspotter attack detection.", "label": "Enable", "name": "enable"}, {"description": "Disable hotspotter attack detection", "help": "Disable hotspotter attack detection.", "label": "Disable", "name": "disable"}]]  # Enable/disable hotspotter attack detection (default = disabl
    pwsave_dos_attack: NotRequired[Literal[{"description": "Enable power save DOS attack detection", "help": "Enable power save DOS attack detection.", "label": "Enable", "name": "enable"}, {"description": "Disable power save DOS attack detection", "help": "Disable power save DOS attack detection.", "label": "Disable", "name": "disable"}]]  # Enable/disable power save DOS attack detection (default = di
    omerta_attack: NotRequired[Literal[{"description": "Enable omerta attack detection", "help": "Enable omerta attack detection.", "label": "Enable", "name": "enable"}, {"description": "Disable omerta attack detection", "help": "Disable omerta attack detection.", "label": "Disable", "name": "disable"}]]  # Enable/disable omerta attack detection (default = disable).
    disconnect_station: NotRequired[Literal[{"description": "Enable disconnect station detection", "help": "Enable disconnect station detection.", "label": "Enable", "name": "enable"}, {"description": "Disable disconnect station detection", "help": "Disable disconnect station detection.", "label": "Disable", "name": "disable"}]]  # Enable/disable disconnect station detection (default = disab
    unencrypted_valid: NotRequired[Literal[{"description": "Enable unencrypted valid detection", "help": "Enable unencrypted valid detection.", "label": "Enable", "name": "enable"}, {"description": "Disable unencrypted valid detection", "help": "Disable unencrypted valid detection.", "label": "Disable", "name": "disable"}]]  # Enable/disable unencrypted valid detection (default = disabl
    fata_jack: NotRequired[Literal[{"description": "Enable FATA-Jack detection", "help": "Enable FATA-Jack detection.", "label": "Enable", "name": "enable"}, {"description": "Disable FATA-Jack detection", "help": "Disable FATA-Jack detection.", "label": "Disable", "name": "disable"}]]  # Enable/disable FATA-Jack detection (default = disable).
    risky_encryption: NotRequired[Literal[{"description": "Enable Risky Encryption detection", "help": "Enable Risky Encryption detection.", "label": "Enable", "name": "enable"}, {"description": "Disable Risky Encryption detection", "help": "Disable Risky Encryption detection.", "label": "Disable", "name": "disable"}]]  # Enable/disable Risky Encryption detection (default = disable
    fuzzed_beacon: NotRequired[Literal[{"description": "Enable fuzzed beacon detection", "help": "Enable fuzzed beacon detection.", "label": "Enable", "name": "enable"}, {"description": "Disable fuzzed beacon detection", "help": "Disable fuzzed beacon detection.", "label": "Disable", "name": "disable"}]]  # Enable/disable fuzzed beacon detection (default = disable).
    fuzzed_probe_request: NotRequired[Literal[{"description": "Enable fuzzed probe request detection", "help": "Enable fuzzed probe request detection.", "label": "Enable", "name": "enable"}, {"description": "Disable fuzzed probe request detection", "help": "Disable fuzzed probe request detection.", "label": "Disable", "name": "disable"}]]  # Enable/disable fuzzed probe request detection (default = dis
    fuzzed_probe_response: NotRequired[Literal[{"description": "Enable fuzzed probe response detection", "help": "Enable fuzzed probe response detection.", "label": "Enable", "name": "enable"}, {"description": "Disable fuzzed probe response detection", "help": "Disable fuzzed probe response detection.", "label": "Disable", "name": "disable"}]]  # Enable/disable fuzzed probe response detection (default = di
    air_jack: NotRequired[Literal[{"description": "Enable AirJack detection", "help": "Enable AirJack detection.", "label": "Enable", "name": "enable"}, {"description": "Disable AirJack detection", "help": "Disable AirJack detection.", "label": "Disable", "name": "disable"}]]  # Enable/disable AirJack detection (default = disable).
    wpa_ft_attack: NotRequired[Literal[{"description": "Enable WPA FT attack detection", "help": "Enable WPA FT attack detection.", "label": "Enable", "name": "enable"}, {"description": "Disable WPA FT attack detection", "help": "Disable WPA FT attack detection.", "label": "Disable", "name": "disable"}]]  # Enable/disable WPA FT attack detection (default = disable).


class WidsProfile:
    """
    Configure wireless intrusion detection system (WIDS) profiles.
    
    Path: wireless_controller/wids_profile
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
        payload_dict: WidsProfilePayload | None = ...,
        name: str | None = ...,
        comment: str | None = ...,
        sensor_mode: Literal[{"description": "Disable the scan", "help": "Disable the scan.", "label": "Disable", "name": "disable"}, {"description": "Enable the scan and monitor foreign channels", "help": "Enable the scan and monitor foreign channels. Foreign channels are all other available channels than the current operating channel.", "label": "Foreign", "name": "foreign"}, {"description": "Enable the scan and monitor both foreign and home channels", "help": "Enable the scan and monitor both foreign and home channels. Select this option to monitor all WiFi channels.", "label": "Both", "name": "both"}] | None = ...,
        ap_scan: Literal[{"description": "Disable rogue AP detection", "help": "Disable rogue AP detection.", "label": "Disable", "name": "disable"}, {"description": "Enable rogue AP detection", "help": "Enable rogue AP detection.", "label": "Enable", "name": "enable"}] | None = ...,
        ap_scan_channel_list_2G_5G: list[dict[str, Any]] | None = ...,
        ap_scan_channel_list_6G: list[dict[str, Any]] | None = ...,
        ap_bgscan_period: int | None = ...,
        ap_bgscan_intv: int | None = ...,
        ap_bgscan_duration: int | None = ...,
        ap_bgscan_idle: int | None = ...,
        ap_bgscan_report_intv: int | None = ...,
        ap_bgscan_disable_schedules: list[dict[str, Any]] | None = ...,
        ap_fgscan_report_intv: int | None = ...,
        ap_scan_passive: Literal[{"description": "Passive scanning on all channels", "help": "Passive scanning on all channels.", "label": "Enable", "name": "enable"}, {"description": "Passive scanning only on DFS channels", "help": "Passive scanning only on DFS channels.", "label": "Disable", "name": "disable"}] | None = ...,
        ap_scan_threshold: str | None = ...,
        ap_auto_suppress: Literal[{"description": "Enable on-wire rogue AP auto-suppression", "help": "Enable on-wire rogue AP auto-suppression.", "label": "Enable", "name": "enable"}, {"description": "Disable on-wire rogue AP auto-suppression", "help": "Disable on-wire rogue AP auto-suppression.", "label": "Disable", "name": "disable"}] | None = ...,
        wireless_bridge: Literal[{"description": "Enable wireless bridge detection", "help": "Enable wireless bridge detection.", "label": "Enable", "name": "enable"}, {"description": "Disable wireless bridge detection", "help": "Disable wireless bridge detection.", "label": "Disable", "name": "disable"}] | None = ...,
        deauth_broadcast: Literal[{"description": "Enable broadcast de-authentication detection", "help": "Enable broadcast de-authentication detection.", "label": "Enable", "name": "enable"}, {"description": "Disable broadcast de-authentication detection", "help": "Disable broadcast de-authentication detection.", "label": "Disable", "name": "disable"}] | None = ...,
        null_ssid_probe_resp: Literal[{"description": "Enable null SSID probe resp detection", "help": "Enable null SSID probe resp detection.", "label": "Enable", "name": "enable"}, {"description": "Disable null SSID probe resp detection", "help": "Disable null SSID probe resp detection.", "label": "Disable", "name": "disable"}] | None = ...,
        long_duration_attack: Literal[{"description": "Enable long duration attack detection", "help": "Enable long duration attack detection.", "label": "Enable", "name": "enable"}, {"description": "Disable long duration attack detection", "help": "Disable long duration attack detection.", "label": "Disable", "name": "disable"}] | None = ...,
        long_duration_thresh: int | None = ...,
        invalid_mac_oui: Literal[{"description": "Enable invalid MAC OUI detection", "help": "Enable invalid MAC OUI detection.", "label": "Enable", "name": "enable"}, {"description": "Disable invalid MAC OUI detection", "help": "Disable invalid MAC OUI detection.", "label": "Disable", "name": "disable"}] | None = ...,
        weak_wep_iv: Literal[{"description": "Enable weak WEP IV detection", "help": "Enable weak WEP IV detection.", "label": "Enable", "name": "enable"}, {"description": "Disable weak WEP IV detection", "help": "Disable weak WEP IV detection.", "label": "Disable", "name": "disable"}] | None = ...,
        auth_frame_flood: Literal[{"description": "Enable authentication frame flooding detection", "help": "Enable authentication frame flooding detection.", "label": "Enable", "name": "enable"}, {"description": "Disable authentication frame flooding detection", "help": "Disable authentication frame flooding detection.", "label": "Disable", "name": "disable"}] | None = ...,
        auth_flood_time: int | None = ...,
        auth_flood_thresh: int | None = ...,
        assoc_frame_flood: Literal[{"description": "Enable association frame flooding detection", "help": "Enable association frame flooding detection.", "label": "Enable", "name": "enable"}, {"description": "Disable association frame flooding detection", "help": "Disable association frame flooding detection.", "label": "Disable", "name": "disable"}] | None = ...,
        assoc_flood_time: int | None = ...,
        assoc_flood_thresh: int | None = ...,
        reassoc_flood: Literal[{"description": "Enable reassociation flood detection", "help": "Enable reassociation flood detection.", "label": "Enable", "name": "enable"}, {"description": "Disable reassociation flood detection", "help": "Disable reassociation flood detection.", "label": "Disable", "name": "disable"}] | None = ...,
        reassoc_flood_time: int | None = ...,
        reassoc_flood_thresh: int | None = ...,
        probe_flood: Literal[{"description": "Enable probe flood detection", "help": "Enable probe flood detection.", "label": "Enable", "name": "enable"}, {"description": "Disable probe flood detection", "help": "Disable probe flood detection.", "label": "Disable", "name": "disable"}] | None = ...,
        probe_flood_time: int | None = ...,
        probe_flood_thresh: int | None = ...,
        bcn_flood: Literal[{"description": "Enable bcn flood detection", "help": "Enable bcn flood detection.", "label": "Enable", "name": "enable"}, {"description": "Disable bcn flood detection", "help": "Disable bcn flood detection.", "label": "Disable", "name": "disable"}] | None = ...,
        bcn_flood_time: int | None = ...,
        bcn_flood_thresh: int | None = ...,
        rts_flood: Literal[{"description": "Enable rts flood detection", "help": "Enable rts flood detection.", "label": "Enable", "name": "enable"}, {"description": "Disable rts flood detection", "help": "Disable rts flood detection.", "label": "Disable", "name": "disable"}] | None = ...,
        rts_flood_time: int | None = ...,
        rts_flood_thresh: int | None = ...,
        cts_flood: Literal[{"description": "Enable cts flood detection", "help": "Enable cts flood detection.", "label": "Enable", "name": "enable"}, {"description": "Disable cts flood detection", "help": "Disable cts flood detection.", "label": "Disable", "name": "disable"}] | None = ...,
        cts_flood_time: int | None = ...,
        cts_flood_thresh: int | None = ...,
        client_flood: Literal[{"description": "Enable client flood detection", "help": "Enable client flood detection.", "label": "Enable", "name": "enable"}, {"description": "Disable client flood detection", "help": "Disable client flood detection.", "label": "Disable", "name": "disable"}] | None = ...,
        client_flood_time: int | None = ...,
        client_flood_thresh: int | None = ...,
        block_ack_flood: Literal[{"description": "Enable block_ack flood detection", "help": "Enable block_ack flood detection.", "label": "Enable", "name": "enable"}, {"description": "Disable block_ack flood detection", "help": "Disable block_ack flood detection.", "label": "Disable", "name": "disable"}] | None = ...,
        block_ack_flood_time: int | None = ...,
        block_ack_flood_thresh: int | None = ...,
        pspoll_flood: Literal[{"description": "Enable pspoll flood detection", "help": "Enable pspoll flood detection.", "label": "Enable", "name": "enable"}, {"description": "Disable pspoll flood detection", "help": "Disable pspoll flood detection.", "label": "Disable", "name": "disable"}] | None = ...,
        pspoll_flood_time: int | None = ...,
        pspoll_flood_thresh: int | None = ...,
        netstumbler: Literal[{"description": "Enable netstumbler detection", "help": "Enable netstumbler detection.", "label": "Enable", "name": "enable"}, {"description": "Disable netstumbler detection", "help": "Disable netstumbler detection.", "label": "Disable", "name": "disable"}] | None = ...,
        netstumbler_time: int | None = ...,
        netstumbler_thresh: int | None = ...,
        wellenreiter: Literal[{"description": "Enable wellenreiter detection", "help": "Enable wellenreiter detection.", "label": "Enable", "name": "enable"}, {"description": "Disable wellenreiter detection", "help": "Disable wellenreiter detection.", "label": "Disable", "name": "disable"}] | None = ...,
        wellenreiter_time: int | None = ...,
        wellenreiter_thresh: int | None = ...,
        spoofed_deauth: Literal[{"description": "Enable spoofed de-authentication attack detection", "help": "Enable spoofed de-authentication attack detection.", "label": "Enable", "name": "enable"}, {"description": "Disable spoofed de-authentication attack detection", "help": "Disable spoofed de-authentication attack detection.", "label": "Disable", "name": "disable"}] | None = ...,
        asleap_attack: Literal[{"description": "Enable asleap attack detection", "help": "Enable asleap attack detection.", "label": "Enable", "name": "enable"}, {"description": "Disable asleap attack detection", "help": "Disable asleap attack detection.", "label": "Disable", "name": "disable"}] | None = ...,
        eapol_start_flood: Literal[{"description": "Enable EAPOL-Start flooding detection", "help": "Enable EAPOL-Start flooding detection.", "label": "Enable", "name": "enable"}, {"description": "Disable EAPOL-Start flooding detection", "help": "Disable EAPOL-Start flooding detection.", "label": "Disable", "name": "disable"}] | None = ...,
        eapol_start_thresh: int | None = ...,
        eapol_start_intv: int | None = ...,
        eapol_logoff_flood: Literal[{"description": "Enable EAPOL-Logoff flooding detection", "help": "Enable EAPOL-Logoff flooding detection.", "label": "Enable", "name": "enable"}, {"description": "Disable EAPOL-Logoff flooding detection", "help": "Disable EAPOL-Logoff flooding detection.", "label": "Disable", "name": "disable"}] | None = ...,
        eapol_logoff_thresh: int | None = ...,
        eapol_logoff_intv: int | None = ...,
        eapol_succ_flood: Literal[{"description": "Enable EAPOL-Success flooding detection", "help": "Enable EAPOL-Success flooding detection.", "label": "Enable", "name": "enable"}, {"description": "Disable EAPOL-Success flooding detection", "help": "Disable EAPOL-Success flooding detection.", "label": "Disable", "name": "disable"}] | None = ...,
        eapol_succ_thresh: int | None = ...,
        eapol_succ_intv: int | None = ...,
        eapol_fail_flood: Literal[{"description": "Enable EAPOL-Failure flooding detection", "help": "Enable EAPOL-Failure flooding detection.", "label": "Enable", "name": "enable"}, {"description": "Disable EAPOL-Failure flooding detection", "help": "Disable EAPOL-Failure flooding detection.", "label": "Disable", "name": "disable"}] | None = ...,
        eapol_fail_thresh: int | None = ...,
        eapol_fail_intv: int | None = ...,
        eapol_pre_succ_flood: Literal[{"description": "Enable premature EAPOL-Success flooding detection", "help": "Enable premature EAPOL-Success flooding detection.", "label": "Enable", "name": "enable"}, {"description": "Disable premature EAPOL-Success flooding detection", "help": "Disable premature EAPOL-Success flooding detection.", "label": "Disable", "name": "disable"}] | None = ...,
        eapol_pre_succ_thresh: int | None = ...,
        eapol_pre_succ_intv: int | None = ...,
        eapol_pre_fail_flood: Literal[{"description": "Enable premature EAPOL-Failure flooding detection", "help": "Enable premature EAPOL-Failure flooding detection.", "label": "Enable", "name": "enable"}, {"description": "Disable premature EAPOL-Failure flooding detection", "help": "Disable premature EAPOL-Failure flooding detection.", "label": "Disable", "name": "disable"}] | None = ...,
        eapol_pre_fail_thresh: int | None = ...,
        eapol_pre_fail_intv: int | None = ...,
        deauth_unknown_src_thresh: int | None = ...,
        windows_bridge: Literal[{"description": "Enable windows bridge detection", "help": "Enable windows bridge detection.", "label": "Enable", "name": "enable"}, {"description": "Disable windows bridge detection", "help": "Disable windows bridge detection.", "label": "Disable", "name": "disable"}] | None = ...,
        disassoc_broadcast: Literal[{"description": "Enable broadcast dis-association detection", "help": "Enable broadcast dis-association detection.", "label": "Enable", "name": "enable"}, {"description": "Disable broadcast dis-association detection", "help": "Disable broadcast dis-association detection.", "label": "Disable", "name": "disable"}] | None = ...,
        ap_spoofing: Literal[{"description": "Enable AP spoofing detection", "help": "Enable AP spoofing detection.", "label": "Enable", "name": "enable"}, {"description": "Disable AP spoofing detection", "help": "Disable AP spoofing detection.", "label": "Disable", "name": "disable"}] | None = ...,
        chan_based_mitm: Literal[{"description": "Enable channel based mitm detection", "help": "Enable channel based mitm detection.", "label": "Enable", "name": "enable"}, {"description": "Disable channel based mitm detection", "help": "Disable channel based mitm detection.", "label": "Disable", "name": "disable"}] | None = ...,
        adhoc_valid_ssid: Literal[{"description": "Enable adhoc using valid SSID detection", "help": "Enable adhoc using valid SSID detection.", "label": "Enable", "name": "enable"}, {"description": "Disable adhoc using valid SSID detection", "help": "Disable adhoc using valid SSID detection.", "label": "Disable", "name": "disable"}] | None = ...,
        adhoc_network: Literal[{"description": "Enable adhoc network detection", "help": "Enable adhoc network detection.", "label": "Enable", "name": "enable"}, {"description": "Disable adhoc network detection", "help": "Disable adhoc network detection.", "label": "Disable", "name": "disable"}] | None = ...,
        eapol_key_overflow: Literal[{"description": "Enable overflow EAPOL key detection", "help": "Enable overflow EAPOL key detection.", "label": "Enable", "name": "enable"}, {"description": "Disable overflow EAPOL key detection", "help": "Disable overflow EAPOL key detection.", "label": "Disable", "name": "disable"}] | None = ...,
        ap_impersonation: Literal[{"description": "Enable AP impersonation detection", "help": "Enable AP impersonation detection.", "label": "Enable", "name": "enable"}, {"description": "Disable AP impersonation detection", "help": "Disable AP impersonation detection.", "label": "Disable", "name": "disable"}] | None = ...,
        invalid_addr_combination: Literal[{"description": "Enable invalid address combination detection", "help": "Enable invalid address combination detection.", "label": "Enable", "name": "enable"}, {"description": "Disable invalid address combination detection", "help": "Disable invalid address combination detection.", "label": "Disable", "name": "disable"}] | None = ...,
        beacon_wrong_channel: Literal[{"description": "Enable beacon wrong channel detection", "help": "Enable beacon wrong channel detection.", "label": "Enable", "name": "enable"}, {"description": "Disable beacon wrong channel detection", "help": "Disable beacon wrong channel detection.", "label": "Disable", "name": "disable"}] | None = ...,
        ht_greenfield: Literal[{"description": "Enable HT greenfield detection", "help": "Enable HT greenfield detection.", "label": "Enable", "name": "enable"}, {"description": "Disable HT greenfield detection", "help": "Disable HT greenfield detection.", "label": "Disable", "name": "disable"}] | None = ...,
        overflow_ie: Literal[{"description": "Enable overflow IE detection", "help": "Enable overflow IE detection.", "label": "Enable", "name": "enable"}, {"description": "Disable overflow IE detection", "help": "Disable overflow IE detection.", "label": "Disable", "name": "disable"}] | None = ...,
        malformed_ht_ie: Literal[{"description": "Enable malformed HT IE detection", "help": "Enable malformed HT IE detection.", "label": "Enable", "name": "enable"}, {"description": "Disable malformed HT IE detection", "help": "Disable malformed HT IE detection.", "label": "Disable", "name": "disable"}] | None = ...,
        malformed_auth: Literal[{"description": "Enable malformed auth frame detection", "help": "Enable malformed auth frame detection.", "label": "Enable", "name": "enable"}, {"description": "Disable malformed auth frame detection", "help": "Disable malformed auth frame detection.", "label": "Disable", "name": "disable"}] | None = ...,
        malformed_association: Literal[{"description": "Enable malformed association request detection", "help": "Enable malformed association request detection.", "label": "Enable", "name": "enable"}, {"description": "Disable malformed association request detection", "help": "Disable malformed association request detection.", "label": "Disable", "name": "disable"}] | None = ...,
        ht_40mhz_intolerance: Literal[{"description": "Enable HT 40 MHz intolerance detection", "help": "Enable HT 40 MHz intolerance detection.", "label": "Enable", "name": "enable"}, {"description": "Disable HT 40 MHz intolerance detection", "help": "Disable HT 40 MHz intolerance detection.", "label": "Disable", "name": "disable"}] | None = ...,
        valid_ssid_misuse: Literal[{"description": "Enable valid SSID misuse detection", "help": "Enable valid SSID misuse detection.", "label": "Enable", "name": "enable"}, {"description": "Disable valid SSID misuse detection", "help": "Disable valid SSID misuse detection.", "label": "Disable", "name": "disable"}] | None = ...,
        valid_client_misassociation: Literal[{"description": "Enable valid client misassociation detection", "help": "Enable valid client misassociation detection.", "label": "Enable", "name": "enable"}, {"description": "Disable valid client misassociation detection", "help": "Disable valid client misassociation detection.", "label": "Disable", "name": "disable"}] | None = ...,
        hotspotter_attack: Literal[{"description": "Enable hotspotter attack detection", "help": "Enable hotspotter attack detection.", "label": "Enable", "name": "enable"}, {"description": "Disable hotspotter attack detection", "help": "Disable hotspotter attack detection.", "label": "Disable", "name": "disable"}] | None = ...,
        pwsave_dos_attack: Literal[{"description": "Enable power save DOS attack detection", "help": "Enable power save DOS attack detection.", "label": "Enable", "name": "enable"}, {"description": "Disable power save DOS attack detection", "help": "Disable power save DOS attack detection.", "label": "Disable", "name": "disable"}] | None = ...,
        omerta_attack: Literal[{"description": "Enable omerta attack detection", "help": "Enable omerta attack detection.", "label": "Enable", "name": "enable"}, {"description": "Disable omerta attack detection", "help": "Disable omerta attack detection.", "label": "Disable", "name": "disable"}] | None = ...,
        disconnect_station: Literal[{"description": "Enable disconnect station detection", "help": "Enable disconnect station detection.", "label": "Enable", "name": "enable"}, {"description": "Disable disconnect station detection", "help": "Disable disconnect station detection.", "label": "Disable", "name": "disable"}] | None = ...,
        unencrypted_valid: Literal[{"description": "Enable unencrypted valid detection", "help": "Enable unencrypted valid detection.", "label": "Enable", "name": "enable"}, {"description": "Disable unencrypted valid detection", "help": "Disable unencrypted valid detection.", "label": "Disable", "name": "disable"}] | None = ...,
        fata_jack: Literal[{"description": "Enable FATA-Jack detection", "help": "Enable FATA-Jack detection.", "label": "Enable", "name": "enable"}, {"description": "Disable FATA-Jack detection", "help": "Disable FATA-Jack detection.", "label": "Disable", "name": "disable"}] | None = ...,
        risky_encryption: Literal[{"description": "Enable Risky Encryption detection", "help": "Enable Risky Encryption detection.", "label": "Enable", "name": "enable"}, {"description": "Disable Risky Encryption detection", "help": "Disable Risky Encryption detection.", "label": "Disable", "name": "disable"}] | None = ...,
        fuzzed_beacon: Literal[{"description": "Enable fuzzed beacon detection", "help": "Enable fuzzed beacon detection.", "label": "Enable", "name": "enable"}, {"description": "Disable fuzzed beacon detection", "help": "Disable fuzzed beacon detection.", "label": "Disable", "name": "disable"}] | None = ...,
        fuzzed_probe_request: Literal[{"description": "Enable fuzzed probe request detection", "help": "Enable fuzzed probe request detection.", "label": "Enable", "name": "enable"}, {"description": "Disable fuzzed probe request detection", "help": "Disable fuzzed probe request detection.", "label": "Disable", "name": "disable"}] | None = ...,
        fuzzed_probe_response: Literal[{"description": "Enable fuzzed probe response detection", "help": "Enable fuzzed probe response detection.", "label": "Enable", "name": "enable"}, {"description": "Disable fuzzed probe response detection", "help": "Disable fuzzed probe response detection.", "label": "Disable", "name": "disable"}] | None = ...,
        air_jack: Literal[{"description": "Enable AirJack detection", "help": "Enable AirJack detection.", "label": "Enable", "name": "enable"}, {"description": "Disable AirJack detection", "help": "Disable AirJack detection.", "label": "Disable", "name": "disable"}] | None = ...,
        wpa_ft_attack: Literal[{"description": "Enable WPA FT attack detection", "help": "Enable WPA FT attack detection.", "label": "Enable", "name": "enable"}, {"description": "Disable WPA FT attack detection", "help": "Disable WPA FT attack detection.", "label": "Disable", "name": "disable"}] | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: WidsProfilePayload | None = ...,
        name: str | None = ...,
        comment: str | None = ...,
        sensor_mode: Literal[{"description": "Disable the scan", "help": "Disable the scan.", "label": "Disable", "name": "disable"}, {"description": "Enable the scan and monitor foreign channels", "help": "Enable the scan and monitor foreign channels. Foreign channels are all other available channels than the current operating channel.", "label": "Foreign", "name": "foreign"}, {"description": "Enable the scan and monitor both foreign and home channels", "help": "Enable the scan and monitor both foreign and home channels. Select this option to monitor all WiFi channels.", "label": "Both", "name": "both"}] | None = ...,
        ap_scan: Literal[{"description": "Disable rogue AP detection", "help": "Disable rogue AP detection.", "label": "Disable", "name": "disable"}, {"description": "Enable rogue AP detection", "help": "Enable rogue AP detection.", "label": "Enable", "name": "enable"}] | None = ...,
        ap_scan_channel_list_2G_5G: list[dict[str, Any]] | None = ...,
        ap_scan_channel_list_6G: list[dict[str, Any]] | None = ...,
        ap_bgscan_period: int | None = ...,
        ap_bgscan_intv: int | None = ...,
        ap_bgscan_duration: int | None = ...,
        ap_bgscan_idle: int | None = ...,
        ap_bgscan_report_intv: int | None = ...,
        ap_bgscan_disable_schedules: list[dict[str, Any]] | None = ...,
        ap_fgscan_report_intv: int | None = ...,
        ap_scan_passive: Literal[{"description": "Passive scanning on all channels", "help": "Passive scanning on all channels.", "label": "Enable", "name": "enable"}, {"description": "Passive scanning only on DFS channels", "help": "Passive scanning only on DFS channels.", "label": "Disable", "name": "disable"}] | None = ...,
        ap_scan_threshold: str | None = ...,
        ap_auto_suppress: Literal[{"description": "Enable on-wire rogue AP auto-suppression", "help": "Enable on-wire rogue AP auto-suppression.", "label": "Enable", "name": "enable"}, {"description": "Disable on-wire rogue AP auto-suppression", "help": "Disable on-wire rogue AP auto-suppression.", "label": "Disable", "name": "disable"}] | None = ...,
        wireless_bridge: Literal[{"description": "Enable wireless bridge detection", "help": "Enable wireless bridge detection.", "label": "Enable", "name": "enable"}, {"description": "Disable wireless bridge detection", "help": "Disable wireless bridge detection.", "label": "Disable", "name": "disable"}] | None = ...,
        deauth_broadcast: Literal[{"description": "Enable broadcast de-authentication detection", "help": "Enable broadcast de-authentication detection.", "label": "Enable", "name": "enable"}, {"description": "Disable broadcast de-authentication detection", "help": "Disable broadcast de-authentication detection.", "label": "Disable", "name": "disable"}] | None = ...,
        null_ssid_probe_resp: Literal[{"description": "Enable null SSID probe resp detection", "help": "Enable null SSID probe resp detection.", "label": "Enable", "name": "enable"}, {"description": "Disable null SSID probe resp detection", "help": "Disable null SSID probe resp detection.", "label": "Disable", "name": "disable"}] | None = ...,
        long_duration_attack: Literal[{"description": "Enable long duration attack detection", "help": "Enable long duration attack detection.", "label": "Enable", "name": "enable"}, {"description": "Disable long duration attack detection", "help": "Disable long duration attack detection.", "label": "Disable", "name": "disable"}] | None = ...,
        long_duration_thresh: int | None = ...,
        invalid_mac_oui: Literal[{"description": "Enable invalid MAC OUI detection", "help": "Enable invalid MAC OUI detection.", "label": "Enable", "name": "enable"}, {"description": "Disable invalid MAC OUI detection", "help": "Disable invalid MAC OUI detection.", "label": "Disable", "name": "disable"}] | None = ...,
        weak_wep_iv: Literal[{"description": "Enable weak WEP IV detection", "help": "Enable weak WEP IV detection.", "label": "Enable", "name": "enable"}, {"description": "Disable weak WEP IV detection", "help": "Disable weak WEP IV detection.", "label": "Disable", "name": "disable"}] | None = ...,
        auth_frame_flood: Literal[{"description": "Enable authentication frame flooding detection", "help": "Enable authentication frame flooding detection.", "label": "Enable", "name": "enable"}, {"description": "Disable authentication frame flooding detection", "help": "Disable authentication frame flooding detection.", "label": "Disable", "name": "disable"}] | None = ...,
        auth_flood_time: int | None = ...,
        auth_flood_thresh: int | None = ...,
        assoc_frame_flood: Literal[{"description": "Enable association frame flooding detection", "help": "Enable association frame flooding detection.", "label": "Enable", "name": "enable"}, {"description": "Disable association frame flooding detection", "help": "Disable association frame flooding detection.", "label": "Disable", "name": "disable"}] | None = ...,
        assoc_flood_time: int | None = ...,
        assoc_flood_thresh: int | None = ...,
        reassoc_flood: Literal[{"description": "Enable reassociation flood detection", "help": "Enable reassociation flood detection.", "label": "Enable", "name": "enable"}, {"description": "Disable reassociation flood detection", "help": "Disable reassociation flood detection.", "label": "Disable", "name": "disable"}] | None = ...,
        reassoc_flood_time: int | None = ...,
        reassoc_flood_thresh: int | None = ...,
        probe_flood: Literal[{"description": "Enable probe flood detection", "help": "Enable probe flood detection.", "label": "Enable", "name": "enable"}, {"description": "Disable probe flood detection", "help": "Disable probe flood detection.", "label": "Disable", "name": "disable"}] | None = ...,
        probe_flood_time: int | None = ...,
        probe_flood_thresh: int | None = ...,
        bcn_flood: Literal[{"description": "Enable bcn flood detection", "help": "Enable bcn flood detection.", "label": "Enable", "name": "enable"}, {"description": "Disable bcn flood detection", "help": "Disable bcn flood detection.", "label": "Disable", "name": "disable"}] | None = ...,
        bcn_flood_time: int | None = ...,
        bcn_flood_thresh: int | None = ...,
        rts_flood: Literal[{"description": "Enable rts flood detection", "help": "Enable rts flood detection.", "label": "Enable", "name": "enable"}, {"description": "Disable rts flood detection", "help": "Disable rts flood detection.", "label": "Disable", "name": "disable"}] | None = ...,
        rts_flood_time: int | None = ...,
        rts_flood_thresh: int | None = ...,
        cts_flood: Literal[{"description": "Enable cts flood detection", "help": "Enable cts flood detection.", "label": "Enable", "name": "enable"}, {"description": "Disable cts flood detection", "help": "Disable cts flood detection.", "label": "Disable", "name": "disable"}] | None = ...,
        cts_flood_time: int | None = ...,
        cts_flood_thresh: int | None = ...,
        client_flood: Literal[{"description": "Enable client flood detection", "help": "Enable client flood detection.", "label": "Enable", "name": "enable"}, {"description": "Disable client flood detection", "help": "Disable client flood detection.", "label": "Disable", "name": "disable"}] | None = ...,
        client_flood_time: int | None = ...,
        client_flood_thresh: int | None = ...,
        block_ack_flood: Literal[{"description": "Enable block_ack flood detection", "help": "Enable block_ack flood detection.", "label": "Enable", "name": "enable"}, {"description": "Disable block_ack flood detection", "help": "Disable block_ack flood detection.", "label": "Disable", "name": "disable"}] | None = ...,
        block_ack_flood_time: int | None = ...,
        block_ack_flood_thresh: int | None = ...,
        pspoll_flood: Literal[{"description": "Enable pspoll flood detection", "help": "Enable pspoll flood detection.", "label": "Enable", "name": "enable"}, {"description": "Disable pspoll flood detection", "help": "Disable pspoll flood detection.", "label": "Disable", "name": "disable"}] | None = ...,
        pspoll_flood_time: int | None = ...,
        pspoll_flood_thresh: int | None = ...,
        netstumbler: Literal[{"description": "Enable netstumbler detection", "help": "Enable netstumbler detection.", "label": "Enable", "name": "enable"}, {"description": "Disable netstumbler detection", "help": "Disable netstumbler detection.", "label": "Disable", "name": "disable"}] | None = ...,
        netstumbler_time: int | None = ...,
        netstumbler_thresh: int | None = ...,
        wellenreiter: Literal[{"description": "Enable wellenreiter detection", "help": "Enable wellenreiter detection.", "label": "Enable", "name": "enable"}, {"description": "Disable wellenreiter detection", "help": "Disable wellenreiter detection.", "label": "Disable", "name": "disable"}] | None = ...,
        wellenreiter_time: int | None = ...,
        wellenreiter_thresh: int | None = ...,
        spoofed_deauth: Literal[{"description": "Enable spoofed de-authentication attack detection", "help": "Enable spoofed de-authentication attack detection.", "label": "Enable", "name": "enable"}, {"description": "Disable spoofed de-authentication attack detection", "help": "Disable spoofed de-authentication attack detection.", "label": "Disable", "name": "disable"}] | None = ...,
        asleap_attack: Literal[{"description": "Enable asleap attack detection", "help": "Enable asleap attack detection.", "label": "Enable", "name": "enable"}, {"description": "Disable asleap attack detection", "help": "Disable asleap attack detection.", "label": "Disable", "name": "disable"}] | None = ...,
        eapol_start_flood: Literal[{"description": "Enable EAPOL-Start flooding detection", "help": "Enable EAPOL-Start flooding detection.", "label": "Enable", "name": "enable"}, {"description": "Disable EAPOL-Start flooding detection", "help": "Disable EAPOL-Start flooding detection.", "label": "Disable", "name": "disable"}] | None = ...,
        eapol_start_thresh: int | None = ...,
        eapol_start_intv: int | None = ...,
        eapol_logoff_flood: Literal[{"description": "Enable EAPOL-Logoff flooding detection", "help": "Enable EAPOL-Logoff flooding detection.", "label": "Enable", "name": "enable"}, {"description": "Disable EAPOL-Logoff flooding detection", "help": "Disable EAPOL-Logoff flooding detection.", "label": "Disable", "name": "disable"}] | None = ...,
        eapol_logoff_thresh: int | None = ...,
        eapol_logoff_intv: int | None = ...,
        eapol_succ_flood: Literal[{"description": "Enable EAPOL-Success flooding detection", "help": "Enable EAPOL-Success flooding detection.", "label": "Enable", "name": "enable"}, {"description": "Disable EAPOL-Success flooding detection", "help": "Disable EAPOL-Success flooding detection.", "label": "Disable", "name": "disable"}] | None = ...,
        eapol_succ_thresh: int | None = ...,
        eapol_succ_intv: int | None = ...,
        eapol_fail_flood: Literal[{"description": "Enable EAPOL-Failure flooding detection", "help": "Enable EAPOL-Failure flooding detection.", "label": "Enable", "name": "enable"}, {"description": "Disable EAPOL-Failure flooding detection", "help": "Disable EAPOL-Failure flooding detection.", "label": "Disable", "name": "disable"}] | None = ...,
        eapol_fail_thresh: int | None = ...,
        eapol_fail_intv: int | None = ...,
        eapol_pre_succ_flood: Literal[{"description": "Enable premature EAPOL-Success flooding detection", "help": "Enable premature EAPOL-Success flooding detection.", "label": "Enable", "name": "enable"}, {"description": "Disable premature EAPOL-Success flooding detection", "help": "Disable premature EAPOL-Success flooding detection.", "label": "Disable", "name": "disable"}] | None = ...,
        eapol_pre_succ_thresh: int | None = ...,
        eapol_pre_succ_intv: int | None = ...,
        eapol_pre_fail_flood: Literal[{"description": "Enable premature EAPOL-Failure flooding detection", "help": "Enable premature EAPOL-Failure flooding detection.", "label": "Enable", "name": "enable"}, {"description": "Disable premature EAPOL-Failure flooding detection", "help": "Disable premature EAPOL-Failure flooding detection.", "label": "Disable", "name": "disable"}] | None = ...,
        eapol_pre_fail_thresh: int | None = ...,
        eapol_pre_fail_intv: int | None = ...,
        deauth_unknown_src_thresh: int | None = ...,
        windows_bridge: Literal[{"description": "Enable windows bridge detection", "help": "Enable windows bridge detection.", "label": "Enable", "name": "enable"}, {"description": "Disable windows bridge detection", "help": "Disable windows bridge detection.", "label": "Disable", "name": "disable"}] | None = ...,
        disassoc_broadcast: Literal[{"description": "Enable broadcast dis-association detection", "help": "Enable broadcast dis-association detection.", "label": "Enable", "name": "enable"}, {"description": "Disable broadcast dis-association detection", "help": "Disable broadcast dis-association detection.", "label": "Disable", "name": "disable"}] | None = ...,
        ap_spoofing: Literal[{"description": "Enable AP spoofing detection", "help": "Enable AP spoofing detection.", "label": "Enable", "name": "enable"}, {"description": "Disable AP spoofing detection", "help": "Disable AP spoofing detection.", "label": "Disable", "name": "disable"}] | None = ...,
        chan_based_mitm: Literal[{"description": "Enable channel based mitm detection", "help": "Enable channel based mitm detection.", "label": "Enable", "name": "enable"}, {"description": "Disable channel based mitm detection", "help": "Disable channel based mitm detection.", "label": "Disable", "name": "disable"}] | None = ...,
        adhoc_valid_ssid: Literal[{"description": "Enable adhoc using valid SSID detection", "help": "Enable adhoc using valid SSID detection.", "label": "Enable", "name": "enable"}, {"description": "Disable adhoc using valid SSID detection", "help": "Disable adhoc using valid SSID detection.", "label": "Disable", "name": "disable"}] | None = ...,
        adhoc_network: Literal[{"description": "Enable adhoc network detection", "help": "Enable adhoc network detection.", "label": "Enable", "name": "enable"}, {"description": "Disable adhoc network detection", "help": "Disable adhoc network detection.", "label": "Disable", "name": "disable"}] | None = ...,
        eapol_key_overflow: Literal[{"description": "Enable overflow EAPOL key detection", "help": "Enable overflow EAPOL key detection.", "label": "Enable", "name": "enable"}, {"description": "Disable overflow EAPOL key detection", "help": "Disable overflow EAPOL key detection.", "label": "Disable", "name": "disable"}] | None = ...,
        ap_impersonation: Literal[{"description": "Enable AP impersonation detection", "help": "Enable AP impersonation detection.", "label": "Enable", "name": "enable"}, {"description": "Disable AP impersonation detection", "help": "Disable AP impersonation detection.", "label": "Disable", "name": "disable"}] | None = ...,
        invalid_addr_combination: Literal[{"description": "Enable invalid address combination detection", "help": "Enable invalid address combination detection.", "label": "Enable", "name": "enable"}, {"description": "Disable invalid address combination detection", "help": "Disable invalid address combination detection.", "label": "Disable", "name": "disable"}] | None = ...,
        beacon_wrong_channel: Literal[{"description": "Enable beacon wrong channel detection", "help": "Enable beacon wrong channel detection.", "label": "Enable", "name": "enable"}, {"description": "Disable beacon wrong channel detection", "help": "Disable beacon wrong channel detection.", "label": "Disable", "name": "disable"}] | None = ...,
        ht_greenfield: Literal[{"description": "Enable HT greenfield detection", "help": "Enable HT greenfield detection.", "label": "Enable", "name": "enable"}, {"description": "Disable HT greenfield detection", "help": "Disable HT greenfield detection.", "label": "Disable", "name": "disable"}] | None = ...,
        overflow_ie: Literal[{"description": "Enable overflow IE detection", "help": "Enable overflow IE detection.", "label": "Enable", "name": "enable"}, {"description": "Disable overflow IE detection", "help": "Disable overflow IE detection.", "label": "Disable", "name": "disable"}] | None = ...,
        malformed_ht_ie: Literal[{"description": "Enable malformed HT IE detection", "help": "Enable malformed HT IE detection.", "label": "Enable", "name": "enable"}, {"description": "Disable malformed HT IE detection", "help": "Disable malformed HT IE detection.", "label": "Disable", "name": "disable"}] | None = ...,
        malformed_auth: Literal[{"description": "Enable malformed auth frame detection", "help": "Enable malformed auth frame detection.", "label": "Enable", "name": "enable"}, {"description": "Disable malformed auth frame detection", "help": "Disable malformed auth frame detection.", "label": "Disable", "name": "disable"}] | None = ...,
        malformed_association: Literal[{"description": "Enable malformed association request detection", "help": "Enable malformed association request detection.", "label": "Enable", "name": "enable"}, {"description": "Disable malformed association request detection", "help": "Disable malformed association request detection.", "label": "Disable", "name": "disable"}] | None = ...,
        ht_40mhz_intolerance: Literal[{"description": "Enable HT 40 MHz intolerance detection", "help": "Enable HT 40 MHz intolerance detection.", "label": "Enable", "name": "enable"}, {"description": "Disable HT 40 MHz intolerance detection", "help": "Disable HT 40 MHz intolerance detection.", "label": "Disable", "name": "disable"}] | None = ...,
        valid_ssid_misuse: Literal[{"description": "Enable valid SSID misuse detection", "help": "Enable valid SSID misuse detection.", "label": "Enable", "name": "enable"}, {"description": "Disable valid SSID misuse detection", "help": "Disable valid SSID misuse detection.", "label": "Disable", "name": "disable"}] | None = ...,
        valid_client_misassociation: Literal[{"description": "Enable valid client misassociation detection", "help": "Enable valid client misassociation detection.", "label": "Enable", "name": "enable"}, {"description": "Disable valid client misassociation detection", "help": "Disable valid client misassociation detection.", "label": "Disable", "name": "disable"}] | None = ...,
        hotspotter_attack: Literal[{"description": "Enable hotspotter attack detection", "help": "Enable hotspotter attack detection.", "label": "Enable", "name": "enable"}, {"description": "Disable hotspotter attack detection", "help": "Disable hotspotter attack detection.", "label": "Disable", "name": "disable"}] | None = ...,
        pwsave_dos_attack: Literal[{"description": "Enable power save DOS attack detection", "help": "Enable power save DOS attack detection.", "label": "Enable", "name": "enable"}, {"description": "Disable power save DOS attack detection", "help": "Disable power save DOS attack detection.", "label": "Disable", "name": "disable"}] | None = ...,
        omerta_attack: Literal[{"description": "Enable omerta attack detection", "help": "Enable omerta attack detection.", "label": "Enable", "name": "enable"}, {"description": "Disable omerta attack detection", "help": "Disable omerta attack detection.", "label": "Disable", "name": "disable"}] | None = ...,
        disconnect_station: Literal[{"description": "Enable disconnect station detection", "help": "Enable disconnect station detection.", "label": "Enable", "name": "enable"}, {"description": "Disable disconnect station detection", "help": "Disable disconnect station detection.", "label": "Disable", "name": "disable"}] | None = ...,
        unencrypted_valid: Literal[{"description": "Enable unencrypted valid detection", "help": "Enable unencrypted valid detection.", "label": "Enable", "name": "enable"}, {"description": "Disable unencrypted valid detection", "help": "Disable unencrypted valid detection.", "label": "Disable", "name": "disable"}] | None = ...,
        fata_jack: Literal[{"description": "Enable FATA-Jack detection", "help": "Enable FATA-Jack detection.", "label": "Enable", "name": "enable"}, {"description": "Disable FATA-Jack detection", "help": "Disable FATA-Jack detection.", "label": "Disable", "name": "disable"}] | None = ...,
        risky_encryption: Literal[{"description": "Enable Risky Encryption detection", "help": "Enable Risky Encryption detection.", "label": "Enable", "name": "enable"}, {"description": "Disable Risky Encryption detection", "help": "Disable Risky Encryption detection.", "label": "Disable", "name": "disable"}] | None = ...,
        fuzzed_beacon: Literal[{"description": "Enable fuzzed beacon detection", "help": "Enable fuzzed beacon detection.", "label": "Enable", "name": "enable"}, {"description": "Disable fuzzed beacon detection", "help": "Disable fuzzed beacon detection.", "label": "Disable", "name": "disable"}] | None = ...,
        fuzzed_probe_request: Literal[{"description": "Enable fuzzed probe request detection", "help": "Enable fuzzed probe request detection.", "label": "Enable", "name": "enable"}, {"description": "Disable fuzzed probe request detection", "help": "Disable fuzzed probe request detection.", "label": "Disable", "name": "disable"}] | None = ...,
        fuzzed_probe_response: Literal[{"description": "Enable fuzzed probe response detection", "help": "Enable fuzzed probe response detection.", "label": "Enable", "name": "enable"}, {"description": "Disable fuzzed probe response detection", "help": "Disable fuzzed probe response detection.", "label": "Disable", "name": "disable"}] | None = ...,
        air_jack: Literal[{"description": "Enable AirJack detection", "help": "Enable AirJack detection.", "label": "Enable", "name": "enable"}, {"description": "Disable AirJack detection", "help": "Disable AirJack detection.", "label": "Disable", "name": "disable"}] | None = ...,
        wpa_ft_attack: Literal[{"description": "Enable WPA FT attack detection", "help": "Enable WPA FT attack detection.", "label": "Enable", "name": "enable"}, {"description": "Disable WPA FT attack detection", "help": "Disable WPA FT attack detection.", "label": "Disable", "name": "disable"}] | None = ...,
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
        payload_dict: WidsProfilePayload | None = ...,
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
    "WidsProfile",
    "WidsProfilePayload",
]