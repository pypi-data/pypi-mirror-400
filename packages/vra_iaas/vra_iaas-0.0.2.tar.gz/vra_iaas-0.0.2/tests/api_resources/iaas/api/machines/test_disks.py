# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from vra_iaas import VraIaas, AsyncVraIaas
from tests.utils import assert_matches_type
from vra_iaas.types.iaas.api import BlockDevice
from vra_iaas.types.iaas.api.machines import (
    BlockDeviceResult,
)
from vra_iaas.types.iaas.api.projects import RequestTracker

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestDisks:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create(self, client: VraIaas) -> None:
        disk = client.iaas.api.machines.disks.create(
            id="id",
            block_device_id="1298765",
        )
        assert_matches_type(RequestTracker, disk, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_with_all_params(self, client: VraIaas) -> None:
        disk = client.iaas.api.machines.disks.create(
            id="id",
            block_device_id="1298765",
            api_version="apiVersion",
            description="description",
            disk_attachment_properties={
                "scsiController": "SCSI_Controller_0",
                "unitNumber": "2",
            },
            name="name",
            scsi_controller="SCSI_Controller_0, SCSI_Controller_1, SCSI_Controller_2, SCSI_Controller_3",
            unit_number="0",
        )
        assert_matches_type(RequestTracker, disk, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create(self, client: VraIaas) -> None:
        response = client.iaas.api.machines.disks.with_raw_response.create(
            id="id",
            block_device_id="1298765",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        disk = response.parse()
        assert_matches_type(RequestTracker, disk, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create(self, client: VraIaas) -> None:
        with client.iaas.api.machines.disks.with_streaming_response.create(
            id="id",
            block_device_id="1298765",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            disk = response.parse()
            assert_matches_type(RequestTracker, disk, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_create(self, client: VraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.iaas.api.machines.disks.with_raw_response.create(
                id="",
                block_device_id="1298765",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve(self, client: VraIaas) -> None:
        disk = client.iaas.api.machines.disks.retrieve(
            disk_id="diskId",
            id="id",
        )
        assert_matches_type(BlockDevice, disk, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_with_all_params(self, client: VraIaas) -> None:
        disk = client.iaas.api.machines.disks.retrieve(
            disk_id="diskId",
            id="id",
            api_version="apiVersion",
        )
        assert_matches_type(BlockDevice, disk, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve(self, client: VraIaas) -> None:
        response = client.iaas.api.machines.disks.with_raw_response.retrieve(
            disk_id="diskId",
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        disk = response.parse()
        assert_matches_type(BlockDevice, disk, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve(self, client: VraIaas) -> None:
        with client.iaas.api.machines.disks.with_streaming_response.retrieve(
            disk_id="diskId",
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            disk = response.parse()
            assert_matches_type(BlockDevice, disk, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve(self, client: VraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.iaas.api.machines.disks.with_raw_response.retrieve(
                disk_id="diskId",
                id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `disk_id` but received ''"):
            client.iaas.api.machines.disks.with_raw_response.retrieve(
                disk_id="",
                id="id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list(self, client: VraIaas) -> None:
        disk = client.iaas.api.machines.disks.list(
            id="id",
        )
        assert_matches_type(BlockDeviceResult, disk, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_with_all_params(self, client: VraIaas) -> None:
        disk = client.iaas.api.machines.disks.list(
            id="id",
            api_version="apiVersion",
        )
        assert_matches_type(BlockDeviceResult, disk, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list(self, client: VraIaas) -> None:
        response = client.iaas.api.machines.disks.with_raw_response.list(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        disk = response.parse()
        assert_matches_type(BlockDeviceResult, disk, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list(self, client: VraIaas) -> None:
        with client.iaas.api.machines.disks.with_streaming_response.list(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            disk = response.parse()
            assert_matches_type(BlockDeviceResult, disk, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_list(self, client: VraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.iaas.api.machines.disks.with_raw_response.list(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete(self, client: VraIaas) -> None:
        disk = client.iaas.api.machines.disks.delete(
            disk_id="diskId",
            id="id",
        )
        assert_matches_type(RequestTracker, disk, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete_with_all_params(self, client: VraIaas) -> None:
        disk = client.iaas.api.machines.disks.delete(
            disk_id="diskId",
            id="id",
            api_version="apiVersion",
        )
        assert_matches_type(RequestTracker, disk, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_delete(self, client: VraIaas) -> None:
        response = client.iaas.api.machines.disks.with_raw_response.delete(
            disk_id="diskId",
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        disk = response.parse()
        assert_matches_type(RequestTracker, disk, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_delete(self, client: VraIaas) -> None:
        with client.iaas.api.machines.disks.with_streaming_response.delete(
            disk_id="diskId",
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            disk = response.parse()
            assert_matches_type(RequestTracker, disk, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_delete(self, client: VraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.iaas.api.machines.disks.with_raw_response.delete(
                disk_id="diskId",
                id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `disk_id` but received ''"):
            client.iaas.api.machines.disks.with_raw_response.delete(
                disk_id="",
                id="id",
            )


class TestAsyncDisks:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create(self, async_client: AsyncVraIaas) -> None:
        disk = await async_client.iaas.api.machines.disks.create(
            id="id",
            block_device_id="1298765",
        )
        assert_matches_type(RequestTracker, disk, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncVraIaas) -> None:
        disk = await async_client.iaas.api.machines.disks.create(
            id="id",
            block_device_id="1298765",
            api_version="apiVersion",
            description="description",
            disk_attachment_properties={
                "scsiController": "SCSI_Controller_0",
                "unitNumber": "2",
            },
            name="name",
            scsi_controller="SCSI_Controller_0, SCSI_Controller_1, SCSI_Controller_2, SCSI_Controller_3",
            unit_number="0",
        )
        assert_matches_type(RequestTracker, disk, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.machines.disks.with_raw_response.create(
            id="id",
            block_device_id="1298765",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        disk = await response.parse()
        assert_matches_type(RequestTracker, disk, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.machines.disks.with_streaming_response.create(
            id="id",
            block_device_id="1298765",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            disk = await response.parse()
            assert_matches_type(RequestTracker, disk, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_create(self, async_client: AsyncVraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.iaas.api.machines.disks.with_raw_response.create(
                id="",
                block_device_id="1298765",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncVraIaas) -> None:
        disk = await async_client.iaas.api.machines.disks.retrieve(
            disk_id="diskId",
            id="id",
        )
        assert_matches_type(BlockDevice, disk, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_with_all_params(self, async_client: AsyncVraIaas) -> None:
        disk = await async_client.iaas.api.machines.disks.retrieve(
            disk_id="diskId",
            id="id",
            api_version="apiVersion",
        )
        assert_matches_type(BlockDevice, disk, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.machines.disks.with_raw_response.retrieve(
            disk_id="diskId",
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        disk = await response.parse()
        assert_matches_type(BlockDevice, disk, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.machines.disks.with_streaming_response.retrieve(
            disk_id="diskId",
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            disk = await response.parse()
            assert_matches_type(BlockDevice, disk, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncVraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.iaas.api.machines.disks.with_raw_response.retrieve(
                disk_id="diskId",
                id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `disk_id` but received ''"):
            await async_client.iaas.api.machines.disks.with_raw_response.retrieve(
                disk_id="",
                id="id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list(self, async_client: AsyncVraIaas) -> None:
        disk = await async_client.iaas.api.machines.disks.list(
            id="id",
        )
        assert_matches_type(BlockDeviceResult, disk, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncVraIaas) -> None:
        disk = await async_client.iaas.api.machines.disks.list(
            id="id",
            api_version="apiVersion",
        )
        assert_matches_type(BlockDeviceResult, disk, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.machines.disks.with_raw_response.list(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        disk = await response.parse()
        assert_matches_type(BlockDeviceResult, disk, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.machines.disks.with_streaming_response.list(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            disk = await response.parse()
            assert_matches_type(BlockDeviceResult, disk, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_list(self, async_client: AsyncVraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.iaas.api.machines.disks.with_raw_response.list(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete(self, async_client: AsyncVraIaas) -> None:
        disk = await async_client.iaas.api.machines.disks.delete(
            disk_id="diskId",
            id="id",
        )
        assert_matches_type(RequestTracker, disk, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete_with_all_params(self, async_client: AsyncVraIaas) -> None:
        disk = await async_client.iaas.api.machines.disks.delete(
            disk_id="diskId",
            id="id",
            api_version="apiVersion",
        )
        assert_matches_type(RequestTracker, disk, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.machines.disks.with_raw_response.delete(
            disk_id="diskId",
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        disk = await response.parse()
        assert_matches_type(RequestTracker, disk, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.machines.disks.with_streaming_response.delete(
            disk_id="diskId",
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            disk = await response.parse()
            assert_matches_type(RequestTracker, disk, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_delete(self, async_client: AsyncVraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.iaas.api.machines.disks.with_raw_response.delete(
                disk_id="diskId",
                id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `disk_id` but received ''"):
            await async_client.iaas.api.machines.disks.with_raw_response.delete(
                disk_id="",
                id="id",
            )
