from typing import Any, Literal

# Enum type aliases for validation
VALID_BODY_STATUS: Literal[{"description": "Disable connection to this SDN Connector", "help": "Disable connection to this SDN Connector.", "label": "Disable", "name": "disable"}, {"description": "Enable connection to this SDN Connector", "help": "Enable connection to this SDN Connector.", "label": "Enable", "name": "enable"}]
VALID_BODY_TYPE: Literal[{"description": "Application Centric Infrastructure (ACI)", "help": "Application Centric Infrastructure (ACI).", "label": "Aci", "name": "aci"}, {"description": "AliCloud Service (ACS)", "help": "AliCloud Service (ACS).", "label": "Alicloud", "name": "alicloud"}, {"description": "Amazon Web Services (AWS)", "help": "Amazon Web Services (AWS).", "label": "Aws", "name": "aws"}, {"description": "Microsoft Azure", "help": "Microsoft Azure.", "label": "Azure", "name": "azure"}, {"description": "Google Cloud Platform (GCP)", "help": "Google Cloud Platform (GCP).", "label": "Gcp", "name": "gcp"}, {"description": "VMware NSX", "help": "VMware NSX.", "label": "Nsx", "name": "nsx"}, {"description": "Nuage VSP", "help": "Nuage VSP.", "label": "Nuage", "name": "nuage"}, {"description": "Oracle Cloud Infrastructure", "help": "Oracle Cloud Infrastructure.", "label": "Oci", "name": "oci"}, {"description": "OpenStack", "help": "OpenStack.", "label": "Openstack", "name": "openstack"}, {"description": "Kubernetes", "help": "Kubernetes.", "label": "Kubernetes", "name": "kubernetes"}, {"description": "VMware vSphere (vCenter \u0026 ESXi)", "help": "VMware vSphere (vCenter \u0026 ESXi).", "label": "Vmware", "name": "vmware"}, {"description": "Symantec Endpoint Protection Manager", "help": "Symantec Endpoint Protection Manager.", "label": "Sepm", "name": "sepm"}, {"description": "Application Centric Infrastructure (ACI Direct Connection)", "help": "Application Centric Infrastructure (ACI Direct Connection).", "label": "Aci Direct", "name": "aci-direct"}, {"description": "IBM Cloud Infrastructure", "help": "IBM Cloud Infrastructure.", "label": "Ibm", "name": "ibm"}, {"description": "Nutanix Prism Central", "help": "Nutanix Prism Central.", "label": "Nutanix", "name": "nutanix"}, {"description": "SAP Control", "help": "SAP Control.", "label": "Sap", "name": "sap"}]
VALID_BODY_USE_METADATA_IAM: Literal[{"description": "Disable using IAM role to call API", "help": "Disable using IAM role to call API.", "label": "Disable", "name": "disable"}, {"description": "Enable using IAM role to call API", "help": "Enable using IAM role to call API.", "label": "Enable", "name": "enable"}]
VALID_BODY_MICROSOFT_365: Literal[{"description": "Azure SDN connector    enable:Microsoft 365 SDN connector", "help": "Azure SDN connector", "label": "Disable", "name": "disable"}, {"help": "Microsoft 365 SDN connector", "label": "Enable", "name": "enable"}]
VALID_BODY_HA_STATUS: Literal[{"description": "Disable use for FortiGate HA service", "help": "Disable use for FortiGate HA service.", "label": "Disable", "name": "disable"}, {"description": "Enable use for FortiGate HA service", "help": "Enable use for FortiGate HA service.", "label": "Enable", "name": "enable"}]
VALID_BODY_VERIFY_CERTIFICATE: Literal[{"description": "Disable server certificate verification", "help": "Disable server certificate verification.", "label": "Disable", "name": "disable"}, {"description": "Enable server certificate verification", "help": "Enable server certificate verification.", "label": "Enable", "name": "enable"}]
VALID_BODY_ALT_RESOURCE_IP: Literal[{"description": "Disable AWS alternative resource IP", "help": "Disable AWS alternative resource IP.", "label": "Disable", "name": "disable"}, {"description": "Enable AWS alternative resource IP", "help": "Enable AWS alternative resource IP.", "label": "Enable", "name": "enable"}]
VALID_BODY_AZURE_REGION: Literal[{"description": "Global Azure Server", "help": "Global Azure Server.", "label": "Global", "name": "global"}, {"description": "China Azure Server", "help": "China Azure Server.", "label": "China", "name": "china"}, {"description": "Germany Azure Server", "help": "Germany Azure Server.", "label": "Germany", "name": "germany"}, {"description": "US Government Azure Server", "help": "US Government Azure Server.", "label": "Usgov", "name": "usgov"}, {"description": "Azure Stack Local Server", "help": "Azure Stack Local Server.", "label": "Local", "name": "local"}]
VALID_BODY_OCI_REGION_TYPE: Literal[{"description": "Commercial region", "help": "Commercial region.", "label": "Commercial", "name": "commercial"}, {"description": "Government region", "help": "Government region.", "label": "Government", "name": "government"}]
VALID_BODY_IBM_REGION: Literal[{"description": "US South (Dallas) Public Endpoint", "help": "US South (Dallas) Public Endpoint.", "label": "Dallas", "name": "dallas"}, {"description": "US East (Washington DC) Public Endpoint", "help": "US East (Washington DC) Public Endpoint.", "label": "Washington Dc", "name": "washington-dc"}, {"description": "United Kingdom (London) Public Endpoint", "help": "United Kingdom (London) Public Endpoint.", "label": "London", "name": "london"}, {"description": "Germany (Frankfurt) Public Endpoint", "help": "Germany (Frankfurt) Public Endpoint.", "label": "Frankfurt", "name": "frankfurt"}, {"description": "Australia (Sydney) Public Endpoint", "help": "Australia (Sydney) Public Endpoint.", "label": "Sydney", "name": "sydney"}, {"description": "Japan (Tokyo) Public Endpoint", "help": "Japan (Tokyo) Public Endpoint.", "label": "Tokyo", "name": "tokyo"}, {"description": "Japan (Osaka) Public Endpoint", "help": "Japan (Osaka) Public Endpoint.", "label": "Osaka", "name": "osaka"}, {"description": "Canada (Toronto) Public Endpoint", "help": "Canada (Toronto) Public Endpoint.", "label": "Toronto", "name": "toronto"}, {"description": "Brazil (Sao Paulo) Public Endpoint", "help": "Brazil (Sao Paulo) Public Endpoint.", "label": "Sao Paulo", "name": "sao-paulo"}, {"description": "Spain (Madrid) Public Endpoint", "help": "Spain (Madrid) Public Endpoint.", "label": "Madrid", "name": "madrid"}]

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
    "VALID_BODY_TYPE",
    "VALID_BODY_USE_METADATA_IAM",
    "VALID_BODY_MICROSOFT_365",
    "VALID_BODY_HA_STATUS",
    "VALID_BODY_VERIFY_CERTIFICATE",
    "VALID_BODY_ALT_RESOURCE_IP",
    "VALID_BODY_AZURE_REGION",
    "VALID_BODY_OCI_REGION_TYPE",
    "VALID_BODY_IBM_REGION",
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