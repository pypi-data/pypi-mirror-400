# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Required, Annotated, TypedDict

from ...._types import SequenceNotStr
from ...._utils import PropertyInfo
from .tag_param import TagParam
from .certificate_info_specification_param import CertificateInfoSpecificationParam

__all__ = ["CloudAccountsNsxTCloudAccountsNsxTParams"]


class CloudAccountsNsxTCloudAccountsNsxTParams(TypedDict, total=False):
    api_version: Required[Annotated[str, PropertyInfo(alias="apiVersion")]]
    """The version of the API in yyyy-MM-dd format (UTC).

    For versioning information refer to /iaas/api/about
    """

    dcid: Required[str]
    """Identifier of a data collector vm deployed in the on premise infrastructure.

    Refer to the data-collector API to create or list data collectors. Note: Data
    collector endpoints are not available in VMware Aria Automation (on-prem)
    release and hence the data collector Id is optional for VMware Aria Automation
    (on-prem).
    """

    host_name: Required[Annotated[str, PropertyInfo(alias="hostName")]]
    """Host name for the NSX-T endpoint"""

    name: Required[str]
    """A human-friendly name used as an identifier in APIs that support this option."""

    password: Required[str]
    """Password for the user used to authenticate with the cloud Account"""

    username: Required[str]
    """Username to authenticate with the cloud account"""

    validate_only: Annotated[str, PropertyInfo(alias="validateOnly")]
    """
    If provided, it only validates the credentials in the Cloud Account
    Specification, and cloud account will not be created.
    """

    accept_self_signed_certificate: Annotated[bool, PropertyInfo(alias="acceptSelfSignedCertificate")]
    """Accept self signed certificate when connecting."""

    associated_cloud_account_ids: Annotated[SequenceNotStr[str], PropertyInfo(alias="associatedCloudAccountIds")]
    """vSphere cloud accounts associated with this NSX-T cloud account."""

    certificate_info: Annotated[CertificateInfoSpecificationParam, PropertyInfo(alias="certificateInfo")]
    """Specification for certificate for a cloud account."""

    description: str
    """A human-friendly description."""

    is_global_manager: Annotated[bool, PropertyInfo(alias="isGlobalManager")]
    """Indicates whether this is an NSX-T Global Manager cloud account.

    NSX-T Global Manager can only be associated with NSX-T cloud accounts. Default
    value: false.
    """

    manager_mode: Annotated[bool, PropertyInfo(alias="managerMode")]
    """Create NSX-T cloud account in Manager (legacy) mode.

    When set to true, NSX-T cloud account in created in Manager mode. Mode cannot be
    changed after cloud account is created. Default value is false.
    """

    tags: Iterable[TagParam]
    """A set of tag keys and optional values to set on the Cloud Account"""
