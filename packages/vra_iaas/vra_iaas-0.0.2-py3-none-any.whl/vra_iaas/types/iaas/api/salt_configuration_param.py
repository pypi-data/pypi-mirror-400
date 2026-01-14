# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict
from typing_extensions import Annotated, TypedDict

from ...._types import SequenceNotStr
from ...._utils import PropertyInfo

__all__ = ["SaltConfigurationParam"]


class SaltConfigurationParam(TypedDict, total=False):
    """
    Represents salt configuration settings that has to be applied on the machine.
    To successfully apply the configurations, remoteAccess property is mandatory.The supported remoteAccess authentication types are usernamePassword and generatedPublicPrivateKey
    """

    additional_auth_params: Annotated[Dict[str, str], PropertyInfo(alias="additionalAuthParams")]
    """
    Additional auth params that can be passed in for provisioning the salt minion.
    Refer: https://docs.saltproject.io/en/master/topics/cloud/profiles.html
    """

    additional_minion_params: Annotated[Dict[str, str], PropertyInfo(alias="additionalMinionParams")]
    """
    Additional configuration parameters for the salt minion, to be passed in as
    dictionary. Refer:
    https://docs.saltproject.io/en/latest/ref/configuration/minion.html
    """

    installer_file_name: Annotated[str, PropertyInfo(alias="installerFileName")]
    """
    Salt minion installer file name on the master. This property is currently not
    being used by any SaltStack operation.
    """

    master_id: Annotated[str, PropertyInfo(alias="masterId")]
    """Salt master id to which the Salt minion will be connected to."""

    minion_id: Annotated[str, PropertyInfo(alias="minionId")]
    """Salt minion ID to be assigned to the deployed minion."""

    pillar_environment: Annotated[str, PropertyInfo(alias="pillarEnvironment")]
    """
    Pillar environment to use when running state files. Refer:
    https://docs.saltproject.io/en/latest/ref/modules/all/salt.modules.state.html
    """

    salt_environment: Annotated[str, PropertyInfo(alias="saltEnvironment")]
    """Salt environment to use when running state files."""

    state_files: Annotated[SequenceNotStr[str], PropertyInfo(alias="stateFiles")]
    """List of state files to run on the deployed minion."""

    variables: Dict[str, str]
    """Parameters required by the state file to run on the deployed minion."""
