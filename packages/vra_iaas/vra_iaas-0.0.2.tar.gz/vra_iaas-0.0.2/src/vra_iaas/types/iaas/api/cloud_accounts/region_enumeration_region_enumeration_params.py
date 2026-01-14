# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict
from typing_extensions import Required, Annotated, TypedDict

from ....._utils import PropertyInfo
from ..certificate_info_specification_param import CertificateInfoSpecificationParam

__all__ = ["RegionEnumerationRegionEnumerationParams"]


class RegionEnumerationRegionEnumerationParams(TypedDict, total=False):
    api_version: Required[Annotated[str, PropertyInfo(alias="apiVersion")]]
    """The version of the API in yyyy-MM-dd format (UTC).

    For versioning information refer to /iaas/api/about
    """

    cloud_account_properties: Required[Annotated[Dict[str, str], PropertyInfo(alias="cloudAccountProperties")]]
    """Cloud Account specific properties supplied in as name value pairs."""

    certificate_info: Annotated[CertificateInfoSpecificationParam, PropertyInfo(alias="certificateInfo")]
    """Specification for certificate for a cloud account."""

    cloud_account_id: Annotated[str, PropertyInfo(alias="cloudAccountId")]
    """Existing cloud account id.

    Either provide existing cloud account Id, or privateKeyId/privateKey credentials
    pair.
    """

    cloud_account_type: Annotated[str, PropertyInfo(alias="cloudAccountType")]
    """Cloud account type"""

    private_key: Annotated[str, PropertyInfo(alias="privateKey")]
    """Secret access key or password to be used to authenticate with the cloud account.

    Either provide privateKey or provide a cloudAccountId of an existing account.
    """

    private_key_id: Annotated[str, PropertyInfo(alias="privateKeyId")]
    """Access key id or username to be used to authenticate with the cloud account.

    Either provide privateKeyId or provide a cloudAccountId of an existing account.
    """
