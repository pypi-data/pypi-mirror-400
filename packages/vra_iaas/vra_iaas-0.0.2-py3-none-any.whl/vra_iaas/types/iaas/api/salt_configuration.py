# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List, Optional

from pydantic import Field as FieldInfo

from ...._models import BaseModel

__all__ = ["SaltConfiguration"]


class SaltConfiguration(BaseModel):
    """
    Represents salt configuration settings that has to be applied on the machine.
    To successfully apply the configurations, remoteAccess property is mandatory.The supported remoteAccess authentication types are usernamePassword and generatedPublicPrivateKey
    """

    additional_auth_params: Optional[Dict[str, str]] = FieldInfo(alias="additionalAuthParams", default=None)
    """
    Additional auth params that can be passed in for provisioning the salt minion.
    Refer: https://docs.saltproject.io/en/master/topics/cloud/profiles.html
    """

    additional_minion_params: Optional[Dict[str, str]] = FieldInfo(alias="additionalMinionParams", default=None)
    """
    Additional configuration parameters for the salt minion, to be passed in as
    dictionary. Refer:
    https://docs.saltproject.io/en/latest/ref/configuration/minion.html
    """

    installer_file_name: Optional[str] = FieldInfo(alias="installerFileName", default=None)
    """
    Salt minion installer file name on the master. This property is currently not
    being used by any SaltStack operation.
    """

    master_id: Optional[str] = FieldInfo(alias="masterId", default=None)
    """Salt master id to which the Salt minion will be connected to."""

    minion_id: Optional[str] = FieldInfo(alias="minionId", default=None)
    """Salt minion ID to be assigned to the deployed minion."""

    pillar_environment: Optional[str] = FieldInfo(alias="pillarEnvironment", default=None)
    """
    Pillar environment to use when running state files. Refer:
    https://docs.saltproject.io/en/latest/ref/modules/all/salt.modules.state.html
    """

    salt_environment: Optional[str] = FieldInfo(alias="saltEnvironment", default=None)
    """Salt environment to use when running state files."""

    state_files: Optional[List[str]] = FieldInfo(alias="stateFiles", default=None)
    """List of state files to run on the deployed minion."""

    variables: Optional[Dict[str, str]] = None
    """Parameters required by the state file to run on the deployed minion."""
