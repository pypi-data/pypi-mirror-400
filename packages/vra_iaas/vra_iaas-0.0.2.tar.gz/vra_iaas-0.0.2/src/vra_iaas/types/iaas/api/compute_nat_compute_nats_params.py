# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Iterable
from typing_extensions import Required, Annotated, TypedDict

from ...._utils import PropertyInfo
from .compute_nats.nat_rule_param import NatRuleParam

__all__ = ["ComputeNatComputeNatsParams"]


class ComputeNatComputeNatsParams(TypedDict, total=False):
    gateway: Required[str]
    """Id of the Compute Gateway to which the Compute Nat resource will be attached"""

    name: Required[str]
    """A human-friendly name used as an identifier in APIs that support this option."""

    nat_rules: Required[Annotated[Iterable[NatRuleParam], PropertyInfo(alias="natRules")]]
    """List of NAT Rules"""

    project_id: Required[Annotated[str, PropertyInfo(alias="projectId")]]
    """The id of the project the current user belongs to."""

    api_version: Annotated[str, PropertyInfo(alias="apiVersion")]
    """The version of the API in yyyy-MM-dd format (UTC).

    For versioning information refer to /iaas/api/about
    """

    custom_properties: Annotated[Dict[str, str], PropertyInfo(alias="customProperties")]
    """Additional custom properties that may be used to extend this resource."""

    deployment_id: Annotated[str, PropertyInfo(alias="deploymentId")]
    """The id of the deployment that is associated with this resource"""
