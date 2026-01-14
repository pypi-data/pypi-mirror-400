# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from vra_iaas import VraIaas, AsyncVraIaas
from tests.utils import assert_matches_type
from vra_iaas.types.iaas.api import (
    NetworkProfile,
    NetworkProfileRetrieveNetworkProfilesResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestNetworkProfiles:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve(self, client: VraIaas) -> None:
        network_profile = client.iaas.api.network_profiles.retrieve(
            id="id",
        )
        assert_matches_type(NetworkProfile, network_profile, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_with_all_params(self, client: VraIaas) -> None:
        network_profile = client.iaas.api.network_profiles.retrieve(
            id="id",
            api_version="apiVersion",
        )
        assert_matches_type(NetworkProfile, network_profile, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve(self, client: VraIaas) -> None:
        response = client.iaas.api.network_profiles.with_raw_response.retrieve(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        network_profile = response.parse()
        assert_matches_type(NetworkProfile, network_profile, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve(self, client: VraIaas) -> None:
        with client.iaas.api.network_profiles.with_streaming_response.retrieve(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            network_profile = response.parse()
            assert_matches_type(NetworkProfile, network_profile, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve(self, client: VraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.iaas.api.network_profiles.with_raw_response.retrieve(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update(self, client: VraIaas) -> None:
        network_profile = client.iaas.api.network_profiles.update(
            id="id",
            name="name",
            region_id="9.0E49",
        )
        assert_matches_type(NetworkProfile, network_profile, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update_with_all_params(self, client: VraIaas) -> None:
        network_profile = client.iaas.api.network_profiles.update(
            id="id",
            name="name",
            region_id="9.0E49",
            api_version="apiVersion",
            custom_properties={
                "resourcePoolId": "resource-pool-1",
                "datastoreId": "StoragePod:group-p87839",
                "computeCluster": "/resources/compute/1234",
                "distributedLogicalRouterStateLink": "/resources/routers/1234",
                "tier0LogicalRouterStateLink": "/resources/routers/2345",
                "onDemandNetworkIPAssignmentType": "dynamic",
            },
            description="description",
            external_ip_block_ids=["3e2bb9bc-6a6a-11ea-bc55-0242ac130003"],
            fabric_network_ids=["6543"],
            isolated_network_cidr_prefix=24,
            isolation_external_fabric_network_id="1234",
            isolation_network_domain_cidr="10.10.10.0/24",
            isolation_network_domain_id="1234",
            isolation_type="SUBNET",
            load_balancer_ids=["6545"],
            security_group_ids=["6545"],
            tags=[
                {
                    "key": "dev",
                    "value": "hard",
                }
            ],
        )
        assert_matches_type(NetworkProfile, network_profile, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_update(self, client: VraIaas) -> None:
        response = client.iaas.api.network_profiles.with_raw_response.update(
            id="id",
            name="name",
            region_id="9.0E49",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        network_profile = response.parse()
        assert_matches_type(NetworkProfile, network_profile, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_update(self, client: VraIaas) -> None:
        with client.iaas.api.network_profiles.with_streaming_response.update(
            id="id",
            name="name",
            region_id="9.0E49",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            network_profile = response.parse()
            assert_matches_type(NetworkProfile, network_profile, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_update(self, client: VraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.iaas.api.network_profiles.with_raw_response.update(
                id="",
                name="name",
                region_id="9.0E49",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete(self, client: VraIaas) -> None:
        network_profile = client.iaas.api.network_profiles.delete(
            id="id",
        )
        assert network_profile is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete_with_all_params(self, client: VraIaas) -> None:
        network_profile = client.iaas.api.network_profiles.delete(
            id="id",
            api_version="apiVersion",
        )
        assert network_profile is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_delete(self, client: VraIaas) -> None:
        response = client.iaas.api.network_profiles.with_raw_response.delete(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        network_profile = response.parse()
        assert network_profile is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_delete(self, client: VraIaas) -> None:
        with client.iaas.api.network_profiles.with_streaming_response.delete(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            network_profile = response.parse()
            assert network_profile is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_delete(self, client: VraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.iaas.api.network_profiles.with_raw_response.delete(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_network_profiles(self, client: VraIaas) -> None:
        network_profile = client.iaas.api.network_profiles.network_profiles(
            name="name",
            region_id="9.0E49",
        )
        assert_matches_type(NetworkProfile, network_profile, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_network_profiles_with_all_params(self, client: VraIaas) -> None:
        network_profile = client.iaas.api.network_profiles.network_profiles(
            name="name",
            region_id="9.0E49",
            api_version="apiVersion",
            custom_properties={
                "resourcePoolId": "resource-pool-1",
                "datastoreId": "StoragePod:group-p87839",
                "computeCluster": "/resources/compute/1234",
                "distributedLogicalRouterStateLink": "/resources/routers/1234",
                "tier0LogicalRouterStateLink": "/resources/routers/2345",
                "onDemandNetworkIPAssignmentType": "dynamic",
            },
            description="description",
            external_ip_block_ids=["3e2bb9bc-6a6a-11ea-bc55-0242ac130003"],
            fabric_network_ids=["6543"],
            isolated_network_cidr_prefix=24,
            isolation_external_fabric_network_id="1234",
            isolation_network_domain_cidr="10.10.10.0/24",
            isolation_network_domain_id="1234",
            isolation_type="SUBNET",
            load_balancer_ids=["6545"],
            security_group_ids=["6545"],
            tags=[
                {
                    "key": "dev",
                    "value": "hard",
                }
            ],
        )
        assert_matches_type(NetworkProfile, network_profile, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_network_profiles(self, client: VraIaas) -> None:
        response = client.iaas.api.network_profiles.with_raw_response.network_profiles(
            name="name",
            region_id="9.0E49",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        network_profile = response.parse()
        assert_matches_type(NetworkProfile, network_profile, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_network_profiles(self, client: VraIaas) -> None:
        with client.iaas.api.network_profiles.with_streaming_response.network_profiles(
            name="name",
            region_id="9.0E49",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            network_profile = response.parse()
            assert_matches_type(NetworkProfile, network_profile, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_network_profiles(self, client: VraIaas) -> None:
        network_profile = client.iaas.api.network_profiles.retrieve_network_profiles()
        assert_matches_type(NetworkProfileRetrieveNetworkProfilesResponse, network_profile, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_network_profiles_with_all_params(self, client: VraIaas) -> None:
        network_profile = client.iaas.api.network_profiles.retrieve_network_profiles(
            count=True,
            filter="$filter",
            select="$select",
            skip=0,
            top=0,
            api_version="apiVersion",
        )
        assert_matches_type(NetworkProfileRetrieveNetworkProfilesResponse, network_profile, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve_network_profiles(self, client: VraIaas) -> None:
        response = client.iaas.api.network_profiles.with_raw_response.retrieve_network_profiles()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        network_profile = response.parse()
        assert_matches_type(NetworkProfileRetrieveNetworkProfilesResponse, network_profile, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve_network_profiles(self, client: VraIaas) -> None:
        with client.iaas.api.network_profiles.with_streaming_response.retrieve_network_profiles() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            network_profile = response.parse()
            assert_matches_type(NetworkProfileRetrieveNetworkProfilesResponse, network_profile, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncNetworkProfiles:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncVraIaas) -> None:
        network_profile = await async_client.iaas.api.network_profiles.retrieve(
            id="id",
        )
        assert_matches_type(NetworkProfile, network_profile, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_with_all_params(self, async_client: AsyncVraIaas) -> None:
        network_profile = await async_client.iaas.api.network_profiles.retrieve(
            id="id",
            api_version="apiVersion",
        )
        assert_matches_type(NetworkProfile, network_profile, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.network_profiles.with_raw_response.retrieve(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        network_profile = await response.parse()
        assert_matches_type(NetworkProfile, network_profile, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.network_profiles.with_streaming_response.retrieve(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            network_profile = await response.parse()
            assert_matches_type(NetworkProfile, network_profile, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncVraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.iaas.api.network_profiles.with_raw_response.retrieve(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update(self, async_client: AsyncVraIaas) -> None:
        network_profile = await async_client.iaas.api.network_profiles.update(
            id="id",
            name="name",
            region_id="9.0E49",
        )
        assert_matches_type(NetworkProfile, network_profile, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncVraIaas) -> None:
        network_profile = await async_client.iaas.api.network_profiles.update(
            id="id",
            name="name",
            region_id="9.0E49",
            api_version="apiVersion",
            custom_properties={
                "resourcePoolId": "resource-pool-1",
                "datastoreId": "StoragePod:group-p87839",
                "computeCluster": "/resources/compute/1234",
                "distributedLogicalRouterStateLink": "/resources/routers/1234",
                "tier0LogicalRouterStateLink": "/resources/routers/2345",
                "onDemandNetworkIPAssignmentType": "dynamic",
            },
            description="description",
            external_ip_block_ids=["3e2bb9bc-6a6a-11ea-bc55-0242ac130003"],
            fabric_network_ids=["6543"],
            isolated_network_cidr_prefix=24,
            isolation_external_fabric_network_id="1234",
            isolation_network_domain_cidr="10.10.10.0/24",
            isolation_network_domain_id="1234",
            isolation_type="SUBNET",
            load_balancer_ids=["6545"],
            security_group_ids=["6545"],
            tags=[
                {
                    "key": "dev",
                    "value": "hard",
                }
            ],
        )
        assert_matches_type(NetworkProfile, network_profile, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_update(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.network_profiles.with_raw_response.update(
            id="id",
            name="name",
            region_id="9.0E49",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        network_profile = await response.parse()
        assert_matches_type(NetworkProfile, network_profile, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.network_profiles.with_streaming_response.update(
            id="id",
            name="name",
            region_id="9.0E49",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            network_profile = await response.parse()
            assert_matches_type(NetworkProfile, network_profile, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_update(self, async_client: AsyncVraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.iaas.api.network_profiles.with_raw_response.update(
                id="",
                name="name",
                region_id="9.0E49",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete(self, async_client: AsyncVraIaas) -> None:
        network_profile = await async_client.iaas.api.network_profiles.delete(
            id="id",
        )
        assert network_profile is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete_with_all_params(self, async_client: AsyncVraIaas) -> None:
        network_profile = await async_client.iaas.api.network_profiles.delete(
            id="id",
            api_version="apiVersion",
        )
        assert network_profile is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.network_profiles.with_raw_response.delete(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        network_profile = await response.parse()
        assert network_profile is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.network_profiles.with_streaming_response.delete(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            network_profile = await response.parse()
            assert network_profile is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_delete(self, async_client: AsyncVraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.iaas.api.network_profiles.with_raw_response.delete(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_network_profiles(self, async_client: AsyncVraIaas) -> None:
        network_profile = await async_client.iaas.api.network_profiles.network_profiles(
            name="name",
            region_id="9.0E49",
        )
        assert_matches_type(NetworkProfile, network_profile, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_network_profiles_with_all_params(self, async_client: AsyncVraIaas) -> None:
        network_profile = await async_client.iaas.api.network_profiles.network_profiles(
            name="name",
            region_id="9.0E49",
            api_version="apiVersion",
            custom_properties={
                "resourcePoolId": "resource-pool-1",
                "datastoreId": "StoragePod:group-p87839",
                "computeCluster": "/resources/compute/1234",
                "distributedLogicalRouterStateLink": "/resources/routers/1234",
                "tier0LogicalRouterStateLink": "/resources/routers/2345",
                "onDemandNetworkIPAssignmentType": "dynamic",
            },
            description="description",
            external_ip_block_ids=["3e2bb9bc-6a6a-11ea-bc55-0242ac130003"],
            fabric_network_ids=["6543"],
            isolated_network_cidr_prefix=24,
            isolation_external_fabric_network_id="1234",
            isolation_network_domain_cidr="10.10.10.0/24",
            isolation_network_domain_id="1234",
            isolation_type="SUBNET",
            load_balancer_ids=["6545"],
            security_group_ids=["6545"],
            tags=[
                {
                    "key": "dev",
                    "value": "hard",
                }
            ],
        )
        assert_matches_type(NetworkProfile, network_profile, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_network_profiles(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.network_profiles.with_raw_response.network_profiles(
            name="name",
            region_id="9.0E49",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        network_profile = await response.parse()
        assert_matches_type(NetworkProfile, network_profile, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_network_profiles(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.network_profiles.with_streaming_response.network_profiles(
            name="name",
            region_id="9.0E49",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            network_profile = await response.parse()
            assert_matches_type(NetworkProfile, network_profile, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_network_profiles(self, async_client: AsyncVraIaas) -> None:
        network_profile = await async_client.iaas.api.network_profiles.retrieve_network_profiles()
        assert_matches_type(NetworkProfileRetrieveNetworkProfilesResponse, network_profile, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_network_profiles_with_all_params(self, async_client: AsyncVraIaas) -> None:
        network_profile = await async_client.iaas.api.network_profiles.retrieve_network_profiles(
            count=True,
            filter="$filter",
            select="$select",
            skip=0,
            top=0,
            api_version="apiVersion",
        )
        assert_matches_type(NetworkProfileRetrieveNetworkProfilesResponse, network_profile, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve_network_profiles(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.network_profiles.with_raw_response.retrieve_network_profiles()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        network_profile = await response.parse()
        assert_matches_type(NetworkProfileRetrieveNetworkProfilesResponse, network_profile, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve_network_profiles(self, async_client: AsyncVraIaas) -> None:
        async with (
            async_client.iaas.api.network_profiles.with_streaming_response.retrieve_network_profiles()
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            network_profile = await response.parse()
            assert_matches_type(NetworkProfileRetrieveNetworkProfilesResponse, network_profile, path=["response"])

        assert cast(Any, response.is_closed) is True
