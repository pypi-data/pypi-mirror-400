# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from vra_iaas import VraIaas, AsyncVraIaas
from tests.utils import assert_matches_type
from vra_iaas.types.iaas.api import (
    CloudAccountAws,
    CloudAccountsAwRetrieveCloudAccountsAwsResponse,
)
from vra_iaas.types.iaas.api.projects import RequestTracker

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestCloudAccountsAws:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve(self, client: VraIaas) -> None:
        cloud_accounts_aw = client.iaas.api.cloud_accounts_aws.retrieve(
            id="id",
        )
        assert_matches_type(CloudAccountAws, cloud_accounts_aw, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_with_all_params(self, client: VraIaas) -> None:
        cloud_accounts_aw = client.iaas.api.cloud_accounts_aws.retrieve(
            id="id",
            api_version="apiVersion",
        )
        assert_matches_type(CloudAccountAws, cloud_accounts_aw, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve(self, client: VraIaas) -> None:
        response = client.iaas.api.cloud_accounts_aws.with_raw_response.retrieve(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        cloud_accounts_aw = response.parse()
        assert_matches_type(CloudAccountAws, cloud_accounts_aw, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve(self, client: VraIaas) -> None:
        with client.iaas.api.cloud_accounts_aws.with_streaming_response.retrieve(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            cloud_accounts_aw = response.parse()
            assert_matches_type(CloudAccountAws, cloud_accounts_aw, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve(self, client: VraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.iaas.api.cloud_accounts_aws.with_raw_response.retrieve(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update(self, client: VraIaas) -> None:
        cloud_accounts_aw = client.iaas.api.cloud_accounts_aws.update(
            id="id",
            api_version="apiVersion",
            name="name",
        )
        assert_matches_type(RequestTracker, cloud_accounts_aw, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update_with_all_params(self, client: VraIaas) -> None:
        cloud_accounts_aw = client.iaas.api.cloud_accounts_aws.update(
            id="id",
            api_version="apiVersion",
            name="name",
            access_key_id="ACDC55DB4MFH6ADG75KK",
            create_default_zones=True,
            description="description",
            iam_role_arn="arn:aws:iam::<account>:role/AriaAuto",
            regions=[
                {
                    "external_region_id": "eu-west-1",
                    "name": "eu-west-1",
                }
            ],
            secret_access_key="gfsScK345sGGaVdds222dasdfDDSSasdfdsa34fS",
            tags=[
                {
                    "key": "env",
                    "value": "dev",
                }
            ],
            trusted_account=True,
        )
        assert_matches_type(RequestTracker, cloud_accounts_aw, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_update(self, client: VraIaas) -> None:
        response = client.iaas.api.cloud_accounts_aws.with_raw_response.update(
            id="id",
            api_version="apiVersion",
            name="name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        cloud_accounts_aw = response.parse()
        assert_matches_type(RequestTracker, cloud_accounts_aw, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_update(self, client: VraIaas) -> None:
        with client.iaas.api.cloud_accounts_aws.with_streaming_response.update(
            id="id",
            api_version="apiVersion",
            name="name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            cloud_accounts_aw = response.parse()
            assert_matches_type(RequestTracker, cloud_accounts_aw, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_update(self, client: VraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.iaas.api.cloud_accounts_aws.with_raw_response.update(
                id="",
                api_version="apiVersion",
                name="name",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete(self, client: VraIaas) -> None:
        cloud_accounts_aw = client.iaas.api.cloud_accounts_aws.delete(
            id="id",
            api_version="apiVersion",
        )
        assert_matches_type(RequestTracker, cloud_accounts_aw, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_delete(self, client: VraIaas) -> None:
        response = client.iaas.api.cloud_accounts_aws.with_raw_response.delete(
            id="id",
            api_version="apiVersion",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        cloud_accounts_aw = response.parse()
        assert_matches_type(RequestTracker, cloud_accounts_aw, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_delete(self, client: VraIaas) -> None:
        with client.iaas.api.cloud_accounts_aws.with_streaming_response.delete(
            id="id",
            api_version="apiVersion",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            cloud_accounts_aw = response.parse()
            assert_matches_type(RequestTracker, cloud_accounts_aw, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_delete(self, client: VraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.iaas.api.cloud_accounts_aws.with_raw_response.delete(
                id="",
                api_version="apiVersion",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_cloud_accounts_aws(self, client: VraIaas) -> None:
        cloud_accounts_aw = client.iaas.api.cloud_accounts_aws.cloud_accounts_aws(
            api_version="apiVersion",
            name="name",
        )
        assert_matches_type(RequestTracker, cloud_accounts_aw, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_cloud_accounts_aws_with_all_params(self, client: VraIaas) -> None:
        cloud_accounts_aw = client.iaas.api.cloud_accounts_aws.cloud_accounts_aws(
            api_version="apiVersion",
            name="name",
            validate_only="validateOnly",
            access_key_id="ACDC55DB4MFH6ADG75KK",
            create_default_zones=True,
            description="description",
            iam_role_arn="arn:aws:iam::<account>:role/AriaAuto",
            regions=[
                {
                    "external_region_id": "eu-west-1",
                    "name": "eu-west-1",
                }
            ],
            secret_access_key="gfsScK345sGGaVdds222dasdfDDSSasdfdsa34fS",
            tags=[
                {
                    "key": "env",
                    "value": "dev",
                }
            ],
            trusted_account=True,
        )
        assert_matches_type(RequestTracker, cloud_accounts_aw, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_cloud_accounts_aws(self, client: VraIaas) -> None:
        response = client.iaas.api.cloud_accounts_aws.with_raw_response.cloud_accounts_aws(
            api_version="apiVersion",
            name="name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        cloud_accounts_aw = response.parse()
        assert_matches_type(RequestTracker, cloud_accounts_aw, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_cloud_accounts_aws(self, client: VraIaas) -> None:
        with client.iaas.api.cloud_accounts_aws.with_streaming_response.cloud_accounts_aws(
            api_version="apiVersion",
            name="name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            cloud_accounts_aw = response.parse()
            assert_matches_type(RequestTracker, cloud_accounts_aw, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_private_image_enumeration(self, client: VraIaas) -> None:
        cloud_accounts_aw = client.iaas.api.cloud_accounts_aws.private_image_enumeration(
            id="id",
        )
        assert_matches_type(RequestTracker, cloud_accounts_aw, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_private_image_enumeration_with_all_params(self, client: VraIaas) -> None:
        cloud_accounts_aw = client.iaas.api.cloud_accounts_aws.private_image_enumeration(
            id="id",
            api_version="apiVersion",
        )
        assert_matches_type(RequestTracker, cloud_accounts_aw, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_private_image_enumeration(self, client: VraIaas) -> None:
        response = client.iaas.api.cloud_accounts_aws.with_raw_response.private_image_enumeration(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        cloud_accounts_aw = response.parse()
        assert_matches_type(RequestTracker, cloud_accounts_aw, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_private_image_enumeration(self, client: VraIaas) -> None:
        with client.iaas.api.cloud_accounts_aws.with_streaming_response.private_image_enumeration(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            cloud_accounts_aw = response.parse()
            assert_matches_type(RequestTracker, cloud_accounts_aw, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_private_image_enumeration(self, client: VraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.iaas.api.cloud_accounts_aws.with_raw_response.private_image_enumeration(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_region_enumeration(self, client: VraIaas) -> None:
        cloud_accounts_aw = client.iaas.api.cloud_accounts_aws.region_enumeration(
            api_version="apiVersion",
        )
        assert_matches_type(RequestTracker, cloud_accounts_aw, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_region_enumeration_with_all_params(self, client: VraIaas) -> None:
        cloud_accounts_aw = client.iaas.api.cloud_accounts_aws.region_enumeration(
            api_version="apiVersion",
            access_key_id="ACDC55DB4MFH6ADG75KK",
            cloud_account_id="b8b7a918-342e-4a53-a3b0-b935da0fe601",
            secret_access_key="gfsScK345sGGaVdds222dasdfDDSSasdfdsa34fS",
        )
        assert_matches_type(RequestTracker, cloud_accounts_aw, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_region_enumeration(self, client: VraIaas) -> None:
        response = client.iaas.api.cloud_accounts_aws.with_raw_response.region_enumeration(
            api_version="apiVersion",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        cloud_accounts_aw = response.parse()
        assert_matches_type(RequestTracker, cloud_accounts_aw, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_region_enumeration(self, client: VraIaas) -> None:
        with client.iaas.api.cloud_accounts_aws.with_streaming_response.region_enumeration(
            api_version="apiVersion",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            cloud_accounts_aw = response.parse()
            assert_matches_type(RequestTracker, cloud_accounts_aw, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_cloud_accounts_aws(self, client: VraIaas) -> None:
        cloud_accounts_aw = client.iaas.api.cloud_accounts_aws.retrieve_cloud_accounts_aws()
        assert_matches_type(CloudAccountsAwRetrieveCloudAccountsAwsResponse, cloud_accounts_aw, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_cloud_accounts_aws_with_all_params(self, client: VraIaas) -> None:
        cloud_accounts_aw = client.iaas.api.cloud_accounts_aws.retrieve_cloud_accounts_aws(
            skip=0,
            top=0,
            api_version="apiVersion",
        )
        assert_matches_type(CloudAccountsAwRetrieveCloudAccountsAwsResponse, cloud_accounts_aw, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve_cloud_accounts_aws(self, client: VraIaas) -> None:
        response = client.iaas.api.cloud_accounts_aws.with_raw_response.retrieve_cloud_accounts_aws()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        cloud_accounts_aw = response.parse()
        assert_matches_type(CloudAccountsAwRetrieveCloudAccountsAwsResponse, cloud_accounts_aw, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve_cloud_accounts_aws(self, client: VraIaas) -> None:
        with client.iaas.api.cloud_accounts_aws.with_streaming_response.retrieve_cloud_accounts_aws() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            cloud_accounts_aw = response.parse()
            assert_matches_type(CloudAccountsAwRetrieveCloudAccountsAwsResponse, cloud_accounts_aw, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncCloudAccountsAws:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncVraIaas) -> None:
        cloud_accounts_aw = await async_client.iaas.api.cloud_accounts_aws.retrieve(
            id="id",
        )
        assert_matches_type(CloudAccountAws, cloud_accounts_aw, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_with_all_params(self, async_client: AsyncVraIaas) -> None:
        cloud_accounts_aw = await async_client.iaas.api.cloud_accounts_aws.retrieve(
            id="id",
            api_version="apiVersion",
        )
        assert_matches_type(CloudAccountAws, cloud_accounts_aw, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.cloud_accounts_aws.with_raw_response.retrieve(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        cloud_accounts_aw = await response.parse()
        assert_matches_type(CloudAccountAws, cloud_accounts_aw, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.cloud_accounts_aws.with_streaming_response.retrieve(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            cloud_accounts_aw = await response.parse()
            assert_matches_type(CloudAccountAws, cloud_accounts_aw, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncVraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.iaas.api.cloud_accounts_aws.with_raw_response.retrieve(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update(self, async_client: AsyncVraIaas) -> None:
        cloud_accounts_aw = await async_client.iaas.api.cloud_accounts_aws.update(
            id="id",
            api_version="apiVersion",
            name="name",
        )
        assert_matches_type(RequestTracker, cloud_accounts_aw, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncVraIaas) -> None:
        cloud_accounts_aw = await async_client.iaas.api.cloud_accounts_aws.update(
            id="id",
            api_version="apiVersion",
            name="name",
            access_key_id="ACDC55DB4MFH6ADG75KK",
            create_default_zones=True,
            description="description",
            iam_role_arn="arn:aws:iam::<account>:role/AriaAuto",
            regions=[
                {
                    "external_region_id": "eu-west-1",
                    "name": "eu-west-1",
                }
            ],
            secret_access_key="gfsScK345sGGaVdds222dasdfDDSSasdfdsa34fS",
            tags=[
                {
                    "key": "env",
                    "value": "dev",
                }
            ],
            trusted_account=True,
        )
        assert_matches_type(RequestTracker, cloud_accounts_aw, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_update(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.cloud_accounts_aws.with_raw_response.update(
            id="id",
            api_version="apiVersion",
            name="name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        cloud_accounts_aw = await response.parse()
        assert_matches_type(RequestTracker, cloud_accounts_aw, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.cloud_accounts_aws.with_streaming_response.update(
            id="id",
            api_version="apiVersion",
            name="name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            cloud_accounts_aw = await response.parse()
            assert_matches_type(RequestTracker, cloud_accounts_aw, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_update(self, async_client: AsyncVraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.iaas.api.cloud_accounts_aws.with_raw_response.update(
                id="",
                api_version="apiVersion",
                name="name",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete(self, async_client: AsyncVraIaas) -> None:
        cloud_accounts_aw = await async_client.iaas.api.cloud_accounts_aws.delete(
            id="id",
            api_version="apiVersion",
        )
        assert_matches_type(RequestTracker, cloud_accounts_aw, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.cloud_accounts_aws.with_raw_response.delete(
            id="id",
            api_version="apiVersion",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        cloud_accounts_aw = await response.parse()
        assert_matches_type(RequestTracker, cloud_accounts_aw, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.cloud_accounts_aws.with_streaming_response.delete(
            id="id",
            api_version="apiVersion",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            cloud_accounts_aw = await response.parse()
            assert_matches_type(RequestTracker, cloud_accounts_aw, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_delete(self, async_client: AsyncVraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.iaas.api.cloud_accounts_aws.with_raw_response.delete(
                id="",
                api_version="apiVersion",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_cloud_accounts_aws(self, async_client: AsyncVraIaas) -> None:
        cloud_accounts_aw = await async_client.iaas.api.cloud_accounts_aws.cloud_accounts_aws(
            api_version="apiVersion",
            name="name",
        )
        assert_matches_type(RequestTracker, cloud_accounts_aw, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_cloud_accounts_aws_with_all_params(self, async_client: AsyncVraIaas) -> None:
        cloud_accounts_aw = await async_client.iaas.api.cloud_accounts_aws.cloud_accounts_aws(
            api_version="apiVersion",
            name="name",
            validate_only="validateOnly",
            access_key_id="ACDC55DB4MFH6ADG75KK",
            create_default_zones=True,
            description="description",
            iam_role_arn="arn:aws:iam::<account>:role/AriaAuto",
            regions=[
                {
                    "external_region_id": "eu-west-1",
                    "name": "eu-west-1",
                }
            ],
            secret_access_key="gfsScK345sGGaVdds222dasdfDDSSasdfdsa34fS",
            tags=[
                {
                    "key": "env",
                    "value": "dev",
                }
            ],
            trusted_account=True,
        )
        assert_matches_type(RequestTracker, cloud_accounts_aw, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_cloud_accounts_aws(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.cloud_accounts_aws.with_raw_response.cloud_accounts_aws(
            api_version="apiVersion",
            name="name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        cloud_accounts_aw = await response.parse()
        assert_matches_type(RequestTracker, cloud_accounts_aw, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_cloud_accounts_aws(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.cloud_accounts_aws.with_streaming_response.cloud_accounts_aws(
            api_version="apiVersion",
            name="name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            cloud_accounts_aw = await response.parse()
            assert_matches_type(RequestTracker, cloud_accounts_aw, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_private_image_enumeration(self, async_client: AsyncVraIaas) -> None:
        cloud_accounts_aw = await async_client.iaas.api.cloud_accounts_aws.private_image_enumeration(
            id="id",
        )
        assert_matches_type(RequestTracker, cloud_accounts_aw, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_private_image_enumeration_with_all_params(self, async_client: AsyncVraIaas) -> None:
        cloud_accounts_aw = await async_client.iaas.api.cloud_accounts_aws.private_image_enumeration(
            id="id",
            api_version="apiVersion",
        )
        assert_matches_type(RequestTracker, cloud_accounts_aw, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_private_image_enumeration(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.cloud_accounts_aws.with_raw_response.private_image_enumeration(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        cloud_accounts_aw = await response.parse()
        assert_matches_type(RequestTracker, cloud_accounts_aw, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_private_image_enumeration(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.cloud_accounts_aws.with_streaming_response.private_image_enumeration(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            cloud_accounts_aw = await response.parse()
            assert_matches_type(RequestTracker, cloud_accounts_aw, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_private_image_enumeration(self, async_client: AsyncVraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.iaas.api.cloud_accounts_aws.with_raw_response.private_image_enumeration(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_region_enumeration(self, async_client: AsyncVraIaas) -> None:
        cloud_accounts_aw = await async_client.iaas.api.cloud_accounts_aws.region_enumeration(
            api_version="apiVersion",
        )
        assert_matches_type(RequestTracker, cloud_accounts_aw, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_region_enumeration_with_all_params(self, async_client: AsyncVraIaas) -> None:
        cloud_accounts_aw = await async_client.iaas.api.cloud_accounts_aws.region_enumeration(
            api_version="apiVersion",
            access_key_id="ACDC55DB4MFH6ADG75KK",
            cloud_account_id="b8b7a918-342e-4a53-a3b0-b935da0fe601",
            secret_access_key="gfsScK345sGGaVdds222dasdfDDSSasdfdsa34fS",
        )
        assert_matches_type(RequestTracker, cloud_accounts_aw, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_region_enumeration(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.cloud_accounts_aws.with_raw_response.region_enumeration(
            api_version="apiVersion",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        cloud_accounts_aw = await response.parse()
        assert_matches_type(RequestTracker, cloud_accounts_aw, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_region_enumeration(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.cloud_accounts_aws.with_streaming_response.region_enumeration(
            api_version="apiVersion",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            cloud_accounts_aw = await response.parse()
            assert_matches_type(RequestTracker, cloud_accounts_aw, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_cloud_accounts_aws(self, async_client: AsyncVraIaas) -> None:
        cloud_accounts_aw = await async_client.iaas.api.cloud_accounts_aws.retrieve_cloud_accounts_aws()
        assert_matches_type(CloudAccountsAwRetrieveCloudAccountsAwsResponse, cloud_accounts_aw, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_cloud_accounts_aws_with_all_params(self, async_client: AsyncVraIaas) -> None:
        cloud_accounts_aw = await async_client.iaas.api.cloud_accounts_aws.retrieve_cloud_accounts_aws(
            skip=0,
            top=0,
            api_version="apiVersion",
        )
        assert_matches_type(CloudAccountsAwRetrieveCloudAccountsAwsResponse, cloud_accounts_aw, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve_cloud_accounts_aws(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.cloud_accounts_aws.with_raw_response.retrieve_cloud_accounts_aws()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        cloud_accounts_aw = await response.parse()
        assert_matches_type(CloudAccountsAwRetrieveCloudAccountsAwsResponse, cloud_accounts_aw, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve_cloud_accounts_aws(self, async_client: AsyncVraIaas) -> None:
        async with (
            async_client.iaas.api.cloud_accounts_aws.with_streaming_response.retrieve_cloud_accounts_aws()
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            cloud_accounts_aw = await response.parse()
            assert_matches_type(CloudAccountsAwRetrieveCloudAccountsAwsResponse, cloud_accounts_aw, path=["response"])

        assert cast(Any, response.is_closed) is True
