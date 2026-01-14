# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from vra_iaas import VraIaas, AsyncVraIaas
from tests.utils import assert_matches_type
from vra_iaas.types.iaas.api.projects import RequestTracker

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestOperations:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_reconfigure(self, client: VraIaas) -> None:
        operation = client.iaas.api.compute_nats.operations.reconfigure(
            id="id",
            nat_rules=[
                {
                    "index": 0,
                    "target_link": "/iaas/api/load-balancers/try6-45ef, /iaas/api/machines/ht54-a472/network-interfaces/dyd6-d67e",
                }
            ],
        )
        assert_matches_type(RequestTracker, operation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_reconfigure_with_all_params(self, client: VraIaas) -> None:
        operation = client.iaas.api.compute_nats.operations.reconfigure(
            id="id",
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
            api_version="apiVersion",
        )
        assert_matches_type(RequestTracker, operation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_reconfigure(self, client: VraIaas) -> None:
        response = client.iaas.api.compute_nats.operations.with_raw_response.reconfigure(
            id="id",
            nat_rules=[
                {
                    "index": 0,
                    "target_link": "/iaas/api/load-balancers/try6-45ef, /iaas/api/machines/ht54-a472/network-interfaces/dyd6-d67e",
                }
            ],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        operation = response.parse()
        assert_matches_type(RequestTracker, operation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_reconfigure(self, client: VraIaas) -> None:
        with client.iaas.api.compute_nats.operations.with_streaming_response.reconfigure(
            id="id",
            nat_rules=[
                {
                    "index": 0,
                    "target_link": "/iaas/api/load-balancers/try6-45ef, /iaas/api/machines/ht54-a472/network-interfaces/dyd6-d67e",
                }
            ],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            operation = response.parse()
            assert_matches_type(RequestTracker, operation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_reconfigure(self, client: VraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.iaas.api.compute_nats.operations.with_raw_response.reconfigure(
                id="",
                nat_rules=[
                    {
                        "index": 0,
                        "target_link": "/iaas/api/load-balancers/try6-45ef, /iaas/api/machines/ht54-a472/network-interfaces/dyd6-d67e",
                    }
                ],
            )


class TestAsyncOperations:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_reconfigure(self, async_client: AsyncVraIaas) -> None:
        operation = await async_client.iaas.api.compute_nats.operations.reconfigure(
            id="id",
            nat_rules=[
                {
                    "index": 0,
                    "target_link": "/iaas/api/load-balancers/try6-45ef, /iaas/api/machines/ht54-a472/network-interfaces/dyd6-d67e",
                }
            ],
        )
        assert_matches_type(RequestTracker, operation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_reconfigure_with_all_params(self, async_client: AsyncVraIaas) -> None:
        operation = await async_client.iaas.api.compute_nats.operations.reconfigure(
            id="id",
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
            api_version="apiVersion",
        )
        assert_matches_type(RequestTracker, operation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_reconfigure(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.compute_nats.operations.with_raw_response.reconfigure(
            id="id",
            nat_rules=[
                {
                    "index": 0,
                    "target_link": "/iaas/api/load-balancers/try6-45ef, /iaas/api/machines/ht54-a472/network-interfaces/dyd6-d67e",
                }
            ],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        operation = await response.parse()
        assert_matches_type(RequestTracker, operation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_reconfigure(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.compute_nats.operations.with_streaming_response.reconfigure(
            id="id",
            nat_rules=[
                {
                    "index": 0,
                    "target_link": "/iaas/api/load-balancers/try6-45ef, /iaas/api/machines/ht54-a472/network-interfaces/dyd6-d67e",
                }
            ],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            operation = await response.parse()
            assert_matches_type(RequestTracker, operation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_reconfigure(self, async_client: AsyncVraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.iaas.api.compute_nats.operations.with_raw_response.reconfigure(
                id="",
                nat_rules=[
                    {
                        "index": 0,
                        "target_link": "/iaas/api/load-balancers/try6-45ef, /iaas/api/machines/ht54-a472/network-interfaces/dyd6-d67e",
                    }
                ],
            )
