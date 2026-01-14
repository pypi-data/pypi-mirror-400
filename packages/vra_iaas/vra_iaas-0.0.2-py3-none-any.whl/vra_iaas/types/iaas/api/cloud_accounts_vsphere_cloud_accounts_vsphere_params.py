# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Iterable
from typing_extensions import Literal, Required, Annotated, TypedDict

from ...._types import SequenceNotStr
from ...._utils import PropertyInfo
from .tag_param import TagParam
from .region_specification_param import RegionSpecificationParam
from .certificate_info_specification_param import CertificateInfoSpecificationParam

__all__ = ["CloudAccountsVsphereCloudAccountsVsphereParams"]


class CloudAccountsVsphereCloudAccountsVsphereParams(TypedDict, total=False):
    api_version: Required[Annotated[str, PropertyInfo(alias="apiVersion")]]
    """The version of the API in yyyy-MM-dd format (UTC).

    For versioning information refer to /iaas/api/about
    """

    host_name: Required[Annotated[str, PropertyInfo(alias="hostName")]]
    """Host name for the vSphere endpoint"""

    name: Required[str]
    """A human-friendly name used as an identifier in APIs that support this option."""

    regions: Required[Iterable[RegionSpecificationParam]]
    """
    A set of regions to enable provisioning on.Refer to
    /iaas/api/cloud-accounts/region-enumeration.
    """

    validate_only: Annotated[str, PropertyInfo(alias="validateOnly")]
    """
    If provided, it only validates the credentials in the Cloud Account
    Specification, and cloud account will not be created.
    """

    accept_self_signed_certificate: Annotated[bool, PropertyInfo(alias="acceptSelfSignedCertificate")]
    """Accept self signed certificate when connecting to vSphere"""

    associated_cloud_account_ids: Annotated[SequenceNotStr[str], PropertyInfo(alias="associatedCloudAccountIds")]
    """NSX-V or NSX-T account to associate with this vSphere cloud account.

    vSphere cloud account can be a single NSX-V cloud account or a single NSX-T
    cloud account.
    """

    associated_mobility_cloud_account_ids: Annotated[
        Dict[str, Literal["UNIDIRECTIONAL", "BIDIRECTIONAL"]], PropertyInfo(alias="associatedMobilityCloudAccountIds")
    ]
    """
    Cloud account IDs and directionalities create associations to other vSphere
    cloud accounts that can be used for workload mobility. ID refers to an
    associated cloud account, and directionality can be unidirectional or
    bidirectional.
    """

    certificate_info: Annotated[CertificateInfoSpecificationParam, PropertyInfo(alias="certificateInfo")]
    """Specification for certificate for a cloud account."""

    create_default_zones: Annotated[bool, PropertyInfo(alias="createDefaultZones")]
    """Create default cloud zones for the enabled regions."""

    dcid: str
    """Identifier of a data collector vm deployed in the on premise infrastructure.

    Refer to the data-collector API to create or list data collectors. Note: Data
    collector endpoints are not available in VMware Aria Automation (on-prem)
    release.
    """

    description: str
    """A human-friendly description."""

    environment: str
    """The environment where data collectors are deployed.

    When the data collectors are deployed on an aap-based cloud gateway appliance,
    use "aap".
    """

    password: str
    """Password for the user used to authenticate with the cloud Account."""

    tags: Iterable[TagParam]
    """A set of tag keys and optional values to set on the Cloud Account"""

    username: str
    """Username to authenticate with the cloud account."""
