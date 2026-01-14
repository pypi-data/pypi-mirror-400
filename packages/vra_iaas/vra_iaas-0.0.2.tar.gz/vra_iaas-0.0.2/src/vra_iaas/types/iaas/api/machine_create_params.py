# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Iterable
from typing_extensions import Required, Annotated, TypedDict

from ...._utils import PropertyInfo
from .tag_param import TagParam
from .salt_configuration_param import SaltConfigurationParam
from .machine_boot_config_param import MachineBootConfigParam
from .placement_constraint_param import PlacementConstraintParam
from .machines.disk_attachment_specification_param import DiskAttachmentSpecificationParam
from .machines.network_interface_specification_param import NetworkInterfaceSpecificationParam

__all__ = ["MachineCreateParams", "BootConfigSettings", "RemoteAccess"]


class MachineCreateParams(TypedDict, total=False):
    flavor: Required[str]
    """Flavor of machine instance."""

    flavor_ref: Required[Annotated[str, PropertyInfo(alias="flavorRef")]]
    """Provider specific flavor reference. Valid if no flavor property is provided"""

    image: Required[str]
    """Type of image used for this machine."""

    image_ref: Required[Annotated[str, PropertyInfo(alias="imageRef")]]
    """Direct image reference used for this machine (name, path, location, uri, etc.).

    Valid if no image property is provided
    """

    name: Required[str]
    """A human-friendly name used as an identifier in APIs that support this option."""

    project_id: Required[Annotated[str, PropertyInfo(alias="projectId")]]
    """The id of the project the current user belongs to."""

    api_version: Annotated[str, PropertyInfo(alias="apiVersion")]
    """The version of the API in yyyy-MM-dd format (UTC).

    For versioning information refer to /iaas/api/about
    """

    boot_config: Annotated[MachineBootConfigParam, PropertyInfo(alias="bootConfig")]
    """
    Machine boot config that will be passed to the instance that can be used to
    perform common automated configuration tasks and even run scripts after the
    instance starts.
    """

    boot_config_settings: Annotated[BootConfigSettings, PropertyInfo(alias="bootConfigSettings")]
    """
    Machine boot config settings that will define how the provisioning will handle
    the boot config script execution.
    """

    constraints: Iterable[PlacementConstraintParam]
    """
    Constraints that are used to drive placement policies for the virtual machine
    that is produced from this specification. Constraint expressions are matched
    against tags on existing placement targets.
    """

    custom_properties: Annotated[Dict[str, str], PropertyInfo(alias="customProperties")]
    """Additional custom properties that may be used to extend this resource."""

    deployment_id: Annotated[str, PropertyInfo(alias="deploymentId")]
    """The id of the deployment that is associated with this resource"""

    description: str
    """
    Describes machine within the scope of your organization and is not propagated to
    the cloud
    """

    disks: Iterable[DiskAttachmentSpecificationParam]
    """A set of disk specifications for this machine."""

    image_disk_constraints: Annotated[Iterable[PlacementConstraintParam], PropertyInfo(alias="imageDiskConstraints")]
    """Constraints that are used to drive placement policies for the image disk.

    Constraint expressions are matched against tags on existing placement targets.
    """

    machine_count: Annotated[int, PropertyInfo(alias="machineCount")]
    """Number of machines to provision - default 1."""

    nics: Iterable[NetworkInterfaceSpecificationParam]
    """A set of network interface controller specifications for this machine.

    If not specified, then a default network connection will be created.
    """

    remote_access: Annotated[RemoteAccess, PropertyInfo(alias="remoteAccess")]
    """Represents a specification for machine's remote access settings."""

    salt_configuration: Annotated[SaltConfigurationParam, PropertyInfo(alias="saltConfiguration")]
    """
    Represents salt configuration settings that has to be applied on the machine. To
    successfully apply the configurations, remoteAccess property is mandatory.The
    supported remoteAccess authentication types are usernamePassword and
    generatedPublicPrivateKey
    """

    tags: Iterable[TagParam]
    """
    A set of tag keys and optional values that should be set on any resource that is
    produced from this specification.
    """


class BootConfigSettings(TypedDict, total=False):
    """
    Machine boot config settings that will define how the provisioning will handle the boot config script execution.
    """

    deployment_fail_on_cloud_config_runtime_error: Annotated[
        bool, PropertyInfo(alias="deploymentFailOnCloudConfigRuntimeError")
    ]
    """
    In case an error is thrown while processing cloud-config whether the
    provisioning process should fail or continue.
    """

    phone_home_fail_on_timeout: Annotated[bool, PropertyInfo(alias="phoneHomeFailOnTimeout")]
    """
    In case a timeout occurs whether the provisioning process should fail or
    continue.
    """

    phone_home_should_wait: Annotated[bool, PropertyInfo(alias="phoneHomeShouldWait")]
    """
    A phone_home module will be added to the Cloud Config and the provisioning will
    wait on a callback prior proceeding
    """

    phone_home_timeout_seconds: Annotated[int, PropertyInfo(alias="phoneHomeTimeoutSeconds")]
    """The period of time to wait for the phone_home module callback to occur"""


class RemoteAccess(TypedDict, total=False):
    """Represents a specification for machine's remote access settings."""

    authentication: Required[str]
    """
    One of four authentication types. `generatedPublicPrivateKey`: The provisioned
    machine generates the public/private key pair and enables SSH to use them
    without user input. `publicPrivateKey`: The user enters the private key in the
    SSH command. See remoteAccess.sshKey. `usernamePassword`: The user enters a
    username and password for remote access. `keyPairName`: The user enters an
    already existing keyPair name. See remoteAccess.keyPair
    """

    key_pair: Annotated[str, PropertyInfo(alias="keyPair")]
    """Key Pair Name."""

    password: str
    """Remote access password for the Azure machine."""

    skip_user_creation: Annotated[bool, PropertyInfo(alias="skipUserCreation")]
    """Remote access Skip user creation for machine."""

    ssh_key: Annotated[str, PropertyInfo(alias="sshKey")]
    """In key pair authentication, the public key on the provisioned machine.

    Users are expected to log in with their private key and a default username from
    the cloud provider. An AWS Ubuntu image comes with default user ubuntu, and
    Azure comes with default user azureuser. To log in by SSH:
    `ssh -i <private-key-path> ubuntu@52.90.80.153`
    `ssh -i <private-key-path> azureuser@40.76.14.255`
    """

    username: str
    """Remote access username for the Azure machine."""
