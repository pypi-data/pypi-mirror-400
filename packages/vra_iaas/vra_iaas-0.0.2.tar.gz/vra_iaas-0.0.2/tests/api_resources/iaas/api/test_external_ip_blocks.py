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


class TestExternalIPBlocks:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve(self, client: VraIaas) -> None:
        external_ip_block = client.iaas.api.external_ip_blocks.retrieve(
            id="id",
        )
        assert_matches_type(FabricNetwork, external_ip_block, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_with_all_params(self, client: VraIaas) -> None:
        external_ip_block = client.iaas.api.external_ip_blocks.retrieve(
            id="id",
            api_version="apiVersion",
        )
        assert_matches_type(FabricNetwork, external_ip_block, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve(self, client: VraIaas) -> None:
        response = client.iaas.api.external_ip_blocks.with_raw_response.retrieve(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        external_ip_block = response.parse()
        assert_matches_type(FabricNetwork, external_ip_block, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve(self, client: VraIaas) -> None:
        with client.iaas.api.external_ip_blocks.with_streaming_response.retrieve(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            external_ip_block = response.parse()
            assert_matches_type(FabricNetwork, external_ip_block, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve(self, client: VraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.iaas.api.external_ip_blocks.with_raw_response.retrieve(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_external_ip_blocks(self, client: VraIaas) -> None:
        external_ip_block = client.iaas.api.external_ip_blocks.retrieve_external_ip_blocks()
        assert_matches_type(FabricNetworkResult, external_ip_block, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_external_ip_blocks_with_all_params(self, client: VraIaas) -> None:
        external_ip_block = client.iaas.api.external_ip_blocks.retrieve_external_ip_blocks(
            api_version="apiVersion",
        )
        assert_matches_type(FabricNetworkResult, external_ip_block, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve_external_ip_blocks(self, client: VraIaas) -> None:
        response = client.iaas.api.external_ip_blocks.with_raw_response.retrieve_external_ip_blocks()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        external_ip_block = response.parse()
        assert_matches_type(FabricNetworkResult, external_ip_block, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve_external_ip_blocks(self, client: VraIaas) -> None:
        with client.iaas.api.external_ip_blocks.with_streaming_response.retrieve_external_ip_blocks() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            external_ip_block = response.parse()
            assert_matches_type(FabricNetworkResult, external_ip_block, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncExternalIPBlocks:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncVraIaas) -> None:
        external_ip_block = await async_client.iaas.api.external_ip_blocks.retrieve(
            id="id",
        )
        assert_matches_type(FabricNetwork, external_ip_block, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_with_all_params(self, async_client: AsyncVraIaas) -> None:
        external_ip_block = await async_client.iaas.api.external_ip_blocks.retrieve(
            id="id",
            api_version="apiVersion",
        )
        assert_matches_type(FabricNetwork, external_ip_block, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.external_ip_blocks.with_raw_response.retrieve(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        external_ip_block = await response.parse()
        assert_matches_type(FabricNetwork, external_ip_block, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.external_ip_blocks.with_streaming_response.retrieve(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            external_ip_block = await response.parse()
            assert_matches_type(FabricNetwork, external_ip_block, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncVraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.iaas.api.external_ip_blocks.with_raw_response.retrieve(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_external_ip_blocks(self, async_client: AsyncVraIaas) -> None:
        external_ip_block = await async_client.iaas.api.external_ip_blocks.retrieve_external_ip_blocks()
        assert_matches_type(FabricNetworkResult, external_ip_block, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_external_ip_blocks_with_all_params(self, async_client: AsyncVraIaas) -> None:
        external_ip_block = await async_client.iaas.api.external_ip_blocks.retrieve_external_ip_blocks(
            api_version="apiVersion",
        )
        assert_matches_type(FabricNetworkResult, external_ip_block, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve_external_ip_blocks(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.external_ip_blocks.with_raw_response.retrieve_external_ip_blocks()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        external_ip_block = await response.parse()
        assert_matches_type(FabricNetworkResult, external_ip_block, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve_external_ip_blocks(self, async_client: AsyncVraIaas) -> None:
        async with (
            async_client.iaas.api.external_ip_blocks.with_streaming_response.retrieve_external_ip_blocks()
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            external_ip_block = await response.parse()
            assert_matches_type(FabricNetworkResult, external_ip_block, path=["response"])

        assert cast(Any, response.is_closed) is True
