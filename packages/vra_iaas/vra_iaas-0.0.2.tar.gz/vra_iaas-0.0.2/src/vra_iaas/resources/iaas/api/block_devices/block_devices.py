# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Iterable

import httpx

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
    block_device_delete_params,
    block_device_update_params,
    block_device_retrieve_params,
    block_device_block_devices_params,
    block_device_retrieve_block_devices_params,
)
from .....types.iaas.api.tag_param import TagParam
from .....types.iaas.api.block_device import BlockDevice
from .....types.iaas.api.projects.request_tracker import RequestTracker
from .....types.iaas.api.placement_constraint_param import PlacementConstraintParam
from .....types.iaas.api.machines.block_device_result import BlockDeviceResult

__all__ = ["BlockDevicesResource", "AsyncBlockDevicesResource"]


class BlockDevicesResource(SyncAPIResource):
    @cached_property
    def operations(self) -> OperationsResource:
        return OperationsResource(self._client)

    @cached_property
    def snapshots(self) -> SnapshotsResource:
        return SnapshotsResource(self._client)

    @cached_property
    def with_raw_response(self) -> BlockDevicesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#accessing-raw-response-data-eg-headers
        """
        return BlockDevicesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> BlockDevicesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#with_streaming_response
        """
        return BlockDevicesResourceWithStreamingResponse(self)

    def retrieve(
        self,
        id: str,
        *,
        api_version: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> BlockDevice:
        """
        Get a single BlockDevice

        Args:
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
            f"/iaas/api/block-devices/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"api_version": api_version}, block_device_retrieve_params.BlockDeviceRetrieveParams
                ),
            ),
            cast_to=BlockDevice,
        )

    def update(
        self,
        id: str,
        *,
        capacity_in_gb: int,
        api_version: str | Omit = omit,
        use_sdrs: bool | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RequestTracker:
        """
        Resize operation on block device.

        Args:
          capacity_in_gb: Resize Capacity in GB

          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          use_sdrs: Only applicable for vSphere block-devices deployed on SDRS cluster. If set to
              true, SDRS Recommendation will be used for resize operation.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._post(
            f"/iaas/api/block-devices/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "capacity_in_gb": capacity_in_gb,
                        "api_version": api_version,
                        "use_sdrs": use_sdrs,
                    },
                    block_device_update_params.BlockDeviceUpdateParams,
                ),
            ),
            cast_to=RequestTracker,
        )

    def delete(
        self,
        id: str,
        *,
        api_version: str | Omit = omit,
        force_delete: bool | Omit = omit,
        purge: bool | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RequestTracker:
        """Delete a BlockDevice

        1.

        A block device cannot be deleted when attached to a machine.

        2. A block device with persistent property set to 'false' is deleted.

        3. A block device with persistent property set to 'true' needs an additional
           parameter 'purge' to be set to true, for deletion.

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          force_delete: Controls whether this is a force delete operation. If true, best effort is made
              for deleting this block device. Use with caution as force deleting may cause
              inconsistencies between the cloud provider and VMware Aria Automation.

          purge: Controls whether this is a force delete operation. If true, best effort is made
              for deleting this block device. Use with caution as force deleting may cause
              inconsistencies between the cloud provider and VMware Aria Automation.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._delete(
            f"/iaas/api/block-devices/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "api_version": api_version,
                        "force_delete": force_delete,
                        "purge": purge,
                    },
                    block_device_delete_params.BlockDeviceDeleteParams,
                ),
            ),
            cast_to=RequestTracker,
        )

    def block_devices(
        self,
        *,
        capacity_in_gb: int,
        name: str,
        project_id: str,
        api_version: str | Omit = omit,
        constraints: Iterable[PlacementConstraintParam] | Omit = omit,
        custom_properties: Dict[str, str] | Omit = omit,
        deployment_id: str | Omit = omit,
        description: str | Omit = omit,
        disk_content_base64: str | Omit = omit,
        encrypted: bool | Omit = omit,
        persistent: bool | Omit = omit,
        source_reference: str | Omit = omit,
        tags: Iterable[TagParam] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RequestTracker:
        """
        Following disk custom properties can be passed while creating a block device:

            1. dataStore: Defines name of the datastore in which the disk has to be provisioned.

            2. storagePolicy: Defines name of the storage policy in which the disk has to be provisioned. If name of the datastore is specified in the custom properties then, datastore takes precedence.

            3. provisioningType: Defines the type of provisioning. For eg. thick/thin.

            4. resourceGroupName: Defines the Azure resource group name where the disk needs to be provisioned.

        Args:
          capacity_in_gb: Capacity of the block device in GB.

          name: A human-friendly name used as an identifier in APIs that support this option.

          project_id: The id of the project the current user belongs to.

          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          constraints: Constraints that are used to drive placement policies for the block device that
              is produced from this specification. Constraint expressions are matched against
              tags on existing placement targets.

          custom_properties: Additional custom properties that may be used to extend this resource.

          deployment_id: The id of the deployment that is associated with this resource

          description: A human-friendly description.

          disk_content_base64: Content of a disk, base64 encoded.

          encrypted: Indicates whether the block device should be encrypted or not.

          persistent: Indicates whether the block device survives a delete action.

          source_reference: Reference to URI using which the block device has to be created.

          tags: A set of tag keys and optional values that should be set on any resource that is
              produced from this specification.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/iaas/api/block-devices",
            body=maybe_transform(
                {
                    "capacity_in_gb": capacity_in_gb,
                    "name": name,
                    "project_id": project_id,
                    "constraints": constraints,
                    "custom_properties": custom_properties,
                    "deployment_id": deployment_id,
                    "description": description,
                    "disk_content_base64": disk_content_base64,
                    "encrypted": encrypted,
                    "persistent": persistent,
                    "source_reference": source_reference,
                    "tags": tags,
                },
                block_device_block_devices_params.BlockDeviceBlockDevicesParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"api_version": api_version}, block_device_block_devices_params.BlockDeviceBlockDevicesParams
                ),
            ),
            cast_to=RequestTracker,
        )

    def retrieve_block_devices(
        self,
        *,
        count: bool | Omit = omit,
        filter: str | Omit = omit,
        skip: int | Omit = omit,
        top: int | Omit = omit,
        api_version: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> BlockDeviceResult:
        """
        Get all BlockDevices

        Args:
          count: Flag which when specified, regardless of the assigned value, shows the total
              number of records. If the collection has a filter it shows the number of records
              matching the filter.

          filter: Filter the results by a specified predicate expression. Operators: eq, ne, and,
              or.

          skip: Number of records you want to skip.

          top: Number of records you want to get.

          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/iaas/api/block-devices",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "count": count,
                        "filter": filter,
                        "skip": skip,
                        "top": top,
                        "api_version": api_version,
                    },
                    block_device_retrieve_block_devices_params.BlockDeviceRetrieveBlockDevicesParams,
                ),
            ),
            cast_to=BlockDeviceResult,
        )


class AsyncBlockDevicesResource(AsyncAPIResource):
    @cached_property
    def operations(self) -> AsyncOperationsResource:
        return AsyncOperationsResource(self._client)

    @cached_property
    def snapshots(self) -> AsyncSnapshotsResource:
        return AsyncSnapshotsResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncBlockDevicesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#accessing-raw-response-data-eg-headers
        """
        return AsyncBlockDevicesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncBlockDevicesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#with_streaming_response
        """
        return AsyncBlockDevicesResourceWithStreamingResponse(self)

    async def retrieve(
        self,
        id: str,
        *,
        api_version: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> BlockDevice:
        """
        Get a single BlockDevice

        Args:
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
            f"/iaas/api/block-devices/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"api_version": api_version}, block_device_retrieve_params.BlockDeviceRetrieveParams
                ),
            ),
            cast_to=BlockDevice,
        )

    async def update(
        self,
        id: str,
        *,
        capacity_in_gb: int,
        api_version: str | Omit = omit,
        use_sdrs: bool | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RequestTracker:
        """
        Resize operation on block device.

        Args:
          capacity_in_gb: Resize Capacity in GB

          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          use_sdrs: Only applicable for vSphere block-devices deployed on SDRS cluster. If set to
              true, SDRS Recommendation will be used for resize operation.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._post(
            f"/iaas/api/block-devices/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "capacity_in_gb": capacity_in_gb,
                        "api_version": api_version,
                        "use_sdrs": use_sdrs,
                    },
                    block_device_update_params.BlockDeviceUpdateParams,
                ),
            ),
            cast_to=RequestTracker,
        )

    async def delete(
        self,
        id: str,
        *,
        api_version: str | Omit = omit,
        force_delete: bool | Omit = omit,
        purge: bool | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RequestTracker:
        """Delete a BlockDevice

        1.

        A block device cannot be deleted when attached to a machine.

        2. A block device with persistent property set to 'false' is deleted.

        3. A block device with persistent property set to 'true' needs an additional
           parameter 'purge' to be set to true, for deletion.

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          force_delete: Controls whether this is a force delete operation. If true, best effort is made
              for deleting this block device. Use with caution as force deleting may cause
              inconsistencies between the cloud provider and VMware Aria Automation.

          purge: Controls whether this is a force delete operation. If true, best effort is made
              for deleting this block device. Use with caution as force deleting may cause
              inconsistencies between the cloud provider and VMware Aria Automation.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._delete(
            f"/iaas/api/block-devices/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "api_version": api_version,
                        "force_delete": force_delete,
                        "purge": purge,
                    },
                    block_device_delete_params.BlockDeviceDeleteParams,
                ),
            ),
            cast_to=RequestTracker,
        )

    async def block_devices(
        self,
        *,
        capacity_in_gb: int,
        name: str,
        project_id: str,
        api_version: str | Omit = omit,
        constraints: Iterable[PlacementConstraintParam] | Omit = omit,
        custom_properties: Dict[str, str] | Omit = omit,
        deployment_id: str | Omit = omit,
        description: str | Omit = omit,
        disk_content_base64: str | Omit = omit,
        encrypted: bool | Omit = omit,
        persistent: bool | Omit = omit,
        source_reference: str | Omit = omit,
        tags: Iterable[TagParam] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RequestTracker:
        """
        Following disk custom properties can be passed while creating a block device:

            1. dataStore: Defines name of the datastore in which the disk has to be provisioned.

            2. storagePolicy: Defines name of the storage policy in which the disk has to be provisioned. If name of the datastore is specified in the custom properties then, datastore takes precedence.

            3. provisioningType: Defines the type of provisioning. For eg. thick/thin.

            4. resourceGroupName: Defines the Azure resource group name where the disk needs to be provisioned.

        Args:
          capacity_in_gb: Capacity of the block device in GB.

          name: A human-friendly name used as an identifier in APIs that support this option.

          project_id: The id of the project the current user belongs to.

          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          constraints: Constraints that are used to drive placement policies for the block device that
              is produced from this specification. Constraint expressions are matched against
              tags on existing placement targets.

          custom_properties: Additional custom properties that may be used to extend this resource.

          deployment_id: The id of the deployment that is associated with this resource

          description: A human-friendly description.

          disk_content_base64: Content of a disk, base64 encoded.

          encrypted: Indicates whether the block device should be encrypted or not.

          persistent: Indicates whether the block device survives a delete action.

          source_reference: Reference to URI using which the block device has to be created.

          tags: A set of tag keys and optional values that should be set on any resource that is
              produced from this specification.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/iaas/api/block-devices",
            body=await async_maybe_transform(
                {
                    "capacity_in_gb": capacity_in_gb,
                    "name": name,
                    "project_id": project_id,
                    "constraints": constraints,
                    "custom_properties": custom_properties,
                    "deployment_id": deployment_id,
                    "description": description,
                    "disk_content_base64": disk_content_base64,
                    "encrypted": encrypted,
                    "persistent": persistent,
                    "source_reference": source_reference,
                    "tags": tags,
                },
                block_device_block_devices_params.BlockDeviceBlockDevicesParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"api_version": api_version}, block_device_block_devices_params.BlockDeviceBlockDevicesParams
                ),
            ),
            cast_to=RequestTracker,
        )

    async def retrieve_block_devices(
        self,
        *,
        count: bool | Omit = omit,
        filter: str | Omit = omit,
        skip: int | Omit = omit,
        top: int | Omit = omit,
        api_version: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> BlockDeviceResult:
        """
        Get all BlockDevices

        Args:
          count: Flag which when specified, regardless of the assigned value, shows the total
              number of records. If the collection has a filter it shows the number of records
              matching the filter.

          filter: Filter the results by a specified predicate expression. Operators: eq, ne, and,
              or.

          skip: Number of records you want to skip.

          top: Number of records you want to get.

          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/iaas/api/block-devices",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "count": count,
                        "filter": filter,
                        "skip": skip,
                        "top": top,
                        "api_version": api_version,
                    },
                    block_device_retrieve_block_devices_params.BlockDeviceRetrieveBlockDevicesParams,
                ),
            ),
            cast_to=BlockDeviceResult,
        )


class BlockDevicesResourceWithRawResponse:
    def __init__(self, block_devices: BlockDevicesResource) -> None:
        self._block_devices = block_devices

        self.retrieve = to_raw_response_wrapper(
            block_devices.retrieve,
        )
        self.update = to_raw_response_wrapper(
            block_devices.update,
        )
        self.delete = to_raw_response_wrapper(
            block_devices.delete,
        )
        self.block_devices = to_raw_response_wrapper(
            block_devices.block_devices,
        )
        self.retrieve_block_devices = to_raw_response_wrapper(
            block_devices.retrieve_block_devices,
        )

    @cached_property
    def operations(self) -> OperationsResourceWithRawResponse:
        return OperationsResourceWithRawResponse(self._block_devices.operations)

    @cached_property
    def snapshots(self) -> SnapshotsResourceWithRawResponse:
        return SnapshotsResourceWithRawResponse(self._block_devices.snapshots)


class AsyncBlockDevicesResourceWithRawResponse:
    def __init__(self, block_devices: AsyncBlockDevicesResource) -> None:
        self._block_devices = block_devices

        self.retrieve = async_to_raw_response_wrapper(
            block_devices.retrieve,
        )
        self.update = async_to_raw_response_wrapper(
            block_devices.update,
        )
        self.delete = async_to_raw_response_wrapper(
            block_devices.delete,
        )
        self.block_devices = async_to_raw_response_wrapper(
            block_devices.block_devices,
        )
        self.retrieve_block_devices = async_to_raw_response_wrapper(
            block_devices.retrieve_block_devices,
        )

    @cached_property
    def operations(self) -> AsyncOperationsResourceWithRawResponse:
        return AsyncOperationsResourceWithRawResponse(self._block_devices.operations)

    @cached_property
    def snapshots(self) -> AsyncSnapshotsResourceWithRawResponse:
        return AsyncSnapshotsResourceWithRawResponse(self._block_devices.snapshots)


class BlockDevicesResourceWithStreamingResponse:
    def __init__(self, block_devices: BlockDevicesResource) -> None:
        self._block_devices = block_devices

        self.retrieve = to_streamed_response_wrapper(
            block_devices.retrieve,
        )
        self.update = to_streamed_response_wrapper(
            block_devices.update,
        )
        self.delete = to_streamed_response_wrapper(
            block_devices.delete,
        )
        self.block_devices = to_streamed_response_wrapper(
            block_devices.block_devices,
        )
        self.retrieve_block_devices = to_streamed_response_wrapper(
            block_devices.retrieve_block_devices,
        )

    @cached_property
    def operations(self) -> OperationsResourceWithStreamingResponse:
        return OperationsResourceWithStreamingResponse(self._block_devices.operations)

    @cached_property
    def snapshots(self) -> SnapshotsResourceWithStreamingResponse:
        return SnapshotsResourceWithStreamingResponse(self._block_devices.snapshots)


class AsyncBlockDevicesResourceWithStreamingResponse:
    def __init__(self, block_devices: AsyncBlockDevicesResource) -> None:
        self._block_devices = block_devices

        self.retrieve = async_to_streamed_response_wrapper(
            block_devices.retrieve,
        )
        self.update = async_to_streamed_response_wrapper(
            block_devices.update,
        )
        self.delete = async_to_streamed_response_wrapper(
            block_devices.delete,
        )
        self.block_devices = async_to_streamed_response_wrapper(
            block_devices.block_devices,
        )
        self.retrieve_block_devices = async_to_streamed_response_wrapper(
            block_devices.retrieve_block_devices,
        )

    @cached_property
    def operations(self) -> AsyncOperationsResourceWithStreamingResponse:
        return AsyncOperationsResourceWithStreamingResponse(self._block_devices.operations)

    @cached_property
    def snapshots(self) -> AsyncSnapshotsResourceWithStreamingResponse:
        return AsyncSnapshotsResourceWithStreamingResponse(self._block_devices.snapshots)
