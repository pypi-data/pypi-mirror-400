from typing import TypedDict, Literal, NotRequired, Any, Coroutine, Union, overload
from hfortix_fortios.models import FortiObject

# Payload TypedDict for IDE autocomplete
class SdnConnectorPayload(TypedDict, total=False):
    """
    Type hints for system/sdn_connector payload fields.
    
    Configure connection to SDN Connector.
    
    **Related Resources:**

    Dependencies (resources this endpoint references):
        - :class:`~.certificate.ca.CaEndpoint` (via: server-ca-cert)
        - :class:`~.certificate.local.LocalEndpoint` (via: oci-cert)
        - :class:`~.certificate.remote.RemoteEndpoint` (via: server-ca-cert, server-cert)
        - :class:`~.system.sdn-proxy.SdnProxyEndpoint` (via: proxy)
        - :class:`~.system.vdom.VdomEndpoint` (via: vdom)

    **Usage:**
        payload: SdnConnectorPayload = {
            "field": "value",  # <- autocomplete shows all fields
        }
    """
    name: NotRequired[str]  # SDN connector name.
    status: Literal[{"description": "Disable connection to this SDN Connector", "help": "Disable connection to this SDN Connector.", "label": "Disable", "name": "disable"}, {"description": "Enable connection to this SDN Connector", "help": "Enable connection to this SDN Connector.", "label": "Enable", "name": "enable"}]  # Enable/disable connection to the remote SDN connector.
    type: Literal[{"description": "Application Centric Infrastructure (ACI)", "help": "Application Centric Infrastructure (ACI).", "label": "Aci", "name": "aci"}, {"description": "AliCloud Service (ACS)", "help": "AliCloud Service (ACS).", "label": "Alicloud", "name": "alicloud"}, {"description": "Amazon Web Services (AWS)", "help": "Amazon Web Services (AWS).", "label": "Aws", "name": "aws"}, {"description": "Microsoft Azure", "help": "Microsoft Azure.", "label": "Azure", "name": "azure"}, {"description": "Google Cloud Platform (GCP)", "help": "Google Cloud Platform (GCP).", "label": "Gcp", "name": "gcp"}, {"description": "VMware NSX", "help": "VMware NSX.", "label": "Nsx", "name": "nsx"}, {"description": "Nuage VSP", "help": "Nuage VSP.", "label": "Nuage", "name": "nuage"}, {"description": "Oracle Cloud Infrastructure", "help": "Oracle Cloud Infrastructure.", "label": "Oci", "name": "oci"}, {"description": "OpenStack", "help": "OpenStack.", "label": "Openstack", "name": "openstack"}, {"description": "Kubernetes", "help": "Kubernetes.", "label": "Kubernetes", "name": "kubernetes"}, {"description": "VMware vSphere (vCenter \u0026 ESXi)", "help": "VMware vSphere (vCenter \u0026 ESXi).", "label": "Vmware", "name": "vmware"}, {"description": "Symantec Endpoint Protection Manager", "help": "Symantec Endpoint Protection Manager.", "label": "Sepm", "name": "sepm"}, {"description": "Application Centric Infrastructure (ACI Direct Connection)", "help": "Application Centric Infrastructure (ACI Direct Connection).", "label": "Aci Direct", "name": "aci-direct"}, {"description": "IBM Cloud Infrastructure", "help": "IBM Cloud Infrastructure.", "label": "Ibm", "name": "ibm"}, {"description": "Nutanix Prism Central", "help": "Nutanix Prism Central.", "label": "Nutanix", "name": "nutanix"}, {"description": "SAP Control", "help": "SAP Control.", "label": "Sap", "name": "sap"}]  # Type of SDN connector.
    proxy: NotRequired[str]  # SDN proxy.
    use_metadata_iam: Literal[{"description": "Disable using IAM role to call API", "help": "Disable using IAM role to call API.", "label": "Disable", "name": "disable"}, {"description": "Enable using IAM role to call API", "help": "Enable using IAM role to call API.", "label": "Enable", "name": "enable"}]  # Enable/disable use of IAM role from metadata to call API.
    microsoft_365: Literal[{"description": "Azure SDN connector    enable:Microsoft 365 SDN connector", "help": "Azure SDN connector", "label": "Disable", "name": "disable"}, {"help": "Microsoft 365 SDN connector", "label": "Enable", "name": "enable"}]  # Enable to use as Microsoft 365 connector.
    ha_status: Literal[{"description": "Disable use for FortiGate HA service", "help": "Disable use for FortiGate HA service.", "label": "Disable", "name": "disable"}, {"description": "Enable use for FortiGate HA service", "help": "Enable use for FortiGate HA service.", "label": "Enable", "name": "enable"}]  # Enable/disable use for FortiGate HA service.
    verify_certificate: Literal[{"description": "Disable server certificate verification", "help": "Disable server certificate verification.", "label": "Disable", "name": "disable"}, {"description": "Enable server certificate verification", "help": "Enable server certificate verification.", "label": "Enable", "name": "enable"}]  # Enable/disable server certificate verification.
    vdom: NotRequired[str]  # Virtual domain name of the remote SDN connector.
    server: str  # Server address of the remote SDN connector.
    server_list: list[dict[str, Any]]  # Server address list of the remote SDN connector.
    server_port: NotRequired[int]  # Port number of the remote SDN connector.
    message_server_port: NotRequired[int]  # HTTP port number of the SAP message server.
    username: str  # Username of the remote SDN connector as login credentials.
    password: str  # Password of the remote SDN connector as login credentials.
    vcenter_server: NotRequired[str]  # vCenter server address for NSX quarantine.
    vcenter_username: NotRequired[str]  # vCenter server username for NSX quarantine.
    vcenter_password: NotRequired[str]  # vCenter server password for NSX quarantine.
    access_key: str  # AWS / ACS access key ID.
    secret_key: str  # AWS / ACS secret access key.
    region: str  # AWS / ACS region name.
    vpc_id: NotRequired[str]  # AWS VPC ID.
    alt_resource_ip: NotRequired[Literal[{"description": "Disable AWS alternative resource IP", "help": "Disable AWS alternative resource IP.", "label": "Disable", "name": "disable"}, {"description": "Enable AWS alternative resource IP", "help": "Enable AWS alternative resource IP.", "label": "Enable", "name": "enable"}]]  # Enable/disable AWS alternative resource IP.
    external_account_list: NotRequired[list[dict[str, Any]]]  # Configure AWS external account list.
    tenant_id: NotRequired[str]  # Tenant ID (directory ID).
    client_id: NotRequired[str]  # Azure client ID (application ID).
    client_secret: NotRequired[str]  # Azure client secret (application key).
    subscription_id: NotRequired[str]  # Azure subscription ID.
    resource_group: NotRequired[str]  # Azure resource group.
    login_endpoint: NotRequired[str]  # Azure Stack login endpoint.
    resource_url: NotRequired[str]  # Azure Stack resource URL.
    azure_region: NotRequired[Literal[{"description": "Global Azure Server", "help": "Global Azure Server.", "label": "Global", "name": "global"}, {"description": "China Azure Server", "help": "China Azure Server.", "label": "China", "name": "china"}, {"description": "Germany Azure Server", "help": "Germany Azure Server.", "label": "Germany", "name": "germany"}, {"description": "US Government Azure Server", "help": "US Government Azure Server.", "label": "Usgov", "name": "usgov"}, {"description": "Azure Stack Local Server", "help": "Azure Stack Local Server.", "label": "Local", "name": "local"}]]  # Azure server region.
    nic: NotRequired[list[dict[str, Any]]]  # Configure Azure network interface.
    route_table: NotRequired[list[dict[str, Any]]]  # Configure Azure route table.
    user_id: NotRequired[str]  # User ID.
    compartment_list: NotRequired[list[dict[str, Any]]]  # Configure OCI compartment list.
    oci_region_list: NotRequired[list[dict[str, Any]]]  # Configure OCI region list.
    oci_region_type: Literal[{"description": "Commercial region", "help": "Commercial region.", "label": "Commercial", "name": "commercial"}, {"description": "Government region", "help": "Government region.", "label": "Government", "name": "government"}]  # OCI region type.
    oci_cert: NotRequired[str]  # OCI certificate.
    oci_fingerprint: NotRequired[str]  # OCI pubkey fingerprint.
    external_ip: NotRequired[list[dict[str, Any]]]  # Configure GCP external IP.
    route: NotRequired[list[dict[str, Any]]]  # Configure GCP route.
    gcp_project_list: NotRequired[list[dict[str, Any]]]  # Configure GCP project list.
    forwarding_rule: NotRequired[list[dict[str, Any]]]  # Configure GCP forwarding rule.
    service_account: str  # GCP service account email.
    private_key: str  # Private key of GCP service account.
    secret_token: str  # Secret token of Kubernetes service account.
    domain: NotRequired[str]  # Domain name.
    group_name: NotRequired[str]  # Full path group name of computers.
    server_cert: NotRequired[str]  # Trust servers that contain this certificate only.
    server_ca_cert: NotRequired[str]  # Trust only those servers whose certificate is directly/indir
    api_key: str  # IBM cloud API key or service ID API key.
    ibm_region: Literal[{"description": "US South (Dallas) Public Endpoint", "help": "US South (Dallas) Public Endpoint.", "label": "Dallas", "name": "dallas"}, {"description": "US East (Washington DC) Public Endpoint", "help": "US East (Washington DC) Public Endpoint.", "label": "Washington Dc", "name": "washington-dc"}, {"description": "United Kingdom (London) Public Endpoint", "help": "United Kingdom (London) Public Endpoint.", "label": "London", "name": "london"}, {"description": "Germany (Frankfurt) Public Endpoint", "help": "Germany (Frankfurt) Public Endpoint.", "label": "Frankfurt", "name": "frankfurt"}, {"description": "Australia (Sydney) Public Endpoint", "help": "Australia (Sydney) Public Endpoint.", "label": "Sydney", "name": "sydney"}, {"description": "Japan (Tokyo) Public Endpoint", "help": "Japan (Tokyo) Public Endpoint.", "label": "Tokyo", "name": "tokyo"}, {"description": "Japan (Osaka) Public Endpoint", "help": "Japan (Osaka) Public Endpoint.", "label": "Osaka", "name": "osaka"}, {"description": "Canada (Toronto) Public Endpoint", "help": "Canada (Toronto) Public Endpoint.", "label": "Toronto", "name": "toronto"}, {"description": "Brazil (Sao Paulo) Public Endpoint", "help": "Brazil (Sao Paulo) Public Endpoint.", "label": "Sao Paulo", "name": "sao-paulo"}, {"description": "Spain (Madrid) Public Endpoint", "help": "Spain (Madrid) Public Endpoint.", "label": "Madrid", "name": "madrid"}]  # IBM cloud region name.
    par_id: NotRequired[str]  # Public address range ID.
    update_interval: NotRequired[int]  # Dynamic object update interval (30 - 3600 sec, default = 60,


class SdnConnector:
    """
    Configure connection to SDN Connector.
    
    Path: system/sdn_connector
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
        payload_dict: SdnConnectorPayload | None = ...,
        name: str | None = ...,
        status: Literal[{"description": "Disable connection to this SDN Connector", "help": "Disable connection to this SDN Connector.", "label": "Disable", "name": "disable"}, {"description": "Enable connection to this SDN Connector", "help": "Enable connection to this SDN Connector.", "label": "Enable", "name": "enable"}] | None = ...,
        type: Literal[{"description": "Application Centric Infrastructure (ACI)", "help": "Application Centric Infrastructure (ACI).", "label": "Aci", "name": "aci"}, {"description": "AliCloud Service (ACS)", "help": "AliCloud Service (ACS).", "label": "Alicloud", "name": "alicloud"}, {"description": "Amazon Web Services (AWS)", "help": "Amazon Web Services (AWS).", "label": "Aws", "name": "aws"}, {"description": "Microsoft Azure", "help": "Microsoft Azure.", "label": "Azure", "name": "azure"}, {"description": "Google Cloud Platform (GCP)", "help": "Google Cloud Platform (GCP).", "label": "Gcp", "name": "gcp"}, {"description": "VMware NSX", "help": "VMware NSX.", "label": "Nsx", "name": "nsx"}, {"description": "Nuage VSP", "help": "Nuage VSP.", "label": "Nuage", "name": "nuage"}, {"description": "Oracle Cloud Infrastructure", "help": "Oracle Cloud Infrastructure.", "label": "Oci", "name": "oci"}, {"description": "OpenStack", "help": "OpenStack.", "label": "Openstack", "name": "openstack"}, {"description": "Kubernetes", "help": "Kubernetes.", "label": "Kubernetes", "name": "kubernetes"}, {"description": "VMware vSphere (vCenter \u0026 ESXi)", "help": "VMware vSphere (vCenter \u0026 ESXi).", "label": "Vmware", "name": "vmware"}, {"description": "Symantec Endpoint Protection Manager", "help": "Symantec Endpoint Protection Manager.", "label": "Sepm", "name": "sepm"}, {"description": "Application Centric Infrastructure (ACI Direct Connection)", "help": "Application Centric Infrastructure (ACI Direct Connection).", "label": "Aci Direct", "name": "aci-direct"}, {"description": "IBM Cloud Infrastructure", "help": "IBM Cloud Infrastructure.", "label": "Ibm", "name": "ibm"}, {"description": "Nutanix Prism Central", "help": "Nutanix Prism Central.", "label": "Nutanix", "name": "nutanix"}, {"description": "SAP Control", "help": "SAP Control.", "label": "Sap", "name": "sap"}] | None = ...,
        proxy: str | None = ...,
        use_metadata_iam: Literal[{"description": "Disable using IAM role to call API", "help": "Disable using IAM role to call API.", "label": "Disable", "name": "disable"}, {"description": "Enable using IAM role to call API", "help": "Enable using IAM role to call API.", "label": "Enable", "name": "enable"}] | None = ...,
        microsoft_365: Literal[{"description": "Azure SDN connector    enable:Microsoft 365 SDN connector", "help": "Azure SDN connector", "label": "Disable", "name": "disable"}, {"help": "Microsoft 365 SDN connector", "label": "Enable", "name": "enable"}] | None = ...,
        ha_status: Literal[{"description": "Disable use for FortiGate HA service", "help": "Disable use for FortiGate HA service.", "label": "Disable", "name": "disable"}, {"description": "Enable use for FortiGate HA service", "help": "Enable use for FortiGate HA service.", "label": "Enable", "name": "enable"}] | None = ...,
        verify_certificate: Literal[{"description": "Disable server certificate verification", "help": "Disable server certificate verification.", "label": "Disable", "name": "disable"}, {"description": "Enable server certificate verification", "help": "Enable server certificate verification.", "label": "Enable", "name": "enable"}] | None = ...,
        server: str | None = ...,
        server_list: list[dict[str, Any]] | None = ...,
        server_port: int | None = ...,
        message_server_port: int | None = ...,
        username: str | None = ...,
        password: str | None = ...,
        vcenter_server: str | None = ...,
        vcenter_username: str | None = ...,
        vcenter_password: str | None = ...,
        access_key: str | None = ...,
        secret_key: str | None = ...,
        region: str | None = ...,
        vpc_id: str | None = ...,
        alt_resource_ip: Literal[{"description": "Disable AWS alternative resource IP", "help": "Disable AWS alternative resource IP.", "label": "Disable", "name": "disable"}, {"description": "Enable AWS alternative resource IP", "help": "Enable AWS alternative resource IP.", "label": "Enable", "name": "enable"}] | None = ...,
        external_account_list: list[dict[str, Any]] | None = ...,
        tenant_id: str | None = ...,
        client_id: str | None = ...,
        client_secret: str | None = ...,
        subscription_id: str | None = ...,
        resource_group: str | None = ...,
        login_endpoint: str | None = ...,
        resource_url: str | None = ...,
        azure_region: Literal[{"description": "Global Azure Server", "help": "Global Azure Server.", "label": "Global", "name": "global"}, {"description": "China Azure Server", "help": "China Azure Server.", "label": "China", "name": "china"}, {"description": "Germany Azure Server", "help": "Germany Azure Server.", "label": "Germany", "name": "germany"}, {"description": "US Government Azure Server", "help": "US Government Azure Server.", "label": "Usgov", "name": "usgov"}, {"description": "Azure Stack Local Server", "help": "Azure Stack Local Server.", "label": "Local", "name": "local"}] | None = ...,
        nic: list[dict[str, Any]] | None = ...,
        route_table: list[dict[str, Any]] | None = ...,
        user_id: str | None = ...,
        compartment_list: list[dict[str, Any]] | None = ...,
        oci_region_list: list[dict[str, Any]] | None = ...,
        oci_region_type: Literal[{"description": "Commercial region", "help": "Commercial region.", "label": "Commercial", "name": "commercial"}, {"description": "Government region", "help": "Government region.", "label": "Government", "name": "government"}] | None = ...,
        oci_cert: str | None = ...,
        oci_fingerprint: str | None = ...,
        external_ip: list[dict[str, Any]] | None = ...,
        route: list[dict[str, Any]] | None = ...,
        gcp_project_list: list[dict[str, Any]] | None = ...,
        forwarding_rule: list[dict[str, Any]] | None = ...,
        service_account: str | None = ...,
        private_key: str | None = ...,
        secret_token: str | None = ...,
        domain: str | None = ...,
        group_name: str | None = ...,
        server_cert: str | None = ...,
        server_ca_cert: str | None = ...,
        api_key: str | None = ...,
        ibm_region: Literal[{"description": "US South (Dallas) Public Endpoint", "help": "US South (Dallas) Public Endpoint.", "label": "Dallas", "name": "dallas"}, {"description": "US East (Washington DC) Public Endpoint", "help": "US East (Washington DC) Public Endpoint.", "label": "Washington Dc", "name": "washington-dc"}, {"description": "United Kingdom (London) Public Endpoint", "help": "United Kingdom (London) Public Endpoint.", "label": "London", "name": "london"}, {"description": "Germany (Frankfurt) Public Endpoint", "help": "Germany (Frankfurt) Public Endpoint.", "label": "Frankfurt", "name": "frankfurt"}, {"description": "Australia (Sydney) Public Endpoint", "help": "Australia (Sydney) Public Endpoint.", "label": "Sydney", "name": "sydney"}, {"description": "Japan (Tokyo) Public Endpoint", "help": "Japan (Tokyo) Public Endpoint.", "label": "Tokyo", "name": "tokyo"}, {"description": "Japan (Osaka) Public Endpoint", "help": "Japan (Osaka) Public Endpoint.", "label": "Osaka", "name": "osaka"}, {"description": "Canada (Toronto) Public Endpoint", "help": "Canada (Toronto) Public Endpoint.", "label": "Toronto", "name": "toronto"}, {"description": "Brazil (Sao Paulo) Public Endpoint", "help": "Brazil (Sao Paulo) Public Endpoint.", "label": "Sao Paulo", "name": "sao-paulo"}, {"description": "Spain (Madrid) Public Endpoint", "help": "Spain (Madrid) Public Endpoint.", "label": "Madrid", "name": "madrid"}] | None = ...,
        par_id: str | None = ...,
        update_interval: int | None = ...,
        vdom: str | bool | None = ...,
        raw_json: bool = ...,
        **kwargs: Any,
    ) -> Union[dict[str, Any], Coroutine[Any, Any, dict[str, Any]]]: ...
    
    def put(
        self,
        payload_dict: SdnConnectorPayload | None = ...,
        name: str | None = ...,
        status: Literal[{"description": "Disable connection to this SDN Connector", "help": "Disable connection to this SDN Connector.", "label": "Disable", "name": "disable"}, {"description": "Enable connection to this SDN Connector", "help": "Enable connection to this SDN Connector.", "label": "Enable", "name": "enable"}] | None = ...,
        type: Literal[{"description": "Application Centric Infrastructure (ACI)", "help": "Application Centric Infrastructure (ACI).", "label": "Aci", "name": "aci"}, {"description": "AliCloud Service (ACS)", "help": "AliCloud Service (ACS).", "label": "Alicloud", "name": "alicloud"}, {"description": "Amazon Web Services (AWS)", "help": "Amazon Web Services (AWS).", "label": "Aws", "name": "aws"}, {"description": "Microsoft Azure", "help": "Microsoft Azure.", "label": "Azure", "name": "azure"}, {"description": "Google Cloud Platform (GCP)", "help": "Google Cloud Platform (GCP).", "label": "Gcp", "name": "gcp"}, {"description": "VMware NSX", "help": "VMware NSX.", "label": "Nsx", "name": "nsx"}, {"description": "Nuage VSP", "help": "Nuage VSP.", "label": "Nuage", "name": "nuage"}, {"description": "Oracle Cloud Infrastructure", "help": "Oracle Cloud Infrastructure.", "label": "Oci", "name": "oci"}, {"description": "OpenStack", "help": "OpenStack.", "label": "Openstack", "name": "openstack"}, {"description": "Kubernetes", "help": "Kubernetes.", "label": "Kubernetes", "name": "kubernetes"}, {"description": "VMware vSphere (vCenter \u0026 ESXi)", "help": "VMware vSphere (vCenter \u0026 ESXi).", "label": "Vmware", "name": "vmware"}, {"description": "Symantec Endpoint Protection Manager", "help": "Symantec Endpoint Protection Manager.", "label": "Sepm", "name": "sepm"}, {"description": "Application Centric Infrastructure (ACI Direct Connection)", "help": "Application Centric Infrastructure (ACI Direct Connection).", "label": "Aci Direct", "name": "aci-direct"}, {"description": "IBM Cloud Infrastructure", "help": "IBM Cloud Infrastructure.", "label": "Ibm", "name": "ibm"}, {"description": "Nutanix Prism Central", "help": "Nutanix Prism Central.", "label": "Nutanix", "name": "nutanix"}, {"description": "SAP Control", "help": "SAP Control.", "label": "Sap", "name": "sap"}] | None = ...,
        proxy: str | None = ...,
        use_metadata_iam: Literal[{"description": "Disable using IAM role to call API", "help": "Disable using IAM role to call API.", "label": "Disable", "name": "disable"}, {"description": "Enable using IAM role to call API", "help": "Enable using IAM role to call API.", "label": "Enable", "name": "enable"}] | None = ...,
        microsoft_365: Literal[{"description": "Azure SDN connector    enable:Microsoft 365 SDN connector", "help": "Azure SDN connector", "label": "Disable", "name": "disable"}, {"help": "Microsoft 365 SDN connector", "label": "Enable", "name": "enable"}] | None = ...,
        ha_status: Literal[{"description": "Disable use for FortiGate HA service", "help": "Disable use for FortiGate HA service.", "label": "Disable", "name": "disable"}, {"description": "Enable use for FortiGate HA service", "help": "Enable use for FortiGate HA service.", "label": "Enable", "name": "enable"}] | None = ...,
        verify_certificate: Literal[{"description": "Disable server certificate verification", "help": "Disable server certificate verification.", "label": "Disable", "name": "disable"}, {"description": "Enable server certificate verification", "help": "Enable server certificate verification.", "label": "Enable", "name": "enable"}] | None = ...,
        server: str | None = ...,
        server_list: list[dict[str, Any]] | None = ...,
        server_port: int | None = ...,
        message_server_port: int | None = ...,
        username: str | None = ...,
        password: str | None = ...,
        vcenter_server: str | None = ...,
        vcenter_username: str | None = ...,
        vcenter_password: str | None = ...,
        access_key: str | None = ...,
        secret_key: str | None = ...,
        region: str | None = ...,
        vpc_id: str | None = ...,
        alt_resource_ip: Literal[{"description": "Disable AWS alternative resource IP", "help": "Disable AWS alternative resource IP.", "label": "Disable", "name": "disable"}, {"description": "Enable AWS alternative resource IP", "help": "Enable AWS alternative resource IP.", "label": "Enable", "name": "enable"}] | None = ...,
        external_account_list: list[dict[str, Any]] | None = ...,
        tenant_id: str | None = ...,
        client_id: str | None = ...,
        client_secret: str | None = ...,
        subscription_id: str | None = ...,
        resource_group: str | None = ...,
        login_endpoint: str | None = ...,
        resource_url: str | None = ...,
        azure_region: Literal[{"description": "Global Azure Server", "help": "Global Azure Server.", "label": "Global", "name": "global"}, {"description": "China Azure Server", "help": "China Azure Server.", "label": "China", "name": "china"}, {"description": "Germany Azure Server", "help": "Germany Azure Server.", "label": "Germany", "name": "germany"}, {"description": "US Government Azure Server", "help": "US Government Azure Server.", "label": "Usgov", "name": "usgov"}, {"description": "Azure Stack Local Server", "help": "Azure Stack Local Server.", "label": "Local", "name": "local"}] | None = ...,
        nic: list[dict[str, Any]] | None = ...,
        route_table: list[dict[str, Any]] | None = ...,
        user_id: str | None = ...,
        compartment_list: list[dict[str, Any]] | None = ...,
        oci_region_list: list[dict[str, Any]] | None = ...,
        oci_region_type: Literal[{"description": "Commercial region", "help": "Commercial region.", "label": "Commercial", "name": "commercial"}, {"description": "Government region", "help": "Government region.", "label": "Government", "name": "government"}] | None = ...,
        oci_cert: str | None = ...,
        oci_fingerprint: str | None = ...,
        external_ip: list[dict[str, Any]] | None = ...,
        route: list[dict[str, Any]] | None = ...,
        gcp_project_list: list[dict[str, Any]] | None = ...,
        forwarding_rule: list[dict[str, Any]] | None = ...,
        service_account: str | None = ...,
        private_key: str | None = ...,
        secret_token: str | None = ...,
        domain: str | None = ...,
        group_name: str | None = ...,
        server_cert: str | None = ...,
        server_ca_cert: str | None = ...,
        api_key: str | None = ...,
        ibm_region: Literal[{"description": "US South (Dallas) Public Endpoint", "help": "US South (Dallas) Public Endpoint.", "label": "Dallas", "name": "dallas"}, {"description": "US East (Washington DC) Public Endpoint", "help": "US East (Washington DC) Public Endpoint.", "label": "Washington Dc", "name": "washington-dc"}, {"description": "United Kingdom (London) Public Endpoint", "help": "United Kingdom (London) Public Endpoint.", "label": "London", "name": "london"}, {"description": "Germany (Frankfurt) Public Endpoint", "help": "Germany (Frankfurt) Public Endpoint.", "label": "Frankfurt", "name": "frankfurt"}, {"description": "Australia (Sydney) Public Endpoint", "help": "Australia (Sydney) Public Endpoint.", "label": "Sydney", "name": "sydney"}, {"description": "Japan (Tokyo) Public Endpoint", "help": "Japan (Tokyo) Public Endpoint.", "label": "Tokyo", "name": "tokyo"}, {"description": "Japan (Osaka) Public Endpoint", "help": "Japan (Osaka) Public Endpoint.", "label": "Osaka", "name": "osaka"}, {"description": "Canada (Toronto) Public Endpoint", "help": "Canada (Toronto) Public Endpoint.", "label": "Toronto", "name": "toronto"}, {"description": "Brazil (Sao Paulo) Public Endpoint", "help": "Brazil (Sao Paulo) Public Endpoint.", "label": "Sao Paulo", "name": "sao-paulo"}, {"description": "Spain (Madrid) Public Endpoint", "help": "Spain (Madrid) Public Endpoint.", "label": "Madrid", "name": "madrid"}] | None = ...,
        par_id: str | None = ...,
        update_interval: int | None = ...,
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
        payload_dict: SdnConnectorPayload | None = ...,
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
    "SdnConnector",
    "SdnConnectorPayload",
]