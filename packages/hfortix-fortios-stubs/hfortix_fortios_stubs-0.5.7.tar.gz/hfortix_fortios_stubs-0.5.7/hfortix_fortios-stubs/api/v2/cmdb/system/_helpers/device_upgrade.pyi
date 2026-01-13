from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_STATUS: Literal[{"description": "No federated upgrade has been configured", "help": "No federated upgrade has been configured.", "label": "Disabled", "name": "disabled"}, {"description": "The upgrade has been configured", "help": "The upgrade has been configured.", "label": "Initialized", "name": "initialized"}, {"description": "The image is downloading in preparation for the upgrade", "help": "The image is downloading in preparation for the upgrade.", "label": "Downloading", "name": "downloading"}, {"description": "The image downloads are complete, but one or more devices have disconnected", "help": "The image downloads are complete, but one or more devices have disconnected.", "label": "Device Disconnected", "name": "device-disconnected"}, {"description": "The image download finished and the upgrade is pending", "help": "The image download finished and the upgrade is pending.", "label": "Ready", "name": "ready"}, {"description": "The upgrade is coordinating with other running upgrades", "help": "The upgrade is coordinating with other running upgrades.", "label": "Coordinating", "name": "coordinating"}, {"description": "The upgrade is confirmed and images are being staged", "help": "The upgrade is confirmed and images are being staged.", "label": "Staging", "name": "staging"}, {"description": "The upgrade is ready and final checks are in progress", "help": "The upgrade is ready and final checks are in progress.", "label": "Final Check", "name": "final-check"}, {"description": "The upgrade is ready and devices are being rebooted", "help": "The upgrade is ready and devices are being rebooted.", "label": "Upgrade Devices", "name": "upgrade-devices"}, {"description": "The upgrade was cancelled due to the tree not being ready", "help": "The upgrade was cancelled due to the tree not being ready.", "label": "Cancelled", "name": "cancelled"}, {"description": "The upgrade was confirmed and reboots are running", "help": "The upgrade was confirmed and reboots are running.", "label": "Confirmed", "name": "confirmed"}, {"description": "The upgrade completed successfully", "help": "The upgrade completed successfully.", "label": "Done", "name": "done"}, {"description": "The upgrade failed due to a local issue", "help": "The upgrade failed due to a local issue.", "label": "Failed", "name": "failed"}]
VALID_BODY_TIMING: Literal[{"description": "Begin the upgrade immediately", "help": "Begin the upgrade immediately.", "label": "Immediate", "name": "immediate"}, {"description": "Begin the upgrade at a configured time", "help": "Begin the upgrade at a configured time.", "label": "Scheduled", "name": "scheduled"}]
VALID_BODY_DEVICE_TYPE: Literal[{"description": "This device is a FortiGate", "help": "This device is a FortiGate.", "label": "Fortigate", "name": "fortigate"}, {"description": "This device is a FortiSwitch", "help": "This device is a FortiSwitch.", "label": "Fortiswitch", "name": "fortiswitch"}, {"description": "This device is a FortiAP", "help": "This device is a FortiAP.", "label": "Fortiap", "name": "fortiap"}, {"description": "This device is a FortiExtender", "help": "This device is a FortiExtender.", "label": "Fortiextender", "name": "fortiextender"}]
VALID_BODY_ALLOW_DOWNLOAD: Literal[{"description": "Allow download of images", "help": "Allow download of images.", "label": "Enable", "name": "enable"}, {"description": "Disable download of images", "help": "Disable download of images.", "label": "Disable", "name": "disable"}]
VALID_BODY_FAILURE_REASON: Literal[{"description": "No failure", "help": "No failure.", "label": "None", "name": "none"}, {"description": "An internal error occurred", "help": "An internal error occurred.", "label": "Internal", "name": "internal"}, {"description": "The upgrade timed out", "help": "The upgrade timed out.", "label": "Timeout", "name": "timeout"}, {"description": "The device type was not supported by the FortiGate", "help": "The device type was not supported by the FortiGate.", "label": "Device Type Unsupported", "name": "device-type-unsupported"}, {"description": "The image could not be downloaded", "help": "The image could not be downloaded.", "label": "Download Failed", "name": "download-failed"}, {"description": "The device was disconnected from the FortiGate", "help": "The device was disconnected from the FortiGate.", "label": "Device Missing", "name": "device-missing"}, {"description": "An image matching the device and version could not be found", "help": "An image matching the device and version could not be found.", "label": "Version Unavailable", "name": "version-unavailable"}, {"description": "The image could not be pushed to the device", "help": "The image could not be pushed to the device.", "label": "Staging Failed", "name": "staging-failed"}, {"description": "The device could not be rebooted", "help": "The device could not be rebooted.", "label": "Reboot Failed", "name": "reboot-failed"}, {"description": "The device did not reconnect after rebooting", "help": "The device did not reconnect after rebooting.", "label": "Device Not Reconnected", "name": "device-not-reconnected"}, {"description": "A device in the Security Fabric tree was not ready", "help": "A device in the Security Fabric tree was not ready.", "label": "Node Not Ready", "name": "node-not-ready"}, {"description": "The coordinating FortiGate did not confirm the upgrade", "help": "The coordinating FortiGate did not confirm the upgrade.", "label": "No Final Confirmation", "name": "no-final-confirmation"}, {"description": "A downstream FortiGate did not initiate final confirmation", "help": "A downstream FortiGate did not initiate final confirmation.", "label": "No Confirmation Query", "name": "no-confirmation-query"}, {"description": "Configuration errors encountered during the upgrade", "help": "Configuration errors encountered during the upgrade.", "label": "Config Error Log Nonempty", "name": "config-error-log-nonempty"}, {"description": "The Security Fabric is disabled on the root FortiGate    firmware-changed:Firmware changed after the upgrade was set up", "help": "The Security Fabric is disabled on the root FortiGate", "label": "Csf Tree Not Supported", "name": "csf-tree-not-supported"}, {"help": "Firmware changed after the upgrade was set up.", "label": "Firmware Changed", "name": "firmware-changed"}, {"description": "A device in the Security Fabric tree failed", "help": "A device in the Security Fabric tree failed.", "label": "Node Failed", "name": "node-failed"}, {"description": "The firmware image is missing and download is not allowed", "help": "The firmware image is missing and download is not allowed", "label": "Image Missing", "name": "image-missing"}]

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
    "VALID_BODY_TIMING",
    "VALID_BODY_DEVICE_TYPE",
    "VALID_BODY_ALLOW_DOWNLOAD",
    "VALID_BODY_FAILURE_REASON",
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