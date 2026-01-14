# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from ....._models import BaseModel

__all__ = ["RequestTracker"]


class RequestTracker(BaseModel):
    """An object used to track long-running operations."""

    id: str
    """ID of this request."""

    progress: int
    """Progress of the request as percentage."""

    self_link: str = FieldInfo(alias="selfLink")
    """Self link of this request."""

    status: Literal["FINISHED", "INPROGRESS", "FAILED"]
    """Status of the request."""

    deployment_id: Optional[str] = FieldInfo(alias="deploymentId", default=None)
    """ID of the deployment, this request is connected to."""

    message: Optional[str] = None
    """Status message of the request."""

    name: Optional[str] = None
    """Name of the operation."""

    resources: Optional[List[str]] = None
    """Collection of resources."""
