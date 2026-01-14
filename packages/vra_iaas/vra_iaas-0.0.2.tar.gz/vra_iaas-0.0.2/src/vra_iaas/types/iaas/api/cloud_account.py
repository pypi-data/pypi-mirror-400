# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import TYPE_CHECKING, Dict, List, Optional
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from .tag import Tag
from .region import Region
from ...._models import BaseModel

__all__ = ["CloudAccount", "_Links", "Link"]


class Link(BaseModel):
    """HATEOAS of the entity"""

    href: Optional[str] = None

    hrefs: Optional[List[str]] = None


class _Links(BaseModel):
    """HATEOAS of the entity"""

    empty: Optional[bool] = None

    if TYPE_CHECKING:
        # Some versions of Pydantic <2.8.0 have a bug and don’t allow assigning a
        # value to this field, so for compatibility we avoid doing it at runtime.
        __pydantic_extra__: Dict[str, Link] = FieldInfo(init=False)  # pyright: ignore[reportIncompatibleVariableOverride]

        # Stub to indicate that arbitrary properties are accepted.
        # To access properties that are not valid identifiers you can use `getattr`, e.g.
        # `getattr(obj, '$type')`
        def __getattr__(self, attr: str) -> Link: ...
    else:
        __pydantic_extra__: Dict[str, Link]


class CloudAccount(BaseModel):
    """
    State object representing a cloud account.<br><br>A cloud account identifies a cloud account type and an account-specific deployment region or data center where the associated cloud account resources are hosted.<br>**HATEOAS** links:<br>**associated-cloud-accounts** - array[CloudAccount] - Cloud accounts associated to this cloud account. For example an NSX endpoint linked to a vSphere cloud account.<br>**regions** - array[Region] - List of regions that are enabled for this cloud account.<br>**self** - CloudAccount - Self link to this cloud account
    """

    id: str
    """The id of this resource instance"""

    api_links: _Links = FieldInfo(alias="_links")
    """HATEOAS of the entity"""

    cloud_account_properties: Dict[str, str] = FieldInfo(alias="cloudAccountProperties")
    """Cloud account specific properties"""

    cloud_account_type: str = FieldInfo(alias="cloudAccountType")
    """Cloud account type"""

    associated_mobility_cloud_account_ids: Optional[Dict[str, Literal["UNIDIRECTIONAL", "BIDIRECTIONAL"]]] = FieldInfo(
        alias="associatedMobilityCloudAccountIds", default=None
    )
    """Workload mobility associations to other vSphere cloud accounts.

    ID refers to an associated cloud account, and directionality can be
    unidirectional or bidirectional. Only supported on vSphere Cloud Accounts.
    """

    created_at: Optional[str] = FieldInfo(alias="createdAt", default=None)
    """Date when the entity was created. The date is in ISO 8601 and UTC."""

    custom_properties: Optional[Dict[str, str]] = FieldInfo(alias="customProperties", default=None)
    """Additional properties that may be used to extend the base type."""

    description: Optional[str] = None
    """A human-friendly description."""

    enabled_regions: Optional[List[Region]] = FieldInfo(alias="enabledRegions", default=None)
    """A list of regions that are enabled for provisioning on this cloud account"""

    healthy: Optional[bool] = None
    """Indicates the health of the cloud account.

    If false, this means there is no connectivity to the cloud provider or the
    credentials are invalid.
    """

    in_maintenance_mode: Optional[bool] = FieldInfo(alias="inMaintenanceMode", default=None)
    """Indicates if the cloud account is undergoing maintenance.

    If true, it can't be used for provisioning and scheduled enumeration is not
    triggered.
    """

    name: Optional[str] = None
    """A human-friendly name used as an identifier in APIs that support this option."""

    org_id: Optional[str] = FieldInfo(alias="orgId", default=None)
    """The id of the organization this entity belongs to."""

    owner: Optional[str] = None
    """Email of the user or display name of the group that owns the entity."""

    owner_type: Optional[str] = FieldInfo(alias="ownerType", default=None)
    """Type of a owner(user/ad_group) that owns the entity."""

    tags: Optional[List[Tag]] = None
    """A set of tag keys and optional values that were set on the Cloud Account"""

    updated_at: Optional[str] = FieldInfo(alias="updatedAt", default=None)
    """Date when the entity was last updated. The date is ISO 8601 and UTC."""
