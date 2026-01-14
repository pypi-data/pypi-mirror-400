# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

__all__ = ["MachineBootConfigParam"]


class MachineBootConfigParam(TypedDict, total=False):
    """
    Machine boot config that will be passed to the instance that can be used to perform common automated configuration tasks and even run scripts after the instance starts.
    """

    content: str
    """A valid cloud config data in json-escaped yaml syntax"""
