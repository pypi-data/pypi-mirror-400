# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from ....._utils import PropertyInfo

__all__ = ["RouteConfigurationParam", "HealthCheckConfiguration"]


class HealthCheckConfiguration(TypedDict, total=False):
    """Load balancer health check configuration."""

    healthy_threshold: Annotated[int, PropertyInfo(alias="healthyThreshold")]
    """
    Number of consecutive successful checks before considering a particular back-end
    instance as healthy.
    """

    http_method: Annotated[str, PropertyInfo(alias="httpMethod")]
    """HTTP or HTTPS method to use when sending a health check request."""

    interval_seconds: Annotated[int, PropertyInfo(alias="intervalSeconds")]
    """Interval (in seconds) at which the health checks will be performed."""

    passive_monitor: Annotated[bool, PropertyInfo(alias="passiveMonitor")]
    """Enable passive monitor mode. This setting only applies to NSX-T."""

    port: str
    """Port on the back-end instance machine to use for the health check."""

    protocol: str
    """The protocol used for the health check."""

    request_body: Annotated[str, PropertyInfo(alias="requestBody")]
    """Request body. Used by HTTP, HTTPS, TCP, UDP."""

    response_body: Annotated[str, PropertyInfo(alias="responseBody")]
    """Expected response body. Used by HTTP, HTTPS, TCP, UDP."""

    timeout_seconds: Annotated[int, PropertyInfo(alias="timeoutSeconds")]
    """Timeout (in seconds) to wait for a response from the back-end instance."""

    unhealthy_threshold: Annotated[int, PropertyInfo(alias="unhealthyThreshold")]
    """
    Number of consecutive check failures before considering a particular back-end
    instance as unhealthy.
    """

    url_path: Annotated[str, PropertyInfo(alias="urlPath")]
    """
    URL path on the back-end instance against which a request will be performed for
    the health check. Useful when the health check protocol is HTTP/HTTPS.
    """


class RouteConfigurationParam(TypedDict, total=False):
    """Load balancer route configuration."""

    member_port: Required[Annotated[str, PropertyInfo(alias="memberPort")]]
    """Member port where the traffic is routed to."""

    member_protocol: Required[Annotated[str, PropertyInfo(alias="memberProtocol")]]
    """The protocol of the member traffic."""

    port: Required[str]
    """Port which the load balancer is listening to."""

    protocol: Required[str]
    """The protocol of the incoming load balancer requests."""

    algorithm: str
    """Algorithm employed for load balancing."""

    algorithm_parameters: Annotated[str, PropertyInfo(alias="algorithmParameters")]
    """
    Parameters need for load balancing algorithm.Use newline to separate multiple
    parameters.
    """

    health_check_configuration: Annotated[HealthCheckConfiguration, PropertyInfo(alias="healthCheckConfiguration")]
    """Load balancer health check configuration."""
