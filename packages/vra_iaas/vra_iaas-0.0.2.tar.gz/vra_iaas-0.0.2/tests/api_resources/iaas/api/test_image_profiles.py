# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from vra_iaas import VraIaas, AsyncVraIaas
from tests.utils import assert_matches_type
from vra_iaas.types.iaas.api import (
    ImageProfile,
    ImageProfileRetrieveImageProfilesResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestImageProfiles:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve(self, client: VraIaas) -> None:
        image_profile = client.iaas.api.image_profiles.retrieve(
            id="id",
        )
        assert_matches_type(ImageProfile, image_profile, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_with_all_params(self, client: VraIaas) -> None:
        image_profile = client.iaas.api.image_profiles.retrieve(
            id="id",
            api_version="apiVersion",
        )
        assert_matches_type(ImageProfile, image_profile, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve(self, client: VraIaas) -> None:
        response = client.iaas.api.image_profiles.with_raw_response.retrieve(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        image_profile = response.parse()
        assert_matches_type(ImageProfile, image_profile, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve(self, client: VraIaas) -> None:
        with client.iaas.api.image_profiles.with_streaming_response.retrieve(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            image_profile = response.parse()
            assert_matches_type(ImageProfile, image_profile, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve(self, client: VraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.iaas.api.image_profiles.with_raw_response.retrieve(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update(self, client: VraIaas) -> None:
        image_profile = client.iaas.api.image_profiles.update(
            id="id",
            image_mapping={
                "ubuntu": {},
                "centos": {},
            },
            name="name",
        )
        assert_matches_type(ImageProfile, image_profile, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update_with_all_params(self, client: VraIaas) -> None:
        image_profile = client.iaas.api.image_profiles.update(
            id="id",
            image_mapping={
                "ubuntu": {
                    "id": "9e49",
                    "cloud_config": 'runcmd:\n  - ["mkdir", "/imageFolder"]',
                    "constraints": [
                        {
                            "expression": "ha:strong",
                            "mandatory": True,
                        }
                    ],
                    "external_id": "https://cloud-images.ubuntu.com/releases/16.04/release-20190605/ubuntu-16.04-server-cloudimg-amd64.ova",
                    "name": "ami-ubuntu-16.04-1.9.1-00-1516139717",
                },
                "centos": {
                    "id": "9e50",
                    "cloud_config": 'runcmd:\n  - ["mkdir", "/imageFolder"]',
                    "constraints": [
                        {
                            "expression": "ha:strong",
                            "mandatory": True,
                        }
                    ],
                    "external_id": "https://cloud-images.ubuntu.com/releases/16.04/release-20190605/ubuntu-16.04-server-cloudimg-amd64.ova",
                    "name": "ami-centos-7-1.13.0-00-1543963388",
                },
            },
            name="name",
            api_version="apiVersion",
            description="description",
        )
        assert_matches_type(ImageProfile, image_profile, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_update(self, client: VraIaas) -> None:
        response = client.iaas.api.image_profiles.with_raw_response.update(
            id="id",
            image_mapping={
                "ubuntu": {},
                "centos": {},
            },
            name="name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        image_profile = response.parse()
        assert_matches_type(ImageProfile, image_profile, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_update(self, client: VraIaas) -> None:
        with client.iaas.api.image_profiles.with_streaming_response.update(
            id="id",
            image_mapping={
                "ubuntu": {},
                "centos": {},
            },
            name="name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            image_profile = response.parse()
            assert_matches_type(ImageProfile, image_profile, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_update(self, client: VraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.iaas.api.image_profiles.with_raw_response.update(
                id="",
                image_mapping={
                    "ubuntu": {},
                    "centos": {},
                },
                name="name",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete(self, client: VraIaas) -> None:
        image_profile = client.iaas.api.image_profiles.delete(
            id="id",
        )
        assert image_profile is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete_with_all_params(self, client: VraIaas) -> None:
        image_profile = client.iaas.api.image_profiles.delete(
            id="id",
            api_version="apiVersion",
        )
        assert image_profile is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_delete(self, client: VraIaas) -> None:
        response = client.iaas.api.image_profiles.with_raw_response.delete(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        image_profile = response.parse()
        assert image_profile is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_delete(self, client: VraIaas) -> None:
        with client.iaas.api.image_profiles.with_streaming_response.delete(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            image_profile = response.parse()
            assert image_profile is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_delete(self, client: VraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.iaas.api.image_profiles.with_raw_response.delete(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_image_profiles(self, client: VraIaas) -> None:
        image_profile = client.iaas.api.image_profiles.image_profiles(
            image_mapping={
                "ubuntu": {},
                "centos": {},
            },
            name="name",
            region_id="9.0E49",
        )
        assert_matches_type(ImageProfile, image_profile, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_image_profiles_with_all_params(self, client: VraIaas) -> None:
        image_profile = client.iaas.api.image_profiles.image_profiles(
            image_mapping={
                "ubuntu": {
                    "id": "9e49",
                    "cloud_config": 'runcmd:\n  - ["mkdir", "/imageFolder"]',
                    "constraints": [
                        {
                            "expression": "ha:strong",
                            "mandatory": True,
                        }
                    ],
                    "external_id": "https://cloud-images.ubuntu.com/releases/16.04/release-20190605/ubuntu-16.04-server-cloudimg-amd64.ova",
                    "name": "ami-ubuntu-16.04-1.9.1-00-1516139717",
                },
                "centos": {
                    "id": "9e50",
                    "cloud_config": 'runcmd:\n  - ["mkdir", "/imageFolder"]',
                    "constraints": [
                        {
                            "expression": "ha:strong",
                            "mandatory": True,
                        }
                    ],
                    "external_id": "https://cloud-images.ubuntu.com/releases/16.04/release-20190605/ubuntu-16.04-server-cloudimg-amd64.ova",
                    "name": "ami-centos-7-1.13.0-00-1543963388",
                },
            },
            name="name",
            region_id="9.0E49",
            api_version="apiVersion",
            description="description",
        )
        assert_matches_type(ImageProfile, image_profile, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_image_profiles(self, client: VraIaas) -> None:
        response = client.iaas.api.image_profiles.with_raw_response.image_profiles(
            image_mapping={
                "ubuntu": {},
                "centos": {},
            },
            name="name",
            region_id="9.0E49",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        image_profile = response.parse()
        assert_matches_type(ImageProfile, image_profile, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_image_profiles(self, client: VraIaas) -> None:
        with client.iaas.api.image_profiles.with_streaming_response.image_profiles(
            image_mapping={
                "ubuntu": {},
                "centos": {},
            },
            name="name",
            region_id="9.0E49",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            image_profile = response.parse()
            assert_matches_type(ImageProfile, image_profile, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_image_profiles(self, client: VraIaas) -> None:
        image_profile = client.iaas.api.image_profiles.retrieve_image_profiles()
        assert_matches_type(ImageProfileRetrieveImageProfilesResponse, image_profile, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_image_profiles_with_all_params(self, client: VraIaas) -> None:
        image_profile = client.iaas.api.image_profiles.retrieve_image_profiles(
            api_version="apiVersion",
        )
        assert_matches_type(ImageProfileRetrieveImageProfilesResponse, image_profile, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve_image_profiles(self, client: VraIaas) -> None:
        response = client.iaas.api.image_profiles.with_raw_response.retrieve_image_profiles()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        image_profile = response.parse()
        assert_matches_type(ImageProfileRetrieveImageProfilesResponse, image_profile, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve_image_profiles(self, client: VraIaas) -> None:
        with client.iaas.api.image_profiles.with_streaming_response.retrieve_image_profiles() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            image_profile = response.parse()
            assert_matches_type(ImageProfileRetrieveImageProfilesResponse, image_profile, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncImageProfiles:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncVraIaas) -> None:
        image_profile = await async_client.iaas.api.image_profiles.retrieve(
            id="id",
        )
        assert_matches_type(ImageProfile, image_profile, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_with_all_params(self, async_client: AsyncVraIaas) -> None:
        image_profile = await async_client.iaas.api.image_profiles.retrieve(
            id="id",
            api_version="apiVersion",
        )
        assert_matches_type(ImageProfile, image_profile, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.image_profiles.with_raw_response.retrieve(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        image_profile = await response.parse()
        assert_matches_type(ImageProfile, image_profile, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.image_profiles.with_streaming_response.retrieve(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            image_profile = await response.parse()
            assert_matches_type(ImageProfile, image_profile, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncVraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.iaas.api.image_profiles.with_raw_response.retrieve(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update(self, async_client: AsyncVraIaas) -> None:
        image_profile = await async_client.iaas.api.image_profiles.update(
            id="id",
            image_mapping={
                "ubuntu": {},
                "centos": {},
            },
            name="name",
        )
        assert_matches_type(ImageProfile, image_profile, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncVraIaas) -> None:
        image_profile = await async_client.iaas.api.image_profiles.update(
            id="id",
            image_mapping={
                "ubuntu": {
                    "id": "9e49",
                    "cloud_config": 'runcmd:\n  - ["mkdir", "/imageFolder"]',
                    "constraints": [
                        {
                            "expression": "ha:strong",
                            "mandatory": True,
                        }
                    ],
                    "external_id": "https://cloud-images.ubuntu.com/releases/16.04/release-20190605/ubuntu-16.04-server-cloudimg-amd64.ova",
                    "name": "ami-ubuntu-16.04-1.9.1-00-1516139717",
                },
                "centos": {
                    "id": "9e50",
                    "cloud_config": 'runcmd:\n  - ["mkdir", "/imageFolder"]',
                    "constraints": [
                        {
                            "expression": "ha:strong",
                            "mandatory": True,
                        }
                    ],
                    "external_id": "https://cloud-images.ubuntu.com/releases/16.04/release-20190605/ubuntu-16.04-server-cloudimg-amd64.ova",
                    "name": "ami-centos-7-1.13.0-00-1543963388",
                },
            },
            name="name",
            api_version="apiVersion",
            description="description",
        )
        assert_matches_type(ImageProfile, image_profile, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_update(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.image_profiles.with_raw_response.update(
            id="id",
            image_mapping={
                "ubuntu": {},
                "centos": {},
            },
            name="name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        image_profile = await response.parse()
        assert_matches_type(ImageProfile, image_profile, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.image_profiles.with_streaming_response.update(
            id="id",
            image_mapping={
                "ubuntu": {},
                "centos": {},
            },
            name="name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            image_profile = await response.parse()
            assert_matches_type(ImageProfile, image_profile, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_update(self, async_client: AsyncVraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.iaas.api.image_profiles.with_raw_response.update(
                id="",
                image_mapping={
                    "ubuntu": {},
                    "centos": {},
                },
                name="name",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete(self, async_client: AsyncVraIaas) -> None:
        image_profile = await async_client.iaas.api.image_profiles.delete(
            id="id",
        )
        assert image_profile is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete_with_all_params(self, async_client: AsyncVraIaas) -> None:
        image_profile = await async_client.iaas.api.image_profiles.delete(
            id="id",
            api_version="apiVersion",
        )
        assert image_profile is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.image_profiles.with_raw_response.delete(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        image_profile = await response.parse()
        assert image_profile is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.image_profiles.with_streaming_response.delete(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            image_profile = await response.parse()
            assert image_profile is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_delete(self, async_client: AsyncVraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.iaas.api.image_profiles.with_raw_response.delete(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_image_profiles(self, async_client: AsyncVraIaas) -> None:
        image_profile = await async_client.iaas.api.image_profiles.image_profiles(
            image_mapping={
                "ubuntu": {},
                "centos": {},
            },
            name="name",
            region_id="9.0E49",
        )
        assert_matches_type(ImageProfile, image_profile, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_image_profiles_with_all_params(self, async_client: AsyncVraIaas) -> None:
        image_profile = await async_client.iaas.api.image_profiles.image_profiles(
            image_mapping={
                "ubuntu": {
                    "id": "9e49",
                    "cloud_config": 'runcmd:\n  - ["mkdir", "/imageFolder"]',
                    "constraints": [
                        {
                            "expression": "ha:strong",
                            "mandatory": True,
                        }
                    ],
                    "external_id": "https://cloud-images.ubuntu.com/releases/16.04/release-20190605/ubuntu-16.04-server-cloudimg-amd64.ova",
                    "name": "ami-ubuntu-16.04-1.9.1-00-1516139717",
                },
                "centos": {
                    "id": "9e50",
                    "cloud_config": 'runcmd:\n  - ["mkdir", "/imageFolder"]',
                    "constraints": [
                        {
                            "expression": "ha:strong",
                            "mandatory": True,
                        }
                    ],
                    "external_id": "https://cloud-images.ubuntu.com/releases/16.04/release-20190605/ubuntu-16.04-server-cloudimg-amd64.ova",
                    "name": "ami-centos-7-1.13.0-00-1543963388",
                },
            },
            name="name",
            region_id="9.0E49",
            api_version="apiVersion",
            description="description",
        )
        assert_matches_type(ImageProfile, image_profile, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_image_profiles(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.image_profiles.with_raw_response.image_profiles(
            image_mapping={
                "ubuntu": {},
                "centos": {},
            },
            name="name",
            region_id="9.0E49",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        image_profile = await response.parse()
        assert_matches_type(ImageProfile, image_profile, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_image_profiles(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.image_profiles.with_streaming_response.image_profiles(
            image_mapping={
                "ubuntu": {},
                "centos": {},
            },
            name="name",
            region_id="9.0E49",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            image_profile = await response.parse()
            assert_matches_type(ImageProfile, image_profile, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_image_profiles(self, async_client: AsyncVraIaas) -> None:
        image_profile = await async_client.iaas.api.image_profiles.retrieve_image_profiles()
        assert_matches_type(ImageProfileRetrieveImageProfilesResponse, image_profile, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_image_profiles_with_all_params(self, async_client: AsyncVraIaas) -> None:
        image_profile = await async_client.iaas.api.image_profiles.retrieve_image_profiles(
            api_version="apiVersion",
        )
        assert_matches_type(ImageProfileRetrieveImageProfilesResponse, image_profile, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve_image_profiles(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.image_profiles.with_raw_response.retrieve_image_profiles()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        image_profile = await response.parse()
        assert_matches_type(ImageProfileRetrieveImageProfilesResponse, image_profile, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve_image_profiles(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.image_profiles.with_streaming_response.retrieve_image_profiles() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            image_profile = await response.parse()
            assert_matches_type(ImageProfileRetrieveImageProfilesResponse, image_profile, path=["response"])

        assert cast(Any, response.is_closed) is True
