# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from pydantic import Field as FieldInfo

from ...._models import BaseModel

__all__ = ["DataCollectorDataCollectorsResponse"]


class DataCollectorDataCollectorsResponse(BaseModel):
    """
    Data collector registration object.<br>The supplied data collector is an OVA tool that contains the credentials and protocols needed to create a connection between a data collector appliance on a host vCenter and a vCenter-based cloud account. . The process of deploying data collector is: <br> 1. Download the data collector ova from the "ovaLink".<br>2. Import the .ova file to the vCenter Server and start the installation.<br> 3. When asked for the key, copy and use the "key" provided.<br> 4. It takes a few minutes to detect your Data Collector after it is deployed and powered on in vCenter.
    """

    key: str
    """A registration key for the data collector"""

    ova_link: str = FieldInfo(alias="ovaLink")
    """Data collector OVA Link"""
