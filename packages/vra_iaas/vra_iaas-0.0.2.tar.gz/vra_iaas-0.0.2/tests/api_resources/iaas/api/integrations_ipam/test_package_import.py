# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from vra_iaas import VraIaas, AsyncVraIaas
from tests.utils import assert_matches_type
from vra_iaas.types.iaas.api.integrations_ipam import (
    PackageImportPackageImportResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestPackageImport:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update(self, client: VraIaas) -> None:
        package_import = client.iaas.api.integrations_ipam.package_import.update(
            id="id",
            tus_resumable="1.0.0",
            upload_offset="Upload-Offset",
        )
        assert package_import is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update_with_all_params(self, client: VraIaas) -> None:
        package_import = client.iaas.api.integrations_ipam.package_import.update(
            id="id",
            tus_resumable="1.0.0",
            upload_offset="Upload-Offset",
            api_version="apiVersion",
            body=b"raw file contents",
        )
        assert package_import is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_update(self, client: VraIaas) -> None:
        response = client.iaas.api.integrations_ipam.package_import.with_raw_response.update(
            id="id",
            tus_resumable="1.0.0",
            upload_offset="Upload-Offset",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        package_import = response.parse()
        assert package_import is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_update(self, client: VraIaas) -> None:
        with client.iaas.api.integrations_ipam.package_import.with_streaming_response.update(
            id="id",
            tus_resumable="1.0.0",
            upload_offset="Upload-Offset",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            package_import = response.parse()
            assert package_import is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_update(self, client: VraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.iaas.api.integrations_ipam.package_import.with_raw_response.update(
                id="",
                tus_resumable="1.0.0",
                upload_offset="Upload-Offset",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_package_import(self, client: VraIaas) -> None:
        package_import = client.iaas.api.integrations_ipam.package_import.package_import(
            tus_resumable="1.0.0",
            upload_length="Upload-Length",
        )
        assert_matches_type(PackageImportPackageImportResponse, package_import, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_package_import_with_all_params(self, client: VraIaas) -> None:
        package_import = client.iaas.api.integrations_ipam.package_import.package_import(
            tus_resumable="1.0.0",
            upload_length="Upload-Length",
            api_version="apiVersion",
            bundle_id="bundleId",
            compressed_bundle="U3RhaW5sZXNzIHJvY2tz",
            option="FAIL",
            properties={"foo": "string"},
        )
        assert_matches_type(PackageImportPackageImportResponse, package_import, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_package_import(self, client: VraIaas) -> None:
        response = client.iaas.api.integrations_ipam.package_import.with_raw_response.package_import(
            tus_resumable="1.0.0",
            upload_length="Upload-Length",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        package_import = response.parse()
        assert_matches_type(PackageImportPackageImportResponse, package_import, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_package_import(self, client: VraIaas) -> None:
        with client.iaas.api.integrations_ipam.package_import.with_streaming_response.package_import(
            tus_resumable="1.0.0",
            upload_length="Upload-Length",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            package_import = response.parse()
            assert_matches_type(PackageImportPackageImportResponse, package_import, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncPackageImport:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update(self, async_client: AsyncVraIaas) -> None:
        package_import = await async_client.iaas.api.integrations_ipam.package_import.update(
            id="id",
            tus_resumable="1.0.0",
            upload_offset="Upload-Offset",
        )
        assert package_import is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncVraIaas) -> None:
        package_import = await async_client.iaas.api.integrations_ipam.package_import.update(
            id="id",
            tus_resumable="1.0.0",
            upload_offset="Upload-Offset",
            api_version="apiVersion",
            body=b"raw file contents",
        )
        assert package_import is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_update(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.integrations_ipam.package_import.with_raw_response.update(
            id="id",
            tus_resumable="1.0.0",
            upload_offset="Upload-Offset",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        package_import = await response.parse()
        assert package_import is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.integrations_ipam.package_import.with_streaming_response.update(
            id="id",
            tus_resumable="1.0.0",
            upload_offset="Upload-Offset",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            package_import = await response.parse()
            assert package_import is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_update(self, async_client: AsyncVraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.iaas.api.integrations_ipam.package_import.with_raw_response.update(
                id="",
                tus_resumable="1.0.0",
                upload_offset="Upload-Offset",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_package_import(self, async_client: AsyncVraIaas) -> None:
        package_import = await async_client.iaas.api.integrations_ipam.package_import.package_import(
            tus_resumable="1.0.0",
            upload_length="Upload-Length",
        )
        assert_matches_type(PackageImportPackageImportResponse, package_import, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_package_import_with_all_params(self, async_client: AsyncVraIaas) -> None:
        package_import = await async_client.iaas.api.integrations_ipam.package_import.package_import(
            tus_resumable="1.0.0",
            upload_length="Upload-Length",
            api_version="apiVersion",
            bundle_id="bundleId",
            compressed_bundle="U3RhaW5sZXNzIHJvY2tz",
            option="FAIL",
            properties={"foo": "string"},
        )
        assert_matches_type(PackageImportPackageImportResponse, package_import, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_package_import(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.integrations_ipam.package_import.with_raw_response.package_import(
            tus_resumable="1.0.0",
            upload_length="Upload-Length",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        package_import = await response.parse()
        assert_matches_type(PackageImportPackageImportResponse, package_import, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_package_import(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.integrations_ipam.package_import.with_streaming_response.package_import(
            tus_resumable="1.0.0",
            upload_length="Upload-Length",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            package_import = await response.parse()
            assert_matches_type(PackageImportPackageImportResponse, package_import, path=["response"])

        assert cast(Any, response.is_closed) is True
