# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Iterable
from typing_extensions import Required, Annotated, TypedDict

from ...._types import SequenceNotStr
from ...._utils import PropertyInfo
from .tag_param import TagParam
from .certificate_info_specification_param import CertificateInfoSpecificationParam

__all__ = ["IntegrationUpdateParams"]


class IntegrationUpdateParams(TypedDict, total=False):
    api_version: Required[Annotated[str, PropertyInfo(alias="apiVersion")]]
    """The version of the API in yyyy-MM-dd format (UTC).

    For versioning information refer to /iaas/api/about
    """

    integration_properties: Required[Annotated[Dict[str, str], PropertyInfo(alias="integrationProperties")]]
    """Integration specific properties supplied in as name value pairs"""

    name: Required[str]
    """A human-friendly name used as an identifier in APIs that support this option."""

    associated_cloud_account_ids: Annotated[SequenceNotStr[str], PropertyInfo(alias="associatedCloudAccountIds")]
    """Cloud accounts to associate with this integration"""

    certificate_info: Annotated[CertificateInfoSpecificationParam, PropertyInfo(alias="certificateInfo")]
    """Specification for certificate for a cloud account."""

    custom_properties: Annotated[Dict[str, str], PropertyInfo(alias="customProperties")]
    """Additional custom properties that may be used to extend the Integration."""

    description: str
    """A human-friendly description."""

    private_key: Annotated[str, PropertyInfo(alias="privateKey")]
    """Secret access key or password to be used to authenticate with the integration"""

    private_key_id: Annotated[str, PropertyInfo(alias="privateKeyId")]
    """Access key id or username to be used to authenticate with the integration"""

    tags: Iterable[TagParam]
    """A set of tag keys and optional values to set on the Integration"""
