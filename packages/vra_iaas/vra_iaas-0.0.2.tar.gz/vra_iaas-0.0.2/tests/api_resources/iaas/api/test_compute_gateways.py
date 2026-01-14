# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from vra_iaas import VraIaas, AsyncVraIaas
from tests.utils import assert_matches_type
from vra_iaas.types.iaas.api import (
    ComputeGateway,
    ComputeGatewayRetrieveComputeGatewaysResponse,
)
from vra_iaas.types.iaas.api.projects import RequestTracker

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestComputeGateways:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve(self, client: VraIaas) -> None:
        compute_gateway = client.iaas.api.compute_gateways.retrieve(
            id="id",
        )
        assert_matches_type(ComputeGateway, compute_gateway, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_with_all_params(self, client: VraIaas) -> None:
        compute_gateway = client.iaas.api.compute_gateways.retrieve(
            id="id",
            api_version="apiVersion",
        )
        assert_matches_type(ComputeGateway, compute_gateway, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve(self, client: VraIaas) -> None:
        response = client.iaas.api.compute_gateways.with_raw_response.retrieve(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        compute_gateway = response.parse()
        assert_matches_type(ComputeGateway, compute_gateway, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve(self, client: VraIaas) -> None:
        with client.iaas.api.compute_gateways.with_streaming_response.retrieve(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            compute_gateway = response.parse()
            assert_matches_type(ComputeGateway, compute_gateway, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve(self, client: VraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.iaas.api.compute_gateways.with_raw_response.retrieve(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete(self, client: VraIaas) -> None:
        compute_gateway = client.iaas.api.compute_gateways.delete(
            id="id",
        )
        assert_matches_type(RequestTracker, compute_gateway, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete_with_all_params(self, client: VraIaas) -> None:
        compute_gateway = client.iaas.api.compute_gateways.delete(
            id="id",
            api_version="apiVersion",
            force_delete=True,
        )
        assert_matches_type(RequestTracker, compute_gateway, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_delete(self, client: VraIaas) -> None:
        response = client.iaas.api.compute_gateways.with_raw_response.delete(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        compute_gateway = response.parse()
        assert_matches_type(RequestTracker, compute_gateway, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_delete(self, client: VraIaas) -> None:
        with client.iaas.api.compute_gateways.with_streaming_response.delete(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            compute_gateway = response.parse()
            assert_matches_type(RequestTracker, compute_gateway, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_delete(self, client: VraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.iaas.api.compute_gateways.with_raw_response.delete(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_compute_gateways(self, client: VraIaas) -> None:
        compute_gateway = client.iaas.api.compute_gateways.compute_gateways(
            name="name",
            nat_rules=[
                {
                    "index": 0,
                    "target_link": "/iaas/api/load-balancers/try6-45ef, /iaas/api/machines/ht54-a472/network-interfaces/dyd6-d67e",
                }
            ],
            networks=["string"],
            project_id="e058",
        )
        assert_matches_type(RequestTracker, compute_gateway, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_compute_gateways_with_all_params(self, client: VraIaas) -> None:
        compute_gateway = client.iaas.api.compute_gateways.compute_gateways(
            name="name",
            nat_rules=[
                {
                    "index": 0,
                    "target_link": "/iaas/api/load-balancers/try6-45ef, /iaas/api/machines/ht54-a472/network-interfaces/dyd6-d67e",
                    "description": "description",
                    "destination_ports": "any, 80, 5000-5100",
                    "kind": "NAT44",
                    "protocol": "TCP, UDP",
                    "source_ips": "any, 10.20.156.101",
                    "source_ports": "any, 80, 5000-5100",
                    "translated_ports": "any, 80, 5000-5100",
                    "type": "DNAT",
                }
            ],
            networks=["string"],
            project_id="e058",
            api_version="apiVersion",
            custom_properties={"foo": "string"},
            deployment_id="123e4567-e89b-12d3-a456-426655440000",
        )
        assert_matches_type(RequestTracker, compute_gateway, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_compute_gateways(self, client: VraIaas) -> None:
        response = client.iaas.api.compute_gateways.with_raw_response.compute_gateways(
            name="name",
            nat_rules=[
                {
                    "index": 0,
                    "target_link": "/iaas/api/load-balancers/try6-45ef, /iaas/api/machines/ht54-a472/network-interfaces/dyd6-d67e",
                }
            ],
            networks=["string"],
            project_id="e058",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        compute_gateway = response.parse()
        assert_matches_type(RequestTracker, compute_gateway, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_compute_gateways(self, client: VraIaas) -> None:
        with client.iaas.api.compute_gateways.with_streaming_response.compute_gateways(
            name="name",
            nat_rules=[
                {
                    "index": 0,
                    "target_link": "/iaas/api/load-balancers/try6-45ef, /iaas/api/machines/ht54-a472/network-interfaces/dyd6-d67e",
                }
            ],
            networks=["string"],
            project_id="e058",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            compute_gateway = response.parse()
            assert_matches_type(RequestTracker, compute_gateway, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_compute_gateways(self, client: VraIaas) -> None:
        compute_gateway = client.iaas.api.compute_gateways.retrieve_compute_gateways()
        assert_matches_type(ComputeGatewayRetrieveComputeGatewaysResponse, compute_gateway, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_compute_gateways_with_all_params(self, client: VraIaas) -> None:
        compute_gateway = client.iaas.api.compute_gateways.retrieve_compute_gateways(
            api_version="apiVersion",
        )
        assert_matches_type(ComputeGatewayRetrieveComputeGatewaysResponse, compute_gateway, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve_compute_gateways(self, client: VraIaas) -> None:
        response = client.iaas.api.compute_gateways.with_raw_response.retrieve_compute_gateways()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        compute_gateway = response.parse()
        assert_matches_type(ComputeGatewayRetrieveComputeGatewaysResponse, compute_gateway, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve_compute_gateways(self, client: VraIaas) -> None:
        with client.iaas.api.compute_gateways.with_streaming_response.retrieve_compute_gateways() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            compute_gateway = response.parse()
            assert_matches_type(ComputeGatewayRetrieveComputeGatewaysResponse, compute_gateway, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncComputeGateways:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncVraIaas) -> None:
        compute_gateway = await async_client.iaas.api.compute_gateways.retrieve(
            id="id",
        )
        assert_matches_type(ComputeGateway, compute_gateway, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_with_all_params(self, async_client: AsyncVraIaas) -> None:
        compute_gateway = await async_client.iaas.api.compute_gateways.retrieve(
            id="id",
            api_version="apiVersion",
        )
        assert_matches_type(ComputeGateway, compute_gateway, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.compute_gateways.with_raw_response.retrieve(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        compute_gateway = await response.parse()
        assert_matches_type(ComputeGateway, compute_gateway, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.compute_gateways.with_streaming_response.retrieve(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            compute_gateway = await response.parse()
            assert_matches_type(ComputeGateway, compute_gateway, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncVraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.iaas.api.compute_gateways.with_raw_response.retrieve(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete(self, async_client: AsyncVraIaas) -> None:
        compute_gateway = await async_client.iaas.api.compute_gateways.delete(
            id="id",
        )
        assert_matches_type(RequestTracker, compute_gateway, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete_with_all_params(self, async_client: AsyncVraIaas) -> None:
        compute_gateway = await async_client.iaas.api.compute_gateways.delete(
            id="id",
            api_version="apiVersion",
            force_delete=True,
        )
        assert_matches_type(RequestTracker, compute_gateway, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.compute_gateways.with_raw_response.delete(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        compute_gateway = await response.parse()
        assert_matches_type(RequestTracker, compute_gateway, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.compute_gateways.with_streaming_response.delete(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            compute_gateway = await response.parse()
            assert_matches_type(RequestTracker, compute_gateway, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_delete(self, async_client: AsyncVraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.iaas.api.compute_gateways.with_raw_response.delete(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_compute_gateways(self, async_client: AsyncVraIaas) -> None:
        compute_gateway = await async_client.iaas.api.compute_gateways.compute_gateways(
            name="name",
            nat_rules=[
                {
                    "index": 0,
                    "target_link": "/iaas/api/load-balancers/try6-45ef, /iaas/api/machines/ht54-a472/network-interfaces/dyd6-d67e",
                }
            ],
            networks=["string"],
            project_id="e058",
        )
        assert_matches_type(RequestTracker, compute_gateway, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_compute_gateways_with_all_params(self, async_client: AsyncVraIaas) -> None:
        compute_gateway = await async_client.iaas.api.compute_gateways.compute_gateways(
            name="name",
            nat_rules=[
                {
                    "index": 0,
                    "target_link": "/iaas/api/load-balancers/try6-45ef, /iaas/api/machines/ht54-a472/network-interfaces/dyd6-d67e",
                    "description": "description",
                    "destination_ports": "any, 80, 5000-5100",
                    "kind": "NAT44",
                    "protocol": "TCP, UDP",
                    "source_ips": "any, 10.20.156.101",
                    "source_ports": "any, 80, 5000-5100",
                    "translated_ports": "any, 80, 5000-5100",
                    "type": "DNAT",
                }
            ],
            networks=["string"],
            project_id="e058",
            api_version="apiVersion",
            custom_properties={"foo": "string"},
            deployment_id="123e4567-e89b-12d3-a456-426655440000",
        )
        assert_matches_type(RequestTracker, compute_gateway, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_compute_gateways(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.compute_gateways.with_raw_response.compute_gateways(
            name="name",
            nat_rules=[
                {
                    "index": 0,
                    "target_link": "/iaas/api/load-balancers/try6-45ef, /iaas/api/machines/ht54-a472/network-interfaces/dyd6-d67e",
                }
            ],
            networks=["string"],
            project_id="e058",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        compute_gateway = await response.parse()
        assert_matches_type(RequestTracker, compute_gateway, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_compute_gateways(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.compute_gateways.with_streaming_response.compute_gateways(
            name="name",
            nat_rules=[
                {
                    "index": 0,
                    "target_link": "/iaas/api/load-balancers/try6-45ef, /iaas/api/machines/ht54-a472/network-interfaces/dyd6-d67e",
                }
            ],
            networks=["string"],
            project_id="e058",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            compute_gateway = await response.parse()
            assert_matches_type(RequestTracker, compute_gateway, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_compute_gateways(self, async_client: AsyncVraIaas) -> None:
        compute_gateway = await async_client.iaas.api.compute_gateways.retrieve_compute_gateways()
        assert_matches_type(ComputeGatewayRetrieveComputeGatewaysResponse, compute_gateway, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_compute_gateways_with_all_params(self, async_client: AsyncVraIaas) -> None:
        compute_gateway = await async_client.iaas.api.compute_gateways.retrieve_compute_gateways(
            api_version="apiVersion",
        )
        assert_matches_type(ComputeGatewayRetrieveComputeGatewaysResponse, compute_gateway, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve_compute_gateways(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.compute_gateways.with_raw_response.retrieve_compute_gateways()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        compute_gateway = await response.parse()
        assert_matches_type(ComputeGatewayRetrieveComputeGatewaysResponse, compute_gateway, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve_compute_gateways(self, async_client: AsyncVraIaas) -> None:
        async with (
            async_client.iaas.api.compute_gateways.with_streaming_response.retrieve_compute_gateways()
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            compute_gateway = await response.parse()
            assert_matches_type(ComputeGatewayRetrieveComputeGatewaysResponse, compute_gateway, path=["response"])

        assert cast(Any, response.is_closed) is True
