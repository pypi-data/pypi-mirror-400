# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from ...._utils import PropertyInfo
from .certificate_info_specification_param import CertificateInfoSpecificationParam

__all__ = ["CloudAccountsVcfRegionEnumerationParams"]


class CloudAccountsVcfRegionEnumerationParams(TypedDict, total=False):
    api_version: Required[Annotated[str, PropertyInfo(alias="apiVersion")]]
    """The version of the API in yyyy-MM-dd format (UTC).

    For versioning information refer to /iaas/api/about
    """

    accept_self_signed_certificate: Annotated[bool, PropertyInfo(alias="acceptSelfSignedCertificate")]
    """Accept self signed certificate when connecting to vSphere and NSX-T"""

    certificate_info: Annotated[CertificateInfoSpecificationParam, PropertyInfo(alias="certificateInfo")]
    """Specification for certificate for a cloud account."""

    cloud_account_id: Annotated[str, PropertyInfo(alias="cloudAccountId")]
    """Existing cloud account id.

    Either provide existing cloud account Id, or workloadDomainId,
    workloadDomainName, vcenterHostName, vcenterUsername, vcenterPassword,
    nsxHostName, nsxUsername and nsxPassword.
    """

    dc_id: Annotated[str, PropertyInfo(alias="dcId")]
    """Identifier of a data collector vm deployed in the on premise infrastructure.

    Refer to the data-collector API to create or list data collectors. Note: Data
    collector endpoints are not available in VMware Aria Automation (on-prem)
    release.
    """

    nsx_certificate: Annotated[str, PropertyInfo(alias="nsxCertificate")]
    """NSX Certificate"""

    nsx_host_name: Annotated[str, PropertyInfo(alias="nsxHostName")]
    """Host name for the NSX endpoint from the specified workload domain.

    Either provide nsxHostName or provide a cloudAccountId of an existing account.
    """

    nsx_password: Annotated[str, PropertyInfo(alias="nsxPassword")]
    """
    Password for the user used to authenticate with the NSX-T manager in VCF cloud
    account. Either provide nsxPassword or provide a cloudAccountId of an existing
    account.
    """

    nsx_username: Annotated[str, PropertyInfo(alias="nsxUsername")]
    """User name for the NSX manager in the specified workload domain.

    Either provide nsxUsername or provide a cloudAccountId of an existing account.
    """

    sddc_manager_id: Annotated[str, PropertyInfo(alias="sddcManagerId")]
    """SDDC manager integration id.

    Either provide sddcManagerId or provide a cloudAccountId of an existing account.
    """

    vcenter_certificate: Annotated[str, PropertyInfo(alias="vcenterCertificate")]
    """vCenter Certificate"""

    vcenter_host_name: Annotated[str, PropertyInfo(alias="vcenterHostName")]
    """Host name for the vSphere from the specified workload domain.

    Either provide vcenterHostName or provide a cloudAccountId of an existing
    account.
    """

    vcenter_password: Annotated[str, PropertyInfo(alias="vcenterPassword")]
    """Password for the user used to authenticate with the vCenter in VCF cloud
    account.

    Either provide vcenterPassword or provide a cloudAccountId of an existing
    account.
    """

    vcenter_username: Annotated[str, PropertyInfo(alias="vcenterUsername")]
    """
    vCenter user name for the specified workload domain.The specified user requires
    CloudAdmin credentials. The user does not require CloudGlobalAdmin credentials.
    """

    workload_domain_id: Annotated[str, PropertyInfo(alias="workloadDomainId")]
    """Id of the workload domain to add as VCF cloud account.

    Either provide workloadDomainId or provide a cloudAccountId of an existing
    account.
    """

    workload_domain_name: Annotated[str, PropertyInfo(alias="workloadDomainName")]
    """Name of the workload domain to add as VCF cloud account.

    Either provide workloadDomainName or provide a cloudAccountId of an existing
    account.
    """
