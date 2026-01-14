# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from vra_iaas import VraIaas, AsyncVraIaas
from tests.utils import assert_matches_type
from vra_iaas.types.iaas.api import (
    LoadBalancer,
    LoadBalancerRetrieveLoadBalancersResponse,
)
from vra_iaas.types.iaas.api.projects import RequestTracker

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestLoadBalancers:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve(self, client: VraIaas) -> None:
        load_balancer = client.iaas.api.load_balancers.retrieve(
            id="id",
        )
        assert_matches_type(LoadBalancer, load_balancer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_with_all_params(self, client: VraIaas) -> None:
        load_balancer = client.iaas.api.load_balancers.retrieve(
            id="id",
            api_version="apiVersion",
        )
        assert_matches_type(LoadBalancer, load_balancer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve(self, client: VraIaas) -> None:
        response = client.iaas.api.load_balancers.with_raw_response.retrieve(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        load_balancer = response.parse()
        assert_matches_type(LoadBalancer, load_balancer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve(self, client: VraIaas) -> None:
        with client.iaas.api.load_balancers.with_streaming_response.retrieve(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            load_balancer = response.parse()
            assert_matches_type(LoadBalancer, load_balancer, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve(self, client: VraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.iaas.api.load_balancers.with_raw_response.retrieve(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete(self, client: VraIaas) -> None:
        load_balancer = client.iaas.api.load_balancers.delete(
            id="id",
        )
        assert_matches_type(RequestTracker, load_balancer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete_with_all_params(self, client: VraIaas) -> None:
        load_balancer = client.iaas.api.load_balancers.delete(
            id="id",
            api_version="apiVersion",
            force_delete=True,
        )
        assert_matches_type(RequestTracker, load_balancer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_delete(self, client: VraIaas) -> None:
        response = client.iaas.api.load_balancers.with_raw_response.delete(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        load_balancer = response.parse()
        assert_matches_type(RequestTracker, load_balancer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_delete(self, client: VraIaas) -> None:
        with client.iaas.api.load_balancers.with_streaming_response.delete(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            load_balancer = response.parse()
            assert_matches_type(RequestTracker, load_balancer, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_delete(self, client: VraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.iaas.api.load_balancers.with_raw_response.delete(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_load_balancers(self, client: VraIaas) -> None:
        load_balancer = client.iaas.api.load_balancers.load_balancers(
            name="name",
            nics=[{}],
            project_id="e058",
            routes=[
                {
                    "member_port": "80",
                    "member_protocol": "TCP, UDP",
                    "port": "80",
                    "protocol": "TCP, UDP",
                }
            ],
        )
        assert_matches_type(RequestTracker, load_balancer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_load_balancers_with_all_params(self, client: VraIaas) -> None:
        load_balancer = client.iaas.api.load_balancers.load_balancers(
            name="name",
            nics=[
                {
                    "addresses": ["10.1.2.190"],
                    "custom_properties": {"awaitIp": "true"},
                    "description": "description",
                    "device_index": 1,
                    "fabric_network_id": "54097407-4532-460c-94a8-8f9e18f4c925",
                    "mac_address": '["00:50:56:99:d8:34"]',
                    "name": "name",
                    "network_id": "54097407-4532-460c-94a8-8f9e18f4c925",
                    "security_group_ids": ["string"],
                }
            ],
            project_id="e058",
            routes=[
                {
                    "member_port": "80",
                    "member_protocol": "TCP, UDP",
                    "port": "80",
                    "protocol": "TCP, UDP",
                    "algorithm": "ROUND_ROBIN",
                    "algorithm_parameters": "uriLength=10\nurlParam=section",
                    "health_check_configuration": {
                        "healthy_threshold": 2,
                        "http_method": "GET, OPTIONS, POST, HEAD, PUT",
                        "interval_seconds": 60,
                        "passive_monitor": False,
                        "port": "80",
                        "protocol": "HTTP, HTTPS",
                        "request_body": "http_request.body",
                        "response_body": "http_response.body",
                        "timeout_seconds": 5,
                        "unhealthy_threshold": 5,
                        "url_path": "/index.html",
                    },
                }
            ],
            api_version="apiVersion",
            custom_properties={"foo": "string"},
            deployment_id="123e4567-e89b-12d3-a456-426655440000",
            description="description",
            internet_facing=True,
            logging_level="ERROR, WARNING, INFO, DEBUG",
            tags=[
                {
                    "key": "ownedBy",
                    "value": "Rainpole",
                }
            ],
            target_links=["/iaas/machines/eac3d"],
            type="SMALL, MEDIUM, LARGE",
        )
        assert_matches_type(RequestTracker, load_balancer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_load_balancers(self, client: VraIaas) -> None:
        response = client.iaas.api.load_balancers.with_raw_response.load_balancers(
            name="name",
            nics=[{}],
            project_id="e058",
            routes=[
                {
                    "member_port": "80",
                    "member_protocol": "TCP, UDP",
                    "port": "80",
                    "protocol": "TCP, UDP",
                }
            ],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        load_balancer = response.parse()
        assert_matches_type(RequestTracker, load_balancer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_load_balancers(self, client: VraIaas) -> None:
        with client.iaas.api.load_balancers.with_streaming_response.load_balancers(
            name="name",
            nics=[{}],
            project_id="e058",
            routes=[
                {
                    "member_port": "80",
                    "member_protocol": "TCP, UDP",
                    "port": "80",
                    "protocol": "TCP, UDP",
                }
            ],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            load_balancer = response.parse()
            assert_matches_type(RequestTracker, load_balancer, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_load_balancers(self, client: VraIaas) -> None:
        load_balancer = client.iaas.api.load_balancers.retrieve_load_balancers()
        assert_matches_type(LoadBalancerRetrieveLoadBalancersResponse, load_balancer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_load_balancers_with_all_params(self, client: VraIaas) -> None:
        load_balancer = client.iaas.api.load_balancers.retrieve_load_balancers(
            api_version="apiVersion",
        )
        assert_matches_type(LoadBalancerRetrieveLoadBalancersResponse, load_balancer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve_load_balancers(self, client: VraIaas) -> None:
        response = client.iaas.api.load_balancers.with_raw_response.retrieve_load_balancers()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        load_balancer = response.parse()
        assert_matches_type(LoadBalancerRetrieveLoadBalancersResponse, load_balancer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve_load_balancers(self, client: VraIaas) -> None:
        with client.iaas.api.load_balancers.with_streaming_response.retrieve_load_balancers() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            load_balancer = response.parse()
            assert_matches_type(LoadBalancerRetrieveLoadBalancersResponse, load_balancer, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncLoadBalancers:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncVraIaas) -> None:
        load_balancer = await async_client.iaas.api.load_balancers.retrieve(
            id="id",
        )
        assert_matches_type(LoadBalancer, load_balancer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_with_all_params(self, async_client: AsyncVraIaas) -> None:
        load_balancer = await async_client.iaas.api.load_balancers.retrieve(
            id="id",
            api_version="apiVersion",
        )
        assert_matches_type(LoadBalancer, load_balancer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.load_balancers.with_raw_response.retrieve(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        load_balancer = await response.parse()
        assert_matches_type(LoadBalancer, load_balancer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.load_balancers.with_streaming_response.retrieve(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            load_balancer = await response.parse()
            assert_matches_type(LoadBalancer, load_balancer, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncVraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.iaas.api.load_balancers.with_raw_response.retrieve(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete(self, async_client: AsyncVraIaas) -> None:
        load_balancer = await async_client.iaas.api.load_balancers.delete(
            id="id",
        )
        assert_matches_type(RequestTracker, load_balancer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete_with_all_params(self, async_client: AsyncVraIaas) -> None:
        load_balancer = await async_client.iaas.api.load_balancers.delete(
            id="id",
            api_version="apiVersion",
            force_delete=True,
        )
        assert_matches_type(RequestTracker, load_balancer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.load_balancers.with_raw_response.delete(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        load_balancer = await response.parse()
        assert_matches_type(RequestTracker, load_balancer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.load_balancers.with_streaming_response.delete(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            load_balancer = await response.parse()
            assert_matches_type(RequestTracker, load_balancer, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_delete(self, async_client: AsyncVraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.iaas.api.load_balancers.with_raw_response.delete(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_load_balancers(self, async_client: AsyncVraIaas) -> None:
        load_balancer = await async_client.iaas.api.load_balancers.load_balancers(
            name="name",
            nics=[{}],
            project_id="e058",
            routes=[
                {
                    "member_port": "80",
                    "member_protocol": "TCP, UDP",
                    "port": "80",
                    "protocol": "TCP, UDP",
                }
            ],
        )
        assert_matches_type(RequestTracker, load_balancer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_load_balancers_with_all_params(self, async_client: AsyncVraIaas) -> None:
        load_balancer = await async_client.iaas.api.load_balancers.load_balancers(
            name="name",
            nics=[
                {
                    "addresses": ["10.1.2.190"],
                    "custom_properties": {"awaitIp": "true"},
                    "description": "description",
                    "device_index": 1,
                    "fabric_network_id": "54097407-4532-460c-94a8-8f9e18f4c925",
                    "mac_address": '["00:50:56:99:d8:34"]',
                    "name": "name",
                    "network_id": "54097407-4532-460c-94a8-8f9e18f4c925",
                    "security_group_ids": ["string"],
                }
            ],
            project_id="e058",
            routes=[
                {
                    "member_port": "80",
                    "member_protocol": "TCP, UDP",
                    "port": "80",
                    "protocol": "TCP, UDP",
                    "algorithm": "ROUND_ROBIN",
                    "algorithm_parameters": "uriLength=10\nurlParam=section",
                    "health_check_configuration": {
                        "healthy_threshold": 2,
                        "http_method": "GET, OPTIONS, POST, HEAD, PUT",
                        "interval_seconds": 60,
                        "passive_monitor": False,
                        "port": "80",
                        "protocol": "HTTP, HTTPS",
                        "request_body": "http_request.body",
                        "response_body": "http_response.body",
                        "timeout_seconds": 5,
                        "unhealthy_threshold": 5,
                        "url_path": "/index.html",
                    },
                }
            ],
            api_version="apiVersion",
            custom_properties={"foo": "string"},
            deployment_id="123e4567-e89b-12d3-a456-426655440000",
            description="description",
            internet_facing=True,
            logging_level="ERROR, WARNING, INFO, DEBUG",
            tags=[
                {
                    "key": "ownedBy",
                    "value": "Rainpole",
                }
            ],
            target_links=["/iaas/machines/eac3d"],
            type="SMALL, MEDIUM, LARGE",
        )
        assert_matches_type(RequestTracker, load_balancer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_load_balancers(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.load_balancers.with_raw_response.load_balancers(
            name="name",
            nics=[{}],
            project_id="e058",
            routes=[
                {
                    "member_port": "80",
                    "member_protocol": "TCP, UDP",
                    "port": "80",
                    "protocol": "TCP, UDP",
                }
            ],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        load_balancer = await response.parse()
        assert_matches_type(RequestTracker, load_balancer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_load_balancers(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.load_balancers.with_streaming_response.load_balancers(
            name="name",
            nics=[{}],
            project_id="e058",
            routes=[
                {
                    "member_port": "80",
                    "member_protocol": "TCP, UDP",
                    "port": "80",
                    "protocol": "TCP, UDP",
                }
            ],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            load_balancer = await response.parse()
            assert_matches_type(RequestTracker, load_balancer, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_load_balancers(self, async_client: AsyncVraIaas) -> None:
        load_balancer = await async_client.iaas.api.load_balancers.retrieve_load_balancers()
        assert_matches_type(LoadBalancerRetrieveLoadBalancersResponse, load_balancer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_load_balancers_with_all_params(self, async_client: AsyncVraIaas) -> None:
        load_balancer = await async_client.iaas.api.load_balancers.retrieve_load_balancers(
            api_version="apiVersion",
        )
        assert_matches_type(LoadBalancerRetrieveLoadBalancersResponse, load_balancer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve_load_balancers(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.load_balancers.with_raw_response.retrieve_load_balancers()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        load_balancer = await response.parse()
        assert_matches_type(LoadBalancerRetrieveLoadBalancersResponse, load_balancer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve_load_balancers(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.load_balancers.with_streaming_response.retrieve_load_balancers() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            load_balancer = await response.parse()
            assert_matches_type(LoadBalancerRetrieveLoadBalancersResponse, load_balancer, path=["response"])

        assert cast(Any, response.is_closed) is True
