# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import TYPE_CHECKING, Dict, List, Optional

from pydantic import Field as FieldInfo

from ....._models import BaseModel

__all__ = ["ZoneAssignment", "_Links", "Link"]


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


class ZoneAssignment(BaseModel):
    """A zone assignment"""

    id: str
    """The id of this resource instance"""

    api_links: Optional[_Links] = FieldInfo(alias="_links", default=None)
    """HATEOAS of the entity"""

    allocated_cpu: Optional[int] = FieldInfo(alias="allocatedCpu", default=None)
    """The amount of CPUs currently allocated."""

    allocated_instances_count: Optional[int] = FieldInfo(alias="allocatedInstancesCount", default=None)
    """The number of resource instances currently allocated"""

    allocated_memory_mb: Optional[int] = FieldInfo(alias="allocatedMemoryMB", default=None)
    """The amount of memory currently allocated."""

    allocated_storage_gb: Optional[float] = FieldInfo(alias="allocatedStorageGB", default=None)
    """The amount of storage currently allocated."""

    cpu_limit: Optional[int] = FieldInfo(alias="cpuLimit", default=None)
    """The maximum amount of cpus that can be used by this cloud zone.

    Default is 0 (unlimited cpu).
    """

    created_at: Optional[str] = FieldInfo(alias="createdAt", default=None)
    """Date when the entity was created. The date is in ISO 8601 and UTC."""

    max_number_instances: Optional[int] = FieldInfo(alias="maxNumberInstances", default=None)
    """The maximum number of instances that can be provisioned in this cloud zone.

    Default is 0 (unlimited instances).
    """

    memory_limit_mb: Optional[int] = FieldInfo(alias="memoryLimitMB", default=None)
    """The maximum amount of memory that can be used by this cloud zone.

    Default is 0 (unlimited memory).
    """

    org_id: Optional[str] = FieldInfo(alias="orgId", default=None)
    """The id of the organization this entity belongs to."""

    owner: Optional[str] = None
    """Email of the user or display name of the group that owns the entity."""

    owner_type: Optional[str] = FieldInfo(alias="ownerType", default=None)
    """Type of a owner(user/ad_group) that owns the entity."""

    priority: Optional[int] = None
    """The priority of this zone in the current project.

    Lower numbers mean higher priority. Default is 0 (highest)
    """

    storage_limit_gb: Optional[int] = FieldInfo(alias="storageLimitGB", default=None)
    """
    Defines an upper limit on storage that can be requested from a cloud zone which
    is part of this project. Default is 0 (unlimited storage). Please note that this
    feature is supported only for vSphere cloud zones. Not valid for other cloud
    zone types.
    """

    updated_at: Optional[str] = FieldInfo(alias="updatedAt", default=None)
    """Date when the entity was last updated. The date is ISO 8601 and UTC."""

    zone_id: Optional[str] = FieldInfo(alias="zoneId", default=None)
    """The Cloud Zone Id"""
