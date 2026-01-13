"""Auth resource for user authentication."""

from .._generated.models import UserResponse
from ._base import AsyncBaseResource, BaseResource


class AuthResource(BaseResource):
    def me(self) -> UserResponse:
        return UserResponse(**self._transport.request("GET", "/api/v1/auth/me"))


class AsyncAuthResource(AsyncBaseResource):
    async def me(self) -> UserResponse:
        return UserResponse(**await self._transport.request("GET", "/api/v1/auth/me"))
