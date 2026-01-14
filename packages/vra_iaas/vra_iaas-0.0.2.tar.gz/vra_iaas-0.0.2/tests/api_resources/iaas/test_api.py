# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from vra_iaas import VraIaas, AsyncVraIaas
from tests.utils import assert_matches_type
from vra_iaas.types.iaas import (
    APILoginResponse,
    APIRetrieveResponse,
    APIRetrieveAboutResponse,
    APIRetrieveImagesResponse,
    APIRetrieveFlavorsResponse,
    APIRetrieveFoldersResponse,
    APIRetrieveEventLogsResponse,
    APIRetrieveRequestGraphResponse,
    APIRetrieveFabricFlavorsResponse,
    APIRetrieveFabricAwsVolumeTypesResponse,
    APIRetrieveFabricAzureDiskEncryptionSetsResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestAPI:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve(self, client: VraIaas) -> None:
        api = client.iaas.api.retrieve(
            id="id",
            api_version="apiVersion",
        )
        assert_matches_type(APIRetrieveResponse, api, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve(self, client: VraIaas) -> None:
        response = client.iaas.api.with_raw_response.retrieve(
            id="id",
            api_version="apiVersion",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        api = response.parse()
        assert_matches_type(APIRetrieveResponse, api, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve(self, client: VraIaas) -> None:
        with client.iaas.api.with_streaming_response.retrieve(
            id="id",
            api_version="apiVersion",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            api = response.parse()
            assert_matches_type(APIRetrieveResponse, api, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve(self, client: VraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.iaas.api.with_raw_response.retrieve(
                id="",
                api_version="apiVersion",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_login(self, client: VraIaas) -> None:
        api = client.iaas.api.login(
            refresh_token="5e7c2c-9a9e-4b0-9339-a7f94",
        )
        assert_matches_type(APILoginResponse, api, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_login_with_all_params(self, client: VraIaas) -> None:
        api = client.iaas.api.login(
            refresh_token="5e7c2c-9a9e-4b0-9339-a7f94",
            api_version="apiVersion",
        )
        assert_matches_type(APILoginResponse, api, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_login(self, client: VraIaas) -> None:
        response = client.iaas.api.with_raw_response.login(
            refresh_token="5e7c2c-9a9e-4b0-9339-a7f94",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        api = response.parse()
        assert_matches_type(APILoginResponse, api, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_login(self, client: VraIaas) -> None:
        with client.iaas.api.with_streaming_response.login(
            refresh_token="5e7c2c-9a9e-4b0-9339-a7f94",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            api = response.parse()
            assert_matches_type(APILoginResponse, api, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_about(self, client: VraIaas) -> None:
        api = client.iaas.api.retrieve_about()
        assert_matches_type(APIRetrieveAboutResponse, api, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve_about(self, client: VraIaas) -> None:
        response = client.iaas.api.with_raw_response.retrieve_about()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        api = response.parse()
        assert_matches_type(APIRetrieveAboutResponse, api, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve_about(self, client: VraIaas) -> None:
        with client.iaas.api.with_streaming_response.retrieve_about() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            api = response.parse()
            assert_matches_type(APIRetrieveAboutResponse, api, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_event_logs(self, client: VraIaas) -> None:
        api = client.iaas.api.retrieve_event_logs()
        assert_matches_type(APIRetrieveEventLogsResponse, api, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_event_logs_with_all_params(self, client: VraIaas) -> None:
        api = client.iaas.api.retrieve_event_logs(
            count=True,
            filter="$filter",
            select="$select",
            skip=0,
            top=0,
            api_version="apiVersion",
            end_date="endDate",
            start_date="startDate",
        )
        assert_matches_type(APIRetrieveEventLogsResponse, api, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve_event_logs(self, client: VraIaas) -> None:
        response = client.iaas.api.with_raw_response.retrieve_event_logs()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        api = response.parse()
        assert_matches_type(APIRetrieveEventLogsResponse, api, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve_event_logs(self, client: VraIaas) -> None:
        with client.iaas.api.with_streaming_response.retrieve_event_logs() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            api = response.parse()
            assert_matches_type(APIRetrieveEventLogsResponse, api, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_fabric_aws_volume_types(self, client: VraIaas) -> None:
        api = client.iaas.api.retrieve_fabric_aws_volume_types()
        assert_matches_type(APIRetrieveFabricAwsVolumeTypesResponse, api, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_fabric_aws_volume_types_with_all_params(self, client: VraIaas) -> None:
        api = client.iaas.api.retrieve_fabric_aws_volume_types(
            api_version="apiVersion",
        )
        assert_matches_type(APIRetrieveFabricAwsVolumeTypesResponse, api, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve_fabric_aws_volume_types(self, client: VraIaas) -> None:
        response = client.iaas.api.with_raw_response.retrieve_fabric_aws_volume_types()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        api = response.parse()
        assert_matches_type(APIRetrieveFabricAwsVolumeTypesResponse, api, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve_fabric_aws_volume_types(self, client: VraIaas) -> None:
        with client.iaas.api.with_streaming_response.retrieve_fabric_aws_volume_types() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            api = response.parse()
            assert_matches_type(APIRetrieveFabricAwsVolumeTypesResponse, api, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_fabric_azure_disk_encryption_sets(self, client: VraIaas) -> None:
        api = client.iaas.api.retrieve_fabric_azure_disk_encryption_sets(
            region_id="regionId",
        )
        assert_matches_type(APIRetrieveFabricAzureDiskEncryptionSetsResponse, api, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_fabric_azure_disk_encryption_sets_with_all_params(self, client: VraIaas) -> None:
        api = client.iaas.api.retrieve_fabric_azure_disk_encryption_sets(
            region_id="regionId",
            api_version="apiVersion",
        )
        assert_matches_type(APIRetrieveFabricAzureDiskEncryptionSetsResponse, api, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve_fabric_azure_disk_encryption_sets(self, client: VraIaas) -> None:
        response = client.iaas.api.with_raw_response.retrieve_fabric_azure_disk_encryption_sets(
            region_id="regionId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        api = response.parse()
        assert_matches_type(APIRetrieveFabricAzureDiskEncryptionSetsResponse, api, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve_fabric_azure_disk_encryption_sets(self, client: VraIaas) -> None:
        with client.iaas.api.with_streaming_response.retrieve_fabric_azure_disk_encryption_sets(
            region_id="regionId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            api = response.parse()
            assert_matches_type(APIRetrieveFabricAzureDiskEncryptionSetsResponse, api, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_fabric_flavors(self, client: VraIaas) -> None:
        api = client.iaas.api.retrieve_fabric_flavors()
        assert_matches_type(APIRetrieveFabricFlavorsResponse, api, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_fabric_flavors_with_all_params(self, client: VraIaas) -> None:
        api = client.iaas.api.retrieve_fabric_flavors(
            api_version="apiVersion",
            include_cores=True,
        )
        assert_matches_type(APIRetrieveFabricFlavorsResponse, api, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve_fabric_flavors(self, client: VraIaas) -> None:
        response = client.iaas.api.with_raw_response.retrieve_fabric_flavors()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        api = response.parse()
        assert_matches_type(APIRetrieveFabricFlavorsResponse, api, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve_fabric_flavors(self, client: VraIaas) -> None:
        with client.iaas.api.with_streaming_response.retrieve_fabric_flavors() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            api = response.parse()
            assert_matches_type(APIRetrieveFabricFlavorsResponse, api, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_flavors(self, client: VraIaas) -> None:
        api = client.iaas.api.retrieve_flavors()
        assert_matches_type(APIRetrieveFlavorsResponse, api, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_flavors_with_all_params(self, client: VraIaas) -> None:
        api = client.iaas.api.retrieve_flavors(
            api_version="apiVersion",
            include_cores=True,
        )
        assert_matches_type(APIRetrieveFlavorsResponse, api, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve_flavors(self, client: VraIaas) -> None:
        response = client.iaas.api.with_raw_response.retrieve_flavors()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        api = response.parse()
        assert_matches_type(APIRetrieveFlavorsResponse, api, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve_flavors(self, client: VraIaas) -> None:
        with client.iaas.api.with_streaming_response.retrieve_flavors() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            api = response.parse()
            assert_matches_type(APIRetrieveFlavorsResponse, api, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_folders(self, client: VraIaas) -> None:
        api = client.iaas.api.retrieve_folders(
            api_version="apiVersion",
        )
        assert_matches_type(APIRetrieveFoldersResponse, api, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_folders_with_all_params(self, client: VraIaas) -> None:
        api = client.iaas.api.retrieve_folders(
            api_version="apiVersion",
            count=True,
            filter="$filter",
            select="$select",
            skip=0,
            top=0,
            cloud_account_id="cloudAccountId",
            external_region_id="externalRegionId",
        )
        assert_matches_type(APIRetrieveFoldersResponse, api, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve_folders(self, client: VraIaas) -> None:
        response = client.iaas.api.with_raw_response.retrieve_folders(
            api_version="apiVersion",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        api = response.parse()
        assert_matches_type(APIRetrieveFoldersResponse, api, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve_folders(self, client: VraIaas) -> None:
        with client.iaas.api.with_streaming_response.retrieve_folders(
            api_version="apiVersion",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            api = response.parse()
            assert_matches_type(APIRetrieveFoldersResponse, api, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_images(self, client: VraIaas) -> None:
        api = client.iaas.api.retrieve_images()
        assert_matches_type(APIRetrieveImagesResponse, api, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_images_with_all_params(self, client: VraIaas) -> None:
        api = client.iaas.api.retrieve_images(
            api_version="apiVersion",
        )
        assert_matches_type(APIRetrieveImagesResponse, api, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve_images(self, client: VraIaas) -> None:
        response = client.iaas.api.with_raw_response.retrieve_images()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        api = response.parse()
        assert_matches_type(APIRetrieveImagesResponse, api, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve_images(self, client: VraIaas) -> None:
        with client.iaas.api.with_streaming_response.retrieve_images() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            api = response.parse()
            assert_matches_type(APIRetrieveImagesResponse, api, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_request_graph(self, client: VraIaas) -> None:
        api = client.iaas.api.retrieve_request_graph(
            deployment_id="deploymentId",
            flow_id="flowId",
        )
        assert_matches_type(APIRetrieveRequestGraphResponse, api, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_request_graph_with_all_params(self, client: VraIaas) -> None:
        api = client.iaas.api.retrieve_request_graph(
            deployment_id="deploymentId",
            flow_id="flowId",
            api_version="apiVersion",
        )
        assert_matches_type(APIRetrieveRequestGraphResponse, api, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve_request_graph(self, client: VraIaas) -> None:
        response = client.iaas.api.with_raw_response.retrieve_request_graph(
            deployment_id="deploymentId",
            flow_id="flowId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        api = response.parse()
        assert_matches_type(APIRetrieveRequestGraphResponse, api, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve_request_graph(self, client: VraIaas) -> None:
        with client.iaas.api.with_streaming_response.retrieve_request_graph(
            deployment_id="deploymentId",
            flow_id="flowId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            api = response.parse()
            assert_matches_type(APIRetrieveRequestGraphResponse, api, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncAPI:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncVraIaas) -> None:
        api = await async_client.iaas.api.retrieve(
            id="id",
            api_version="apiVersion",
        )
        assert_matches_type(APIRetrieveResponse, api, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.with_raw_response.retrieve(
            id="id",
            api_version="apiVersion",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        api = await response.parse()
        assert_matches_type(APIRetrieveResponse, api, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.with_streaming_response.retrieve(
            id="id",
            api_version="apiVersion",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            api = await response.parse()
            assert_matches_type(APIRetrieveResponse, api, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncVraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.iaas.api.with_raw_response.retrieve(
                id="",
                api_version="apiVersion",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_login(self, async_client: AsyncVraIaas) -> None:
        api = await async_client.iaas.api.login(
            refresh_token="5e7c2c-9a9e-4b0-9339-a7f94",
        )
        assert_matches_type(APILoginResponse, api, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_login_with_all_params(self, async_client: AsyncVraIaas) -> None:
        api = await async_client.iaas.api.login(
            refresh_token="5e7c2c-9a9e-4b0-9339-a7f94",
            api_version="apiVersion",
        )
        assert_matches_type(APILoginResponse, api, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_login(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.with_raw_response.login(
            refresh_token="5e7c2c-9a9e-4b0-9339-a7f94",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        api = await response.parse()
        assert_matches_type(APILoginResponse, api, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_login(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.with_streaming_response.login(
            refresh_token="5e7c2c-9a9e-4b0-9339-a7f94",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            api = await response.parse()
            assert_matches_type(APILoginResponse, api, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_about(self, async_client: AsyncVraIaas) -> None:
        api = await async_client.iaas.api.retrieve_about()
        assert_matches_type(APIRetrieveAboutResponse, api, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve_about(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.with_raw_response.retrieve_about()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        api = await response.parse()
        assert_matches_type(APIRetrieveAboutResponse, api, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve_about(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.with_streaming_response.retrieve_about() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            api = await response.parse()
            assert_matches_type(APIRetrieveAboutResponse, api, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_event_logs(self, async_client: AsyncVraIaas) -> None:
        api = await async_client.iaas.api.retrieve_event_logs()
        assert_matches_type(APIRetrieveEventLogsResponse, api, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_event_logs_with_all_params(self, async_client: AsyncVraIaas) -> None:
        api = await async_client.iaas.api.retrieve_event_logs(
            count=True,
            filter="$filter",
            select="$select",
            skip=0,
            top=0,
            api_version="apiVersion",
            end_date="endDate",
            start_date="startDate",
        )
        assert_matches_type(APIRetrieveEventLogsResponse, api, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve_event_logs(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.with_raw_response.retrieve_event_logs()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        api = await response.parse()
        assert_matches_type(APIRetrieveEventLogsResponse, api, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve_event_logs(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.with_streaming_response.retrieve_event_logs() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            api = await response.parse()
            assert_matches_type(APIRetrieveEventLogsResponse, api, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_fabric_aws_volume_types(self, async_client: AsyncVraIaas) -> None:
        api = await async_client.iaas.api.retrieve_fabric_aws_volume_types()
        assert_matches_type(APIRetrieveFabricAwsVolumeTypesResponse, api, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_fabric_aws_volume_types_with_all_params(self, async_client: AsyncVraIaas) -> None:
        api = await async_client.iaas.api.retrieve_fabric_aws_volume_types(
            api_version="apiVersion",
        )
        assert_matches_type(APIRetrieveFabricAwsVolumeTypesResponse, api, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve_fabric_aws_volume_types(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.with_raw_response.retrieve_fabric_aws_volume_types()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        api = await response.parse()
        assert_matches_type(APIRetrieveFabricAwsVolumeTypesResponse, api, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve_fabric_aws_volume_types(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.with_streaming_response.retrieve_fabric_aws_volume_types() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            api = await response.parse()
            assert_matches_type(APIRetrieveFabricAwsVolumeTypesResponse, api, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_fabric_azure_disk_encryption_sets(self, async_client: AsyncVraIaas) -> None:
        api = await async_client.iaas.api.retrieve_fabric_azure_disk_encryption_sets(
            region_id="regionId",
        )
        assert_matches_type(APIRetrieveFabricAzureDiskEncryptionSetsResponse, api, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_fabric_azure_disk_encryption_sets_with_all_params(
        self, async_client: AsyncVraIaas
    ) -> None:
        api = await async_client.iaas.api.retrieve_fabric_azure_disk_encryption_sets(
            region_id="regionId",
            api_version="apiVersion",
        )
        assert_matches_type(APIRetrieveFabricAzureDiskEncryptionSetsResponse, api, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve_fabric_azure_disk_encryption_sets(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.with_raw_response.retrieve_fabric_azure_disk_encryption_sets(
            region_id="regionId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        api = await response.parse()
        assert_matches_type(APIRetrieveFabricAzureDiskEncryptionSetsResponse, api, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve_fabric_azure_disk_encryption_sets(
        self, async_client: AsyncVraIaas
    ) -> None:
        async with async_client.iaas.api.with_streaming_response.retrieve_fabric_azure_disk_encryption_sets(
            region_id="regionId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            api = await response.parse()
            assert_matches_type(APIRetrieveFabricAzureDiskEncryptionSetsResponse, api, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_fabric_flavors(self, async_client: AsyncVraIaas) -> None:
        api = await async_client.iaas.api.retrieve_fabric_flavors()
        assert_matches_type(APIRetrieveFabricFlavorsResponse, api, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_fabric_flavors_with_all_params(self, async_client: AsyncVraIaas) -> None:
        api = await async_client.iaas.api.retrieve_fabric_flavors(
            api_version="apiVersion",
            include_cores=True,
        )
        assert_matches_type(APIRetrieveFabricFlavorsResponse, api, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve_fabric_flavors(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.with_raw_response.retrieve_fabric_flavors()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        api = await response.parse()
        assert_matches_type(APIRetrieveFabricFlavorsResponse, api, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve_fabric_flavors(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.with_streaming_response.retrieve_fabric_flavors() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            api = await response.parse()
            assert_matches_type(APIRetrieveFabricFlavorsResponse, api, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_flavors(self, async_client: AsyncVraIaas) -> None:
        api = await async_client.iaas.api.retrieve_flavors()
        assert_matches_type(APIRetrieveFlavorsResponse, api, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_flavors_with_all_params(self, async_client: AsyncVraIaas) -> None:
        api = await async_client.iaas.api.retrieve_flavors(
            api_version="apiVersion",
            include_cores=True,
        )
        assert_matches_type(APIRetrieveFlavorsResponse, api, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve_flavors(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.with_raw_response.retrieve_flavors()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        api = await response.parse()
        assert_matches_type(APIRetrieveFlavorsResponse, api, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve_flavors(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.with_streaming_response.retrieve_flavors() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            api = await response.parse()
            assert_matches_type(APIRetrieveFlavorsResponse, api, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_folders(self, async_client: AsyncVraIaas) -> None:
        api = await async_client.iaas.api.retrieve_folders(
            api_version="apiVersion",
        )
        assert_matches_type(APIRetrieveFoldersResponse, api, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_folders_with_all_params(self, async_client: AsyncVraIaas) -> None:
        api = await async_client.iaas.api.retrieve_folders(
            api_version="apiVersion",
            count=True,
            filter="$filter",
            select="$select",
            skip=0,
            top=0,
            cloud_account_id="cloudAccountId",
            external_region_id="externalRegionId",
        )
        assert_matches_type(APIRetrieveFoldersResponse, api, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve_folders(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.with_raw_response.retrieve_folders(
            api_version="apiVersion",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        api = await response.parse()
        assert_matches_type(APIRetrieveFoldersResponse, api, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve_folders(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.with_streaming_response.retrieve_folders(
            api_version="apiVersion",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            api = await response.parse()
            assert_matches_type(APIRetrieveFoldersResponse, api, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_images(self, async_client: AsyncVraIaas) -> None:
        api = await async_client.iaas.api.retrieve_images()
        assert_matches_type(APIRetrieveImagesResponse, api, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_images_with_all_params(self, async_client: AsyncVraIaas) -> None:
        api = await async_client.iaas.api.retrieve_images(
            api_version="apiVersion",
        )
        assert_matches_type(APIRetrieveImagesResponse, api, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve_images(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.with_raw_response.retrieve_images()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        api = await response.parse()
        assert_matches_type(APIRetrieveImagesResponse, api, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve_images(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.with_streaming_response.retrieve_images() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            api = await response.parse()
            assert_matches_type(APIRetrieveImagesResponse, api, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_request_graph(self, async_client: AsyncVraIaas) -> None:
        api = await async_client.iaas.api.retrieve_request_graph(
            deployment_id="deploymentId",
            flow_id="flowId",
        )
        assert_matches_type(APIRetrieveRequestGraphResponse, api, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_request_graph_with_all_params(self, async_client: AsyncVraIaas) -> None:
        api = await async_client.iaas.api.retrieve_request_graph(
            deployment_id="deploymentId",
            flow_id="flowId",
            api_version="apiVersion",
        )
        assert_matches_type(APIRetrieveRequestGraphResponse, api, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve_request_graph(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.with_raw_response.retrieve_request_graph(
            deployment_id="deploymentId",
            flow_id="flowId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        api = await response.parse()
        assert_matches_type(APIRetrieveRequestGraphResponse, api, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve_request_graph(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.with_streaming_response.retrieve_request_graph(
            deployment_id="deploymentId",
            flow_id="flowId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            api = await response.parse()
            assert_matches_type(APIRetrieveRequestGraphResponse, api, path=["response"])

        assert cast(Any, response.is_closed) is True
