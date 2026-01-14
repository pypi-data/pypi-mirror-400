# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable

import httpx

from ...._types import Body, Omit, Query, Headers, NotGiven, omit, not_given
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
from ....types.iaas.api import naming_list_params, naming_create_params, naming_delete_params, naming_retrieve_params
from ....types.iaas.api.custom_naming import CustomNaming
from ....types.iaas.api.naming_list_response import NamingListResponse

__all__ = ["NamingResource", "AsyncNamingResource"]


class NamingResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> NamingResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#accessing-raw-response-data-eg-headers
        """
        return NamingResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> NamingResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#with_streaming_response
        """
        return NamingResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        api_version: str,
        id: str | Omit = omit,
        description: str | Omit = omit,
        name: str | Omit = omit,
        projects: Iterable[naming_create_params.Project] | Omit = omit,
        templates: Iterable[naming_create_params.Template] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> CustomNaming:
        """
        Create Custom Name

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/iaas/api/naming",
            body=maybe_transform(
                {
                    "id": id,
                    "description": description,
                    "name": name,
                    "projects": projects,
                    "templates": templates,
                },
                naming_create_params.NamingCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"api_version": api_version}, naming_create_params.NamingCreateParams),
            ),
            cast_to=CustomNaming,
        )

    def retrieve(
        self,
        id: str,
        *,
        api_version: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> CustomNaming:
        """
        Get Custom Names For Project Id

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
            f"/iaas/api/naming/projectId/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"api_version": api_version}, naming_retrieve_params.NamingRetrieveParams),
            ),
            cast_to=CustomNaming,
        )

    def list(
        self,
        *,
        api_version: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> NamingListResponse:
        """
        Get All Custom Names

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/iaas/api/naming",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"api_version": api_version}, naming_list_params.NamingListParams),
            ),
            cast_to=NamingListResponse,
        )

    def delete(
        self,
        id: str,
        *,
        api_version: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> CustomNaming:
        """
        Delete custom name with a given id

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
        return self._delete(
            f"/iaas/api/naming/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"api_version": api_version}, naming_delete_params.NamingDeleteParams),
            ),
            cast_to=CustomNaming,
        )


class AsyncNamingResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncNamingResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#accessing-raw-response-data-eg-headers
        """
        return AsyncNamingResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncNamingResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#with_streaming_response
        """
        return AsyncNamingResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        api_version: str,
        id: str | Omit = omit,
        description: str | Omit = omit,
        name: str | Omit = omit,
        projects: Iterable[naming_create_params.Project] | Omit = omit,
        templates: Iterable[naming_create_params.Template] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> CustomNaming:
        """
        Create Custom Name

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/iaas/api/naming",
            body=await async_maybe_transform(
                {
                    "id": id,
                    "description": description,
                    "name": name,
                    "projects": projects,
                    "templates": templates,
                },
                naming_create_params.NamingCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"api_version": api_version}, naming_create_params.NamingCreateParams
                ),
            ),
            cast_to=CustomNaming,
        )

    async def retrieve(
        self,
        id: str,
        *,
        api_version: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> CustomNaming:
        """
        Get Custom Names For Project Id

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
            f"/iaas/api/naming/projectId/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"api_version": api_version}, naming_retrieve_params.NamingRetrieveParams
                ),
            ),
            cast_to=CustomNaming,
        )

    async def list(
        self,
        *,
        api_version: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> NamingListResponse:
        """
        Get All Custom Names

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/iaas/api/naming",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform({"api_version": api_version}, naming_list_params.NamingListParams),
            ),
            cast_to=NamingListResponse,
        )

    async def delete(
        self,
        id: str,
        *,
        api_version: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> CustomNaming:
        """
        Delete custom name with a given id

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
        return await self._delete(
            f"/iaas/api/naming/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"api_version": api_version}, naming_delete_params.NamingDeleteParams
                ),
            ),
            cast_to=CustomNaming,
        )


class NamingResourceWithRawResponse:
    def __init__(self, naming: NamingResource) -> None:
        self._naming = naming

        self.create = to_raw_response_wrapper(
            naming.create,
        )
        self.retrieve = to_raw_response_wrapper(
            naming.retrieve,
        )
        self.list = to_raw_response_wrapper(
            naming.list,
        )
        self.delete = to_raw_response_wrapper(
            naming.delete,
        )


class AsyncNamingResourceWithRawResponse:
    def __init__(self, naming: AsyncNamingResource) -> None:
        self._naming = naming

        self.create = async_to_raw_response_wrapper(
            naming.create,
        )
        self.retrieve = async_to_raw_response_wrapper(
            naming.retrieve,
        )
        self.list = async_to_raw_response_wrapper(
            naming.list,
        )
        self.delete = async_to_raw_response_wrapper(
            naming.delete,
        )


class NamingResourceWithStreamingResponse:
    def __init__(self, naming: NamingResource) -> None:
        self._naming = naming

        self.create = to_streamed_response_wrapper(
            naming.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            naming.retrieve,
        )
        self.list = to_streamed_response_wrapper(
            naming.list,
        )
        self.delete = to_streamed_response_wrapper(
            naming.delete,
        )


class AsyncNamingResourceWithStreamingResponse:
    def __init__(self, naming: AsyncNamingResource) -> None:
        self._naming = naming

        self.create = async_to_streamed_response_wrapper(
            naming.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            naming.retrieve,
        )
        self.list = async_to_streamed_response_wrapper(
            naming.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            naming.delete,
        )
