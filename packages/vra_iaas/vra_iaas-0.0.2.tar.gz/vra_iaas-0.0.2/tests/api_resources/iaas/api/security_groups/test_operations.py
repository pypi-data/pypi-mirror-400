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
        operation = client.iaas.api.security_groups.operations.reconfigure(
            id="id",
            name="name",
            project_id="e058",
        )
        assert_matches_type(RequestTracker, operation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_reconfigure_with_all_params(self, client: VraIaas) -> None:
        operation = client.iaas.api.security_groups.operations.reconfigure(
            id="id",
            name="name",
            project_id="e058",
            api_version="apiVersion",
            custom_properties={"foo": "string"},
            deployment_id="123e4567-e89b-12d3-a456-426655440000",
            description="description",
            rules=[
                {
                    "access": "Allow",
                    "direction": "Outbound",
                    "ip_range_cidr": "66.170.99.2/32",
                    "ports": "443, 1-655535",
                    "name": "5756f7e2",
                    "protocol": "ANY, TCP, UDP",
                    "service": "HTTPS, SSH",
                }
            ],
            tags=[
                {
                    "key": "group",
                    "value": "ssh",
                }
            ],
        )
        assert_matches_type(RequestTracker, operation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_reconfigure(self, client: VraIaas) -> None:
        response = client.iaas.api.security_groups.operations.with_raw_response.reconfigure(
            id="id",
            name="name",
            project_id="e058",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        operation = response.parse()
        assert_matches_type(RequestTracker, operation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_reconfigure(self, client: VraIaas) -> None:
        with client.iaas.api.security_groups.operations.with_streaming_response.reconfigure(
            id="id",
            name="name",
            project_id="e058",
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
            client.iaas.api.security_groups.operations.with_raw_response.reconfigure(
                id="",
                name="name",
                project_id="e058",
            )


class TestAsyncOperations:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_reconfigure(self, async_client: AsyncVraIaas) -> None:
        operation = await async_client.iaas.api.security_groups.operations.reconfigure(
            id="id",
            name="name",
            project_id="e058",
        )
        assert_matches_type(RequestTracker, operation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_reconfigure_with_all_params(self, async_client: AsyncVraIaas) -> None:
        operation = await async_client.iaas.api.security_groups.operations.reconfigure(
            id="id",
            name="name",
            project_id="e058",
            api_version="apiVersion",
            custom_properties={"foo": "string"},
            deployment_id="123e4567-e89b-12d3-a456-426655440000",
            description="description",
            rules=[
                {
                    "access": "Allow",
                    "direction": "Outbound",
                    "ip_range_cidr": "66.170.99.2/32",
                    "ports": "443, 1-655535",
                    "name": "5756f7e2",
                    "protocol": "ANY, TCP, UDP",
                    "service": "HTTPS, SSH",
                }
            ],
            tags=[
                {
                    "key": "group",
                    "value": "ssh",
                }
            ],
        )
        assert_matches_type(RequestTracker, operation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_reconfigure(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.security_groups.operations.with_raw_response.reconfigure(
            id="id",
            name="name",
            project_id="e058",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        operation = await response.parse()
        assert_matches_type(RequestTracker, operation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_reconfigure(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.security_groups.operations.with_streaming_response.reconfigure(
            id="id",
            name="name",
            project_id="e058",
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
            await async_client.iaas.api.security_groups.operations.with_raw_response.reconfigure(
                id="",
                name="name",
                project_id="e058",
            )
