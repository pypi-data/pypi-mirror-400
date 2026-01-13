from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class HsProfilePayload(TypedDict, total=False):
    """
    Type hints for wireless_controller/hotspot20/hs_profile payload fields.
    
    Configure hotspot profile.
    
    **Related Resources:**

    Dependencies (resources this endpoint references):
        - :class:`~.wireless-controller.hotspot20.anqp-3gpp-cellular.Anqp3GppCellularEndpoint` (via: 3gpp-plmn)
        - :class:`~.wireless-controller.hotspot20.anqp-ip-address-type.AnqpIpAddressTypeEndpoint` (via: ip-addr-type)
        - :class:`~.wireless-controller.hotspot20.anqp-nai-realm.AnqpNaiRealmEndpoint` (via: nai-realm)
        - :class:`~.wireless-controller.hotspot20.anqp-network-auth-type.AnqpNetworkAuthTypeEndpoint` (via: network-auth)
        - :class:`~.wireless-controller.hotspot20.anqp-roaming-consortium.AnqpRoamingConsortiumEndpoint` (via: roaming-consortium)
        - :class:`~.wireless-controller.hotspot20.anqp-venue-name.AnqpVenueNameEndpoint` (via: venue-name)
        - :class:`~.wireless-controller.hotspot20.anqp-venue-url.AnqpVenueUrlEndpoint` (via: venue-url)
        - :class:`~.wireless-controller.hotspot20.h2qp-advice-of-charge.H2QpAdviceOfChargeEndpoint` (via: advice-of-charge)
        - :class:`~.wireless-controller.hotspot20.h2qp-conn-capability.H2QpConnCapabilityEndpoint` (via: conn-cap)
        - :class:`~.wireless-controller.hotspot20.h2qp-operator-name.H2QpOperatorNameEndpoint` (via: oper-friendly-name)
        - ... and 5 more dependencies

    **Usage:**
        payload: HsProfilePayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    name: NotRequired[str]  # Hotspot profile name.
    release: NotRequired[int]  # Hotspot 2.0 Release number (1, 2, 3, default = 2).
    access_network_type: NotRequired[Literal[{"description": "Private network", "help": "Private network.", "label": "Private Network", "name": "private-network"}, {"description": "Private network with guest access", "help": "Private network with guest access.", "label": "Private Network With Guest Access", "name": "private-network-with-guest-access"}, {"description": "Chargeable public network", "help": "Chargeable public network.", "label": "Chargeable Public Network", "name": "chargeable-public-network"}, {"description": "Free public network", "help": "Free public network.", "label": "Free Public Network", "name": "free-public-network"}, {"description": "Personal devices network", "help": "Personal devices network.", "label": "Personal Device Network", "name": "personal-device-network"}, {"description": "Emergency services only network", "help": "Emergency services only network.", "label": "Emergency Services Only Network", "name": "emergency-services-only-network"}, {"description": "Test or experimental", "help": "Test or experimental.", "label": "Test Or Experimental", "name": "test-or-experimental"}, {"description": "Wildcard", "help": "Wildcard.", "label": "Wildcard", "name": "wildcard"}]]  # Access network type.
    access_network_internet: NotRequired[Literal[{"description": "Enable connectivity to the Internet", "help": "Enable connectivity to the Internet.", "label": "Enable", "name": "enable"}, {"description": "Disable connectivity to the Internet", "help": "Disable connectivity to the Internet.", "label": "Disable", "name": "disable"}]]  # Enable/disable connectivity to the Internet.
    access_network_asra: NotRequired[Literal[{"description": "Enable additional step required for access (ASRA)", "help": "Enable additional step required for access (ASRA).", "label": "Enable", "name": "enable"}, {"description": "Disable additional step required for access (ASRA)", "help": "Disable additional step required for access (ASRA).", "label": "Disable", "name": "disable"}]]  # Enable/disable additional step required for access (ASRA).
    access_network_esr: NotRequired[Literal[{"description": "Enable emergency services reachable (ESR)", "help": "Enable emergency services reachable (ESR).", "label": "Enable", "name": "enable"}, {"description": "Disable emergency services reachable (ESR)", "help": "Disable emergency services reachable (ESR).", "label": "Disable", "name": "disable"}]]  # Enable/disable emergency services reachable (ESR).
    access_network_uesa: NotRequired[Literal[{"description": "Enable unauthenticated emergency service accessible (UESA)", "help": "Enable unauthenticated emergency service accessible (UESA).", "label": "Enable", "name": "enable"}, {"description": "Disable unauthenticated emergency service accessible (UESA)", "help": "Disable unauthenticated emergency service accessible (UESA).", "label": "Disable", "name": "disable"}]]  # Enable/disable unauthenticated emergency service accessible 
    venue_group: NotRequired[Literal[{"description": "Unspecified", "help": "Unspecified.", "label": "Unspecified", "name": "unspecified"}, {"description": "Assembly", "help": "Assembly.", "label": "Assembly", "name": "assembly"}, {"description": "Business", "help": "Business.", "label": "Business", "name": "business"}, {"description": "Educational", "help": "Educational.", "label": "Educational", "name": "educational"}, {"description": "Factory and industrial", "help": "Factory and industrial.", "label": "Factory", "name": "factory"}, {"description": "Institutional", "help": "Institutional.", "label": "Institutional", "name": "institutional"}, {"description": "Mercantile", "help": "Mercantile.", "label": "Mercantile", "name": "mercantile"}, {"description": "Residential", "help": "Residential.", "label": "Residential", "name": "residential"}, {"description": "Storage", "help": "Storage.", "label": "Storage", "name": "storage"}, {"description": "Utility and miscellaneous", "help": "Utility and miscellaneous.", "label": "Utility", "name": "utility"}, {"description": "Vehicular", "help": "Vehicular.", "label": "Vehicular", "name": "vehicular"}, {"description": "Outdoor", "help": "Outdoor.", "label": "Outdoor", "name": "outdoor"}]]  # Venue group.
    venue_type: NotRequired[Literal[{"description": "Unspecified", "help": "Unspecified.", "label": "Unspecified", "name": "unspecified"}, {"description": "Arena", "help": "Arena.", "label": "Arena", "name": "arena"}, {"description": "Stadium", "help": "Stadium.", "label": "Stadium", "name": "stadium"}, {"description": "Passenger terminal", "help": "Passenger terminal.", "label": "Passenger Terminal", "name": "passenger-terminal"}, {"description": "Amphitheater", "help": "Amphitheater.", "label": "Amphitheater", "name": "amphitheater"}, {"description": "Amusement park", "help": "Amusement park.", "label": "Amusement Park", "name": "amusement-park"}, {"description": "Place of worship", "help": "Place of worship.", "label": "Place Of Worship", "name": "place-of-worship"}, {"description": "Convention center", "help": "Convention center.", "label": "Convention Center", "name": "convention-center"}, {"description": "Library", "help": "Library.", "label": "Library", "name": "library"}, {"description": "Museum", "help": "Museum.", "label": "Museum", "name": "museum"}, {"description": "Restaurant", "help": "Restaurant.", "label": "Restaurant", "name": "restaurant"}, {"description": "Theater", "help": "Theater.", "label": "Theater", "name": "theater"}, {"description": "Bar", "help": "Bar.", "label": "Bar", "name": "bar"}, {"description": "Coffee shop", "help": "Coffee shop.", "label": "Coffee Shop", "name": "coffee-shop"}, {"description": "Zoo or aquarium", "help": "Zoo or aquarium.", "label": "Zoo Or Aquarium", "name": "zoo-or-aquarium"}, {"description": "Emergency coordination center", "help": "Emergency coordination center.", "label": "Emergency Center", "name": "emergency-center"}, {"description": "Doctor or dentist office", "help": "Doctor or dentist office.", "label": "Doctor Office", "name": "doctor-office"}, {"description": "Bank", "help": "Bank.", "label": "Bank", "name": "bank"}, {"description": "Fire station", "help": "Fire station.", "label": "Fire Station", "name": "fire-station"}, {"description": "Police station", "help": "Police station.", "label": "Police Station", "name": "police-station"}, {"description": "Post office", "help": "Post office.", "label": "Post Office", "name": "post-office"}, {"description": "Professional office", "help": "Professional office.", "label": "Professional Office", "name": "professional-office"}, {"description": "Research and development facility", "help": "Research and development facility.", "label": "Research Facility", "name": "research-facility"}, {"description": "Attorney office", "help": "Attorney office.", "label": "Attorney Office", "name": "attorney-office"}, {"description": "Primary school", "help": "Primary school.", "label": "Primary School", "name": "primary-school"}, {"description": "Secondary school", "help": "Secondary school.", "label": "Secondary School", "name": "secondary-school"}, {"description": "University or college", "help": "University or college.", "label": "University Or College", "name": "university-or-college"}, {"description": "Factory", "help": "Factory.", "label": "Factory", "name": "factory"}, {"description": "Hospital", "help": "Hospital.", "label": "Hospital", "name": "hospital"}, {"description": "Long term care facility", "help": "Long term care facility.", "label": "Long Term Care Facility", "name": "long-term-care-facility"}, {"description": "Alcohol and drug rehabilitation center", "help": "Alcohol and drug rehabilitation center.", "label": "Rehab Center", "name": "rehab-center"}, {"description": "Group home", "help": "Group home.", "label": "Group Home", "name": "group-home"}, {"description": "Prison or jail", "help": "Prison or jail.", "label": "Prison Or Jail", "name": "prison-or-jail"}, {"description": "Retail store", "help": "Retail store.", "label": "Retail Store", "name": "retail-store"}, {"description": "Grocery market", "help": "Grocery market.", "label": "Grocery Market", "name": "grocery-market"}, {"description": "Auto service station", "help": "Auto service station.", "label": "Auto Service Station", "name": "auto-service-station"}, {"description": "Shopping mall", "help": "Shopping mall.", "label": "Shopping Mall", "name": "shopping-mall"}, {"description": "Gas station", "help": "Gas station.", "label": "Gas Station", "name": "gas-station"}, {"description": "Private residence", "help": "Private residence.", "label": "Private", "name": "private"}, {"description": "Hotel or motel", "help": "Hotel or motel.", "label": "Hotel Or Motel", "name": "hotel-or-motel"}, {"description": "Dormitory", "help": "Dormitory.", "label": "Dormitory", "name": "dormitory"}, {"description": "Boarding house", "help": "Boarding house.", "label": "Boarding House", "name": "boarding-house"}, {"description": "Automobile or truck", "help": "Automobile or truck.", "label": "Automobile", "name": "automobile"}, {"description": "Airplane", "help": "Airplane.", "label": "Airplane", "name": "airplane"}, {"description": "Bus", "help": "Bus.", "label": "Bus", "name": "bus"}, {"description": "Ferry", "help": "Ferry.", "label": "Ferry", "name": "ferry"}, {"description": "Ship or boat", "help": "Ship or boat.", "label": "Ship Or Boat", "name": "ship-or-boat"}, {"description": "Train", "help": "Train.", "label": "Train", "name": "train"}, {"description": "Motor bike", "help": "Motor bike.", "label": "Motor Bike", "name": "motor-bike"}, {"description": "Muni mesh network", "help": "Muni mesh network.", "label": "Muni Mesh Network", "name": "muni-mesh-network"}, {"description": "City park", "help": "City park.", "label": "City Park", "name": "city-park"}, {"description": "Rest area", "help": "Rest area.", "label": "Rest Area", "name": "rest-area"}, {"description": "Traffic control", "help": "Traffic control.", "label": "Traffic Control", "name": "traffic-control"}, {"description": "Bus stop", "help": "Bus stop.", "label": "Bus Stop", "name": "bus-stop"}, {"description": "Kiosk", "help": "Kiosk.", "label": "Kiosk", "name": "kiosk"}]]  # Venue type.
    hessid: NotRequired[str]  # Homogeneous extended service set identifier (HESSID).
    proxy_arp: NotRequired[Literal[{"description": "Enable Proxy ARP", "help": "Enable Proxy ARP.", "label": "Enable", "name": "enable"}, {"description": "Disable Proxy ARP", "help": "Disable Proxy ARP.", "label": "Disable", "name": "disable"}]]  # Enable/disable Proxy ARP.
    l2tif: NotRequired[Literal[{"description": "Enable Layer 2 traffic inspection and filtering", "help": "Enable Layer 2 traffic inspection and filtering.", "label": "Enable", "name": "enable"}, {"description": "Disable Layer 2 traffic inspection and filtering", "help": "Disable Layer 2 traffic inspection and filtering.", "label": "Disable", "name": "disable"}]]  # Enable/disable Layer 2 traffic inspection and filtering.
    pame_bi: NotRequired[Literal[{"description": "Disable Pre-Association Message Exchange BSSID Independent (PAME-BI)", "help": "Disable Pre-Association Message Exchange BSSID Independent (PAME-BI).", "label": "Disable", "name": "disable"}, {"description": "Enable Pre-Association Message Exchange BSSID Independent (PAME-BI)", "help": "Enable Pre-Association Message Exchange BSSID Independent (PAME-BI).", "label": "Enable", "name": "enable"}]]  # Enable/disable Pre-Association Message Exchange BSSID Indepe
    anqp_domain_id: NotRequired[int]  # ANQP Domain ID (0-65535).
    domain_name: NotRequired[str]  # Domain name.
    osu_ssid: NotRequired[str]  # Online sign up (OSU) SSID.
    gas_comeback_delay: NotRequired[int]  # GAS comeback delay (0 or 100 - 10000 milliseconds, default =
    gas_fragmentation_limit: NotRequired[int]  # GAS fragmentation limit (512 - 4096, default = 1024).
    dgaf: NotRequired[Literal[{"description": "Enable downstream group-addressed forwarding (DGAF)", "help": "Enable downstream group-addressed forwarding (DGAF).", "label": "Enable", "name": "enable"}, {"description": "Disable downstream group-addressed forwarding (DGAF)", "help": "Disable downstream group-addressed forwarding (DGAF).", "label": "Disable", "name": "disable"}]]  # Enable/disable downstream group-addressed forwarding (DGAF).
    deauth_request_timeout: NotRequired[int]  # Deauthentication request timeout (in seconds).
    wnm_sleep_mode: NotRequired[Literal[{"description": "Enable wireless network management (WNM) sleep mode", "help": "Enable wireless network management (WNM) sleep mode.", "label": "Enable", "name": "enable"}, {"description": "Disable wireless network management (WNM) sleep mode", "help": "Disable wireless network management (WNM) sleep mode.", "label": "Disable", "name": "disable"}]]  # Enable/disable wireless network management (WNM) sleep mode.
    bss_transition: NotRequired[Literal[{"description": "Enable basic service set (BSS) transition support", "help": "Enable basic service set (BSS) transition support.", "label": "Enable", "name": "enable"}, {"description": "Disable basic service set (BSS) transition support", "help": "Disable basic service set (BSS) transition support.", "label": "Disable", "name": "disable"}]]  # Enable/disable basic service set (BSS) transition Support.
    venue_name: NotRequired[str]  # Venue name.
    venue_url: NotRequired[str]  # Venue name.
    roaming_consortium: NotRequired[str]  # Roaming consortium list name.
    nai_realm: NotRequired[str]  # NAI realm list name.
    oper_friendly_name: NotRequired[str]  # Operator friendly name.
    oper_icon: NotRequired[str]  # Operator icon.
    advice_of_charge: NotRequired[str]  # Advice of charge.
    osu_provider_nai: NotRequired[str]  # OSU Provider NAI.
    terms_and_conditions: NotRequired[str]  # Terms and conditions.
    osu_provider: NotRequired[list[dict[str, Any]]]  # Manually selected list of OSU provider(s).
    wan_metrics: NotRequired[str]  # WAN metric name.
    network_auth: NotRequired[str]  # Network authentication name.
    x3gpp_plmn: NotRequired[str]  # 3GPP PLMN name.
    conn_cap: NotRequired[str]  # Connection capability name.
    qos_map: NotRequired[str]  # QoS MAP set ID.
    ip_addr_type: NotRequired[str]  # IP address type name.
    wba_open_roaming: NotRequired[Literal[{"description": "Disable WBA open roaming support", "help": "Disable WBA open roaming support.", "label": "Disable", "name": "disable"}, {"description": "Enable WBA open roaming support", "help": "Enable WBA open roaming support.", "label": "Enable", "name": "enable"}]]  # Enable/disable WBA open roaming support.
    wba_financial_clearing_provider: NotRequired[str]  # WBA ID of financial clearing provider.
    wba_data_clearing_provider: NotRequired[str]  # WBA ID of data clearing provider.
    wba_charging_currency: NotRequired[str]  # Three letter currency code.
    wba_charging_rate: NotRequired[int]  # Number of currency units per kilobyte.


class HsProfile:
    """
    Configure hotspot profile.
    
    Path: wireless_controller/hotspot20/hs_profile
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
        payload_dict: HsProfilePayload | None = ...,
        name: str | None = ...,
        release: int | None = ...,
        access_network_type: Literal[{"description": "Private network", "help": "Private network.", "label": "Private Network", "name": "private-network"}, {"description": "Private network with guest access", "help": "Private network with guest access.", "label": "Private Network With Guest Access", "name": "private-network-with-guest-access"}, {"description": "Chargeable public network", "help": "Chargeable public network.", "label": "Chargeable Public Network", "name": "chargeable-public-network"}, {"description": "Free public network", "help": "Free public network.", "label": "Free Public Network", "name": "free-public-network"}, {"description": "Personal devices network", "help": "Personal devices network.", "label": "Personal Device Network", "name": "personal-device-network"}, {"description": "Emergency services only network", "help": "Emergency services only network.", "label": "Emergency Services Only Network", "name": "emergency-services-only-network"}, {"description": "Test or experimental", "help": "Test or experimental.", "label": "Test Or Experimental", "name": "test-or-experimental"}, {"description": "Wildcard", "help": "Wildcard.", "label": "Wildcard", "name": "wildcard"}] | None = ...,
        access_network_internet: Literal[{"description": "Enable connectivity to the Internet", "help": "Enable connectivity to the Internet.", "label": "Enable", "name": "enable"}, {"description": "Disable connectivity to the Internet", "help": "Disable connectivity to the Internet.", "label": "Disable", "name": "disable"}] | None = ...,
        access_network_asra: Literal[{"description": "Enable additional step required for access (ASRA)", "help": "Enable additional step required for access (ASRA).", "label": "Enable", "name": "enable"}, {"description": "Disable additional step required for access (ASRA)", "help": "Disable additional step required for access (ASRA).", "label": "Disable", "name": "disable"}] | None = ...,
        access_network_esr: Literal[{"description": "Enable emergency services reachable (ESR)", "help": "Enable emergency services reachable (ESR).", "label": "Enable", "name": "enable"}, {"description": "Disable emergency services reachable (ESR)", "help": "Disable emergency services reachable (ESR).", "label": "Disable", "name": "disable"}] | None = ...,
        access_network_uesa: Literal[{"description": "Enable unauthenticated emergency service accessible (UESA)", "help": "Enable unauthenticated emergency service accessible (UESA).", "label": "Enable", "name": "enable"}, {"description": "Disable unauthenticated emergency service accessible (UESA)", "help": "Disable unauthenticated emergency service accessible (UESA).", "label": "Disable", "name": "disable"}] | None = ...,
        venue_group: Literal[{"description": "Unspecified", "help": "Unspecified.", "label": "Unspecified", "name": "unspecified"}, {"description": "Assembly", "help": "Assembly.", "label": "Assembly", "name": "assembly"}, {"description": "Business", "help": "Business.", "label": "Business", "name": "business"}, {"description": "Educational", "help": "Educational.", "label": "Educational", "name": "educational"}, {"description": "Factory and industrial", "help": "Factory and industrial.", "label": "Factory", "name": "factory"}, {"description": "Institutional", "help": "Institutional.", "label": "Institutional", "name": "institutional"}, {"description": "Mercantile", "help": "Mercantile.", "label": "Mercantile", "name": "mercantile"}, {"description": "Residential", "help": "Residential.", "label": "Residential", "name": "residential"}, {"description": "Storage", "help": "Storage.", "label": "Storage", "name": "storage"}, {"description": "Utility and miscellaneous", "help": "Utility and miscellaneous.", "label": "Utility", "name": "utility"}, {"description": "Vehicular", "help": "Vehicular.", "label": "Vehicular", "name": "vehicular"}, {"description": "Outdoor", "help": "Outdoor.", "label": "Outdoor", "name": "outdoor"}] | None = ...,
        venue_type: Literal[{"description": "Unspecified", "help": "Unspecified.", "label": "Unspecified", "name": "unspecified"}, {"description": "Arena", "help": "Arena.", "label": "Arena", "name": "arena"}, {"description": "Stadium", "help": "Stadium.", "label": "Stadium", "name": "stadium"}, {"description": "Passenger terminal", "help": "Passenger terminal.", "label": "Passenger Terminal", "name": "passenger-terminal"}, {"description": "Amphitheater", "help": "Amphitheater.", "label": "Amphitheater", "name": "amphitheater"}, {"description": "Amusement park", "help": "Amusement park.", "label": "Amusement Park", "name": "amusement-park"}, {"description": "Place of worship", "help": "Place of worship.", "label": "Place Of Worship", "name": "place-of-worship"}, {"description": "Convention center", "help": "Convention center.", "label": "Convention Center", "name": "convention-center"}, {"description": "Library", "help": "Library.", "label": "Library", "name": "library"}, {"description": "Museum", "help": "Museum.", "label": "Museum", "name": "museum"}, {"description": "Restaurant", "help": "Restaurant.", "label": "Restaurant", "name": "restaurant"}, {"description": "Theater", "help": "Theater.", "label": "Theater", "name": "theater"}, {"description": "Bar", "help": "Bar.", "label": "Bar", "name": "bar"}, {"description": "Coffee shop", "help": "Coffee shop.", "label": "Coffee Shop", "name": "coffee-shop"}, {"description": "Zoo or aquarium", "help": "Zoo or aquarium.", "label": "Zoo Or Aquarium", "name": "zoo-or-aquarium"}, {"description": "Emergency coordination center", "help": "Emergency coordination center.", "label": "Emergency Center", "name": "emergency-center"}, {"description": "Doctor or dentist office", "help": "Doctor or dentist office.", "label": "Doctor Office", "name": "doctor-office"}, {"description": "Bank", "help": "Bank.", "label": "Bank", "name": "bank"}, {"description": "Fire station", "help": "Fire station.", "label": "Fire Station", "name": "fire-station"}, {"description": "Police station", "help": "Police station.", "label": "Police Station", "name": "police-station"}, {"description": "Post office", "help": "Post office.", "label": "Post Office", "name": "post-office"}, {"description": "Professional office", "help": "Professional office.", "label": "Professional Office", "name": "professional-office"}, {"description": "Research and development facility", "help": "Research and development facility.", "label": "Research Facility", "name": "research-facility"}, {"description": "Attorney office", "help": "Attorney office.", "label": "Attorney Office", "name": "attorney-office"}, {"description": "Primary school", "help": "Primary school.", "label": "Primary School", "name": "primary-school"}, {"description": "Secondary school", "help": "Secondary school.", "label": "Secondary School", "name": "secondary-school"}, {"description": "University or college", "help": "University or college.", "label": "University Or College", "name": "university-or-college"}, {"description": "Factory", "help": "Factory.", "label": "Factory", "name": "factory"}, {"description": "Hospital", "help": "Hospital.", "label": "Hospital", "name": "hospital"}, {"description": "Long term care facility", "help": "Long term care facility.", "label": "Long Term Care Facility", "name": "long-term-care-facility"}, {"description": "Alcohol and drug rehabilitation center", "help": "Alcohol and drug rehabilitation center.", "label": "Rehab Center", "name": "rehab-center"}, {"description": "Group home", "help": "Group home.", "label": "Group Home", "name": "group-home"}, {"description": "Prison or jail", "help": "Prison or jail.", "label": "Prison Or Jail", "name": "prison-or-jail"}, {"description": "Retail store", "help": "Retail store.", "label": "Retail Store", "name": "retail-store"}, {"description": "Grocery market", "help": "Grocery market.", "label": "Grocery Market", "name": "grocery-market"}, {"description": "Auto service station", "help": "Auto service station.", "label": "Auto Service Station", "name": "auto-service-station"}, {"description": "Shopping mall", "help": "Shopping mall.", "label": "Shopping Mall", "name": "shopping-mall"}, {"description": "Gas station", "help": "Gas station.", "label": "Gas Station", "name": "gas-station"}, {"description": "Private residence", "help": "Private residence.", "label": "Private", "name": "private"}, {"description": "Hotel or motel", "help": "Hotel or motel.", "label": "Hotel Or Motel", "name": "hotel-or-motel"}, {"description": "Dormitory", "help": "Dormitory.", "label": "Dormitory", "name": "dormitory"}, {"description": "Boarding house", "help": "Boarding house.", "label": "Boarding House", "name": "boarding-house"}, {"description": "Automobile or truck", "help": "Automobile or truck.", "label": "Automobile", "name": "automobile"}, {"description": "Airplane", "help": "Airplane.", "label": "Airplane", "name": "airplane"}, {"description": "Bus", "help": "Bus.", "label": "Bus", "name": "bus"}, {"description": "Ferry", "help": "Ferry.", "label": "Ferry", "name": "ferry"}, {"description": "Ship or boat", "help": "Ship or boat.", "label": "Ship Or Boat", "name": "ship-or-boat"}, {"description": "Train", "help": "Train.", "label": "Train", "name": "train"}, {"description": "Motor bike", "help": "Motor bike.", "label": "Motor Bike", "name": "motor-bike"}, {"description": "Muni mesh network", "help": "Muni mesh network.", "label": "Muni Mesh Network", "name": "muni-mesh-network"}, {"description": "City park", "help": "City park.", "label": "City Park", "name": "city-park"}, {"description": "Rest area", "help": "Rest area.", "label": "Rest Area", "name": "rest-area"}, {"description": "Traffic control", "help": "Traffic control.", "label": "Traffic Control", "name": "traffic-control"}, {"description": "Bus stop", "help": "Bus stop.", "label": "Bus Stop", "name": "bus-stop"}, {"description": "Kiosk", "help": "Kiosk.", "label": "Kiosk", "name": "kiosk"}] | None = ...,
        hessid: str | None = ...,
        proxy_arp: Literal[{"description": "Enable Proxy ARP", "help": "Enable Proxy ARP.", "label": "Enable", "name": "enable"}, {"description": "Disable Proxy ARP", "help": "Disable Proxy ARP.", "label": "Disable", "name": "disable"}] | None = ...,
        l2tif: Literal[{"description": "Enable Layer 2 traffic inspection and filtering", "help": "Enable Layer 2 traffic inspection and filtering.", "label": "Enable", "name": "enable"}, {"description": "Disable Layer 2 traffic inspection and filtering", "help": "Disable Layer 2 traffic inspection and filtering.", "label": "Disable", "name": "disable"}] | None = ...,
        pame_bi: Literal[{"description": "Disable Pre-Association Message Exchange BSSID Independent (PAME-BI)", "help": "Disable Pre-Association Message Exchange BSSID Independent (PAME-BI).", "label": "Disable", "name": "disable"}, {"description": "Enable Pre-Association Message Exchange BSSID Independent (PAME-BI)", "help": "Enable Pre-Association Message Exchange BSSID Independent (PAME-BI).", "label": "Enable", "name": "enable"}] | None = ...,
        anqp_domain_id: int | None = ...,
        domain_name: str | None = ...,
        osu_ssid: str | None = ...,
        gas_comeback_delay: int | None = ...,
        gas_fragmentation_limit: int | None = ...,
        dgaf: Literal[{"description": "Enable downstream group-addressed forwarding (DGAF)", "help": "Enable downstream group-addressed forwarding (DGAF).", "label": "Enable", "name": "enable"}, {"description": "Disable downstream group-addressed forwarding (DGAF)", "help": "Disable downstream group-addressed forwarding (DGAF).", "label": "Disable", "name": "disable"}] | None = ...,
        deauth_request_timeout: int | None = ...,
        wnm_sleep_mode: Literal[{"description": "Enable wireless network management (WNM) sleep mode", "help": "Enable wireless network management (WNM) sleep mode.", "label": "Enable", "name": "enable"}, {"description": "Disable wireless network management (WNM) sleep mode", "help": "Disable wireless network management (WNM) sleep mode.", "label": "Disable", "name": "disable"}] | None = ...,
        bss_transition: Literal[{"description": "Enable basic service set (BSS) transition support", "help": "Enable basic service set (BSS) transition support.", "label": "Enable", "name": "enable"}, {"description": "Disable basic service set (BSS) transition support", "help": "Disable basic service set (BSS) transition support.", "label": "Disable", "name": "disable"}] | None = ...,
        venue_name: str | None = ...,
        venue_url: str | None = ...,
        roaming_consortium: str | None = ...,
        nai_realm: str | None = ...,
        oper_friendly_name: str | None = ...,
        oper_icon: str | None = ...,
        advice_of_charge: str | None = ...,
        osu_provider_nai: str | None = ...,
        terms_and_conditions: str | None = ...,
        osu_provider: list[dict[str, Any]] | None = ...,
        wan_metrics: str | None = ...,
        network_auth: str | None = ...,
        x3gpp_plmn: str | None = ...,
        conn_cap: str | None = ...,
        qos_map: str | None = ...,
        ip_addr_type: str | None = ...,
        wba_open_roaming: Literal[{"description": "Disable WBA open roaming support", "help": "Disable WBA open roaming support.", "label": "Disable", "name": "disable"}, {"description": "Enable WBA open roaming support", "help": "Enable WBA open roaming support.", "label": "Enable", "name": "enable"}] | None = ...,
        wba_financial_clearing_provider: str | None = ...,
        wba_data_clearing_provider: str | None = ...,
        wba_charging_currency: str | None = ...,
        wba_charging_rate: int | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: HsProfilePayload | None = ...,
        name: str | None = ...,
        release: int | None = ...,
        access_network_type: Literal[{"description": "Private network", "help": "Private network.", "label": "Private Network", "name": "private-network"}, {"description": "Private network with guest access", "help": "Private network with guest access.", "label": "Private Network With Guest Access", "name": "private-network-with-guest-access"}, {"description": "Chargeable public network", "help": "Chargeable public network.", "label": "Chargeable Public Network", "name": "chargeable-public-network"}, {"description": "Free public network", "help": "Free public network.", "label": "Free Public Network", "name": "free-public-network"}, {"description": "Personal devices network", "help": "Personal devices network.", "label": "Personal Device Network", "name": "personal-device-network"}, {"description": "Emergency services only network", "help": "Emergency services only network.", "label": "Emergency Services Only Network", "name": "emergency-services-only-network"}, {"description": "Test or experimental", "help": "Test or experimental.", "label": "Test Or Experimental", "name": "test-or-experimental"}, {"description": "Wildcard", "help": "Wildcard.", "label": "Wildcard", "name": "wildcard"}] | None = ...,
        access_network_internet: Literal[{"description": "Enable connectivity to the Internet", "help": "Enable connectivity to the Internet.", "label": "Enable", "name": "enable"}, {"description": "Disable connectivity to the Internet", "help": "Disable connectivity to the Internet.", "label": "Disable", "name": "disable"}] | None = ...,
        access_network_asra: Literal[{"description": "Enable additional step required for access (ASRA)", "help": "Enable additional step required for access (ASRA).", "label": "Enable", "name": "enable"}, {"description": "Disable additional step required for access (ASRA)", "help": "Disable additional step required for access (ASRA).", "label": "Disable", "name": "disable"}] | None = ...,
        access_network_esr: Literal[{"description": "Enable emergency services reachable (ESR)", "help": "Enable emergency services reachable (ESR).", "label": "Enable", "name": "enable"}, {"description": "Disable emergency services reachable (ESR)", "help": "Disable emergency services reachable (ESR).", "label": "Disable", "name": "disable"}] | None = ...,
        access_network_uesa: Literal[{"description": "Enable unauthenticated emergency service accessible (UESA)", "help": "Enable unauthenticated emergency service accessible (UESA).", "label": "Enable", "name": "enable"}, {"description": "Disable unauthenticated emergency service accessible (UESA)", "help": "Disable unauthenticated emergency service accessible (UESA).", "label": "Disable", "name": "disable"}] | None = ...,
        venue_group: Literal[{"description": "Unspecified", "help": "Unspecified.", "label": "Unspecified", "name": "unspecified"}, {"description": "Assembly", "help": "Assembly.", "label": "Assembly", "name": "assembly"}, {"description": "Business", "help": "Business.", "label": "Business", "name": "business"}, {"description": "Educational", "help": "Educational.", "label": "Educational", "name": "educational"}, {"description": "Factory and industrial", "help": "Factory and industrial.", "label": "Factory", "name": "factory"}, {"description": "Institutional", "help": "Institutional.", "label": "Institutional", "name": "institutional"}, {"description": "Mercantile", "help": "Mercantile.", "label": "Mercantile", "name": "mercantile"}, {"description": "Residential", "help": "Residential.", "label": "Residential", "name": "residential"}, {"description": "Storage", "help": "Storage.", "label": "Storage", "name": "storage"}, {"description": "Utility and miscellaneous", "help": "Utility and miscellaneous.", "label": "Utility", "name": "utility"}, {"description": "Vehicular", "help": "Vehicular.", "label": "Vehicular", "name": "vehicular"}, {"description": "Outdoor", "help": "Outdoor.", "label": "Outdoor", "name": "outdoor"}] | None = ...,
        venue_type: Literal[{"description": "Unspecified", "help": "Unspecified.", "label": "Unspecified", "name": "unspecified"}, {"description": "Arena", "help": "Arena.", "label": "Arena", "name": "arena"}, {"description": "Stadium", "help": "Stadium.", "label": "Stadium", "name": "stadium"}, {"description": "Passenger terminal", "help": "Passenger terminal.", "label": "Passenger Terminal", "name": "passenger-terminal"}, {"description": "Amphitheater", "help": "Amphitheater.", "label": "Amphitheater", "name": "amphitheater"}, {"description": "Amusement park", "help": "Amusement park.", "label": "Amusement Park", "name": "amusement-park"}, {"description": "Place of worship", "help": "Place of worship.", "label": "Place Of Worship", "name": "place-of-worship"}, {"description": "Convention center", "help": "Convention center.", "label": "Convention Center", "name": "convention-center"}, {"description": "Library", "help": "Library.", "label": "Library", "name": "library"}, {"description": "Museum", "help": "Museum.", "label": "Museum", "name": "museum"}, {"description": "Restaurant", "help": "Restaurant.", "label": "Restaurant", "name": "restaurant"}, {"description": "Theater", "help": "Theater.", "label": "Theater", "name": "theater"}, {"description": "Bar", "help": "Bar.", "label": "Bar", "name": "bar"}, {"description": "Coffee shop", "help": "Coffee shop.", "label": "Coffee Shop", "name": "coffee-shop"}, {"description": "Zoo or aquarium", "help": "Zoo or aquarium.", "label": "Zoo Or Aquarium", "name": "zoo-or-aquarium"}, {"description": "Emergency coordination center", "help": "Emergency coordination center.", "label": "Emergency Center", "name": "emergency-center"}, {"description": "Doctor or dentist office", "help": "Doctor or dentist office.", "label": "Doctor Office", "name": "doctor-office"}, {"description": "Bank", "help": "Bank.", "label": "Bank", "name": "bank"}, {"description": "Fire station", "help": "Fire station.", "label": "Fire Station", "name": "fire-station"}, {"description": "Police station", "help": "Police station.", "label": "Police Station", "name": "police-station"}, {"description": "Post office", "help": "Post office.", "label": "Post Office", "name": "post-office"}, {"description": "Professional office", "help": "Professional office.", "label": "Professional Office", "name": "professional-office"}, {"description": "Research and development facility", "help": "Research and development facility.", "label": "Research Facility", "name": "research-facility"}, {"description": "Attorney office", "help": "Attorney office.", "label": "Attorney Office", "name": "attorney-office"}, {"description": "Primary school", "help": "Primary school.", "label": "Primary School", "name": "primary-school"}, {"description": "Secondary school", "help": "Secondary school.", "label": "Secondary School", "name": "secondary-school"}, {"description": "University or college", "help": "University or college.", "label": "University Or College", "name": "university-or-college"}, {"description": "Factory", "help": "Factory.", "label": "Factory", "name": "factory"}, {"description": "Hospital", "help": "Hospital.", "label": "Hospital", "name": "hospital"}, {"description": "Long term care facility", "help": "Long term care facility.", "label": "Long Term Care Facility", "name": "long-term-care-facility"}, {"description": "Alcohol and drug rehabilitation center", "help": "Alcohol and drug rehabilitation center.", "label": "Rehab Center", "name": "rehab-center"}, {"description": "Group home", "help": "Group home.", "label": "Group Home", "name": "group-home"}, {"description": "Prison or jail", "help": "Prison or jail.", "label": "Prison Or Jail", "name": "prison-or-jail"}, {"description": "Retail store", "help": "Retail store.", "label": "Retail Store", "name": "retail-store"}, {"description": "Grocery market", "help": "Grocery market.", "label": "Grocery Market", "name": "grocery-market"}, {"description": "Auto service station", "help": "Auto service station.", "label": "Auto Service Station", "name": "auto-service-station"}, {"description": "Shopping mall", "help": "Shopping mall.", "label": "Shopping Mall", "name": "shopping-mall"}, {"description": "Gas station", "help": "Gas station.", "label": "Gas Station", "name": "gas-station"}, {"description": "Private residence", "help": "Private residence.", "label": "Private", "name": "private"}, {"description": "Hotel or motel", "help": "Hotel or motel.", "label": "Hotel Or Motel", "name": "hotel-or-motel"}, {"description": "Dormitory", "help": "Dormitory.", "label": "Dormitory", "name": "dormitory"}, {"description": "Boarding house", "help": "Boarding house.", "label": "Boarding House", "name": "boarding-house"}, {"description": "Automobile or truck", "help": "Automobile or truck.", "label": "Automobile", "name": "automobile"}, {"description": "Airplane", "help": "Airplane.", "label": "Airplane", "name": "airplane"}, {"description": "Bus", "help": "Bus.", "label": "Bus", "name": "bus"}, {"description": "Ferry", "help": "Ferry.", "label": "Ferry", "name": "ferry"}, {"description": "Ship or boat", "help": "Ship or boat.", "label": "Ship Or Boat", "name": "ship-or-boat"}, {"description": "Train", "help": "Train.", "label": "Train", "name": "train"}, {"description": "Motor bike", "help": "Motor bike.", "label": "Motor Bike", "name": "motor-bike"}, {"description": "Muni mesh network", "help": "Muni mesh network.", "label": "Muni Mesh Network", "name": "muni-mesh-network"}, {"description": "City park", "help": "City park.", "label": "City Park", "name": "city-park"}, {"description": "Rest area", "help": "Rest area.", "label": "Rest Area", "name": "rest-area"}, {"description": "Traffic control", "help": "Traffic control.", "label": "Traffic Control", "name": "traffic-control"}, {"description": "Bus stop", "help": "Bus stop.", "label": "Bus Stop", "name": "bus-stop"}, {"description": "Kiosk", "help": "Kiosk.", "label": "Kiosk", "name": "kiosk"}] | None = ...,
        hessid: str | None = ...,
        proxy_arp: Literal[{"description": "Enable Proxy ARP", "help": "Enable Proxy ARP.", "label": "Enable", "name": "enable"}, {"description": "Disable Proxy ARP", "help": "Disable Proxy ARP.", "label": "Disable", "name": "disable"}] | None = ...,
        l2tif: Literal[{"description": "Enable Layer 2 traffic inspection and filtering", "help": "Enable Layer 2 traffic inspection and filtering.", "label": "Enable", "name": "enable"}, {"description": "Disable Layer 2 traffic inspection and filtering", "help": "Disable Layer 2 traffic inspection and filtering.", "label": "Disable", "name": "disable"}] | None = ...,
        pame_bi: Literal[{"description": "Disable Pre-Association Message Exchange BSSID Independent (PAME-BI)", "help": "Disable Pre-Association Message Exchange BSSID Independent (PAME-BI).", "label": "Disable", "name": "disable"}, {"description": "Enable Pre-Association Message Exchange BSSID Independent (PAME-BI)", "help": "Enable Pre-Association Message Exchange BSSID Independent (PAME-BI).", "label": "Enable", "name": "enable"}] | None = ...,
        anqp_domain_id: int | None = ...,
        domain_name: str | None = ...,
        osu_ssid: str | None = ...,
        gas_comeback_delay: int | None = ...,
        gas_fragmentation_limit: int | None = ...,
        dgaf: Literal[{"description": "Enable downstream group-addressed forwarding (DGAF)", "help": "Enable downstream group-addressed forwarding (DGAF).", "label": "Enable", "name": "enable"}, {"description": "Disable downstream group-addressed forwarding (DGAF)", "help": "Disable downstream group-addressed forwarding (DGAF).", "label": "Disable", "name": "disable"}] | None = ...,
        deauth_request_timeout: int | None = ...,
        wnm_sleep_mode: Literal[{"description": "Enable wireless network management (WNM) sleep mode", "help": "Enable wireless network management (WNM) sleep mode.", "label": "Enable", "name": "enable"}, {"description": "Disable wireless network management (WNM) sleep mode", "help": "Disable wireless network management (WNM) sleep mode.", "label": "Disable", "name": "disable"}] | None = ...,
        bss_transition: Literal[{"description": "Enable basic service set (BSS) transition support", "help": "Enable basic service set (BSS) transition support.", "label": "Enable", "name": "enable"}, {"description": "Disable basic service set (BSS) transition support", "help": "Disable basic service set (BSS) transition support.", "label": "Disable", "name": "disable"}] | None = ...,
        venue_name: str | None = ...,
        venue_url: str | None = ...,
        roaming_consortium: str | None = ...,
        nai_realm: str | None = ...,
        oper_friendly_name: str | None = ...,
        oper_icon: str | None = ...,
        advice_of_charge: str | None = ...,
        osu_provider_nai: str | None = ...,
        terms_and_conditions: str | None = ...,
        osu_provider: list[dict[str, Any]] | None = ...,
        wan_metrics: str | None = ...,
        network_auth: str | None = ...,
        x3gpp_plmn: str | None = ...,
        conn_cap: str | None = ...,
        qos_map: str | None = ...,
        ip_addr_type: str | None = ...,
        wba_open_roaming: Literal[{"description": "Disable WBA open roaming support", "help": "Disable WBA open roaming support.", "label": "Disable", "name": "disable"}, {"description": "Enable WBA open roaming support", "help": "Enable WBA open roaming support.", "label": "Enable", "name": "enable"}] | None = ...,
        wba_financial_clearing_provider: str | None = ...,
        wba_data_clearing_provider: str | None = ...,
        wba_charging_currency: str | None = ...,
        wba_charging_rate: int | None = ...,
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
        payload_dict: HsProfilePayload | None = ...,
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
    "HsProfile",
    "HsProfilePayload",
]