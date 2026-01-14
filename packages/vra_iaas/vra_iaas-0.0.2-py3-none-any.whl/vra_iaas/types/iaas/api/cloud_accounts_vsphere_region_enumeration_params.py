# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from ...._utils import PropertyInfo
from .certificate_info_specification_param import CertificateInfoSpecificationParam

__all__ = ["CloudAccountsVsphereRegionEnumerationParams"]


class CloudAccountsVsphereRegionEnumerationParams(TypedDict, total=False):
    api_version: Required[Annotated[str, PropertyInfo(alias="apiVersion")]]
    """The version of the API in yyyy-MM-dd format (UTC).

    For versioning information refer to /iaas/api/about
    """

    accept_self_signed_certificate: Annotated[bool, PropertyInfo(alias="acceptSelfSignedCertificate")]
    """Accept self signed certificate when connecting to vSphere"""

    certificate_info: Annotated[CertificateInfoSpecificationParam, PropertyInfo(alias="certificateInfo")]
    """Specification for certificate for a cloud account."""

    cloud_account_id: Annotated[str, PropertyInfo(alias="cloudAccountId")]
    """Existing cloud account id.

    Either provide existing cloud account Id, or hostName, username, password.
    """

    dcid: str
    """Identifier of a data collector vm deployed in the on premise infrastructure.

    Refer to the data-collector API to create or list data collectors. Note: Data
    collector endpoints are not available in VMware Aria Automation (on-prem)
    release.
    """

    environment: str
    """The environment where data collectors are deployed.

    When the data collectors are deployed on a cloud gateway appliance, use "aap".
    """

    host_name: Annotated[str, PropertyInfo(alias="hostName")]
    """Host name for the vSphere endpoint.

    Either provide hostName or provide a cloudAccountId of an existing account.
    """

    password: str
    """Password for the user used to authenticate with the cloud Account.

    Either provide password or provide a cloudAccountId of an existing account.
    """

    username: str
    """Username to authenticate with the cloud account.

    Either provide username or provide a cloudAccountId of an existing account.
    """
