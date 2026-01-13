from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class IsisPayload(TypedDict, total=False):
    """
    Type hints for router/isis payload fields.
    
    Configure IS-IS.
    
    **Related Resources:**

    Dependencies (resources this endpoint references):
        - :class:`~.router.access-list.AccessListEndpoint` (via: redistribute-l1-list, redistribute-l2-list)
        - :class:`~.router.access-list6.AccessList6Endpoint` (via: redistribute6-l1-list, redistribute6-l2-list)
        - :class:`~.router.key-chain.KeyChainEndpoint` (via: auth-keychain-l1, auth-keychain-l2)

    **Usage:**
        payload: IsisPayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    is_type: NotRequired[Literal[{"description": "Level 1 and 2", "help": "Level 1 and 2.", "label": "Level 1 2", "name": "level-1-2"}, {"description": "Level 1 only", "help": "Level 1 only.", "label": "Level 1", "name": "level-1"}, {"description": "Level 2 only", "help": "Level 2 only.", "label": "Level 2 Only", "name": "level-2-only"}]]  # IS type.
    adv_passive_only: NotRequired[Literal[{"description": "Advertise passive interfaces only", "help": "Advertise passive interfaces only.", "label": "Enable", "name": "enable"}, {"description": "Advertise all IS-IS enabled interfaces", "help": "Advertise all IS-IS enabled interfaces.", "label": "Disable", "name": "disable"}]]  # Enable/disable IS-IS advertisement of passive interfaces onl
    adv_passive_only6: NotRequired[Literal[{"description": "Advertise passive interfaces only", "help": "Advertise passive interfaces only.", "label": "Enable", "name": "enable"}, {"description": "Advertise all IS-IS enabled interfaces", "help": "Advertise all IS-IS enabled interfaces.", "label": "Disable", "name": "disable"}]]  # Enable/disable IPv6 IS-IS advertisement of passive interface
    auth_mode_l1: NotRequired[Literal[{"description": "Password", "help": "Password.", "label": "Password", "name": "password"}, {"description": "MD5", "help": "MD5.", "label": "Md5", "name": "md5"}]]  # Level 1 authentication mode.
    auth_mode_l2: NotRequired[Literal[{"description": "Password", "help": "Password.", "label": "Password", "name": "password"}, {"description": "MD5", "help": "MD5.", "label": "Md5", "name": "md5"}]]  # Level 2 authentication mode.
    auth_password_l1: NotRequired[str]  # Authentication password for level 1 PDUs.
    auth_password_l2: NotRequired[str]  # Authentication password for level 2 PDUs.
    auth_keychain_l1: NotRequired[str]  # Authentication key-chain for level 1 PDUs.
    auth_keychain_l2: NotRequired[str]  # Authentication key-chain for level 2 PDUs.
    auth_sendonly_l1: NotRequired[Literal[{"description": "Enable level 1 authentication send-only", "help": "Enable level 1 authentication send-only.", "label": "Enable", "name": "enable"}, {"description": "Disable level 1 authentication send-only", "help": "Disable level 1 authentication send-only.", "label": "Disable", "name": "disable"}]]  # Enable/disable level 1 authentication send-only.
    auth_sendonly_l2: NotRequired[Literal[{"description": "Enable level 2 authentication send-only", "help": "Enable level 2 authentication send-only.", "label": "Enable", "name": "enable"}, {"description": "Disable level 2 authentication send-only", "help": "Disable level 2 authentication send-only.", "label": "Disable", "name": "disable"}]]  # Enable/disable level 2 authentication send-only.
    ignore_lsp_errors: NotRequired[Literal[{"description": "Enable ignoring of LSP errors with bad checksums", "help": "Enable ignoring of LSP errors with bad checksums.", "label": "Enable", "name": "enable"}, {"description": "Disable ignoring of LSP errors with bad checksums", "help": "Disable ignoring of LSP errors with bad checksums.", "label": "Disable", "name": "disable"}]]  # Enable/disable ignoring of LSP errors with bad checksums.
    lsp_gen_interval_l1: NotRequired[int]  # Minimum interval for level 1 LSP regenerating.
    lsp_gen_interval_l2: NotRequired[int]  # Minimum interval for level 2 LSP regenerating.
    lsp_refresh_interval: NotRequired[int]  # LSP refresh time in seconds.
    max_lsp_lifetime: NotRequired[int]  # Maximum LSP lifetime in seconds.
    spf_interval_exp_l1: NotRequired[str]  # Level 1 SPF calculation delay.
    spf_interval_exp_l2: NotRequired[str]  # Level 2 SPF calculation delay.
    dynamic_hostname: NotRequired[Literal[{"description": "Enable dynamic hostname", "help": "Enable dynamic hostname.", "label": "Enable", "name": "enable"}, {"description": "Disable dynamic hostname", "help": "Disable dynamic hostname.", "label": "Disable", "name": "disable"}]]  # Enable/disable dynamic hostname.
    adjacency_check: NotRequired[Literal[{"description": "Enable adjacency check", "help": "Enable adjacency check.", "label": "Enable", "name": "enable"}, {"description": "Disable adjacency check", "help": "Disable adjacency check.", "label": "Disable", "name": "disable"}]]  # Enable/disable adjacency check.
    adjacency_check6: NotRequired[Literal[{"description": "Enable IPv6 adjacency check", "help": "Enable IPv6 adjacency check.", "label": "Enable", "name": "enable"}, {"description": "Disable IPv6 adjacency check", "help": "Disable IPv6 adjacency check.", "label": "Disable", "name": "disable"}]]  # Enable/disable IPv6 adjacency check.
    overload_bit: NotRequired[Literal[{"description": "Enable overload bit", "help": "Enable overload bit.", "label": "Enable", "name": "enable"}, {"description": "Disable overload bit", "help": "Disable overload bit.", "label": "Disable", "name": "disable"}]]  # Enable/disable signal other routers not to use us in SPF.
    overload_bit_suppress: NotRequired[Literal[{"description": "External", "help": "External.", "label": "External", "name": "external"}, {"description": "Inter-level", "help": "Inter-level.", "label": "Interlevel", "name": "interlevel"}]]  # Suppress overload-bit for the specific prefixes.
    overload_bit_on_startup: NotRequired[int]  # Overload-bit only temporarily after reboot.
    default_originate: NotRequired[Literal[{"description": "Enable distribution of default route information", "help": "Enable distribution of default route information.", "label": "Enable", "name": "enable"}, {"description": "Disable distribution of default route information", "help": "Disable distribution of default route information.", "label": "Disable", "name": "disable"}]]  # Enable/disable distribution of default route information.
    default_originate6: NotRequired[Literal[{"description": "Enable distribution of default IPv6 route information", "help": "Enable distribution of default IPv6 route information.", "label": "Enable", "name": "enable"}, {"description": "Disable distribution of default IPv6 route information", "help": "Disable distribution of default IPv6 route information.", "label": "Disable", "name": "disable"}]]  # Enable/disable distribution of default IPv6 route informatio
    metric_style: NotRequired[Literal[{"description": "Use old style of TLVs with narrow metric", "help": "Use old style of TLVs with narrow metric.", "label": "Narrow", "name": "narrow"}, {"description": "Use new style of TLVs to carry wider metric", "help": "Use new style of TLVs to carry wider metric.", "label": "Wide", "name": "wide"}, {"description": "Send and accept both styles of TLVs during transition", "help": "Send and accept both styles of TLVs during transition.", "label": "Transition", "name": "transition"}, {"description": "Narrow and accept both styles of TLVs during transition", "help": "Narrow and accept both styles of TLVs during transition.", "label": "Narrow Transition", "name": "narrow-transition"}, {"description": "Narrow-transition level-1 only", "help": "Narrow-transition level-1 only.", "label": "Narrow Transition L1", "name": "narrow-transition-l1"}, {"description": "Narrow-transition level-2 only", "help": "Narrow-transition level-2 only.", "label": "Narrow Transition L2", "name": "narrow-transition-l2"}, {"description": "Wide level-1 only", "help": "Wide level-1 only.", "label": "Wide L1", "name": "wide-l1"}, {"description": "Wide level-2 only", "help": "Wide level-2 only.", "label": "Wide L2", "name": "wide-l2"}, {"description": "Wide and accept both styles of TLVs during transition", "help": "Wide and accept both styles of TLVs during transition.", "label": "Wide Transition", "name": "wide-transition"}, {"description": "Wide-transition level-1 only", "help": "Wide-transition level-1 only.", "label": "Wide Transition L1", "name": "wide-transition-l1"}, {"description": "Wide-transition level-2 only", "help": "Wide-transition level-2 only.", "label": "Wide Transition L2", "name": "wide-transition-l2"}, {"description": "Transition level-1 only", "help": "Transition level-1 only.", "label": "Transition L1", "name": "transition-l1"}, {"description": "Transition level-2 only", "help": "Transition level-2 only.", "label": "Transition L2", "name": "transition-l2"}]]  # Use old-style (ISO 10589) or new-style packet formats.
    redistribute_l1: NotRequired[Literal[{"description": "Enable redistribution of level 1 routes into level 2", "help": "Enable redistribution of level 1 routes into level 2.", "label": "Enable", "name": "enable"}, {"description": "Disable redistribution of level 1 routes into level 2", "help": "Disable redistribution of level 1 routes into level 2.", "label": "Disable", "name": "disable"}]]  # Enable/disable redistribution of level 1 routes into level 2
    redistribute_l1_list: NotRequired[str]  # Access-list for route redistribution from l1 to l2.
    redistribute_l2: NotRequired[Literal[{"description": "Enable redistribution of level 2 routes into level 1", "help": "Enable redistribution of level 2 routes into level 1.", "label": "Enable", "name": "enable"}, {"description": "Disable redistribution of  level 2 routes into level 1", "help": "Disable redistribution of  level 2 routes into level 1.", "label": "Disable", "name": "disable"}]]  # Enable/disable redistribution of level 2 routes into level 1
    redistribute_l2_list: NotRequired[str]  # Access-list for route redistribution from l2 to l1.
    redistribute6_l1: NotRequired[Literal[{"description": "Enable redistribution of level 1 IPv6 routes into level 2", "help": "Enable redistribution of level 1 IPv6 routes into level 2.", "label": "Enable", "name": "enable"}, {"description": "Disable redistribution of level 1 IPv6 routes into level 2", "help": "Disable redistribution of level 1 IPv6 routes into level 2.", "label": "Disable", "name": "disable"}]]  # Enable/disable redistribution of level 1 IPv6 routes into le
    redistribute6_l1_list: NotRequired[str]  # Access-list for IPv6 route redistribution from l1 to l2.
    redistribute6_l2: NotRequired[Literal[{"description": "Enable redistribution of level 2 IPv6 routes into level 1", "help": "Enable redistribution of level 2 IPv6 routes into level 1.", "label": "Enable", "name": "enable"}, {"description": "Disable redistribution of level 2 IPv6 routes into level 1", "help": "Disable redistribution of level 2 IPv6 routes into level 1.", "label": "Disable", "name": "disable"}]]  # Enable/disable redistribution of level 2 IPv6 routes into le
    redistribute6_l2_list: NotRequired[str]  # Access-list for IPv6 route redistribution from l2 to l1.
    isis_net: NotRequired[list[dict[str, Any]]]  # IS-IS net configuration.
    isis_interface: NotRequired[list[dict[str, Any]]]  # IS-IS interface configuration.
    summary_address: NotRequired[list[dict[str, Any]]]  # IS-IS summary addresses.
    summary_address6: NotRequired[list[dict[str, Any]]]  # IS-IS IPv6 summary address.
    redistribute: NotRequired[list[dict[str, Any]]]  # IS-IS redistribute protocols.
    redistribute6: NotRequired[list[dict[str, Any]]]  # IS-IS IPv6 redistribution for routing protocols.


class Isis:
    """
    Configure IS-IS.
    
    Path: router/isis
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
        payload_dict: IsisPayload | None = ...,
        is_type: Literal[{"description": "Level 1 and 2", "help": "Level 1 and 2.", "label": "Level 1 2", "name": "level-1-2"}, {"description": "Level 1 only", "help": "Level 1 only.", "label": "Level 1", "name": "level-1"}, {"description": "Level 2 only", "help": "Level 2 only.", "label": "Level 2 Only", "name": "level-2-only"}] | None = ...,
        adv_passive_only: Literal[{"description": "Advertise passive interfaces only", "help": "Advertise passive interfaces only.", "label": "Enable", "name": "enable"}, {"description": "Advertise all IS-IS enabled interfaces", "help": "Advertise all IS-IS enabled interfaces.", "label": "Disable", "name": "disable"}] | None = ...,
        adv_passive_only6: Literal[{"description": "Advertise passive interfaces only", "help": "Advertise passive interfaces only.", "label": "Enable", "name": "enable"}, {"description": "Advertise all IS-IS enabled interfaces", "help": "Advertise all IS-IS enabled interfaces.", "label": "Disable", "name": "disable"}] | None = ...,
        auth_mode_l1: Literal[{"description": "Password", "help": "Password.", "label": "Password", "name": "password"}, {"description": "MD5", "help": "MD5.", "label": "Md5", "name": "md5"}] | None = ...,
        auth_mode_l2: Literal[{"description": "Password", "help": "Password.", "label": "Password", "name": "password"}, {"description": "MD5", "help": "MD5.", "label": "Md5", "name": "md5"}] | None = ...,
        auth_password_l1: str | None = ...,
        auth_password_l2: str | None = ...,
        auth_keychain_l1: str | None = ...,
        auth_keychain_l2: str | None = ...,
        auth_sendonly_l1: Literal[{"description": "Enable level 1 authentication send-only", "help": "Enable level 1 authentication send-only.", "label": "Enable", "name": "enable"}, {"description": "Disable level 1 authentication send-only", "help": "Disable level 1 authentication send-only.", "label": "Disable", "name": "disable"}] | None = ...,
        auth_sendonly_l2: Literal[{"description": "Enable level 2 authentication send-only", "help": "Enable level 2 authentication send-only.", "label": "Enable", "name": "enable"}, {"description": "Disable level 2 authentication send-only", "help": "Disable level 2 authentication send-only.", "label": "Disable", "name": "disable"}] | None = ...,
        ignore_lsp_errors: Literal[{"description": "Enable ignoring of LSP errors with bad checksums", "help": "Enable ignoring of LSP errors with bad checksums.", "label": "Enable", "name": "enable"}, {"description": "Disable ignoring of LSP errors with bad checksums", "help": "Disable ignoring of LSP errors with bad checksums.", "label": "Disable", "name": "disable"}] | None = ...,
        lsp_gen_interval_l1: int | None = ...,
        lsp_gen_interval_l2: int | None = ...,
        lsp_refresh_interval: int | None = ...,
        max_lsp_lifetime: int | None = ...,
        spf_interval_exp_l1: str | None = ...,
        spf_interval_exp_l2: str | None = ...,
        dynamic_hostname: Literal[{"description": "Enable dynamic hostname", "help": "Enable dynamic hostname.", "label": "Enable", "name": "enable"}, {"description": "Disable dynamic hostname", "help": "Disable dynamic hostname.", "label": "Disable", "name": "disable"}] | None = ...,
        adjacency_check: Literal[{"description": "Enable adjacency check", "help": "Enable adjacency check.", "label": "Enable", "name": "enable"}, {"description": "Disable adjacency check", "help": "Disable adjacency check.", "label": "Disable", "name": "disable"}] | None = ...,
        adjacency_check6: Literal[{"description": "Enable IPv6 adjacency check", "help": "Enable IPv6 adjacency check.", "label": "Enable", "name": "enable"}, {"description": "Disable IPv6 adjacency check", "help": "Disable IPv6 adjacency check.", "label": "Disable", "name": "disable"}] | None = ...,
        overload_bit: Literal[{"description": "Enable overload bit", "help": "Enable overload bit.", "label": "Enable", "name": "enable"}, {"description": "Disable overload bit", "help": "Disable overload bit.", "label": "Disable", "name": "disable"}] | None = ...,
        overload_bit_suppress: Literal[{"description": "External", "help": "External.", "label": "External", "name": "external"}, {"description": "Inter-level", "help": "Inter-level.", "label": "Interlevel", "name": "interlevel"}] | None = ...,
        overload_bit_on_startup: int | None = ...,
        default_originate: Literal[{"description": "Enable distribution of default route information", "help": "Enable distribution of default route information.", "label": "Enable", "name": "enable"}, {"description": "Disable distribution of default route information", "help": "Disable distribution of default route information.", "label": "Disable", "name": "disable"}] | None = ...,
        default_originate6: Literal[{"description": "Enable distribution of default IPv6 route information", "help": "Enable distribution of default IPv6 route information.", "label": "Enable", "name": "enable"}, {"description": "Disable distribution of default IPv6 route information", "help": "Disable distribution of default IPv6 route information.", "label": "Disable", "name": "disable"}] | None = ...,
        metric_style: Literal[{"description": "Use old style of TLVs with narrow metric", "help": "Use old style of TLVs with narrow metric.", "label": "Narrow", "name": "narrow"}, {"description": "Use new style of TLVs to carry wider metric", "help": "Use new style of TLVs to carry wider metric.", "label": "Wide", "name": "wide"}, {"description": "Send and accept both styles of TLVs during transition", "help": "Send and accept both styles of TLVs during transition.", "label": "Transition", "name": "transition"}, {"description": "Narrow and accept both styles of TLVs during transition", "help": "Narrow and accept both styles of TLVs during transition.", "label": "Narrow Transition", "name": "narrow-transition"}, {"description": "Narrow-transition level-1 only", "help": "Narrow-transition level-1 only.", "label": "Narrow Transition L1", "name": "narrow-transition-l1"}, {"description": "Narrow-transition level-2 only", "help": "Narrow-transition level-2 only.", "label": "Narrow Transition L2", "name": "narrow-transition-l2"}, {"description": "Wide level-1 only", "help": "Wide level-1 only.", "label": "Wide L1", "name": "wide-l1"}, {"description": "Wide level-2 only", "help": "Wide level-2 only.", "label": "Wide L2", "name": "wide-l2"}, {"description": "Wide and accept both styles of TLVs during transition", "help": "Wide and accept both styles of TLVs during transition.", "label": "Wide Transition", "name": "wide-transition"}, {"description": "Wide-transition level-1 only", "help": "Wide-transition level-1 only.", "label": "Wide Transition L1", "name": "wide-transition-l1"}, {"description": "Wide-transition level-2 only", "help": "Wide-transition level-2 only.", "label": "Wide Transition L2", "name": "wide-transition-l2"}, {"description": "Transition level-1 only", "help": "Transition level-1 only.", "label": "Transition L1", "name": "transition-l1"}, {"description": "Transition level-2 only", "help": "Transition level-2 only.", "label": "Transition L2", "name": "transition-l2"}] | None = ...,
        redistribute_l1: Literal[{"description": "Enable redistribution of level 1 routes into level 2", "help": "Enable redistribution of level 1 routes into level 2.", "label": "Enable", "name": "enable"}, {"description": "Disable redistribution of level 1 routes into level 2", "help": "Disable redistribution of level 1 routes into level 2.", "label": "Disable", "name": "disable"}] | None = ...,
        redistribute_l1_list: str | None = ...,
        redistribute_l2: Literal[{"description": "Enable redistribution of level 2 routes into level 1", "help": "Enable redistribution of level 2 routes into level 1.", "label": "Enable", "name": "enable"}, {"description": "Disable redistribution of  level 2 routes into level 1", "help": "Disable redistribution of  level 2 routes into level 1.", "label": "Disable", "name": "disable"}] | None = ...,
        redistribute_l2_list: str | None = ...,
        redistribute6_l1: Literal[{"description": "Enable redistribution of level 1 IPv6 routes into level 2", "help": "Enable redistribution of level 1 IPv6 routes into level 2.", "label": "Enable", "name": "enable"}, {"description": "Disable redistribution of level 1 IPv6 routes into level 2", "help": "Disable redistribution of level 1 IPv6 routes into level 2.", "label": "Disable", "name": "disable"}] | None = ...,
        redistribute6_l1_list: str | None = ...,
        redistribute6_l2: Literal[{"description": "Enable redistribution of level 2 IPv6 routes into level 1", "help": "Enable redistribution of level 2 IPv6 routes into level 1.", "label": "Enable", "name": "enable"}, {"description": "Disable redistribution of level 2 IPv6 routes into level 1", "help": "Disable redistribution of level 2 IPv6 routes into level 1.", "label": "Disable", "name": "disable"}] | None = ...,
        redistribute6_l2_list: str | None = ...,
        isis_net: list[dict[str, Any]] | None = ...,
        isis_interface: list[dict[str, Any]] | None = ...,
        summary_address: list[dict[str, Any]] | None = ...,
        summary_address6: list[dict[str, Any]] | None = ...,
        redistribute: list[dict[str, Any]] | None = ...,
        redistribute6: list[dict[str, Any]] | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: IsisPayload | None = ...,
        is_type: Literal[{"description": "Level 1 and 2", "help": "Level 1 and 2.", "label": "Level 1 2", "name": "level-1-2"}, {"description": "Level 1 only", "help": "Level 1 only.", "label": "Level 1", "name": "level-1"}, {"description": "Level 2 only", "help": "Level 2 only.", "label": "Level 2 Only", "name": "level-2-only"}] | None = ...,
        adv_passive_only: Literal[{"description": "Advertise passive interfaces only", "help": "Advertise passive interfaces only.", "label": "Enable", "name": "enable"}, {"description": "Advertise all IS-IS enabled interfaces", "help": "Advertise all IS-IS enabled interfaces.", "label": "Disable", "name": "disable"}] | None = ...,
        adv_passive_only6: Literal[{"description": "Advertise passive interfaces only", "help": "Advertise passive interfaces only.", "label": "Enable", "name": "enable"}, {"description": "Advertise all IS-IS enabled interfaces", "help": "Advertise all IS-IS enabled interfaces.", "label": "Disable", "name": "disable"}] | None = ...,
        auth_mode_l1: Literal[{"description": "Password", "help": "Password.", "label": "Password", "name": "password"}, {"description": "MD5", "help": "MD5.", "label": "Md5", "name": "md5"}] | None = ...,
        auth_mode_l2: Literal[{"description": "Password", "help": "Password.", "label": "Password", "name": "password"}, {"description": "MD5", "help": "MD5.", "label": "Md5", "name": "md5"}] | None = ...,
        auth_password_l1: str | None = ...,
        auth_password_l2: str | None = ...,
        auth_keychain_l1: str | None = ...,
        auth_keychain_l2: str | None = ...,
        auth_sendonly_l1: Literal[{"description": "Enable level 1 authentication send-only", "help": "Enable level 1 authentication send-only.", "label": "Enable", "name": "enable"}, {"description": "Disable level 1 authentication send-only", "help": "Disable level 1 authentication send-only.", "label": "Disable", "name": "disable"}] | None = ...,
        auth_sendonly_l2: Literal[{"description": "Enable level 2 authentication send-only", "help": "Enable level 2 authentication send-only.", "label": "Enable", "name": "enable"}, {"description": "Disable level 2 authentication send-only", "help": "Disable level 2 authentication send-only.", "label": "Disable", "name": "disable"}] | None = ...,
        ignore_lsp_errors: Literal[{"description": "Enable ignoring of LSP errors with bad checksums", "help": "Enable ignoring of LSP errors with bad checksums.", "label": "Enable", "name": "enable"}, {"description": "Disable ignoring of LSP errors with bad checksums", "help": "Disable ignoring of LSP errors with bad checksums.", "label": "Disable", "name": "disable"}] | None = ...,
        lsp_gen_interval_l1: int | None = ...,
        lsp_gen_interval_l2: int | None = ...,
        lsp_refresh_interval: int | None = ...,
        max_lsp_lifetime: int | None = ...,
        spf_interval_exp_l1: str | None = ...,
        spf_interval_exp_l2: str | None = ...,
        dynamic_hostname: Literal[{"description": "Enable dynamic hostname", "help": "Enable dynamic hostname.", "label": "Enable", "name": "enable"}, {"description": "Disable dynamic hostname", "help": "Disable dynamic hostname.", "label": "Disable", "name": "disable"}] | None = ...,
        adjacency_check: Literal[{"description": "Enable adjacency check", "help": "Enable adjacency check.", "label": "Enable", "name": "enable"}, {"description": "Disable adjacency check", "help": "Disable adjacency check.", "label": "Disable", "name": "disable"}] | None = ...,
        adjacency_check6: Literal[{"description": "Enable IPv6 adjacency check", "help": "Enable IPv6 adjacency check.", "label": "Enable", "name": "enable"}, {"description": "Disable IPv6 adjacency check", "help": "Disable IPv6 adjacency check.", "label": "Disable", "name": "disable"}] | None = ...,
        overload_bit: Literal[{"description": "Enable overload bit", "help": "Enable overload bit.", "label": "Enable", "name": "enable"}, {"description": "Disable overload bit", "help": "Disable overload bit.", "label": "Disable", "name": "disable"}] | None = ...,
        overload_bit_suppress: Literal[{"description": "External", "help": "External.", "label": "External", "name": "external"}, {"description": "Inter-level", "help": "Inter-level.", "label": "Interlevel", "name": "interlevel"}] | None = ...,
        overload_bit_on_startup: int | None = ...,
        default_originate: Literal[{"description": "Enable distribution of default route information", "help": "Enable distribution of default route information.", "label": "Enable", "name": "enable"}, {"description": "Disable distribution of default route information", "help": "Disable distribution of default route information.", "label": "Disable", "name": "disable"}] | None = ...,
        default_originate6: Literal[{"description": "Enable distribution of default IPv6 route information", "help": "Enable distribution of default IPv6 route information.", "label": "Enable", "name": "enable"}, {"description": "Disable distribution of default IPv6 route information", "help": "Disable distribution of default IPv6 route information.", "label": "Disable", "name": "disable"}] | None = ...,
        metric_style: Literal[{"description": "Use old style of TLVs with narrow metric", "help": "Use old style of TLVs with narrow metric.", "label": "Narrow", "name": "narrow"}, {"description": "Use new style of TLVs to carry wider metric", "help": "Use new style of TLVs to carry wider metric.", "label": "Wide", "name": "wide"}, {"description": "Send and accept both styles of TLVs during transition", "help": "Send and accept both styles of TLVs during transition.", "label": "Transition", "name": "transition"}, {"description": "Narrow and accept both styles of TLVs during transition", "help": "Narrow and accept both styles of TLVs during transition.", "label": "Narrow Transition", "name": "narrow-transition"}, {"description": "Narrow-transition level-1 only", "help": "Narrow-transition level-1 only.", "label": "Narrow Transition L1", "name": "narrow-transition-l1"}, {"description": "Narrow-transition level-2 only", "help": "Narrow-transition level-2 only.", "label": "Narrow Transition L2", "name": "narrow-transition-l2"}, {"description": "Wide level-1 only", "help": "Wide level-1 only.", "label": "Wide L1", "name": "wide-l1"}, {"description": "Wide level-2 only", "help": "Wide level-2 only.", "label": "Wide L2", "name": "wide-l2"}, {"description": "Wide and accept both styles of TLVs during transition", "help": "Wide and accept both styles of TLVs during transition.", "label": "Wide Transition", "name": "wide-transition"}, {"description": "Wide-transition level-1 only", "help": "Wide-transition level-1 only.", "label": "Wide Transition L1", "name": "wide-transition-l1"}, {"description": "Wide-transition level-2 only", "help": "Wide-transition level-2 only.", "label": "Wide Transition L2", "name": "wide-transition-l2"}, {"description": "Transition level-1 only", "help": "Transition level-1 only.", "label": "Transition L1", "name": "transition-l1"}, {"description": "Transition level-2 only", "help": "Transition level-2 only.", "label": "Transition L2", "name": "transition-l2"}] | None = ...,
        redistribute_l1: Literal[{"description": "Enable redistribution of level 1 routes into level 2", "help": "Enable redistribution of level 1 routes into level 2.", "label": "Enable", "name": "enable"}, {"description": "Disable redistribution of level 1 routes into level 2", "help": "Disable redistribution of level 1 routes into level 2.", "label": "Disable", "name": "disable"}] | None = ...,
        redistribute_l1_list: str | None = ...,
        redistribute_l2: Literal[{"description": "Enable redistribution of level 2 routes into level 1", "help": "Enable redistribution of level 2 routes into level 1.", "label": "Enable", "name": "enable"}, {"description": "Disable redistribution of  level 2 routes into level 1", "help": "Disable redistribution of  level 2 routes into level 1.", "label": "Disable", "name": "disable"}] | None = ...,
        redistribute_l2_list: str | None = ...,
        redistribute6_l1: Literal[{"description": "Enable redistribution of level 1 IPv6 routes into level 2", "help": "Enable redistribution of level 1 IPv6 routes into level 2.", "label": "Enable", "name": "enable"}, {"description": "Disable redistribution of level 1 IPv6 routes into level 2", "help": "Disable redistribution of level 1 IPv6 routes into level 2.", "label": "Disable", "name": "disable"}] | None = ...,
        redistribute6_l1_list: str | None = ...,
        redistribute6_l2: Literal[{"description": "Enable redistribution of level 2 IPv6 routes into level 1", "help": "Enable redistribution of level 2 IPv6 routes into level 1.", "label": "Enable", "name": "enable"}, {"description": "Disable redistribution of level 2 IPv6 routes into level 1", "help": "Disable redistribution of level 2 IPv6 routes into level 1.", "label": "Disable", "name": "disable"}] | None = ...,
        redistribute6_l2_list: str | None = ...,
        isis_net: list[dict[str, Any]] | None = ...,
        isis_interface: list[dict[str, Any]] | None = ...,
        summary_address: list[dict[str, Any]] | None = ...,
        summary_address6: list[dict[str, Any]] | None = ...,
        redistribute: list[dict[str, Any]] | None = ...,
        redistribute6: list[dict[str, Any]] | None = ...,
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
        payload_dict: IsisPayload | None = ...,
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
    "Isis",
    "IsisPayload",
]