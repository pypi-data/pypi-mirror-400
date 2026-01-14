# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from vra_iaas import VraIaas, AsyncVraIaas
from tests.utils import assert_matches_type
from vra_iaas.types.iaas.api import (
    FabricNetwork,
    FabricNetworkResult,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestFabricNetworks:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve(self, client: VraIaas) -> None:
        fabric_network = client.iaas.api.fabric_networks.retrieve(
            id="id",
        )
        assert_matches_type(FabricNetwork, fabric_network, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_with_all_params(self, client: VraIaas) -> None:
        fabric_network = client.iaas.api.fabric_networks.retrieve(
            id="id",
            select="$select",
            api_version="apiVersion",
        )
        assert_matches_type(FabricNetwork, fabric_network, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve(self, client: VraIaas) -> None:
        response = client.iaas.api.fabric_networks.with_raw_response.retrieve(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        fabric_network = response.parse()
        assert_matches_type(FabricNetwork, fabric_network, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve(self, client: VraIaas) -> None:
        with client.iaas.api.fabric_networks.with_streaming_response.retrieve(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            fabric_network = response.parse()
            assert_matches_type(FabricNetwork, fabric_network, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve(self, client: VraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.iaas.api.fabric_networks.with_raw_response.retrieve(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update(self, client: VraIaas) -> None:
        fabric_network = client.iaas.api.fabric_networks.update(
            id="id",
        )
        assert_matches_type(FabricNetwork, fabric_network, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update_with_all_params(self, client: VraIaas) -> None:
        fabric_network = client.iaas.api.fabric_networks.update(
            id="id",
            api_version="apiVersion",
            tags=[
                {
                    "key": "fast-network",
                    "value": "true",
                }
            ],
        )
        assert_matches_type(FabricNetwork, fabric_network, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_update(self, client: VraIaas) -> None:
        response = client.iaas.api.fabric_networks.with_raw_response.update(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        fabric_network = response.parse()
        assert_matches_type(FabricNetwork, fabric_network, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_update(self, client: VraIaas) -> None:
        with client.iaas.api.fabric_networks.with_streaming_response.update(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            fabric_network = response.parse()
            assert_matches_type(FabricNetwork, fabric_network, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_update(self, client: VraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.iaas.api.fabric_networks.with_raw_response.update(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_fabric_networks(self, client: VraIaas) -> None:
        fabric_network = client.iaas.api.fabric_networks.retrieve_fabric_networks()
        assert_matches_type(FabricNetworkResult, fabric_network, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_fabric_networks_with_all_params(self, client: VraIaas) -> None:
        fabric_network = client.iaas.api.fabric_networks.retrieve_fabric_networks(
            count=True,
            filter="$filter",
            select="$select",
            skip=0,
            top=0,
            api_version="apiVersion",
        )
        assert_matches_type(FabricNetworkResult, fabric_network, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve_fabric_networks(self, client: VraIaas) -> None:
        response = client.iaas.api.fabric_networks.with_raw_response.retrieve_fabric_networks()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        fabric_network = response.parse()
        assert_matches_type(FabricNetworkResult, fabric_network, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve_fabric_networks(self, client: VraIaas) -> None:
        with client.iaas.api.fabric_networks.with_streaming_response.retrieve_fabric_networks() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            fabric_network = response.parse()
            assert_matches_type(FabricNetworkResult, fabric_network, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_network_ip_ranges(self, client: VraIaas) -> None:
        fabric_network = client.iaas.api.fabric_networks.retrieve_network_ip_ranges(
            id="id",
        )
        assert_matches_type(FabricNetwork, fabric_network, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_network_ip_ranges_with_all_params(self, client: VraIaas) -> None:
        fabric_network = client.iaas.api.fabric_networks.retrieve_network_ip_ranges(
            id="id",
            skip=0,
            top=0,
            api_version="apiVersion",
        )
        assert_matches_type(FabricNetwork, fabric_network, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve_network_ip_ranges(self, client: VraIaas) -> None:
        response = client.iaas.api.fabric_networks.with_raw_response.retrieve_network_ip_ranges(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        fabric_network = response.parse()
        assert_matches_type(FabricNetwork, fabric_network, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve_network_ip_ranges(self, client: VraIaas) -> None:
        with client.iaas.api.fabric_networks.with_streaming_response.retrieve_network_ip_ranges(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            fabric_network = response.parse()
            assert_matches_type(FabricNetwork, fabric_network, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve_network_ip_ranges(self, client: VraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.iaas.api.fabric_networks.with_raw_response.retrieve_network_ip_ranges(
                id="",
            )


class TestAsyncFabricNetworks:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncVraIaas) -> None:
        fabric_network = await async_client.iaas.api.fabric_networks.retrieve(
            id="id",
        )
        assert_matches_type(FabricNetwork, fabric_network, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_with_all_params(self, async_client: AsyncVraIaas) -> None:
        fabric_network = await async_client.iaas.api.fabric_networks.retrieve(
            id="id",
            select="$select",
            api_version="apiVersion",
        )
        assert_matches_type(FabricNetwork, fabric_network, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.fabric_networks.with_raw_response.retrieve(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        fabric_network = await response.parse()
        assert_matches_type(FabricNetwork, fabric_network, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.fabric_networks.with_streaming_response.retrieve(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            fabric_network = await response.parse()
            assert_matches_type(FabricNetwork, fabric_network, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncVraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.iaas.api.fabric_networks.with_raw_response.retrieve(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update(self, async_client: AsyncVraIaas) -> None:
        fabric_network = await async_client.iaas.api.fabric_networks.update(
            id="id",
        )
        assert_matches_type(FabricNetwork, fabric_network, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncVraIaas) -> None:
        fabric_network = await async_client.iaas.api.fabric_networks.update(
            id="id",
            api_version="apiVersion",
            tags=[
                {
                    "key": "fast-network",
                    "value": "true",
                }
            ],
        )
        assert_matches_type(FabricNetwork, fabric_network, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_update(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.fabric_networks.with_raw_response.update(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        fabric_network = await response.parse()
        assert_matches_type(FabricNetwork, fabric_network, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.fabric_networks.with_streaming_response.update(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            fabric_network = await response.parse()
            assert_matches_type(FabricNetwork, fabric_network, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_update(self, async_client: AsyncVraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.iaas.api.fabric_networks.with_raw_response.update(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_fabric_networks(self, async_client: AsyncVraIaas) -> None:
        fabric_network = await async_client.iaas.api.fabric_networks.retrieve_fabric_networks()
        assert_matches_type(FabricNetworkResult, fabric_network, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_fabric_networks_with_all_params(self, async_client: AsyncVraIaas) -> None:
        fabric_network = await async_client.iaas.api.fabric_networks.retrieve_fabric_networks(
            count=True,
            filter="$filter",
            select="$select",
            skip=0,
            top=0,
            api_version="apiVersion",
        )
        assert_matches_type(FabricNetworkResult, fabric_network, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve_fabric_networks(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.fabric_networks.with_raw_response.retrieve_fabric_networks()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        fabric_network = await response.parse()
        assert_matches_type(FabricNetworkResult, fabric_network, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve_fabric_networks(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.fabric_networks.with_streaming_response.retrieve_fabric_networks() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            fabric_network = await response.parse()
            assert_matches_type(FabricNetworkResult, fabric_network, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_network_ip_ranges(self, async_client: AsyncVraIaas) -> None:
        fabric_network = await async_client.iaas.api.fabric_networks.retrieve_network_ip_ranges(
            id="id",
        )
        assert_matches_type(FabricNetwork, fabric_network, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_network_ip_ranges_with_all_params(self, async_client: AsyncVraIaas) -> None:
        fabric_network = await async_client.iaas.api.fabric_networks.retrieve_network_ip_ranges(
            id="id",
            skip=0,
            top=0,
            api_version="apiVersion",
        )
        assert_matches_type(FabricNetwork, fabric_network, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve_network_ip_ranges(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.fabric_networks.with_raw_response.retrieve_network_ip_ranges(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        fabric_network = await response.parse()
        assert_matches_type(FabricNetwork, fabric_network, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve_network_ip_ranges(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.fabric_networks.with_streaming_response.retrieve_network_ip_ranges(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            fabric_network = await response.parse()
            assert_matches_type(FabricNetwork, fabric_network, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve_network_ip_ranges(self, async_client: AsyncVraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.iaas.api.fabric_networks.with_raw_response.retrieve_network_ip_ranges(
                id="",
            )
