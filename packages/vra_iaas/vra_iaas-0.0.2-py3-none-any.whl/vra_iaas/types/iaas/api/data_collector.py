# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from pydantic import Field as FieldInfo

from ...._models import BaseModel

__all__ = ["DataCollector"]


class DataCollector(BaseModel):
    """
    State object representing a data collector.<br>The data collector is an OVA tool that contains the credentials and protocols needed to create a connection between a data collector appliance on a host vCenter and a vCenter-based cloud account.<br><br>Filtering is currently possible for some of the data collector fields via $filter.<br>Supported fields:<br>services<br>proxyId<br>creationTimeMicros<br>customProperties<br><br>Supported operators: eq, ne, lt, gt, and, or.<br><br>By default, the obtained list contains the enabled data collectors. A query parameter "disabled=true" can be added to obtain disabled data collectors.<br><br>Special case: If the user specifies $filter=((services.item ne 'cloud_assembly_extensibility') and (services.item ne 'cloud_assembly')), which is equivalent to disabled=true, and does not specify the "disabled" parameter, the resulting query will be equivalent to ((disabled=true) and (disabled=false)). This call will return an empty list.
    """

    dc_id: str = FieldInfo(alias="dcId")
    """Data collector identifier"""

    host_name: str = FieldInfo(alias="hostName")
    """Data collector host name"""

    ip_address: str = FieldInfo(alias="ipAddress")
    """Ip Address of the data collector VM"""

    name: str
    """Data collector name"""

    status: str
    """Current status of the data collector"""
