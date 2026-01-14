# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable

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
from .....types.iaas.api.project import Project
from .....types.iaas.api.projects import (
    resource_metadata_update_resource_metadata_params,
    resource_metadata_retrieve_resource_metadata_params,
)
from .....types.iaas.api.tag_param import TagParam
from .....types.iaas.api.projects.resource_metadata_retrieve_resource_metadata_response import (
    ResourceMetadataRetrieveResourceMetadataResponse,
)

__all__ = ["ResourceMetadataResource", "AsyncResourceMetadataResource"]


class ResourceMetadataResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> ResourceMetadataResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#accessing-raw-response-data-eg-headers
        """
        return ResourceMetadataResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ResourceMetadataResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#with_streaming_response
        """
        return ResourceMetadataResourceWithStreamingResponse(self)

    def retrieve_resource_metadata(
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
    ) -> ResourceMetadataRetrieveResourceMetadataResponse:
        """
        Get project resource metadata by a given project id

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
            f"/iaas/api/projects/{id}/resource-metadata",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"api_version": api_version},
                    resource_metadata_retrieve_resource_metadata_params.ResourceMetadataRetrieveResourceMetadataParams,
                ),
            ),
            cast_to=ResourceMetadataRetrieveResourceMetadataResponse,
        )

    def update_resource_metadata(
        self,
        id: str,
        *,
        api_version: str | Omit = omit,
        tags: Iterable[TagParam] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Project:
        """
        Update project resource metadata by a given project id

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          tags: A list of keys and optional values to be applied to compute resources
              provisioned in a project

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._patch(
            f"/iaas/api/projects/{id}/resource-metadata",
            body=maybe_transform(
                {"tags": tags},
                resource_metadata_update_resource_metadata_params.ResourceMetadataUpdateResourceMetadataParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"api_version": api_version},
                    resource_metadata_update_resource_metadata_params.ResourceMetadataUpdateResourceMetadataParams,
                ),
            ),
            cast_to=Project,
        )


class AsyncResourceMetadataResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncResourceMetadataResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#accessing-raw-response-data-eg-headers
        """
        return AsyncResourceMetadataResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncResourceMetadataResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#with_streaming_response
        """
        return AsyncResourceMetadataResourceWithStreamingResponse(self)

    async def retrieve_resource_metadata(
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
    ) -> ResourceMetadataRetrieveResourceMetadataResponse:
        """
        Get project resource metadata by a given project id

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
            f"/iaas/api/projects/{id}/resource-metadata",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"api_version": api_version},
                    resource_metadata_retrieve_resource_metadata_params.ResourceMetadataRetrieveResourceMetadataParams,
                ),
            ),
            cast_to=ResourceMetadataRetrieveResourceMetadataResponse,
        )

    async def update_resource_metadata(
        self,
        id: str,
        *,
        api_version: str | Omit = omit,
        tags: Iterable[TagParam] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Project:
        """
        Update project resource metadata by a given project id

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          tags: A list of keys and optional values to be applied to compute resources
              provisioned in a project

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._patch(
            f"/iaas/api/projects/{id}/resource-metadata",
            body=await async_maybe_transform(
                {"tags": tags},
                resource_metadata_update_resource_metadata_params.ResourceMetadataUpdateResourceMetadataParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"api_version": api_version},
                    resource_metadata_update_resource_metadata_params.ResourceMetadataUpdateResourceMetadataParams,
                ),
            ),
            cast_to=Project,
        )


class ResourceMetadataResourceWithRawResponse:
    def __init__(self, resource_metadata: ResourceMetadataResource) -> None:
        self._resource_metadata = resource_metadata

        self.retrieve_resource_metadata = to_raw_response_wrapper(
            resource_metadata.retrieve_resource_metadata,
        )
        self.update_resource_metadata = to_raw_response_wrapper(
            resource_metadata.update_resource_metadata,
        )


class AsyncResourceMetadataResourceWithRawResponse:
    def __init__(self, resource_metadata: AsyncResourceMetadataResource) -> None:
        self._resource_metadata = resource_metadata

        self.retrieve_resource_metadata = async_to_raw_response_wrapper(
            resource_metadata.retrieve_resource_metadata,
        )
        self.update_resource_metadata = async_to_raw_response_wrapper(
            resource_metadata.update_resource_metadata,
        )


class ResourceMetadataResourceWithStreamingResponse:
    def __init__(self, resource_metadata: ResourceMetadataResource) -> None:
        self._resource_metadata = resource_metadata

        self.retrieve_resource_metadata = to_streamed_response_wrapper(
            resource_metadata.retrieve_resource_metadata,
        )
        self.update_resource_metadata = to_streamed_response_wrapper(
            resource_metadata.update_resource_metadata,
        )


class AsyncResourceMetadataResourceWithStreamingResponse:
    def __init__(self, resource_metadata: AsyncResourceMetadataResource) -> None:
        self._resource_metadata = resource_metadata

        self.retrieve_resource_metadata = async_to_streamed_response_wrapper(
            resource_metadata.retrieve_resource_metadata,
        )
        self.update_resource_metadata = async_to_streamed_response_wrapper(
            resource_metadata.update_resource_metadata,
        )
