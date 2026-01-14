# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Iterable

import httpx

from .zones import (
    ZonesResource,
    AsyncZonesResource,
    ZonesResourceWithRawResponse,
    AsyncZonesResourceWithRawResponse,
    ZonesResourceWithStreamingResponse,
    AsyncZonesResourceWithStreamingResponse,
)
from ....._types import Body, Omit, Query, Headers, NoneType, NotGiven, omit, not_given
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
from .resource_metadata import (
    ResourceMetadataResource,
    AsyncResourceMetadataResource,
    ResourceMetadataResourceWithRawResponse,
    AsyncResourceMetadataResourceWithRawResponse,
    ResourceMetadataResourceWithStreamingResponse,
    AsyncResourceMetadataResourceWithStreamingResponse,
)
from .....types.iaas.api import (
    project_list_params,
    project_create_params,
    project_delete_params,
    project_update_params,
    project_retrieve_params,
)
from .....types.iaas.api.project import Project
from .....types.iaas.api.user_param import UserParam
from .....types.iaas.api.project_list_response import ProjectListResponse
from .....types.iaas.api.placement_constraint_param import PlacementConstraintParam
from .....types.iaas.api.projects.zone_assignment_specification_param import ZoneAssignmentSpecificationParam

__all__ = ["ProjectsResource", "AsyncProjectsResource"]


class ProjectsResource(SyncAPIResource):
    @cached_property
    def zones(self) -> ZonesResource:
        return ZonesResource(self._client)

    @cached_property
    def resource_metadata(self) -> ResourceMetadataResource:
        return ResourceMetadataResource(self._client)

    @cached_property
    def with_raw_response(self) -> ProjectsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#accessing-raw-response-data-eg-headers
        """
        return ProjectsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ProjectsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#with_streaming_response
        """
        return ProjectsResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        name: str,
        api_version: str | Omit = omit,
        validate_principals: bool | Omit = omit,
        administrators: Iterable[UserParam] | Omit = omit,
        constraints: Dict[str, Iterable[PlacementConstraintParam]] | Omit = omit,
        custom_properties: Dict[str, str] | Omit = omit,
        description: str | Omit = omit,
        machine_naming_template: str | Omit = omit,
        members: Iterable[UserParam] | Omit = omit,
        operation_timeout: int | Omit = omit,
        placement_policy: str | Omit = omit,
        shared_resources: bool | Omit = omit,
        supervisors: Iterable[UserParam] | Omit = omit,
        viewers: Iterable[UserParam] | Omit = omit,
        zone_assignment_configurations: Iterable[ZoneAssignmentSpecificationParam] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Project:
        """
        Create project

        Args:
          name: A human-friendly name used as an identifier in APIs that support this option.

          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          validate_principals: If true, a limit of 20 principals is enforced. Additionally each principal is
              validated in the Identity provider and important rules for group email formats
              are enforced.

          administrators: List of administrator users associated with the project. Only administrators can
              manage project's configuration.

          constraints: List of storage, network and extensibility constraints to be applied when
              provisioning through this project.

          custom_properties: The project custom properties which are added to all requests in this project

          description: A human-friendly description.

          machine_naming_template: The naming template to be used for machines provisioned in this project

          members: List of member users associated with the project.

          operation_timeout: The timeout that should be used for Blueprint operations and Provisioning tasks.
              The timeout is in seconds

          placement_policy: Placement policy for the project. Determines how a zone will be selected for
              provisioning. DEFAULT, SPREAD or SPREAD_MEMORY.

          shared_resources: Specifies whether the resources in this projects are shared or not. If not set
              default will be used.

          supervisors: List of supervisor users associated with the project.

          viewers: List of viewer users associated with the project.

          zone_assignment_configurations: List of configurations for zone assignment to a project.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/iaas/api/projects",
            body=maybe_transform(
                {
                    "name": name,
                    "administrators": administrators,
                    "constraints": constraints,
                    "custom_properties": custom_properties,
                    "description": description,
                    "machine_naming_template": machine_naming_template,
                    "members": members,
                    "operation_timeout": operation_timeout,
                    "placement_policy": placement_policy,
                    "shared_resources": shared_resources,
                    "supervisors": supervisors,
                    "viewers": viewers,
                    "zone_assignment_configurations": zone_assignment_configurations,
                },
                project_create_params.ProjectCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "api_version": api_version,
                        "validate_principals": validate_principals,
                    },
                    project_create_params.ProjectCreateParams,
                ),
            ),
            cast_to=Project,
        )

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
    ) -> Project:
        """
        Get project with a given id

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
            f"/iaas/api/projects/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"api_version": api_version}, project_retrieve_params.ProjectRetrieveParams),
            ),
            cast_to=Project,
        )

    def update(
        self,
        id: str,
        *,
        name: str,
        api_version: str | Omit = omit,
        validate_principals: bool | Omit = omit,
        administrators: Iterable[UserParam] | Omit = omit,
        constraints: Dict[str, Iterable[PlacementConstraintParam]] | Omit = omit,
        custom_properties: Dict[str, str] | Omit = omit,
        description: str | Omit = omit,
        machine_naming_template: str | Omit = omit,
        members: Iterable[UserParam] | Omit = omit,
        operation_timeout: int | Omit = omit,
        placement_policy: str | Omit = omit,
        shared_resources: bool | Omit = omit,
        supervisors: Iterable[UserParam] | Omit = omit,
        viewers: Iterable[UserParam] | Omit = omit,
        zone_assignment_configurations: Iterable[ZoneAssignmentSpecificationParam] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Project:
        """
        Update project

        Args:
          name: A human-friendly name used as an identifier in APIs that support this option.

          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          validate_principals: If true, a limit of 20 principals is enforced. Additionally each principal is
              validated in the Identity provider and important rules for group email formats
              are enforced.

          administrators: List of administrator users associated with the project. Only administrators can
              manage project's configuration.

          constraints: List of storage, network and extensibility constraints to be applied when
              provisioning through this project.

          custom_properties: The project custom properties which are added to all requests in this project

          description: A human-friendly description.

          machine_naming_template: The naming template to be used for machines provisioned in this project

          members: List of member users associated with the project.

          operation_timeout: The timeout that should be used for Blueprint operations and Provisioning tasks.
              The timeout is in seconds

          placement_policy: Placement policy for the project. Determines how a zone will be selected for
              provisioning. DEFAULT, SPREAD or SPREAD_MEMORY.

          shared_resources: Specifies whether the resources in this projects are shared or not. If not set
              default will be used.

          supervisors: List of supervisor users associated with the project.

          viewers: List of viewer users associated with the project.

          zone_assignment_configurations: List of configurations for zone assignment to a project.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._patch(
            f"/iaas/api/projects/{id}",
            body=maybe_transform(
                {
                    "name": name,
                    "administrators": administrators,
                    "constraints": constraints,
                    "custom_properties": custom_properties,
                    "description": description,
                    "machine_naming_template": machine_naming_template,
                    "members": members,
                    "operation_timeout": operation_timeout,
                    "placement_policy": placement_policy,
                    "shared_resources": shared_resources,
                    "supervisors": supervisors,
                    "viewers": viewers,
                    "zone_assignment_configurations": zone_assignment_configurations,
                },
                project_update_params.ProjectUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "api_version": api_version,
                        "validate_principals": validate_principals,
                    },
                    project_update_params.ProjectUpdateParams,
                ),
            ),
            cast_to=Project,
        )

    def list(
        self,
        *,
        count: bool | Omit = omit,
        filter: str | Omit = omit,
        order_by: str | Omit = omit,
        skip: int | Omit = omit,
        top: int | Omit = omit,
        api_version: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ProjectListResponse:
        """
        Get all projects

        Args:
          count: Flag which when specified, regardless of the assigned value, shows the total
              number of records. If the collection has a filter it shows the number of records
              matching the filter.

          filter: Filter the results by a specified predicate expression. A set of operators and
              functions are defined for use: Operators: eq, ne, gt, ge, lt, le, and, or, not.
              Functions: bool substringof(string p0, string p1) bool endswith(string p0,
              string p1) bool startswith(string p0, string p1) int length(string p0) int
              indexof(string p0, string p1) string replace(string p0, string find, string
              replace) string substring(string p0, int pos) string substring(string p0, int
              pos, int length) string tolower(string p0) string toupper(string p0) string
              trim(string p0) string concat(string p0, string p1)

          order_by: Sorting criteria in the format: property (asc|desc). Default sort order is
              ascending. Multiple sort criteria are supported.

          skip: Number of records you want to skip.

          top: Number of records you want to get.

          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/iaas/api/projects",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "count": count,
                        "filter": filter,
                        "order_by": order_by,
                        "skip": skip,
                        "top": top,
                        "api_version": api_version,
                    },
                    project_list_params.ProjectListParams,
                ),
            ),
            cast_to=ProjectListResponse,
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
        Delete project with a given id

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
            f"/iaas/api/projects/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"api_version": api_version}, project_delete_params.ProjectDeleteParams),
            ),
            cast_to=NoneType,
        )


class AsyncProjectsResource(AsyncAPIResource):
    @cached_property
    def zones(self) -> AsyncZonesResource:
        return AsyncZonesResource(self._client)

    @cached_property
    def resource_metadata(self) -> AsyncResourceMetadataResource:
        return AsyncResourceMetadataResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncProjectsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#accessing-raw-response-data-eg-headers
        """
        return AsyncProjectsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncProjectsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#with_streaming_response
        """
        return AsyncProjectsResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        name: str,
        api_version: str | Omit = omit,
        validate_principals: bool | Omit = omit,
        administrators: Iterable[UserParam] | Omit = omit,
        constraints: Dict[str, Iterable[PlacementConstraintParam]] | Omit = omit,
        custom_properties: Dict[str, str] | Omit = omit,
        description: str | Omit = omit,
        machine_naming_template: str | Omit = omit,
        members: Iterable[UserParam] | Omit = omit,
        operation_timeout: int | Omit = omit,
        placement_policy: str | Omit = omit,
        shared_resources: bool | Omit = omit,
        supervisors: Iterable[UserParam] | Omit = omit,
        viewers: Iterable[UserParam] | Omit = omit,
        zone_assignment_configurations: Iterable[ZoneAssignmentSpecificationParam] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Project:
        """
        Create project

        Args:
          name: A human-friendly name used as an identifier in APIs that support this option.

          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          validate_principals: If true, a limit of 20 principals is enforced. Additionally each principal is
              validated in the Identity provider and important rules for group email formats
              are enforced.

          administrators: List of administrator users associated with the project. Only administrators can
              manage project's configuration.

          constraints: List of storage, network and extensibility constraints to be applied when
              provisioning through this project.

          custom_properties: The project custom properties which are added to all requests in this project

          description: A human-friendly description.

          machine_naming_template: The naming template to be used for machines provisioned in this project

          members: List of member users associated with the project.

          operation_timeout: The timeout that should be used for Blueprint operations and Provisioning tasks.
              The timeout is in seconds

          placement_policy: Placement policy for the project. Determines how a zone will be selected for
              provisioning. DEFAULT, SPREAD or SPREAD_MEMORY.

          shared_resources: Specifies whether the resources in this projects are shared or not. If not set
              default will be used.

          supervisors: List of supervisor users associated with the project.

          viewers: List of viewer users associated with the project.

          zone_assignment_configurations: List of configurations for zone assignment to a project.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/iaas/api/projects",
            body=await async_maybe_transform(
                {
                    "name": name,
                    "administrators": administrators,
                    "constraints": constraints,
                    "custom_properties": custom_properties,
                    "description": description,
                    "machine_naming_template": machine_naming_template,
                    "members": members,
                    "operation_timeout": operation_timeout,
                    "placement_policy": placement_policy,
                    "shared_resources": shared_resources,
                    "supervisors": supervisors,
                    "viewers": viewers,
                    "zone_assignment_configurations": zone_assignment_configurations,
                },
                project_create_params.ProjectCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "api_version": api_version,
                        "validate_principals": validate_principals,
                    },
                    project_create_params.ProjectCreateParams,
                ),
            ),
            cast_to=Project,
        )

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
    ) -> Project:
        """
        Get project with a given id

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
            f"/iaas/api/projects/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"api_version": api_version}, project_retrieve_params.ProjectRetrieveParams
                ),
            ),
            cast_to=Project,
        )

    async def update(
        self,
        id: str,
        *,
        name: str,
        api_version: str | Omit = omit,
        validate_principals: bool | Omit = omit,
        administrators: Iterable[UserParam] | Omit = omit,
        constraints: Dict[str, Iterable[PlacementConstraintParam]] | Omit = omit,
        custom_properties: Dict[str, str] | Omit = omit,
        description: str | Omit = omit,
        machine_naming_template: str | Omit = omit,
        members: Iterable[UserParam] | Omit = omit,
        operation_timeout: int | Omit = omit,
        placement_policy: str | Omit = omit,
        shared_resources: bool | Omit = omit,
        supervisors: Iterable[UserParam] | Omit = omit,
        viewers: Iterable[UserParam] | Omit = omit,
        zone_assignment_configurations: Iterable[ZoneAssignmentSpecificationParam] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Project:
        """
        Update project

        Args:
          name: A human-friendly name used as an identifier in APIs that support this option.

          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          validate_principals: If true, a limit of 20 principals is enforced. Additionally each principal is
              validated in the Identity provider and important rules for group email formats
              are enforced.

          administrators: List of administrator users associated with the project. Only administrators can
              manage project's configuration.

          constraints: List of storage, network and extensibility constraints to be applied when
              provisioning through this project.

          custom_properties: The project custom properties which are added to all requests in this project

          description: A human-friendly description.

          machine_naming_template: The naming template to be used for machines provisioned in this project

          members: List of member users associated with the project.

          operation_timeout: The timeout that should be used for Blueprint operations and Provisioning tasks.
              The timeout is in seconds

          placement_policy: Placement policy for the project. Determines how a zone will be selected for
              provisioning. DEFAULT, SPREAD or SPREAD_MEMORY.

          shared_resources: Specifies whether the resources in this projects are shared or not. If not set
              default will be used.

          supervisors: List of supervisor users associated with the project.

          viewers: List of viewer users associated with the project.

          zone_assignment_configurations: List of configurations for zone assignment to a project.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._patch(
            f"/iaas/api/projects/{id}",
            body=await async_maybe_transform(
                {
                    "name": name,
                    "administrators": administrators,
                    "constraints": constraints,
                    "custom_properties": custom_properties,
                    "description": description,
                    "machine_naming_template": machine_naming_template,
                    "members": members,
                    "operation_timeout": operation_timeout,
                    "placement_policy": placement_policy,
                    "shared_resources": shared_resources,
                    "supervisors": supervisors,
                    "viewers": viewers,
                    "zone_assignment_configurations": zone_assignment_configurations,
                },
                project_update_params.ProjectUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "api_version": api_version,
                        "validate_principals": validate_principals,
                    },
                    project_update_params.ProjectUpdateParams,
                ),
            ),
            cast_to=Project,
        )

    async def list(
        self,
        *,
        count: bool | Omit = omit,
        filter: str | Omit = omit,
        order_by: str | Omit = omit,
        skip: int | Omit = omit,
        top: int | Omit = omit,
        api_version: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ProjectListResponse:
        """
        Get all projects

        Args:
          count: Flag which when specified, regardless of the assigned value, shows the total
              number of records. If the collection has a filter it shows the number of records
              matching the filter.

          filter: Filter the results by a specified predicate expression. A set of operators and
              functions are defined for use: Operators: eq, ne, gt, ge, lt, le, and, or, not.
              Functions: bool substringof(string p0, string p1) bool endswith(string p0,
              string p1) bool startswith(string p0, string p1) int length(string p0) int
              indexof(string p0, string p1) string replace(string p0, string find, string
              replace) string substring(string p0, int pos) string substring(string p0, int
              pos, int length) string tolower(string p0) string toupper(string p0) string
              trim(string p0) string concat(string p0, string p1)

          order_by: Sorting criteria in the format: property (asc|desc). Default sort order is
              ascending. Multiple sort criteria are supported.

          skip: Number of records you want to skip.

          top: Number of records you want to get.

          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/iaas/api/projects",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "count": count,
                        "filter": filter,
                        "order_by": order_by,
                        "skip": skip,
                        "top": top,
                        "api_version": api_version,
                    },
                    project_list_params.ProjectListParams,
                ),
            ),
            cast_to=ProjectListResponse,
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
        Delete project with a given id

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
            f"/iaas/api/projects/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"api_version": api_version}, project_delete_params.ProjectDeleteParams
                ),
            ),
            cast_to=NoneType,
        )


class ProjectsResourceWithRawResponse:
    def __init__(self, projects: ProjectsResource) -> None:
        self._projects = projects

        self.create = to_raw_response_wrapper(
            projects.create,
        )
        self.retrieve = to_raw_response_wrapper(
            projects.retrieve,
        )
        self.update = to_raw_response_wrapper(
            projects.update,
        )
        self.list = to_raw_response_wrapper(
            projects.list,
        )
        self.delete = to_raw_response_wrapper(
            projects.delete,
        )

    @cached_property
    def zones(self) -> ZonesResourceWithRawResponse:
        return ZonesResourceWithRawResponse(self._projects.zones)

    @cached_property
    def resource_metadata(self) -> ResourceMetadataResourceWithRawResponse:
        return ResourceMetadataResourceWithRawResponse(self._projects.resource_metadata)


class AsyncProjectsResourceWithRawResponse:
    def __init__(self, projects: AsyncProjectsResource) -> None:
        self._projects = projects

        self.create = async_to_raw_response_wrapper(
            projects.create,
        )
        self.retrieve = async_to_raw_response_wrapper(
            projects.retrieve,
        )
        self.update = async_to_raw_response_wrapper(
            projects.update,
        )
        self.list = async_to_raw_response_wrapper(
            projects.list,
        )
        self.delete = async_to_raw_response_wrapper(
            projects.delete,
        )

    @cached_property
    def zones(self) -> AsyncZonesResourceWithRawResponse:
        return AsyncZonesResourceWithRawResponse(self._projects.zones)

    @cached_property
    def resource_metadata(self) -> AsyncResourceMetadataResourceWithRawResponse:
        return AsyncResourceMetadataResourceWithRawResponse(self._projects.resource_metadata)


class ProjectsResourceWithStreamingResponse:
    def __init__(self, projects: ProjectsResource) -> None:
        self._projects = projects

        self.create = to_streamed_response_wrapper(
            projects.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            projects.retrieve,
        )
        self.update = to_streamed_response_wrapper(
            projects.update,
        )
        self.list = to_streamed_response_wrapper(
            projects.list,
        )
        self.delete = to_streamed_response_wrapper(
            projects.delete,
        )

    @cached_property
    def zones(self) -> ZonesResourceWithStreamingResponse:
        return ZonesResourceWithStreamingResponse(self._projects.zones)

    @cached_property
    def resource_metadata(self) -> ResourceMetadataResourceWithStreamingResponse:
        return ResourceMetadataResourceWithStreamingResponse(self._projects.resource_metadata)


class AsyncProjectsResourceWithStreamingResponse:
    def __init__(self, projects: AsyncProjectsResource) -> None:
        self._projects = projects

        self.create = async_to_streamed_response_wrapper(
            projects.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            projects.retrieve,
        )
        self.update = async_to_streamed_response_wrapper(
            projects.update,
        )
        self.list = async_to_streamed_response_wrapper(
            projects.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            projects.delete,
        )

    @cached_property
    def zones(self) -> AsyncZonesResourceWithStreamingResponse:
        return AsyncZonesResourceWithStreamingResponse(self._projects.zones)

    @cached_property
    def resource_metadata(self) -> AsyncResourceMetadataResourceWithStreamingResponse:
        return AsyncResourceMetadataResourceWithStreamingResponse(self._projects.resource_metadata)
