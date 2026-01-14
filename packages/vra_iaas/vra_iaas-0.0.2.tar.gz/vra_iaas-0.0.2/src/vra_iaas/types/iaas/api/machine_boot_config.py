# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ...._models import BaseModel

__all__ = ["MachineBootConfig"]


class MachineBootConfig(BaseModel):
    """
    Machine boot config that will be passed to the instance that can be used to perform common automated configuration tasks and even run scripts after the instance starts.
    """

    content: Optional[str] = None
    """A valid cloud config data in json-escaped yaml syntax"""
