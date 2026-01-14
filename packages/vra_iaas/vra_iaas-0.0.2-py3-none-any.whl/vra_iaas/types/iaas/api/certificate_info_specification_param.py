# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["CertificateInfoSpecificationParam"]


class CertificateInfoSpecificationParam(TypedDict, total=False):
    """Specification for certificate for a cloud account."""

    certificate: Required[str]
    """The certificate in string format."""
