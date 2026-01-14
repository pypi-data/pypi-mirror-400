# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from .... import _resource
from .tags import (
    TagsResource,
    AsyncTagsResource,
    TagsResourceWithRawResponse,
    AsyncTagsResourceWithRawResponse,
    TagsResourceWithStreamingResponse,
    AsyncTagsResourceWithStreamingResponse,
)
from .zones import (
    ZonesResource,
    AsyncZonesResource,
    ZonesResourceWithRawResponse,
    AsyncZonesResourceWithRawResponse,
    ZonesResourceWithStreamingResponse,
    AsyncZonesResourceWithStreamingResponse,
)
from .naming import (
    NamingResource,
    AsyncNamingResource,
    NamingResourceWithRawResponse,
    AsyncNamingResourceWithRawResponse,
    NamingResourceWithStreamingResponse,
    AsyncNamingResourceWithStreamingResponse,
)
from .regions import (
    RegionsResource,
    AsyncRegionsResource,
    RegionsResourceWithRawResponse,
    AsyncRegionsResourceWithRawResponse,
    RegionsResourceWithStreamingResponse,
    AsyncRegionsResourceWithStreamingResponse,
)
from .networks import (
    NetworksResource,
    AsyncNetworksResource,
    NetworksResourceWithRawResponse,
    AsyncNetworksResourceWithRawResponse,
    NetworksResourceWithStreamingResponse,
    AsyncNetworksResourceWithStreamingResponse,
)
from ...._types import Body, Omit, Query, Headers, NotGiven, omit, not_given
from ...._utils import maybe_transform, async_maybe_transform
from ...._compat import cached_property
from .deployments import (
    DeploymentsResource,
    AsyncDeploymentsResource,
    DeploymentsResourceWithRawResponse,
    AsyncDeploymentsResourceWithRawResponse,
    DeploymentsResourceWithStreamingResponse,
    AsyncDeploymentsResourceWithStreamingResponse,
)
from ...._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from .integrations import (
    IntegrationsResource,
    AsyncIntegrationsResource,
    IntegrationsResourceWithRawResponse,
    AsyncIntegrationsResourceWithRawResponse,
    IntegrationsResourceWithStreamingResponse,
    AsyncIntegrationsResourceWithStreamingResponse,
)
from ....types.iaas import (
    api_login_params,
    api_retrieve_params,
    api_retrieve_images_params,
    api_retrieve_flavors_params,
    api_retrieve_folders_params,
    api_retrieve_event_logs_params,
    api_retrieve_request_graph_params,
    api_retrieve_fabric_flavors_params,
    api_retrieve_fabric_aws_volume_types_params,
    api_retrieve_fabric_azure_disk_encryption_sets_params,
)
from .fabric_images import (
    FabricImagesResource,
    AsyncFabricImagesResource,
    FabricImagesResourceWithRawResponse,
    AsyncFabricImagesResourceWithRawResponse,
    FabricImagesResourceWithStreamingResponse,
    AsyncFabricImagesResourceWithStreamingResponse,
)
from .image_profiles import (
    ImageProfilesResource,
    AsyncImageProfilesResource,
    ImageProfilesResourceWithRawResponse,
    AsyncImageProfilesResourceWithRawResponse,
    ImageProfilesResourceWithStreamingResponse,
    AsyncImageProfilesResourceWithStreamingResponse,
)
from ...._base_client import make_request_options
from .data_collectors import (
    DataCollectorsResource,
    AsyncDataCollectorsResource,
    DataCollectorsResourceWithRawResponse,
    AsyncDataCollectorsResourceWithRawResponse,
    DataCollectorsResourceWithStreamingResponse,
    AsyncDataCollectorsResourceWithStreamingResponse,
)
from .fabric_computes import (
    FabricComputesResource,
    AsyncFabricComputesResource,
    FabricComputesResourceWithRawResponse,
    AsyncFabricComputesResourceWithRawResponse,
    FabricComputesResourceWithStreamingResponse,
    AsyncFabricComputesResourceWithStreamingResponse,
)
from .fabric_networks import (
    FabricNetworksResource,
    AsyncFabricNetworksResource,
    FabricNetworksResourceWithRawResponse,
    AsyncFabricNetworksResourceWithRawResponse,
    FabricNetworksResourceWithStreamingResponse,
    AsyncFabricNetworksResourceWithStreamingResponse,
)
from .flavor_profiles import (
    FlavorProfilesResource,
    AsyncFlavorProfilesResource,
    FlavorProfilesResourceWithRawResponse,
    AsyncFlavorProfilesResourceWithRawResponse,
    FlavorProfilesResourceWithStreamingResponse,
    AsyncFlavorProfilesResourceWithStreamingResponse,
)
from .network_domains import (
    NetworkDomainsResource,
    AsyncNetworkDomainsResource,
    NetworkDomainsResourceWithRawResponse,
    AsyncNetworkDomainsResourceWithRawResponse,
    NetworkDomainsResourceWithStreamingResponse,
    AsyncNetworkDomainsResourceWithStreamingResponse,
)
from .request_tracker import (
    RequestTrackerResource,
    AsyncRequestTrackerResource,
    RequestTrackerResourceWithRawResponse,
    AsyncRequestTrackerResourceWithRawResponse,
    RequestTrackerResourceWithStreamingResponse,
    AsyncRequestTrackerResourceWithStreamingResponse,
)
from .compute_gateways import (
    ComputeGatewaysResource,
    AsyncComputeGatewaysResource,
    ComputeGatewaysResourceWithRawResponse,
    AsyncComputeGatewaysResourceWithRawResponse,
    ComputeGatewaysResourceWithStreamingResponse,
    AsyncComputeGatewaysResourceWithStreamingResponse,
)
from .network_profiles import (
    NetworkProfilesResource,
    AsyncNetworkProfilesResource,
    NetworkProfilesResourceWithRawResponse,
    AsyncNetworkProfilesResourceWithRawResponse,
    NetworkProfilesResourceWithStreamingResponse,
    AsyncNetworkProfilesResourceWithStreamingResponse,
)
from .machines.machines import (
    MachinesResource,
    AsyncMachinesResource,
    MachinesResourceWithRawResponse,
    AsyncMachinesResourceWithRawResponse,
    MachinesResourceWithStreamingResponse,
    AsyncMachinesResourceWithStreamingResponse,
)
from .projects.projects import (
    ProjectsResource,
    AsyncProjectsResource,
    ProjectsResourceWithRawResponse,
    AsyncProjectsResourceWithRawResponse,
    ProjectsResourceWithStreamingResponse,
    AsyncProjectsResourceWithStreamingResponse,
)
from .cloud_accounts_aws import (
    CloudAccountsAwsResource,
    AsyncCloudAccountsAwsResource,
    CloudAccountsAwsResourceWithRawResponse,
    AsyncCloudAccountsAwsResourceWithRawResponse,
    CloudAccountsAwsResourceWithStreamingResponse,
    AsyncCloudAccountsAwsResourceWithStreamingResponse,
)
from .cloud_accounts_gcp import (
    CloudAccountsGcpResource,
    AsyncCloudAccountsGcpResource,
    CloudAccountsGcpResourceWithRawResponse,
    AsyncCloudAccountsGcpResourceWithRawResponse,
    CloudAccountsGcpResourceWithStreamingResponse,
    AsyncCloudAccountsGcpResourceWithStreamingResponse,
)
from .cloud_accounts_vcf import (
    CloudAccountsVcfResource,
    AsyncCloudAccountsVcfResource,
    CloudAccountsVcfResourceWithRawResponse,
    AsyncCloudAccountsVcfResourceWithRawResponse,
    CloudAccountsVcfResourceWithStreamingResponse,
    AsyncCloudAccountsVcfResourceWithStreamingResponse,
)
from .cloud_accounts_vmc import (
    CloudAccountsVmcResource,
    AsyncCloudAccountsVmcResource,
    CloudAccountsVmcResourceWithRawResponse,
    AsyncCloudAccountsVmcResourceWithRawResponse,
    CloudAccountsVmcResourceWithStreamingResponse,
    AsyncCloudAccountsVmcResourceWithStreamingResponse,
)
from .external_ip_blocks import (
    ExternalIPBlocksResource,
    AsyncExternalIPBlocksResource,
    ExternalIPBlocksResourceWithRawResponse,
    AsyncExternalIPBlocksResourceWithRawResponse,
    ExternalIPBlocksResourceWithStreamingResponse,
    AsyncExternalIPBlocksResourceWithStreamingResponse,
)
from .cloud_accounts_avilb import (
    CloudAccountsAvilbResource,
    AsyncCloudAccountsAvilbResource,
    CloudAccountsAvilbResourceWithRawResponse,
    AsyncCloudAccountsAvilbResourceWithRawResponse,
    CloudAccountsAvilbResourceWithStreamingResponse,
    AsyncCloudAccountsAvilbResourceWithStreamingResponse,
)
from .cloud_accounts_azure import (
    CloudAccountsAzureResource,
    AsyncCloudAccountsAzureResource,
    CloudAccountsAzureResourceWithRawResponse,
    AsyncCloudAccountsAzureResourceWithRawResponse,
    CloudAccountsAzureResourceWithStreamingResponse,
    AsyncCloudAccountsAzureResourceWithStreamingResponse,
)
from .cloud_accounts_nsx_t import (
    CloudAccountsNsxTResource,
    AsyncCloudAccountsNsxTResource,
    CloudAccountsNsxTResourceWithRawResponse,
    AsyncCloudAccountsNsxTResourceWithRawResponse,
    CloudAccountsNsxTResourceWithStreamingResponse,
    AsyncCloudAccountsNsxTResourceWithStreamingResponse,
)
from .cloud_accounts_nsx_v import (
    CloudAccountsNsxVResource,
    AsyncCloudAccountsNsxVResource,
    CloudAccountsNsxVResourceWithRawResponse,
    AsyncCloudAccountsNsxVResourceWithRawResponse,
    CloudAccountsNsxVResourceWithStreamingResponse,
    AsyncCloudAccountsNsxVResourceWithStreamingResponse,
)
from .storage_profiles_aws import (
    StorageProfilesAwsResource,
    AsyncStorageProfilesAwsResource,
    StorageProfilesAwsResourceWithRawResponse,
    AsyncStorageProfilesAwsResourceWithRawResponse,
    StorageProfilesAwsResourceWithStreamingResponse,
    AsyncStorageProfilesAwsResourceWithStreamingResponse,
)
from .storage_profiles_gcp import (
    StorageProfilesGcpResource,
    AsyncStorageProfilesGcpResource,
    StorageProfilesGcpResourceWithRawResponse,
    AsyncStorageProfilesGcpResourceWithRawResponse,
    StorageProfilesGcpResourceWithStreamingResponse,
    AsyncStorageProfilesGcpResourceWithStreamingResponse,
)
from .cloud_accounts_vsphere import (
    CloudAccountsVsphereResource,
    AsyncCloudAccountsVsphereResource,
    CloudAccountsVsphereResourceWithRawResponse,
    AsyncCloudAccountsVsphereResourceWithRawResponse,
    CloudAccountsVsphereResourceWithStreamingResponse,
    AsyncCloudAccountsVsphereResourceWithStreamingResponse,
)
from .storage_profiles_azure import (
    StorageProfilesAzureResource,
    AsyncStorageProfilesAzureResource,
    StorageProfilesAzureResourceWithRawResponse,
    AsyncStorageProfilesAzureResourceWithRawResponse,
    StorageProfilesAzureResourceWithStreamingResponse,
    AsyncStorageProfilesAzureResourceWithStreamingResponse,
)
from .fabric_networks_vsphere import (
    FabricNetworksVsphereResource,
    AsyncFabricNetworksVsphereResource,
    FabricNetworksVsphereResourceWithRawResponse,
    AsyncFabricNetworksVsphereResourceWithRawResponse,
    FabricNetworksVsphereResourceWithStreamingResponse,
    AsyncFabricNetworksVsphereResourceWithStreamingResponse,
)
from .configuration_properties import (
    ConfigurationPropertiesResource,
    AsyncConfigurationPropertiesResource,
    ConfigurationPropertiesResourceWithRawResponse,
    AsyncConfigurationPropertiesResourceWithRawResponse,
    ConfigurationPropertiesResourceWithStreamingResponse,
    AsyncConfigurationPropertiesResourceWithStreamingResponse,
)
from .storage_profiles_vsphere import (
    StorageProfilesVsphereResource,
    AsyncStorageProfilesVsphereResource,
    StorageProfilesVsphereResourceWithRawResponse,
    AsyncStorageProfilesVsphereResourceWithRawResponse,
    StorageProfilesVsphereResourceWithStreamingResponse,
    AsyncStorageProfilesVsphereResourceWithStreamingResponse,
)
from .compute_nats.compute_nats import (
    ComputeNatsResource,
    AsyncComputeNatsResource,
    ComputeNatsResourceWithRawResponse,
    AsyncComputeNatsResourceWithRawResponse,
    ComputeNatsResourceWithStreamingResponse,
    AsyncComputeNatsResourceWithStreamingResponse,
)
from .fabric_vsphere_datastores import (
    FabricVsphereDatastoresResource,
    AsyncFabricVsphereDatastoresResource,
    FabricVsphereDatastoresResourceWithRawResponse,
    AsyncFabricVsphereDatastoresResourceWithRawResponse,
    FabricVsphereDatastoresResourceWithStreamingResponse,
    AsyncFabricVsphereDatastoresResourceWithStreamingResponse,
)
from .external_network_ip_ranges import (
    ExternalNetworkIPRangesResource,
    AsyncExternalNetworkIPRangesResource,
    ExternalNetworkIPRangesResourceWithRawResponse,
    AsyncExternalNetworkIPRangesResourceWithRawResponse,
    ExternalNetworkIPRangesResourceWithStreamingResponse,
    AsyncExternalNetworkIPRangesResourceWithStreamingResponse,
)
from .block_devices.block_devices import (
    BlockDevicesResource,
    AsyncBlockDevicesResource,
    BlockDevicesResourceWithRawResponse,
    AsyncBlockDevicesResourceWithRawResponse,
    BlockDevicesResourceWithStreamingResponse,
    AsyncBlockDevicesResourceWithStreamingResponse,
)
from .cloud_accounts.cloud_accounts import (
    CloudAccountsResource,
    AsyncCloudAccountsResource,
    CloudAccountsResourceWithRawResponse,
    AsyncCloudAccountsResourceWithRawResponse,
    CloudAccountsResourceWithStreamingResponse,
    AsyncCloudAccountsResourceWithStreamingResponse,
)
from .fabric_azure_storage_accounts import (
    FabricAzureStorageAccountsResource,
    AsyncFabricAzureStorageAccountsResource,
    FabricAzureStorageAccountsResourceWithRawResponse,
    AsyncFabricAzureStorageAccountsResourceWithRawResponse,
    FabricAzureStorageAccountsResourceWithStreamingResponse,
    AsyncFabricAzureStorageAccountsResourceWithStreamingResponse,
)
from .load_balancers.load_balancers import (
    LoadBalancersResource,
    AsyncLoadBalancersResource,
    LoadBalancersResourceWithRawResponse,
    AsyncLoadBalancersResourceWithRawResponse,
    LoadBalancersResourceWithStreamingResponse,
    AsyncLoadBalancersResourceWithStreamingResponse,
)
from .fabric_vsphere_storage_policies import (
    FabricVsphereStoragePoliciesResource,
    AsyncFabricVsphereStoragePoliciesResource,
    FabricVsphereStoragePoliciesResourceWithRawResponse,
    AsyncFabricVsphereStoragePoliciesResourceWithRawResponse,
    FabricVsphereStoragePoliciesResourceWithStreamingResponse,
    AsyncFabricVsphereStoragePoliciesResourceWithStreamingResponse,
)
from .security_groups.security_groups import (
    SecurityGroupsResource,
    AsyncSecurityGroupsResource,
    SecurityGroupsResourceWithRawResponse,
    AsyncSecurityGroupsResourceWithRawResponse,
    SecurityGroupsResourceWithStreamingResponse,
    AsyncSecurityGroupsResourceWithStreamingResponse,
)
from ....types.iaas.api_login_response import APILoginResponse
from .storage_profiles.storage_profiles import (
    StorageProfilesResource,
    AsyncStorageProfilesResource,
    StorageProfilesResourceWithRawResponse,
    AsyncStorageProfilesResourceWithRawResponse,
    StorageProfilesResourceWithStreamingResponse,
    AsyncStorageProfilesResourceWithStreamingResponse,
)
from ....types.iaas.api_retrieve_response import APIRetrieveResponse
from .integrations_ipam.integrations_ipam import (
    IntegrationsIpamResource,
    AsyncIntegrationsIpamResource,
    IntegrationsIpamResourceWithRawResponse,
    AsyncIntegrationsIpamResourceWithRawResponse,
    IntegrationsIpamResourceWithStreamingResponse,
    AsyncIntegrationsIpamResourceWithStreamingResponse,
)
from .network_ip_ranges.network_ip_ranges import (
    NetworkIPRangesResource,
    AsyncNetworkIPRangesResource,
    NetworkIPRangesResourceWithRawResponse,
    AsyncNetworkIPRangesResourceWithRawResponse,
    NetworkIPRangesResourceWithStreamingResponse,
    AsyncNetworkIPRangesResourceWithStreamingResponse,
)
from ....types.iaas.api_retrieve_about_response import APIRetrieveAboutResponse
from ....types.iaas.api_retrieve_images_response import APIRetrieveImagesResponse
from ....types.iaas.api_retrieve_flavors_response import APIRetrieveFlavorsResponse
from ....types.iaas.api_retrieve_folders_response import APIRetrieveFoldersResponse
from ....types.iaas.api_retrieve_event_logs_response import APIRetrieveEventLogsResponse
from ....types.iaas.api_retrieve_request_graph_response import APIRetrieveRequestGraphResponse
from ....types.iaas.api_retrieve_fabric_flavors_response import APIRetrieveFabricFlavorsResponse
from ....types.iaas.api_retrieve_fabric_aws_volume_types_response import APIRetrieveFabricAwsVolumeTypesResponse
from ....types.iaas.api_retrieve_fabric_azure_disk_encryption_sets_response import (
    APIRetrieveFabricAzureDiskEncryptionSetsResponse,
)

__all__ = ["APIResource", "AsyncAPIResource"]


class APIResource(_resource.SyncAPIResource):
    @cached_property
    def storage_profiles(self) -> StorageProfilesResource:
        return StorageProfilesResource(self._client)

    @cached_property
    def projects(self) -> ProjectsResource:
        return ProjectsResource(self._client)

    @cached_property
    def naming(self) -> NamingResource:
        return NamingResource(self._client)

    @cached_property
    def zones(self) -> ZonesResource:
        return ZonesResource(self._client)

    @cached_property
    def tags(self) -> TagsResource:
        return TagsResource(self._client)

    @cached_property
    def storage_profiles_vsphere(self) -> StorageProfilesVsphereResource:
        return StorageProfilesVsphereResource(self._client)

    @cached_property
    def storage_profiles_gcp(self) -> StorageProfilesGcpResource:
        return StorageProfilesGcpResource(self._client)

    @cached_property
    def storage_profiles_azure(self) -> StorageProfilesAzureResource:
        return StorageProfilesAzureResource(self._client)

    @cached_property
    def storage_profiles_aws(self) -> StorageProfilesAwsResource:
        return StorageProfilesAwsResource(self._client)

    @cached_property
    def security_groups(self) -> SecurityGroupsResource:
        return SecurityGroupsResource(self._client)

    @cached_property
    def networks(self) -> NetworksResource:
        return NetworksResource(self._client)

    @cached_property
    def network_profiles(self) -> NetworkProfilesResource:
        return NetworkProfilesResource(self._client)

    @cached_property
    def network_ip_ranges(self) -> NetworkIPRangesResource:
        return NetworkIPRangesResource(self._client)

    @cached_property
    def machines(self) -> MachinesResource:
        return MachinesResource(self._client)

    @cached_property
    def load_balancers(self) -> LoadBalancersResource:
        return LoadBalancersResource(self._client)

    @cached_property
    def integrations_ipam(self) -> IntegrationsIpamResource:
        return IntegrationsIpamResource(self._client)

    @cached_property
    def integrations(self) -> IntegrationsResource:
        return IntegrationsResource(self._client)

    @cached_property
    def image_profiles(self) -> ImageProfilesResource:
        return ImageProfilesResource(self._client)

    @cached_property
    def flavor_profiles(self) -> FlavorProfilesResource:
        return FlavorProfilesResource(self._client)

    @cached_property
    def deployments(self) -> DeploymentsResource:
        return DeploymentsResource(self._client)

    @cached_property
    def data_collectors(self) -> DataCollectorsResource:
        return DataCollectorsResource(self._client)

    @cached_property
    def compute_nats(self) -> ComputeNatsResource:
        return ComputeNatsResource(self._client)

    @cached_property
    def compute_gateways(self) -> ComputeGatewaysResource:
        return ComputeGatewaysResource(self._client)

    @cached_property
    def cloud_accounts(self) -> CloudAccountsResource:
        return CloudAccountsResource(self._client)

    @cached_property
    def cloud_accounts_vsphere(self) -> CloudAccountsVsphereResource:
        return CloudAccountsVsphereResource(self._client)

    @cached_property
    def cloud_accounts_vmc(self) -> CloudAccountsVmcResource:
        return CloudAccountsVmcResource(self._client)

    @cached_property
    def cloud_accounts_vcf(self) -> CloudAccountsVcfResource:
        return CloudAccountsVcfResource(self._client)

    @cached_property
    def cloud_accounts_nsx_v(self) -> CloudAccountsNsxVResource:
        return CloudAccountsNsxVResource(self._client)

    @cached_property
    def cloud_accounts_nsx_t(self) -> CloudAccountsNsxTResource:
        return CloudAccountsNsxTResource(self._client)

    @cached_property
    def cloud_accounts_gcp(self) -> CloudAccountsGcpResource:
        return CloudAccountsGcpResource(self._client)

    @cached_property
    def cloud_accounts_azure(self) -> CloudAccountsAzureResource:
        return CloudAccountsAzureResource(self._client)

    @cached_property
    def cloud_accounts_aws(self) -> CloudAccountsAwsResource:
        return CloudAccountsAwsResource(self._client)

    @cached_property
    def cloud_accounts_avilb(self) -> CloudAccountsAvilbResource:
        return CloudAccountsAvilbResource(self._client)

    @cached_property
    def block_devices(self) -> BlockDevicesResource:
        return BlockDevicesResource(self._client)

    @cached_property
    def fabric_vsphere_datastores(self) -> FabricVsphereDatastoresResource:
        return FabricVsphereDatastoresResource(self._client)

    @cached_property
    def fabric_networks(self) -> FabricNetworksResource:
        return FabricNetworksResource(self._client)

    @cached_property
    def fabric_networks_vsphere(self) -> FabricNetworksVsphereResource:
        return FabricNetworksVsphereResource(self._client)

    @cached_property
    def fabric_computes(self) -> FabricComputesResource:
        return FabricComputesResource(self._client)

    @cached_property
    def external_network_ip_ranges(self) -> ExternalNetworkIPRangesResource:
        return ExternalNetworkIPRangesResource(self._client)

    @cached_property
    def configuration_properties(self) -> ConfigurationPropertiesResource:
        return ConfigurationPropertiesResource(self._client)

    @cached_property
    def request_tracker(self) -> RequestTrackerResource:
        return RequestTrackerResource(self._client)

    @cached_property
    def regions(self) -> RegionsResource:
        return RegionsResource(self._client)

    @cached_property
    def network_domains(self) -> NetworkDomainsResource:
        return NetworkDomainsResource(self._client)

    @cached_property
    def fabric_vsphere_storage_policies(self) -> FabricVsphereStoragePoliciesResource:
        return FabricVsphereStoragePoliciesResource(self._client)

    @cached_property
    def fabric_images(self) -> FabricImagesResource:
        return FabricImagesResource(self._client)

    @cached_property
    def fabric_azure_storage_accounts(self) -> FabricAzureStorageAccountsResource:
        return FabricAzureStorageAccountsResource(self._client)

    @cached_property
    def external_ip_blocks(self) -> ExternalIPBlocksResource:
        return ExternalIPBlocksResource(self._client)

    @cached_property
    def with_raw_response(self) -> APIResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#accessing-raw-response-data-eg-headers
        """
        return APIResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> APIResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#with_streaming_response
        """
        return APIResourceWithStreamingResponse(self)

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
    ) -> APIRetrieveResponse:
        """
        Get certificate info

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
            f"/iaas/api/certificates/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"api_version": api_version}, api_retrieve_params.APIRetrieveParams),
            ),
            cast_to=APIRetrieveResponse,
        )

    def login(
        self,
        *,
        refresh_token: str,
        api_version: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> APILoginResponse:
        """Retrieve AuthToken for local csp users.

        When accessing other endpoints the
        `Bearer` authentication scheme and the received `token` must be provided in the
        `Authorization` request header field as follows: `Authorization: Bearer {token}`

        Args:
          refresh_token: Refresh token obtained from the UI

          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/iaas/api/login",
            body=maybe_transform({"refresh_token": refresh_token}, api_login_params.APILoginParams),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"api_version": api_version}, api_login_params.APILoginParams),
            ),
            cast_to=APILoginResponse,
        )

    def retrieve_about(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> APIRetrieveAboutResponse:
        """
        The page contains information about the supported API versions and the latest
        API version. The version parameter is mandatory for endpoints introduced after
        version 2019-01-15and optional for the rest though highly recommended. If you do
        not specify explicitly an exact version, you will be calling the latest
        supported General Availability API version. Here is an example of a call which
        specifies the exact version you are using:
        `GET /iaas/api/network-profiles?apiVersion=2021-07-15`

        Note that this version is deprecated: 2019-01-15.
        """
        return self._get(
            "/iaas/api/about",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=APIRetrieveAboutResponse,
        )

    def retrieve_event_logs(
        self,
        *,
        count: bool | Omit = omit,
        filter: str | Omit = omit,
        select: str | Omit = omit,
        skip: int | Omit = omit,
        top: int | Omit = omit,
        api_version: str | Omit = omit,
        end_date: str | Omit = omit,
        start_date: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> APIRetrieveEventLogsResponse:
        """
        Get all Event logs

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

          end_date: End Date e.g. 2020-12-01T08:00:00.000Z

          start_date: Start Date e.g. 2020-12-01T08:00:00.000Z

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/iaas/api/event-logs",
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
                        "end_date": end_date,
                        "start_date": start_date,
                    },
                    api_retrieve_event_logs_params.APIRetrieveEventLogsParams,
                ),
            ),
            cast_to=APIRetrieveEventLogsResponse,
        )

    def retrieve_fabric_aws_volume_types(
        self,
        *,
        api_version: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> APIRetrieveFabricAwsVolumeTypesResponse:
        """
        Get all fabric AWS volume types.

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/iaas/api/fabric-aws-volume-types",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"api_version": api_version},
                    api_retrieve_fabric_aws_volume_types_params.APIRetrieveFabricAwsVolumeTypesParams,
                ),
            ),
            cast_to=APIRetrieveFabricAwsVolumeTypesResponse,
        )

    def retrieve_fabric_azure_disk_encryption_sets(
        self,
        *,
        region_id: str,
        api_version: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> APIRetrieveFabricAzureDiskEncryptionSetsResponse:
        """
        Get all Azure disk encryption sets

        Args:
          region_id: Region id

          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/iaas/api/fabric-azure-disk-encryption-sets",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "region_id": region_id,
                        "api_version": api_version,
                    },
                    api_retrieve_fabric_azure_disk_encryption_sets_params.APIRetrieveFabricAzureDiskEncryptionSetsParams,
                ),
            ),
            cast_to=APIRetrieveFabricAzureDiskEncryptionSetsResponse,
        )

    def retrieve_fabric_flavors(
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
    ) -> APIRetrieveFabricFlavorsResponse:
        """
        Get all fabric flavors

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
            "/iaas/api/fabric-flavors",
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
                    api_retrieve_fabric_flavors_params.APIRetrieveFabricFlavorsParams,
                ),
            ),
            cast_to=APIRetrieveFabricFlavorsResponse,
        )

    def retrieve_flavors(
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
    ) -> APIRetrieveFlavorsResponse:
        """
        Get all flavors defined in FlavorProfile

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
            "/iaas/api/flavors",
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
                    api_retrieve_flavors_params.APIRetrieveFlavorsParams,
                ),
            ),
            cast_to=APIRetrieveFlavorsResponse,
        )

    def retrieve_folders(
        self,
        *,
        api_version: str,
        count: bool | Omit = omit,
        filter: str | Omit = omit,
        select: str | Omit = omit,
        skip: int | Omit = omit,
        top: int | Omit = omit,
        cloud_account_id: str | Omit = omit,
        external_region_id: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> APIRetrieveFoldersResponse:
        """
        Get all folders within the current organization

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

          cloud_account_id: The ID of a vcenter cloud account.

          external_region_id: The external unique identifier of the region associated with the vcenter cloud
              account.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/iaas/api/folders",
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
                        "cloud_account_id": cloud_account_id,
                        "external_region_id": external_region_id,
                    },
                    api_retrieve_folders_params.APIRetrieveFoldersParams,
                ),
            ),
            cast_to=APIRetrieveFoldersResponse,
        )

    def retrieve_images(
        self,
        *,
        api_version: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> APIRetrieveImagesResponse:
        """Get all images defined in ImageProfile.

        To get all enumerated images use Fabric
        Image endpoint.

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/iaas/api/images",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"api_version": api_version}, api_retrieve_images_params.APIRetrieveImagesParams),
            ),
            cast_to=APIRetrieveImagesResponse,
        )

    def retrieve_request_graph(
        self,
        *,
        deployment_id: str,
        flow_id: str,
        api_version: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> APIRetrieveRequestGraphResponse:
        """
        Get Request Graph For Provisioning Request

        Args:
          deployment_id: Deployment Id For Provisioning Request

          flow_id: Flow Id For Provisioning Request

          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/iaas/api/request-graph",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "deployment_id": deployment_id,
                        "flow_id": flow_id,
                        "api_version": api_version,
                    },
                    api_retrieve_request_graph_params.APIRetrieveRequestGraphParams,
                ),
            ),
            cast_to=APIRetrieveRequestGraphResponse,
        )


class AsyncAPIResource(_resource.AsyncAPIResource):
    @cached_property
    def storage_profiles(self) -> AsyncStorageProfilesResource:
        return AsyncStorageProfilesResource(self._client)

    @cached_property
    def projects(self) -> AsyncProjectsResource:
        return AsyncProjectsResource(self._client)

    @cached_property
    def naming(self) -> AsyncNamingResource:
        return AsyncNamingResource(self._client)

    @cached_property
    def zones(self) -> AsyncZonesResource:
        return AsyncZonesResource(self._client)

    @cached_property
    def tags(self) -> AsyncTagsResource:
        return AsyncTagsResource(self._client)

    @cached_property
    def storage_profiles_vsphere(self) -> AsyncStorageProfilesVsphereResource:
        return AsyncStorageProfilesVsphereResource(self._client)

    @cached_property
    def storage_profiles_gcp(self) -> AsyncStorageProfilesGcpResource:
        return AsyncStorageProfilesGcpResource(self._client)

    @cached_property
    def storage_profiles_azure(self) -> AsyncStorageProfilesAzureResource:
        return AsyncStorageProfilesAzureResource(self._client)

    @cached_property
    def storage_profiles_aws(self) -> AsyncStorageProfilesAwsResource:
        return AsyncStorageProfilesAwsResource(self._client)

    @cached_property
    def security_groups(self) -> AsyncSecurityGroupsResource:
        return AsyncSecurityGroupsResource(self._client)

    @cached_property
    def networks(self) -> AsyncNetworksResource:
        return AsyncNetworksResource(self._client)

    @cached_property
    def network_profiles(self) -> AsyncNetworkProfilesResource:
        return AsyncNetworkProfilesResource(self._client)

    @cached_property
    def network_ip_ranges(self) -> AsyncNetworkIPRangesResource:
        return AsyncNetworkIPRangesResource(self._client)

    @cached_property
    def machines(self) -> AsyncMachinesResource:
        return AsyncMachinesResource(self._client)

    @cached_property
    def load_balancers(self) -> AsyncLoadBalancersResource:
        return AsyncLoadBalancersResource(self._client)

    @cached_property
    def integrations_ipam(self) -> AsyncIntegrationsIpamResource:
        return AsyncIntegrationsIpamResource(self._client)

    @cached_property
    def integrations(self) -> AsyncIntegrationsResource:
        return AsyncIntegrationsResource(self._client)

    @cached_property
    def image_profiles(self) -> AsyncImageProfilesResource:
        return AsyncImageProfilesResource(self._client)

    @cached_property
    def flavor_profiles(self) -> AsyncFlavorProfilesResource:
        return AsyncFlavorProfilesResource(self._client)

    @cached_property
    def deployments(self) -> AsyncDeploymentsResource:
        return AsyncDeploymentsResource(self._client)

    @cached_property
    def data_collectors(self) -> AsyncDataCollectorsResource:
        return AsyncDataCollectorsResource(self._client)

    @cached_property
    def compute_nats(self) -> AsyncComputeNatsResource:
        return AsyncComputeNatsResource(self._client)

    @cached_property
    def compute_gateways(self) -> AsyncComputeGatewaysResource:
        return AsyncComputeGatewaysResource(self._client)

    @cached_property
    def cloud_accounts(self) -> AsyncCloudAccountsResource:
        return AsyncCloudAccountsResource(self._client)

    @cached_property
    def cloud_accounts_vsphere(self) -> AsyncCloudAccountsVsphereResource:
        return AsyncCloudAccountsVsphereResource(self._client)

    @cached_property
    def cloud_accounts_vmc(self) -> AsyncCloudAccountsVmcResource:
        return AsyncCloudAccountsVmcResource(self._client)

    @cached_property
    def cloud_accounts_vcf(self) -> AsyncCloudAccountsVcfResource:
        return AsyncCloudAccountsVcfResource(self._client)

    @cached_property
    def cloud_accounts_nsx_v(self) -> AsyncCloudAccountsNsxVResource:
        return AsyncCloudAccountsNsxVResource(self._client)

    @cached_property
    def cloud_accounts_nsx_t(self) -> AsyncCloudAccountsNsxTResource:
        return AsyncCloudAccountsNsxTResource(self._client)

    @cached_property
    def cloud_accounts_gcp(self) -> AsyncCloudAccountsGcpResource:
        return AsyncCloudAccountsGcpResource(self._client)

    @cached_property
    def cloud_accounts_azure(self) -> AsyncCloudAccountsAzureResource:
        return AsyncCloudAccountsAzureResource(self._client)

    @cached_property
    def cloud_accounts_aws(self) -> AsyncCloudAccountsAwsResource:
        return AsyncCloudAccountsAwsResource(self._client)

    @cached_property
    def cloud_accounts_avilb(self) -> AsyncCloudAccountsAvilbResource:
        return AsyncCloudAccountsAvilbResource(self._client)

    @cached_property
    def block_devices(self) -> AsyncBlockDevicesResource:
        return AsyncBlockDevicesResource(self._client)

    @cached_property
    def fabric_vsphere_datastores(self) -> AsyncFabricVsphereDatastoresResource:
        return AsyncFabricVsphereDatastoresResource(self._client)

    @cached_property
    def fabric_networks(self) -> AsyncFabricNetworksResource:
        return AsyncFabricNetworksResource(self._client)

    @cached_property
    def fabric_networks_vsphere(self) -> AsyncFabricNetworksVsphereResource:
        return AsyncFabricNetworksVsphereResource(self._client)

    @cached_property
    def fabric_computes(self) -> AsyncFabricComputesResource:
        return AsyncFabricComputesResource(self._client)

    @cached_property
    def external_network_ip_ranges(self) -> AsyncExternalNetworkIPRangesResource:
        return AsyncExternalNetworkIPRangesResource(self._client)

    @cached_property
    def configuration_properties(self) -> AsyncConfigurationPropertiesResource:
        return AsyncConfigurationPropertiesResource(self._client)

    @cached_property
    def request_tracker(self) -> AsyncRequestTrackerResource:
        return AsyncRequestTrackerResource(self._client)

    @cached_property
    def regions(self) -> AsyncRegionsResource:
        return AsyncRegionsResource(self._client)

    @cached_property
    def network_domains(self) -> AsyncNetworkDomainsResource:
        return AsyncNetworkDomainsResource(self._client)

    @cached_property
    def fabric_vsphere_storage_policies(self) -> AsyncFabricVsphereStoragePoliciesResource:
        return AsyncFabricVsphereStoragePoliciesResource(self._client)

    @cached_property
    def fabric_images(self) -> AsyncFabricImagesResource:
        return AsyncFabricImagesResource(self._client)

    @cached_property
    def fabric_azure_storage_accounts(self) -> AsyncFabricAzureStorageAccountsResource:
        return AsyncFabricAzureStorageAccountsResource(self._client)

    @cached_property
    def external_ip_blocks(self) -> AsyncExternalIPBlocksResource:
        return AsyncExternalIPBlocksResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncAPIResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#accessing-raw-response-data-eg-headers
        """
        return AsyncAPIResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncAPIResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#with_streaming_response
        """
        return AsyncAPIResourceWithStreamingResponse(self)

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
    ) -> APIRetrieveResponse:
        """
        Get certificate info

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
            f"/iaas/api/certificates/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform({"api_version": api_version}, api_retrieve_params.APIRetrieveParams),
            ),
            cast_to=APIRetrieveResponse,
        )

    async def login(
        self,
        *,
        refresh_token: str,
        api_version: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> APILoginResponse:
        """Retrieve AuthToken for local csp users.

        When accessing other endpoints the
        `Bearer` authentication scheme and the received `token` must be provided in the
        `Authorization` request header field as follows: `Authorization: Bearer {token}`

        Args:
          refresh_token: Refresh token obtained from the UI

          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/iaas/api/login",
            body=await async_maybe_transform({"refresh_token": refresh_token}, api_login_params.APILoginParams),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform({"api_version": api_version}, api_login_params.APILoginParams),
            ),
            cast_to=APILoginResponse,
        )

    async def retrieve_about(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> APIRetrieveAboutResponse:
        """
        The page contains information about the supported API versions and the latest
        API version. The version parameter is mandatory for endpoints introduced after
        version 2019-01-15and optional for the rest though highly recommended. If you do
        not specify explicitly an exact version, you will be calling the latest
        supported General Availability API version. Here is an example of a call which
        specifies the exact version you are using:
        `GET /iaas/api/network-profiles?apiVersion=2021-07-15`

        Note that this version is deprecated: 2019-01-15.
        """
        return await self._get(
            "/iaas/api/about",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=APIRetrieveAboutResponse,
        )

    async def retrieve_event_logs(
        self,
        *,
        count: bool | Omit = omit,
        filter: str | Omit = omit,
        select: str | Omit = omit,
        skip: int | Omit = omit,
        top: int | Omit = omit,
        api_version: str | Omit = omit,
        end_date: str | Omit = omit,
        start_date: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> APIRetrieveEventLogsResponse:
        """
        Get all Event logs

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

          end_date: End Date e.g. 2020-12-01T08:00:00.000Z

          start_date: Start Date e.g. 2020-12-01T08:00:00.000Z

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/iaas/api/event-logs",
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
                        "end_date": end_date,
                        "start_date": start_date,
                    },
                    api_retrieve_event_logs_params.APIRetrieveEventLogsParams,
                ),
            ),
            cast_to=APIRetrieveEventLogsResponse,
        )

    async def retrieve_fabric_aws_volume_types(
        self,
        *,
        api_version: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> APIRetrieveFabricAwsVolumeTypesResponse:
        """
        Get all fabric AWS volume types.

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/iaas/api/fabric-aws-volume-types",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"api_version": api_version},
                    api_retrieve_fabric_aws_volume_types_params.APIRetrieveFabricAwsVolumeTypesParams,
                ),
            ),
            cast_to=APIRetrieveFabricAwsVolumeTypesResponse,
        )

    async def retrieve_fabric_azure_disk_encryption_sets(
        self,
        *,
        region_id: str,
        api_version: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> APIRetrieveFabricAzureDiskEncryptionSetsResponse:
        """
        Get all Azure disk encryption sets

        Args:
          region_id: Region id

          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/iaas/api/fabric-azure-disk-encryption-sets",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "region_id": region_id,
                        "api_version": api_version,
                    },
                    api_retrieve_fabric_azure_disk_encryption_sets_params.APIRetrieveFabricAzureDiskEncryptionSetsParams,
                ),
            ),
            cast_to=APIRetrieveFabricAzureDiskEncryptionSetsResponse,
        )

    async def retrieve_fabric_flavors(
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
    ) -> APIRetrieveFabricFlavorsResponse:
        """
        Get all fabric flavors

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
            "/iaas/api/fabric-flavors",
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
                    api_retrieve_fabric_flavors_params.APIRetrieveFabricFlavorsParams,
                ),
            ),
            cast_to=APIRetrieveFabricFlavorsResponse,
        )

    async def retrieve_flavors(
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
    ) -> APIRetrieveFlavorsResponse:
        """
        Get all flavors defined in FlavorProfile

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
            "/iaas/api/flavors",
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
                    api_retrieve_flavors_params.APIRetrieveFlavorsParams,
                ),
            ),
            cast_to=APIRetrieveFlavorsResponse,
        )

    async def retrieve_folders(
        self,
        *,
        api_version: str,
        count: bool | Omit = omit,
        filter: str | Omit = omit,
        select: str | Omit = omit,
        skip: int | Omit = omit,
        top: int | Omit = omit,
        cloud_account_id: str | Omit = omit,
        external_region_id: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> APIRetrieveFoldersResponse:
        """
        Get all folders within the current organization

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

          cloud_account_id: The ID of a vcenter cloud account.

          external_region_id: The external unique identifier of the region associated with the vcenter cloud
              account.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/iaas/api/folders",
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
                        "cloud_account_id": cloud_account_id,
                        "external_region_id": external_region_id,
                    },
                    api_retrieve_folders_params.APIRetrieveFoldersParams,
                ),
            ),
            cast_to=APIRetrieveFoldersResponse,
        )

    async def retrieve_images(
        self,
        *,
        api_version: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> APIRetrieveImagesResponse:
        """Get all images defined in ImageProfile.

        To get all enumerated images use Fabric
        Image endpoint.

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/iaas/api/images",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"api_version": api_version}, api_retrieve_images_params.APIRetrieveImagesParams
                ),
            ),
            cast_to=APIRetrieveImagesResponse,
        )

    async def retrieve_request_graph(
        self,
        *,
        deployment_id: str,
        flow_id: str,
        api_version: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> APIRetrieveRequestGraphResponse:
        """
        Get Request Graph For Provisioning Request

        Args:
          deployment_id: Deployment Id For Provisioning Request

          flow_id: Flow Id For Provisioning Request

          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/iaas/api/request-graph",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "deployment_id": deployment_id,
                        "flow_id": flow_id,
                        "api_version": api_version,
                    },
                    api_retrieve_request_graph_params.APIRetrieveRequestGraphParams,
                ),
            ),
            cast_to=APIRetrieveRequestGraphResponse,
        )


class APIResourceWithRawResponse:
    def __init__(self, api: APIResource) -> None:
        self._api = api

        self.retrieve = to_raw_response_wrapper(
            api.retrieve,
        )
        self.login = to_raw_response_wrapper(
            api.login,
        )
        self.retrieve_about = to_raw_response_wrapper(
            api.retrieve_about,
        )
        self.retrieve_event_logs = to_raw_response_wrapper(
            api.retrieve_event_logs,
        )
        self.retrieve_fabric_aws_volume_types = to_raw_response_wrapper(
            api.retrieve_fabric_aws_volume_types,
        )
        self.retrieve_fabric_azure_disk_encryption_sets = to_raw_response_wrapper(
            api.retrieve_fabric_azure_disk_encryption_sets,
        )
        self.retrieve_fabric_flavors = to_raw_response_wrapper(
            api.retrieve_fabric_flavors,
        )
        self.retrieve_flavors = to_raw_response_wrapper(
            api.retrieve_flavors,
        )
        self.retrieve_folders = to_raw_response_wrapper(
            api.retrieve_folders,
        )
        self.retrieve_images = to_raw_response_wrapper(
            api.retrieve_images,
        )
        self.retrieve_request_graph = to_raw_response_wrapper(
            api.retrieve_request_graph,
        )

    @cached_property
    def storage_profiles(self) -> StorageProfilesResourceWithRawResponse:
        return StorageProfilesResourceWithRawResponse(self._api.storage_profiles)

    @cached_property
    def projects(self) -> ProjectsResourceWithRawResponse:
        return ProjectsResourceWithRawResponse(self._api.projects)

    @cached_property
    def naming(self) -> NamingResourceWithRawResponse:
        return NamingResourceWithRawResponse(self._api.naming)

    @cached_property
    def zones(self) -> ZonesResourceWithRawResponse:
        return ZonesResourceWithRawResponse(self._api.zones)

    @cached_property
    def tags(self) -> TagsResourceWithRawResponse:
        return TagsResourceWithRawResponse(self._api.tags)

    @cached_property
    def storage_profiles_vsphere(self) -> StorageProfilesVsphereResourceWithRawResponse:
        return StorageProfilesVsphereResourceWithRawResponse(self._api.storage_profiles_vsphere)

    @cached_property
    def storage_profiles_gcp(self) -> StorageProfilesGcpResourceWithRawResponse:
        return StorageProfilesGcpResourceWithRawResponse(self._api.storage_profiles_gcp)

    @cached_property
    def storage_profiles_azure(self) -> StorageProfilesAzureResourceWithRawResponse:
        return StorageProfilesAzureResourceWithRawResponse(self._api.storage_profiles_azure)

    @cached_property
    def storage_profiles_aws(self) -> StorageProfilesAwsResourceWithRawResponse:
        return StorageProfilesAwsResourceWithRawResponse(self._api.storage_profiles_aws)

    @cached_property
    def security_groups(self) -> SecurityGroupsResourceWithRawResponse:
        return SecurityGroupsResourceWithRawResponse(self._api.security_groups)

    @cached_property
    def networks(self) -> NetworksResourceWithRawResponse:
        return NetworksResourceWithRawResponse(self._api.networks)

    @cached_property
    def network_profiles(self) -> NetworkProfilesResourceWithRawResponse:
        return NetworkProfilesResourceWithRawResponse(self._api.network_profiles)

    @cached_property
    def network_ip_ranges(self) -> NetworkIPRangesResourceWithRawResponse:
        return NetworkIPRangesResourceWithRawResponse(self._api.network_ip_ranges)

    @cached_property
    def machines(self) -> MachinesResourceWithRawResponse:
        return MachinesResourceWithRawResponse(self._api.machines)

    @cached_property
    def load_balancers(self) -> LoadBalancersResourceWithRawResponse:
        return LoadBalancersResourceWithRawResponse(self._api.load_balancers)

    @cached_property
    def integrations_ipam(self) -> IntegrationsIpamResourceWithRawResponse:
        return IntegrationsIpamResourceWithRawResponse(self._api.integrations_ipam)

    @cached_property
    def integrations(self) -> IntegrationsResourceWithRawResponse:
        return IntegrationsResourceWithRawResponse(self._api.integrations)

    @cached_property
    def image_profiles(self) -> ImageProfilesResourceWithRawResponse:
        return ImageProfilesResourceWithRawResponse(self._api.image_profiles)

    @cached_property
    def flavor_profiles(self) -> FlavorProfilesResourceWithRawResponse:
        return FlavorProfilesResourceWithRawResponse(self._api.flavor_profiles)

    @cached_property
    def deployments(self) -> DeploymentsResourceWithRawResponse:
        return DeploymentsResourceWithRawResponse(self._api.deployments)

    @cached_property
    def data_collectors(self) -> DataCollectorsResourceWithRawResponse:
        return DataCollectorsResourceWithRawResponse(self._api.data_collectors)

    @cached_property
    def compute_nats(self) -> ComputeNatsResourceWithRawResponse:
        return ComputeNatsResourceWithRawResponse(self._api.compute_nats)

    @cached_property
    def compute_gateways(self) -> ComputeGatewaysResourceWithRawResponse:
        return ComputeGatewaysResourceWithRawResponse(self._api.compute_gateways)

    @cached_property
    def cloud_accounts(self) -> CloudAccountsResourceWithRawResponse:
        return CloudAccountsResourceWithRawResponse(self._api.cloud_accounts)

    @cached_property
    def cloud_accounts_vsphere(self) -> CloudAccountsVsphereResourceWithRawResponse:
        return CloudAccountsVsphereResourceWithRawResponse(self._api.cloud_accounts_vsphere)

    @cached_property
    def cloud_accounts_vmc(self) -> CloudAccountsVmcResourceWithRawResponse:
        return CloudAccountsVmcResourceWithRawResponse(self._api.cloud_accounts_vmc)

    @cached_property
    def cloud_accounts_vcf(self) -> CloudAccountsVcfResourceWithRawResponse:
        return CloudAccountsVcfResourceWithRawResponse(self._api.cloud_accounts_vcf)

    @cached_property
    def cloud_accounts_nsx_v(self) -> CloudAccountsNsxVResourceWithRawResponse:
        return CloudAccountsNsxVResourceWithRawResponse(self._api.cloud_accounts_nsx_v)

    @cached_property
    def cloud_accounts_nsx_t(self) -> CloudAccountsNsxTResourceWithRawResponse:
        return CloudAccountsNsxTResourceWithRawResponse(self._api.cloud_accounts_nsx_t)

    @cached_property
    def cloud_accounts_gcp(self) -> CloudAccountsGcpResourceWithRawResponse:
        return CloudAccountsGcpResourceWithRawResponse(self._api.cloud_accounts_gcp)

    @cached_property
    def cloud_accounts_azure(self) -> CloudAccountsAzureResourceWithRawResponse:
        return CloudAccountsAzureResourceWithRawResponse(self._api.cloud_accounts_azure)

    @cached_property
    def cloud_accounts_aws(self) -> CloudAccountsAwsResourceWithRawResponse:
        return CloudAccountsAwsResourceWithRawResponse(self._api.cloud_accounts_aws)

    @cached_property
    def cloud_accounts_avilb(self) -> CloudAccountsAvilbResourceWithRawResponse:
        return CloudAccountsAvilbResourceWithRawResponse(self._api.cloud_accounts_avilb)

    @cached_property
    def block_devices(self) -> BlockDevicesResourceWithRawResponse:
        return BlockDevicesResourceWithRawResponse(self._api.block_devices)

    @cached_property
    def fabric_vsphere_datastores(self) -> FabricVsphereDatastoresResourceWithRawResponse:
        return FabricVsphereDatastoresResourceWithRawResponse(self._api.fabric_vsphere_datastores)

    @cached_property
    def fabric_networks(self) -> FabricNetworksResourceWithRawResponse:
        return FabricNetworksResourceWithRawResponse(self._api.fabric_networks)

    @cached_property
    def fabric_networks_vsphere(self) -> FabricNetworksVsphereResourceWithRawResponse:
        return FabricNetworksVsphereResourceWithRawResponse(self._api.fabric_networks_vsphere)

    @cached_property
    def fabric_computes(self) -> FabricComputesResourceWithRawResponse:
        return FabricComputesResourceWithRawResponse(self._api.fabric_computes)

    @cached_property
    def external_network_ip_ranges(self) -> ExternalNetworkIPRangesResourceWithRawResponse:
        return ExternalNetworkIPRangesResourceWithRawResponse(self._api.external_network_ip_ranges)

    @cached_property
    def configuration_properties(self) -> ConfigurationPropertiesResourceWithRawResponse:
        return ConfigurationPropertiesResourceWithRawResponse(self._api.configuration_properties)

    @cached_property
    def request_tracker(self) -> RequestTrackerResourceWithRawResponse:
        return RequestTrackerResourceWithRawResponse(self._api.request_tracker)

    @cached_property
    def regions(self) -> RegionsResourceWithRawResponse:
        return RegionsResourceWithRawResponse(self._api.regions)

    @cached_property
    def network_domains(self) -> NetworkDomainsResourceWithRawResponse:
        return NetworkDomainsResourceWithRawResponse(self._api.network_domains)

    @cached_property
    def fabric_vsphere_storage_policies(self) -> FabricVsphereStoragePoliciesResourceWithRawResponse:
        return FabricVsphereStoragePoliciesResourceWithRawResponse(self._api.fabric_vsphere_storage_policies)

    @cached_property
    def fabric_images(self) -> FabricImagesResourceWithRawResponse:
        return FabricImagesResourceWithRawResponse(self._api.fabric_images)

    @cached_property
    def fabric_azure_storage_accounts(self) -> FabricAzureStorageAccountsResourceWithRawResponse:
        return FabricAzureStorageAccountsResourceWithRawResponse(self._api.fabric_azure_storage_accounts)

    @cached_property
    def external_ip_blocks(self) -> ExternalIPBlocksResourceWithRawResponse:
        return ExternalIPBlocksResourceWithRawResponse(self._api.external_ip_blocks)


class AsyncAPIResourceWithRawResponse:
    def __init__(self, api: AsyncAPIResource) -> None:
        self._api = api

        self.retrieve = async_to_raw_response_wrapper(
            api.retrieve,
        )
        self.login = async_to_raw_response_wrapper(
            api.login,
        )
        self.retrieve_about = async_to_raw_response_wrapper(
            api.retrieve_about,
        )
        self.retrieve_event_logs = async_to_raw_response_wrapper(
            api.retrieve_event_logs,
        )
        self.retrieve_fabric_aws_volume_types = async_to_raw_response_wrapper(
            api.retrieve_fabric_aws_volume_types,
        )
        self.retrieve_fabric_azure_disk_encryption_sets = async_to_raw_response_wrapper(
            api.retrieve_fabric_azure_disk_encryption_sets,
        )
        self.retrieve_fabric_flavors = async_to_raw_response_wrapper(
            api.retrieve_fabric_flavors,
        )
        self.retrieve_flavors = async_to_raw_response_wrapper(
            api.retrieve_flavors,
        )
        self.retrieve_folders = async_to_raw_response_wrapper(
            api.retrieve_folders,
        )
        self.retrieve_images = async_to_raw_response_wrapper(
            api.retrieve_images,
        )
        self.retrieve_request_graph = async_to_raw_response_wrapper(
            api.retrieve_request_graph,
        )

    @cached_property
    def storage_profiles(self) -> AsyncStorageProfilesResourceWithRawResponse:
        return AsyncStorageProfilesResourceWithRawResponse(self._api.storage_profiles)

    @cached_property
    def projects(self) -> AsyncProjectsResourceWithRawResponse:
        return AsyncProjectsResourceWithRawResponse(self._api.projects)

    @cached_property
    def naming(self) -> AsyncNamingResourceWithRawResponse:
        return AsyncNamingResourceWithRawResponse(self._api.naming)

    @cached_property
    def zones(self) -> AsyncZonesResourceWithRawResponse:
        return AsyncZonesResourceWithRawResponse(self._api.zones)

    @cached_property
    def tags(self) -> AsyncTagsResourceWithRawResponse:
        return AsyncTagsResourceWithRawResponse(self._api.tags)

    @cached_property
    def storage_profiles_vsphere(self) -> AsyncStorageProfilesVsphereResourceWithRawResponse:
        return AsyncStorageProfilesVsphereResourceWithRawResponse(self._api.storage_profiles_vsphere)

    @cached_property
    def storage_profiles_gcp(self) -> AsyncStorageProfilesGcpResourceWithRawResponse:
        return AsyncStorageProfilesGcpResourceWithRawResponse(self._api.storage_profiles_gcp)

    @cached_property
    def storage_profiles_azure(self) -> AsyncStorageProfilesAzureResourceWithRawResponse:
        return AsyncStorageProfilesAzureResourceWithRawResponse(self._api.storage_profiles_azure)

    @cached_property
    def storage_profiles_aws(self) -> AsyncStorageProfilesAwsResourceWithRawResponse:
        return AsyncStorageProfilesAwsResourceWithRawResponse(self._api.storage_profiles_aws)

    @cached_property
    def security_groups(self) -> AsyncSecurityGroupsResourceWithRawResponse:
        return AsyncSecurityGroupsResourceWithRawResponse(self._api.security_groups)

    @cached_property
    def networks(self) -> AsyncNetworksResourceWithRawResponse:
        return AsyncNetworksResourceWithRawResponse(self._api.networks)

    @cached_property
    def network_profiles(self) -> AsyncNetworkProfilesResourceWithRawResponse:
        return AsyncNetworkProfilesResourceWithRawResponse(self._api.network_profiles)

    @cached_property
    def network_ip_ranges(self) -> AsyncNetworkIPRangesResourceWithRawResponse:
        return AsyncNetworkIPRangesResourceWithRawResponse(self._api.network_ip_ranges)

    @cached_property
    def machines(self) -> AsyncMachinesResourceWithRawResponse:
        return AsyncMachinesResourceWithRawResponse(self._api.machines)

    @cached_property
    def load_balancers(self) -> AsyncLoadBalancersResourceWithRawResponse:
        return AsyncLoadBalancersResourceWithRawResponse(self._api.load_balancers)

    @cached_property
    def integrations_ipam(self) -> AsyncIntegrationsIpamResourceWithRawResponse:
        return AsyncIntegrationsIpamResourceWithRawResponse(self._api.integrations_ipam)

    @cached_property
    def integrations(self) -> AsyncIntegrationsResourceWithRawResponse:
        return AsyncIntegrationsResourceWithRawResponse(self._api.integrations)

    @cached_property
    def image_profiles(self) -> AsyncImageProfilesResourceWithRawResponse:
        return AsyncImageProfilesResourceWithRawResponse(self._api.image_profiles)

    @cached_property
    def flavor_profiles(self) -> AsyncFlavorProfilesResourceWithRawResponse:
        return AsyncFlavorProfilesResourceWithRawResponse(self._api.flavor_profiles)

    @cached_property
    def deployments(self) -> AsyncDeploymentsResourceWithRawResponse:
        return AsyncDeploymentsResourceWithRawResponse(self._api.deployments)

    @cached_property
    def data_collectors(self) -> AsyncDataCollectorsResourceWithRawResponse:
        return AsyncDataCollectorsResourceWithRawResponse(self._api.data_collectors)

    @cached_property
    def compute_nats(self) -> AsyncComputeNatsResourceWithRawResponse:
        return AsyncComputeNatsResourceWithRawResponse(self._api.compute_nats)

    @cached_property
    def compute_gateways(self) -> AsyncComputeGatewaysResourceWithRawResponse:
        return AsyncComputeGatewaysResourceWithRawResponse(self._api.compute_gateways)

    @cached_property
    def cloud_accounts(self) -> AsyncCloudAccountsResourceWithRawResponse:
        return AsyncCloudAccountsResourceWithRawResponse(self._api.cloud_accounts)

    @cached_property
    def cloud_accounts_vsphere(self) -> AsyncCloudAccountsVsphereResourceWithRawResponse:
        return AsyncCloudAccountsVsphereResourceWithRawResponse(self._api.cloud_accounts_vsphere)

    @cached_property
    def cloud_accounts_vmc(self) -> AsyncCloudAccountsVmcResourceWithRawResponse:
        return AsyncCloudAccountsVmcResourceWithRawResponse(self._api.cloud_accounts_vmc)

    @cached_property
    def cloud_accounts_vcf(self) -> AsyncCloudAccountsVcfResourceWithRawResponse:
        return AsyncCloudAccountsVcfResourceWithRawResponse(self._api.cloud_accounts_vcf)

    @cached_property
    def cloud_accounts_nsx_v(self) -> AsyncCloudAccountsNsxVResourceWithRawResponse:
        return AsyncCloudAccountsNsxVResourceWithRawResponse(self._api.cloud_accounts_nsx_v)

    @cached_property
    def cloud_accounts_nsx_t(self) -> AsyncCloudAccountsNsxTResourceWithRawResponse:
        return AsyncCloudAccountsNsxTResourceWithRawResponse(self._api.cloud_accounts_nsx_t)

    @cached_property
    def cloud_accounts_gcp(self) -> AsyncCloudAccountsGcpResourceWithRawResponse:
        return AsyncCloudAccountsGcpResourceWithRawResponse(self._api.cloud_accounts_gcp)

    @cached_property
    def cloud_accounts_azure(self) -> AsyncCloudAccountsAzureResourceWithRawResponse:
        return AsyncCloudAccountsAzureResourceWithRawResponse(self._api.cloud_accounts_azure)

    @cached_property
    def cloud_accounts_aws(self) -> AsyncCloudAccountsAwsResourceWithRawResponse:
        return AsyncCloudAccountsAwsResourceWithRawResponse(self._api.cloud_accounts_aws)

    @cached_property
    def cloud_accounts_avilb(self) -> AsyncCloudAccountsAvilbResourceWithRawResponse:
        return AsyncCloudAccountsAvilbResourceWithRawResponse(self._api.cloud_accounts_avilb)

    @cached_property
    def block_devices(self) -> AsyncBlockDevicesResourceWithRawResponse:
        return AsyncBlockDevicesResourceWithRawResponse(self._api.block_devices)

    @cached_property
    def fabric_vsphere_datastores(self) -> AsyncFabricVsphereDatastoresResourceWithRawResponse:
        return AsyncFabricVsphereDatastoresResourceWithRawResponse(self._api.fabric_vsphere_datastores)

    @cached_property
    def fabric_networks(self) -> AsyncFabricNetworksResourceWithRawResponse:
        return AsyncFabricNetworksResourceWithRawResponse(self._api.fabric_networks)

    @cached_property
    def fabric_networks_vsphere(self) -> AsyncFabricNetworksVsphereResourceWithRawResponse:
        return AsyncFabricNetworksVsphereResourceWithRawResponse(self._api.fabric_networks_vsphere)

    @cached_property
    def fabric_computes(self) -> AsyncFabricComputesResourceWithRawResponse:
        return AsyncFabricComputesResourceWithRawResponse(self._api.fabric_computes)

    @cached_property
    def external_network_ip_ranges(self) -> AsyncExternalNetworkIPRangesResourceWithRawResponse:
        return AsyncExternalNetworkIPRangesResourceWithRawResponse(self._api.external_network_ip_ranges)

    @cached_property
    def configuration_properties(self) -> AsyncConfigurationPropertiesResourceWithRawResponse:
        return AsyncConfigurationPropertiesResourceWithRawResponse(self._api.configuration_properties)

    @cached_property
    def request_tracker(self) -> AsyncRequestTrackerResourceWithRawResponse:
        return AsyncRequestTrackerResourceWithRawResponse(self._api.request_tracker)

    @cached_property
    def regions(self) -> AsyncRegionsResourceWithRawResponse:
        return AsyncRegionsResourceWithRawResponse(self._api.regions)

    @cached_property
    def network_domains(self) -> AsyncNetworkDomainsResourceWithRawResponse:
        return AsyncNetworkDomainsResourceWithRawResponse(self._api.network_domains)

    @cached_property
    def fabric_vsphere_storage_policies(self) -> AsyncFabricVsphereStoragePoliciesResourceWithRawResponse:
        return AsyncFabricVsphereStoragePoliciesResourceWithRawResponse(self._api.fabric_vsphere_storage_policies)

    @cached_property
    def fabric_images(self) -> AsyncFabricImagesResourceWithRawResponse:
        return AsyncFabricImagesResourceWithRawResponse(self._api.fabric_images)

    @cached_property
    def fabric_azure_storage_accounts(self) -> AsyncFabricAzureStorageAccountsResourceWithRawResponse:
        return AsyncFabricAzureStorageAccountsResourceWithRawResponse(self._api.fabric_azure_storage_accounts)

    @cached_property
    def external_ip_blocks(self) -> AsyncExternalIPBlocksResourceWithRawResponse:
        return AsyncExternalIPBlocksResourceWithRawResponse(self._api.external_ip_blocks)


class APIResourceWithStreamingResponse:
    def __init__(self, api: APIResource) -> None:
        self._api = api

        self.retrieve = to_streamed_response_wrapper(
            api.retrieve,
        )
        self.login = to_streamed_response_wrapper(
            api.login,
        )
        self.retrieve_about = to_streamed_response_wrapper(
            api.retrieve_about,
        )
        self.retrieve_event_logs = to_streamed_response_wrapper(
            api.retrieve_event_logs,
        )
        self.retrieve_fabric_aws_volume_types = to_streamed_response_wrapper(
            api.retrieve_fabric_aws_volume_types,
        )
        self.retrieve_fabric_azure_disk_encryption_sets = to_streamed_response_wrapper(
            api.retrieve_fabric_azure_disk_encryption_sets,
        )
        self.retrieve_fabric_flavors = to_streamed_response_wrapper(
            api.retrieve_fabric_flavors,
        )
        self.retrieve_flavors = to_streamed_response_wrapper(
            api.retrieve_flavors,
        )
        self.retrieve_folders = to_streamed_response_wrapper(
            api.retrieve_folders,
        )
        self.retrieve_images = to_streamed_response_wrapper(
            api.retrieve_images,
        )
        self.retrieve_request_graph = to_streamed_response_wrapper(
            api.retrieve_request_graph,
        )

    @cached_property
    def storage_profiles(self) -> StorageProfilesResourceWithStreamingResponse:
        return StorageProfilesResourceWithStreamingResponse(self._api.storage_profiles)

    @cached_property
    def projects(self) -> ProjectsResourceWithStreamingResponse:
        return ProjectsResourceWithStreamingResponse(self._api.projects)

    @cached_property
    def naming(self) -> NamingResourceWithStreamingResponse:
        return NamingResourceWithStreamingResponse(self._api.naming)

    @cached_property
    def zones(self) -> ZonesResourceWithStreamingResponse:
        return ZonesResourceWithStreamingResponse(self._api.zones)

    @cached_property
    def tags(self) -> TagsResourceWithStreamingResponse:
        return TagsResourceWithStreamingResponse(self._api.tags)

    @cached_property
    def storage_profiles_vsphere(self) -> StorageProfilesVsphereResourceWithStreamingResponse:
        return StorageProfilesVsphereResourceWithStreamingResponse(self._api.storage_profiles_vsphere)

    @cached_property
    def storage_profiles_gcp(self) -> StorageProfilesGcpResourceWithStreamingResponse:
        return StorageProfilesGcpResourceWithStreamingResponse(self._api.storage_profiles_gcp)

    @cached_property
    def storage_profiles_azure(self) -> StorageProfilesAzureResourceWithStreamingResponse:
        return StorageProfilesAzureResourceWithStreamingResponse(self._api.storage_profiles_azure)

    @cached_property
    def storage_profiles_aws(self) -> StorageProfilesAwsResourceWithStreamingResponse:
        return StorageProfilesAwsResourceWithStreamingResponse(self._api.storage_profiles_aws)

    @cached_property
    def security_groups(self) -> SecurityGroupsResourceWithStreamingResponse:
        return SecurityGroupsResourceWithStreamingResponse(self._api.security_groups)

    @cached_property
    def networks(self) -> NetworksResourceWithStreamingResponse:
        return NetworksResourceWithStreamingResponse(self._api.networks)

    @cached_property
    def network_profiles(self) -> NetworkProfilesResourceWithStreamingResponse:
        return NetworkProfilesResourceWithStreamingResponse(self._api.network_profiles)

    @cached_property
    def network_ip_ranges(self) -> NetworkIPRangesResourceWithStreamingResponse:
        return NetworkIPRangesResourceWithStreamingResponse(self._api.network_ip_ranges)

    @cached_property
    def machines(self) -> MachinesResourceWithStreamingResponse:
        return MachinesResourceWithStreamingResponse(self._api.machines)

    @cached_property
    def load_balancers(self) -> LoadBalancersResourceWithStreamingResponse:
        return LoadBalancersResourceWithStreamingResponse(self._api.load_balancers)

    @cached_property
    def integrations_ipam(self) -> IntegrationsIpamResourceWithStreamingResponse:
        return IntegrationsIpamResourceWithStreamingResponse(self._api.integrations_ipam)

    @cached_property
    def integrations(self) -> IntegrationsResourceWithStreamingResponse:
        return IntegrationsResourceWithStreamingResponse(self._api.integrations)

    @cached_property
    def image_profiles(self) -> ImageProfilesResourceWithStreamingResponse:
        return ImageProfilesResourceWithStreamingResponse(self._api.image_profiles)

    @cached_property
    def flavor_profiles(self) -> FlavorProfilesResourceWithStreamingResponse:
        return FlavorProfilesResourceWithStreamingResponse(self._api.flavor_profiles)

    @cached_property
    def deployments(self) -> DeploymentsResourceWithStreamingResponse:
        return DeploymentsResourceWithStreamingResponse(self._api.deployments)

    @cached_property
    def data_collectors(self) -> DataCollectorsResourceWithStreamingResponse:
        return DataCollectorsResourceWithStreamingResponse(self._api.data_collectors)

    @cached_property
    def compute_nats(self) -> ComputeNatsResourceWithStreamingResponse:
        return ComputeNatsResourceWithStreamingResponse(self._api.compute_nats)

    @cached_property
    def compute_gateways(self) -> ComputeGatewaysResourceWithStreamingResponse:
        return ComputeGatewaysResourceWithStreamingResponse(self._api.compute_gateways)

    @cached_property
    def cloud_accounts(self) -> CloudAccountsResourceWithStreamingResponse:
        return CloudAccountsResourceWithStreamingResponse(self._api.cloud_accounts)

    @cached_property
    def cloud_accounts_vsphere(self) -> CloudAccountsVsphereResourceWithStreamingResponse:
        return CloudAccountsVsphereResourceWithStreamingResponse(self._api.cloud_accounts_vsphere)

    @cached_property
    def cloud_accounts_vmc(self) -> CloudAccountsVmcResourceWithStreamingResponse:
        return CloudAccountsVmcResourceWithStreamingResponse(self._api.cloud_accounts_vmc)

    @cached_property
    def cloud_accounts_vcf(self) -> CloudAccountsVcfResourceWithStreamingResponse:
        return CloudAccountsVcfResourceWithStreamingResponse(self._api.cloud_accounts_vcf)

    @cached_property
    def cloud_accounts_nsx_v(self) -> CloudAccountsNsxVResourceWithStreamingResponse:
        return CloudAccountsNsxVResourceWithStreamingResponse(self._api.cloud_accounts_nsx_v)

    @cached_property
    def cloud_accounts_nsx_t(self) -> CloudAccountsNsxTResourceWithStreamingResponse:
        return CloudAccountsNsxTResourceWithStreamingResponse(self._api.cloud_accounts_nsx_t)

    @cached_property
    def cloud_accounts_gcp(self) -> CloudAccountsGcpResourceWithStreamingResponse:
        return CloudAccountsGcpResourceWithStreamingResponse(self._api.cloud_accounts_gcp)

    @cached_property
    def cloud_accounts_azure(self) -> CloudAccountsAzureResourceWithStreamingResponse:
        return CloudAccountsAzureResourceWithStreamingResponse(self._api.cloud_accounts_azure)

    @cached_property
    def cloud_accounts_aws(self) -> CloudAccountsAwsResourceWithStreamingResponse:
        return CloudAccountsAwsResourceWithStreamingResponse(self._api.cloud_accounts_aws)

    @cached_property
    def cloud_accounts_avilb(self) -> CloudAccountsAvilbResourceWithStreamingResponse:
        return CloudAccountsAvilbResourceWithStreamingResponse(self._api.cloud_accounts_avilb)

    @cached_property
    def block_devices(self) -> BlockDevicesResourceWithStreamingResponse:
        return BlockDevicesResourceWithStreamingResponse(self._api.block_devices)

    @cached_property
    def fabric_vsphere_datastores(self) -> FabricVsphereDatastoresResourceWithStreamingResponse:
        return FabricVsphereDatastoresResourceWithStreamingResponse(self._api.fabric_vsphere_datastores)

    @cached_property
    def fabric_networks(self) -> FabricNetworksResourceWithStreamingResponse:
        return FabricNetworksResourceWithStreamingResponse(self._api.fabric_networks)

    @cached_property
    def fabric_networks_vsphere(self) -> FabricNetworksVsphereResourceWithStreamingResponse:
        return FabricNetworksVsphereResourceWithStreamingResponse(self._api.fabric_networks_vsphere)

    @cached_property
    def fabric_computes(self) -> FabricComputesResourceWithStreamingResponse:
        return FabricComputesResourceWithStreamingResponse(self._api.fabric_computes)

    @cached_property
    def external_network_ip_ranges(self) -> ExternalNetworkIPRangesResourceWithStreamingResponse:
        return ExternalNetworkIPRangesResourceWithStreamingResponse(self._api.external_network_ip_ranges)

    @cached_property
    def configuration_properties(self) -> ConfigurationPropertiesResourceWithStreamingResponse:
        return ConfigurationPropertiesResourceWithStreamingResponse(self._api.configuration_properties)

    @cached_property
    def request_tracker(self) -> RequestTrackerResourceWithStreamingResponse:
        return RequestTrackerResourceWithStreamingResponse(self._api.request_tracker)

    @cached_property
    def regions(self) -> RegionsResourceWithStreamingResponse:
        return RegionsResourceWithStreamingResponse(self._api.regions)

    @cached_property
    def network_domains(self) -> NetworkDomainsResourceWithStreamingResponse:
        return NetworkDomainsResourceWithStreamingResponse(self._api.network_domains)

    @cached_property
    def fabric_vsphere_storage_policies(self) -> FabricVsphereStoragePoliciesResourceWithStreamingResponse:
        return FabricVsphereStoragePoliciesResourceWithStreamingResponse(self._api.fabric_vsphere_storage_policies)

    @cached_property
    def fabric_images(self) -> FabricImagesResourceWithStreamingResponse:
        return FabricImagesResourceWithStreamingResponse(self._api.fabric_images)

    @cached_property
    def fabric_azure_storage_accounts(self) -> FabricAzureStorageAccountsResourceWithStreamingResponse:
        return FabricAzureStorageAccountsResourceWithStreamingResponse(self._api.fabric_azure_storage_accounts)

    @cached_property
    def external_ip_blocks(self) -> ExternalIPBlocksResourceWithStreamingResponse:
        return ExternalIPBlocksResourceWithStreamingResponse(self._api.external_ip_blocks)


class AsyncAPIResourceWithStreamingResponse:
    def __init__(self, api: AsyncAPIResource) -> None:
        self._api = api

        self.retrieve = async_to_streamed_response_wrapper(
            api.retrieve,
        )
        self.login = async_to_streamed_response_wrapper(
            api.login,
        )
        self.retrieve_about = async_to_streamed_response_wrapper(
            api.retrieve_about,
        )
        self.retrieve_event_logs = async_to_streamed_response_wrapper(
            api.retrieve_event_logs,
        )
        self.retrieve_fabric_aws_volume_types = async_to_streamed_response_wrapper(
            api.retrieve_fabric_aws_volume_types,
        )
        self.retrieve_fabric_azure_disk_encryption_sets = async_to_streamed_response_wrapper(
            api.retrieve_fabric_azure_disk_encryption_sets,
        )
        self.retrieve_fabric_flavors = async_to_streamed_response_wrapper(
            api.retrieve_fabric_flavors,
        )
        self.retrieve_flavors = async_to_streamed_response_wrapper(
            api.retrieve_flavors,
        )
        self.retrieve_folders = async_to_streamed_response_wrapper(
            api.retrieve_folders,
        )
        self.retrieve_images = async_to_streamed_response_wrapper(
            api.retrieve_images,
        )
        self.retrieve_request_graph = async_to_streamed_response_wrapper(
            api.retrieve_request_graph,
        )

    @cached_property
    def storage_profiles(self) -> AsyncStorageProfilesResourceWithStreamingResponse:
        return AsyncStorageProfilesResourceWithStreamingResponse(self._api.storage_profiles)

    @cached_property
    def projects(self) -> AsyncProjectsResourceWithStreamingResponse:
        return AsyncProjectsResourceWithStreamingResponse(self._api.projects)

    @cached_property
    def naming(self) -> AsyncNamingResourceWithStreamingResponse:
        return AsyncNamingResourceWithStreamingResponse(self._api.naming)

    @cached_property
    def zones(self) -> AsyncZonesResourceWithStreamingResponse:
        return AsyncZonesResourceWithStreamingResponse(self._api.zones)

    @cached_property
    def tags(self) -> AsyncTagsResourceWithStreamingResponse:
        return AsyncTagsResourceWithStreamingResponse(self._api.tags)

    @cached_property
    def storage_profiles_vsphere(self) -> AsyncStorageProfilesVsphereResourceWithStreamingResponse:
        return AsyncStorageProfilesVsphereResourceWithStreamingResponse(self._api.storage_profiles_vsphere)

    @cached_property
    def storage_profiles_gcp(self) -> AsyncStorageProfilesGcpResourceWithStreamingResponse:
        return AsyncStorageProfilesGcpResourceWithStreamingResponse(self._api.storage_profiles_gcp)

    @cached_property
    def storage_profiles_azure(self) -> AsyncStorageProfilesAzureResourceWithStreamingResponse:
        return AsyncStorageProfilesAzureResourceWithStreamingResponse(self._api.storage_profiles_azure)

    @cached_property
    def storage_profiles_aws(self) -> AsyncStorageProfilesAwsResourceWithStreamingResponse:
        return AsyncStorageProfilesAwsResourceWithStreamingResponse(self._api.storage_profiles_aws)

    @cached_property
    def security_groups(self) -> AsyncSecurityGroupsResourceWithStreamingResponse:
        return AsyncSecurityGroupsResourceWithStreamingResponse(self._api.security_groups)

    @cached_property
    def networks(self) -> AsyncNetworksResourceWithStreamingResponse:
        return AsyncNetworksResourceWithStreamingResponse(self._api.networks)

    @cached_property
    def network_profiles(self) -> AsyncNetworkProfilesResourceWithStreamingResponse:
        return AsyncNetworkProfilesResourceWithStreamingResponse(self._api.network_profiles)

    @cached_property
    def network_ip_ranges(self) -> AsyncNetworkIPRangesResourceWithStreamingResponse:
        return AsyncNetworkIPRangesResourceWithStreamingResponse(self._api.network_ip_ranges)

    @cached_property
    def machines(self) -> AsyncMachinesResourceWithStreamingResponse:
        return AsyncMachinesResourceWithStreamingResponse(self._api.machines)

    @cached_property
    def load_balancers(self) -> AsyncLoadBalancersResourceWithStreamingResponse:
        return AsyncLoadBalancersResourceWithStreamingResponse(self._api.load_balancers)

    @cached_property
    def integrations_ipam(self) -> AsyncIntegrationsIpamResourceWithStreamingResponse:
        return AsyncIntegrationsIpamResourceWithStreamingResponse(self._api.integrations_ipam)

    @cached_property
    def integrations(self) -> AsyncIntegrationsResourceWithStreamingResponse:
        return AsyncIntegrationsResourceWithStreamingResponse(self._api.integrations)

    @cached_property
    def image_profiles(self) -> AsyncImageProfilesResourceWithStreamingResponse:
        return AsyncImageProfilesResourceWithStreamingResponse(self._api.image_profiles)

    @cached_property
    def flavor_profiles(self) -> AsyncFlavorProfilesResourceWithStreamingResponse:
        return AsyncFlavorProfilesResourceWithStreamingResponse(self._api.flavor_profiles)

    @cached_property
    def deployments(self) -> AsyncDeploymentsResourceWithStreamingResponse:
        return AsyncDeploymentsResourceWithStreamingResponse(self._api.deployments)

    @cached_property
    def data_collectors(self) -> AsyncDataCollectorsResourceWithStreamingResponse:
        return AsyncDataCollectorsResourceWithStreamingResponse(self._api.data_collectors)

    @cached_property
    def compute_nats(self) -> AsyncComputeNatsResourceWithStreamingResponse:
        return AsyncComputeNatsResourceWithStreamingResponse(self._api.compute_nats)

    @cached_property
    def compute_gateways(self) -> AsyncComputeGatewaysResourceWithStreamingResponse:
        return AsyncComputeGatewaysResourceWithStreamingResponse(self._api.compute_gateways)

    @cached_property
    def cloud_accounts(self) -> AsyncCloudAccountsResourceWithStreamingResponse:
        return AsyncCloudAccountsResourceWithStreamingResponse(self._api.cloud_accounts)

    @cached_property
    def cloud_accounts_vsphere(self) -> AsyncCloudAccountsVsphereResourceWithStreamingResponse:
        return AsyncCloudAccountsVsphereResourceWithStreamingResponse(self._api.cloud_accounts_vsphere)

    @cached_property
    def cloud_accounts_vmc(self) -> AsyncCloudAccountsVmcResourceWithStreamingResponse:
        return AsyncCloudAccountsVmcResourceWithStreamingResponse(self._api.cloud_accounts_vmc)

    @cached_property
    def cloud_accounts_vcf(self) -> AsyncCloudAccountsVcfResourceWithStreamingResponse:
        return AsyncCloudAccountsVcfResourceWithStreamingResponse(self._api.cloud_accounts_vcf)

    @cached_property
    def cloud_accounts_nsx_v(self) -> AsyncCloudAccountsNsxVResourceWithStreamingResponse:
        return AsyncCloudAccountsNsxVResourceWithStreamingResponse(self._api.cloud_accounts_nsx_v)

    @cached_property
    def cloud_accounts_nsx_t(self) -> AsyncCloudAccountsNsxTResourceWithStreamingResponse:
        return AsyncCloudAccountsNsxTResourceWithStreamingResponse(self._api.cloud_accounts_nsx_t)

    @cached_property
    def cloud_accounts_gcp(self) -> AsyncCloudAccountsGcpResourceWithStreamingResponse:
        return AsyncCloudAccountsGcpResourceWithStreamingResponse(self._api.cloud_accounts_gcp)

    @cached_property
    def cloud_accounts_azure(self) -> AsyncCloudAccountsAzureResourceWithStreamingResponse:
        return AsyncCloudAccountsAzureResourceWithStreamingResponse(self._api.cloud_accounts_azure)

    @cached_property
    def cloud_accounts_aws(self) -> AsyncCloudAccountsAwsResourceWithStreamingResponse:
        return AsyncCloudAccountsAwsResourceWithStreamingResponse(self._api.cloud_accounts_aws)

    @cached_property
    def cloud_accounts_avilb(self) -> AsyncCloudAccountsAvilbResourceWithStreamingResponse:
        return AsyncCloudAccountsAvilbResourceWithStreamingResponse(self._api.cloud_accounts_avilb)

    @cached_property
    def block_devices(self) -> AsyncBlockDevicesResourceWithStreamingResponse:
        return AsyncBlockDevicesResourceWithStreamingResponse(self._api.block_devices)

    @cached_property
    def fabric_vsphere_datastores(self) -> AsyncFabricVsphereDatastoresResourceWithStreamingResponse:
        return AsyncFabricVsphereDatastoresResourceWithStreamingResponse(self._api.fabric_vsphere_datastores)

    @cached_property
    def fabric_networks(self) -> AsyncFabricNetworksResourceWithStreamingResponse:
        return AsyncFabricNetworksResourceWithStreamingResponse(self._api.fabric_networks)

    @cached_property
    def fabric_networks_vsphere(self) -> AsyncFabricNetworksVsphereResourceWithStreamingResponse:
        return AsyncFabricNetworksVsphereResourceWithStreamingResponse(self._api.fabric_networks_vsphere)

    @cached_property
    def fabric_computes(self) -> AsyncFabricComputesResourceWithStreamingResponse:
        return AsyncFabricComputesResourceWithStreamingResponse(self._api.fabric_computes)

    @cached_property
    def external_network_ip_ranges(self) -> AsyncExternalNetworkIPRangesResourceWithStreamingResponse:
        return AsyncExternalNetworkIPRangesResourceWithStreamingResponse(self._api.external_network_ip_ranges)

    @cached_property
    def configuration_properties(self) -> AsyncConfigurationPropertiesResourceWithStreamingResponse:
        return AsyncConfigurationPropertiesResourceWithStreamingResponse(self._api.configuration_properties)

    @cached_property
    def request_tracker(self) -> AsyncRequestTrackerResourceWithStreamingResponse:
        return AsyncRequestTrackerResourceWithStreamingResponse(self._api.request_tracker)

    @cached_property
    def regions(self) -> AsyncRegionsResourceWithStreamingResponse:
        return AsyncRegionsResourceWithStreamingResponse(self._api.regions)

    @cached_property
    def network_domains(self) -> AsyncNetworkDomainsResourceWithStreamingResponse:
        return AsyncNetworkDomainsResourceWithStreamingResponse(self._api.network_domains)

    @cached_property
    def fabric_vsphere_storage_policies(self) -> AsyncFabricVsphereStoragePoliciesResourceWithStreamingResponse:
        return AsyncFabricVsphereStoragePoliciesResourceWithStreamingResponse(self._api.fabric_vsphere_storage_policies)

    @cached_property
    def fabric_images(self) -> AsyncFabricImagesResourceWithStreamingResponse:
        return AsyncFabricImagesResourceWithStreamingResponse(self._api.fabric_images)

    @cached_property
    def fabric_azure_storage_accounts(self) -> AsyncFabricAzureStorageAccountsResourceWithStreamingResponse:
        return AsyncFabricAzureStorageAccountsResourceWithStreamingResponse(self._api.fabric_azure_storage_accounts)

    @cached_property
    def external_ip_blocks(self) -> AsyncExternalIPBlocksResourceWithStreamingResponse:
        return AsyncExternalIPBlocksResourceWithStreamingResponse(self._api.external_ip_blocks)
