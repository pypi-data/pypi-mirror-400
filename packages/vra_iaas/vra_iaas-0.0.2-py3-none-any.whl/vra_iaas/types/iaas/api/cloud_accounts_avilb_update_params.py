# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Iterable
from typing_extensions import Required, Annotated, TypedDict

from ...._utils import PropertyInfo
from .tag_param import TagParam
from .region_specification_param import RegionSpecificationParam
from .certificate_info_specification_param import CertificateInfoSpecificationParam

__all__ = ["CloudAccountsAvilbUpdateParams"]


class CloudAccountsAvilbUpdateParams(TypedDict, total=False):
    api_version: Required[Annotated[str, PropertyInfo(alias="apiVersion")]]
    """The version of the API in yyyy-MM-dd format (UTC).

    For versioning information refer to /iaas/api/about
    """

    host_name: Required[Annotated[str, PropertyInfo(alias="hostName")]]
    """Host name for the AVI Load Balancer endpoint"""

    name: Required[str]
    """A human-friendly name used as an identifier in APIs that support this option."""

    password: Required[str]
    """Password for the user used to authenticate with the cloud Account"""

    regions: Required[Iterable[RegionSpecificationParam]]
    """
    A set of regions to enable provisioning on.Refer to
    /iaas/api/cloud-accounts/region-enumeration.
    """

    username: Required[str]
    """Username to authenticate with the cloud account"""

    accept_self_signed_certificate: Annotated[bool, PropertyInfo(alias="acceptSelfSignedCertificate")]
    """Accept self signed certificate when connecting."""

    certificate_info: Annotated[CertificateInfoSpecificationParam, PropertyInfo(alias="certificateInfo")]
    """Specification for certificate for a cloud account."""

    cloud_account_properties: Annotated[Dict[str, str], PropertyInfo(alias="cloudAccountProperties")]
    """Cloud Account specific properties supplied in as name value pairs"""

    create_default_zones: Annotated[bool, PropertyInfo(alias="createDefaultZones")]
    """Create default cloud zones for the enabled regions"""

    description: str
    """A human-friendly description."""

    tags: Iterable[TagParam]
    """A set of tag keys and optional values to set on the Cloud Account"""
