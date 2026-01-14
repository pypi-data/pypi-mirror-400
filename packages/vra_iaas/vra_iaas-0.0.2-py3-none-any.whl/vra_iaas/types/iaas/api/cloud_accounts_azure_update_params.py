# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Required, Annotated, TypedDict

from ...._utils import PropertyInfo
from .tag_param import TagParam
from .region_specification_param import RegionSpecificationParam

__all__ = ["CloudAccountsAzureUpdateParams"]


class CloudAccountsAzureUpdateParams(TypedDict, total=False):
    api_version: Required[Annotated[str, PropertyInfo(alias="apiVersion")]]
    """The version of the API in yyyy-MM-dd format (UTC).

    For versioning information refer to /iaas/api/about
    """

    client_application_id: Required[Annotated[str, PropertyInfo(alias="clientApplicationId")]]
    """Azure Client Application ID"""

    client_application_secret_key: Required[Annotated[str, PropertyInfo(alias="clientApplicationSecretKey")]]
    """Azure Client Application Secret Key"""

    name: Required[str]
    """A human-friendly name used as an identifier in APIs that support this option."""

    regions: Required[Iterable[RegionSpecificationParam]]
    """
    A set of regions to enable provisioning on.Refer to
    /iaas/api/cloud-accounts/region-enumeration.
    """

    subscription_id: Required[Annotated[str, PropertyInfo(alias="subscriptionId")]]
    """Azure Subscribtion ID"""

    tenant_id: Required[Annotated[str, PropertyInfo(alias="tenantId")]]
    """Azure Tenant ID"""

    create_default_zones: Annotated[bool, PropertyInfo(alias="createDefaultZones")]
    """Create default cloud zones for the enabled regions."""

    description: str
    """A human-friendly description."""

    tags: Iterable[TagParam]
    """A set of tag keys and optional values to set on the Cloud Account"""
