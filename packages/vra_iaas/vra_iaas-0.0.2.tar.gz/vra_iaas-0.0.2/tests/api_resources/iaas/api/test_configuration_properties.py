# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from vra_iaas import VraIaas, AsyncVraIaas
from tests.utils import assert_matches_type
from vra_iaas.types.iaas.api import (
    ConfigurationProperty,
    ConfigurationPropertyResult,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestConfigurationProperties:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve(self, client: VraIaas) -> None:
        configuration_property = client.iaas.api.configuration_properties.retrieve(
            id="id",
            api_version="apiVersion",
        )
        assert_matches_type(ConfigurationPropertyResult, configuration_property, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve(self, client: VraIaas) -> None:
        response = client.iaas.api.configuration_properties.with_raw_response.retrieve(
            id="id",
            api_version="apiVersion",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        configuration_property = response.parse()
        assert_matches_type(ConfigurationPropertyResult, configuration_property, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve(self, client: VraIaas) -> None:
        with client.iaas.api.configuration_properties.with_streaming_response.retrieve(
            id="id",
            api_version="apiVersion",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            configuration_property = response.parse()
            assert_matches_type(ConfigurationPropertyResult, configuration_property, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve(self, client: VraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.iaas.api.configuration_properties.with_raw_response.retrieve(
                id="",
                api_version="apiVersion",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete(self, client: VraIaas) -> None:
        configuration_property = client.iaas.api.configuration_properties.delete(
            id="id",
            api_version="apiVersion",
        )
        assert_matches_type(ConfigurationProperty, configuration_property, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_delete(self, client: VraIaas) -> None:
        response = client.iaas.api.configuration_properties.with_raw_response.delete(
            id="id",
            api_version="apiVersion",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        configuration_property = response.parse()
        assert_matches_type(ConfigurationProperty, configuration_property, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_delete(self, client: VraIaas) -> None:
        with client.iaas.api.configuration_properties.with_streaming_response.delete(
            id="id",
            api_version="apiVersion",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            configuration_property = response.parse()
            assert_matches_type(ConfigurationProperty, configuration_property, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_delete(self, client: VraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.iaas.api.configuration_properties.with_raw_response.delete(
                id="",
                api_version="apiVersion",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_configuration_properties(self, client: VraIaas) -> None:
        configuration_property = client.iaas.api.configuration_properties.retrieve_configuration_properties(
            api_version="apiVersion",
        )
        assert_matches_type(ConfigurationPropertyResult, configuration_property, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve_configuration_properties(self, client: VraIaas) -> None:
        response = client.iaas.api.configuration_properties.with_raw_response.retrieve_configuration_properties(
            api_version="apiVersion",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        configuration_property = response.parse()
        assert_matches_type(ConfigurationPropertyResult, configuration_property, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve_configuration_properties(self, client: VraIaas) -> None:
        with client.iaas.api.configuration_properties.with_streaming_response.retrieve_configuration_properties(
            api_version="apiVersion",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            configuration_property = response.parse()
            assert_matches_type(ConfigurationPropertyResult, configuration_property, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update_configuration_properties(self, client: VraIaas) -> None:
        configuration_property = client.iaas.api.configuration_properties.update_configuration_properties(
            api_version="apiVersion",
            key="SESSION_TIMEOUT_DURATION_MINUTES, RELEASE_IPADDRESS_PERIOD_MINUTES, NSXT_RETRY_DURATION_MINUTES",
            value="value",
        )
        assert_matches_type(ConfigurationProperty, configuration_property, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_update_configuration_properties(self, client: VraIaas) -> None:
        response = client.iaas.api.configuration_properties.with_raw_response.update_configuration_properties(
            api_version="apiVersion",
            key="SESSION_TIMEOUT_DURATION_MINUTES, RELEASE_IPADDRESS_PERIOD_MINUTES, NSXT_RETRY_DURATION_MINUTES",
            value="value",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        configuration_property = response.parse()
        assert_matches_type(ConfigurationProperty, configuration_property, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_update_configuration_properties(self, client: VraIaas) -> None:
        with client.iaas.api.configuration_properties.with_streaming_response.update_configuration_properties(
            api_version="apiVersion",
            key="SESSION_TIMEOUT_DURATION_MINUTES, RELEASE_IPADDRESS_PERIOD_MINUTES, NSXT_RETRY_DURATION_MINUTES",
            value="value",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            configuration_property = response.parse()
            assert_matches_type(ConfigurationProperty, configuration_property, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncConfigurationProperties:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncVraIaas) -> None:
        configuration_property = await async_client.iaas.api.configuration_properties.retrieve(
            id="id",
            api_version="apiVersion",
        )
        assert_matches_type(ConfigurationPropertyResult, configuration_property, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.configuration_properties.with_raw_response.retrieve(
            id="id",
            api_version="apiVersion",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        configuration_property = await response.parse()
        assert_matches_type(ConfigurationPropertyResult, configuration_property, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.configuration_properties.with_streaming_response.retrieve(
            id="id",
            api_version="apiVersion",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            configuration_property = await response.parse()
            assert_matches_type(ConfigurationPropertyResult, configuration_property, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncVraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.iaas.api.configuration_properties.with_raw_response.retrieve(
                id="",
                api_version="apiVersion",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete(self, async_client: AsyncVraIaas) -> None:
        configuration_property = await async_client.iaas.api.configuration_properties.delete(
            id="id",
            api_version="apiVersion",
        )
        assert_matches_type(ConfigurationProperty, configuration_property, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.configuration_properties.with_raw_response.delete(
            id="id",
            api_version="apiVersion",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        configuration_property = await response.parse()
        assert_matches_type(ConfigurationProperty, configuration_property, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.configuration_properties.with_streaming_response.delete(
            id="id",
            api_version="apiVersion",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            configuration_property = await response.parse()
            assert_matches_type(ConfigurationProperty, configuration_property, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_delete(self, async_client: AsyncVraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.iaas.api.configuration_properties.with_raw_response.delete(
                id="",
                api_version="apiVersion",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_configuration_properties(self, async_client: AsyncVraIaas) -> None:
        configuration_property = await async_client.iaas.api.configuration_properties.retrieve_configuration_properties(
            api_version="apiVersion",
        )
        assert_matches_type(ConfigurationPropertyResult, configuration_property, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve_configuration_properties(self, async_client: AsyncVraIaas) -> None:
        response = (
            await async_client.iaas.api.configuration_properties.with_raw_response.retrieve_configuration_properties(
                api_version="apiVersion",
            )
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        configuration_property = await response.parse()
        assert_matches_type(ConfigurationPropertyResult, configuration_property, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve_configuration_properties(self, async_client: AsyncVraIaas) -> None:
        async with (
            async_client.iaas.api.configuration_properties.with_streaming_response.retrieve_configuration_properties(
                api_version="apiVersion",
            )
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            configuration_property = await response.parse()
            assert_matches_type(ConfigurationPropertyResult, configuration_property, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update_configuration_properties(self, async_client: AsyncVraIaas) -> None:
        configuration_property = await async_client.iaas.api.configuration_properties.update_configuration_properties(
            api_version="apiVersion",
            key="SESSION_TIMEOUT_DURATION_MINUTES, RELEASE_IPADDRESS_PERIOD_MINUTES, NSXT_RETRY_DURATION_MINUTES",
            value="value",
        )
        assert_matches_type(ConfigurationProperty, configuration_property, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_update_configuration_properties(self, async_client: AsyncVraIaas) -> None:
        response = (
            await async_client.iaas.api.configuration_properties.with_raw_response.update_configuration_properties(
                api_version="apiVersion",
                key="SESSION_TIMEOUT_DURATION_MINUTES, RELEASE_IPADDRESS_PERIOD_MINUTES, NSXT_RETRY_DURATION_MINUTES",
                value="value",
            )
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        configuration_property = await response.parse()
        assert_matches_type(ConfigurationProperty, configuration_property, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_update_configuration_properties(self, async_client: AsyncVraIaas) -> None:
        async with (
            async_client.iaas.api.configuration_properties.with_streaming_response.update_configuration_properties(
                api_version="apiVersion",
                key="SESSION_TIMEOUT_DURATION_MINUTES, RELEASE_IPADDRESS_PERIOD_MINUTES, NSXT_RETRY_DURATION_MINUTES",
                value="value",
            )
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            configuration_property = await response.parse()
            assert_matches_type(ConfigurationProperty, configuration_property, path=["response"])

        assert cast(Any, response.is_closed) is True
