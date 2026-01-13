from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_MODE: Literal[{"description": "Standalone mode", "help": "Standalone mode.", "label": "Standalone", "name": "standalone"}, {"description": "Active-active mode", "help": "Active-active mode.", "label": "A A", "name": "a-a"}, {"description": "Active-passive mode", "help": "Active-passive mode.", "label": "A P", "name": "a-p"}]
VALID_BODY_SYNC_PACKET_BALANCE: Literal[{"description": "Enable HA packet distribution to multiple CPUs", "help": "Enable HA packet distribution to multiple CPUs.", "label": "Enable", "name": "enable"}, {"description": "Disable HA packet distribution to multiple CPUs", "help": "Disable HA packet distribution to multiple CPUs.", "label": "Disable", "name": "disable"}]
VALID_BODY_UNICAST_HB: Literal[{"help": "Enable setting.", "label": "Enable", "name": "enable"}, {"help": "Disable setting.", "label": "Disable", "name": "disable"}]
VALID_BODY_LOAD_BALANCE_ALL: Literal[{"description": "Enable load balance", "help": "Enable load balance.", "label": "Enable", "name": "enable"}, {"description": "Disable load balance", "help": "Disable load balance.", "label": "Disable", "name": "disable"}]
VALID_BODY_SYNC_CONFIG: Literal[{"description": "Enable configuration synchronization", "help": "Enable configuration synchronization.", "label": "Enable", "name": "enable"}, {"description": "Disable configuration synchronization", "help": "Disable configuration synchronization.", "label": "Disable", "name": "disable"}]
VALID_BODY_ENCRYPTION: Literal[{"description": "Enable heartbeat message encryption", "help": "Enable heartbeat message encryption.", "label": "Enable", "name": "enable"}, {"description": "Disable heartbeat message encryption", "help": "Disable heartbeat message encryption.", "label": "Disable", "name": "disable"}]
VALID_BODY_AUTHENTICATION: Literal[{"description": "Enable heartbeat message authentication", "help": "Enable heartbeat message authentication.", "label": "Enable", "name": "enable"}, {"description": "Disable heartbeat message authentication", "help": "Disable heartbeat message authentication.", "label": "Disable", "name": "disable"}]
VALID_BODY_HB_INTERVAL_IN_MILLISECONDS: Literal[{"description": "Each heartbeat interval is 100ms", "help": "Each heartbeat interval is 100ms.", "label": "100Ms", "name": "100ms"}, {"description": "Each heartbeat interval is 10ms", "help": "Each heartbeat interval is 10ms.", "label": "10Ms", "name": "10ms"}]
VALID_BODY_GRATUITOUS_ARPS: Literal[{"description": "Enable gratuitous ARPs", "help": "Enable gratuitous ARPs.", "label": "Enable", "name": "enable"}, {"description": "Disable gratuitous ARPs", "help": "Disable gratuitous ARPs.", "label": "Disable", "name": "disable"}]
VALID_BODY_SESSION_PICKUP: Literal[{"description": "Enable session pickup", "help": "Enable session pickup.", "label": "Enable", "name": "enable"}, {"description": "Disable session pickup", "help": "Disable session pickup.", "label": "Disable", "name": "disable"}]
VALID_BODY_SESSION_PICKUP_CONNECTIONLESS: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]
VALID_BODY_SESSION_PICKUP_EXPECTATION: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]
VALID_BODY_SESSION_PICKUP_NAT: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]
VALID_BODY_SESSION_PICKUP_DELAY: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]
VALID_BODY_LINK_FAILED_SIGNAL: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]
VALID_BODY_UPGRADE_MODE: Literal[{"description": "Upgrade all HA members at the same time", "help": "Upgrade all HA members at the same time.", "label": "Simultaneous", "name": "simultaneous"}, {"description": "Upgrade HA cluster without blocking network traffic", "help": "Upgrade HA cluster without blocking network traffic.", "label": "Uninterruptible", "name": "uninterruptible"}, {"description": "Upgrade local member only", "help": "Upgrade local member only.", "label": "Local Only", "name": "local-only"}, {"description": "Upgrade secondary member only", "help": "Upgrade secondary member only.", "label": "Secondary Only", "name": "secondary-only"}]
VALID_BODY_STANDALONE_MGMT_VDOM: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]
VALID_BODY_HA_MGMT_STATUS: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]
VALID_BODY_STANDALONE_CONFIG_SYNC: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]
VALID_BODY_UNICAST_STATUS: Literal[{"help": "Enable setting.", "label": "Enable", "name": "enable"}, {"help": "Disable setting.", "label": "Disable", "name": "disable"}]
VALID_BODY_SCHEDULE: Literal[{"description": "None", "help": "None.", "label": "None", "name": "none"}, {"description": "Least connection", "help": "Least connection.", "label": "Leastconnection", "name": "leastconnection"}, {"description": "Round robin", "help": "Round robin.", "label": "Round Robin", "name": "round-robin"}, {"description": "Weight round robin", "help": "Weight round robin.", "label": "Weight Round Robin", "name": "weight-round-robin"}, {"description": "Random", "help": "Random.", "label": "Random", "name": "random"}, {"description": "IP", "help": "IP.", "label": "Ip", "name": "ip"}, {"description": "IP port", "help": "IP port.", "label": "Ipport", "name": "ipport"}]
VALID_BODY_OVERRIDE: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]
VALID_BODY_PINGSERVER_SECONDARY_FORCE_RESET: Literal[{"description": "Enable force reset of secondary member after PING server failure", "help": "Enable force reset of secondary member after PING server failure.", "label": "Enable", "name": "enable"}, {"description": "Disable force reset of secondary member after PING server failure", "help": "Disable force reset of secondary member after PING server failure.", "label": "Disable", "name": "disable"}]
VALID_BODY_VCLUSTER_STATUS: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]
VALID_BODY_HA_DIRECT: Literal[{"description": "Enable using ha-mgmt interface for syslog, remote authentication (RADIUS), FortiAnalyzer, FortiSandbox, sFlow, and Netflow", "help": "Enable using ha-mgmt interface for syslog, remote authentication (RADIUS), FortiAnalyzer, FortiSandbox, sFlow, and Netflow.", "label": "Enable", "name": "enable"}, {"description": "Disable using ha-mgmt interface for syslog, remote authentication (RADIUS), FortiAnalyzer, FortiSandbox, sFlow, and Netflow", "help": "Disable using ha-mgmt interface for syslog, remote authentication (RADIUS), FortiAnalyzer, FortiSandbox, sFlow, and Netflow.", "label": "Disable", "name": "disable"}]
VALID_BODY_SSD_FAILOVER: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]
VALID_BODY_MEMORY_COMPATIBLE_MODE: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]
VALID_BODY_MEMORY_BASED_FAILOVER: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]
VALID_BODY_CHECK_SECONDARY_DEV_HEALTH: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]
VALID_BODY_IPSEC_PHASE2_PROPOSAL: Literal[{"description": "aes128-sha1    aes128-sha256:aes128-sha256    aes128-sha384:aes128-sha384    aes128-sha512:aes128-sha512    aes192-sha1:aes192-sha1    aes192-sha256:aes192-sha256    aes192-sha384:aes192-sha384    aes192-sha512:aes192-sha512    aes256-sha1:aes256-sha1    aes256-sha256:aes256-sha256    aes256-sha384:aes256-sha384    aes256-sha512:aes256-sha512    aes128gcm:aes128gcm    aes256gcm:aes256gcm    chacha20poly1305:chacha20poly1305", "help": "aes128-sha1", "label": "Aes128 Sha1", "name": "aes128-sha1"}, {"help": "aes128-sha256", "label": "Aes128 Sha256", "name": "aes128-sha256"}, {"help": "aes128-sha384", "label": "Aes128 Sha384", "name": "aes128-sha384"}, {"help": "aes128-sha512", "label": "Aes128 Sha512", "name": "aes128-sha512"}, {"help": "aes192-sha1", "label": "Aes192 Sha1", "name": "aes192-sha1"}, {"help": "aes192-sha256", "label": "Aes192 Sha256", "name": "aes192-sha256"}, {"help": "aes192-sha384", "label": "Aes192 Sha384", "name": "aes192-sha384"}, {"help": "aes192-sha512", "label": "Aes192 Sha512", "name": "aes192-sha512"}, {"help": "aes256-sha1", "label": "Aes256 Sha1", "name": "aes256-sha1"}, {"help": "aes256-sha256", "label": "Aes256 Sha256", "name": "aes256-sha256"}, {"help": "aes256-sha384", "label": "Aes256 Sha384", "name": "aes256-sha384"}, {"help": "aes256-sha512", "label": "Aes256 Sha512", "name": "aes256-sha512"}, {"help": "aes128gcm", "label": "Aes128Gcm", "name": "aes128gcm"}, {"help": "aes256gcm", "label": "Aes256Gcm", "name": "aes256gcm"}, {"help": "chacha20poly1305", "label": "Chacha20Poly1305", "name": "chacha20poly1305"}]
VALID_BODY_BOUNCE_INTF_UPON_FAILOVER: Literal[{"description": "Enable setting", "help": "Enable setting.", "label": "Enable", "name": "enable"}, {"description": "Disable setting", "help": "Disable setting.", "label": "Disable", "name": "disable"}]

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
    "VALID_BODY_MODE",
    "VALID_BODY_SYNC_PACKET_BALANCE",
    "VALID_BODY_UNICAST_HB",
    "VALID_BODY_LOAD_BALANCE_ALL",
    "VALID_BODY_SYNC_CONFIG",
    "VALID_BODY_ENCRYPTION",
    "VALID_BODY_AUTHENTICATION",
    "VALID_BODY_HB_INTERVAL_IN_MILLISECONDS",
    "VALID_BODY_GRATUITOUS_ARPS",
    "VALID_BODY_SESSION_PICKUP",
    "VALID_BODY_SESSION_PICKUP_CONNECTIONLESS",
    "VALID_BODY_SESSION_PICKUP_EXPECTATION",
    "VALID_BODY_SESSION_PICKUP_NAT",
    "VALID_BODY_SESSION_PICKUP_DELAY",
    "VALID_BODY_LINK_FAILED_SIGNAL",
    "VALID_BODY_UPGRADE_MODE",
    "VALID_BODY_STANDALONE_MGMT_VDOM",
    "VALID_BODY_HA_MGMT_STATUS",
    "VALID_BODY_STANDALONE_CONFIG_SYNC",
    "VALID_BODY_UNICAST_STATUS",
    "VALID_BODY_SCHEDULE",
    "VALID_BODY_OVERRIDE",
    "VALID_BODY_PINGSERVER_SECONDARY_FORCE_RESET",
    "VALID_BODY_VCLUSTER_STATUS",
    "VALID_BODY_HA_DIRECT",
    "VALID_BODY_SSD_FAILOVER",
    "VALID_BODY_MEMORY_COMPATIBLE_MODE",
    "VALID_BODY_MEMORY_BASED_FAILOVER",
    "VALID_BODY_CHECK_SECONDARY_DEV_HEALTH",
    "VALID_BODY_IPSEC_PHASE2_PROPOSAL",
    "VALID_BODY_BOUNCE_INTF_UPON_FAILOVER",
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