# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Iterable

import httpx

from .disks import (
    DisksResource,
    AsyncDisksResource,
    DisksResourceWithRawResponse,
    AsyncDisksResourceWithRawResponse,
    DisksResourceWithStreamingResponse,
    AsyncDisksResourceWithStreamingResponse,
)
from .snapshots import (
    SnapshotsResource,
    AsyncSnapshotsResource,
    SnapshotsResourceWithRawResponse,
    AsyncSnapshotsResourceWithRawResponse,
    SnapshotsResourceWithStreamingResponse,
    AsyncSnapshotsResourceWithStreamingResponse,
)
from ....._types import Body, Omit, Query, Headers, NotGiven, omit, not_given
from ....._utils import maybe_transform, async_maybe_transform
from .operations import (
    OperationsResource,
    AsyncOperationsResource,
    OperationsResourceWithRawResponse,
    AsyncOperationsResourceWithRawResponse,
    OperationsResourceWithStreamingResponse,
    AsyncOperationsResourceWithStreamingResponse,
)
from ....._compat import cached_property
from ....._resource import SyncAPIResource, AsyncAPIResource
from ....._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ....._base_client import make_request_options
from .....types.iaas.api import (
    machine_list_params,
    machine_create_params,
    machine_delete_params,
    machine_update_params,
    machine_retrieve_params,
)
from .network_interfaces import (
    NetworkInterfacesResource,
    AsyncNetworkInterfacesResource,
    NetworkInterfacesResourceWithRawResponse,
    AsyncNetworkInterfacesResourceWithRawResponse,
    NetworkInterfacesResourceWithStreamingResponse,
    AsyncNetworkInterfacesResourceWithStreamingResponse,
)
from .....types.iaas.api.machine import Machine
from .....types.iaas.api.tag_param import TagParam
from .....types.iaas.api.machine_list_response import MachineListResponse
from .....types.iaas.api.projects.request_tracker import RequestTracker
from .....types.iaas.api.salt_configuration_param import SaltConfigurationParam
from .....types.iaas.api.machine_boot_config_param import MachineBootConfigParam
from .....types.iaas.api.placement_constraint_param import PlacementConstraintParam
from .....types.iaas.api.machines.disk_attachment_specification_param import DiskAttachmentSpecificationParam
from .....types.iaas.api.machines.network_interface_specification_param import NetworkInterfaceSpecificationParam

__all__ = ["MachinesResource", "AsyncMachinesResource"]


class MachinesResource(SyncAPIResource):
    @cached_property
    def operations(self) -> OperationsResource:
        return OperationsResource(self._client)

    @cached_property
    def disks(self) -> DisksResource:
        return DisksResource(self._client)

    @cached_property
    def network_interfaces(self) -> NetworkInterfacesResource:
        return NetworkInterfacesResource(self._client)

    @cached_property
    def snapshots(self) -> SnapshotsResource:
        return SnapshotsResource(self._client)

    @cached_property
    def with_raw_response(self) -> MachinesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#accessing-raw-response-data-eg-headers
        """
        return MachinesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> MachinesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#with_streaming_response
        """
        return MachinesResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        flavor: str,
        flavor_ref: str,
        image: str,
        image_ref: str,
        name: str,
        project_id: str,
        api_version: str | Omit = omit,
        boot_config: MachineBootConfigParam | Omit = omit,
        boot_config_settings: machine_create_params.BootConfigSettings | Omit = omit,
        constraints: Iterable[PlacementConstraintParam] | Omit = omit,
        custom_properties: Dict[str, str] | Omit = omit,
        deployment_id: str | Omit = omit,
        description: str | Omit = omit,
        disks: Iterable[DiskAttachmentSpecificationParam] | Omit = omit,
        image_disk_constraints: Iterable[PlacementConstraintParam] | Omit = omit,
        machine_count: int | Omit = omit,
        nics: Iterable[NetworkInterfaceSpecificationParam] | Omit = omit,
        remote_access: machine_create_params.RemoteAccess | Omit = omit,
        salt_configuration: SaltConfigurationParam | Omit = omit,
        tags: Iterable[TagParam] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RequestTracker:
        """
        Create machine

        Args:
          flavor: Flavor of machine instance.

          flavor_ref: Provider specific flavor reference. Valid if no flavor property is provided

          image: Type of image used for this machine.

          image_ref: Direct image reference used for this machine (name, path, location, uri, etc.).
              Valid if no image property is provided

          name: A human-friendly name used as an identifier in APIs that support this option.

          project_id: The id of the project the current user belongs to.

          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          boot_config: Machine boot config that will be passed to the instance that can be used to
              perform common automated configuration tasks and even run scripts after the
              instance starts.

          boot_config_settings: Machine boot config settings that will define how the provisioning will handle
              the boot config script execution.

          constraints: Constraints that are used to drive placement policies for the virtual machine
              that is produced from this specification. Constraint expressions are matched
              against tags on existing placement targets.

          custom_properties: Additional custom properties that may be used to extend this resource.

          deployment_id: The id of the deployment that is associated with this resource

          description: Describes machine within the scope of your organization and is not propagated to
              the cloud

          disks: A set of disk specifications for this machine.

          image_disk_constraints: Constraints that are used to drive placement policies for the image disk.
              Constraint expressions are matched against tags on existing placement targets.

          machine_count: Number of machines to provision - default 1.

          nics: A set of network interface controller specifications for this machine. If not
              specified, then a default network connection will be created.

          remote_access: Represents a specification for machine's remote access settings.

          salt_configuration: Represents salt configuration settings that has to be applied on the machine. To
              successfully apply the configurations, remoteAccess property is mandatory.The
              supported remoteAccess authentication types are usernamePassword and
              generatedPublicPrivateKey

          tags: A set of tag keys and optional values that should be set on any resource that is
              produced from this specification.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/iaas/api/machines",
            body=maybe_transform(
                {
                    "flavor": flavor,
                    "flavor_ref": flavor_ref,
                    "image": image,
                    "image_ref": image_ref,
                    "name": name,
                    "project_id": project_id,
                    "boot_config": boot_config,
                    "boot_config_settings": boot_config_settings,
                    "constraints": constraints,
                    "custom_properties": custom_properties,
                    "deployment_id": deployment_id,
                    "description": description,
                    "disks": disks,
                    "image_disk_constraints": image_disk_constraints,
                    "machine_count": machine_count,
                    "nics": nics,
                    "remote_access": remote_access,
                    "salt_configuration": salt_configuration,
                    "tags": tags,
                },
                machine_create_params.MachineCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"api_version": api_version}, machine_create_params.MachineCreateParams),
            ),
            cast_to=RequestTracker,
        )

    def retrieve(
        self,
        id: str,
        *,
        select: str | Omit = omit,
        api_version: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Machine:
        """
        Get machine with a given id

        Args:
          select: Select a subset of properties to include in the response.

          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._get(
            f"/iaas/api/machines/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "select": select,
                        "api_version": api_version,
                    },
                    machine_retrieve_params.MachineRetrieveParams,
                ),
            ),
            cast_to=Machine,
        )

    def update(
        self,
        id: str,
        *,
        api_version: str | Omit = omit,
        boot_config: MachineBootConfigParam | Omit = omit,
        custom_properties: Dict[str, str] | Omit = omit,
        description: str | Omit = omit,
        tags: Iterable[TagParam] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Machine:
        """Update machine.

        Only description, tag, custom property and bootConfig updates
        are supported. Please note that all existing tags, assigned to this machine,
        that are not implicitly added in the Patch body, will be unassigned from this
        machine!All other properties in the MachineSpecification body are ignored.

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          boot_config: Machine boot config that will be passed to the instance that can be used to
              perform common automated configuration tasks and even run scripts after the
              instance starts.

          custom_properties: Additional custom properties that may be used to extend the machine. Internal
              custom properties (for example, prefixed with: "\\__\\__") are discarded.

          description: Describes machine within the scope of your organization and is not propagated to
              the cloud

          tags: A set of tag keys and optional values that should be set on any resource that is
              produced from this specification.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._patch(
            f"/iaas/api/machines/{id}",
            body=maybe_transform(
                {
                    "boot_config": boot_config,
                    "custom_properties": custom_properties,
                    "description": description,
                    "tags": tags,
                },
                machine_update_params.MachineUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"api_version": api_version}, machine_update_params.MachineUpdateParams),
            ),
            cast_to=Machine,
        )

    def list(
        self,
        *,
        count: bool | Omit = omit,
        filter: str | Omit = omit,
        select: str | Omit = omit,
        skip: int | Omit = omit,
        top: int | Omit = omit,
        api_version: str | Omit = omit,
        skip_operation_links: bool | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> MachineListResponse:
        """
        Get all machines

        Args:
          count: Flag which when specified, regardless of the assigned value, shows the total
              number of records. If the collection has a filter it shows the number of records
              matching the filter.

          filter: Filter the results by a specified predicate expression. Operators: eq, ne, and,
              or.

          select: Select a subset of properties to include in the response.

          skip: Number of records you want to skip.

          top: Number of records you want to get.

          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          skip_operation_links: If set to true will not return operation links.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/iaas/api/machines",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "count": count,
                        "filter": filter,
                        "select": select,
                        "skip": skip,
                        "top": top,
                        "api_version": api_version,
                        "skip_operation_links": skip_operation_links,
                    },
                    machine_list_params.MachineListParams,
                ),
            ),
            cast_to=MachineListResponse,
        )

    def delete(
        self,
        id: str,
        *,
        api_version: str | Omit = omit,
        force_delete: bool | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RequestTracker:
        """
        Delete Machine with a given id

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          force_delete: Controls whether this is a force delete operation. If true, best effort is made
              for deleting this machine. Use with caution as force deleting may cause
              inconsistencies between the cloud provider and VMware Aria Automation.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._delete(
            f"/iaas/api/machines/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "api_version": api_version,
                        "force_delete": force_delete,
                    },
                    machine_delete_params.MachineDeleteParams,
                ),
            ),
            cast_to=RequestTracker,
        )


class AsyncMachinesResource(AsyncAPIResource):
    @cached_property
    def operations(self) -> AsyncOperationsResource:
        return AsyncOperationsResource(self._client)

    @cached_property
    def disks(self) -> AsyncDisksResource:
        return AsyncDisksResource(self._client)

    @cached_property
    def network_interfaces(self) -> AsyncNetworkInterfacesResource:
        return AsyncNetworkInterfacesResource(self._client)

    @cached_property
    def snapshots(self) -> AsyncSnapshotsResource:
        return AsyncSnapshotsResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncMachinesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#accessing-raw-response-data-eg-headers
        """
        return AsyncMachinesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncMachinesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#with_streaming_response
        """
        return AsyncMachinesResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        flavor: str,
        flavor_ref: str,
        image: str,
        image_ref: str,
        name: str,
        project_id: str,
        api_version: str | Omit = omit,
        boot_config: MachineBootConfigParam | Omit = omit,
        boot_config_settings: machine_create_params.BootConfigSettings | Omit = omit,
        constraints: Iterable[PlacementConstraintParam] | Omit = omit,
        custom_properties: Dict[str, str] | Omit = omit,
        deployment_id: str | Omit = omit,
        description: str | Omit = omit,
        disks: Iterable[DiskAttachmentSpecificationParam] | Omit = omit,
        image_disk_constraints: Iterable[PlacementConstraintParam] | Omit = omit,
        machine_count: int | Omit = omit,
        nics: Iterable[NetworkInterfaceSpecificationParam] | Omit = omit,
        remote_access: machine_create_params.RemoteAccess | Omit = omit,
        salt_configuration: SaltConfigurationParam | Omit = omit,
        tags: Iterable[TagParam] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RequestTracker:
        """
        Create machine

        Args:
          flavor: Flavor of machine instance.

          flavor_ref: Provider specific flavor reference. Valid if no flavor property is provided

          image: Type of image used for this machine.

          image_ref: Direct image reference used for this machine (name, path, location, uri, etc.).
              Valid if no image property is provided

          name: A human-friendly name used as an identifier in APIs that support this option.

          project_id: The id of the project the current user belongs to.

          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          boot_config: Machine boot config that will be passed to the instance that can be used to
              perform common automated configuration tasks and even run scripts after the
              instance starts.

          boot_config_settings: Machine boot config settings that will define how the provisioning will handle
              the boot config script execution.

          constraints: Constraints that are used to drive placement policies for the virtual machine
              that is produced from this specification. Constraint expressions are matched
              against tags on existing placement targets.

          custom_properties: Additional custom properties that may be used to extend this resource.

          deployment_id: The id of the deployment that is associated with this resource

          description: Describes machine within the scope of your organization and is not propagated to
              the cloud

          disks: A set of disk specifications for this machine.

          image_disk_constraints: Constraints that are used to drive placement policies for the image disk.
              Constraint expressions are matched against tags on existing placement targets.

          machine_count: Number of machines to provision - default 1.

          nics: A set of network interface controller specifications for this machine. If not
              specified, then a default network connection will be created.

          remote_access: Represents a specification for machine's remote access settings.

          salt_configuration: Represents salt configuration settings that has to be applied on the machine. To
              successfully apply the configurations, remoteAccess property is mandatory.The
              supported remoteAccess authentication types are usernamePassword and
              generatedPublicPrivateKey

          tags: A set of tag keys and optional values that should be set on any resource that is
              produced from this specification.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/iaas/api/machines",
            body=await async_maybe_transform(
                {
                    "flavor": flavor,
                    "flavor_ref": flavor_ref,
                    "image": image,
                    "image_ref": image_ref,
                    "name": name,
                    "project_id": project_id,
                    "boot_config": boot_config,
                    "boot_config_settings": boot_config_settings,
                    "constraints": constraints,
                    "custom_properties": custom_properties,
                    "deployment_id": deployment_id,
                    "description": description,
                    "disks": disks,
                    "image_disk_constraints": image_disk_constraints,
                    "machine_count": machine_count,
                    "nics": nics,
                    "remote_access": remote_access,
                    "salt_configuration": salt_configuration,
                    "tags": tags,
                },
                machine_create_params.MachineCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"api_version": api_version}, machine_create_params.MachineCreateParams
                ),
            ),
            cast_to=RequestTracker,
        )

    async def retrieve(
        self,
        id: str,
        *,
        select: str | Omit = omit,
        api_version: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Machine:
        """
        Get machine with a given id

        Args:
          select: Select a subset of properties to include in the response.

          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._get(
            f"/iaas/api/machines/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "select": select,
                        "api_version": api_version,
                    },
                    machine_retrieve_params.MachineRetrieveParams,
                ),
            ),
            cast_to=Machine,
        )

    async def update(
        self,
        id: str,
        *,
        api_version: str | Omit = omit,
        boot_config: MachineBootConfigParam | Omit = omit,
        custom_properties: Dict[str, str] | Omit = omit,
        description: str | Omit = omit,
        tags: Iterable[TagParam] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Machine:
        """Update machine.

        Only description, tag, custom property and bootConfig updates
        are supported. Please note that all existing tags, assigned to this machine,
        that are not implicitly added in the Patch body, will be unassigned from this
        machine!All other properties in the MachineSpecification body are ignored.

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          boot_config: Machine boot config that will be passed to the instance that can be used to
              perform common automated configuration tasks and even run scripts after the
              instance starts.

          custom_properties: Additional custom properties that may be used to extend the machine. Internal
              custom properties (for example, prefixed with: "\\__\\__") are discarded.

          description: Describes machine within the scope of your organization and is not propagated to
              the cloud

          tags: A set of tag keys and optional values that should be set on any resource that is
              produced from this specification.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._patch(
            f"/iaas/api/machines/{id}",
            body=await async_maybe_transform(
                {
                    "boot_config": boot_config,
                    "custom_properties": custom_properties,
                    "description": description,
                    "tags": tags,
                },
                machine_update_params.MachineUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"api_version": api_version}, machine_update_params.MachineUpdateParams
                ),
            ),
            cast_to=Machine,
        )

    async def list(
        self,
        *,
        count: bool | Omit = omit,
        filter: str | Omit = omit,
        select: str | Omit = omit,
        skip: int | Omit = omit,
        top: int | Omit = omit,
        api_version: str | Omit = omit,
        skip_operation_links: bool | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> MachineListResponse:
        """
        Get all machines

        Args:
          count: Flag which when specified, regardless of the assigned value, shows the total
              number of records. If the collection has a filter it shows the number of records
              matching the filter.

          filter: Filter the results by a specified predicate expression. Operators: eq, ne, and,
              or.

          select: Select a subset of properties to include in the response.

          skip: Number of records you want to skip.

          top: Number of records you want to get.

          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          skip_operation_links: If set to true will not return operation links.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/iaas/api/machines",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "count": count,
                        "filter": filter,
                        "select": select,
                        "skip": skip,
                        "top": top,
                        "api_version": api_version,
                        "skip_operation_links": skip_operation_links,
                    },
                    machine_list_params.MachineListParams,
                ),
            ),
            cast_to=MachineListResponse,
        )

    async def delete(
        self,
        id: str,
        *,
        api_version: str | Omit = omit,
        force_delete: bool | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RequestTracker:
        """
        Delete Machine with a given id

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          force_delete: Controls whether this is a force delete operation. If true, best effort is made
              for deleting this machine. Use with caution as force deleting may cause
              inconsistencies between the cloud provider and VMware Aria Automation.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._delete(
            f"/iaas/api/machines/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "api_version": api_version,
                        "force_delete": force_delete,
                    },
                    machine_delete_params.MachineDeleteParams,
                ),
            ),
            cast_to=RequestTracker,
        )


class MachinesResourceWithRawResponse:
    def __init__(self, machines: MachinesResource) -> None:
        self._machines = machines

        self.create = to_raw_response_wrapper(
            machines.create,
        )
        self.retrieve = to_raw_response_wrapper(
            machines.retrieve,
        )
        self.update = to_raw_response_wrapper(
            machines.update,
        )
        self.list = to_raw_response_wrapper(
            machines.list,
        )
        self.delete = to_raw_response_wrapper(
            machines.delete,
        )

    @cached_property
    def operations(self) -> OperationsResourceWithRawResponse:
        return OperationsResourceWithRawResponse(self._machines.operations)

    @cached_property
    def disks(self) -> DisksResourceWithRawResponse:
        return DisksResourceWithRawResponse(self._machines.disks)

    @cached_property
    def network_interfaces(self) -> NetworkInterfacesResourceWithRawResponse:
        return NetworkInterfacesResourceWithRawResponse(self._machines.network_interfaces)

    @cached_property
    def snapshots(self) -> SnapshotsResourceWithRawResponse:
        return SnapshotsResourceWithRawResponse(self._machines.snapshots)


class AsyncMachinesResourceWithRawResponse:
    def __init__(self, machines: AsyncMachinesResource) -> None:
        self._machines = machines

        self.create = async_to_raw_response_wrapper(
            machines.create,
        )
        self.retrieve = async_to_raw_response_wrapper(
            machines.retrieve,
        )
        self.update = async_to_raw_response_wrapper(
            machines.update,
        )
        self.list = async_to_raw_response_wrapper(
            machines.list,
        )
        self.delete = async_to_raw_response_wrapper(
            machines.delete,
        )

    @cached_property
    def operations(self) -> AsyncOperationsResourceWithRawResponse:
        return AsyncOperationsResourceWithRawResponse(self._machines.operations)

    @cached_property
    def disks(self) -> AsyncDisksResourceWithRawResponse:
        return AsyncDisksResourceWithRawResponse(self._machines.disks)

    @cached_property
    def network_interfaces(self) -> AsyncNetworkInterfacesResourceWithRawResponse:
        return AsyncNetworkInterfacesResourceWithRawResponse(self._machines.network_interfaces)

    @cached_property
    def snapshots(self) -> AsyncSnapshotsResourceWithRawResponse:
        return AsyncSnapshotsResourceWithRawResponse(self._machines.snapshots)


class MachinesResourceWithStreamingResponse:
    def __init__(self, machines: MachinesResource) -> None:
        self._machines = machines

        self.create = to_streamed_response_wrapper(
            machines.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            machines.retrieve,
        )
        self.update = to_streamed_response_wrapper(
            machines.update,
        )
        self.list = to_streamed_response_wrapper(
            machines.list,
        )
        self.delete = to_streamed_response_wrapper(
            machines.delete,
        )

    @cached_property
    def operations(self) -> OperationsResourceWithStreamingResponse:
        return OperationsResourceWithStreamingResponse(self._machines.operations)

    @cached_property
    def disks(self) -> DisksResourceWithStreamingResponse:
        return DisksResourceWithStreamingResponse(self._machines.disks)

    @cached_property
    def network_interfaces(self) -> NetworkInterfacesResourceWithStreamingResponse:
        return NetworkInterfacesResourceWithStreamingResponse(self._machines.network_interfaces)

    @cached_property
    def snapshots(self) -> SnapshotsResourceWithStreamingResponse:
        return SnapshotsResourceWithStreamingResponse(self._machines.snapshots)


class AsyncMachinesResourceWithStreamingResponse:
    def __init__(self, machines: AsyncMachinesResource) -> None:
        self._machines = machines

        self.create = async_to_streamed_response_wrapper(
            machines.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            machines.retrieve,
        )
        self.update = async_to_streamed_response_wrapper(
            machines.update,
        )
        self.list = async_to_streamed_response_wrapper(
            machines.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            machines.delete,
        )

    @cached_property
    def operations(self) -> AsyncOperationsResourceWithStreamingResponse:
        return AsyncOperationsResourceWithStreamingResponse(self._machines.operations)

    @cached_property
    def disks(self) -> AsyncDisksResourceWithStreamingResponse:
        return AsyncDisksResourceWithStreamingResponse(self._machines.disks)

    @cached_property
    def network_interfaces(self) -> AsyncNetworkInterfacesResourceWithStreamingResponse:
        return AsyncNetworkInterfacesResourceWithStreamingResponse(self._machines.network_interfaces)

    @cached_property
    def snapshots(self) -> AsyncSnapshotsResourceWithStreamingResponse:
        return AsyncSnapshotsResourceWithStreamingResponse(self._machines.snapshots)
