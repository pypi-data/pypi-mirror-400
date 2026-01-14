# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from vra_iaas import VraIaas, AsyncVraIaas
from tests.utils import assert_matches_type
from vra_iaas.types.iaas.api import (
    FabricCompute,
    FabricComputeResult,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestFabricComputes:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve(self, client: VraIaas) -> None:
        fabric_compute = client.iaas.api.fabric_computes.retrieve(
            id="id",
        )
        assert_matches_type(FabricCompute, fabric_compute, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_with_all_params(self, client: VraIaas) -> None:
        fabric_compute = client.iaas.api.fabric_computes.retrieve(
            id="id",
            api_version="apiVersion",
        )
        assert_matches_type(FabricCompute, fabric_compute, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve(self, client: VraIaas) -> None:
        response = client.iaas.api.fabric_computes.with_raw_response.retrieve(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        fabric_compute = response.parse()
        assert_matches_type(FabricCompute, fabric_compute, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve(self, client: VraIaas) -> None:
        with client.iaas.api.fabric_computes.with_streaming_response.retrieve(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            fabric_compute = response.parse()
            assert_matches_type(FabricCompute, fabric_compute, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve(self, client: VraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.iaas.api.fabric_computes.with_raw_response.retrieve(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update(self, client: VraIaas) -> None:
        fabric_compute = client.iaas.api.fabric_computes.update(
            id="id",
        )
        assert_matches_type(FabricCompute, fabric_compute, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update_with_all_params(self, client: VraIaas) -> None:
        fabric_compute = client.iaas.api.fabric_computes.update(
            id="id",
            api_version="apiVersion",
            maximum_allowed_cpu_allocation_percent=120,
            maximum_allowed_memory_allocation_percent=120,
            tags=[
                {
                    "key": "?",
                    "value": "Environment",
                }
            ],
        )
        assert_matches_type(FabricCompute, fabric_compute, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_update(self, client: VraIaas) -> None:
        response = client.iaas.api.fabric_computes.with_raw_response.update(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        fabric_compute = response.parse()
        assert_matches_type(FabricCompute, fabric_compute, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_update(self, client: VraIaas) -> None:
        with client.iaas.api.fabric_computes.with_streaming_response.update(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            fabric_compute = response.parse()
            assert_matches_type(FabricCompute, fabric_compute, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_update(self, client: VraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.iaas.api.fabric_computes.with_raw_response.update(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_fabric_computes(self, client: VraIaas) -> None:
        fabric_compute = client.iaas.api.fabric_computes.retrieve_fabric_computes()
        assert_matches_type(FabricComputeResult, fabric_compute, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_fabric_computes_with_all_params(self, client: VraIaas) -> None:
        fabric_compute = client.iaas.api.fabric_computes.retrieve_fabric_computes(
            count=True,
            filter="$filter",
            skip=0,
            top=0,
            api_version="apiVersion",
        )
        assert_matches_type(FabricComputeResult, fabric_compute, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve_fabric_computes(self, client: VraIaas) -> None:
        response = client.iaas.api.fabric_computes.with_raw_response.retrieve_fabric_computes()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        fabric_compute = response.parse()
        assert_matches_type(FabricComputeResult, fabric_compute, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve_fabric_computes(self, client: VraIaas) -> None:
        with client.iaas.api.fabric_computes.with_streaming_response.retrieve_fabric_computes() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            fabric_compute = response.parse()
            assert_matches_type(FabricComputeResult, fabric_compute, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncFabricComputes:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncVraIaas) -> None:
        fabric_compute = await async_client.iaas.api.fabric_computes.retrieve(
            id="id",
        )
        assert_matches_type(FabricCompute, fabric_compute, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_with_all_params(self, async_client: AsyncVraIaas) -> None:
        fabric_compute = await async_client.iaas.api.fabric_computes.retrieve(
            id="id",
            api_version="apiVersion",
        )
        assert_matches_type(FabricCompute, fabric_compute, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.fabric_computes.with_raw_response.retrieve(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        fabric_compute = await response.parse()
        assert_matches_type(FabricCompute, fabric_compute, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.fabric_computes.with_streaming_response.retrieve(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            fabric_compute = await response.parse()
            assert_matches_type(FabricCompute, fabric_compute, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncVraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.iaas.api.fabric_computes.with_raw_response.retrieve(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update(self, async_client: AsyncVraIaas) -> None:
        fabric_compute = await async_client.iaas.api.fabric_computes.update(
            id="id",
        )
        assert_matches_type(FabricCompute, fabric_compute, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncVraIaas) -> None:
        fabric_compute = await async_client.iaas.api.fabric_computes.update(
            id="id",
            api_version="apiVersion",
            maximum_allowed_cpu_allocation_percent=120,
            maximum_allowed_memory_allocation_percent=120,
            tags=[
                {
                    "key": "?",
                    "value": "Environment",
                }
            ],
        )
        assert_matches_type(FabricCompute, fabric_compute, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_update(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.fabric_computes.with_raw_response.update(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        fabric_compute = await response.parse()
        assert_matches_type(FabricCompute, fabric_compute, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.fabric_computes.with_streaming_response.update(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            fabric_compute = await response.parse()
            assert_matches_type(FabricCompute, fabric_compute, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_update(self, async_client: AsyncVraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.iaas.api.fabric_computes.with_raw_response.update(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_fabric_computes(self, async_client: AsyncVraIaas) -> None:
        fabric_compute = await async_client.iaas.api.fabric_computes.retrieve_fabric_computes()
        assert_matches_type(FabricComputeResult, fabric_compute, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_fabric_computes_with_all_params(self, async_client: AsyncVraIaas) -> None:
        fabric_compute = await async_client.iaas.api.fabric_computes.retrieve_fabric_computes(
            count=True,
            filter="$filter",
            skip=0,
            top=0,
            api_version="apiVersion",
        )
        assert_matches_type(FabricComputeResult, fabric_compute, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve_fabric_computes(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.fabric_computes.with_raw_response.retrieve_fabric_computes()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        fabric_compute = await response.parse()
        assert_matches_type(FabricComputeResult, fabric_compute, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve_fabric_computes(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.fabric_computes.with_streaming_response.retrieve_fabric_computes() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            fabric_compute = await response.parse()
            assert_matches_type(FabricComputeResult, fabric_compute, path=["response"])

        assert cast(Any, response.is_closed) is True
