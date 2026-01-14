# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict
from typing_extensions import Required, Annotated, TypedDict

from ....._utils import PropertyInfo

__all__ = ["DiskAttachmentSpecificationParam"]


class DiskAttachmentSpecificationParam(TypedDict, total=False):
    """Specification for attaching disk to a machine"""

    block_device_id: Required[Annotated[str, PropertyInfo(alias="blockDeviceId")]]
    """The id of the existing block device"""

    description: str
    """A human-friendly description."""

    disk_attachment_properties: Annotated[Dict[str, str], PropertyInfo(alias="diskAttachmentProperties")]
    """Disk Attachment specific properties"""

    name: str
    """A human-friendly name used as an identifier in APIs that support this option."""

    scsi_controller: Annotated[str, PropertyInfo(alias="scsiController")]
    """Deprecated: The SCSI controller to be assigned"""

    unit_number: Annotated[str, PropertyInfo(alias="unitNumber")]
    """Deprecated: The Unit Number to be assigned"""
