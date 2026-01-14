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
    def test_method_promote(self, client: VraIaas) -> None:
        operation = client.iaas.api.block_devices.operations.promote(
            id="id",
        )
        assert_matches_type(RequestTracker, operation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_promote_with_all_params(self, client: VraIaas) -> None:
        operation = client.iaas.api.block_devices.operations.promote(
            id="id",
            api_version="apiVersion",
        )
        assert_matches_type(RequestTracker, operation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_promote(self, client: VraIaas) -> None:
        response = client.iaas.api.block_devices.operations.with_raw_response.promote(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        operation = response.parse()
        assert_matches_type(RequestTracker, operation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_promote(self, client: VraIaas) -> None:
        with client.iaas.api.block_devices.operations.with_streaming_response.promote(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            operation = response.parse()
            assert_matches_type(RequestTracker, operation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_promote(self, client: VraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.iaas.api.block_devices.operations.with_raw_response.promote(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_revert(self, client: VraIaas) -> None:
        operation = client.iaas.api.block_devices.operations.revert(
            disk_id="diskId",
            id="id",
        )
        assert_matches_type(RequestTracker, operation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_revert_with_all_params(self, client: VraIaas) -> None:
        operation = client.iaas.api.block_devices.operations.revert(
            disk_id="diskId",
            id="id",
            api_version="apiVersion",
        )
        assert_matches_type(RequestTracker, operation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_revert(self, client: VraIaas) -> None:
        response = client.iaas.api.block_devices.operations.with_raw_response.revert(
            disk_id="diskId",
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        operation = response.parse()
        assert_matches_type(RequestTracker, operation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_revert(self, client: VraIaas) -> None:
        with client.iaas.api.block_devices.operations.with_streaming_response.revert(
            disk_id="diskId",
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            operation = response.parse()
            assert_matches_type(RequestTracker, operation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_revert(self, client: VraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `disk_id` but received ''"):
            client.iaas.api.block_devices.operations.with_raw_response.revert(
                disk_id="",
                id="id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_snapshots(self, client: VraIaas) -> None:
        operation = client.iaas.api.block_devices.operations.snapshots(
            id="id",
        )
        assert_matches_type(RequestTracker, operation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_snapshots_with_all_params(self, client: VraIaas) -> None:
        operation = client.iaas.api.block_devices.operations.snapshots(
            id="id",
            api_version="apiVersion",
            description="description",
            name="name",
            snapshot_properties={
                "0": "{",
                "1": '"',
                "2": "i",
                "3": "n",
                "4": "c",
                "5": "r",
                "6": "e",
                "7": "m",
                "8": "e",
                "9": "n",
                "10": "t",
                "11": "a",
                "12": "l",
                "13": '"',
                "14": ":",
                "15": " ",
                "16": '"',
                "17": "t",
                "18": "r",
                "19": "u",
                "20": "e",
                "21": '"',
                "22": ",",
            },
            tags=[
                {
                    "key": "env",
                    "value": "dev",
                }
            ],
        )
        assert_matches_type(RequestTracker, operation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_snapshots(self, client: VraIaas) -> None:
        response = client.iaas.api.block_devices.operations.with_raw_response.snapshots(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        operation = response.parse()
        assert_matches_type(RequestTracker, operation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_snapshots(self, client: VraIaas) -> None:
        with client.iaas.api.block_devices.operations.with_streaming_response.snapshots(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            operation = response.parse()
            assert_matches_type(RequestTracker, operation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_snapshots(self, client: VraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.iaas.api.block_devices.operations.with_raw_response.snapshots(
                id="",
            )


class TestAsyncOperations:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_promote(self, async_client: AsyncVraIaas) -> None:
        operation = await async_client.iaas.api.block_devices.operations.promote(
            id="id",
        )
        assert_matches_type(RequestTracker, operation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_promote_with_all_params(self, async_client: AsyncVraIaas) -> None:
        operation = await async_client.iaas.api.block_devices.operations.promote(
            id="id",
            api_version="apiVersion",
        )
        assert_matches_type(RequestTracker, operation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_promote(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.block_devices.operations.with_raw_response.promote(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        operation = await response.parse()
        assert_matches_type(RequestTracker, operation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_promote(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.block_devices.operations.with_streaming_response.promote(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            operation = await response.parse()
            assert_matches_type(RequestTracker, operation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_promote(self, async_client: AsyncVraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.iaas.api.block_devices.operations.with_raw_response.promote(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_revert(self, async_client: AsyncVraIaas) -> None:
        operation = await async_client.iaas.api.block_devices.operations.revert(
            disk_id="diskId",
            id="id",
        )
        assert_matches_type(RequestTracker, operation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_revert_with_all_params(self, async_client: AsyncVraIaas) -> None:
        operation = await async_client.iaas.api.block_devices.operations.revert(
            disk_id="diskId",
            id="id",
            api_version="apiVersion",
        )
        assert_matches_type(RequestTracker, operation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_revert(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.block_devices.operations.with_raw_response.revert(
            disk_id="diskId",
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        operation = await response.parse()
        assert_matches_type(RequestTracker, operation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_revert(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.block_devices.operations.with_streaming_response.revert(
            disk_id="diskId",
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            operation = await response.parse()
            assert_matches_type(RequestTracker, operation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_revert(self, async_client: AsyncVraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `disk_id` but received ''"):
            await async_client.iaas.api.block_devices.operations.with_raw_response.revert(
                disk_id="",
                id="id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_snapshots(self, async_client: AsyncVraIaas) -> None:
        operation = await async_client.iaas.api.block_devices.operations.snapshots(
            id="id",
        )
        assert_matches_type(RequestTracker, operation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_snapshots_with_all_params(self, async_client: AsyncVraIaas) -> None:
        operation = await async_client.iaas.api.block_devices.operations.snapshots(
            id="id",
            api_version="apiVersion",
            description="description",
            name="name",
            snapshot_properties={
                "0": "{",
                "1": '"',
                "2": "i",
                "3": "n",
                "4": "c",
                "5": "r",
                "6": "e",
                "7": "m",
                "8": "e",
                "9": "n",
                "10": "t",
                "11": "a",
                "12": "l",
                "13": '"',
                "14": ":",
                "15": " ",
                "16": '"',
                "17": "t",
                "18": "r",
                "19": "u",
                "20": "e",
                "21": '"',
                "22": ",",
            },
            tags=[
                {
                    "key": "env",
                    "value": "dev",
                }
            ],
        )
        assert_matches_type(RequestTracker, operation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_snapshots(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.block_devices.operations.with_raw_response.snapshots(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        operation = await response.parse()
        assert_matches_type(RequestTracker, operation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_snapshots(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.block_devices.operations.with_streaming_response.snapshots(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            operation = await response.parse()
            assert_matches_type(RequestTracker, operation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_snapshots(self, async_client: AsyncVraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.iaas.api.block_devices.operations.with_raw_response.snapshots(
                id="",
            )
