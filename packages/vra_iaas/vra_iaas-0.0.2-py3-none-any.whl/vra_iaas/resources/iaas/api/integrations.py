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
    integration_list_params,
    integration_create_params,
    integration_delete_params,
    integration_update_params,
    integration_retrieve_params,
)
from ....types.iaas.api.tag_param import TagParam
from ....types.iaas.api.integration import Integration
from ....types.iaas.api.projects.request_tracker import RequestTracker
from ....types.iaas.api.integration_list_response import IntegrationListResponse
from ....types.iaas.api.certificate_info_specification_param import CertificateInfoSpecificationParam

__all__ = ["IntegrationsResource", "AsyncIntegrationsResource"]


class IntegrationsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> IntegrationsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#accessing-raw-response-data-eg-headers
        """
        return IntegrationsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> IntegrationsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#with_streaming_response
        """
        return IntegrationsResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        api_version: str,
        integration_properties: Dict[str, str],
        integration_type: str,
        name: str,
        validate_only: str | Omit = omit,
        associated_cloud_account_ids: SequenceNotStr[str] | Omit = omit,
        certificate_info: CertificateInfoSpecificationParam | Omit = omit,
        custom_properties: Dict[str, str] | Omit = omit,
        description: str | Omit = omit,
        private_key: str | Omit = omit,
        private_key_id: str | Omit = omit,
        tags: Iterable[TagParam] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RequestTracker:
        """
        Create an integration in the current organization asynchronously

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          integration_properties: Integration specific properties supplied in as name value pairs

          integration_type: Integration type

          name: A human-friendly name used as an identifier in APIs that support this option.

          validate_only: Only validate provided Integration Specification. Integration will not be
              created.

          associated_cloud_account_ids: Cloud accounts to associate with this integration

          certificate_info: Specification for certificate for a cloud account.

          custom_properties: Additional custom properties that may be used to extend the Integration.

          description: A human-friendly description.

          private_key: Secret access key or password to be used to authenticate with the integration

          private_key_id: Access key id or username to be used to authenticate with the integration

          tags: A set of tag keys and optional values to set on the Integration

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/iaas/api/integrations",
            body=maybe_transform(
                {
                    "integration_properties": integration_properties,
                    "integration_type": integration_type,
                    "name": name,
                    "associated_cloud_account_ids": associated_cloud_account_ids,
                    "certificate_info": certificate_info,
                    "custom_properties": custom_properties,
                    "description": description,
                    "private_key": private_key,
                    "private_key_id": private_key_id,
                    "tags": tags,
                },
                integration_create_params.IntegrationCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "api_version": api_version,
                        "validate_only": validate_only,
                    },
                    integration_create_params.IntegrationCreateParams,
                ),
            ),
            cast_to=RequestTracker,
        )

    def retrieve(
        self,
        id: str,
        *,
        api_version: str,
        select: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Integration:
        """
        Get an integration with a given id

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          select: Select a subset of properties to include in the response.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._get(
            f"/iaas/api/integrations/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "api_version": api_version,
                        "select": select,
                    },
                    integration_retrieve_params.IntegrationRetrieveParams,
                ),
            ),
            cast_to=Integration,
        )

    def update(
        self,
        id: str,
        *,
        api_version: str,
        integration_properties: Dict[str, str],
        name: str,
        associated_cloud_account_ids: SequenceNotStr[str] | Omit = omit,
        certificate_info: CertificateInfoSpecificationParam | Omit = omit,
        custom_properties: Dict[str, str] | Omit = omit,
        description: str | Omit = omit,
        private_key: str | Omit = omit,
        private_key_id: str | Omit = omit,
        tags: Iterable[TagParam] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RequestTracker:
        """
        Update a single integration asynchronously

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          integration_properties: Integration specific properties supplied in as name value pairs

          name: A human-friendly name used as an identifier in APIs that support this option.

          associated_cloud_account_ids: Cloud accounts to associate with this integration

          certificate_info: Specification for certificate for a cloud account.

          custom_properties: Additional custom properties that may be used to extend the Integration.

          description: A human-friendly description.

          private_key: Secret access key or password to be used to authenticate with the integration

          private_key_id: Access key id or username to be used to authenticate with the integration

          tags: A set of tag keys and optional values to set on the Integration

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._patch(
            f"/iaas/api/integrations/{id}",
            body=maybe_transform(
                {
                    "integration_properties": integration_properties,
                    "name": name,
                    "associated_cloud_account_ids": associated_cloud_account_ids,
                    "certificate_info": certificate_info,
                    "custom_properties": custom_properties,
                    "description": description,
                    "private_key": private_key,
                    "private_key_id": private_key_id,
                    "tags": tags,
                },
                integration_update_params.IntegrationUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"api_version": api_version}, integration_update_params.IntegrationUpdateParams),
            ),
            cast_to=RequestTracker,
        )

    def list(
        self,
        *,
        api_version: str,
        count: bool | Omit = omit,
        filter: str | Omit = omit,
        select: str | Omit = omit,
        skip: int | Omit = omit,
        top: int | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> IntegrationListResponse:
        """
        Get all integrations within the current organization

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          count: Flag which when specified, regardless of the assigned value, shows the total
              number of records. If the collection has a filter it shows the number of records
              matching the filter.

          filter: Filter the results by a specified predicate expression. Operators: eq, ne, and,
              or.

          select: Select a subset of properties to include in the response.

          skip: Number of records you want to skip.

          top: Number of records you want to get.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/iaas/api/integrations",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "api_version": api_version,
                        "count": count,
                        "filter": filter,
                        "select": select,
                        "skip": skip,
                        "top": top,
                    },
                    integration_list_params.IntegrationListParams,
                ),
            ),
            cast_to=IntegrationListResponse,
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
    ) -> RequestTracker:
        """
        Delete an integration with a given id asynchronously

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
            f"/iaas/api/integrations/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"api_version": api_version}, integration_delete_params.IntegrationDeleteParams),
            ),
            cast_to=RequestTracker,
        )


class AsyncIntegrationsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncIntegrationsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#accessing-raw-response-data-eg-headers
        """
        return AsyncIntegrationsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncIntegrationsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#with_streaming_response
        """
        return AsyncIntegrationsResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        api_version: str,
        integration_properties: Dict[str, str],
        integration_type: str,
        name: str,
        validate_only: str | Omit = omit,
        associated_cloud_account_ids: SequenceNotStr[str] | Omit = omit,
        certificate_info: CertificateInfoSpecificationParam | Omit = omit,
        custom_properties: Dict[str, str] | Omit = omit,
        description: str | Omit = omit,
        private_key: str | Omit = omit,
        private_key_id: str | Omit = omit,
        tags: Iterable[TagParam] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RequestTracker:
        """
        Create an integration in the current organization asynchronously

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          integration_properties: Integration specific properties supplied in as name value pairs

          integration_type: Integration type

          name: A human-friendly name used as an identifier in APIs that support this option.

          validate_only: Only validate provided Integration Specification. Integration will not be
              created.

          associated_cloud_account_ids: Cloud accounts to associate with this integration

          certificate_info: Specification for certificate for a cloud account.

          custom_properties: Additional custom properties that may be used to extend the Integration.

          description: A human-friendly description.

          private_key: Secret access key or password to be used to authenticate with the integration

          private_key_id: Access key id or username to be used to authenticate with the integration

          tags: A set of tag keys and optional values to set on the Integration

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/iaas/api/integrations",
            body=await async_maybe_transform(
                {
                    "integration_properties": integration_properties,
                    "integration_type": integration_type,
                    "name": name,
                    "associated_cloud_account_ids": associated_cloud_account_ids,
                    "certificate_info": certificate_info,
                    "custom_properties": custom_properties,
                    "description": description,
                    "private_key": private_key,
                    "private_key_id": private_key_id,
                    "tags": tags,
                },
                integration_create_params.IntegrationCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "api_version": api_version,
                        "validate_only": validate_only,
                    },
                    integration_create_params.IntegrationCreateParams,
                ),
            ),
            cast_to=RequestTracker,
        )

    async def retrieve(
        self,
        id: str,
        *,
        api_version: str,
        select: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Integration:
        """
        Get an integration with a given id

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          select: Select a subset of properties to include in the response.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._get(
            f"/iaas/api/integrations/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "api_version": api_version,
                        "select": select,
                    },
                    integration_retrieve_params.IntegrationRetrieveParams,
                ),
            ),
            cast_to=Integration,
        )

    async def update(
        self,
        id: str,
        *,
        api_version: str,
        integration_properties: Dict[str, str],
        name: str,
        associated_cloud_account_ids: SequenceNotStr[str] | Omit = omit,
        certificate_info: CertificateInfoSpecificationParam | Omit = omit,
        custom_properties: Dict[str, str] | Omit = omit,
        description: str | Omit = omit,
        private_key: str | Omit = omit,
        private_key_id: str | Omit = omit,
        tags: Iterable[TagParam] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RequestTracker:
        """
        Update a single integration asynchronously

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          integration_properties: Integration specific properties supplied in as name value pairs

          name: A human-friendly name used as an identifier in APIs that support this option.

          associated_cloud_account_ids: Cloud accounts to associate with this integration

          certificate_info: Specification for certificate for a cloud account.

          custom_properties: Additional custom properties that may be used to extend the Integration.

          description: A human-friendly description.

          private_key: Secret access key or password to be used to authenticate with the integration

          private_key_id: Access key id or username to be used to authenticate with the integration

          tags: A set of tag keys and optional values to set on the Integration

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._patch(
            f"/iaas/api/integrations/{id}",
            body=await async_maybe_transform(
                {
                    "integration_properties": integration_properties,
                    "name": name,
                    "associated_cloud_account_ids": associated_cloud_account_ids,
                    "certificate_info": certificate_info,
                    "custom_properties": custom_properties,
                    "description": description,
                    "private_key": private_key,
                    "private_key_id": private_key_id,
                    "tags": tags,
                },
                integration_update_params.IntegrationUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"api_version": api_version}, integration_update_params.IntegrationUpdateParams
                ),
            ),
            cast_to=RequestTracker,
        )

    async def list(
        self,
        *,
        api_version: str,
        count: bool | Omit = omit,
        filter: str | Omit = omit,
        select: str | Omit = omit,
        skip: int | Omit = omit,
        top: int | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> IntegrationListResponse:
        """
        Get all integrations within the current organization

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          count: Flag which when specified, regardless of the assigned value, shows the total
              number of records. If the collection has a filter it shows the number of records
              matching the filter.

          filter: Filter the results by a specified predicate expression. Operators: eq, ne, and,
              or.

          select: Select a subset of properties to include in the response.

          skip: Number of records you want to skip.

          top: Number of records you want to get.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/iaas/api/integrations",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "api_version": api_version,
                        "count": count,
                        "filter": filter,
                        "select": select,
                        "skip": skip,
                        "top": top,
                    },
                    integration_list_params.IntegrationListParams,
                ),
            ),
            cast_to=IntegrationListResponse,
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
    ) -> RequestTracker:
        """
        Delete an integration with a given id asynchronously

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
            f"/iaas/api/integrations/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"api_version": api_version}, integration_delete_params.IntegrationDeleteParams
                ),
            ),
            cast_to=RequestTracker,
        )


class IntegrationsResourceWithRawResponse:
    def __init__(self, integrations: IntegrationsResource) -> None:
        self._integrations = integrations

        self.create = to_raw_response_wrapper(
            integrations.create,
        )
        self.retrieve = to_raw_response_wrapper(
            integrations.retrieve,
        )
        self.update = to_raw_response_wrapper(
            integrations.update,
        )
        self.list = to_raw_response_wrapper(
            integrations.list,
        )
        self.delete = to_raw_response_wrapper(
            integrations.delete,
        )


class AsyncIntegrationsResourceWithRawResponse:
    def __init__(self, integrations: AsyncIntegrationsResource) -> None:
        self._integrations = integrations

        self.create = async_to_raw_response_wrapper(
            integrations.create,
        )
        self.retrieve = async_to_raw_response_wrapper(
            integrations.retrieve,
        )
        self.update = async_to_raw_response_wrapper(
            integrations.update,
        )
        self.list = async_to_raw_response_wrapper(
            integrations.list,
        )
        self.delete = async_to_raw_response_wrapper(
            integrations.delete,
        )


class IntegrationsResourceWithStreamingResponse:
    def __init__(self, integrations: IntegrationsResource) -> None:
        self._integrations = integrations

        self.create = to_streamed_response_wrapper(
            integrations.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            integrations.retrieve,
        )
        self.update = to_streamed_response_wrapper(
            integrations.update,
        )
        self.list = to_streamed_response_wrapper(
            integrations.list,
        )
        self.delete = to_streamed_response_wrapper(
            integrations.delete,
        )


class AsyncIntegrationsResourceWithStreamingResponse:
    def __init__(self, integrations: AsyncIntegrationsResource) -> None:
        self._integrations = integrations

        self.create = async_to_streamed_response_wrapper(
            integrations.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            integrations.retrieve,
        )
        self.update = async_to_streamed_response_wrapper(
            integrations.update,
        )
        self.list = async_to_streamed_response_wrapper(
            integrations.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            integrations.delete,
        )
