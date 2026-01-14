# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from vra_iaas import VraIaas, AsyncVraIaas
from tests.utils import assert_matches_type
from vra_iaas.types.iaas.api import (
    RequestTrackerRetrieveRequestTrackerResponse,
)
from vra_iaas.types.iaas.api.projects import RequestTracker

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestRequestTracker:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve(self, client: VraIaas) -> None:
        request_tracker = client.iaas.api.request_tracker.retrieve(
            id="id",
        )
        assert_matches_type(RequestTracker, request_tracker, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_with_all_params(self, client: VraIaas) -> None:
        request_tracker = client.iaas.api.request_tracker.retrieve(
            id="id",
            api_version="apiVersion",
        )
        assert_matches_type(RequestTracker, request_tracker, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve(self, client: VraIaas) -> None:
        response = client.iaas.api.request_tracker.with_raw_response.retrieve(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        request_tracker = response.parse()
        assert_matches_type(RequestTracker, request_tracker, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve(self, client: VraIaas) -> None:
        with client.iaas.api.request_tracker.with_streaming_response.retrieve(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            request_tracker = response.parse()
            assert_matches_type(RequestTracker, request_tracker, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve(self, client: VraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.iaas.api.request_tracker.with_raw_response.retrieve(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete(self, client: VraIaas) -> None:
        request_tracker = client.iaas.api.request_tracker.delete(
            id="id",
        )
        assert request_tracker is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete_with_all_params(self, client: VraIaas) -> None:
        request_tracker = client.iaas.api.request_tracker.delete(
            id="id",
            api_version="apiVersion",
        )
        assert request_tracker is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_delete(self, client: VraIaas) -> None:
        response = client.iaas.api.request_tracker.with_raw_response.delete(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        request_tracker = response.parse()
        assert request_tracker is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_delete(self, client: VraIaas) -> None:
        with client.iaas.api.request_tracker.with_streaming_response.delete(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            request_tracker = response.parse()
            assert request_tracker is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_delete(self, client: VraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.iaas.api.request_tracker.with_raw_response.delete(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_request_tracker(self, client: VraIaas) -> None:
        request_tracker = client.iaas.api.request_tracker.retrieve_request_tracker()
        assert_matches_type(RequestTrackerRetrieveRequestTrackerResponse, request_tracker, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_request_tracker_with_all_params(self, client: VraIaas) -> None:
        request_tracker = client.iaas.api.request_tracker.retrieve_request_tracker(
            api_version="apiVersion",
        )
        assert_matches_type(RequestTrackerRetrieveRequestTrackerResponse, request_tracker, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve_request_tracker(self, client: VraIaas) -> None:
        response = client.iaas.api.request_tracker.with_raw_response.retrieve_request_tracker()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        request_tracker = response.parse()
        assert_matches_type(RequestTrackerRetrieveRequestTrackerResponse, request_tracker, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve_request_tracker(self, client: VraIaas) -> None:
        with client.iaas.api.request_tracker.with_streaming_response.retrieve_request_tracker() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            request_tracker = response.parse()
            assert_matches_type(RequestTrackerRetrieveRequestTrackerResponse, request_tracker, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncRequestTracker:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncVraIaas) -> None:
        request_tracker = await async_client.iaas.api.request_tracker.retrieve(
            id="id",
        )
        assert_matches_type(RequestTracker, request_tracker, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_with_all_params(self, async_client: AsyncVraIaas) -> None:
        request_tracker = await async_client.iaas.api.request_tracker.retrieve(
            id="id",
            api_version="apiVersion",
        )
        assert_matches_type(RequestTracker, request_tracker, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.request_tracker.with_raw_response.retrieve(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        request_tracker = await response.parse()
        assert_matches_type(RequestTracker, request_tracker, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.request_tracker.with_streaming_response.retrieve(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            request_tracker = await response.parse()
            assert_matches_type(RequestTracker, request_tracker, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncVraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.iaas.api.request_tracker.with_raw_response.retrieve(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete(self, async_client: AsyncVraIaas) -> None:
        request_tracker = await async_client.iaas.api.request_tracker.delete(
            id="id",
        )
        assert request_tracker is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete_with_all_params(self, async_client: AsyncVraIaas) -> None:
        request_tracker = await async_client.iaas.api.request_tracker.delete(
            id="id",
            api_version="apiVersion",
        )
        assert request_tracker is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.request_tracker.with_raw_response.delete(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        request_tracker = await response.parse()
        assert request_tracker is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.request_tracker.with_streaming_response.delete(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            request_tracker = await response.parse()
            assert request_tracker is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_delete(self, async_client: AsyncVraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.iaas.api.request_tracker.with_raw_response.delete(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_request_tracker(self, async_client: AsyncVraIaas) -> None:
        request_tracker = await async_client.iaas.api.request_tracker.retrieve_request_tracker()
        assert_matches_type(RequestTrackerRetrieveRequestTrackerResponse, request_tracker, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_request_tracker_with_all_params(self, async_client: AsyncVraIaas) -> None:
        request_tracker = await async_client.iaas.api.request_tracker.retrieve_request_tracker(
            api_version="apiVersion",
        )
        assert_matches_type(RequestTrackerRetrieveRequestTrackerResponse, request_tracker, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve_request_tracker(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.request_tracker.with_raw_response.retrieve_request_tracker()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        request_tracker = await response.parse()
        assert_matches_type(RequestTrackerRetrieveRequestTrackerResponse, request_tracker, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve_request_tracker(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.request_tracker.with_streaming_response.retrieve_request_tracker() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            request_tracker = await response.parse()
            assert_matches_type(RequestTrackerRetrieveRequestTrackerResponse, request_tracker, path=["response"])

        assert cast(Any, response.is_closed) is True
