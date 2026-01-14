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
    security_group_delete_params,
    security_group_update_params,
    security_group_retrieve_params,
    security_group_security_groups_params,
    security_group_retrieve_security_groups_params,
)
from .....types.iaas.api.tag_param import TagParam
from .....types.iaas.api.security_group import SecurityGroup
from .....types.iaas.api.projects.request_tracker import RequestTracker
from .....types.iaas.api.security_groups.rule_param import RuleParam
from .....types.iaas.api.security_group_retrieve_security_groups_response import (
    SecurityGroupRetrieveSecurityGroupsResponse,
)

__all__ = ["SecurityGroupsResource", "AsyncSecurityGroupsResource"]


class SecurityGroupsResource(SyncAPIResource):
    @cached_property
    def operations(self) -> OperationsResource:
        return OperationsResource(self._client)

    @cached_property
    def with_raw_response(self) -> SecurityGroupsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#accessing-raw-response-data-eg-headers
        """
        return SecurityGroupsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> SecurityGroupsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#with_streaming_response
        """
        return SecurityGroupsResourceWithStreamingResponse(self)

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
    ) -> SecurityGroup:
        """
        Get security group with a given id

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
            f"/iaas/api/security-groups/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"api_version": api_version}, security_group_retrieve_params.SecurityGroupRetrieveParams
                ),
            ),
            cast_to=SecurityGroup,
        )

    def update(
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
    ) -> SecurityGroup:
        """Update security group.

        Only tag updates are supported.

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          tags: A set of tag keys and optional values that should be set on any resource that is
              produced from this specification.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._patch(
            f"/iaas/api/security-groups/{id}",
            body=maybe_transform({"tags": tags}, security_group_update_params.SecurityGroupUpdateParams),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"api_version": api_version}, security_group_update_params.SecurityGroupUpdateParams
                ),
            ),
            cast_to=SecurityGroup,
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
        Delete an on-demand security group with a given id

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          force_delete: Controls whether this is a force delete operation. If true, best effort is made
              for deleting this security group. Use with caution as force deleting may cause
              inconsistencies between the cloud provider and VMware Aria Automation.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._delete(
            f"/iaas/api/security-groups/{id}",
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
                    security_group_delete_params.SecurityGroupDeleteParams,
                ),
            ),
            cast_to=RequestTracker,
        )

    def retrieve_security_groups(
        self,
        *,
        api_version: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SecurityGroupRetrieveSecurityGroupsResponse:
        """
        Get all security groups

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/iaas/api/security-groups",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"api_version": api_version},
                    security_group_retrieve_security_groups_params.SecurityGroupRetrieveSecurityGroupsParams,
                ),
            ),
            cast_to=SecurityGroupRetrieveSecurityGroupsResponse,
        )

    def security_groups(
        self,
        *,
        name: str,
        project_id: str,
        api_version: str | Omit = omit,
        custom_properties: Dict[str, str] | Omit = omit,
        deployment_id: str | Omit = omit,
        description: str | Omit = omit,
        rules: Iterable[RuleParam] | Omit = omit,
        tags: Iterable[TagParam] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RequestTracker:
        """
        Provision a new on-demand security group

        Args:
          name: A human-friendly name used as an identifier in APIs that support this option.

          project_id: The id of the project the current user belongs to.

          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          custom_properties: Additional custom properties that may be used to extend this resource.

          deployment_id: The id of the deployment that is associated with this resource

          description: A human-friendly description.

          rules: List of security rules.

          tags: A set of tag keys and optional values that should be set on any resource that is
              produced from this specification.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/iaas/api/security-groups",
            body=maybe_transform(
                {
                    "name": name,
                    "project_id": project_id,
                    "custom_properties": custom_properties,
                    "deployment_id": deployment_id,
                    "description": description,
                    "rules": rules,
                    "tags": tags,
                },
                security_group_security_groups_params.SecurityGroupSecurityGroupsParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"api_version": api_version},
                    security_group_security_groups_params.SecurityGroupSecurityGroupsParams,
                ),
            ),
            cast_to=RequestTracker,
        )


class AsyncSecurityGroupsResource(AsyncAPIResource):
    @cached_property
    def operations(self) -> AsyncOperationsResource:
        return AsyncOperationsResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncSecurityGroupsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#accessing-raw-response-data-eg-headers
        """
        return AsyncSecurityGroupsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncSecurityGroupsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#with_streaming_response
        """
        return AsyncSecurityGroupsResourceWithStreamingResponse(self)

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
    ) -> SecurityGroup:
        """
        Get security group with a given id

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
            f"/iaas/api/security-groups/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"api_version": api_version}, security_group_retrieve_params.SecurityGroupRetrieveParams
                ),
            ),
            cast_to=SecurityGroup,
        )

    async def update(
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
    ) -> SecurityGroup:
        """Update security group.

        Only tag updates are supported.

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          tags: A set of tag keys and optional values that should be set on any resource that is
              produced from this specification.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._patch(
            f"/iaas/api/security-groups/{id}",
            body=await async_maybe_transform({"tags": tags}, security_group_update_params.SecurityGroupUpdateParams),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"api_version": api_version}, security_group_update_params.SecurityGroupUpdateParams
                ),
            ),
            cast_to=SecurityGroup,
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
        Delete an on-demand security group with a given id

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          force_delete: Controls whether this is a force delete operation. If true, best effort is made
              for deleting this security group. Use with caution as force deleting may cause
              inconsistencies between the cloud provider and VMware Aria Automation.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._delete(
            f"/iaas/api/security-groups/{id}",
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
                    security_group_delete_params.SecurityGroupDeleteParams,
                ),
            ),
            cast_to=RequestTracker,
        )

    async def retrieve_security_groups(
        self,
        *,
        api_version: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SecurityGroupRetrieveSecurityGroupsResponse:
        """
        Get all security groups

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/iaas/api/security-groups",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"api_version": api_version},
                    security_group_retrieve_security_groups_params.SecurityGroupRetrieveSecurityGroupsParams,
                ),
            ),
            cast_to=SecurityGroupRetrieveSecurityGroupsResponse,
        )

    async def security_groups(
        self,
        *,
        name: str,
        project_id: str,
        api_version: str | Omit = omit,
        custom_properties: Dict[str, str] | Omit = omit,
        deployment_id: str | Omit = omit,
        description: str | Omit = omit,
        rules: Iterable[RuleParam] | Omit = omit,
        tags: Iterable[TagParam] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RequestTracker:
        """
        Provision a new on-demand security group

        Args:
          name: A human-friendly name used as an identifier in APIs that support this option.

          project_id: The id of the project the current user belongs to.

          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          custom_properties: Additional custom properties that may be used to extend this resource.

          deployment_id: The id of the deployment that is associated with this resource

          description: A human-friendly description.

          rules: List of security rules.

          tags: A set of tag keys and optional values that should be set on any resource that is
              produced from this specification.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/iaas/api/security-groups",
            body=await async_maybe_transform(
                {
                    "name": name,
                    "project_id": project_id,
                    "custom_properties": custom_properties,
                    "deployment_id": deployment_id,
                    "description": description,
                    "rules": rules,
                    "tags": tags,
                },
                security_group_security_groups_params.SecurityGroupSecurityGroupsParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"api_version": api_version},
                    security_group_security_groups_params.SecurityGroupSecurityGroupsParams,
                ),
            ),
            cast_to=RequestTracker,
        )


class SecurityGroupsResourceWithRawResponse:
    def __init__(self, security_groups: SecurityGroupsResource) -> None:
        self._security_groups = security_groups

        self.retrieve = to_raw_response_wrapper(
            security_groups.retrieve,
        )
        self.update = to_raw_response_wrapper(
            security_groups.update,
        )
        self.delete = to_raw_response_wrapper(
            security_groups.delete,
        )
        self.retrieve_security_groups = to_raw_response_wrapper(
            security_groups.retrieve_security_groups,
        )
        self.security_groups = to_raw_response_wrapper(
            security_groups.security_groups,
        )

    @cached_property
    def operations(self) -> OperationsResourceWithRawResponse:
        return OperationsResourceWithRawResponse(self._security_groups.operations)


class AsyncSecurityGroupsResourceWithRawResponse:
    def __init__(self, security_groups: AsyncSecurityGroupsResource) -> None:
        self._security_groups = security_groups

        self.retrieve = async_to_raw_response_wrapper(
            security_groups.retrieve,
        )
        self.update = async_to_raw_response_wrapper(
            security_groups.update,
        )
        self.delete = async_to_raw_response_wrapper(
            security_groups.delete,
        )
        self.retrieve_security_groups = async_to_raw_response_wrapper(
            security_groups.retrieve_security_groups,
        )
        self.security_groups = async_to_raw_response_wrapper(
            security_groups.security_groups,
        )

    @cached_property
    def operations(self) -> AsyncOperationsResourceWithRawResponse:
        return AsyncOperationsResourceWithRawResponse(self._security_groups.operations)


class SecurityGroupsResourceWithStreamingResponse:
    def __init__(self, security_groups: SecurityGroupsResource) -> None:
        self._security_groups = security_groups

        self.retrieve = to_streamed_response_wrapper(
            security_groups.retrieve,
        )
        self.update = to_streamed_response_wrapper(
            security_groups.update,
        )
        self.delete = to_streamed_response_wrapper(
            security_groups.delete,
        )
        self.retrieve_security_groups = to_streamed_response_wrapper(
            security_groups.retrieve_security_groups,
        )
        self.security_groups = to_streamed_response_wrapper(
            security_groups.security_groups,
        )

    @cached_property
    def operations(self) -> OperationsResourceWithStreamingResponse:
        return OperationsResourceWithStreamingResponse(self._security_groups.operations)


class AsyncSecurityGroupsResourceWithStreamingResponse:
    def __init__(self, security_groups: AsyncSecurityGroupsResource) -> None:
        self._security_groups = security_groups

        self.retrieve = async_to_streamed_response_wrapper(
            security_groups.retrieve,
        )
        self.update = async_to_streamed_response_wrapper(
            security_groups.update,
        )
        self.delete = async_to_streamed_response_wrapper(
            security_groups.delete,
        )
        self.retrieve_security_groups = async_to_streamed_response_wrapper(
            security_groups.retrieve_security_groups,
        )
        self.security_groups = async_to_streamed_response_wrapper(
            security_groups.security_groups,
        )

    @cached_property
    def operations(self) -> AsyncOperationsResourceWithStreamingResponse:
        return AsyncOperationsResourceWithStreamingResponse(self._security_groups.operations)
