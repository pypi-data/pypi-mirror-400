# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict

import httpx

from ....._types import Body, Omit, Query, Headers, NotGiven, omit, not_given
from ....._utils import maybe_transform, async_maybe_transform
from ....._compat import cached_property
from ....._resource import SyncAPIResource, AsyncAPIResource
from ....._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ....._base_client import make_request_options
from .....types.iaas.api.machines import disk_list_params, disk_create_params, disk_delete_params, disk_retrieve_params
from .....types.iaas.api.block_device import BlockDevice
from .....types.iaas.api.projects.request_tracker import RequestTracker
from .....types.iaas.api.machines.block_device_result import BlockDeviceResult

__all__ = ["DisksResource", "AsyncDisksResource"]


class DisksResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> DisksResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#accessing-raw-response-data-eg-headers
        """
        return DisksResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> DisksResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#with_streaming_response
        """
        return DisksResourceWithStreamingResponse(self)

    def create(
        self,
        id: str,
        *,
        block_device_id: str,
        api_version: str | Omit = omit,
        description: str | Omit = omit,
        disk_attachment_properties: Dict[str, str] | Omit = omit,
        name: str | Omit = omit,
        scsi_controller: str | Omit = omit,
        unit_number: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RequestTracker:
        """
        Attach a disk to a machine.

        Args:
          block_device_id: The id of the existing block device

          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          description: A human-friendly description.

          disk_attachment_properties: Disk Attachment specific properties

          name: A human-friendly name used as an identifier in APIs that support this option.

          scsi_controller: Deprecated: The SCSI controller to be assigned

          unit_number: Deprecated: The Unit Number to be assigned

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._post(
            f"/iaas/api/machines/{id}/disks",
            body=maybe_transform(
                {
                    "block_device_id": block_device_id,
                    "description": description,
                    "disk_attachment_properties": disk_attachment_properties,
                    "name": name,
                    "scsi_controller": scsi_controller,
                    "unit_number": unit_number,
                },
                disk_create_params.DiskCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"api_version": api_version}, disk_create_params.DiskCreateParams),
            ),
            cast_to=RequestTracker,
        )

    def retrieve(
        self,
        disk_id: str,
        *,
        id: str,
        api_version: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> BlockDevice:
        """
        Get disk with a given id for specific machine

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
        if not disk_id:
            raise ValueError(f"Expected a non-empty value for `disk_id` but received {disk_id!r}")
        return self._get(
            f"/iaas/api/machines/{id}/disks/{disk_id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"api_version": api_version}, disk_retrieve_params.DiskRetrieveParams),
            ),
            cast_to=BlockDevice,
        )

    def list(
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
    ) -> BlockDeviceResult:
        """
        Get all machine disks

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
            f"/iaas/api/machines/{id}/disks",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"api_version": api_version}, disk_list_params.DiskListParams),
            ),
            cast_to=BlockDeviceResult,
        )

    def delete(
        self,
        disk_id: str,
        *,
        id: str,
        api_version: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RequestTracker:
        """
        Remove a disk from a given machine.

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
        if not disk_id:
            raise ValueError(f"Expected a non-empty value for `disk_id` but received {disk_id!r}")
        return self._delete(
            f"/iaas/api/machines/{id}/disks/{disk_id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"api_version": api_version}, disk_delete_params.DiskDeleteParams),
            ),
            cast_to=RequestTracker,
        )


class AsyncDisksResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncDisksResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#accessing-raw-response-data-eg-headers
        """
        return AsyncDisksResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncDisksResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#with_streaming_response
        """
        return AsyncDisksResourceWithStreamingResponse(self)

    async def create(
        self,
        id: str,
        *,
        block_device_id: str,
        api_version: str | Omit = omit,
        description: str | Omit = omit,
        disk_attachment_properties: Dict[str, str] | Omit = omit,
        name: str | Omit = omit,
        scsi_controller: str | Omit = omit,
        unit_number: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RequestTracker:
        """
        Attach a disk to a machine.

        Args:
          block_device_id: The id of the existing block device

          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          description: A human-friendly description.

          disk_attachment_properties: Disk Attachment specific properties

          name: A human-friendly name used as an identifier in APIs that support this option.

          scsi_controller: Deprecated: The SCSI controller to be assigned

          unit_number: Deprecated: The Unit Number to be assigned

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._post(
            f"/iaas/api/machines/{id}/disks",
            body=await async_maybe_transform(
                {
                    "block_device_id": block_device_id,
                    "description": description,
                    "disk_attachment_properties": disk_attachment_properties,
                    "name": name,
                    "scsi_controller": scsi_controller,
                    "unit_number": unit_number,
                },
                disk_create_params.DiskCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform({"api_version": api_version}, disk_create_params.DiskCreateParams),
            ),
            cast_to=RequestTracker,
        )

    async def retrieve(
        self,
        disk_id: str,
        *,
        id: str,
        api_version: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> BlockDevice:
        """
        Get disk with a given id for specific machine

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
        if not disk_id:
            raise ValueError(f"Expected a non-empty value for `disk_id` but received {disk_id!r}")
        return await self._get(
            f"/iaas/api/machines/{id}/disks/{disk_id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"api_version": api_version}, disk_retrieve_params.DiskRetrieveParams
                ),
            ),
            cast_to=BlockDevice,
        )

    async def list(
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
    ) -> BlockDeviceResult:
        """
        Get all machine disks

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
            f"/iaas/api/machines/{id}/disks",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform({"api_version": api_version}, disk_list_params.DiskListParams),
            ),
            cast_to=BlockDeviceResult,
        )

    async def delete(
        self,
        disk_id: str,
        *,
        id: str,
        api_version: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RequestTracker:
        """
        Remove a disk from a given machine.

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
        if not disk_id:
            raise ValueError(f"Expected a non-empty value for `disk_id` but received {disk_id!r}")
        return await self._delete(
            f"/iaas/api/machines/{id}/disks/{disk_id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform({"api_version": api_version}, disk_delete_params.DiskDeleteParams),
            ),
            cast_to=RequestTracker,
        )


class DisksResourceWithRawResponse:
    def __init__(self, disks: DisksResource) -> None:
        self._disks = disks

        self.create = to_raw_response_wrapper(
            disks.create,
        )
        self.retrieve = to_raw_response_wrapper(
            disks.retrieve,
        )
        self.list = to_raw_response_wrapper(
            disks.list,
        )
        self.delete = to_raw_response_wrapper(
            disks.delete,
        )


class AsyncDisksResourceWithRawResponse:
    def __init__(self, disks: AsyncDisksResource) -> None:
        self._disks = disks

        self.create = async_to_raw_response_wrapper(
            disks.create,
        )
        self.retrieve = async_to_raw_response_wrapper(
            disks.retrieve,
        )
        self.list = async_to_raw_response_wrapper(
            disks.list,
        )
        self.delete = async_to_raw_response_wrapper(
            disks.delete,
        )


class DisksResourceWithStreamingResponse:
    def __init__(self, disks: DisksResource) -> None:
        self._disks = disks

        self.create = to_streamed_response_wrapper(
            disks.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            disks.retrieve,
        )
        self.list = to_streamed_response_wrapper(
            disks.list,
        )
        self.delete = to_streamed_response_wrapper(
            disks.delete,
        )


class AsyncDisksResourceWithStreamingResponse:
    def __init__(self, disks: AsyncDisksResource) -> None:
        self._disks = disks

        self.create = async_to_streamed_response_wrapper(
            disks.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            disks.retrieve,
        )
        self.list = async_to_streamed_response_wrapper(
            disks.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            disks.delete,
        )
