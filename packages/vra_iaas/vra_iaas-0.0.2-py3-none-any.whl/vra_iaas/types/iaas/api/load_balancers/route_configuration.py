# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from pydantic import Field as FieldInfo

from ....._models import BaseModel

__all__ = ["RouteConfiguration", "HealthCheckConfiguration"]


class HealthCheckConfiguration(BaseModel):
    """Load balancer health check configuration."""

    healthy_threshold: Optional[int] = FieldInfo(alias="healthyThreshold", default=None)
    """
    Number of consecutive successful checks before considering a particular back-end
    instance as healthy.
    """

    http_method: Optional[str] = FieldInfo(alias="httpMethod", default=None)
    """HTTP or HTTPS method to use when sending a health check request."""

    interval_seconds: Optional[int] = FieldInfo(alias="intervalSeconds", default=None)
    """Interval (in seconds) at which the health checks will be performed."""

    passive_monitor: Optional[bool] = FieldInfo(alias="passiveMonitor", default=None)
    """Enable passive monitor mode. This setting only applies to NSX-T."""

    port: Optional[str] = None
    """Port on the back-end instance machine to use for the health check."""

    protocol: Optional[str] = None
    """The protocol used for the health check."""

    request_body: Optional[str] = FieldInfo(alias="requestBody", default=None)
    """Request body. Used by HTTP, HTTPS, TCP, UDP."""

    response_body: Optional[str] = FieldInfo(alias="responseBody", default=None)
    """Expected response body. Used by HTTP, HTTPS, TCP, UDP."""

    timeout_seconds: Optional[int] = FieldInfo(alias="timeoutSeconds", default=None)
    """Timeout (in seconds) to wait for a response from the back-end instance."""

    unhealthy_threshold: Optional[int] = FieldInfo(alias="unhealthyThreshold", default=None)
    """
    Number of consecutive check failures before considering a particular back-end
    instance as unhealthy.
    """

    url_path: Optional[str] = FieldInfo(alias="urlPath", default=None)
    """
    URL path on the back-end instance against which a request will be performed for
    the health check. Useful when the health check protocol is HTTP/HTTPS.
    """


class RouteConfiguration(BaseModel):
    """Load balancer route configuration."""

    member_port: str = FieldInfo(alias="memberPort")
    """Member port where the traffic is routed to."""

    member_protocol: str = FieldInfo(alias="memberProtocol")
    """The protocol of the member traffic."""

    port: str
    """Port which the load balancer is listening to."""

    protocol: str
    """The protocol of the incoming load balancer requests."""

    algorithm: Optional[str] = None
    """Algorithm employed for load balancing."""

    algorithm_parameters: Optional[str] = FieldInfo(alias="algorithmParameters", default=None)
    """
    Parameters need for load balancing algorithm.Use newline to separate multiple
    parameters.
    """

    health_check_configuration: Optional[HealthCheckConfiguration] = FieldInfo(
        alias="healthCheckConfiguration", default=None
    )
    """Load balancer health check configuration."""
