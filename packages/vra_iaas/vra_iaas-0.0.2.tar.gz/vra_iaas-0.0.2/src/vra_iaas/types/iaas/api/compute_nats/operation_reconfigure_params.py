# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Required, Annotated, TypedDict

from ....._utils import PropertyInfo
from .nat_rule_param import NatRuleParam

__all__ = ["OperationReconfigureParams"]


class OperationReconfigureParams(TypedDict, total=False):
    nat_rules: Required[Annotated[Iterable[NatRuleParam], PropertyInfo(alias="natRules")]]
    """List of NAT rules to be applied on this Compute Nat."""

    api_version: Annotated[str, PropertyInfo(alias="apiVersion")]
    """The version of the API in yyyy-MM-dd format (UTC).

    For versioning information refer to /iaas/api/about
    """
