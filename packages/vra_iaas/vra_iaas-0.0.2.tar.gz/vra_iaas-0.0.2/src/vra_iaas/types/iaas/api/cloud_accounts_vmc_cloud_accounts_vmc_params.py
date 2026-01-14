# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Required, Annotated, TypedDict

from ...._utils import PropertyInfo
from .tag_param import TagParam
from .region_specification_param import RegionSpecificationParam
from .certificate_info_specification_param import CertificateInfoSpecificationParam

__all__ = ["CloudAccountsVmcCloudAccountsVmcParams"]


class CloudAccountsVmcCloudAccountsVmcParams(TypedDict, total=False):
    api_version: Required[Annotated[str, PropertyInfo(alias="apiVersion")]]
    """The version of the API in yyyy-MM-dd format (UTC).

    For versioning information refer to /iaas/api/about
    """

    api_key: Required[Annotated[str, PropertyInfo(alias="apiKey")]]
    """VMC API access key."""

    dc_id: Required[Annotated[str, PropertyInfo(alias="dcId")]]
    """Identifier of a data collector vm deployed in the on premise infrastructure.

    Refer to the data-collector API to create or list data collectors.
    """

    host_name: Required[Annotated[str, PropertyInfo(alias="hostName")]]
    """Enter the IP address or FQDN of the vCenter Server in the specified SDDC.

    The cloud proxy belongs on this vCenter.
    """

    name: Required[str]
    """A human-friendly name used as an identifier in APIs that support this option."""

    nsx_host_name: Required[Annotated[str, PropertyInfo(alias="nsxHostName")]]
    """The IP address of the NSX Manager server in the specified SDDC / FQDN."""

    password: Required[str]
    """Password for the user used to authenticate with the cloud Account."""

    regions: Required[Iterable[RegionSpecificationParam]]
    """
    A set of regions to enable provisioning on.Refer to
    /iaas/api/cloud-accounts/region-enumeration.
    """

    sddc_id: Required[Annotated[str, PropertyInfo(alias="sddcId")]]
    """Identifier of the on-premise SDDC to be used by this cloud account.

    Note that NSX-V SDDCs are not supported.
    """

    username: Required[str]
    """
    vCenter user name for the specified SDDC.The specified user requires CloudAdmin
    credentials. The user does not require CloudGlobalAdmin credentials.
    """

    validate_only: Annotated[str, PropertyInfo(alias="validateOnly")]
    """
    If provided, it only validates the credentials in the Cloud Account
    Specification, and cloud account will not be created.
    """

    accept_self_signed_certificate: Annotated[bool, PropertyInfo(alias="acceptSelfSignedCertificate")]
    """Accept self signed certificate when connecting to vSphere"""

    certificate_info: Annotated[CertificateInfoSpecificationParam, PropertyInfo(alias="certificateInfo")]
    """Specification for certificate for a cloud account."""

    create_default_zones: Annotated[bool, PropertyInfo(alias="createDefaultZones")]
    """Create default cloud zones for the enabled regions."""

    description: str
    """A human-friendly description."""

    environment: str
    """The environment where the agent has been deployed.

    When the agent has been deployed using the "Add Ons" in VMC UI or Api use "aap".
    """

    tags: Iterable[TagParam]
    """
    A set of tag keys and optional values to set on the Cloud Account.Cloud account
    capability tags may enable different features.
    """
