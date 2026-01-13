"""Info resource for service information and health."""

from .._generated.models import (
    HealthCheckResponse,
    ServiceInfoResponse,
    TasksInfoResponse,
)
from ._base import AsyncBaseResource, BaseResource


class InfoResource(BaseResource):
    def info(self) -> ServiceInfoResponse:
        return ServiceInfoResponse(**self._transport.request("GET", "/api/v1/info"))

    def tasks(self) -> TasksInfoResponse:
        return TasksInfoResponse(**self._transport.request("GET", "/api/v1/info/tasks"))

    def health(self) -> HealthCheckResponse:
        return HealthCheckResponse(**self._transport.request("GET", "/api/v1/health"))


class AsyncInfoResource(AsyncBaseResource):
    async def info(self) -> ServiceInfoResponse:
        return ServiceInfoResponse(
            **await self._transport.request("GET", "/api/v1/info")
        )

    async def tasks(self) -> TasksInfoResponse:
        return TasksInfoResponse(
            **await self._transport.request("GET", "/api/v1/info/tasks")
        )

    async def health(self) -> HealthCheckResponse:
        return HealthCheckResponse(
            **await self._transport.request("GET", "/api/v1/health")
        )
