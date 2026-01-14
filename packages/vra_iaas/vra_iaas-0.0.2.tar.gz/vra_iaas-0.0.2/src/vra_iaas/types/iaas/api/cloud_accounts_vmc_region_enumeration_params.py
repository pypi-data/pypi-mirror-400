# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from ...._utils import PropertyInfo
from .certificate_info_specification_param import CertificateInfoSpecificationParam

__all__ = ["CloudAccountsVmcRegionEnumerationParams"]


class CloudAccountsVmcRegionEnumerationParams(TypedDict, total=False):
    api_version: Required[Annotated[str, PropertyInfo(alias="apiVersion")]]
    """The version of the API in yyyy-MM-dd format (UTC).

    For versioning information refer to /iaas/api/about
    """

    accept_self_signed_certificate: Annotated[bool, PropertyInfo(alias="acceptSelfSignedCertificate")]
    """Accept self signed certificate when connecting to vSphere"""

    api_key: Annotated[str, PropertyInfo(alias="apiKey")]
    """VMC API access key.

    Either provide apiKey or provide a cloudAccountId of an existing account.
    """

    certificate_info: Annotated[CertificateInfoSpecificationParam, PropertyInfo(alias="certificateInfo")]
    """Specification for certificate for a cloud account."""

    cloud_account_id: Annotated[str, PropertyInfo(alias="cloudAccountId")]
    """Existing cloud account id.

    Either provide existing cloud account Id, or apiKey, sddcId, username, password,
    hostName, nsxHostName.
    """

    csp_host_name: Annotated[str, PropertyInfo(alias="cspHostName")]
    """The host name of the CSP service."""

    dc_id: Annotated[str, PropertyInfo(alias="dcId")]
    """Identifier of a data collector vm deployed in the on premise infrastructure.

    Refer to the data-collector API to create or list data collectors
    """

    environment: str
    """The environment where the agent has been deployed.

    When the agent has been deployed using the "Add Ons" in VMC UI or Api use "aap".
    """

    host_name: Annotated[str, PropertyInfo(alias="hostName")]
    """Enter the IP address or FQDN of the vCenter Server in the specified SDDC.

    The cloud proxy belongs on this vCenter. Either provide hostName or provide a
    cloudAccountId of an existing account.
    """

    nsx_host_name: Annotated[str, PropertyInfo(alias="nsxHostName")]
    """
    The IP address of the NSX Manager server in the specified SDDC / FQDN.Either
    provide nsxHostName or provide a cloudAccountId of an existing account.
    """

    password: str
    """Password for the user used to authenticate with the cloud Account.

    Either provide password or provide a cloudAccountId of an existing account.
    """

    sddc_id: Annotated[str, PropertyInfo(alias="sddcId")]
    """Identifier of the on-premise SDDC to be used by this cloud account.

    Note that NSX-V SDDCs are not supported. Either provide sddcId or provide a
    cloudAccountId of an existing account.
    """

    username: str
    """
    vCenter user name for the specified SDDC.The specified user requires CloudAdmin
    credentials. The user does not require CloudGlobalAdmin credentials.Either
    provide username or provide a cloudAccountId of an existing account.
    """
