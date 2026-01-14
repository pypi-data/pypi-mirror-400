# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict

import httpx

from ...._types import Body, Omit, Query, Headers, NoneType, NotGiven, omit, not_given
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
    flavor_profile_delete_params,
    flavor_profile_update_params,
    flavor_profile_retrieve_params,
    flavor_profile_flavor_profiles_params,
    flavor_profile_retrieve_flavor_profiles_params,
)
from ....types.iaas.api.flavor_profile import FlavorProfile
from ....types.iaas.api.flavor_profile_retrieve_flavor_profiles_response import (
    FlavorProfileRetrieveFlavorProfilesResponse,
)

__all__ = ["FlavorProfilesResource", "AsyncFlavorProfilesResource"]


class FlavorProfilesResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> FlavorProfilesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#accessing-raw-response-data-eg-headers
        """
        return FlavorProfilesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> FlavorProfilesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#with_streaming_response
        """
        return FlavorProfilesResourceWithStreamingResponse(self)

    def retrieve(
        self,
        id: str,
        *,
        api_version: str | Omit = omit,
        include_cores: bool | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> FlavorProfile:
        """
        Get flavor profile with a given id

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          include_cores: If set to true will include cores in response.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._get(
            f"/iaas/api/flavor-profiles/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "api_version": api_version,
                        "include_cores": include_cores,
                    },
                    flavor_profile_retrieve_params.FlavorProfileRetrieveParams,
                ),
            ),
            cast_to=FlavorProfile,
        )

    def update(
        self,
        id: str,
        *,
        flavor_mapping: Dict[str, flavor_profile_update_params.FlavorMapping],
        name: str,
        api_version: str | Omit = omit,
        include_cores: bool | Omit = omit,
        description: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> FlavorProfile:
        """
        Update flavor profile

        Args:
          flavor_mapping: Map between global fabric flavor keys <String> and fabric flavor descriptions
              <FabricFlavorDescription>

          name: A human-friendly name used as an identifier in APIs that support this option.

          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          include_cores: If set to true will include cores in response.

          description: A human-friendly description.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._patch(
            f"/iaas/api/flavor-profiles/{id}",
            body=maybe_transform(
                {
                    "flavor_mapping": flavor_mapping,
                    "name": name,
                    "description": description,
                },
                flavor_profile_update_params.FlavorProfileUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "api_version": api_version,
                        "include_cores": include_cores,
                    },
                    flavor_profile_update_params.FlavorProfileUpdateParams,
                ),
            ),
            cast_to=FlavorProfile,
        )

    def delete(
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
    ) -> None:
        """
        Delete flavor profile with a given id

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
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._delete(
            f"/iaas/api/flavor-profiles/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"api_version": api_version}, flavor_profile_delete_params.FlavorProfileDeleteParams
                ),
            ),
            cast_to=NoneType,
        )

    def flavor_profiles(
        self,
        *,
        flavor_mapping: Dict[str, flavor_profile_flavor_profiles_params.FlavorMapping],
        name: str,
        region_id: str,
        api_version: str | Omit = omit,
        include_cores: bool | Omit = omit,
        description: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> FlavorProfile:
        """
        Create flavor profile

        Args:
          flavor_mapping: Map between global fabric flavor keys <String> and fabric flavor descriptions
              <FabricFlavorDescription>

          name: A human-friendly name used as an identifier in APIs that support this option.

          region_id: The id of the region for which this profile is created

          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          include_cores: If set to true will include cores in response.

          description: A human-friendly description.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/iaas/api/flavor-profiles",
            body=maybe_transform(
                {
                    "flavor_mapping": flavor_mapping,
                    "name": name,
                    "region_id": region_id,
                    "description": description,
                },
                flavor_profile_flavor_profiles_params.FlavorProfileFlavorProfilesParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "api_version": api_version,
                        "include_cores": include_cores,
                    },
                    flavor_profile_flavor_profiles_params.FlavorProfileFlavorProfilesParams,
                ),
            ),
            cast_to=FlavorProfile,
        )

    def retrieve_flavor_profiles(
        self,
        *,
        api_version: str | Omit = omit,
        include_cores: bool | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> FlavorProfileRetrieveFlavorProfilesResponse:
        """
        Get all flavor profile

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          include_cores: If set to true will include cores in response.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/iaas/api/flavor-profiles",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "api_version": api_version,
                        "include_cores": include_cores,
                    },
                    flavor_profile_retrieve_flavor_profiles_params.FlavorProfileRetrieveFlavorProfilesParams,
                ),
            ),
            cast_to=FlavorProfileRetrieveFlavorProfilesResponse,
        )


class AsyncFlavorProfilesResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncFlavorProfilesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#accessing-raw-response-data-eg-headers
        """
        return AsyncFlavorProfilesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncFlavorProfilesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#with_streaming_response
        """
        return AsyncFlavorProfilesResourceWithStreamingResponse(self)

    async def retrieve(
        self,
        id: str,
        *,
        api_version: str | Omit = omit,
        include_cores: bool | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> FlavorProfile:
        """
        Get flavor profile with a given id

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          include_cores: If set to true will include cores in response.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._get(
            f"/iaas/api/flavor-profiles/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "api_version": api_version,
                        "include_cores": include_cores,
                    },
                    flavor_profile_retrieve_params.FlavorProfileRetrieveParams,
                ),
            ),
            cast_to=FlavorProfile,
        )

    async def update(
        self,
        id: str,
        *,
        flavor_mapping: Dict[str, flavor_profile_update_params.FlavorMapping],
        name: str,
        api_version: str | Omit = omit,
        include_cores: bool | Omit = omit,
        description: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> FlavorProfile:
        """
        Update flavor profile

        Args:
          flavor_mapping: Map between global fabric flavor keys <String> and fabric flavor descriptions
              <FabricFlavorDescription>

          name: A human-friendly name used as an identifier in APIs that support this option.

          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          include_cores: If set to true will include cores in response.

          description: A human-friendly description.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._patch(
            f"/iaas/api/flavor-profiles/{id}",
            body=await async_maybe_transform(
                {
                    "flavor_mapping": flavor_mapping,
                    "name": name,
                    "description": description,
                },
                flavor_profile_update_params.FlavorProfileUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "api_version": api_version,
                        "include_cores": include_cores,
                    },
                    flavor_profile_update_params.FlavorProfileUpdateParams,
                ),
            ),
            cast_to=FlavorProfile,
        )

    async def delete(
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
    ) -> None:
        """
        Delete flavor profile with a given id

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
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._delete(
            f"/iaas/api/flavor-profiles/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"api_version": api_version}, flavor_profile_delete_params.FlavorProfileDeleteParams
                ),
            ),
            cast_to=NoneType,
        )

    async def flavor_profiles(
        self,
        *,
        flavor_mapping: Dict[str, flavor_profile_flavor_profiles_params.FlavorMapping],
        name: str,
        region_id: str,
        api_version: str | Omit = omit,
        include_cores: bool | Omit = omit,
        description: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> FlavorProfile:
        """
        Create flavor profile

        Args:
          flavor_mapping: Map between global fabric flavor keys <String> and fabric flavor descriptions
              <FabricFlavorDescription>

          name: A human-friendly name used as an identifier in APIs that support this option.

          region_id: The id of the region for which this profile is created

          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          include_cores: If set to true will include cores in response.

          description: A human-friendly description.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/iaas/api/flavor-profiles",
            body=await async_maybe_transform(
                {
                    "flavor_mapping": flavor_mapping,
                    "name": name,
                    "region_id": region_id,
                    "description": description,
                },
                flavor_profile_flavor_profiles_params.FlavorProfileFlavorProfilesParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "api_version": api_version,
                        "include_cores": include_cores,
                    },
                    flavor_profile_flavor_profiles_params.FlavorProfileFlavorProfilesParams,
                ),
            ),
            cast_to=FlavorProfile,
        )

    async def retrieve_flavor_profiles(
        self,
        *,
        api_version: str | Omit = omit,
        include_cores: bool | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> FlavorProfileRetrieveFlavorProfilesResponse:
        """
        Get all flavor profile

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          include_cores: If set to true will include cores in response.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/iaas/api/flavor-profiles",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "api_version": api_version,
                        "include_cores": include_cores,
                    },
                    flavor_profile_retrieve_flavor_profiles_params.FlavorProfileRetrieveFlavorProfilesParams,
                ),
            ),
            cast_to=FlavorProfileRetrieveFlavorProfilesResponse,
        )


class FlavorProfilesResourceWithRawResponse:
    def __init__(self, flavor_profiles: FlavorProfilesResource) -> None:
        self._flavor_profiles = flavor_profiles

        self.retrieve = to_raw_response_wrapper(
            flavor_profiles.retrieve,
        )
        self.update = to_raw_response_wrapper(
            flavor_profiles.update,
        )
        self.delete = to_raw_response_wrapper(
            flavor_profiles.delete,
        )
        self.flavor_profiles = to_raw_response_wrapper(
            flavor_profiles.flavor_profiles,
        )
        self.retrieve_flavor_profiles = to_raw_response_wrapper(
            flavor_profiles.retrieve_flavor_profiles,
        )


class AsyncFlavorProfilesResourceWithRawResponse:
    def __init__(self, flavor_profiles: AsyncFlavorProfilesResource) -> None:
        self._flavor_profiles = flavor_profiles

        self.retrieve = async_to_raw_response_wrapper(
            flavor_profiles.retrieve,
        )
        self.update = async_to_raw_response_wrapper(
            flavor_profiles.update,
        )
        self.delete = async_to_raw_response_wrapper(
            flavor_profiles.delete,
        )
        self.flavor_profiles = async_to_raw_response_wrapper(
            flavor_profiles.flavor_profiles,
        )
        self.retrieve_flavor_profiles = async_to_raw_response_wrapper(
            flavor_profiles.retrieve_flavor_profiles,
        )


class FlavorProfilesResourceWithStreamingResponse:
    def __init__(self, flavor_profiles: FlavorProfilesResource) -> None:
        self._flavor_profiles = flavor_profiles

        self.retrieve = to_streamed_response_wrapper(
            flavor_profiles.retrieve,
        )
        self.update = to_streamed_response_wrapper(
            flavor_profiles.update,
        )
        self.delete = to_streamed_response_wrapper(
            flavor_profiles.delete,
        )
        self.flavor_profiles = to_streamed_response_wrapper(
            flavor_profiles.flavor_profiles,
        )
        self.retrieve_flavor_profiles = to_streamed_response_wrapper(
            flavor_profiles.retrieve_flavor_profiles,
        )


class AsyncFlavorProfilesResourceWithStreamingResponse:
    def __init__(self, flavor_profiles: AsyncFlavorProfilesResource) -> None:
        self._flavor_profiles = flavor_profiles

        self.retrieve = async_to_streamed_response_wrapper(
            flavor_profiles.retrieve,
        )
        self.update = async_to_streamed_response_wrapper(
            flavor_profiles.update,
        )
        self.delete = async_to_streamed_response_wrapper(
            flavor_profiles.delete,
        )
        self.flavor_profiles = async_to_streamed_response_wrapper(
            flavor_profiles.flavor_profiles,
        )
        self.retrieve_flavor_profiles = async_to_streamed_response_wrapper(
            flavor_profiles.retrieve_flavor_profiles,
        )
