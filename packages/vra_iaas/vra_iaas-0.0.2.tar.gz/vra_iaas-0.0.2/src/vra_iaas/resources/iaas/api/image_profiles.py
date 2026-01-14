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
    image_profile_delete_params,
    image_profile_update_params,
    image_profile_retrieve_params,
    image_profile_image_profiles_params,
    image_profile_retrieve_image_profiles_params,
)
from ....types.iaas.api.image_profile import ImageProfile
from ....types.iaas.api.image_profile_retrieve_image_profiles_response import ImageProfileRetrieveImageProfilesResponse

__all__ = ["ImageProfilesResource", "AsyncImageProfilesResource"]


class ImageProfilesResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> ImageProfilesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#accessing-raw-response-data-eg-headers
        """
        return ImageProfilesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ImageProfilesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#with_streaming_response
        """
        return ImageProfilesResourceWithStreamingResponse(self)

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
    ) -> ImageProfile:
        """
        Get image profile with a given id

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
            f"/iaas/api/image-profiles/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"api_version": api_version}, image_profile_retrieve_params.ImageProfileRetrieveParams
                ),
            ),
            cast_to=ImageProfile,
        )

    def update(
        self,
        id: str,
        *,
        image_mapping: Dict[str, image_profile_update_params.ImageMapping],
        name: str,
        api_version: str | Omit = omit,
        description: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ImageProfile:
        """Update image profile.

        All existing image mapping definitions for the specified
        region will be replaced with the payload provided and if you want to keep the
        existing definitions, they should be added to the payload.

        Args:
          image_mapping: Image mapping defined for the corresponding region.

          name: A human-friendly name used as an identifier in APIs that support this option.

          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          description: A human-friendly description.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._patch(
            f"/iaas/api/image-profiles/{id}",
            body=maybe_transform(
                {
                    "image_mapping": image_mapping,
                    "name": name,
                    "description": description,
                },
                image_profile_update_params.ImageProfileUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"api_version": api_version}, image_profile_update_params.ImageProfileUpdateParams
                ),
            ),
            cast_to=ImageProfile,
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
        Delete image profile with a given id

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
            f"/iaas/api/image-profiles/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"api_version": api_version}, image_profile_delete_params.ImageProfileDeleteParams
                ),
            ),
            cast_to=NoneType,
        )

    def image_profiles(
        self,
        *,
        image_mapping: Dict[str, image_profile_image_profiles_params.ImageMapping],
        name: str,
        region_id: str,
        api_version: str | Omit = omit,
        description: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ImageProfile:
        """Create image profile.

        This image profile is created for the specific region.
        Image mapping definitions are created together with the profile. All existing
        image mapping definitions for the specified region will be replaced with the
        payload provided and if you want to keep the existing definitions, they should
        be added to the payload.

        Args:
          image_mapping: Image mapping defined for the corresponding region.

          name: A human-friendly name used as an identifier in APIs that support this option.

          region_id: The id of the region for which this profile is created

          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          description: A human-friendly description.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/iaas/api/image-profiles",
            body=maybe_transform(
                {
                    "image_mapping": image_mapping,
                    "name": name,
                    "region_id": region_id,
                    "description": description,
                },
                image_profile_image_profiles_params.ImageProfileImageProfilesParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"api_version": api_version}, image_profile_image_profiles_params.ImageProfileImageProfilesParams
                ),
            ),
            cast_to=ImageProfile,
        )

    def retrieve_image_profiles(
        self,
        *,
        api_version: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ImageProfileRetrieveImageProfilesResponse:
        """
        Get all image profiles

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/iaas/api/image-profiles",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"api_version": api_version},
                    image_profile_retrieve_image_profiles_params.ImageProfileRetrieveImageProfilesParams,
                ),
            ),
            cast_to=ImageProfileRetrieveImageProfilesResponse,
        )


class AsyncImageProfilesResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncImageProfilesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#accessing-raw-response-data-eg-headers
        """
        return AsyncImageProfilesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncImageProfilesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#with_streaming_response
        """
        return AsyncImageProfilesResourceWithStreamingResponse(self)

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
    ) -> ImageProfile:
        """
        Get image profile with a given id

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
            f"/iaas/api/image-profiles/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"api_version": api_version}, image_profile_retrieve_params.ImageProfileRetrieveParams
                ),
            ),
            cast_to=ImageProfile,
        )

    async def update(
        self,
        id: str,
        *,
        image_mapping: Dict[str, image_profile_update_params.ImageMapping],
        name: str,
        api_version: str | Omit = omit,
        description: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ImageProfile:
        """Update image profile.

        All existing image mapping definitions for the specified
        region will be replaced with the payload provided and if you want to keep the
        existing definitions, they should be added to the payload.

        Args:
          image_mapping: Image mapping defined for the corresponding region.

          name: A human-friendly name used as an identifier in APIs that support this option.

          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          description: A human-friendly description.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._patch(
            f"/iaas/api/image-profiles/{id}",
            body=await async_maybe_transform(
                {
                    "image_mapping": image_mapping,
                    "name": name,
                    "description": description,
                },
                image_profile_update_params.ImageProfileUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"api_version": api_version}, image_profile_update_params.ImageProfileUpdateParams
                ),
            ),
            cast_to=ImageProfile,
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
        Delete image profile with a given id

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
            f"/iaas/api/image-profiles/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"api_version": api_version}, image_profile_delete_params.ImageProfileDeleteParams
                ),
            ),
            cast_to=NoneType,
        )

    async def image_profiles(
        self,
        *,
        image_mapping: Dict[str, image_profile_image_profiles_params.ImageMapping],
        name: str,
        region_id: str,
        api_version: str | Omit = omit,
        description: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ImageProfile:
        """Create image profile.

        This image profile is created for the specific region.
        Image mapping definitions are created together with the profile. All existing
        image mapping definitions for the specified region will be replaced with the
        payload provided and if you want to keep the existing definitions, they should
        be added to the payload.

        Args:
          image_mapping: Image mapping defined for the corresponding region.

          name: A human-friendly name used as an identifier in APIs that support this option.

          region_id: The id of the region for which this profile is created

          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          description: A human-friendly description.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/iaas/api/image-profiles",
            body=await async_maybe_transform(
                {
                    "image_mapping": image_mapping,
                    "name": name,
                    "region_id": region_id,
                    "description": description,
                },
                image_profile_image_profiles_params.ImageProfileImageProfilesParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"api_version": api_version}, image_profile_image_profiles_params.ImageProfileImageProfilesParams
                ),
            ),
            cast_to=ImageProfile,
        )

    async def retrieve_image_profiles(
        self,
        *,
        api_version: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ImageProfileRetrieveImageProfilesResponse:
        """
        Get all image profiles

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/iaas/api/image-profiles",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"api_version": api_version},
                    image_profile_retrieve_image_profiles_params.ImageProfileRetrieveImageProfilesParams,
                ),
            ),
            cast_to=ImageProfileRetrieveImageProfilesResponse,
        )


class ImageProfilesResourceWithRawResponse:
    def __init__(self, image_profiles: ImageProfilesResource) -> None:
        self._image_profiles = image_profiles

        self.retrieve = to_raw_response_wrapper(
            image_profiles.retrieve,
        )
        self.update = to_raw_response_wrapper(
            image_profiles.update,
        )
        self.delete = to_raw_response_wrapper(
            image_profiles.delete,
        )
        self.image_profiles = to_raw_response_wrapper(
            image_profiles.image_profiles,
        )
        self.retrieve_image_profiles = to_raw_response_wrapper(
            image_profiles.retrieve_image_profiles,
        )


class AsyncImageProfilesResourceWithRawResponse:
    def __init__(self, image_profiles: AsyncImageProfilesResource) -> None:
        self._image_profiles = image_profiles

        self.retrieve = async_to_raw_response_wrapper(
            image_profiles.retrieve,
        )
        self.update = async_to_raw_response_wrapper(
            image_profiles.update,
        )
        self.delete = async_to_raw_response_wrapper(
            image_profiles.delete,
        )
        self.image_profiles = async_to_raw_response_wrapper(
            image_profiles.image_profiles,
        )
        self.retrieve_image_profiles = async_to_raw_response_wrapper(
            image_profiles.retrieve_image_profiles,
        )


class ImageProfilesResourceWithStreamingResponse:
    def __init__(self, image_profiles: ImageProfilesResource) -> None:
        self._image_profiles = image_profiles

        self.retrieve = to_streamed_response_wrapper(
            image_profiles.retrieve,
        )
        self.update = to_streamed_response_wrapper(
            image_profiles.update,
        )
        self.delete = to_streamed_response_wrapper(
            image_profiles.delete,
        )
        self.image_profiles = to_streamed_response_wrapper(
            image_profiles.image_profiles,
        )
        self.retrieve_image_profiles = to_streamed_response_wrapper(
            image_profiles.retrieve_image_profiles,
        )


class AsyncImageProfilesResourceWithStreamingResponse:
    def __init__(self, image_profiles: AsyncImageProfilesResource) -> None:
        self._image_profiles = image_profiles

        self.retrieve = async_to_streamed_response_wrapper(
            image_profiles.retrieve,
        )
        self.update = async_to_streamed_response_wrapper(
            image_profiles.update,
        )
        self.delete = async_to_streamed_response_wrapper(
            image_profiles.delete,
        )
        self.image_profiles = async_to_streamed_response_wrapper(
            image_profiles.image_profiles,
        )
        self.retrieve_image_profiles = async_to_streamed_response_wrapper(
            image_profiles.retrieve_image_profiles,
        )
