from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class DeviceUpgradePayload(TypedDict, total=False):
    """
    Type hints for system/device_upgrade payload fields.
    
    Independent upgrades for managed devices.
    
    **Related Resources:**

    Dependencies (resources this endpoint references):
        - :class:`~.system.vdom.VdomEndpoint` (via: vdom)

    **Usage:**
        payload: DeviceUpgradePayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    vdom: NotRequired[str]  # Limit upgrade to this virtual domain (VDOM).
    status: Literal[{"description": "No federated upgrade has been configured", "help": "No federated upgrade has been configured.", "label": "Disabled", "name": "disabled"}, {"description": "The upgrade has been configured", "help": "The upgrade has been configured.", "label": "Initialized", "name": "initialized"}, {"description": "The image is downloading in preparation for the upgrade", "help": "The image is downloading in preparation for the upgrade.", "label": "Downloading", "name": "downloading"}, {"description": "The image downloads are complete, but one or more devices have disconnected", "help": "The image downloads are complete, but one or more devices have disconnected.", "label": "Device Disconnected", "name": "device-disconnected"}, {"description": "The image download finished and the upgrade is pending", "help": "The image download finished and the upgrade is pending.", "label": "Ready", "name": "ready"}, {"description": "The upgrade is coordinating with other running upgrades", "help": "The upgrade is coordinating with other running upgrades.", "label": "Coordinating", "name": "coordinating"}, {"description": "The upgrade is confirmed and images are being staged", "help": "The upgrade is confirmed and images are being staged.", "label": "Staging", "name": "staging"}, {"description": "The upgrade is ready and final checks are in progress", "help": "The upgrade is ready and final checks are in progress.", "label": "Final Check", "name": "final-check"}, {"description": "The upgrade is ready and devices are being rebooted", "help": "The upgrade is ready and devices are being rebooted.", "label": "Upgrade Devices", "name": "upgrade-devices"}, {"description": "The upgrade was cancelled due to the tree not being ready", "help": "The upgrade was cancelled due to the tree not being ready.", "label": "Cancelled", "name": "cancelled"}, {"description": "The upgrade was confirmed and reboots are running", "help": "The upgrade was confirmed and reboots are running.", "label": "Confirmed", "name": "confirmed"}, {"description": "The upgrade completed successfully", "help": "The upgrade completed successfully.", "label": "Done", "name": "done"}, {"description": "The upgrade failed due to a local issue", "help": "The upgrade failed due to a local issue.", "label": "Failed", "name": "failed"}]  # Current status of the upgrade.
    ha_reboot_controller: NotRequired[str]  # Serial number of the FortiGate unit that will control the re
    next_path_index: int  # The index of the next image to upgrade to.
    known_ha_members: list[dict[str, Any]]  # Known members of the HA cluster. If a member is missing at u
    initial_version: NotRequired[str]  # Firmware version when the upgrade was set up.
    starter_admin: NotRequired[str]  # Admin that started the upgrade.
    serial: str  # Serial number of the node to include.
    timing: Literal[{"description": "Begin the upgrade immediately", "help": "Begin the upgrade immediately.", "label": "Immediate", "name": "immediate"}, {"description": "Begin the upgrade at a configured time", "help": "Begin the upgrade at a configured time.", "label": "Scheduled", "name": "scheduled"}]  # Run immediately or at a scheduled time.
    maximum_minutes: int  # Maximum number of minutes to allow for immediate upgrade pre
    time: str  # Scheduled upgrade execution time in UTC (hh:mm yyyy/mm/dd UT
    setup_time: str  # Upgrade preparation start time in UTC (hh:mm yyyy/mm/dd UTC)
    upgrade_path: str  # Fortinet OS image versions to upgrade through in major-minor
    device_type: Literal[{"description": "This device is a FortiGate", "help": "This device is a FortiGate.", "label": "Fortigate", "name": "fortigate"}, {"description": "This device is a FortiSwitch", "help": "This device is a FortiSwitch.", "label": "Fortiswitch", "name": "fortiswitch"}, {"description": "This device is a FortiAP", "help": "This device is a FortiAP.", "label": "Fortiap", "name": "fortiap"}, {"description": "This device is a FortiExtender", "help": "This device is a FortiExtender.", "label": "Fortiextender", "name": "fortiextender"}]  # Fortinet device type.
    allow_download: NotRequired[Literal[{"description": "Allow download of images", "help": "Allow download of images.", "label": "Enable", "name": "enable"}, {"description": "Disable download of images", "help": "Disable download of images.", "label": "Disable", "name": "disable"}]]  # Enable/disable download firmware images.
    failure_reason: NotRequired[Literal[{"description": "No failure", "help": "No failure.", "label": "None", "name": "none"}, {"description": "An internal error occurred", "help": "An internal error occurred.", "label": "Internal", "name": "internal"}, {"description": "The upgrade timed out", "help": "The upgrade timed out.", "label": "Timeout", "name": "timeout"}, {"description": "The device type was not supported by the FortiGate", "help": "The device type was not supported by the FortiGate.", "label": "Device Type Unsupported", "name": "device-type-unsupported"}, {"description": "The image could not be downloaded", "help": "The image could not be downloaded.", "label": "Download Failed", "name": "download-failed"}, {"description": "The device was disconnected from the FortiGate", "help": "The device was disconnected from the FortiGate.", "label": "Device Missing", "name": "device-missing"}, {"description": "An image matching the device and version could not be found", "help": "An image matching the device and version could not be found.", "label": "Version Unavailable", "name": "version-unavailable"}, {"description": "The image could not be pushed to the device", "help": "The image could not be pushed to the device.", "label": "Staging Failed", "name": "staging-failed"}, {"description": "The device could not be rebooted", "help": "The device could not be rebooted.", "label": "Reboot Failed", "name": "reboot-failed"}, {"description": "The device did not reconnect after rebooting", "help": "The device did not reconnect after rebooting.", "label": "Device Not Reconnected", "name": "device-not-reconnected"}, {"description": "A device in the Security Fabric tree was not ready", "help": "A device in the Security Fabric tree was not ready.", "label": "Node Not Ready", "name": "node-not-ready"}, {"description": "The coordinating FortiGate did not confirm the upgrade", "help": "The coordinating FortiGate did not confirm the upgrade.", "label": "No Final Confirmation", "name": "no-final-confirmation"}, {"description": "A downstream FortiGate did not initiate final confirmation", "help": "A downstream FortiGate did not initiate final confirmation.", "label": "No Confirmation Query", "name": "no-confirmation-query"}, {"description": "Configuration errors encountered during the upgrade", "help": "Configuration errors encountered during the upgrade.", "label": "Config Error Log Nonempty", "name": "config-error-log-nonempty"}, {"description": "The Security Fabric is disabled on the root FortiGate    firmware-changed:Firmware changed after the upgrade was set up", "help": "The Security Fabric is disabled on the root FortiGate", "label": "Csf Tree Not Supported", "name": "csf-tree-not-supported"}, {"help": "Firmware changed after the upgrade was set up.", "label": "Firmware Changed", "name": "firmware-changed"}, {"description": "A device in the Security Fabric tree failed", "help": "A device in the Security Fabric tree failed.", "label": "Node Failed", "name": "node-failed"}, {"description": "The firmware image is missing and download is not allowed", "help": "The firmware image is missing and download is not allowed", "label": "Image Missing", "name": "image-missing"}]]  # Upgrade failure reason.


class DeviceUpgrade:
    """
    Independent upgrades for managed devices.
    
    Path: system/device_upgrade
    Category: cmdb
    Primary Key: serial
    """
    
    # Overloads for get() with response_mode="object"
    @overload
    def get(
        self,
        serial: str | None = ...,
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
        serial: str,
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
        serial: str | None = ...,
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
        serial: str | None = ...,
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
        serial: str | None = ...,
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
        payload_dict: DeviceUpgradePayload | None = ...,
        status: Literal[{"description": "No federated upgrade has been configured", "help": "No federated upgrade has been configured.", "label": "Disabled", "name": "disabled"}, {"description": "The upgrade has been configured", "help": "The upgrade has been configured.", "label": "Initialized", "name": "initialized"}, {"description": "The image is downloading in preparation for the upgrade", "help": "The image is downloading in preparation for the upgrade.", "label": "Downloading", "name": "downloading"}, {"description": "The image downloads are complete, but one or more devices have disconnected", "help": "The image downloads are complete, but one or more devices have disconnected.", "label": "Device Disconnected", "name": "device-disconnected"}, {"description": "The image download finished and the upgrade is pending", "help": "The image download finished and the upgrade is pending.", "label": "Ready", "name": "ready"}, {"description": "The upgrade is coordinating with other running upgrades", "help": "The upgrade is coordinating with other running upgrades.", "label": "Coordinating", "name": "coordinating"}, {"description": "The upgrade is confirmed and images are being staged", "help": "The upgrade is confirmed and images are being staged.", "label": "Staging", "name": "staging"}, {"description": "The upgrade is ready and final checks are in progress", "help": "The upgrade is ready and final checks are in progress.", "label": "Final Check", "name": "final-check"}, {"description": "The upgrade is ready and devices are being rebooted", "help": "The upgrade is ready and devices are being rebooted.", "label": "Upgrade Devices", "name": "upgrade-devices"}, {"description": "The upgrade was cancelled due to the tree not being ready", "help": "The upgrade was cancelled due to the tree not being ready.", "label": "Cancelled", "name": "cancelled"}, {"description": "The upgrade was confirmed and reboots are running", "help": "The upgrade was confirmed and reboots are running.", "label": "Confirmed", "name": "confirmed"}, {"description": "The upgrade completed successfully", "help": "The upgrade completed successfully.", "label": "Done", "name": "done"}, {"description": "The upgrade failed due to a local issue", "help": "The upgrade failed due to a local issue.", "label": "Failed", "name": "failed"}] | None = ...,
        ha_reboot_controller: str | None = ...,
        next_path_index: int | None = ...,
        known_ha_members: list[dict[str, Any]] | None = ...,
        initial_version: str | None = ...,
        starter_admin: str | None = ...,
        serial: str | None = ...,
        timing: Literal[{"description": "Begin the upgrade immediately", "help": "Begin the upgrade immediately.", "label": "Immediate", "name": "immediate"}, {"description": "Begin the upgrade at a configured time", "help": "Begin the upgrade at a configured time.", "label": "Scheduled", "name": "scheduled"}] | None = ...,
        maximum_minutes: int | None = ...,
        time: str | None = ...,
        setup_time: str | None = ...,
        upgrade_path: str | None = ...,
        device_type: Literal[{"description": "This device is a FortiGate", "help": "This device is a FortiGate.", "label": "Fortigate", "name": "fortigate"}, {"description": "This device is a FortiSwitch", "help": "This device is a FortiSwitch.", "label": "Fortiswitch", "name": "fortiswitch"}, {"description": "This device is a FortiAP", "help": "This device is a FortiAP.", "label": "Fortiap", "name": "fortiap"}, {"description": "This device is a FortiExtender", "help": "This device is a FortiExtender.", "label": "Fortiextender", "name": "fortiextender"}] | None = ...,
        allow_download: Literal[{"description": "Allow download of images", "help": "Allow download of images.", "label": "Enable", "name": "enable"}, {"description": "Disable download of images", "help": "Disable download of images.", "label": "Disable", "name": "disable"}] | None = ...,
        failure_reason: Literal[{"description": "No failure", "help": "No failure.", "label": "None", "name": "none"}, {"description": "An internal error occurred", "help": "An internal error occurred.", "label": "Internal", "name": "internal"}, {"description": "The upgrade timed out", "help": "The upgrade timed out.", "label": "Timeout", "name": "timeout"}, {"description": "The device type was not supported by the FortiGate", "help": "The device type was not supported by the FortiGate.", "label": "Device Type Unsupported", "name": "device-type-unsupported"}, {"description": "The image could not be downloaded", "help": "The image could not be downloaded.", "label": "Download Failed", "name": "download-failed"}, {"description": "The device was disconnected from the FortiGate", "help": "The device was disconnected from the FortiGate.", "label": "Device Missing", "name": "device-missing"}, {"description": "An image matching the device and version could not be found", "help": "An image matching the device and version could not be found.", "label": "Version Unavailable", "name": "version-unavailable"}, {"description": "The image could not be pushed to the device", "help": "The image could not be pushed to the device.", "label": "Staging Failed", "name": "staging-failed"}, {"description": "The device could not be rebooted", "help": "The device could not be rebooted.", "label": "Reboot Failed", "name": "reboot-failed"}, {"description": "The device did not reconnect after rebooting", "help": "The device did not reconnect after rebooting.", "label": "Device Not Reconnected", "name": "device-not-reconnected"}, {"description": "A device in the Security Fabric tree was not ready", "help": "A device in the Security Fabric tree was not ready.", "label": "Node Not Ready", "name": "node-not-ready"}, {"description": "The coordinating FortiGate did not confirm the upgrade", "help": "The coordinating FortiGate did not confirm the upgrade.", "label": "No Final Confirmation", "name": "no-final-confirmation"}, {"description": "A downstream FortiGate did not initiate final confirmation", "help": "A downstream FortiGate did not initiate final confirmation.", "label": "No Confirmation Query", "name": "no-confirmation-query"}, {"description": "Configuration errors encountered during the upgrade", "help": "Configuration errors encountered during the upgrade.", "label": "Config Error Log Nonempty", "name": "config-error-log-nonempty"}, {"description": "The Security Fabric is disabled on the root FortiGate    firmware-changed:Firmware changed after the upgrade was set up", "help": "The Security Fabric is disabled on the root FortiGate", "label": "Csf Tree Not Supported", "name": "csf-tree-not-supported"}, {"help": "Firmware changed after the upgrade was set up.", "label": "Firmware Changed", "name": "firmware-changed"}, {"description": "A device in the Security Fabric tree failed", "help": "A device in the Security Fabric tree failed.", "label": "Node Failed", "name": "node-failed"}, {"description": "The firmware image is missing and download is not allowed", "help": "The firmware image is missing and download is not allowed", "label": "Image Missing", "name": "image-missing"}] | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: DeviceUpgradePayload | None = ...,
        status: Literal[{"description": "No federated upgrade has been configured", "help": "No federated upgrade has been configured.", "label": "Disabled", "name": "disabled"}, {"description": "The upgrade has been configured", "help": "The upgrade has been configured.", "label": "Initialized", "name": "initialized"}, {"description": "The image is downloading in preparation for the upgrade", "help": "The image is downloading in preparation for the upgrade.", "label": "Downloading", "name": "downloading"}, {"description": "The image downloads are complete, but one or more devices have disconnected", "help": "The image downloads are complete, but one or more devices have disconnected.", "label": "Device Disconnected", "name": "device-disconnected"}, {"description": "The image download finished and the upgrade is pending", "help": "The image download finished and the upgrade is pending.", "label": "Ready", "name": "ready"}, {"description": "The upgrade is coordinating with other running upgrades", "help": "The upgrade is coordinating with other running upgrades.", "label": "Coordinating", "name": "coordinating"}, {"description": "The upgrade is confirmed and images are being staged", "help": "The upgrade is confirmed and images are being staged.", "label": "Staging", "name": "staging"}, {"description": "The upgrade is ready and final checks are in progress", "help": "The upgrade is ready and final checks are in progress.", "label": "Final Check", "name": "final-check"}, {"description": "The upgrade is ready and devices are being rebooted", "help": "The upgrade is ready and devices are being rebooted.", "label": "Upgrade Devices", "name": "upgrade-devices"}, {"description": "The upgrade was cancelled due to the tree not being ready", "help": "The upgrade was cancelled due to the tree not being ready.", "label": "Cancelled", "name": "cancelled"}, {"description": "The upgrade was confirmed and reboots are running", "help": "The upgrade was confirmed and reboots are running.", "label": "Confirmed", "name": "confirmed"}, {"description": "The upgrade completed successfully", "help": "The upgrade completed successfully.", "label": "Done", "name": "done"}, {"description": "The upgrade failed due to a local issue", "help": "The upgrade failed due to a local issue.", "label": "Failed", "name": "failed"}] | None = ...,
        ha_reboot_controller: str | None = ...,
        next_path_index: int | None = ...,
        known_ha_members: list[dict[str, Any]] | None = ...,
        initial_version: str | None = ...,
        starter_admin: str | None = ...,
        serial: str | None = ...,
        timing: Literal[{"description": "Begin the upgrade immediately", "help": "Begin the upgrade immediately.", "label": "Immediate", "name": "immediate"}, {"description": "Begin the upgrade at a configured time", "help": "Begin the upgrade at a configured time.", "label": "Scheduled", "name": "scheduled"}] | None = ...,
        maximum_minutes: int | None = ...,
        time: str | None = ...,
        setup_time: str | None = ...,
        upgrade_path: str | None = ...,
        device_type: Literal[{"description": "This device is a FortiGate", "help": "This device is a FortiGate.", "label": "Fortigate", "name": "fortigate"}, {"description": "This device is a FortiSwitch", "help": "This device is a FortiSwitch.", "label": "Fortiswitch", "name": "fortiswitch"}, {"description": "This device is a FortiAP", "help": "This device is a FortiAP.", "label": "Fortiap", "name": "fortiap"}, {"description": "This device is a FortiExtender", "help": "This device is a FortiExtender.", "label": "Fortiextender", "name": "fortiextender"}] | None = ...,
        allow_download: Literal[{"description": "Allow download of images", "help": "Allow download of images.", "label": "Enable", "name": "enable"}, {"description": "Disable download of images", "help": "Disable download of images.", "label": "Disable", "name": "disable"}] | None = ...,
        failure_reason: Literal[{"description": "No failure", "help": "No failure.", "label": "None", "name": "none"}, {"description": "An internal error occurred", "help": "An internal error occurred.", "label": "Internal", "name": "internal"}, {"description": "The upgrade timed out", "help": "The upgrade timed out.", "label": "Timeout", "name": "timeout"}, {"description": "The device type was not supported by the FortiGate", "help": "The device type was not supported by the FortiGate.", "label": "Device Type Unsupported", "name": "device-type-unsupported"}, {"description": "The image could not be downloaded", "help": "The image could not be downloaded.", "label": "Download Failed", "name": "download-failed"}, {"description": "The device was disconnected from the FortiGate", "help": "The device was disconnected from the FortiGate.", "label": "Device Missing", "name": "device-missing"}, {"description": "An image matching the device and version could not be found", "help": "An image matching the device and version could not be found.", "label": "Version Unavailable", "name": "version-unavailable"}, {"description": "The image could not be pushed to the device", "help": "The image could not be pushed to the device.", "label": "Staging Failed", "name": "staging-failed"}, {"description": "The device could not be rebooted", "help": "The device could not be rebooted.", "label": "Reboot Failed", "name": "reboot-failed"}, {"description": "The device did not reconnect after rebooting", "help": "The device did not reconnect after rebooting.", "label": "Device Not Reconnected", "name": "device-not-reconnected"}, {"description": "A device in the Security Fabric tree was not ready", "help": "A device in the Security Fabric tree was not ready.", "label": "Node Not Ready", "name": "node-not-ready"}, {"description": "The coordinating FortiGate did not confirm the upgrade", "help": "The coordinating FortiGate did not confirm the upgrade.", "label": "No Final Confirmation", "name": "no-final-confirmation"}, {"description": "A downstream FortiGate did not initiate final confirmation", "help": "A downstream FortiGate did not initiate final confirmation.", "label": "No Confirmation Query", "name": "no-confirmation-query"}, {"description": "Configuration errors encountered during the upgrade", "help": "Configuration errors encountered during the upgrade.", "label": "Config Error Log Nonempty", "name": "config-error-log-nonempty"}, {"description": "The Security Fabric is disabled on the root FortiGate    firmware-changed:Firmware changed after the upgrade was set up", "help": "The Security Fabric is disabled on the root FortiGate", "label": "Csf Tree Not Supported", "name": "csf-tree-not-supported"}, {"help": "Firmware changed after the upgrade was set up.", "label": "Firmware Changed", "name": "firmware-changed"}, {"description": "A device in the Security Fabric tree failed", "help": "A device in the Security Fabric tree failed.", "label": "Node Failed", "name": "node-failed"}, {"description": "The firmware image is missing and download is not allowed", "help": "The firmware image is missing and download is not allowed", "label": "Image Missing", "name": "image-missing"}] | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def delete(
        self,
        serial: str | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def exists(
        self,
        serial: str,
        vdom: str | bool | None = ...,
    ) -> Union[bool, Coroutine[Any, Any, bool]]: ...
    
    def set(
        self,
        payload_dict: DeviceUpgradePayload | None = ...,
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
    "DeviceUpgrade",
    "DeviceUpgradePayload",
]