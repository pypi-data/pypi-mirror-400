# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Iterable

import httpx

from ...._types import Body, Omit, Query, Headers, NotGiven, SequenceNotStr, omit, not_given
from ...._utils import maybe_transform, async_maybe_transform
from ...._compat import cached_property
from ...._resource import SyncAPIResource, AsyncAPIResource
from ...._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ...._base_client import make_request_options
from ....types.iaas.api import (
    compute_gateway_delete_params,
    compute_gateway_retrieve_params,
    compute_gateway_compute_gateways_params,
    compute_gateway_retrieve_compute_gateways_params,
)
from ....types.iaas.api.compute_gateway import ComputeGateway
from ....types.iaas.api.projects.request_tracker import RequestTracker
from ....types.iaas.api.compute_nats.nat_rule_param import NatRuleParam
from ....types.iaas.api.compute_gateway_retrieve_compute_gateways_response import (
    ComputeGatewayRetrieveComputeGatewaysResponse,
)

__all__ = ["ComputeGatewaysResource", "AsyncComputeGatewaysResource"]


class ComputeGatewaysResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> ComputeGatewaysResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#accessing-raw-response-data-eg-headers
        """
        return ComputeGatewaysResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ComputeGatewaysResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#with_streaming_response
        """
        return ComputeGatewaysResourceWithStreamingResponse(self)

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
    ) -> ComputeGateway:
        """
        Get compute gateway with a given id

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
            f"/iaas/api/compute-gateways/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"api_version": api_version}, compute_gateway_retrieve_params.ComputeGatewayRetrieveParams
                ),
            ),
            cast_to=ComputeGateway,
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
        Delete compute gateway with a given id

        Args:
          api_version: Controls whether this is a force delete operation. If true, best effort is made
              for deleting this compute gateway. Use with caution as force deleting may cause
              inconsistencies between the cloud provider and VMware Aria Automation.

          force_delete: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._delete(
            f"/iaas/api/compute-gateways/{id}",
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
                    compute_gateway_delete_params.ComputeGatewayDeleteParams,
                ),
            ),
            cast_to=RequestTracker,
        )

    def compute_gateways(
        self,
        *,
        name: str,
        nat_rules: Iterable[NatRuleParam],
        networks: SequenceNotStr[str],
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
        Create a new compute gateway.

        Args:
          name: A human-friendly name used as an identifier in APIs that support this option.

          nat_rules: List of NAT Rules

          networks: List of networks

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
            "/iaas/api/compute-gateways",
            body=maybe_transform(
                {
                    "name": name,
                    "nat_rules": nat_rules,
                    "networks": networks,
                    "project_id": project_id,
                    "custom_properties": custom_properties,
                    "deployment_id": deployment_id,
                },
                compute_gateway_compute_gateways_params.ComputeGatewayComputeGatewaysParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"api_version": api_version},
                    compute_gateway_compute_gateways_params.ComputeGatewayComputeGatewaysParams,
                ),
            ),
            cast_to=RequestTracker,
        )

    def retrieve_compute_gateways(
        self,
        *,
        api_version: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ComputeGatewayRetrieveComputeGatewaysResponse:
        """
        Get all compute gateways

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/iaas/api/compute-gateways",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"api_version": api_version},
                    compute_gateway_retrieve_compute_gateways_params.ComputeGatewayRetrieveComputeGatewaysParams,
                ),
            ),
            cast_to=ComputeGatewayRetrieveComputeGatewaysResponse,
        )


class AsyncComputeGatewaysResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncComputeGatewaysResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#accessing-raw-response-data-eg-headers
        """
        return AsyncComputeGatewaysResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncComputeGatewaysResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#with_streaming_response
        """
        return AsyncComputeGatewaysResourceWithStreamingResponse(self)

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
    ) -> ComputeGateway:
        """
        Get compute gateway with a given id

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
            f"/iaas/api/compute-gateways/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"api_version": api_version}, compute_gateway_retrieve_params.ComputeGatewayRetrieveParams
                ),
            ),
            cast_to=ComputeGateway,
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
        Delete compute gateway with a given id

        Args:
          api_version: Controls whether this is a force delete operation. If true, best effort is made
              for deleting this compute gateway. Use with caution as force deleting may cause
              inconsistencies between the cloud provider and VMware Aria Automation.

          force_delete: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._delete(
            f"/iaas/api/compute-gateways/{id}",
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
                    compute_gateway_delete_params.ComputeGatewayDeleteParams,
                ),
            ),
            cast_to=RequestTracker,
        )

    async def compute_gateways(
        self,
        *,
        name: str,
        nat_rules: Iterable[NatRuleParam],
        networks: SequenceNotStr[str],
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
        Create a new compute gateway.

        Args:
          name: A human-friendly name used as an identifier in APIs that support this option.

          nat_rules: List of NAT Rules

          networks: List of networks

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
            "/iaas/api/compute-gateways",
            body=await async_maybe_transform(
                {
                    "name": name,
                    "nat_rules": nat_rules,
                    "networks": networks,
                    "project_id": project_id,
                    "custom_properties": custom_properties,
                    "deployment_id": deployment_id,
                },
                compute_gateway_compute_gateways_params.ComputeGatewayComputeGatewaysParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"api_version": api_version},
                    compute_gateway_compute_gateways_params.ComputeGatewayComputeGatewaysParams,
                ),
            ),
            cast_to=RequestTracker,
        )

    async def retrieve_compute_gateways(
        self,
        *,
        api_version: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ComputeGatewayRetrieveComputeGatewaysResponse:
        """
        Get all compute gateways

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/iaas/api/compute-gateways",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"api_version": api_version},
                    compute_gateway_retrieve_compute_gateways_params.ComputeGatewayRetrieveComputeGatewaysParams,
                ),
            ),
            cast_to=ComputeGatewayRetrieveComputeGatewaysResponse,
        )


class ComputeGatewaysResourceWithRawResponse:
    def __init__(self, compute_gateways: ComputeGatewaysResource) -> None:
        self._compute_gateways = compute_gateways

        self.retrieve = to_raw_response_wrapper(
            compute_gateways.retrieve,
        )
        self.delete = to_raw_response_wrapper(
            compute_gateways.delete,
        )
        self.compute_gateways = to_raw_response_wrapper(
            compute_gateways.compute_gateways,
        )
        self.retrieve_compute_gateways = to_raw_response_wrapper(
            compute_gateways.retrieve_compute_gateways,
        )


class AsyncComputeGatewaysResourceWithRawResponse:
    def __init__(self, compute_gateways: AsyncComputeGatewaysResource) -> None:
        self._compute_gateways = compute_gateways

        self.retrieve = async_to_raw_response_wrapper(
            compute_gateways.retrieve,
        )
        self.delete = async_to_raw_response_wrapper(
            compute_gateways.delete,
        )
        self.compute_gateways = async_to_raw_response_wrapper(
            compute_gateways.compute_gateways,
        )
        self.retrieve_compute_gateways = async_to_raw_response_wrapper(
            compute_gateways.retrieve_compute_gateways,
        )


class ComputeGatewaysResourceWithStreamingResponse:
    def __init__(self, compute_gateways: ComputeGatewaysResource) -> None:
        self._compute_gateways = compute_gateways

        self.retrieve = to_streamed_response_wrapper(
            compute_gateways.retrieve,
        )
        self.delete = to_streamed_response_wrapper(
            compute_gateways.delete,
        )
        self.compute_gateways = to_streamed_response_wrapper(
            compute_gateways.compute_gateways,
        )
        self.retrieve_compute_gateways = to_streamed_response_wrapper(
            compute_gateways.retrieve_compute_gateways,
        )


class AsyncComputeGatewaysResourceWithStreamingResponse:
    def __init__(self, compute_gateways: AsyncComputeGatewaysResource) -> None:
        self._compute_gateways = compute_gateways

        self.retrieve = async_to_streamed_response_wrapper(
            compute_gateways.retrieve,
        )
        self.delete = async_to_streamed_response_wrapper(
            compute_gateways.delete,
        )
        self.compute_gateways = async_to_streamed_response_wrapper(
            compute_gateways.compute_gateways,
        )
        self.retrieve_compute_gateways = async_to_streamed_response_wrapper(
            compute_gateways.retrieve_compute_gateways,
        )
