# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Iterable

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
from .....types.iaas.api.tag_param import TagParam
from .....types.iaas.api.block_devices import (
    operation_revert_params,
    operation_promote_params,
    operation_snapshots_params,
)
from .....types.iaas.api.projects.request_tracker import RequestTracker

__all__ = ["OperationsResource", "AsyncOperationsResource"]


class OperationsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> OperationsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#accessing-raw-response-data-eg-headers
        """
        return OperationsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> OperationsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#with_streaming_response
        """
        return OperationsResourceWithStreamingResponse(self)

    def promote(
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
    ) -> RequestTracker:
        """Second day promote operation on disk.

        Applicable for vSphere Block Devices only

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
        return self._post(
            f"/iaas/api/block-devices/{id}/operations/promote",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"api_version": api_version}, operation_promote_params.OperationPromoteParams),
            ),
            cast_to=RequestTracker,
        )

    def revert(
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
        Second day revert snapshot operation for Block device

        Args:
          id: Snapshot id to revert.

          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not disk_id:
            raise ValueError(f"Expected a non-empty value for `disk_id` but received {disk_id!r}")
        return self._post(
            f"/iaas/api/block-devices/{disk_id}/operations/revert",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "id": id,
                        "api_version": api_version,
                    },
                    operation_revert_params.OperationRevertParams,
                ),
            ),
            cast_to=RequestTracker,
        )

    def snapshots(
        self,
        id: str,
        *,
        api_version: str | Omit = omit,
        description: str | Omit = omit,
        name: str | Omit = omit,
        snapshot_properties: Dict[str, str] | Omit = omit,
        tags: Iterable[TagParam] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RequestTracker:
        """
        Second day create snapshot operation for Block device

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          description: A human-friendly description.

          name: A human-friendly name used as an identifier in APIs that support this option.

          snapshot_properties: Cloud specific snapshot properties supplied in as name value pairs

          tags: A set of tag keys and optional values that have to be set on the snapshot in the
              cloud. Currently supported for Azure Snapshots

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._post(
            f"/iaas/api/block-devices/{id}/operations/snapshots",
            body=maybe_transform(
                {
                    "description": description,
                    "name": name,
                    "snapshot_properties": snapshot_properties,
                    "tags": tags,
                },
                operation_snapshots_params.OperationSnapshotsParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"api_version": api_version}, operation_snapshots_params.OperationSnapshotsParams
                ),
            ),
            cast_to=RequestTracker,
        )


class AsyncOperationsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncOperationsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#accessing-raw-response-data-eg-headers
        """
        return AsyncOperationsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncOperationsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#with_streaming_response
        """
        return AsyncOperationsResourceWithStreamingResponse(self)

    async def promote(
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
    ) -> RequestTracker:
        """Second day promote operation on disk.

        Applicable for vSphere Block Devices only

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
        return await self._post(
            f"/iaas/api/block-devices/{id}/operations/promote",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"api_version": api_version}, operation_promote_params.OperationPromoteParams
                ),
            ),
            cast_to=RequestTracker,
        )

    async def revert(
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
        Second day revert snapshot operation for Block device

        Args:
          id: Snapshot id to revert.

          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not disk_id:
            raise ValueError(f"Expected a non-empty value for `disk_id` but received {disk_id!r}")
        return await self._post(
            f"/iaas/api/block-devices/{disk_id}/operations/revert",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "id": id,
                        "api_version": api_version,
                    },
                    operation_revert_params.OperationRevertParams,
                ),
            ),
            cast_to=RequestTracker,
        )

    async def snapshots(
        self,
        id: str,
        *,
        api_version: str | Omit = omit,
        description: str | Omit = omit,
        name: str | Omit = omit,
        snapshot_properties: Dict[str, str] | Omit = omit,
        tags: Iterable[TagParam] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RequestTracker:
        """
        Second day create snapshot operation for Block device

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          description: A human-friendly description.

          name: A human-friendly name used as an identifier in APIs that support this option.

          snapshot_properties: Cloud specific snapshot properties supplied in as name value pairs

          tags: A set of tag keys and optional values that have to be set on the snapshot in the
              cloud. Currently supported for Azure Snapshots

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._post(
            f"/iaas/api/block-devices/{id}/operations/snapshots",
            body=await async_maybe_transform(
                {
                    "description": description,
                    "name": name,
                    "snapshot_properties": snapshot_properties,
                    "tags": tags,
                },
                operation_snapshots_params.OperationSnapshotsParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"api_version": api_version}, operation_snapshots_params.OperationSnapshotsParams
                ),
            ),
            cast_to=RequestTracker,
        )


class OperationsResourceWithRawResponse:
    def __init__(self, operations: OperationsResource) -> None:
        self._operations = operations

        self.promote = to_raw_response_wrapper(
            operations.promote,
        )
        self.revert = to_raw_response_wrapper(
            operations.revert,
        )
        self.snapshots = to_raw_response_wrapper(
            operations.snapshots,
        )


class AsyncOperationsResourceWithRawResponse:
    def __init__(self, operations: AsyncOperationsResource) -> None:
        self._operations = operations

        self.promote = async_to_raw_response_wrapper(
            operations.promote,
        )
        self.revert = async_to_raw_response_wrapper(
            operations.revert,
        )
        self.snapshots = async_to_raw_response_wrapper(
            operations.snapshots,
        )


class OperationsResourceWithStreamingResponse:
    def __init__(self, operations: OperationsResource) -> None:
        self._operations = operations

        self.promote = to_streamed_response_wrapper(
            operations.promote,
        )
        self.revert = to_streamed_response_wrapper(
            operations.revert,
        )
        self.snapshots = to_streamed_response_wrapper(
            operations.snapshots,
        )


class AsyncOperationsResourceWithStreamingResponse:
    def __init__(self, operations: AsyncOperationsResource) -> None:
        self._operations = operations

        self.promote = async_to_streamed_response_wrapper(
            operations.promote,
        )
        self.revert = async_to_streamed_response_wrapper(
            operations.revert,
        )
        self.snapshots = async_to_streamed_response_wrapper(
            operations.snapshots,
        )
