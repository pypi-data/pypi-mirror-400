# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from pydantic import Field as FieldInfo

from ...._models import BaseModel
from .cloud_account_avi_lb import CloudAccountAviLb

__all__ = ["CloudAccountsAvilbRetrieveCloudAccountsAvilbResponse"]


class CloudAccountsAvilbRetrieveCloudAccountsAvilbResponse(BaseModel):
    """State object representing a query result of AVI Load Balancer cloud accounts."""

    content: Optional[List[CloudAccountAviLb]] = None
    """List of content items"""

    number_of_elements: Optional[int] = FieldInfo(alias="numberOfElements", default=None)
    """Number of elements in the current page"""

    total_elements: Optional[int] = FieldInfo(alias="totalElements", default=None)
    """Total number of elements. In some cases the field may not be populated"""
