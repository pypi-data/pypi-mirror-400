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
from ....types.iaas.api import (
    cloud_accounts_vmc_delete_params,
    cloud_accounts_vmc_update_params,
    cloud_accounts_vmc_retrieve_params,
    cloud_accounts_vmc_cloud_accounts_vmc_params,
    cloud_accounts_vmc_region_enumeration_params,
    cloud_accounts_vmc_private_image_enumeration_params,
    cloud_accounts_vmc_retrieve_cloud_accounts_vmc_params,
)
from ....types.iaas.api.tag_param import TagParam
from ....types.iaas.api.cloud_account_vmc import CloudAccountVmc
from ....types.iaas.api.projects.request_tracker import RequestTracker
from ....types.iaas.api.region_specification_param import RegionSpecificationParam
from ....types.iaas.api.certificate_info_specification_param import CertificateInfoSpecificationParam
from ....types.iaas.api.cloud_accounts_vmc_retrieve_cloud_accounts_vmc_response import (
    CloudAccountsVmcRetrieveCloudAccountsVmcResponse,
)

__all__ = ["CloudAccountsVmcResource", "AsyncCloudAccountsVmcResource"]


class CloudAccountsVmcResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> CloudAccountsVmcResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#accessing-raw-response-data-eg-headers
        """
        return CloudAccountsVmcResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> CloudAccountsVmcResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#with_streaming_response
        """
        return CloudAccountsVmcResourceWithStreamingResponse(self)

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
    ) -> CloudAccountVmc:
        """
        Get an VMC cloud account with a given id

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
            f"/iaas/api/cloud-accounts-vmc/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"api_version": api_version}, cloud_accounts_vmc_retrieve_params.CloudAccountsVmcRetrieveParams
                ),
            ),
            cast_to=CloudAccountVmc,
        )

    def update(
        self,
        id: str,
        *,
        api_version: str,
        api_key: str,
        dc_id: str,
        host_name: str,
        name: str,
        nsx_host_name: str,
        password: str,
        regions: Iterable[RegionSpecificationParam],
        sddc_id: str,
        username: str,
        accept_self_signed_certificate: bool | Omit = omit,
        certificate_info: CertificateInfoSpecificationParam | Omit = omit,
        create_default_zones: bool | Omit = omit,
        description: str | Omit = omit,
        environment: str | Omit = omit,
        tags: Iterable[TagParam] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RequestTracker:
        """
        Update VMC cloud account

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          api_key: VMC API access key. Optional when updating.

          dc_id: Identifier of a data collector vm deployed in the on premise infrastructure.
              Refer to the data-collector API to create or list data collectors.

          host_name: Enter the IP address or FQDN of the vCenter Server in the specified SDDC. The
              cloud proxy belongs on this vCenter.

          name: A human-friendly name used as an identifier in APIs that support this option.

          nsx_host_name: The IP address of the NSX Manager server in the specified SDDC / FQDN.

          password: Password for the user used to authenticate with the cloud Account.

          regions: A set of regions to enable provisioning on.Refer to
              /iaas/api/cloud-accounts/region-enumeration.

          sddc_id: Identifier of the on-premise SDDC to be used by this cloud account. Note that
              NSX-V SDDCs are not supported.

          username: vCenter user name for the specified SDDC.The specified user requires CloudAdmin
              credentials. The user does not require CloudGlobalAdmin credentials.

          accept_self_signed_certificate: Accept self signed certificate when connecting to vSphere

          certificate_info: Specification for certificate for a cloud account.

          create_default_zones: Create default cloud zones for the enabled regions.

          description: A human-friendly description.

          environment: The environment where the agent has been deployed. When the agent has been
              deployed using the "Add Ons" in VMC UI or Api use "aap".

          tags: A set of tag keys and optional values to set on the Cloud Account.Cloud account
              capability tags may enable different features.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._patch(
            f"/iaas/api/cloud-accounts-vmc/{id}",
            body=maybe_transform(
                {
                    "api_key": api_key,
                    "dc_id": dc_id,
                    "host_name": host_name,
                    "name": name,
                    "nsx_host_name": nsx_host_name,
                    "password": password,
                    "regions": regions,
                    "sddc_id": sddc_id,
                    "username": username,
                    "accept_self_signed_certificate": accept_self_signed_certificate,
                    "certificate_info": certificate_info,
                    "create_default_zones": create_default_zones,
                    "description": description,
                    "environment": environment,
                    "tags": tags,
                },
                cloud_accounts_vmc_update_params.CloudAccountsVmcUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"api_version": api_version}, cloud_accounts_vmc_update_params.CloudAccountsVmcUpdateParams
                ),
            ),
            cast_to=RequestTracker,
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
        Delete an VMC cloud account with a given id

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
            f"/iaas/api/cloud-accounts-vmc/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"api_version": api_version}, cloud_accounts_vmc_delete_params.CloudAccountsVmcDeleteParams
                ),
            ),
            cast_to=RequestTracker,
        )

    def cloud_accounts_vmc(
        self,
        *,
        api_version: str,
        api_key: str,
        dc_id: str,
        host_name: str,
        name: str,
        nsx_host_name: str,
        password: str,
        regions: Iterable[RegionSpecificationParam],
        sddc_id: str,
        username: str,
        validate_only: str | Omit = omit,
        accept_self_signed_certificate: bool | Omit = omit,
        certificate_info: CertificateInfoSpecificationParam | Omit = omit,
        create_default_zones: bool | Omit = omit,
        description: str | Omit = omit,
        environment: str | Omit = omit,
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

          api_key: VMC API access key.

          dc_id: Identifier of a data collector vm deployed in the on premise infrastructure.
              Refer to the data-collector API to create or list data collectors.

          host_name: Enter the IP address or FQDN of the vCenter Server in the specified SDDC. The
              cloud proxy belongs on this vCenter.

          name: A human-friendly name used as an identifier in APIs that support this option.

          nsx_host_name: The IP address of the NSX Manager server in the specified SDDC / FQDN.

          password: Password for the user used to authenticate with the cloud Account.

          regions: A set of regions to enable provisioning on.Refer to
              /iaas/api/cloud-accounts/region-enumeration.

          sddc_id: Identifier of the on-premise SDDC to be used by this cloud account. Note that
              NSX-V SDDCs are not supported.

          username: vCenter user name for the specified SDDC.The specified user requires CloudAdmin
              credentials. The user does not require CloudGlobalAdmin credentials.

          validate_only: If provided, it only validates the credentials in the Cloud Account
              Specification, and cloud account will not be created.

          accept_self_signed_certificate: Accept self signed certificate when connecting to vSphere

          certificate_info: Specification for certificate for a cloud account.

          create_default_zones: Create default cloud zones for the enabled regions.

          description: A human-friendly description.

          environment: The environment where the agent has been deployed. When the agent has been
              deployed using the "Add Ons" in VMC UI or Api use "aap".

          tags: A set of tag keys and optional values to set on the Cloud Account.Cloud account
              capability tags may enable different features.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/iaas/api/cloud-accounts-vmc",
            body=maybe_transform(
                {
                    "api_key": api_key,
                    "dc_id": dc_id,
                    "host_name": host_name,
                    "name": name,
                    "nsx_host_name": nsx_host_name,
                    "password": password,
                    "regions": regions,
                    "sddc_id": sddc_id,
                    "username": username,
                    "accept_self_signed_certificate": accept_self_signed_certificate,
                    "certificate_info": certificate_info,
                    "create_default_zones": create_default_zones,
                    "description": description,
                    "environment": environment,
                    "tags": tags,
                },
                cloud_accounts_vmc_cloud_accounts_vmc_params.CloudAccountsVmcCloudAccountsVmcParams,
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
                    cloud_accounts_vmc_cloud_accounts_vmc_params.CloudAccountsVmcCloudAccountsVmcParams,
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
        Enumerate all private images for enabled regions of the specified VMC account

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
            f"/iaas/api/cloud-accounts-vmc/{id}/private-image-enumeration",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"api_version": api_version},
                    cloud_accounts_vmc_private_image_enumeration_params.CloudAccountsVmcPrivateImageEnumerationParams,
                ),
            ),
            cast_to=RequestTracker,
        )

    def region_enumeration(
        self,
        *,
        api_version: str,
        accept_self_signed_certificate: bool | Omit = omit,
        api_key: str | Omit = omit,
        certificate_info: CertificateInfoSpecificationParam | Omit = omit,
        cloud_account_id: str | Omit = omit,
        csp_host_name: str | Omit = omit,
        dc_id: str | Omit = omit,
        environment: str | Omit = omit,
        host_name: str | Omit = omit,
        nsx_host_name: str | Omit = omit,
        password: str | Omit = omit,
        sddc_id: str | Omit = omit,
        username: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RequestTracker:
        """
        Get the available regions for specified VMC cloud account

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          accept_self_signed_certificate: Accept self signed certificate when connecting to vSphere

          api_key: VMC API access key. Either provide apiKey or provide a cloudAccountId of an
              existing account.

          certificate_info: Specification for certificate for a cloud account.

          cloud_account_id: Existing cloud account id. Either provide existing cloud account Id, or apiKey,
              sddcId, username, password, hostName, nsxHostName.

          csp_host_name: The host name of the CSP service.

          dc_id: Identifier of a data collector vm deployed in the on premise infrastructure.
              Refer to the data-collector API to create or list data collectors

          environment: The environment where the agent has been deployed. When the agent has been
              deployed using the "Add Ons" in VMC UI or Api use "aap".

          host_name: Enter the IP address or FQDN of the vCenter Server in the specified SDDC. The
              cloud proxy belongs on this vCenter. Either provide hostName or provide a
              cloudAccountId of an existing account.

          nsx_host_name: The IP address of the NSX Manager server in the specified SDDC / FQDN.Either
              provide nsxHostName or provide a cloudAccountId of an existing account.

          password: Password for the user used to authenticate with the cloud Account. Either
              provide password or provide a cloudAccountId of an existing account.

          sddc_id: Identifier of the on-premise SDDC to be used by this cloud account. Note that
              NSX-V SDDCs are not supported. Either provide sddcId or provide a cloudAccountId
              of an existing account.

          username: vCenter user name for the specified SDDC.The specified user requires CloudAdmin
              credentials. The user does not require CloudGlobalAdmin credentials.Either
              provide username or provide a cloudAccountId of an existing account.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/iaas/api/cloud-accounts-vmc/region-enumeration",
            body=maybe_transform(
                {
                    "accept_self_signed_certificate": accept_self_signed_certificate,
                    "api_key": api_key,
                    "certificate_info": certificate_info,
                    "cloud_account_id": cloud_account_id,
                    "csp_host_name": csp_host_name,
                    "dc_id": dc_id,
                    "environment": environment,
                    "host_name": host_name,
                    "nsx_host_name": nsx_host_name,
                    "password": password,
                    "sddc_id": sddc_id,
                    "username": username,
                },
                cloud_accounts_vmc_region_enumeration_params.CloudAccountsVmcRegionEnumerationParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"api_version": api_version},
                    cloud_accounts_vmc_region_enumeration_params.CloudAccountsVmcRegionEnumerationParams,
                ),
            ),
            cast_to=RequestTracker,
        )

    def retrieve_cloud_accounts_vmc(
        self,
        *,
        skip: int | Omit = omit,
        top: int | Omit = omit,
        api_version: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> CloudAccountsVmcRetrieveCloudAccountsVmcResponse:
        """
        Get all VMC cloud accounts within the current organization

        Args:
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
            "/iaas/api/cloud-accounts-vmc",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "skip": skip,
                        "top": top,
                        "api_version": api_version,
                    },
                    cloud_accounts_vmc_retrieve_cloud_accounts_vmc_params.CloudAccountsVmcRetrieveCloudAccountsVmcParams,
                ),
            ),
            cast_to=CloudAccountsVmcRetrieveCloudAccountsVmcResponse,
        )


class AsyncCloudAccountsVmcResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncCloudAccountsVmcResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#accessing-raw-response-data-eg-headers
        """
        return AsyncCloudAccountsVmcResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncCloudAccountsVmcResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#with_streaming_response
        """
        return AsyncCloudAccountsVmcResourceWithStreamingResponse(self)

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
    ) -> CloudAccountVmc:
        """
        Get an VMC cloud account with a given id

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
            f"/iaas/api/cloud-accounts-vmc/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"api_version": api_version}, cloud_accounts_vmc_retrieve_params.CloudAccountsVmcRetrieveParams
                ),
            ),
            cast_to=CloudAccountVmc,
        )

    async def update(
        self,
        id: str,
        *,
        api_version: str,
        api_key: str,
        dc_id: str,
        host_name: str,
        name: str,
        nsx_host_name: str,
        password: str,
        regions: Iterable[RegionSpecificationParam],
        sddc_id: str,
        username: str,
        accept_self_signed_certificate: bool | Omit = omit,
        certificate_info: CertificateInfoSpecificationParam | Omit = omit,
        create_default_zones: bool | Omit = omit,
        description: str | Omit = omit,
        environment: str | Omit = omit,
        tags: Iterable[TagParam] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RequestTracker:
        """
        Update VMC cloud account

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          api_key: VMC API access key. Optional when updating.

          dc_id: Identifier of a data collector vm deployed in the on premise infrastructure.
              Refer to the data-collector API to create or list data collectors.

          host_name: Enter the IP address or FQDN of the vCenter Server in the specified SDDC. The
              cloud proxy belongs on this vCenter.

          name: A human-friendly name used as an identifier in APIs that support this option.

          nsx_host_name: The IP address of the NSX Manager server in the specified SDDC / FQDN.

          password: Password for the user used to authenticate with the cloud Account.

          regions: A set of regions to enable provisioning on.Refer to
              /iaas/api/cloud-accounts/region-enumeration.

          sddc_id: Identifier of the on-premise SDDC to be used by this cloud account. Note that
              NSX-V SDDCs are not supported.

          username: vCenter user name for the specified SDDC.The specified user requires CloudAdmin
              credentials. The user does not require CloudGlobalAdmin credentials.

          accept_self_signed_certificate: Accept self signed certificate when connecting to vSphere

          certificate_info: Specification for certificate for a cloud account.

          create_default_zones: Create default cloud zones for the enabled regions.

          description: A human-friendly description.

          environment: The environment where the agent has been deployed. When the agent has been
              deployed using the "Add Ons" in VMC UI or Api use "aap".

          tags: A set of tag keys and optional values to set on the Cloud Account.Cloud account
              capability tags may enable different features.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._patch(
            f"/iaas/api/cloud-accounts-vmc/{id}",
            body=await async_maybe_transform(
                {
                    "api_key": api_key,
                    "dc_id": dc_id,
                    "host_name": host_name,
                    "name": name,
                    "nsx_host_name": nsx_host_name,
                    "password": password,
                    "regions": regions,
                    "sddc_id": sddc_id,
                    "username": username,
                    "accept_self_signed_certificate": accept_self_signed_certificate,
                    "certificate_info": certificate_info,
                    "create_default_zones": create_default_zones,
                    "description": description,
                    "environment": environment,
                    "tags": tags,
                },
                cloud_accounts_vmc_update_params.CloudAccountsVmcUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"api_version": api_version}, cloud_accounts_vmc_update_params.CloudAccountsVmcUpdateParams
                ),
            ),
            cast_to=RequestTracker,
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
        Delete an VMC cloud account with a given id

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
            f"/iaas/api/cloud-accounts-vmc/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"api_version": api_version}, cloud_accounts_vmc_delete_params.CloudAccountsVmcDeleteParams
                ),
            ),
            cast_to=RequestTracker,
        )

    async def cloud_accounts_vmc(
        self,
        *,
        api_version: str,
        api_key: str,
        dc_id: str,
        host_name: str,
        name: str,
        nsx_host_name: str,
        password: str,
        regions: Iterable[RegionSpecificationParam],
        sddc_id: str,
        username: str,
        validate_only: str | Omit = omit,
        accept_self_signed_certificate: bool | Omit = omit,
        certificate_info: CertificateInfoSpecificationParam | Omit = omit,
        create_default_zones: bool | Omit = omit,
        description: str | Omit = omit,
        environment: str | Omit = omit,
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

          api_key: VMC API access key.

          dc_id: Identifier of a data collector vm deployed in the on premise infrastructure.
              Refer to the data-collector API to create or list data collectors.

          host_name: Enter the IP address or FQDN of the vCenter Server in the specified SDDC. The
              cloud proxy belongs on this vCenter.

          name: A human-friendly name used as an identifier in APIs that support this option.

          nsx_host_name: The IP address of the NSX Manager server in the specified SDDC / FQDN.

          password: Password for the user used to authenticate with the cloud Account.

          regions: A set of regions to enable provisioning on.Refer to
              /iaas/api/cloud-accounts/region-enumeration.

          sddc_id: Identifier of the on-premise SDDC to be used by this cloud account. Note that
              NSX-V SDDCs are not supported.

          username: vCenter user name for the specified SDDC.The specified user requires CloudAdmin
              credentials. The user does not require CloudGlobalAdmin credentials.

          validate_only: If provided, it only validates the credentials in the Cloud Account
              Specification, and cloud account will not be created.

          accept_self_signed_certificate: Accept self signed certificate when connecting to vSphere

          certificate_info: Specification for certificate for a cloud account.

          create_default_zones: Create default cloud zones for the enabled regions.

          description: A human-friendly description.

          environment: The environment where the agent has been deployed. When the agent has been
              deployed using the "Add Ons" in VMC UI or Api use "aap".

          tags: A set of tag keys and optional values to set on the Cloud Account.Cloud account
              capability tags may enable different features.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/iaas/api/cloud-accounts-vmc",
            body=await async_maybe_transform(
                {
                    "api_key": api_key,
                    "dc_id": dc_id,
                    "host_name": host_name,
                    "name": name,
                    "nsx_host_name": nsx_host_name,
                    "password": password,
                    "regions": regions,
                    "sddc_id": sddc_id,
                    "username": username,
                    "accept_self_signed_certificate": accept_self_signed_certificate,
                    "certificate_info": certificate_info,
                    "create_default_zones": create_default_zones,
                    "description": description,
                    "environment": environment,
                    "tags": tags,
                },
                cloud_accounts_vmc_cloud_accounts_vmc_params.CloudAccountsVmcCloudAccountsVmcParams,
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
                    cloud_accounts_vmc_cloud_accounts_vmc_params.CloudAccountsVmcCloudAccountsVmcParams,
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
        Enumerate all private images for enabled regions of the specified VMC account

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
            f"/iaas/api/cloud-accounts-vmc/{id}/private-image-enumeration",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"api_version": api_version},
                    cloud_accounts_vmc_private_image_enumeration_params.CloudAccountsVmcPrivateImageEnumerationParams,
                ),
            ),
            cast_to=RequestTracker,
        )

    async def region_enumeration(
        self,
        *,
        api_version: str,
        accept_self_signed_certificate: bool | Omit = omit,
        api_key: str | Omit = omit,
        certificate_info: CertificateInfoSpecificationParam | Omit = omit,
        cloud_account_id: str | Omit = omit,
        csp_host_name: str | Omit = omit,
        dc_id: str | Omit = omit,
        environment: str | Omit = omit,
        host_name: str | Omit = omit,
        nsx_host_name: str | Omit = omit,
        password: str | Omit = omit,
        sddc_id: str | Omit = omit,
        username: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RequestTracker:
        """
        Get the available regions for specified VMC cloud account

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          accept_self_signed_certificate: Accept self signed certificate when connecting to vSphere

          api_key: VMC API access key. Either provide apiKey or provide a cloudAccountId of an
              existing account.

          certificate_info: Specification for certificate for a cloud account.

          cloud_account_id: Existing cloud account id. Either provide existing cloud account Id, or apiKey,
              sddcId, username, password, hostName, nsxHostName.

          csp_host_name: The host name of the CSP service.

          dc_id: Identifier of a data collector vm deployed in the on premise infrastructure.
              Refer to the data-collector API to create or list data collectors

          environment: The environment where the agent has been deployed. When the agent has been
              deployed using the "Add Ons" in VMC UI or Api use "aap".

          host_name: Enter the IP address or FQDN of the vCenter Server in the specified SDDC. The
              cloud proxy belongs on this vCenter. Either provide hostName or provide a
              cloudAccountId of an existing account.

          nsx_host_name: The IP address of the NSX Manager server in the specified SDDC / FQDN.Either
              provide nsxHostName or provide a cloudAccountId of an existing account.

          password: Password for the user used to authenticate with the cloud Account. Either
              provide password or provide a cloudAccountId of an existing account.

          sddc_id: Identifier of the on-premise SDDC to be used by this cloud account. Note that
              NSX-V SDDCs are not supported. Either provide sddcId or provide a cloudAccountId
              of an existing account.

          username: vCenter user name for the specified SDDC.The specified user requires CloudAdmin
              credentials. The user does not require CloudGlobalAdmin credentials.Either
              provide username or provide a cloudAccountId of an existing account.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/iaas/api/cloud-accounts-vmc/region-enumeration",
            body=await async_maybe_transform(
                {
                    "accept_self_signed_certificate": accept_self_signed_certificate,
                    "api_key": api_key,
                    "certificate_info": certificate_info,
                    "cloud_account_id": cloud_account_id,
                    "csp_host_name": csp_host_name,
                    "dc_id": dc_id,
                    "environment": environment,
                    "host_name": host_name,
                    "nsx_host_name": nsx_host_name,
                    "password": password,
                    "sddc_id": sddc_id,
                    "username": username,
                },
                cloud_accounts_vmc_region_enumeration_params.CloudAccountsVmcRegionEnumerationParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"api_version": api_version},
                    cloud_accounts_vmc_region_enumeration_params.CloudAccountsVmcRegionEnumerationParams,
                ),
            ),
            cast_to=RequestTracker,
        )

    async def retrieve_cloud_accounts_vmc(
        self,
        *,
        skip: int | Omit = omit,
        top: int | Omit = omit,
        api_version: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> CloudAccountsVmcRetrieveCloudAccountsVmcResponse:
        """
        Get all VMC cloud accounts within the current organization

        Args:
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
            "/iaas/api/cloud-accounts-vmc",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "skip": skip,
                        "top": top,
                        "api_version": api_version,
                    },
                    cloud_accounts_vmc_retrieve_cloud_accounts_vmc_params.CloudAccountsVmcRetrieveCloudAccountsVmcParams,
                ),
            ),
            cast_to=CloudAccountsVmcRetrieveCloudAccountsVmcResponse,
        )


class CloudAccountsVmcResourceWithRawResponse:
    def __init__(self, cloud_accounts_vmc: CloudAccountsVmcResource) -> None:
        self._cloud_accounts_vmc = cloud_accounts_vmc

        self.retrieve = to_raw_response_wrapper(
            cloud_accounts_vmc.retrieve,
        )
        self.update = to_raw_response_wrapper(
            cloud_accounts_vmc.update,
        )
        self.delete = to_raw_response_wrapper(
            cloud_accounts_vmc.delete,
        )
        self.cloud_accounts_vmc = to_raw_response_wrapper(
            cloud_accounts_vmc.cloud_accounts_vmc,
        )
        self.private_image_enumeration = to_raw_response_wrapper(
            cloud_accounts_vmc.private_image_enumeration,
        )
        self.region_enumeration = to_raw_response_wrapper(
            cloud_accounts_vmc.region_enumeration,
        )
        self.retrieve_cloud_accounts_vmc = to_raw_response_wrapper(
            cloud_accounts_vmc.retrieve_cloud_accounts_vmc,
        )


class AsyncCloudAccountsVmcResourceWithRawResponse:
    def __init__(self, cloud_accounts_vmc: AsyncCloudAccountsVmcResource) -> None:
        self._cloud_accounts_vmc = cloud_accounts_vmc

        self.retrieve = async_to_raw_response_wrapper(
            cloud_accounts_vmc.retrieve,
        )
        self.update = async_to_raw_response_wrapper(
            cloud_accounts_vmc.update,
        )
        self.delete = async_to_raw_response_wrapper(
            cloud_accounts_vmc.delete,
        )
        self.cloud_accounts_vmc = async_to_raw_response_wrapper(
            cloud_accounts_vmc.cloud_accounts_vmc,
        )
        self.private_image_enumeration = async_to_raw_response_wrapper(
            cloud_accounts_vmc.private_image_enumeration,
        )
        self.region_enumeration = async_to_raw_response_wrapper(
            cloud_accounts_vmc.region_enumeration,
        )
        self.retrieve_cloud_accounts_vmc = async_to_raw_response_wrapper(
            cloud_accounts_vmc.retrieve_cloud_accounts_vmc,
        )


class CloudAccountsVmcResourceWithStreamingResponse:
    def __init__(self, cloud_accounts_vmc: CloudAccountsVmcResource) -> None:
        self._cloud_accounts_vmc = cloud_accounts_vmc

        self.retrieve = to_streamed_response_wrapper(
            cloud_accounts_vmc.retrieve,
        )
        self.update = to_streamed_response_wrapper(
            cloud_accounts_vmc.update,
        )
        self.delete = to_streamed_response_wrapper(
            cloud_accounts_vmc.delete,
        )
        self.cloud_accounts_vmc = to_streamed_response_wrapper(
            cloud_accounts_vmc.cloud_accounts_vmc,
        )
        self.private_image_enumeration = to_streamed_response_wrapper(
            cloud_accounts_vmc.private_image_enumeration,
        )
        self.region_enumeration = to_streamed_response_wrapper(
            cloud_accounts_vmc.region_enumeration,
        )
        self.retrieve_cloud_accounts_vmc = to_streamed_response_wrapper(
            cloud_accounts_vmc.retrieve_cloud_accounts_vmc,
        )


class AsyncCloudAccountsVmcResourceWithStreamingResponse:
    def __init__(self, cloud_accounts_vmc: AsyncCloudAccountsVmcResource) -> None:
        self._cloud_accounts_vmc = cloud_accounts_vmc

        self.retrieve = async_to_streamed_response_wrapper(
            cloud_accounts_vmc.retrieve,
        )
        self.update = async_to_streamed_response_wrapper(
            cloud_accounts_vmc.update,
        )
        self.delete = async_to_streamed_response_wrapper(
            cloud_accounts_vmc.delete,
        )
        self.cloud_accounts_vmc = async_to_streamed_response_wrapper(
            cloud_accounts_vmc.cloud_accounts_vmc,
        )
        self.private_image_enumeration = async_to_streamed_response_wrapper(
            cloud_accounts_vmc.private_image_enumeration,
        )
        self.region_enumeration = async_to_streamed_response_wrapper(
            cloud_accounts_vmc.region_enumeration,
        )
        self.retrieve_cloud_accounts_vmc = async_to_streamed_response_wrapper(
            cloud_accounts_vmc.retrieve_cloud_accounts_vmc,
        )
