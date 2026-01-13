"""Provider API keys resource."""

from .._generated.models import (
    ApiKeyCreatedResponse,
    ApiKeyResponse,
    CreateApiKeyRequest,
    UserApiKeysResponse,
)
from ._base import AsyncBaseResource, BaseResource


class ProviderApiKeysResource(BaseResource):
    def create(
        self, provider: str, api_key: str, description: str | None = None
    ) -> ApiKeyCreatedResponse:
        data = CreateApiKeyRequest(
            provider=provider, api_key=api_key, description=description
        ).model_dump(mode="json")
        return ApiKeyCreatedResponse(
            **self._transport.request("POST", "/api/v1/provider-api-keys", json=data)
        )

    def list(
        self, active_only: bool = True, provider: str | None = None
    ) -> UserApiKeysResponse:
        params = {
            "active_only": active_only,
            **({"provider": provider} if provider else {}),
        }
        return UserApiKeysResponse(
            **self._transport.request("GET", "/api/v1/provider-api-keys", params=params)
        )

    def get(self, api_key_id: str) -> ApiKeyResponse:
        return ApiKeyResponse(
            **self._transport.request("GET", f"/api/v1/provider-api-keys/{api_key_id}")
        )

    def delete(self, api_key_id: str) -> None:
        self._transport.request("DELETE", f"/api/v1/provider-api-keys/{api_key_id}")


class AsyncProviderApiKeysResource(AsyncBaseResource):
    async def create(
        self, provider: str, api_key: str, description: str | None = None
    ) -> ApiKeyCreatedResponse:
        data = CreateApiKeyRequest(
            provider=provider, api_key=api_key, description=description
        ).model_dump(mode="json")
        return ApiKeyCreatedResponse(
            **await self._transport.request(
                "POST", "/api/v1/provider-api-keys", json=data
            )
        )

    async def list(
        self, active_only: bool = True, provider: str | None = None
    ) -> UserApiKeysResponse:
        params = {
            "active_only": active_only,
            **({"provider": provider} if provider else {}),
        }
        return UserApiKeysResponse(
            **await self._transport.request(
                "GET", "/api/v1/provider-api-keys", params=params
            )
        )

    async def get(self, api_key_id: str) -> ApiKeyResponse:
        return ApiKeyResponse(
            **await self._transport.request(
                "GET", f"/api/v1/provider-api-keys/{api_key_id}"
            )
        )

    async def delete(self, api_key_id: str) -> None:
        await self._transport.request(
            "DELETE", f"/api/v1/provider-api-keys/{api_key_id}"
        )
