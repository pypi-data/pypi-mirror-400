# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Iterable
from typing_extensions import Literal

import httpx

from ...._types import Body, Omit, Query, Headers, NoneType, NotGiven, SequenceNotStr, omit, not_given
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
    network_profile_delete_params,
    network_profile_update_params,
    network_profile_retrieve_params,
    network_profile_network_profiles_params,
    network_profile_retrieve_network_profiles_params,
)
from ....types.iaas.api.tag_param import TagParam
from ....types.iaas.api.network_profile import NetworkProfile
from ....types.iaas.api.network_profile_retrieve_network_profiles_response import (
    NetworkProfileRetrieveNetworkProfilesResponse,
)

__all__ = ["NetworkProfilesResource", "AsyncNetworkProfilesResource"]


class NetworkProfilesResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> NetworkProfilesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#accessing-raw-response-data-eg-headers
        """
        return NetworkProfilesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> NetworkProfilesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#with_streaming_response
        """
        return NetworkProfilesResourceWithStreamingResponse(self)

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
    ) -> NetworkProfile:
        """
        Get network profile with a given id

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
            f"/iaas/api/network-profiles/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"api_version": api_version}, network_profile_retrieve_params.NetworkProfileRetrieveParams
                ),
            ),
            cast_to=NetworkProfile,
        )

    def update(
        self,
        id: str,
        *,
        name: str,
        region_id: str,
        api_version: str | Omit = omit,
        custom_properties: Dict[str, str] | Omit = omit,
        description: str | Omit = omit,
        external_ip_block_ids: SequenceNotStr[str] | Omit = omit,
        fabric_network_ids: SequenceNotStr[str] | Omit = omit,
        isolated_network_cidr_prefix: int | Omit = omit,
        isolation_external_fabric_network_id: str | Omit = omit,
        isolation_network_domain_cidr: str | Omit = omit,
        isolation_network_domain_id: str | Omit = omit,
        isolation_type: Literal["NONE", "SUBNET", "SECURITY_GROUP"] | Omit = omit,
        load_balancer_ids: SequenceNotStr[str] | Omit = omit,
        security_group_ids: SequenceNotStr[str] | Omit = omit,
        tags: Iterable[TagParam] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> NetworkProfile:
        """
        Update network profile

        Args:
          name: A human-friendly name used as an identifier in APIs that support this option.

          region_id: The Id of the region for which this profile is created

          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          custom_properties: Additional properties that may be used to extend the Network Profile object that
              is produced from this specification. For isolationType security group,
              datastoreId identifies the Compute Resource Edge datastore. computeCluster and
              resourcePoolId identify the Compute Resource Edge cluster. For isolationType
              subnet, distributedLogicalRouterStateLink identifies the on-demand network
              distributed local router (NSX-V only). For isolationType subnet,
              tier0LogicalRouterStateLink identifies the on-demand network tier-0 logical
              router (NSX-T only). onDemandNetworkIPAssignmentType identifies the on-demand
              network IP range assignment type static, dynamic, or mixed.

          description: A human-friendly description.

          external_ip_block_ids: List of external IP blocks coming from an external IPAM provider that can be
              used to create subnetworks inside them

          fabric_network_ids: A list of fabric network Ids which are assigned to the network profile.

          isolated_network_cidr_prefix: The CIDR prefix length to be used for the isolated networks that are created
              with the network profile.

          isolation_external_fabric_network_id: The Id of the fabric network used for outbound access.

          isolation_network_domain_cidr: CIDR of the isolation network domain.

          isolation_network_domain_id: The Id of the network domain used for creating isolated networks.

          isolation_type: Specifies the isolation type e.g. none, subnet or security group

          load_balancer_ids: A list of load balancers which are assigned to the network profile.

          security_group_ids: A list of security group Ids which are assigned to the network profile.

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
            f"/iaas/api/network-profiles/{id}",
            body=maybe_transform(
                {
                    "name": name,
                    "region_id": region_id,
                    "custom_properties": custom_properties,
                    "description": description,
                    "external_ip_block_ids": external_ip_block_ids,
                    "fabric_network_ids": fabric_network_ids,
                    "isolated_network_cidr_prefix": isolated_network_cidr_prefix,
                    "isolation_external_fabric_network_id": isolation_external_fabric_network_id,
                    "isolation_network_domain_cidr": isolation_network_domain_cidr,
                    "isolation_network_domain_id": isolation_network_domain_id,
                    "isolation_type": isolation_type,
                    "load_balancer_ids": load_balancer_ids,
                    "security_group_ids": security_group_ids,
                    "tags": tags,
                },
                network_profile_update_params.NetworkProfileUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"api_version": api_version}, network_profile_update_params.NetworkProfileUpdateParams
                ),
            ),
            cast_to=NetworkProfile,
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
        Delete network profile with a given id

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
            f"/iaas/api/network-profiles/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"api_version": api_version}, network_profile_delete_params.NetworkProfileDeleteParams
                ),
            ),
            cast_to=NoneType,
        )

    def network_profiles(
        self,
        *,
        name: str,
        region_id: str,
        api_version: str | Omit = omit,
        custom_properties: Dict[str, str] | Omit = omit,
        description: str | Omit = omit,
        external_ip_block_ids: SequenceNotStr[str] | Omit = omit,
        fabric_network_ids: SequenceNotStr[str] | Omit = omit,
        isolated_network_cidr_prefix: int | Omit = omit,
        isolation_external_fabric_network_id: str | Omit = omit,
        isolation_network_domain_cidr: str | Omit = omit,
        isolation_network_domain_id: str | Omit = omit,
        isolation_type: Literal["NONE", "SUBNET", "SECURITY_GROUP"] | Omit = omit,
        load_balancer_ids: SequenceNotStr[str] | Omit = omit,
        security_group_ids: SequenceNotStr[str] | Omit = omit,
        tags: Iterable[TagParam] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> NetworkProfile:
        """
        Create network profile

        Args:
          name: A human-friendly name used as an identifier in APIs that support this option.

          region_id: The Id of the region for which this profile is created

          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          custom_properties: Additional properties that may be used to extend the Network Profile object that
              is produced from this specification. For isolationType security group,
              datastoreId identifies the Compute Resource Edge datastore. computeCluster and
              resourcePoolId identify the Compute Resource Edge cluster. For isolationType
              subnet, distributedLogicalRouterStateLink identifies the on-demand network
              distributed local router (NSX-V only). For isolationType subnet,
              tier0LogicalRouterStateLink identifies the on-demand network tier-0 logical
              router (NSX-T only). onDemandNetworkIPAssignmentType identifies the on-demand
              network IP range assignment type static, dynamic, or mixed.

          description: A human-friendly description.

          external_ip_block_ids: List of external IP blocks coming from an external IPAM provider that can be
              used to create subnetworks inside them

          fabric_network_ids: A list of fabric network Ids which are assigned to the network profile.

          isolated_network_cidr_prefix: The CIDR prefix length to be used for the isolated networks that are created
              with the network profile.

          isolation_external_fabric_network_id: The Id of the fabric network used for outbound access.

          isolation_network_domain_cidr: CIDR of the isolation network domain.

          isolation_network_domain_id: The Id of the network domain used for creating isolated networks.

          isolation_type: Specifies the isolation type e.g. none, subnet or security group

          load_balancer_ids: A list of load balancers which are assigned to the network profile.

          security_group_ids: A list of security group Ids which are assigned to the network profile.

          tags: A set of tag keys and optional values that should be set on any resource that is
              produced from this specification.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/iaas/api/network-profiles",
            body=maybe_transform(
                {
                    "name": name,
                    "region_id": region_id,
                    "custom_properties": custom_properties,
                    "description": description,
                    "external_ip_block_ids": external_ip_block_ids,
                    "fabric_network_ids": fabric_network_ids,
                    "isolated_network_cidr_prefix": isolated_network_cidr_prefix,
                    "isolation_external_fabric_network_id": isolation_external_fabric_network_id,
                    "isolation_network_domain_cidr": isolation_network_domain_cidr,
                    "isolation_network_domain_id": isolation_network_domain_id,
                    "isolation_type": isolation_type,
                    "load_balancer_ids": load_balancer_ids,
                    "security_group_ids": security_group_ids,
                    "tags": tags,
                },
                network_profile_network_profiles_params.NetworkProfileNetworkProfilesParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"api_version": api_version},
                    network_profile_network_profiles_params.NetworkProfileNetworkProfilesParams,
                ),
            ),
            cast_to=NetworkProfile,
        )

    def retrieve_network_profiles(
        self,
        *,
        count: bool | Omit = omit,
        filter: str | Omit = omit,
        select: str | Omit = omit,
        skip: int | Omit = omit,
        top: int | Omit = omit,
        api_version: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> NetworkProfileRetrieveNetworkProfilesResponse:
        """
        Get all network profiles

        Args:
          count: Flag which when specified, regardless of the assigned value, shows the total
              number of records. If the collection has a filter it shows the number of records
              matching the filter.

          filter: Filter the results by a specified predicate expression. Operators: eq, ne, and,
              or.

          select: Select a subset of properties to include in the response.

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
            "/iaas/api/network-profiles",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "count": count,
                        "filter": filter,
                        "select": select,
                        "skip": skip,
                        "top": top,
                        "api_version": api_version,
                    },
                    network_profile_retrieve_network_profiles_params.NetworkProfileRetrieveNetworkProfilesParams,
                ),
            ),
            cast_to=NetworkProfileRetrieveNetworkProfilesResponse,
        )


class AsyncNetworkProfilesResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncNetworkProfilesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#accessing-raw-response-data-eg-headers
        """
        return AsyncNetworkProfilesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncNetworkProfilesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#with_streaming_response
        """
        return AsyncNetworkProfilesResourceWithStreamingResponse(self)

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
    ) -> NetworkProfile:
        """
        Get network profile with a given id

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
            f"/iaas/api/network-profiles/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"api_version": api_version}, network_profile_retrieve_params.NetworkProfileRetrieveParams
                ),
            ),
            cast_to=NetworkProfile,
        )

    async def update(
        self,
        id: str,
        *,
        name: str,
        region_id: str,
        api_version: str | Omit = omit,
        custom_properties: Dict[str, str] | Omit = omit,
        description: str | Omit = omit,
        external_ip_block_ids: SequenceNotStr[str] | Omit = omit,
        fabric_network_ids: SequenceNotStr[str] | Omit = omit,
        isolated_network_cidr_prefix: int | Omit = omit,
        isolation_external_fabric_network_id: str | Omit = omit,
        isolation_network_domain_cidr: str | Omit = omit,
        isolation_network_domain_id: str | Omit = omit,
        isolation_type: Literal["NONE", "SUBNET", "SECURITY_GROUP"] | Omit = omit,
        load_balancer_ids: SequenceNotStr[str] | Omit = omit,
        security_group_ids: SequenceNotStr[str] | Omit = omit,
        tags: Iterable[TagParam] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> NetworkProfile:
        """
        Update network profile

        Args:
          name: A human-friendly name used as an identifier in APIs that support this option.

          region_id: The Id of the region for which this profile is created

          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          custom_properties: Additional properties that may be used to extend the Network Profile object that
              is produced from this specification. For isolationType security group,
              datastoreId identifies the Compute Resource Edge datastore. computeCluster and
              resourcePoolId identify the Compute Resource Edge cluster. For isolationType
              subnet, distributedLogicalRouterStateLink identifies the on-demand network
              distributed local router (NSX-V only). For isolationType subnet,
              tier0LogicalRouterStateLink identifies the on-demand network tier-0 logical
              router (NSX-T only). onDemandNetworkIPAssignmentType identifies the on-demand
              network IP range assignment type static, dynamic, or mixed.

          description: A human-friendly description.

          external_ip_block_ids: List of external IP blocks coming from an external IPAM provider that can be
              used to create subnetworks inside them

          fabric_network_ids: A list of fabric network Ids which are assigned to the network profile.

          isolated_network_cidr_prefix: The CIDR prefix length to be used for the isolated networks that are created
              with the network profile.

          isolation_external_fabric_network_id: The Id of the fabric network used for outbound access.

          isolation_network_domain_cidr: CIDR of the isolation network domain.

          isolation_network_domain_id: The Id of the network domain used for creating isolated networks.

          isolation_type: Specifies the isolation type e.g. none, subnet or security group

          load_balancer_ids: A list of load balancers which are assigned to the network profile.

          security_group_ids: A list of security group Ids which are assigned to the network profile.

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
            f"/iaas/api/network-profiles/{id}",
            body=await async_maybe_transform(
                {
                    "name": name,
                    "region_id": region_id,
                    "custom_properties": custom_properties,
                    "description": description,
                    "external_ip_block_ids": external_ip_block_ids,
                    "fabric_network_ids": fabric_network_ids,
                    "isolated_network_cidr_prefix": isolated_network_cidr_prefix,
                    "isolation_external_fabric_network_id": isolation_external_fabric_network_id,
                    "isolation_network_domain_cidr": isolation_network_domain_cidr,
                    "isolation_network_domain_id": isolation_network_domain_id,
                    "isolation_type": isolation_type,
                    "load_balancer_ids": load_balancer_ids,
                    "security_group_ids": security_group_ids,
                    "tags": tags,
                },
                network_profile_update_params.NetworkProfileUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"api_version": api_version}, network_profile_update_params.NetworkProfileUpdateParams
                ),
            ),
            cast_to=NetworkProfile,
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
        Delete network profile with a given id

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
            f"/iaas/api/network-profiles/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"api_version": api_version}, network_profile_delete_params.NetworkProfileDeleteParams
                ),
            ),
            cast_to=NoneType,
        )

    async def network_profiles(
        self,
        *,
        name: str,
        region_id: str,
        api_version: str | Omit = omit,
        custom_properties: Dict[str, str] | Omit = omit,
        description: str | Omit = omit,
        external_ip_block_ids: SequenceNotStr[str] | Omit = omit,
        fabric_network_ids: SequenceNotStr[str] | Omit = omit,
        isolated_network_cidr_prefix: int | Omit = omit,
        isolation_external_fabric_network_id: str | Omit = omit,
        isolation_network_domain_cidr: str | Omit = omit,
        isolation_network_domain_id: str | Omit = omit,
        isolation_type: Literal["NONE", "SUBNET", "SECURITY_GROUP"] | Omit = omit,
        load_balancer_ids: SequenceNotStr[str] | Omit = omit,
        security_group_ids: SequenceNotStr[str] | Omit = omit,
        tags: Iterable[TagParam] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> NetworkProfile:
        """
        Create network profile

        Args:
          name: A human-friendly name used as an identifier in APIs that support this option.

          region_id: The Id of the region for which this profile is created

          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          custom_properties: Additional properties that may be used to extend the Network Profile object that
              is produced from this specification. For isolationType security group,
              datastoreId identifies the Compute Resource Edge datastore. computeCluster and
              resourcePoolId identify the Compute Resource Edge cluster. For isolationType
              subnet, distributedLogicalRouterStateLink identifies the on-demand network
              distributed local router (NSX-V only). For isolationType subnet,
              tier0LogicalRouterStateLink identifies the on-demand network tier-0 logical
              router (NSX-T only). onDemandNetworkIPAssignmentType identifies the on-demand
              network IP range assignment type static, dynamic, or mixed.

          description: A human-friendly description.

          external_ip_block_ids: List of external IP blocks coming from an external IPAM provider that can be
              used to create subnetworks inside them

          fabric_network_ids: A list of fabric network Ids which are assigned to the network profile.

          isolated_network_cidr_prefix: The CIDR prefix length to be used for the isolated networks that are created
              with the network profile.

          isolation_external_fabric_network_id: The Id of the fabric network used for outbound access.

          isolation_network_domain_cidr: CIDR of the isolation network domain.

          isolation_network_domain_id: The Id of the network domain used for creating isolated networks.

          isolation_type: Specifies the isolation type e.g. none, subnet or security group

          load_balancer_ids: A list of load balancers which are assigned to the network profile.

          security_group_ids: A list of security group Ids which are assigned to the network profile.

          tags: A set of tag keys and optional values that should be set on any resource that is
              produced from this specification.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/iaas/api/network-profiles",
            body=await async_maybe_transform(
                {
                    "name": name,
                    "region_id": region_id,
                    "custom_properties": custom_properties,
                    "description": description,
                    "external_ip_block_ids": external_ip_block_ids,
                    "fabric_network_ids": fabric_network_ids,
                    "isolated_network_cidr_prefix": isolated_network_cidr_prefix,
                    "isolation_external_fabric_network_id": isolation_external_fabric_network_id,
                    "isolation_network_domain_cidr": isolation_network_domain_cidr,
                    "isolation_network_domain_id": isolation_network_domain_id,
                    "isolation_type": isolation_type,
                    "load_balancer_ids": load_balancer_ids,
                    "security_group_ids": security_group_ids,
                    "tags": tags,
                },
                network_profile_network_profiles_params.NetworkProfileNetworkProfilesParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"api_version": api_version},
                    network_profile_network_profiles_params.NetworkProfileNetworkProfilesParams,
                ),
            ),
            cast_to=NetworkProfile,
        )

    async def retrieve_network_profiles(
        self,
        *,
        count: bool | Omit = omit,
        filter: str | Omit = omit,
        select: str | Omit = omit,
        skip: int | Omit = omit,
        top: int | Omit = omit,
        api_version: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> NetworkProfileRetrieveNetworkProfilesResponse:
        """
        Get all network profiles

        Args:
          count: Flag which when specified, regardless of the assigned value, shows the total
              number of records. If the collection has a filter it shows the number of records
              matching the filter.

          filter: Filter the results by a specified predicate expression. Operators: eq, ne, and,
              or.

          select: Select a subset of properties to include in the response.

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
            "/iaas/api/network-profiles",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "count": count,
                        "filter": filter,
                        "select": select,
                        "skip": skip,
                        "top": top,
                        "api_version": api_version,
                    },
                    network_profile_retrieve_network_profiles_params.NetworkProfileRetrieveNetworkProfilesParams,
                ),
            ),
            cast_to=NetworkProfileRetrieveNetworkProfilesResponse,
        )


class NetworkProfilesResourceWithRawResponse:
    def __init__(self, network_profiles: NetworkProfilesResource) -> None:
        self._network_profiles = network_profiles

        self.retrieve = to_raw_response_wrapper(
            network_profiles.retrieve,
        )
        self.update = to_raw_response_wrapper(
            network_profiles.update,
        )
        self.delete = to_raw_response_wrapper(
            network_profiles.delete,
        )
        self.network_profiles = to_raw_response_wrapper(
            network_profiles.network_profiles,
        )
        self.retrieve_network_profiles = to_raw_response_wrapper(
            network_profiles.retrieve_network_profiles,
        )


class AsyncNetworkProfilesResourceWithRawResponse:
    def __init__(self, network_profiles: AsyncNetworkProfilesResource) -> None:
        self._network_profiles = network_profiles

        self.retrieve = async_to_raw_response_wrapper(
            network_profiles.retrieve,
        )
        self.update = async_to_raw_response_wrapper(
            network_profiles.update,
        )
        self.delete = async_to_raw_response_wrapper(
            network_profiles.delete,
        )
        self.network_profiles = async_to_raw_response_wrapper(
            network_profiles.network_profiles,
        )
        self.retrieve_network_profiles = async_to_raw_response_wrapper(
            network_profiles.retrieve_network_profiles,
        )


class NetworkProfilesResourceWithStreamingResponse:
    def __init__(self, network_profiles: NetworkProfilesResource) -> None:
        self._network_profiles = network_profiles

        self.retrieve = to_streamed_response_wrapper(
            network_profiles.retrieve,
        )
        self.update = to_streamed_response_wrapper(
            network_profiles.update,
        )
        self.delete = to_streamed_response_wrapper(
            network_profiles.delete,
        )
        self.network_profiles = to_streamed_response_wrapper(
            network_profiles.network_profiles,
        )
        self.retrieve_network_profiles = to_streamed_response_wrapper(
            network_profiles.retrieve_network_profiles,
        )


class AsyncNetworkProfilesResourceWithStreamingResponse:
    def __init__(self, network_profiles: AsyncNetworkProfilesResource) -> None:
        self._network_profiles = network_profiles

        self.retrieve = async_to_streamed_response_wrapper(
            network_profiles.retrieve,
        )
        self.update = async_to_streamed_response_wrapper(
            network_profiles.update,
        )
        self.delete = async_to_streamed_response_wrapper(
            network_profiles.delete,
        )
        self.network_profiles = async_to_streamed_response_wrapper(
            network_profiles.network_profiles,
        )
        self.retrieve_network_profiles = async_to_streamed_response_wrapper(
            network_profiles.retrieve_network_profiles,
        )
