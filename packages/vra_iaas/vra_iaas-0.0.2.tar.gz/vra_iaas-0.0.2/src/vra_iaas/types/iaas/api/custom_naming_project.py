# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from pydantic import Field as FieldInfo

from ...._models import BaseModel

__all__ = ["CustomNamingProject"]


class CustomNamingProject(BaseModel):
    """A representation of a Project."""

    id: Optional[str] = None
    """Unique id of custom naming project"""

    active: Optional[bool] = None
    """Flag to check if project is active"""

    default_org: Optional[bool] = FieldInfo(alias="defaultOrg", default=None)
    """Flag to represent if custom name is default for org"""

    org_id: Optional[str] = FieldInfo(alias="orgId", default=None)
    """Org id"""

    project_id: Optional[str] = FieldInfo(alias="projectId", default=None)
    """Project id mapped to custom name"""

    project_name: Optional[str] = FieldInfo(alias="projectName", default=None)
    """Name of mapped project"""
