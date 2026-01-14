# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal

import httpx

from ...._types import Body, Query, Headers, NotGiven, not_given
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
    configuration_property_delete_params,
    configuration_property_retrieve_params,
    configuration_property_update_configuration_properties_params,
    configuration_property_retrieve_configuration_properties_params,
)
from ....types.iaas.api.configuration_property import ConfigurationProperty
from ....types.iaas.api.configuration_property_result import ConfigurationPropertyResult

__all__ = ["ConfigurationPropertiesResource", "AsyncConfigurationPropertiesResource"]


class ConfigurationPropertiesResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> ConfigurationPropertiesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#accessing-raw-response-data-eg-headers
        """
        return ConfigurationPropertiesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ConfigurationPropertiesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#with_streaming_response
        """
        return ConfigurationPropertiesResourceWithStreamingResponse(self)

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
    ) -> ConfigurationPropertyResult:
        """
        Get single configuration property

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
            f"/iaas/api/configuration-properties/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"api_version": api_version},
                    configuration_property_retrieve_params.ConfigurationPropertyRetrieveParams,
                ),
            ),
            cast_to=ConfigurationPropertyResult,
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
    ) -> ConfigurationProperty:
        """
        Delete a configuration property

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
            f"/iaas/api/configuration-properties/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"api_version": api_version}, configuration_property_delete_params.ConfigurationPropertyDeleteParams
                ),
            ),
            cast_to=ConfigurationProperty,
        )

    def retrieve_configuration_properties(
        self,
        *,
        api_version: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ConfigurationPropertyResult:
        """
        Get all configuration properties

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/iaas/api/configuration-properties",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"api_version": api_version},
                    configuration_property_retrieve_configuration_properties_params.ConfigurationPropertyRetrieveConfigurationPropertiesParams,
                ),
            ),
            cast_to=ConfigurationPropertyResult,
        )

    def update_configuration_properties(
        self,
        *,
        api_version: str,
        key: Literal["SESSION_TIMEOUT_DURATION_MINUTES, RELEASE_IPADDRESS_PERIOD_MINUTES, NSXT_RETRY_DURATION_MINUTES"],
        value: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ConfigurationProperty:
        """
        Update or create configuration property.

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          key: The key of the property.

          value: The value of the property.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._patch(
            "/iaas/api/configuration-properties",
            body=maybe_transform(
                {
                    "key": key,
                    "value": value,
                },
                configuration_property_update_configuration_properties_params.ConfigurationPropertyUpdateConfigurationPropertiesParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"api_version": api_version},
                    configuration_property_update_configuration_properties_params.ConfigurationPropertyUpdateConfigurationPropertiesParams,
                ),
            ),
            cast_to=ConfigurationProperty,
        )


class AsyncConfigurationPropertiesResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncConfigurationPropertiesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#accessing-raw-response-data-eg-headers
        """
        return AsyncConfigurationPropertiesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncConfigurationPropertiesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#with_streaming_response
        """
        return AsyncConfigurationPropertiesResourceWithStreamingResponse(self)

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
    ) -> ConfigurationPropertyResult:
        """
        Get single configuration property

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
            f"/iaas/api/configuration-properties/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"api_version": api_version},
                    configuration_property_retrieve_params.ConfigurationPropertyRetrieveParams,
                ),
            ),
            cast_to=ConfigurationPropertyResult,
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
    ) -> ConfigurationProperty:
        """
        Delete a configuration property

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
            f"/iaas/api/configuration-properties/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"api_version": api_version}, configuration_property_delete_params.ConfigurationPropertyDeleteParams
                ),
            ),
            cast_to=ConfigurationProperty,
        )

    async def retrieve_configuration_properties(
        self,
        *,
        api_version: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ConfigurationPropertyResult:
        """
        Get all configuration properties

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/iaas/api/configuration-properties",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"api_version": api_version},
                    configuration_property_retrieve_configuration_properties_params.ConfigurationPropertyRetrieveConfigurationPropertiesParams,
                ),
            ),
            cast_to=ConfigurationPropertyResult,
        )

    async def update_configuration_properties(
        self,
        *,
        api_version: str,
        key: Literal["SESSION_TIMEOUT_DURATION_MINUTES, RELEASE_IPADDRESS_PERIOD_MINUTES, NSXT_RETRY_DURATION_MINUTES"],
        value: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ConfigurationProperty:
        """
        Update or create configuration property.

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          key: The key of the property.

          value: The value of the property.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._patch(
            "/iaas/api/configuration-properties",
            body=await async_maybe_transform(
                {
                    "key": key,
                    "value": value,
                },
                configuration_property_update_configuration_properties_params.ConfigurationPropertyUpdateConfigurationPropertiesParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"api_version": api_version},
                    configuration_property_update_configuration_properties_params.ConfigurationPropertyUpdateConfigurationPropertiesParams,
                ),
            ),
            cast_to=ConfigurationProperty,
        )


class ConfigurationPropertiesResourceWithRawResponse:
    def __init__(self, configuration_properties: ConfigurationPropertiesResource) -> None:
        self._configuration_properties = configuration_properties

        self.retrieve = to_raw_response_wrapper(
            configuration_properties.retrieve,
        )
        self.delete = to_raw_response_wrapper(
            configuration_properties.delete,
        )
        self.retrieve_configuration_properties = to_raw_response_wrapper(
            configuration_properties.retrieve_configuration_properties,
        )
        self.update_configuration_properties = to_raw_response_wrapper(
            configuration_properties.update_configuration_properties,
        )


class AsyncConfigurationPropertiesResourceWithRawResponse:
    def __init__(self, configuration_properties: AsyncConfigurationPropertiesResource) -> None:
        self._configuration_properties = configuration_properties

        self.retrieve = async_to_raw_response_wrapper(
            configuration_properties.retrieve,
        )
        self.delete = async_to_raw_response_wrapper(
            configuration_properties.delete,
        )
        self.retrieve_configuration_properties = async_to_raw_response_wrapper(
            configuration_properties.retrieve_configuration_properties,
        )
        self.update_configuration_properties = async_to_raw_response_wrapper(
            configuration_properties.update_configuration_properties,
        )


class ConfigurationPropertiesResourceWithStreamingResponse:
    def __init__(self, configuration_properties: ConfigurationPropertiesResource) -> None:
        self._configuration_properties = configuration_properties

        self.retrieve = to_streamed_response_wrapper(
            configuration_properties.retrieve,
        )
        self.delete = to_streamed_response_wrapper(
            configuration_properties.delete,
        )
        self.retrieve_configuration_properties = to_streamed_response_wrapper(
            configuration_properties.retrieve_configuration_properties,
        )
        self.update_configuration_properties = to_streamed_response_wrapper(
            configuration_properties.update_configuration_properties,
        )


class AsyncConfigurationPropertiesResourceWithStreamingResponse:
    def __init__(self, configuration_properties: AsyncConfigurationPropertiesResource) -> None:
        self._configuration_properties = configuration_properties

        self.retrieve = async_to_streamed_response_wrapper(
            configuration_properties.retrieve,
        )
        self.delete = async_to_streamed_response_wrapper(
            configuration_properties.delete,
        )
        self.retrieve_configuration_properties = async_to_streamed_response_wrapper(
            configuration_properties.retrieve_configuration_properties,
        )
        self.update_configuration_properties = async_to_streamed_response_wrapper(
            configuration_properties.update_configuration_properties,
        )
