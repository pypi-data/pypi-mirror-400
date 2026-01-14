# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Required, Annotated, TypedDict

from ...._utils import PropertyInfo
from .tag_param import TagParam
from .region_specification_param import RegionSpecificationParam
from .certificate_info_specification_param import CertificateInfoSpecificationParam

__all__ = ["CloudAccountsVcfUpdateParams"]


class CloudAccountsVcfUpdateParams(TypedDict, total=False):
    api_version: Required[Annotated[str, PropertyInfo(alias="apiVersion")]]
    """The version of the API in yyyy-MM-dd format (UTC).

    For versioning information refer to /iaas/api/about
    """

    name: Required[str]
    """A human-friendly name used as an identifier in APIs that support this option."""

    nsx_host_name: Required[Annotated[str, PropertyInfo(alias="nsxHostName")]]
    """Host name for the NSX endpoint from the specified workload domain."""

    nsx_password: Required[Annotated[str, PropertyInfo(alias="nsxPassword")]]
    """
    Password for the user used to authenticate with the NSX-T manager in VCF cloud
    account
    """

    nsx_username: Required[Annotated[str, PropertyInfo(alias="nsxUsername")]]
    """User name for the NSX manager in the specified workload domain."""

    regions: Required[Iterable[RegionSpecificationParam]]
    """
    A set of regions to enable provisioning on.Refer to
    /iaas/api/cloud-accounts/region-enumeration.
    """

    vcenter_host_name: Required[Annotated[str, PropertyInfo(alias="vcenterHostName")]]
    """Host name for the vSphere from the specified workload domain."""

    vcenter_password: Required[Annotated[str, PropertyInfo(alias="vcenterPassword")]]
    """
    Password for the user used to authenticate with the vCenter in VCF cloud account
    """

    vcenter_username: Required[Annotated[str, PropertyInfo(alias="vcenterUsername")]]
    """
    vCenter user name for the specified workload domain.The specified user requires
    CloudAdmin credentials. The user does not require CloudGlobalAdmin credentials.
    """

    workload_domain_id: Required[Annotated[str, PropertyInfo(alias="workloadDomainId")]]
    """Id of the workload domain to add as VCF cloud account."""

    workload_domain_name: Required[Annotated[str, PropertyInfo(alias="workloadDomainName")]]
    """Name of the workload domain to add as VCF cloud account."""

    accept_self_signed_certificate: Annotated[bool, PropertyInfo(alias="acceptSelfSignedCertificate")]
    """Accept self signed certificate when connecting to vSphere and NSX-T"""

    certificate_info: Annotated[CertificateInfoSpecificationParam, PropertyInfo(alias="certificateInfo")]
    """Specification for certificate for a cloud account."""

    create_default_zones: Annotated[bool, PropertyInfo(alias="createDefaultZones")]
    """Create default cloud zones for the enabled regions."""

    dc_id: Annotated[str, PropertyInfo(alias="dcId")]
    """Identifier of a data collector vm deployed in the on premise infrastructure.

    Refer to the data-collector API to create or list data collectors. Note: Data
    collector endpoints are not available in VMware Aria Automation (on-prem)
    release.
    """

    description: str
    """A human-friendly description."""

    nsx_certificate: Annotated[str, PropertyInfo(alias="nsxCertificate")]
    """NSX Certificate"""

    sddc_manager_id: Annotated[str, PropertyInfo(alias="sddcManagerId")]
    """SDDC manager integration id"""

    tags: Iterable[TagParam]
    """
    A set of tag keys and optional values to set on the Cloud Account.Cloud account
    capability tags may enable different features.
    """

    vcenter_certificate: Annotated[str, PropertyInfo(alias="vcenterCertificate")]
    """vCenter Certificate"""
