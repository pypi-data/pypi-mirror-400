"""HTTP transport layer with retry logic."""

import asyncio
import logging
import time
from typing import Any

import httpx

from .config import Config
from .exceptions import (
    KrakenAuthError,
    KrakenConflictError,
    KrakenHttpError,
    KrakenNotFoundError,
    KrakenRateLimitError,
    KrakenServerError,
    KrakenTransportError,
    KrakenValidationError,
)

logger = logging.getLogger("kraken_sdk")
logger.addHandler(logging.NullHandler())
RETRYABLE: set[int] = {408, 429, 500, 502, 503, 504}
ERROR_MAP: dict[int, tuple[type[KrakenHttpError], str]] = {
    400: (KrakenValidationError, "Validation error"),
    422: (KrakenValidationError, "Validation error"),
    401: (KrakenAuthError, "Auth error"),
    403: (KrakenAuthError, "Auth error"),
    404: (KrakenNotFoundError, "Not found"),
    409: (KrakenConflictError, "Conflict"),
    429: (KrakenRateLimitError, "Rate limited"),
}


class TransportBase:
    def __init__(self, config: Config) -> None:
        self.config = config
        self._headers: dict[str, str] = {"Accept": "application/json"}
        if config.user_agent:
            self._headers["User-Agent"] = config.user_agent
        if config.api_key:
            self._headers["X-API-Key"] = config.api_key

    def _backoff(self, attempt: int, retry_after: str | None = None) -> float:
        if retry_after:
            try:
                return float(retry_after)
            except ValueError:
                pass
        return float(min(2**attempt, 30.0))

    def _raise_error(self, r: httpx.Response) -> None:
        status, retry_h = r.status_code, r.headers.get("Retry-After")
        retry_after = (
            float(retry_h) if retry_h and retry_h.replace(".", "").isdigit() else None
        )
        try:
            detail = r.json()
        except Exception:
            detail = r.text
        cls, msg = ERROR_MAP.get(status) or (
            (KrakenServerError, "Server error")
            if status >= 500
            else (KrakenHttpError, f"HTTP {status}")
        )
        raise cls(
            message=msg,
            status_code=status,
            method=r.request.method,
            url=str(r.request.url),
            request_id=r.headers.get("x-request-id"),
            detail=detail,
            raw_body=r.text,
            retry_after=retry_after,
        )


class HttpxTransport(TransportBase):
    def __init__(self, config: Config) -> None:
        super().__init__(config)
        # Handle proxy configuration
        proxy = config.proxy if isinstance(config.proxy, str) else None
        mounts: dict[str, httpx.HTTPTransport] | None = None
        if isinstance(config.proxy, dict):
            mounts = {
                scheme: httpx.HTTPTransport(proxy=proxy_url)
                for scheme, proxy_url in config.proxy.items()
            }
        self._client = httpx.Client(
            base_url=config.base_url,
            headers=self._headers,
            timeout=config.timeout,
            proxy=proxy,
            mounts=mounts,
        )

    def request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: Any = None,
        data: Any = None,
        files: Any = None,
        headers: dict[str, str] | None = None,
        raw_response: bool = False,
    ) -> Any:
        last_exc: Exception | None = None
        for attempt in range(self.config.retries + 1):
            try:
                r = self._client.request(
                    method,
                    path,
                    params=params,
                    json=json,
                    data=data,
                    files=files,
                    headers=headers,
                )
                if r.status_code in RETRYABLE and attempt < self.config.retries:
                    time.sleep(self._backoff(attempt, r.headers.get("Retry-After")))
                    continue
                if r.is_success:
                    if raw_response:
                        return r
                    if r.headers.get("content-type", "").startswith("application/json"):
                        return r.json()
                    return r.content
                self._raise_error(r)
            except httpx.RequestError as e:
                last_exc = e
                if attempt < self.config.retries:
                    time.sleep(self._backoff(attempt))
                    continue
                raise KrakenTransportError(f"Network error: {e}") from e
        if last_exc:
            raise KrakenTransportError(f"Request failed: {last_exc}") from last_exc
        return None

    def close(self) -> None:
        self._client.close()


class HttpxAsyncTransport(TransportBase):
    def __init__(self, config: Config) -> None:
        super().__init__(config)
        # Handle proxy configuration
        proxy = config.proxy if isinstance(config.proxy, str) else None
        mounts: dict[str, httpx.AsyncHTTPTransport] | None = None
        if isinstance(config.proxy, dict):
            mounts = {
                scheme: httpx.AsyncHTTPTransport(proxy=proxy_url)
                for scheme, proxy_url in config.proxy.items()
            }
        self._client = httpx.AsyncClient(
            base_url=config.base_url,
            headers=self._headers,
            timeout=config.timeout,
            proxy=proxy,
            mounts=mounts,
        )

    async def request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: Any = None,
        data: Any = None,
        files: Any = None,
        headers: dict[str, str] | None = None,
        raw_response: bool = False,
    ) -> Any:
        last_exc: Exception | None = None
        for attempt in range(self.config.retries + 1):
            try:
                r = await self._client.request(
                    method,
                    path,
                    params=params,
                    json=json,
                    data=data,
                    files=files,
                    headers=headers,
                )
                if r.status_code in RETRYABLE and attempt < self.config.retries:
                    await asyncio.sleep(
                        self._backoff(attempt, r.headers.get("Retry-After"))
                    )
                    continue
                if r.is_success:
                    if raw_response:
                        return r
                    if r.headers.get("content-type", "").startswith("application/json"):
                        return r.json()
                    return r.content
                self._raise_error(r)
            except httpx.RequestError as e:
                last_exc = e
                if attempt < self.config.retries:
                    await asyncio.sleep(self._backoff(attempt))
                    continue
                raise KrakenTransportError(f"Network error: {e}") from e
        if last_exc:
            raise KrakenTransportError(f"Request failed: {last_exc}") from last_exc
        return None

    async def close(self) -> None:
        await self._client.aclose()
