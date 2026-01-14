# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from vra_iaas import VraIaas, AsyncVraIaas
from tests.utils import assert_matches_type
from vra_iaas.types.iaas.api import (
    Project,
    ProjectListResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestProjects:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create(self, client: VraIaas) -> None:
        project = client.iaas.api.projects.create(
            name="name",
        )
        assert_matches_type(Project, project, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_with_all_params(self, client: VraIaas) -> None:
        project = client.iaas.api.projects.create(
            name="name",
            api_version="apiVersion",
            validate_principals=True,
            administrators=[
                {
                    "email": "administrator@vmware.com",
                    "type": "user",
                }
            ],
            constraints={
                "network": [
                    {
                        "expression": "env:dev",
                        "mandatory": True,
                    }
                ],
                "storage": [
                    {
                        "expression": "gold",
                        "mandatory": True,
                    }
                ],
                "extensibility": [
                    {
                        "expression": "key:value",
                        "mandatory": True,
                    }
                ],
            },
            custom_properties={"property": "value"},
            description="description",
            machine_naming_template="${project.name}-test-${####}",
            members=[
                {
                    "email": "member@vmware.com",
                    "type": "user",
                }
            ],
            operation_timeout=30,
            placement_policy="DEFAULT",
            shared_resources=True,
            supervisors=[
                {
                    "email": "supervisor@vmware.com",
                    "type": "user",
                }
            ],
            viewers=[
                {
                    "email": "viewer@vmware.com",
                    "type": "user",
                }
            ],
            zone_assignment_configurations=[
                {
                    "cpu_limit": 2048,
                    "max_number_instances": 50,
                    "memory_limit_mb": 2048,
                    "priority": 1,
                    "storage_limit_gb": 20,
                    "zone_id": "77ee1",
                }
            ],
        )
        assert_matches_type(Project, project, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create(self, client: VraIaas) -> None:
        response = client.iaas.api.projects.with_raw_response.create(
            name="name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        project = response.parse()
        assert_matches_type(Project, project, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create(self, client: VraIaas) -> None:
        with client.iaas.api.projects.with_streaming_response.create(
            name="name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            project = response.parse()
            assert_matches_type(Project, project, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve(self, client: VraIaas) -> None:
        project = client.iaas.api.projects.retrieve(
            id="id",
        )
        assert_matches_type(Project, project, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_with_all_params(self, client: VraIaas) -> None:
        project = client.iaas.api.projects.retrieve(
            id="id",
            api_version="apiVersion",
        )
        assert_matches_type(Project, project, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve(self, client: VraIaas) -> None:
        response = client.iaas.api.projects.with_raw_response.retrieve(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        project = response.parse()
        assert_matches_type(Project, project, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve(self, client: VraIaas) -> None:
        with client.iaas.api.projects.with_streaming_response.retrieve(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            project = response.parse()
            assert_matches_type(Project, project, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve(self, client: VraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.iaas.api.projects.with_raw_response.retrieve(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update(self, client: VraIaas) -> None:
        project = client.iaas.api.projects.update(
            id="id",
            name="name",
        )
        assert_matches_type(Project, project, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update_with_all_params(self, client: VraIaas) -> None:
        project = client.iaas.api.projects.update(
            id="id",
            name="name",
            api_version="apiVersion",
            validate_principals=True,
            administrators=[
                {
                    "email": "administrator@vmware.com",
                    "type": "user",
                }
            ],
            constraints={
                "network": [
                    {
                        "expression": "env:dev",
                        "mandatory": True,
                    }
                ],
                "storage": [
                    {
                        "expression": "gold",
                        "mandatory": True,
                    }
                ],
                "extensibility": [
                    {
                        "expression": "key:value",
                        "mandatory": True,
                    }
                ],
            },
            custom_properties={"property": "value"},
            description="description",
            machine_naming_template="${project.name}-test-${####}",
            members=[
                {
                    "email": "member@vmware.com",
                    "type": "user",
                }
            ],
            operation_timeout=30,
            placement_policy="DEFAULT",
            shared_resources=True,
            supervisors=[
                {
                    "email": "supervisor@vmware.com",
                    "type": "user",
                }
            ],
            viewers=[
                {
                    "email": "viewer@vmware.com",
                    "type": "user",
                }
            ],
            zone_assignment_configurations=[
                {
                    "cpu_limit": 2048,
                    "max_number_instances": 50,
                    "memory_limit_mb": 2048,
                    "priority": 1,
                    "storage_limit_gb": 20,
                    "zone_id": "77ee1",
                }
            ],
        )
        assert_matches_type(Project, project, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_update(self, client: VraIaas) -> None:
        response = client.iaas.api.projects.with_raw_response.update(
            id="id",
            name="name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        project = response.parse()
        assert_matches_type(Project, project, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_update(self, client: VraIaas) -> None:
        with client.iaas.api.projects.with_streaming_response.update(
            id="id",
            name="name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            project = response.parse()
            assert_matches_type(Project, project, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_update(self, client: VraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.iaas.api.projects.with_raw_response.update(
                id="",
                name="name",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list(self, client: VraIaas) -> None:
        project = client.iaas.api.projects.list()
        assert_matches_type(ProjectListResponse, project, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_with_all_params(self, client: VraIaas) -> None:
        project = client.iaas.api.projects.list(
            count=True,
            filter="$filter",
            order_by="$orderBy",
            skip=0,
            top=0,
            api_version="apiVersion",
        )
        assert_matches_type(ProjectListResponse, project, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list(self, client: VraIaas) -> None:
        response = client.iaas.api.projects.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        project = response.parse()
        assert_matches_type(ProjectListResponse, project, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list(self, client: VraIaas) -> None:
        with client.iaas.api.projects.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            project = response.parse()
            assert_matches_type(ProjectListResponse, project, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete(self, client: VraIaas) -> None:
        project = client.iaas.api.projects.delete(
            id="id",
        )
        assert project is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete_with_all_params(self, client: VraIaas) -> None:
        project = client.iaas.api.projects.delete(
            id="id",
            api_version="apiVersion",
        )
        assert project is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_delete(self, client: VraIaas) -> None:
        response = client.iaas.api.projects.with_raw_response.delete(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        project = response.parse()
        assert project is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_delete(self, client: VraIaas) -> None:
        with client.iaas.api.projects.with_streaming_response.delete(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            project = response.parse()
            assert project is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_delete(self, client: VraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.iaas.api.projects.with_raw_response.delete(
                id="",
            )


class TestAsyncProjects:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create(self, async_client: AsyncVraIaas) -> None:
        project = await async_client.iaas.api.projects.create(
            name="name",
        )
        assert_matches_type(Project, project, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncVraIaas) -> None:
        project = await async_client.iaas.api.projects.create(
            name="name",
            api_version="apiVersion",
            validate_principals=True,
            administrators=[
                {
                    "email": "administrator@vmware.com",
                    "type": "user",
                }
            ],
            constraints={
                "network": [
                    {
                        "expression": "env:dev",
                        "mandatory": True,
                    }
                ],
                "storage": [
                    {
                        "expression": "gold",
                        "mandatory": True,
                    }
                ],
                "extensibility": [
                    {
                        "expression": "key:value",
                        "mandatory": True,
                    }
                ],
            },
            custom_properties={"property": "value"},
            description="description",
            machine_naming_template="${project.name}-test-${####}",
            members=[
                {
                    "email": "member@vmware.com",
                    "type": "user",
                }
            ],
            operation_timeout=30,
            placement_policy="DEFAULT",
            shared_resources=True,
            supervisors=[
                {
                    "email": "supervisor@vmware.com",
                    "type": "user",
                }
            ],
            viewers=[
                {
                    "email": "viewer@vmware.com",
                    "type": "user",
                }
            ],
            zone_assignment_configurations=[
                {
                    "cpu_limit": 2048,
                    "max_number_instances": 50,
                    "memory_limit_mb": 2048,
                    "priority": 1,
                    "storage_limit_gb": 20,
                    "zone_id": "77ee1",
                }
            ],
        )
        assert_matches_type(Project, project, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.projects.with_raw_response.create(
            name="name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        project = await response.parse()
        assert_matches_type(Project, project, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.projects.with_streaming_response.create(
            name="name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            project = await response.parse()
            assert_matches_type(Project, project, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncVraIaas) -> None:
        project = await async_client.iaas.api.projects.retrieve(
            id="id",
        )
        assert_matches_type(Project, project, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_with_all_params(self, async_client: AsyncVraIaas) -> None:
        project = await async_client.iaas.api.projects.retrieve(
            id="id",
            api_version="apiVersion",
        )
        assert_matches_type(Project, project, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.projects.with_raw_response.retrieve(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        project = await response.parse()
        assert_matches_type(Project, project, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.projects.with_streaming_response.retrieve(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            project = await response.parse()
            assert_matches_type(Project, project, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncVraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.iaas.api.projects.with_raw_response.retrieve(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update(self, async_client: AsyncVraIaas) -> None:
        project = await async_client.iaas.api.projects.update(
            id="id",
            name="name",
        )
        assert_matches_type(Project, project, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncVraIaas) -> None:
        project = await async_client.iaas.api.projects.update(
            id="id",
            name="name",
            api_version="apiVersion",
            validate_principals=True,
            administrators=[
                {
                    "email": "administrator@vmware.com",
                    "type": "user",
                }
            ],
            constraints={
                "network": [
                    {
                        "expression": "env:dev",
                        "mandatory": True,
                    }
                ],
                "storage": [
                    {
                        "expression": "gold",
                        "mandatory": True,
                    }
                ],
                "extensibility": [
                    {
                        "expression": "key:value",
                        "mandatory": True,
                    }
                ],
            },
            custom_properties={"property": "value"},
            description="description",
            machine_naming_template="${project.name}-test-${####}",
            members=[
                {
                    "email": "member@vmware.com",
                    "type": "user",
                }
            ],
            operation_timeout=30,
            placement_policy="DEFAULT",
            shared_resources=True,
            supervisors=[
                {
                    "email": "supervisor@vmware.com",
                    "type": "user",
                }
            ],
            viewers=[
                {
                    "email": "viewer@vmware.com",
                    "type": "user",
                }
            ],
            zone_assignment_configurations=[
                {
                    "cpu_limit": 2048,
                    "max_number_instances": 50,
                    "memory_limit_mb": 2048,
                    "priority": 1,
                    "storage_limit_gb": 20,
                    "zone_id": "77ee1",
                }
            ],
        )
        assert_matches_type(Project, project, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_update(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.projects.with_raw_response.update(
            id="id",
            name="name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        project = await response.parse()
        assert_matches_type(Project, project, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.projects.with_streaming_response.update(
            id="id",
            name="name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            project = await response.parse()
            assert_matches_type(Project, project, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_update(self, async_client: AsyncVraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.iaas.api.projects.with_raw_response.update(
                id="",
                name="name",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list(self, async_client: AsyncVraIaas) -> None:
        project = await async_client.iaas.api.projects.list()
        assert_matches_type(ProjectListResponse, project, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncVraIaas) -> None:
        project = await async_client.iaas.api.projects.list(
            count=True,
            filter="$filter",
            order_by="$orderBy",
            skip=0,
            top=0,
            api_version="apiVersion",
        )
        assert_matches_type(ProjectListResponse, project, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.projects.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        project = await response.parse()
        assert_matches_type(ProjectListResponse, project, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.projects.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            project = await response.parse()
            assert_matches_type(ProjectListResponse, project, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete(self, async_client: AsyncVraIaas) -> None:
        project = await async_client.iaas.api.projects.delete(
            id="id",
        )
        assert project is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete_with_all_params(self, async_client: AsyncVraIaas) -> None:
        project = await async_client.iaas.api.projects.delete(
            id="id",
            api_version="apiVersion",
        )
        assert project is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.projects.with_raw_response.delete(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        project = await response.parse()
        assert project is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.projects.with_streaming_response.delete(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            project = await response.parse()
            assert project is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_delete(self, async_client: AsyncVraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.iaas.api.projects.with_raw_response.delete(
                id="",
            )
