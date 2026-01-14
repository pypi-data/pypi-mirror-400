# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Iterable
from typing_extensions import Literal

import httpx

from ....._types import Body, Omit, Query, Headers, NotGiven, SequenceNotStr, omit, not_given
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
from .....types.iaas.api import (
    cloud_account_delete_params,
    cloud_account_update_params,
    cloud_account_retrieve_params,
    cloud_account_health_check_params,
    cloud_account_cloud_accounts_params,
    cloud_account_retrieve_cloud_accounts_params,
    cloud_account_private_image_enumeration_params,
)
from .region_enumeration import (
    RegionEnumerationResource,
    AsyncRegionEnumerationResource,
    RegionEnumerationResourceWithRawResponse,
    AsyncRegionEnumerationResourceWithRawResponse,
    RegionEnumerationResourceWithStreamingResponse,
    AsyncRegionEnumerationResourceWithStreamingResponse,
)
from .....types.iaas.api.tag_param import TagParam
from .....types.iaas.api.cloud_account import CloudAccount
from .....types.iaas.api.projects.request_tracker import RequestTracker
from .....types.iaas.api.region_specification_param import RegionSpecificationParam
from .....types.iaas.api.certificate_info_specification_param import CertificateInfoSpecificationParam
from .....types.iaas.api.cloud_account_retrieve_cloud_accounts_response import CloudAccountRetrieveCloudAccountsResponse

__all__ = ["CloudAccountsResource", "AsyncCloudAccountsResource"]


class CloudAccountsResource(SyncAPIResource):
    @cached_property
    def region_enumeration(self) -> RegionEnumerationResource:
        return RegionEnumerationResource(self._client)

    @cached_property
    def with_raw_response(self) -> CloudAccountsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#accessing-raw-response-data-eg-headers
        """
        return CloudAccountsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> CloudAccountsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#with_streaming_response
        """
        return CloudAccountsResourceWithStreamingResponse(self)

    def retrieve(
        self,
        id: str,
        *,
        select: str | Omit = omit,
        api_version: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> CloudAccount:
        """
        Get cloud account with a given id

        Args:
          select: Select a subset of properties to include in the response.

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
            f"/iaas/api/cloud-accounts/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "select": select,
                        "api_version": api_version,
                    },
                    cloud_account_retrieve_params.CloudAccountRetrieveParams,
                ),
            ),
            cast_to=CloudAccount,
        )

    def update(
        self,
        id: str,
        *,
        api_version: str,
        cloud_account_properties: Dict[str, str],
        name: str,
        regions: Iterable[RegionSpecificationParam],
        associated_cloud_account_ids: SequenceNotStr[str] | Omit = omit,
        associated_mobility_cloud_account_ids: Dict[str, Literal["UNIDIRECTIONAL", "BIDIRECTIONAL"]] | Omit = omit,
        certificate_info: CertificateInfoSpecificationParam | Omit = omit,
        create_default_zones: bool | Omit = omit,
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
        Update a single CloudAccount

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          cloud_account_properties: Cloud Account specific properties supplied in as name value pairs

          name: A human-friendly name used as an identifier in APIs that support this option.

          regions: A set of regions to enable provisioning on.Refer to
              /iaas/api/cloud-accounts/region-enumeration. 'regionInfos' is a required
              parameter for AWS, AZURE, GCP, VSPHERE, VMC, VCF cloud account types.

          associated_cloud_account_ids: Cloud accounts to associate with this cloud account

          associated_mobility_cloud_account_ids: Cloud Account IDs and directionalities create associations to other vSphere
              cloud accounts that can be used for workload mobility. ID refers to an
              associated cloud account, and directionality can be unidirectional or
              bidirectional. Only supported on vSphere cloud accounts.

          certificate_info: Specification for certificate for a cloud account.

          create_default_zones: Create default cloud zones for the enabled regions.

          custom_properties: Additional custom properties that may be used to extend the Cloud Account.

          description: A human-friendly description.

          private_key: Secret access key or password to be used to authenticate with the cloud account.

          private_key_id: Access key id or username to be used to authenticate with the cloud account

          tags: A set of tag keys and optional values to set on the Cloud Account

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._patch(
            f"/iaas/api/cloud-accounts/{id}",
            body=maybe_transform(
                {
                    "cloud_account_properties": cloud_account_properties,
                    "name": name,
                    "regions": regions,
                    "associated_cloud_account_ids": associated_cloud_account_ids,
                    "associated_mobility_cloud_account_ids": associated_mobility_cloud_account_ids,
                    "certificate_info": certificate_info,
                    "create_default_zones": create_default_zones,
                    "custom_properties": custom_properties,
                    "description": description,
                    "private_key": private_key,
                    "private_key_id": private_key_id,
                    "tags": tags,
                },
                cloud_account_update_params.CloudAccountUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"api_version": api_version}, cloud_account_update_params.CloudAccountUpdateParams
                ),
            ),
            cast_to=RequestTracker,
        )

    def delete(
        self,
        id: str,
        *,
        api_version: str,
        force_delete: bool | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RequestTracker:
        """
        Delete a cloud account with a given id

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          force_delete: If true, best effort is made for deleting this endpoint and all related
              resources. In some situations, this may leave provisioned infrastructure
              resources behind. Please ensure you remove them manually. If false, a standard
              delete action will be executed.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._delete(
            f"/iaas/api/cloud-accounts/{id}",
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
                    cloud_account_delete_params.CloudAccountDeleteParams,
                ),
            ),
            cast_to=RequestTracker,
        )

    def cloud_accounts(
        self,
        *,
        api_version: str,
        cloud_account_properties: Dict[str, str],
        cloud_account_type: str,
        name: str,
        regions: Iterable[RegionSpecificationParam],
        validate_only: str | Omit = omit,
        associated_cloud_account_ids: SequenceNotStr[str] | Omit = omit,
        associated_mobility_cloud_account_ids: Dict[str, Literal["UNIDIRECTIONAL", "BIDIRECTIONAL"]] | Omit = omit,
        certificate_info: CertificateInfoSpecificationParam | Omit = omit,
        create_default_zones: bool | Omit = omit,
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
        Create a cloud account in the current organization

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          cloud_account_properties: Cloud Account specific properties supplied in as name value pairs

          cloud_account_type: Cloud account type

          name: A human-friendly name used as an identifier in APIs that support this option.

          regions: A set of regions to enable provisioning on.Refer to
              /iaas/api/cloud-accounts/region-enumeration. 'regionInfos' is a required
              parameter for AWS, AZURE, GCP, VSPHERE, VMC, VCF cloud account types.

          validate_only: If provided, it only validates the credentials in the Cloud Account
              Specification, and cloud account will not be created.

          associated_cloud_account_ids: Cloud accounts to associate with this cloud account

          associated_mobility_cloud_account_ids: Cloud Account IDs and directionalities create associations to other vSphere
              cloud accounts that can be used for workload mobility. ID refers to an
              associated cloud account, and directionality can be unidirectional or
              bidirectional. Only supported on vSphere cloud accounts.

          certificate_info: Specification for certificate for a cloud account.

          create_default_zones: Create default cloud zones for the enabled regions.

          custom_properties: Additional custom properties that may be used to extend the Cloud Account.

          description: A human-friendly description.

          private_key: Secret access key or password to be used to authenticate with the cloud account.

          private_key_id: Access key id or username to be used to authenticate with the cloud account

          tags: A set of tag keys and optional values to set on the Cloud Account

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/iaas/api/cloud-accounts",
            body=maybe_transform(
                {
                    "cloud_account_properties": cloud_account_properties,
                    "cloud_account_type": cloud_account_type,
                    "name": name,
                    "regions": regions,
                    "associated_cloud_account_ids": associated_cloud_account_ids,
                    "associated_mobility_cloud_account_ids": associated_mobility_cloud_account_ids,
                    "certificate_info": certificate_info,
                    "create_default_zones": create_default_zones,
                    "custom_properties": custom_properties,
                    "description": description,
                    "private_key": private_key,
                    "private_key_id": private_key_id,
                    "tags": tags,
                },
                cloud_account_cloud_accounts_params.CloudAccountCloudAccountsParams,
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
                    cloud_account_cloud_accounts_params.CloudAccountCloudAccountsParams,
                ),
            ),
            cast_to=RequestTracker,
        )

    def health_check(
        self,
        id: str,
        *,
        api_version: str | Omit = omit,
        periodic_health_check_id: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RequestTracker:
        """
        Starts cloud account health check identified by its endpoint state

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          periodic_health_check_id: If query param is provided then the endpoint health check is not started
              manually from the UI, but after a scheduled process.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._post(
            f"/iaas/api/cloud-accounts/{id}/health-check",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "api_version": api_version,
                        "periodic_health_check_id": periodic_health_check_id,
                    },
                    cloud_account_health_check_params.CloudAccountHealthCheckParams,
                ),
            ),
            cast_to=RequestTracker,
        )

    def private_image_enumeration(
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
    ) -> RequestTracker:
        """
        Enumerate all private images for enabled regions of the specified cloud account

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
        return self._post(
            f"/iaas/api/cloud-accounts/{id}/private-image-enumeration",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"api_version": api_version},
                    cloud_account_private_image_enumeration_params.CloudAccountPrivateImageEnumerationParams,
                ),
            ),
            cast_to=RequestTracker,
        )

    def retrieve_cloud_accounts(
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
    ) -> CloudAccountRetrieveCloudAccountsResponse:
        """
        Get all cloud accounts within the current organization

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
            "/iaas/api/cloud-accounts",
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
                    cloud_account_retrieve_cloud_accounts_params.CloudAccountRetrieveCloudAccountsParams,
                ),
            ),
            cast_to=CloudAccountRetrieveCloudAccountsResponse,
        )


class AsyncCloudAccountsResource(AsyncAPIResource):
    @cached_property
    def region_enumeration(self) -> AsyncRegionEnumerationResource:
        return AsyncRegionEnumerationResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncCloudAccountsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#accessing-raw-response-data-eg-headers
        """
        return AsyncCloudAccountsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncCloudAccountsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#with_streaming_response
        """
        return AsyncCloudAccountsResourceWithStreamingResponse(self)

    async def retrieve(
        self,
        id: str,
        *,
        select: str | Omit = omit,
        api_version: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> CloudAccount:
        """
        Get cloud account with a given id

        Args:
          select: Select a subset of properties to include in the response.

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
            f"/iaas/api/cloud-accounts/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "select": select,
                        "api_version": api_version,
                    },
                    cloud_account_retrieve_params.CloudAccountRetrieveParams,
                ),
            ),
            cast_to=CloudAccount,
        )

    async def update(
        self,
        id: str,
        *,
        api_version: str,
        cloud_account_properties: Dict[str, str],
        name: str,
        regions: Iterable[RegionSpecificationParam],
        associated_cloud_account_ids: SequenceNotStr[str] | Omit = omit,
        associated_mobility_cloud_account_ids: Dict[str, Literal["UNIDIRECTIONAL", "BIDIRECTIONAL"]] | Omit = omit,
        certificate_info: CertificateInfoSpecificationParam | Omit = omit,
        create_default_zones: bool | Omit = omit,
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
        Update a single CloudAccount

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          cloud_account_properties: Cloud Account specific properties supplied in as name value pairs

          name: A human-friendly name used as an identifier in APIs that support this option.

          regions: A set of regions to enable provisioning on.Refer to
              /iaas/api/cloud-accounts/region-enumeration. 'regionInfos' is a required
              parameter for AWS, AZURE, GCP, VSPHERE, VMC, VCF cloud account types.

          associated_cloud_account_ids: Cloud accounts to associate with this cloud account

          associated_mobility_cloud_account_ids: Cloud Account IDs and directionalities create associations to other vSphere
              cloud accounts that can be used for workload mobility. ID refers to an
              associated cloud account, and directionality can be unidirectional or
              bidirectional. Only supported on vSphere cloud accounts.

          certificate_info: Specification for certificate for a cloud account.

          create_default_zones: Create default cloud zones for the enabled regions.

          custom_properties: Additional custom properties that may be used to extend the Cloud Account.

          description: A human-friendly description.

          private_key: Secret access key or password to be used to authenticate with the cloud account.

          private_key_id: Access key id or username to be used to authenticate with the cloud account

          tags: A set of tag keys and optional values to set on the Cloud Account

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._patch(
            f"/iaas/api/cloud-accounts/{id}",
            body=await async_maybe_transform(
                {
                    "cloud_account_properties": cloud_account_properties,
                    "name": name,
                    "regions": regions,
                    "associated_cloud_account_ids": associated_cloud_account_ids,
                    "associated_mobility_cloud_account_ids": associated_mobility_cloud_account_ids,
                    "certificate_info": certificate_info,
                    "create_default_zones": create_default_zones,
                    "custom_properties": custom_properties,
                    "description": description,
                    "private_key": private_key,
                    "private_key_id": private_key_id,
                    "tags": tags,
                },
                cloud_account_update_params.CloudAccountUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"api_version": api_version}, cloud_account_update_params.CloudAccountUpdateParams
                ),
            ),
            cast_to=RequestTracker,
        )

    async def delete(
        self,
        id: str,
        *,
        api_version: str,
        force_delete: bool | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RequestTracker:
        """
        Delete a cloud account with a given id

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          force_delete: If true, best effort is made for deleting this endpoint and all related
              resources. In some situations, this may leave provisioned infrastructure
              resources behind. Please ensure you remove them manually. If false, a standard
              delete action will be executed.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._delete(
            f"/iaas/api/cloud-accounts/{id}",
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
                    cloud_account_delete_params.CloudAccountDeleteParams,
                ),
            ),
            cast_to=RequestTracker,
        )

    async def cloud_accounts(
        self,
        *,
        api_version: str,
        cloud_account_properties: Dict[str, str],
        cloud_account_type: str,
        name: str,
        regions: Iterable[RegionSpecificationParam],
        validate_only: str | Omit = omit,
        associated_cloud_account_ids: SequenceNotStr[str] | Omit = omit,
        associated_mobility_cloud_account_ids: Dict[str, Literal["UNIDIRECTIONAL", "BIDIRECTIONAL"]] | Omit = omit,
        certificate_info: CertificateInfoSpecificationParam | Omit = omit,
        create_default_zones: bool | Omit = omit,
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
        Create a cloud account in the current organization

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          cloud_account_properties: Cloud Account specific properties supplied in as name value pairs

          cloud_account_type: Cloud account type

          name: A human-friendly name used as an identifier in APIs that support this option.

          regions: A set of regions to enable provisioning on.Refer to
              /iaas/api/cloud-accounts/region-enumeration. 'regionInfos' is a required
              parameter for AWS, AZURE, GCP, VSPHERE, VMC, VCF cloud account types.

          validate_only: If provided, it only validates the credentials in the Cloud Account
              Specification, and cloud account will not be created.

          associated_cloud_account_ids: Cloud accounts to associate with this cloud account

          associated_mobility_cloud_account_ids: Cloud Account IDs and directionalities create associations to other vSphere
              cloud accounts that can be used for workload mobility. ID refers to an
              associated cloud account, and directionality can be unidirectional or
              bidirectional. Only supported on vSphere cloud accounts.

          certificate_info: Specification for certificate for a cloud account.

          create_default_zones: Create default cloud zones for the enabled regions.

          custom_properties: Additional custom properties that may be used to extend the Cloud Account.

          description: A human-friendly description.

          private_key: Secret access key or password to be used to authenticate with the cloud account.

          private_key_id: Access key id or username to be used to authenticate with the cloud account

          tags: A set of tag keys and optional values to set on the Cloud Account

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/iaas/api/cloud-accounts",
            body=await async_maybe_transform(
                {
                    "cloud_account_properties": cloud_account_properties,
                    "cloud_account_type": cloud_account_type,
                    "name": name,
                    "regions": regions,
                    "associated_cloud_account_ids": associated_cloud_account_ids,
                    "associated_mobility_cloud_account_ids": associated_mobility_cloud_account_ids,
                    "certificate_info": certificate_info,
                    "create_default_zones": create_default_zones,
                    "custom_properties": custom_properties,
                    "description": description,
                    "private_key": private_key,
                    "private_key_id": private_key_id,
                    "tags": tags,
                },
                cloud_account_cloud_accounts_params.CloudAccountCloudAccountsParams,
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
                    cloud_account_cloud_accounts_params.CloudAccountCloudAccountsParams,
                ),
            ),
            cast_to=RequestTracker,
        )

    async def health_check(
        self,
        id: str,
        *,
        api_version: str | Omit = omit,
        periodic_health_check_id: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RequestTracker:
        """
        Starts cloud account health check identified by its endpoint state

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          periodic_health_check_id: If query param is provided then the endpoint health check is not started
              manually from the UI, but after a scheduled process.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._post(
            f"/iaas/api/cloud-accounts/{id}/health-check",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "api_version": api_version,
                        "periodic_health_check_id": periodic_health_check_id,
                    },
                    cloud_account_health_check_params.CloudAccountHealthCheckParams,
                ),
            ),
            cast_to=RequestTracker,
        )

    async def private_image_enumeration(
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
    ) -> RequestTracker:
        """
        Enumerate all private images for enabled regions of the specified cloud account

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
        return await self._post(
            f"/iaas/api/cloud-accounts/{id}/private-image-enumeration",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"api_version": api_version},
                    cloud_account_private_image_enumeration_params.CloudAccountPrivateImageEnumerationParams,
                ),
            ),
            cast_to=RequestTracker,
        )

    async def retrieve_cloud_accounts(
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
    ) -> CloudAccountRetrieveCloudAccountsResponse:
        """
        Get all cloud accounts within the current organization

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
            "/iaas/api/cloud-accounts",
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
                    cloud_account_retrieve_cloud_accounts_params.CloudAccountRetrieveCloudAccountsParams,
                ),
            ),
            cast_to=CloudAccountRetrieveCloudAccountsResponse,
        )


class CloudAccountsResourceWithRawResponse:
    def __init__(self, cloud_accounts: CloudAccountsResource) -> None:
        self._cloud_accounts = cloud_accounts

        self.retrieve = to_raw_response_wrapper(
            cloud_accounts.retrieve,
        )
        self.update = to_raw_response_wrapper(
            cloud_accounts.update,
        )
        self.delete = to_raw_response_wrapper(
            cloud_accounts.delete,
        )
        self.cloud_accounts = to_raw_response_wrapper(
            cloud_accounts.cloud_accounts,
        )
        self.health_check = to_raw_response_wrapper(
            cloud_accounts.health_check,
        )
        self.private_image_enumeration = to_raw_response_wrapper(
            cloud_accounts.private_image_enumeration,
        )
        self.retrieve_cloud_accounts = to_raw_response_wrapper(
            cloud_accounts.retrieve_cloud_accounts,
        )

    @cached_property
    def region_enumeration(self) -> RegionEnumerationResourceWithRawResponse:
        return RegionEnumerationResourceWithRawResponse(self._cloud_accounts.region_enumeration)


class AsyncCloudAccountsResourceWithRawResponse:
    def __init__(self, cloud_accounts: AsyncCloudAccountsResource) -> None:
        self._cloud_accounts = cloud_accounts

        self.retrieve = async_to_raw_response_wrapper(
            cloud_accounts.retrieve,
        )
        self.update = async_to_raw_response_wrapper(
            cloud_accounts.update,
        )
        self.delete = async_to_raw_response_wrapper(
            cloud_accounts.delete,
        )
        self.cloud_accounts = async_to_raw_response_wrapper(
            cloud_accounts.cloud_accounts,
        )
        self.health_check = async_to_raw_response_wrapper(
            cloud_accounts.health_check,
        )
        self.private_image_enumeration = async_to_raw_response_wrapper(
            cloud_accounts.private_image_enumeration,
        )
        self.retrieve_cloud_accounts = async_to_raw_response_wrapper(
            cloud_accounts.retrieve_cloud_accounts,
        )

    @cached_property
    def region_enumeration(self) -> AsyncRegionEnumerationResourceWithRawResponse:
        return AsyncRegionEnumerationResourceWithRawResponse(self._cloud_accounts.region_enumeration)


class CloudAccountsResourceWithStreamingResponse:
    def __init__(self, cloud_accounts: CloudAccountsResource) -> None:
        self._cloud_accounts = cloud_accounts

        self.retrieve = to_streamed_response_wrapper(
            cloud_accounts.retrieve,
        )
        self.update = to_streamed_response_wrapper(
            cloud_accounts.update,
        )
        self.delete = to_streamed_response_wrapper(
            cloud_accounts.delete,
        )
        self.cloud_accounts = to_streamed_response_wrapper(
            cloud_accounts.cloud_accounts,
        )
        self.health_check = to_streamed_response_wrapper(
            cloud_accounts.health_check,
        )
        self.private_image_enumeration = to_streamed_response_wrapper(
            cloud_accounts.private_image_enumeration,
        )
        self.retrieve_cloud_accounts = to_streamed_response_wrapper(
            cloud_accounts.retrieve_cloud_accounts,
        )

    @cached_property
    def region_enumeration(self) -> RegionEnumerationResourceWithStreamingResponse:
        return RegionEnumerationResourceWithStreamingResponse(self._cloud_accounts.region_enumeration)


class AsyncCloudAccountsResourceWithStreamingResponse:
    def __init__(self, cloud_accounts: AsyncCloudAccountsResource) -> None:
        self._cloud_accounts = cloud_accounts

        self.retrieve = async_to_streamed_response_wrapper(
            cloud_accounts.retrieve,
        )
        self.update = async_to_streamed_response_wrapper(
            cloud_accounts.update,
        )
        self.delete = async_to_streamed_response_wrapper(
            cloud_accounts.delete,
        )
        self.cloud_accounts = async_to_streamed_response_wrapper(
            cloud_accounts.cloud_accounts,
        )
        self.health_check = async_to_streamed_response_wrapper(
            cloud_accounts.health_check,
        )
        self.private_image_enumeration = async_to_streamed_response_wrapper(
            cloud_accounts.private_image_enumeration,
        )
        self.retrieve_cloud_accounts = async_to_streamed_response_wrapper(
            cloud_accounts.retrieve_cloud_accounts,
        )

    @cached_property
    def region_enumeration(self) -> AsyncRegionEnumerationResourceWithStreamingResponse:
        return AsyncRegionEnumerationResourceWithStreamingResponse(self._cloud_accounts.region_enumeration)
