# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Iterable

import httpx

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
    compute_nat_delete_params,
    compute_nat_retrieve_params,
    compute_nat_compute_nats_params,
    compute_nat_retrieve_compute_nats_params,
)
from .....types.iaas.api.compute_nat import ComputeNat
from .....types.iaas.api.projects.request_tracker import RequestTracker
from .....types.iaas.api.compute_nats.nat_rule_param import NatRuleParam
from .....types.iaas.api.compute_nat_retrieve_compute_nats_response import ComputeNatRetrieveComputeNatsResponse

__all__ = ["ComputeNatsResource", "AsyncComputeNatsResource"]


class ComputeNatsResource(SyncAPIResource):
    @cached_property
    def operations(self) -> OperationsResource:
        return OperationsResource(self._client)

    @cached_property
    def with_raw_response(self) -> ComputeNatsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#accessing-raw-response-data-eg-headers
        """
        return ComputeNatsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ComputeNatsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#with_streaming_response
        """
        return ComputeNatsResourceWithStreamingResponse(self)

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
    ) -> ComputeNat:
        """
        Get Compute Nat with a given id

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
            f"/iaas/api/compute-nats/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"api_version": api_version}, compute_nat_retrieve_params.ComputeNatRetrieveParams
                ),
            ),
            cast_to=ComputeNat,
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
        Delete compute nat with a given id

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          force_delete: Controls whether this is a force delete operation. If true, best effort is made
              for deleting this nat. Use with caution as force deleting may cause
              inconsistencies between the cloud provider and VMware Aria Automation.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._delete(
            f"/iaas/api/compute-nats/{id}",
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
                    compute_nat_delete_params.ComputeNatDeleteParams,
                ),
            ),
            cast_to=RequestTracker,
        )

    def compute_nats(
        self,
        *,
        gateway: str,
        name: str,
        nat_rules: Iterable[NatRuleParam],
        project_id: str,
        api_version: str | Omit = omit,
        custom_properties: Dict[str, str] | Omit = omit,
        deployment_id: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RequestTracker:
        """
        Create a new Compute Nat.

        Args:
          gateway: Id of the Compute Gateway to which the Compute Nat resource will be attached

          name: A human-friendly name used as an identifier in APIs that support this option.

          nat_rules: List of NAT Rules

          project_id: The id of the project the current user belongs to.

          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          custom_properties: Additional custom properties that may be used to extend this resource.

          deployment_id: The id of the deployment that is associated with this resource

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/iaas/api/compute-nats",
            body=maybe_transform(
                {
                    "gateway": gateway,
                    "name": name,
                    "nat_rules": nat_rules,
                    "project_id": project_id,
                    "custom_properties": custom_properties,
                    "deployment_id": deployment_id,
                },
                compute_nat_compute_nats_params.ComputeNatComputeNatsParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"api_version": api_version}, compute_nat_compute_nats_params.ComputeNatComputeNatsParams
                ),
            ),
            cast_to=RequestTracker,
        )

    def retrieve_compute_nats(
        self,
        *,
        api_version: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ComputeNatRetrieveComputeNatsResponse:
        """
        Get all Compute Nats

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/iaas/api/compute-nats",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"api_version": api_version},
                    compute_nat_retrieve_compute_nats_params.ComputeNatRetrieveComputeNatsParams,
                ),
            ),
            cast_to=ComputeNatRetrieveComputeNatsResponse,
        )


class AsyncComputeNatsResource(AsyncAPIResource):
    @cached_property
    def operations(self) -> AsyncOperationsResource:
        return AsyncOperationsResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncComputeNatsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#accessing-raw-response-data-eg-headers
        """
        return AsyncComputeNatsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncComputeNatsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#with_streaming_response
        """
        return AsyncComputeNatsResourceWithStreamingResponse(self)

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
    ) -> ComputeNat:
        """
        Get Compute Nat with a given id

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
            f"/iaas/api/compute-nats/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"api_version": api_version}, compute_nat_retrieve_params.ComputeNatRetrieveParams
                ),
            ),
            cast_to=ComputeNat,
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
        Delete compute nat with a given id

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          force_delete: Controls whether this is a force delete operation. If true, best effort is made
              for deleting this nat. Use with caution as force deleting may cause
              inconsistencies between the cloud provider and VMware Aria Automation.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._delete(
            f"/iaas/api/compute-nats/{id}",
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
                    compute_nat_delete_params.ComputeNatDeleteParams,
                ),
            ),
            cast_to=RequestTracker,
        )

    async def compute_nats(
        self,
        *,
        gateway: str,
        name: str,
        nat_rules: Iterable[NatRuleParam],
        project_id: str,
        api_version: str | Omit = omit,
        custom_properties: Dict[str, str] | Omit = omit,
        deployment_id: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RequestTracker:
        """
        Create a new Compute Nat.

        Args:
          gateway: Id of the Compute Gateway to which the Compute Nat resource will be attached

          name: A human-friendly name used as an identifier in APIs that support this option.

          nat_rules: List of NAT Rules

          project_id: The id of the project the current user belongs to.

          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          custom_properties: Additional custom properties that may be used to extend this resource.

          deployment_id: The id of the deployment that is associated with this resource

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/iaas/api/compute-nats",
            body=await async_maybe_transform(
                {
                    "gateway": gateway,
                    "name": name,
                    "nat_rules": nat_rules,
                    "project_id": project_id,
                    "custom_properties": custom_properties,
                    "deployment_id": deployment_id,
                },
                compute_nat_compute_nats_params.ComputeNatComputeNatsParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"api_version": api_version}, compute_nat_compute_nats_params.ComputeNatComputeNatsParams
                ),
            ),
            cast_to=RequestTracker,
        )

    async def retrieve_compute_nats(
        self,
        *,
        api_version: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ComputeNatRetrieveComputeNatsResponse:
        """
        Get all Compute Nats

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/iaas/api/compute-nats",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"api_version": api_version},
                    compute_nat_retrieve_compute_nats_params.ComputeNatRetrieveComputeNatsParams,
                ),
            ),
            cast_to=ComputeNatRetrieveComputeNatsResponse,
        )


class ComputeNatsResourceWithRawResponse:
    def __init__(self, compute_nats: ComputeNatsResource) -> None:
        self._compute_nats = compute_nats

        self.retrieve = to_raw_response_wrapper(
            compute_nats.retrieve,
        )
        self.delete = to_raw_response_wrapper(
            compute_nats.delete,
        )
        self.compute_nats = to_raw_response_wrapper(
            compute_nats.compute_nats,
        )
        self.retrieve_compute_nats = to_raw_response_wrapper(
            compute_nats.retrieve_compute_nats,
        )

    @cached_property
    def operations(self) -> OperationsResourceWithRawResponse:
        return OperationsResourceWithRawResponse(self._compute_nats.operations)


class AsyncComputeNatsResourceWithRawResponse:
    def __init__(self, compute_nats: AsyncComputeNatsResource) -> None:
        self._compute_nats = compute_nats

        self.retrieve = async_to_raw_response_wrapper(
            compute_nats.retrieve,
        )
        self.delete = async_to_raw_response_wrapper(
            compute_nats.delete,
        )
        self.compute_nats = async_to_raw_response_wrapper(
            compute_nats.compute_nats,
        )
        self.retrieve_compute_nats = async_to_raw_response_wrapper(
            compute_nats.retrieve_compute_nats,
        )

    @cached_property
    def operations(self) -> AsyncOperationsResourceWithRawResponse:
        return AsyncOperationsResourceWithRawResponse(self._compute_nats.operations)


class ComputeNatsResourceWithStreamingResponse:
    def __init__(self, compute_nats: ComputeNatsResource) -> None:
        self._compute_nats = compute_nats

        self.retrieve = to_streamed_response_wrapper(
            compute_nats.retrieve,
        )
        self.delete = to_streamed_response_wrapper(
            compute_nats.delete,
        )
        self.compute_nats = to_streamed_response_wrapper(
            compute_nats.compute_nats,
        )
        self.retrieve_compute_nats = to_streamed_response_wrapper(
            compute_nats.retrieve_compute_nats,
        )

    @cached_property
    def operations(self) -> OperationsResourceWithStreamingResponse:
        return OperationsResourceWithStreamingResponse(self._compute_nats.operations)


class AsyncComputeNatsResourceWithStreamingResponse:
    def __init__(self, compute_nats: AsyncComputeNatsResource) -> None:
        self._compute_nats = compute_nats

        self.retrieve = async_to_streamed_response_wrapper(
            compute_nats.retrieve,
        )
        self.delete = async_to_streamed_response_wrapper(
            compute_nats.delete,
        )
        self.compute_nats = async_to_streamed_response_wrapper(
            compute_nats.compute_nats,
        )
        self.retrieve_compute_nats = async_to_streamed_response_wrapper(
            compute_nats.retrieve_compute_nats,
        )

    @cached_property
    def operations(self) -> AsyncOperationsResourceWithStreamingResponse:
        return AsyncOperationsResourceWithStreamingResponse(self._compute_nats.operations)
