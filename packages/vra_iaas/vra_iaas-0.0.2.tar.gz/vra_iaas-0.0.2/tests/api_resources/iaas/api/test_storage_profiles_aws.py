# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from vra_iaas import VraIaas, AsyncVraIaas
from tests.utils import assert_matches_type
from vra_iaas.types.iaas.api import (
    AwsStorageProfile,
    StorageProfilesAwRetrieveStorageProfilesAwsResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestStorageProfilesAws:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve(self, client: VraIaas) -> None:
        storage_profiles_aw = client.iaas.api.storage_profiles_aws.retrieve(
            id="id",
        )
        assert_matches_type(AwsStorageProfile, storage_profiles_aw, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_with_all_params(self, client: VraIaas) -> None:
        storage_profiles_aw = client.iaas.api.storage_profiles_aws.retrieve(
            id="id",
            api_version="apiVersion",
        )
        assert_matches_type(AwsStorageProfile, storage_profiles_aw, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve(self, client: VraIaas) -> None:
        response = client.iaas.api.storage_profiles_aws.with_raw_response.retrieve(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        storage_profiles_aw = response.parse()
        assert_matches_type(AwsStorageProfile, storage_profiles_aw, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve(self, client: VraIaas) -> None:
        with client.iaas.api.storage_profiles_aws.with_streaming_response.retrieve(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            storage_profiles_aw = response.parse()
            assert_matches_type(AwsStorageProfile, storage_profiles_aw, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve(self, client: VraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.iaas.api.storage_profiles_aws.with_raw_response.retrieve(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update(self, client: VraIaas) -> None:
        storage_profiles_aw = client.iaas.api.storage_profiles_aws.update(
            id="id",
            device_type="ebs / instance-store",
            name="name",
            region_id="31186",
        )
        assert_matches_type(AwsStorageProfile, storage_profiles_aw, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update_with_all_params(self, client: VraIaas) -> None:
        storage_profiles_aw = client.iaas.api.storage_profiles_aws.update(
            id="id",
            device_type="ebs / instance-store",
            name="name",
            region_id="31186",
            api_version="apiVersion",
            default_item=True,
            description="description",
            iops="2000",
            supports_encryption=False,
            tags=[
                {
                    "key": "tier",
                    "value": "silver",
                }
            ],
            volume_type="gp3 / io2 / gp2 / io1 / sc1 / st1 / standard",
        )
        assert_matches_type(AwsStorageProfile, storage_profiles_aw, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_update(self, client: VraIaas) -> None:
        response = client.iaas.api.storage_profiles_aws.with_raw_response.update(
            id="id",
            device_type="ebs / instance-store",
            name="name",
            region_id="31186",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        storage_profiles_aw = response.parse()
        assert_matches_type(AwsStorageProfile, storage_profiles_aw, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_update(self, client: VraIaas) -> None:
        with client.iaas.api.storage_profiles_aws.with_streaming_response.update(
            id="id",
            device_type="ebs / instance-store",
            name="name",
            region_id="31186",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            storage_profiles_aw = response.parse()
            assert_matches_type(AwsStorageProfile, storage_profiles_aw, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_update(self, client: VraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.iaas.api.storage_profiles_aws.with_raw_response.update(
                id="",
                device_type="ebs / instance-store",
                name="name",
                region_id="31186",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete(self, client: VraIaas) -> None:
        storage_profiles_aw = client.iaas.api.storage_profiles_aws.delete(
            id="id",
        )
        assert storage_profiles_aw is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete_with_all_params(self, client: VraIaas) -> None:
        storage_profiles_aw = client.iaas.api.storage_profiles_aws.delete(
            id="id",
            api_version="apiVersion",
        )
        assert storage_profiles_aw is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_delete(self, client: VraIaas) -> None:
        response = client.iaas.api.storage_profiles_aws.with_raw_response.delete(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        storage_profiles_aw = response.parse()
        assert storage_profiles_aw is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_delete(self, client: VraIaas) -> None:
        with client.iaas.api.storage_profiles_aws.with_streaming_response.delete(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            storage_profiles_aw = response.parse()
            assert storage_profiles_aw is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_delete(self, client: VraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.iaas.api.storage_profiles_aws.with_raw_response.delete(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_storage_profiles_aws(self, client: VraIaas) -> None:
        storage_profiles_aw = client.iaas.api.storage_profiles_aws.retrieve_storage_profiles_aws()
        assert_matches_type(StorageProfilesAwRetrieveStorageProfilesAwsResponse, storage_profiles_aw, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_storage_profiles_aws_with_all_params(self, client: VraIaas) -> None:
        storage_profiles_aw = client.iaas.api.storage_profiles_aws.retrieve_storage_profiles_aws(
            api_version="apiVersion",
        )
        assert_matches_type(StorageProfilesAwRetrieveStorageProfilesAwsResponse, storage_profiles_aw, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve_storage_profiles_aws(self, client: VraIaas) -> None:
        response = client.iaas.api.storage_profiles_aws.with_raw_response.retrieve_storage_profiles_aws()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        storage_profiles_aw = response.parse()
        assert_matches_type(StorageProfilesAwRetrieveStorageProfilesAwsResponse, storage_profiles_aw, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve_storage_profiles_aws(self, client: VraIaas) -> None:
        with client.iaas.api.storage_profiles_aws.with_streaming_response.retrieve_storage_profiles_aws() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            storage_profiles_aw = response.parse()
            assert_matches_type(
                StorageProfilesAwRetrieveStorageProfilesAwsResponse, storage_profiles_aw, path=["response"]
            )

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_storage_profiles_aws(self, client: VraIaas) -> None:
        storage_profiles_aw = client.iaas.api.storage_profiles_aws.storage_profiles_aws(
            device_type="ebs / instance-store",
            name="name",
            region_id="31186",
        )
        assert_matches_type(AwsStorageProfile, storage_profiles_aw, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_storage_profiles_aws_with_all_params(self, client: VraIaas) -> None:
        storage_profiles_aw = client.iaas.api.storage_profiles_aws.storage_profiles_aws(
            device_type="ebs / instance-store",
            name="name",
            region_id="31186",
            api_version="apiVersion",
            default_item=True,
            description="description",
            iops="2000",
            supports_encryption=False,
            tags=[
                {
                    "key": "tier",
                    "value": "silver",
                }
            ],
            volume_type="gp3 / io2 / gp2 / io1 / sc1 / st1 / standard",
        )
        assert_matches_type(AwsStorageProfile, storage_profiles_aw, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_storage_profiles_aws(self, client: VraIaas) -> None:
        response = client.iaas.api.storage_profiles_aws.with_raw_response.storage_profiles_aws(
            device_type="ebs / instance-store",
            name="name",
            region_id="31186",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        storage_profiles_aw = response.parse()
        assert_matches_type(AwsStorageProfile, storage_profiles_aw, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_storage_profiles_aws(self, client: VraIaas) -> None:
        with client.iaas.api.storage_profiles_aws.with_streaming_response.storage_profiles_aws(
            device_type="ebs / instance-store",
            name="name",
            region_id="31186",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            storage_profiles_aw = response.parse()
            assert_matches_type(AwsStorageProfile, storage_profiles_aw, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncStorageProfilesAws:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncVraIaas) -> None:
        storage_profiles_aw = await async_client.iaas.api.storage_profiles_aws.retrieve(
            id="id",
        )
        assert_matches_type(AwsStorageProfile, storage_profiles_aw, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_with_all_params(self, async_client: AsyncVraIaas) -> None:
        storage_profiles_aw = await async_client.iaas.api.storage_profiles_aws.retrieve(
            id="id",
            api_version="apiVersion",
        )
        assert_matches_type(AwsStorageProfile, storage_profiles_aw, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.storage_profiles_aws.with_raw_response.retrieve(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        storage_profiles_aw = await response.parse()
        assert_matches_type(AwsStorageProfile, storage_profiles_aw, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.storage_profiles_aws.with_streaming_response.retrieve(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            storage_profiles_aw = await response.parse()
            assert_matches_type(AwsStorageProfile, storage_profiles_aw, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncVraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.iaas.api.storage_profiles_aws.with_raw_response.retrieve(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update(self, async_client: AsyncVraIaas) -> None:
        storage_profiles_aw = await async_client.iaas.api.storage_profiles_aws.update(
            id="id",
            device_type="ebs / instance-store",
            name="name",
            region_id="31186",
        )
        assert_matches_type(AwsStorageProfile, storage_profiles_aw, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncVraIaas) -> None:
        storage_profiles_aw = await async_client.iaas.api.storage_profiles_aws.update(
            id="id",
            device_type="ebs / instance-store",
            name="name",
            region_id="31186",
            api_version="apiVersion",
            default_item=True,
            description="description",
            iops="2000",
            supports_encryption=False,
            tags=[
                {
                    "key": "tier",
                    "value": "silver",
                }
            ],
            volume_type="gp3 / io2 / gp2 / io1 / sc1 / st1 / standard",
        )
        assert_matches_type(AwsStorageProfile, storage_profiles_aw, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_update(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.storage_profiles_aws.with_raw_response.update(
            id="id",
            device_type="ebs / instance-store",
            name="name",
            region_id="31186",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        storage_profiles_aw = await response.parse()
        assert_matches_type(AwsStorageProfile, storage_profiles_aw, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.storage_profiles_aws.with_streaming_response.update(
            id="id",
            device_type="ebs / instance-store",
            name="name",
            region_id="31186",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            storage_profiles_aw = await response.parse()
            assert_matches_type(AwsStorageProfile, storage_profiles_aw, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_update(self, async_client: AsyncVraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.iaas.api.storage_profiles_aws.with_raw_response.update(
                id="",
                device_type="ebs / instance-store",
                name="name",
                region_id="31186",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete(self, async_client: AsyncVraIaas) -> None:
        storage_profiles_aw = await async_client.iaas.api.storage_profiles_aws.delete(
            id="id",
        )
        assert storage_profiles_aw is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete_with_all_params(self, async_client: AsyncVraIaas) -> None:
        storage_profiles_aw = await async_client.iaas.api.storage_profiles_aws.delete(
            id="id",
            api_version="apiVersion",
        )
        assert storage_profiles_aw is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.storage_profiles_aws.with_raw_response.delete(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        storage_profiles_aw = await response.parse()
        assert storage_profiles_aw is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.storage_profiles_aws.with_streaming_response.delete(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            storage_profiles_aw = await response.parse()
            assert storage_profiles_aw is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_delete(self, async_client: AsyncVraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.iaas.api.storage_profiles_aws.with_raw_response.delete(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_storage_profiles_aws(self, async_client: AsyncVraIaas) -> None:
        storage_profiles_aw = await async_client.iaas.api.storage_profiles_aws.retrieve_storage_profiles_aws()
        assert_matches_type(StorageProfilesAwRetrieveStorageProfilesAwsResponse, storage_profiles_aw, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_storage_profiles_aws_with_all_params(self, async_client: AsyncVraIaas) -> None:
        storage_profiles_aw = await async_client.iaas.api.storage_profiles_aws.retrieve_storage_profiles_aws(
            api_version="apiVersion",
        )
        assert_matches_type(StorageProfilesAwRetrieveStorageProfilesAwsResponse, storage_profiles_aw, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve_storage_profiles_aws(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.storage_profiles_aws.with_raw_response.retrieve_storage_profiles_aws()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        storage_profiles_aw = await response.parse()
        assert_matches_type(StorageProfilesAwRetrieveStorageProfilesAwsResponse, storage_profiles_aw, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve_storage_profiles_aws(self, async_client: AsyncVraIaas) -> None:
        async with (
            async_client.iaas.api.storage_profiles_aws.with_streaming_response.retrieve_storage_profiles_aws()
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            storage_profiles_aw = await response.parse()
            assert_matches_type(
                StorageProfilesAwRetrieveStorageProfilesAwsResponse, storage_profiles_aw, path=["response"]
            )

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_storage_profiles_aws(self, async_client: AsyncVraIaas) -> None:
        storage_profiles_aw = await async_client.iaas.api.storage_profiles_aws.storage_profiles_aws(
            device_type="ebs / instance-store",
            name="name",
            region_id="31186",
        )
        assert_matches_type(AwsStorageProfile, storage_profiles_aw, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_storage_profiles_aws_with_all_params(self, async_client: AsyncVraIaas) -> None:
        storage_profiles_aw = await async_client.iaas.api.storage_profiles_aws.storage_profiles_aws(
            device_type="ebs / instance-store",
            name="name",
            region_id="31186",
            api_version="apiVersion",
            default_item=True,
            description="description",
            iops="2000",
            supports_encryption=False,
            tags=[
                {
                    "key": "tier",
                    "value": "silver",
                }
            ],
            volume_type="gp3 / io2 / gp2 / io1 / sc1 / st1 / standard",
        )
        assert_matches_type(AwsStorageProfile, storage_profiles_aw, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_storage_profiles_aws(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.storage_profiles_aws.with_raw_response.storage_profiles_aws(
            device_type="ebs / instance-store",
            name="name",
            region_id="31186",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        storage_profiles_aw = await response.parse()
        assert_matches_type(AwsStorageProfile, storage_profiles_aw, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_storage_profiles_aws(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.storage_profiles_aws.with_streaming_response.storage_profiles_aws(
            device_type="ebs / instance-store",
            name="name",
            region_id="31186",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            storage_profiles_aw = await response.parse()
            assert_matches_type(AwsStorageProfile, storage_profiles_aw, path=["response"])

        assert cast(Any, response.is_closed) is True
