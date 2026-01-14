# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from vra_iaas import VraIaas, AsyncVraIaas
from tests.utils import assert_matches_type
from vra_iaas.types.iaas.api import (
    SecurityGroup,
    SecurityGroupRetrieveSecurityGroupsResponse,
)
from vra_iaas.types.iaas.api.projects import RequestTracker

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestSecurityGroups:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve(self, client: VraIaas) -> None:
        security_group = client.iaas.api.security_groups.retrieve(
            id="id",
        )
        assert_matches_type(SecurityGroup, security_group, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_with_all_params(self, client: VraIaas) -> None:
        security_group = client.iaas.api.security_groups.retrieve(
            id="id",
            api_version="apiVersion",
        )
        assert_matches_type(SecurityGroup, security_group, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve(self, client: VraIaas) -> None:
        response = client.iaas.api.security_groups.with_raw_response.retrieve(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        security_group = response.parse()
        assert_matches_type(SecurityGroup, security_group, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve(self, client: VraIaas) -> None:
        with client.iaas.api.security_groups.with_streaming_response.retrieve(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            security_group = response.parse()
            assert_matches_type(SecurityGroup, security_group, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve(self, client: VraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.iaas.api.security_groups.with_raw_response.retrieve(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update(self, client: VraIaas) -> None:
        security_group = client.iaas.api.security_groups.update(
            id="id",
        )
        assert_matches_type(SecurityGroup, security_group, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update_with_all_params(self, client: VraIaas) -> None:
        security_group = client.iaas.api.security_groups.update(
            id="id",
            api_version="apiVersion",
            tags=[
                {
                    "key": "ownedBy",
                    "value": "Rainpole",
                }
            ],
        )
        assert_matches_type(SecurityGroup, security_group, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_update(self, client: VraIaas) -> None:
        response = client.iaas.api.security_groups.with_raw_response.update(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        security_group = response.parse()
        assert_matches_type(SecurityGroup, security_group, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_update(self, client: VraIaas) -> None:
        with client.iaas.api.security_groups.with_streaming_response.update(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            security_group = response.parse()
            assert_matches_type(SecurityGroup, security_group, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_update(self, client: VraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.iaas.api.security_groups.with_raw_response.update(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete(self, client: VraIaas) -> None:
        security_group = client.iaas.api.security_groups.delete(
            id="id",
        )
        assert_matches_type(RequestTracker, security_group, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete_with_all_params(self, client: VraIaas) -> None:
        security_group = client.iaas.api.security_groups.delete(
            id="id",
            api_version="apiVersion",
            force_delete=True,
        )
        assert_matches_type(RequestTracker, security_group, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_delete(self, client: VraIaas) -> None:
        response = client.iaas.api.security_groups.with_raw_response.delete(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        security_group = response.parse()
        assert_matches_type(RequestTracker, security_group, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_delete(self, client: VraIaas) -> None:
        with client.iaas.api.security_groups.with_streaming_response.delete(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            security_group = response.parse()
            assert_matches_type(RequestTracker, security_group, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_delete(self, client: VraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.iaas.api.security_groups.with_raw_response.delete(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_security_groups(self, client: VraIaas) -> None:
        security_group = client.iaas.api.security_groups.retrieve_security_groups()
        assert_matches_type(SecurityGroupRetrieveSecurityGroupsResponse, security_group, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_security_groups_with_all_params(self, client: VraIaas) -> None:
        security_group = client.iaas.api.security_groups.retrieve_security_groups(
            api_version="apiVersion",
        )
        assert_matches_type(SecurityGroupRetrieveSecurityGroupsResponse, security_group, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve_security_groups(self, client: VraIaas) -> None:
        response = client.iaas.api.security_groups.with_raw_response.retrieve_security_groups()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        security_group = response.parse()
        assert_matches_type(SecurityGroupRetrieveSecurityGroupsResponse, security_group, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve_security_groups(self, client: VraIaas) -> None:
        with client.iaas.api.security_groups.with_streaming_response.retrieve_security_groups() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            security_group = response.parse()
            assert_matches_type(SecurityGroupRetrieveSecurityGroupsResponse, security_group, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_security_groups(self, client: VraIaas) -> None:
        security_group = client.iaas.api.security_groups.security_groups(
            name="name",
            project_id="e058",
        )
        assert_matches_type(RequestTracker, security_group, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_security_groups_with_all_params(self, client: VraIaas) -> None:
        security_group = client.iaas.api.security_groups.security_groups(
            name="name",
            project_id="e058",
            api_version="apiVersion",
            custom_properties={"foo": "string"},
            deployment_id="123e4567-e89b-12d3-a456-426655440000",
            description="description",
            rules=[
                {
                    "access": "Allow",
                    "direction": "Outbound",
                    "ip_range_cidr": "66.170.99.2/32",
                    "ports": "443, 1-655535",
                    "name": "5756f7e2",
                    "protocol": "ANY, TCP, UDP",
                    "service": "HTTPS, SSH",
                }
            ],
            tags=[
                {
                    "key": "group",
                    "value": "ssh",
                }
            ],
        )
        assert_matches_type(RequestTracker, security_group, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_security_groups(self, client: VraIaas) -> None:
        response = client.iaas.api.security_groups.with_raw_response.security_groups(
            name="name",
            project_id="e058",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        security_group = response.parse()
        assert_matches_type(RequestTracker, security_group, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_security_groups(self, client: VraIaas) -> None:
        with client.iaas.api.security_groups.with_streaming_response.security_groups(
            name="name",
            project_id="e058",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            security_group = response.parse()
            assert_matches_type(RequestTracker, security_group, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncSecurityGroups:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncVraIaas) -> None:
        security_group = await async_client.iaas.api.security_groups.retrieve(
            id="id",
        )
        assert_matches_type(SecurityGroup, security_group, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_with_all_params(self, async_client: AsyncVraIaas) -> None:
        security_group = await async_client.iaas.api.security_groups.retrieve(
            id="id",
            api_version="apiVersion",
        )
        assert_matches_type(SecurityGroup, security_group, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.security_groups.with_raw_response.retrieve(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        security_group = await response.parse()
        assert_matches_type(SecurityGroup, security_group, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.security_groups.with_streaming_response.retrieve(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            security_group = await response.parse()
            assert_matches_type(SecurityGroup, security_group, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncVraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.iaas.api.security_groups.with_raw_response.retrieve(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update(self, async_client: AsyncVraIaas) -> None:
        security_group = await async_client.iaas.api.security_groups.update(
            id="id",
        )
        assert_matches_type(SecurityGroup, security_group, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncVraIaas) -> None:
        security_group = await async_client.iaas.api.security_groups.update(
            id="id",
            api_version="apiVersion",
            tags=[
                {
                    "key": "ownedBy",
                    "value": "Rainpole",
                }
            ],
        )
        assert_matches_type(SecurityGroup, security_group, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_update(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.security_groups.with_raw_response.update(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        security_group = await response.parse()
        assert_matches_type(SecurityGroup, security_group, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.security_groups.with_streaming_response.update(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            security_group = await response.parse()
            assert_matches_type(SecurityGroup, security_group, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_update(self, async_client: AsyncVraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.iaas.api.security_groups.with_raw_response.update(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete(self, async_client: AsyncVraIaas) -> None:
        security_group = await async_client.iaas.api.security_groups.delete(
            id="id",
        )
        assert_matches_type(RequestTracker, security_group, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete_with_all_params(self, async_client: AsyncVraIaas) -> None:
        security_group = await async_client.iaas.api.security_groups.delete(
            id="id",
            api_version="apiVersion",
            force_delete=True,
        )
        assert_matches_type(RequestTracker, security_group, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.security_groups.with_raw_response.delete(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        security_group = await response.parse()
        assert_matches_type(RequestTracker, security_group, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.security_groups.with_streaming_response.delete(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            security_group = await response.parse()
            assert_matches_type(RequestTracker, security_group, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_delete(self, async_client: AsyncVraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.iaas.api.security_groups.with_raw_response.delete(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_security_groups(self, async_client: AsyncVraIaas) -> None:
        security_group = await async_client.iaas.api.security_groups.retrieve_security_groups()
        assert_matches_type(SecurityGroupRetrieveSecurityGroupsResponse, security_group, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_security_groups_with_all_params(self, async_client: AsyncVraIaas) -> None:
        security_group = await async_client.iaas.api.security_groups.retrieve_security_groups(
            api_version="apiVersion",
        )
        assert_matches_type(SecurityGroupRetrieveSecurityGroupsResponse, security_group, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve_security_groups(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.security_groups.with_raw_response.retrieve_security_groups()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        security_group = await response.parse()
        assert_matches_type(SecurityGroupRetrieveSecurityGroupsResponse, security_group, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve_security_groups(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.security_groups.with_streaming_response.retrieve_security_groups() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            security_group = await response.parse()
            assert_matches_type(SecurityGroupRetrieveSecurityGroupsResponse, security_group, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_security_groups(self, async_client: AsyncVraIaas) -> None:
        security_group = await async_client.iaas.api.security_groups.security_groups(
            name="name",
            project_id="e058",
        )
        assert_matches_type(RequestTracker, security_group, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_security_groups_with_all_params(self, async_client: AsyncVraIaas) -> None:
        security_group = await async_client.iaas.api.security_groups.security_groups(
            name="name",
            project_id="e058",
            api_version="apiVersion",
            custom_properties={"foo": "string"},
            deployment_id="123e4567-e89b-12d3-a456-426655440000",
            description="description",
            rules=[
                {
                    "access": "Allow",
                    "direction": "Outbound",
                    "ip_range_cidr": "66.170.99.2/32",
                    "ports": "443, 1-655535",
                    "name": "5756f7e2",
                    "protocol": "ANY, TCP, UDP",
                    "service": "HTTPS, SSH",
                }
            ],
            tags=[
                {
                    "key": "group",
                    "value": "ssh",
                }
            ],
        )
        assert_matches_type(RequestTracker, security_group, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_security_groups(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.security_groups.with_raw_response.security_groups(
            name="name",
            project_id="e058",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        security_group = await response.parse()
        assert_matches_type(RequestTracker, security_group, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_security_groups(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.security_groups.with_streaming_response.security_groups(
            name="name",
            project_id="e058",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            security_group = await response.parse()
            assert_matches_type(RequestTracker, security_group, path=["response"])

        assert cast(Any, response.is_closed) is True
