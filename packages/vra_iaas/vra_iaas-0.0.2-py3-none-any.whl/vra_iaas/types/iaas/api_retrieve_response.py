# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, Optional
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["APIRetrieveResponse"]


class APIRetrieveResponse(BaseModel):
    """Certificate for a cloud account."""

    certificate: str
    """The certificate in string format."""

    properties: Dict[str, str]
    """
    Certificate related properties which may provide additional information about
    the given certificate.
    """

    certificate_error_detail: Optional[
        Literal[
            "UNTRUSTED_CERTIFICATE",
            "EXPIRED_CERTIFICATE",
            "NOT_YET_VALID_CERTIFICATE",
            "KEYSTORE_TAMPERED_OR_PASSWORD_INCORRECT",
        ]
    ] = FieldInfo(alias="certificateErrorDetail", default=None)
    """Details about the certificate."""
