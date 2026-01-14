# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Iterable

import httpx

from ....._types import Body, Omit, Query, Headers, NotGiven, omit, not_given
from ....._utils import maybe_transform, async_maybe_transform
from ....._compat import cached_property
from ....._resource import SyncAPIResource, AsyncAPIResource
from ....._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ....._base_client import make_request_options
from .....types.iaas.api.machines import (
    operation_reset_params,
    operation_reboot_params,
    operation_resize_params,
    operation_update_params,
    operation_restart_params,
    operation_suspend_params,
    operation_power_on_params,
    operation_shutdown_params,
    operation_power_off_params,
    operation_snapshots_params,
    operation_unregister_params,
    operation_change_security_groups_params,
)
from .....types.iaas.api.projects.request_tracker import RequestTracker
from .....types.iaas.api.machines.network_interface_specification_param import NetworkInterfaceSpecificationParam

__all__ = ["OperationsResource", "AsyncOperationsResource"]


class OperationsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> OperationsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#accessing-raw-response-data-eg-headers
        """
        return OperationsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> OperationsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#with_streaming_response
        """
        return OperationsResourceWithStreamingResponse(self)

    def update(
        self,
        snapshot_id: str,
        *,
        id: str,
        api_version: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RequestTracker:
        """
        Second day revert snapshot operation for machine

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        if not snapshot_id:
            raise ValueError(f"Expected a non-empty value for `snapshot_id` but received {snapshot_id!r}")
        return self._post(
            f"/iaas/api/machines/{id}/operations/revert/{snapshot_id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"api_version": api_version}, operation_update_params.OperationUpdateParams),
            ),
            cast_to=RequestTracker,
        )

    def change_security_groups(
        self,
        path_id: str,
        *,
        body_id: str,
        _links: operation_change_security_groups_params._Links,
        api_version: str | Omit = omit,
        created_at: str | Omit = omit,
        description: str | Omit = omit,
        name: str | Omit = omit,
        network_interface_specifications: Iterable[NetworkInterfaceSpecificationParam] | Omit = omit,
        org_id: str | Omit = omit,
        owner: str | Omit = omit,
        owner_type: str | Omit = omit,
        updated_at: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RequestTracker:
        """Change security groups for a vSphere machine network interfaces.

        Securing group
        that is part of the same deployment can be added or removed for a machine
        network interface.

        Args:
          body_id: The id of this resource instance

          _links: HATEOAS of the entity

          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          created_at: Date when the entity was created. The date is in ISO 8601 and UTC.

          description: A human-friendly description.

          name: A human-friendly name used as an identifier in APIs that support this option.

          network_interface_specifications: A set of network interface controller specifications for this machine. If not
              specified, then no reconfiguration will be performed.

          org_id: The id of the organization this entity belongs to.

          owner: Email of the user or display name of the group that owns the entity.

          owner_type: Type of a owner(user/ad_group) that owns the entity.

          updated_at: Date when the entity was last updated. The date is ISO 8601 and UTC.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not path_id:
            raise ValueError(f"Expected a non-empty value for `path_id` but received {path_id!r}")
        return self._post(
            f"/iaas/api/machines/{path_id}/operations/change-security-groups",
            body=maybe_transform(
                {
                    "body_id": body_id,
                    "_links": _links,
                    "created_at": created_at,
                    "description": description,
                    "name": name,
                    "network_interface_specifications": network_interface_specifications,
                    "org_id": org_id,
                    "owner": owner,
                    "owner_type": owner_type,
                    "updated_at": updated_at,
                },
                operation_change_security_groups_params.OperationChangeSecurityGroupsParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"api_version": api_version},
                    operation_change_security_groups_params.OperationChangeSecurityGroupsParams,
                ),
            ),
            cast_to=RequestTracker,
        )

    def power_off(
        self,
        id: str,
        *,
        api_version: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RequestTracker:
        """
        Second day power-off operation for machine

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._post(
            f"/iaas/api/machines/{id}/operations/power-off",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"api_version": api_version}, operation_power_off_params.OperationPowerOffParams),
            ),
            cast_to=RequestTracker,
        )

    def power_on(
        self,
        id: str,
        *,
        api_version: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RequestTracker:
        """
        Second day power-on operation for machine

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._post(
            f"/iaas/api/machines/{id}/operations/power-on",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"api_version": api_version}, operation_power_on_params.OperationPowerOnParams),
            ),
            cast_to=RequestTracker,
        )

    def reboot(
        self,
        id: str,
        *,
        api_version: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RequestTracker:
        """
        Second day reboot operation for machine

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._post(
            f"/iaas/api/machines/{id}/operations/reboot",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"api_version": api_version}, operation_reboot_params.OperationRebootParams),
            ),
            cast_to=RequestTracker,
        )

    def reset(
        self,
        id: str,
        *,
        api_version: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RequestTracker:
        """
        Second day reset operation for machine

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._post(
            f"/iaas/api/machines/{id}/operations/reset",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"api_version": api_version}, operation_reset_params.OperationResetParams),
            ),
            cast_to=RequestTracker,
        )

    def resize(
        self,
        id: str,
        *,
        api_version: str | Omit = omit,
        core_count: str | Omit = omit,
        cpu_count: str | Omit = omit,
        flavor_name: str | Omit = omit,
        memory_in_mb: str | Omit = omit,
        reboot_machine: bool | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RequestTracker:
        """
        Second day resize operation for machine

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          core_count: The desired number of cores per socket to resize the Machine

          cpu_count: The desired number of CPUs to resize the

          flavor_name: The desired flavor to resize the Machine.

          memory_in_mb: The desired memory in MBs to resize the Machine

          reboot_machine: Only applicable for vSphere VMs with the CPU Hot Add or Memory Hot Plug options
              enabled. If set to false, VM is resized without reboot.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._post(
            f"/iaas/api/machines/{id}/operations/resize",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "api_version": api_version,
                        "core_count": core_count,
                        "cpu_count": cpu_count,
                        "flavor_name": flavor_name,
                        "memory_in_mb": memory_in_mb,
                        "reboot_machine": reboot_machine,
                    },
                    operation_resize_params.OperationResizeParams,
                ),
            ),
            cast_to=RequestTracker,
        )

    def restart(
        self,
        id: str,
        *,
        api_version: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RequestTracker:
        """
        Second day restart operation for machine

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._post(
            f"/iaas/api/machines/{id}/operations/restart",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"api_version": api_version}, operation_restart_params.OperationRestartParams),
            ),
            cast_to=RequestTracker,
        )

    def shutdown(
        self,
        id: str,
        *,
        api_version: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RequestTracker:
        """
        Second day shut down operation machine

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._post(
            f"/iaas/api/machines/{id}/operations/shutdown",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"api_version": api_version}, operation_shutdown_params.OperationShutdownParams),
            ),
            cast_to=RequestTracker,
        )

    def snapshots(
        self,
        path_id: str,
        *,
        body_id: str,
        _links: operation_snapshots_params._Links,
        api_version: str | Omit = omit,
        created_at: str | Omit = omit,
        custom_properties: Dict[str, str] | Omit = omit,
        description: str | Omit = omit,
        name: str | Omit = omit,
        org_id: str | Omit = omit,
        owner: str | Omit = omit,
        owner_type: str | Omit = omit,
        snapshot_memory: bool | Omit = omit,
        updated_at: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RequestTracker:
        """
        Second day create snapshot operation for machine

        Args:
          body_id: The id of this resource instance

          _links: HATEOAS of the entity

          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          created_at: Date when the entity was created. The date is in ISO 8601 and UTC.

          custom_properties: Additional custom properties that may be used to extend the snapshot.

          description: A human-friendly description.

          name: A human-friendly name used as an identifier in APIs that support this option.

          org_id: The id of the organization this entity belongs to.

          owner: Email of the user or display name of the group that owns the entity.

          owner_type: Type of a owner(user/ad_group) that owns the entity.

          snapshot_memory: Captures the full state of a running virtual machine, including the memory.

          updated_at: Date when the entity was last updated. The date is ISO 8601 and UTC.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not path_id:
            raise ValueError(f"Expected a non-empty value for `path_id` but received {path_id!r}")
        return self._post(
            f"/iaas/api/machines/{path_id}/operations/snapshots",
            body=maybe_transform(
                {
                    "body_id": body_id,
                    "_links": _links,
                    "created_at": created_at,
                    "custom_properties": custom_properties,
                    "description": description,
                    "name": name,
                    "org_id": org_id,
                    "owner": owner,
                    "owner_type": owner_type,
                    "snapshot_memory": snapshot_memory,
                    "updated_at": updated_at,
                },
                operation_snapshots_params.OperationSnapshotsParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"api_version": api_version}, operation_snapshots_params.OperationSnapshotsParams
                ),
            ),
            cast_to=RequestTracker,
        )

    def suspend(
        self,
        id: str,
        *,
        api_version: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RequestTracker:
        """
        Second day suspend operation for machine

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._post(
            f"/iaas/api/machines/{id}/operations/suspend",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"api_version": api_version}, operation_suspend_params.OperationSuspendParams),
            ),
            cast_to=RequestTracker,
        )

    def unregister(
        self,
        id: str,
        *,
        api_version: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RequestTracker:
        """
        Unregister a vSphere provisioned machine

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._post(
            f"/iaas/api/machines/{id}/operations/unregister",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"api_version": api_version}, operation_unregister_params.OperationUnregisterParams
                ),
            ),
            cast_to=RequestTracker,
        )


class AsyncOperationsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncOperationsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#accessing-raw-response-data-eg-headers
        """
        return AsyncOperationsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncOperationsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#with_streaming_response
        """
        return AsyncOperationsResourceWithStreamingResponse(self)

    async def update(
        self,
        snapshot_id: str,
        *,
        id: str,
        api_version: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RequestTracker:
        """
        Second day revert snapshot operation for machine

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        if not snapshot_id:
            raise ValueError(f"Expected a non-empty value for `snapshot_id` but received {snapshot_id!r}")
        return await self._post(
            f"/iaas/api/machines/{id}/operations/revert/{snapshot_id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"api_version": api_version}, operation_update_params.OperationUpdateParams
                ),
            ),
            cast_to=RequestTracker,
        )

    async def change_security_groups(
        self,
        path_id: str,
        *,
        body_id: str,
        _links: operation_change_security_groups_params._Links,
        api_version: str | Omit = omit,
        created_at: str | Omit = omit,
        description: str | Omit = omit,
        name: str | Omit = omit,
        network_interface_specifications: Iterable[NetworkInterfaceSpecificationParam] | Omit = omit,
        org_id: str | Omit = omit,
        owner: str | Omit = omit,
        owner_type: str | Omit = omit,
        updated_at: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RequestTracker:
        """Change security groups for a vSphere machine network interfaces.

        Securing group
        that is part of the same deployment can be added or removed for a machine
        network interface.

        Args:
          body_id: The id of this resource instance

          _links: HATEOAS of the entity

          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          created_at: Date when the entity was created. The date is in ISO 8601 and UTC.

          description: A human-friendly description.

          name: A human-friendly name used as an identifier in APIs that support this option.

          network_interface_specifications: A set of network interface controller specifications for this machine. If not
              specified, then no reconfiguration will be performed.

          org_id: The id of the organization this entity belongs to.

          owner: Email of the user or display name of the group that owns the entity.

          owner_type: Type of a owner(user/ad_group) that owns the entity.

          updated_at: Date when the entity was last updated. The date is ISO 8601 and UTC.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not path_id:
            raise ValueError(f"Expected a non-empty value for `path_id` but received {path_id!r}")
        return await self._post(
            f"/iaas/api/machines/{path_id}/operations/change-security-groups",
            body=await async_maybe_transform(
                {
                    "body_id": body_id,
                    "_links": _links,
                    "created_at": created_at,
                    "description": description,
                    "name": name,
                    "network_interface_specifications": network_interface_specifications,
                    "org_id": org_id,
                    "owner": owner,
                    "owner_type": owner_type,
                    "updated_at": updated_at,
                },
                operation_change_security_groups_params.OperationChangeSecurityGroupsParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"api_version": api_version},
                    operation_change_security_groups_params.OperationChangeSecurityGroupsParams,
                ),
            ),
            cast_to=RequestTracker,
        )

    async def power_off(
        self,
        id: str,
        *,
        api_version: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RequestTracker:
        """
        Second day power-off operation for machine

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._post(
            f"/iaas/api/machines/{id}/operations/power-off",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"api_version": api_version}, operation_power_off_params.OperationPowerOffParams
                ),
            ),
            cast_to=RequestTracker,
        )

    async def power_on(
        self,
        id: str,
        *,
        api_version: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RequestTracker:
        """
        Second day power-on operation for machine

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._post(
            f"/iaas/api/machines/{id}/operations/power-on",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"api_version": api_version}, operation_power_on_params.OperationPowerOnParams
                ),
            ),
            cast_to=RequestTracker,
        )

    async def reboot(
        self,
        id: str,
        *,
        api_version: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RequestTracker:
        """
        Second day reboot operation for machine

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._post(
            f"/iaas/api/machines/{id}/operations/reboot",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"api_version": api_version}, operation_reboot_params.OperationRebootParams
                ),
            ),
            cast_to=RequestTracker,
        )

    async def reset(
        self,
        id: str,
        *,
        api_version: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RequestTracker:
        """
        Second day reset operation for machine

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._post(
            f"/iaas/api/machines/{id}/operations/reset",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"api_version": api_version}, operation_reset_params.OperationResetParams
                ),
            ),
            cast_to=RequestTracker,
        )

    async def resize(
        self,
        id: str,
        *,
        api_version: str | Omit = omit,
        core_count: str | Omit = omit,
        cpu_count: str | Omit = omit,
        flavor_name: str | Omit = omit,
        memory_in_mb: str | Omit = omit,
        reboot_machine: bool | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RequestTracker:
        """
        Second day resize operation for machine

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          core_count: The desired number of cores per socket to resize the Machine

          cpu_count: The desired number of CPUs to resize the

          flavor_name: The desired flavor to resize the Machine.

          memory_in_mb: The desired memory in MBs to resize the Machine

          reboot_machine: Only applicable for vSphere VMs with the CPU Hot Add or Memory Hot Plug options
              enabled. If set to false, VM is resized without reboot.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._post(
            f"/iaas/api/machines/{id}/operations/resize",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "api_version": api_version,
                        "core_count": core_count,
                        "cpu_count": cpu_count,
                        "flavor_name": flavor_name,
                        "memory_in_mb": memory_in_mb,
                        "reboot_machine": reboot_machine,
                    },
                    operation_resize_params.OperationResizeParams,
                ),
            ),
            cast_to=RequestTracker,
        )

    async def restart(
        self,
        id: str,
        *,
        api_version: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RequestTracker:
        """
        Second day restart operation for machine

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._post(
            f"/iaas/api/machines/{id}/operations/restart",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"api_version": api_version}, operation_restart_params.OperationRestartParams
                ),
            ),
            cast_to=RequestTracker,
        )

    async def shutdown(
        self,
        id: str,
        *,
        api_version: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RequestTracker:
        """
        Second day shut down operation machine

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._post(
            f"/iaas/api/machines/{id}/operations/shutdown",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"api_version": api_version}, operation_shutdown_params.OperationShutdownParams
                ),
            ),
            cast_to=RequestTracker,
        )

    async def snapshots(
        self,
        path_id: str,
        *,
        body_id: str,
        _links: operation_snapshots_params._Links,
        api_version: str | Omit = omit,
        created_at: str | Omit = omit,
        custom_properties: Dict[str, str] | Omit = omit,
        description: str | Omit = omit,
        name: str | Omit = omit,
        org_id: str | Omit = omit,
        owner: str | Omit = omit,
        owner_type: str | Omit = omit,
        snapshot_memory: bool | Omit = omit,
        updated_at: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RequestTracker:
        """
        Second day create snapshot operation for machine

        Args:
          body_id: The id of this resource instance

          _links: HATEOAS of the entity

          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          created_at: Date when the entity was created. The date is in ISO 8601 and UTC.

          custom_properties: Additional custom properties that may be used to extend the snapshot.

          description: A human-friendly description.

          name: A human-friendly name used as an identifier in APIs that support this option.

          org_id: The id of the organization this entity belongs to.

          owner: Email of the user or display name of the group that owns the entity.

          owner_type: Type of a owner(user/ad_group) that owns the entity.

          snapshot_memory: Captures the full state of a running virtual machine, including the memory.

          updated_at: Date when the entity was last updated. The date is ISO 8601 and UTC.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not path_id:
            raise ValueError(f"Expected a non-empty value for `path_id` but received {path_id!r}")
        return await self._post(
            f"/iaas/api/machines/{path_id}/operations/snapshots",
            body=await async_maybe_transform(
                {
                    "body_id": body_id,
                    "_links": _links,
                    "created_at": created_at,
                    "custom_properties": custom_properties,
                    "description": description,
                    "name": name,
                    "org_id": org_id,
                    "owner": owner,
                    "owner_type": owner_type,
                    "snapshot_memory": snapshot_memory,
                    "updated_at": updated_at,
                },
                operation_snapshots_params.OperationSnapshotsParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"api_version": api_version}, operation_snapshots_params.OperationSnapshotsParams
                ),
            ),
            cast_to=RequestTracker,
        )

    async def suspend(
        self,
        id: str,
        *,
        api_version: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RequestTracker:
        """
        Second day suspend operation for machine

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._post(
            f"/iaas/api/machines/{id}/operations/suspend",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"api_version": api_version}, operation_suspend_params.OperationSuspendParams
                ),
            ),
            cast_to=RequestTracker,
        )

    async def unregister(
        self,
        id: str,
        *,
        api_version: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RequestTracker:
        """
        Unregister a vSphere provisioned machine

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._post(
            f"/iaas/api/machines/{id}/operations/unregister",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"api_version": api_version}, operation_unregister_params.OperationUnregisterParams
                ),
            ),
            cast_to=RequestTracker,
        )


class OperationsResourceWithRawResponse:
    def __init__(self, operations: OperationsResource) -> None:
        self._operations = operations

        self.update = to_raw_response_wrapper(
            operations.update,
        )
        self.change_security_groups = to_raw_response_wrapper(
            operations.change_security_groups,
        )
        self.power_off = to_raw_response_wrapper(
            operations.power_off,
        )
        self.power_on = to_raw_response_wrapper(
            operations.power_on,
        )
        self.reboot = to_raw_response_wrapper(
            operations.reboot,
        )
        self.reset = to_raw_response_wrapper(
            operations.reset,
        )
        self.resize = to_raw_response_wrapper(
            operations.resize,
        )
        self.restart = to_raw_response_wrapper(
            operations.restart,
        )
        self.shutdown = to_raw_response_wrapper(
            operations.shutdown,
        )
        self.snapshots = to_raw_response_wrapper(
            operations.snapshots,
        )
        self.suspend = to_raw_response_wrapper(
            operations.suspend,
        )
        self.unregister = to_raw_response_wrapper(
            operations.unregister,
        )


class AsyncOperationsResourceWithRawResponse:
    def __init__(self, operations: AsyncOperationsResource) -> None:
        self._operations = operations

        self.update = async_to_raw_response_wrapper(
            operations.update,
        )
        self.change_security_groups = async_to_raw_response_wrapper(
            operations.change_security_groups,
        )
        self.power_off = async_to_raw_response_wrapper(
            operations.power_off,
        )
        self.power_on = async_to_raw_response_wrapper(
            operations.power_on,
        )
        self.reboot = async_to_raw_response_wrapper(
            operations.reboot,
        )
        self.reset = async_to_raw_response_wrapper(
            operations.reset,
        )
        self.resize = async_to_raw_response_wrapper(
            operations.resize,
        )
        self.restart = async_to_raw_response_wrapper(
            operations.restart,
        )
        self.shutdown = async_to_raw_response_wrapper(
            operations.shutdown,
        )
        self.snapshots = async_to_raw_response_wrapper(
            operations.snapshots,
        )
        self.suspend = async_to_raw_response_wrapper(
            operations.suspend,
        )
        self.unregister = async_to_raw_response_wrapper(
            operations.unregister,
        )


class OperationsResourceWithStreamingResponse:
    def __init__(self, operations: OperationsResource) -> None:
        self._operations = operations

        self.update = to_streamed_response_wrapper(
            operations.update,
        )
        self.change_security_groups = to_streamed_response_wrapper(
            operations.change_security_groups,
        )
        self.power_off = to_streamed_response_wrapper(
            operations.power_off,
        )
        self.power_on = to_streamed_response_wrapper(
            operations.power_on,
        )
        self.reboot = to_streamed_response_wrapper(
            operations.reboot,
        )
        self.reset = to_streamed_response_wrapper(
            operations.reset,
        )
        self.resize = to_streamed_response_wrapper(
            operations.resize,
        )
        self.restart = to_streamed_response_wrapper(
            operations.restart,
        )
        self.shutdown = to_streamed_response_wrapper(
            operations.shutdown,
        )
        self.snapshots = to_streamed_response_wrapper(
            operations.snapshots,
        )
        self.suspend = to_streamed_response_wrapper(
            operations.suspend,
        )
        self.unregister = to_streamed_response_wrapper(
            operations.unregister,
        )


class AsyncOperationsResourceWithStreamingResponse:
    def __init__(self, operations: AsyncOperationsResource) -> None:
        self._operations = operations

        self.update = async_to_streamed_response_wrapper(
            operations.update,
        )
        self.change_security_groups = async_to_streamed_response_wrapper(
            operations.change_security_groups,
        )
        self.power_off = async_to_streamed_response_wrapper(
            operations.power_off,
        )
        self.power_on = async_to_streamed_response_wrapper(
            operations.power_on,
        )
        self.reboot = async_to_streamed_response_wrapper(
            operations.reboot,
        )
        self.reset = async_to_streamed_response_wrapper(
            operations.reset,
        )
        self.resize = async_to_streamed_response_wrapper(
            operations.resize,
        )
        self.restart = async_to_streamed_response_wrapper(
            operations.restart,
        )
        self.shutdown = async_to_streamed_response_wrapper(
            operations.shutdown,
        )
        self.snapshots = async_to_streamed_response_wrapper(
            operations.snapshots,
        )
        self.suspend = async_to_streamed_response_wrapper(
            operations.suspend,
        )
        self.unregister = async_to_streamed_response_wrapper(
            operations.unregister,
        )
