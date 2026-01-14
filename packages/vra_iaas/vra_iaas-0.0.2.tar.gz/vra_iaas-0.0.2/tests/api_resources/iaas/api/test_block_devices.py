# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from vra_iaas import VraIaas, AsyncVraIaas
from tests.utils import assert_matches_type
from vra_iaas.types.iaas.api import (
    BlockDevice,
)
from vra_iaas.types.iaas.api.machines import BlockDeviceResult
from vra_iaas.types.iaas.api.projects import RequestTracker

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestBlockDevices:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve(self, client: VraIaas) -> None:
        block_device = client.iaas.api.block_devices.retrieve(
            id="id",
        )
        assert_matches_type(BlockDevice, block_device, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_with_all_params(self, client: VraIaas) -> None:
        block_device = client.iaas.api.block_devices.retrieve(
            id="id",
            api_version="apiVersion",
        )
        assert_matches_type(BlockDevice, block_device, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve(self, client: VraIaas) -> None:
        response = client.iaas.api.block_devices.with_raw_response.retrieve(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        block_device = response.parse()
        assert_matches_type(BlockDevice, block_device, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve(self, client: VraIaas) -> None:
        with client.iaas.api.block_devices.with_streaming_response.retrieve(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            block_device = response.parse()
            assert_matches_type(BlockDevice, block_device, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve(self, client: VraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.iaas.api.block_devices.with_raw_response.retrieve(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update(self, client: VraIaas) -> None:
        block_device = client.iaas.api.block_devices.update(
            id="id",
            capacity_in_gb=0,
        )
        assert_matches_type(RequestTracker, block_device, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update_with_all_params(self, client: VraIaas) -> None:
        block_device = client.iaas.api.block_devices.update(
            id="id",
            capacity_in_gb=0,
            api_version="apiVersion",
            use_sdrs=True,
        )
        assert_matches_type(RequestTracker, block_device, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_update(self, client: VraIaas) -> None:
        response = client.iaas.api.block_devices.with_raw_response.update(
            id="id",
            capacity_in_gb=0,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        block_device = response.parse()
        assert_matches_type(RequestTracker, block_device, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_update(self, client: VraIaas) -> None:
        with client.iaas.api.block_devices.with_streaming_response.update(
            id="id",
            capacity_in_gb=0,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            block_device = response.parse()
            assert_matches_type(RequestTracker, block_device, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_update(self, client: VraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.iaas.api.block_devices.with_raw_response.update(
                id="",
                capacity_in_gb=0,
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete(self, client: VraIaas) -> None:
        block_device = client.iaas.api.block_devices.delete(
            id="id",
        )
        assert_matches_type(RequestTracker, block_device, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete_with_all_params(self, client: VraIaas) -> None:
        block_device = client.iaas.api.block_devices.delete(
            id="id",
            api_version="apiVersion",
            force_delete=True,
            purge=True,
        )
        assert_matches_type(RequestTracker, block_device, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_delete(self, client: VraIaas) -> None:
        response = client.iaas.api.block_devices.with_raw_response.delete(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        block_device = response.parse()
        assert_matches_type(RequestTracker, block_device, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_delete(self, client: VraIaas) -> None:
        with client.iaas.api.block_devices.with_streaming_response.delete(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            block_device = response.parse()
            assert_matches_type(RequestTracker, block_device, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_delete(self, client: VraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.iaas.api.block_devices.with_raw_response.delete(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_block_devices(self, client: VraIaas) -> None:
        block_device = client.iaas.api.block_devices.block_devices(
            capacity_in_gb=78,
            name="name",
            project_id="e058",
        )
        assert_matches_type(RequestTracker, block_device, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_block_devices_with_all_params(self, client: VraIaas) -> None:
        block_device = client.iaas.api.block_devices.block_devices(
            capacity_in_gb=78,
            name="name",
            project_id="e058",
            api_version="apiVersion",
            constraints=[
                {
                    "expression": "ha:strong",
                    "mandatory": True,
                }
            ],
            custom_properties={"foo": "string"},
            deployment_id="123e4567-e89b-12d3-a456-426655440000",
            description="description",
            disk_content_base64="dGVzdA",
            encrypted=True,
            persistent=True,
            source_reference="ami-0d4cfd66",
            tags=[
                {
                    "key": "location",
                    "value": "SOF",
                }
            ],
        )
        assert_matches_type(RequestTracker, block_device, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_block_devices(self, client: VraIaas) -> None:
        response = client.iaas.api.block_devices.with_raw_response.block_devices(
            capacity_in_gb=78,
            name="name",
            project_id="e058",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        block_device = response.parse()
        assert_matches_type(RequestTracker, block_device, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_block_devices(self, client: VraIaas) -> None:
        with client.iaas.api.block_devices.with_streaming_response.block_devices(
            capacity_in_gb=78,
            name="name",
            project_id="e058",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            block_device = response.parse()
            assert_matches_type(RequestTracker, block_device, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_block_devices(self, client: VraIaas) -> None:
        block_device = client.iaas.api.block_devices.retrieve_block_devices()
        assert_matches_type(BlockDeviceResult, block_device, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_block_devices_with_all_params(self, client: VraIaas) -> None:
        block_device = client.iaas.api.block_devices.retrieve_block_devices(
            count=True,
            filter="$filter",
            skip=0,
            top=0,
            api_version="apiVersion",
        )
        assert_matches_type(BlockDeviceResult, block_device, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve_block_devices(self, client: VraIaas) -> None:
        response = client.iaas.api.block_devices.with_raw_response.retrieve_block_devices()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        block_device = response.parse()
        assert_matches_type(BlockDeviceResult, block_device, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve_block_devices(self, client: VraIaas) -> None:
        with client.iaas.api.block_devices.with_streaming_response.retrieve_block_devices() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            block_device = response.parse()
            assert_matches_type(BlockDeviceResult, block_device, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncBlockDevices:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncVraIaas) -> None:
        block_device = await async_client.iaas.api.block_devices.retrieve(
            id="id",
        )
        assert_matches_type(BlockDevice, block_device, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_with_all_params(self, async_client: AsyncVraIaas) -> None:
        block_device = await async_client.iaas.api.block_devices.retrieve(
            id="id",
            api_version="apiVersion",
        )
        assert_matches_type(BlockDevice, block_device, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.block_devices.with_raw_response.retrieve(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        block_device = await response.parse()
        assert_matches_type(BlockDevice, block_device, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.block_devices.with_streaming_response.retrieve(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            block_device = await response.parse()
            assert_matches_type(BlockDevice, block_device, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncVraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.iaas.api.block_devices.with_raw_response.retrieve(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update(self, async_client: AsyncVraIaas) -> None:
        block_device = await async_client.iaas.api.block_devices.update(
            id="id",
            capacity_in_gb=0,
        )
        assert_matches_type(RequestTracker, block_device, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncVraIaas) -> None:
        block_device = await async_client.iaas.api.block_devices.update(
            id="id",
            capacity_in_gb=0,
            api_version="apiVersion",
            use_sdrs=True,
        )
        assert_matches_type(RequestTracker, block_device, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_update(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.block_devices.with_raw_response.update(
            id="id",
            capacity_in_gb=0,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        block_device = await response.parse()
        assert_matches_type(RequestTracker, block_device, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.block_devices.with_streaming_response.update(
            id="id",
            capacity_in_gb=0,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            block_device = await response.parse()
            assert_matches_type(RequestTracker, block_device, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_update(self, async_client: AsyncVraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.iaas.api.block_devices.with_raw_response.update(
                id="",
                capacity_in_gb=0,
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete(self, async_client: AsyncVraIaas) -> None:
        block_device = await async_client.iaas.api.block_devices.delete(
            id="id",
        )
        assert_matches_type(RequestTracker, block_device, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete_with_all_params(self, async_client: AsyncVraIaas) -> None:
        block_device = await async_client.iaas.api.block_devices.delete(
            id="id",
            api_version="apiVersion",
            force_delete=True,
            purge=True,
        )
        assert_matches_type(RequestTracker, block_device, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.block_devices.with_raw_response.delete(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        block_device = await response.parse()
        assert_matches_type(RequestTracker, block_device, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.block_devices.with_streaming_response.delete(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            block_device = await response.parse()
            assert_matches_type(RequestTracker, block_device, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_delete(self, async_client: AsyncVraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.iaas.api.block_devices.with_raw_response.delete(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_block_devices(self, async_client: AsyncVraIaas) -> None:
        block_device = await async_client.iaas.api.block_devices.block_devices(
            capacity_in_gb=78,
            name="name",
            project_id="e058",
        )
        assert_matches_type(RequestTracker, block_device, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_block_devices_with_all_params(self, async_client: AsyncVraIaas) -> None:
        block_device = await async_client.iaas.api.block_devices.block_devices(
            capacity_in_gb=78,
            name="name",
            project_id="e058",
            api_version="apiVersion",
            constraints=[
                {
                    "expression": "ha:strong",
                    "mandatory": True,
                }
            ],
            custom_properties={"foo": "string"},
            deployment_id="123e4567-e89b-12d3-a456-426655440000",
            description="description",
            disk_content_base64="dGVzdA",
            encrypted=True,
            persistent=True,
            source_reference="ami-0d4cfd66",
            tags=[
                {
                    "key": "location",
                    "value": "SOF",
                }
            ],
        )
        assert_matches_type(RequestTracker, block_device, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_block_devices(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.block_devices.with_raw_response.block_devices(
            capacity_in_gb=78,
            name="name",
            project_id="e058",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        block_device = await response.parse()
        assert_matches_type(RequestTracker, block_device, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_block_devices(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.block_devices.with_streaming_response.block_devices(
            capacity_in_gb=78,
            name="name",
            project_id="e058",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            block_device = await response.parse()
            assert_matches_type(RequestTracker, block_device, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_block_devices(self, async_client: AsyncVraIaas) -> None:
        block_device = await async_client.iaas.api.block_devices.retrieve_block_devices()
        assert_matches_type(BlockDeviceResult, block_device, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_block_devices_with_all_params(self, async_client: AsyncVraIaas) -> None:
        block_device = await async_client.iaas.api.block_devices.retrieve_block_devices(
            count=True,
            filter="$filter",
            skip=0,
            top=0,
            api_version="apiVersion",
        )
        assert_matches_type(BlockDeviceResult, block_device, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve_block_devices(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.block_devices.with_raw_response.retrieve_block_devices()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        block_device = await response.parse()
        assert_matches_type(BlockDeviceResult, block_device, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve_block_devices(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.block_devices.with_streaming_response.retrieve_block_devices() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            block_device = await response.parse()
            assert_matches_type(BlockDeviceResult, block_device, path=["response"])

        assert cast(Any, response.is_closed) is True
