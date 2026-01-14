# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Iterable
from typing_extensions import Literal, Required, Annotated, TypedDict

from ...._types import SequenceNotStr
from ...._utils import PropertyInfo
from .tag_param import TagParam
from .region_specification_param import RegionSpecificationParam
from .certificate_info_specification_param import CertificateInfoSpecificationParam

__all__ = ["CloudAccountUpdateParams"]


class CloudAccountUpdateParams(TypedDict, total=False):
    api_version: Required[Annotated[str, PropertyInfo(alias="apiVersion")]]
    """The version of the API in yyyy-MM-dd format (UTC).

    For versioning information refer to /iaas/api/about
    """

    cloud_account_properties: Required[Annotated[Dict[str, str], PropertyInfo(alias="cloudAccountProperties")]]
    """Cloud Account specific properties supplied in as name value pairs"""

    name: Required[str]
    """A human-friendly name used as an identifier in APIs that support this option."""

    regions: Required[Iterable[RegionSpecificationParam]]
    """
    A set of regions to enable provisioning on.Refer to
    /iaas/api/cloud-accounts/region-enumeration. 'regionInfos' is a required
    parameter for AWS, AZURE, GCP, VSPHERE, VMC, VCF cloud account types.
    """

    associated_cloud_account_ids: Annotated[SequenceNotStr[str], PropertyInfo(alias="associatedCloudAccountIds")]
    """Cloud accounts to associate with this cloud account"""

    associated_mobility_cloud_account_ids: Annotated[
        Dict[str, Literal["UNIDIRECTIONAL", "BIDIRECTIONAL"]], PropertyInfo(alias="associatedMobilityCloudAccountIds")
    ]
    """
    Cloud Account IDs and directionalities create associations to other vSphere
    cloud accounts that can be used for workload mobility. ID refers to an
    associated cloud account, and directionality can be unidirectional or
    bidirectional. Only supported on vSphere cloud accounts.
    """

    certificate_info: Annotated[CertificateInfoSpecificationParam, PropertyInfo(alias="certificateInfo")]
    """Specification for certificate for a cloud account."""

    create_default_zones: Annotated[bool, PropertyInfo(alias="createDefaultZones")]
    """Create default cloud zones for the enabled regions."""

    custom_properties: Annotated[Dict[str, str], PropertyInfo(alias="customProperties")]
    """Additional custom properties that may be used to extend the Cloud Account."""

    description: str
    """A human-friendly description."""

    private_key: Annotated[str, PropertyInfo(alias="privateKey")]
    """
    Secret access key or password to be used to authenticate with the cloud account.
    """

    private_key_id: Annotated[str, PropertyInfo(alias="privateKeyId")]
    """Access key id or username to be used to authenticate with the cloud account"""

    tags: Iterable[TagParam]
    """A set of tag keys and optional values to set on the Cloud Account"""
