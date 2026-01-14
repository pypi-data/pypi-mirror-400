# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from vra_iaas import VraIaas, AsyncVraIaas
from tests.utils import assert_matches_type
from vra_iaas.types.iaas.api import (
    CustomNaming,
    NamingListResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestNaming:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create(self, client: VraIaas) -> None:
        naming = client.iaas.api.naming.create(
            api_version="apiVersion",
        )
        assert_matches_type(CustomNaming, naming, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_with_all_params(self, client: VraIaas) -> None:
        naming = client.iaas.api.naming.create(
            api_version="apiVersion",
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            description="description",
            name="name",
            projects=[
                {
                    "id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                    "active": True,
                    "default_org": True,
                    "org_id": "orgId",
                    "project_id": "projectId",
                    "project_name": "projectName",
                }
            ],
            templates=[
                {
                    "id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                    "counters": [
                        {
                            "id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                            "active": True,
                            "cn_resource_type": "COMPUTE",
                            "current_counter": 0,
                            "project_id": "projectId",
                        }
                    ],
                    "increment_step": 0,
                    "name": "name",
                    "pattern": "pattern",
                    "resource_default": True,
                    "resource_type": "COMPUTE",
                    "resource_type_name": "resourceTypeName",
                    "start_counter": 0,
                    "static_pattern": "staticPattern",
                    "unique_name": True,
                }
            ],
        )
        assert_matches_type(CustomNaming, naming, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create(self, client: VraIaas) -> None:
        response = client.iaas.api.naming.with_raw_response.create(
            api_version="apiVersion",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        naming = response.parse()
        assert_matches_type(CustomNaming, naming, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create(self, client: VraIaas) -> None:
        with client.iaas.api.naming.with_streaming_response.create(
            api_version="apiVersion",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            naming = response.parse()
            assert_matches_type(CustomNaming, naming, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve(self, client: VraIaas) -> None:
        naming = client.iaas.api.naming.retrieve(
            id="id",
            api_version="apiVersion",
        )
        assert_matches_type(CustomNaming, naming, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve(self, client: VraIaas) -> None:
        response = client.iaas.api.naming.with_raw_response.retrieve(
            id="id",
            api_version="apiVersion",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        naming = response.parse()
        assert_matches_type(CustomNaming, naming, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve(self, client: VraIaas) -> None:
        with client.iaas.api.naming.with_streaming_response.retrieve(
            id="id",
            api_version="apiVersion",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            naming = response.parse()
            assert_matches_type(CustomNaming, naming, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve(self, client: VraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.iaas.api.naming.with_raw_response.retrieve(
                id="",
                api_version="apiVersion",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list(self, client: VraIaas) -> None:
        naming = client.iaas.api.naming.list(
            api_version="apiVersion",
        )
        assert_matches_type(NamingListResponse, naming, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list(self, client: VraIaas) -> None:
        response = client.iaas.api.naming.with_raw_response.list(
            api_version="apiVersion",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        naming = response.parse()
        assert_matches_type(NamingListResponse, naming, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list(self, client: VraIaas) -> None:
        with client.iaas.api.naming.with_streaming_response.list(
            api_version="apiVersion",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            naming = response.parse()
            assert_matches_type(NamingListResponse, naming, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete(self, client: VraIaas) -> None:
        naming = client.iaas.api.naming.delete(
            id="id",
            api_version="apiVersion",
        )
        assert_matches_type(CustomNaming, naming, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_delete(self, client: VraIaas) -> None:
        response = client.iaas.api.naming.with_raw_response.delete(
            id="id",
            api_version="apiVersion",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        naming = response.parse()
        assert_matches_type(CustomNaming, naming, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_delete(self, client: VraIaas) -> None:
        with client.iaas.api.naming.with_streaming_response.delete(
            id="id",
            api_version="apiVersion",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            naming = response.parse()
            assert_matches_type(CustomNaming, naming, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_delete(self, client: VraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.iaas.api.naming.with_raw_response.delete(
                id="",
                api_version="apiVersion",
            )


class TestAsyncNaming:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create(self, async_client: AsyncVraIaas) -> None:
        naming = await async_client.iaas.api.naming.create(
            api_version="apiVersion",
        )
        assert_matches_type(CustomNaming, naming, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncVraIaas) -> None:
        naming = await async_client.iaas.api.naming.create(
            api_version="apiVersion",
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            description="description",
            name="name",
            projects=[
                {
                    "id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                    "active": True,
                    "default_org": True,
                    "org_id": "orgId",
                    "project_id": "projectId",
                    "project_name": "projectName",
                }
            ],
            templates=[
                {
                    "id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                    "counters": [
                        {
                            "id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                            "active": True,
                            "cn_resource_type": "COMPUTE",
                            "current_counter": 0,
                            "project_id": "projectId",
                        }
                    ],
                    "increment_step": 0,
                    "name": "name",
                    "pattern": "pattern",
                    "resource_default": True,
                    "resource_type": "COMPUTE",
                    "resource_type_name": "resourceTypeName",
                    "start_counter": 0,
                    "static_pattern": "staticPattern",
                    "unique_name": True,
                }
            ],
        )
        assert_matches_type(CustomNaming, naming, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.naming.with_raw_response.create(
            api_version="apiVersion",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        naming = await response.parse()
        assert_matches_type(CustomNaming, naming, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.naming.with_streaming_response.create(
            api_version="apiVersion",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            naming = await response.parse()
            assert_matches_type(CustomNaming, naming, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncVraIaas) -> None:
        naming = await async_client.iaas.api.naming.retrieve(
            id="id",
            api_version="apiVersion",
        )
        assert_matches_type(CustomNaming, naming, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.naming.with_raw_response.retrieve(
            id="id",
            api_version="apiVersion",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        naming = await response.parse()
        assert_matches_type(CustomNaming, naming, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.naming.with_streaming_response.retrieve(
            id="id",
            api_version="apiVersion",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            naming = await response.parse()
            assert_matches_type(CustomNaming, naming, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncVraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.iaas.api.naming.with_raw_response.retrieve(
                id="",
                api_version="apiVersion",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list(self, async_client: AsyncVraIaas) -> None:
        naming = await async_client.iaas.api.naming.list(
            api_version="apiVersion",
        )
        assert_matches_type(NamingListResponse, naming, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.naming.with_raw_response.list(
            api_version="apiVersion",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        naming = await response.parse()
        assert_matches_type(NamingListResponse, naming, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.naming.with_streaming_response.list(
            api_version="apiVersion",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            naming = await response.parse()
            assert_matches_type(NamingListResponse, naming, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete(self, async_client: AsyncVraIaas) -> None:
        naming = await async_client.iaas.api.naming.delete(
            id="id",
            api_version="apiVersion",
        )
        assert_matches_type(CustomNaming, naming, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.naming.with_raw_response.delete(
            id="id",
            api_version="apiVersion",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        naming = await response.parse()
        assert_matches_type(CustomNaming, naming, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.naming.with_streaming_response.delete(
            id="id",
            api_version="apiVersion",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            naming = await response.parse()
            assert_matches_type(CustomNaming, naming, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_delete(self, async_client: AsyncVraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.iaas.api.naming.with_raw_response.delete(
                id="",
                api_version="apiVersion",
            )
