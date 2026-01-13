"""Kraken SDK clients."""

from .config import Config, ProxyTypes
from .resources import (
    AsyncAuthResource,
    AsyncBenchmarksResource,
    AsyncInfoResource,
    AsyncJobsResource,
    AsyncProviderApiKeysResource,
    AsyncSourcesResource,
    AuthResource,
    BenchmarksResource,
    InfoResource,
    JobsResource,
    ProviderApiKeysResource,
    SourcesResource,
)
from .transport import HttpxAsyncTransport, HttpxTransport


def _make_config(
    base_url: str,
    api_key: str | None,
    timeout: float,
    retries: int,
    proxy: ProxyTypes,
    user_agent: str | None,
) -> Config:
    return Config(
        base_url=base_url,
        api_key=api_key,
        timeout=timeout,
        retries=retries,
        proxy=proxy,
        user_agent=user_agent,
    )


class KrakenClient:
    def __init__(
        self,
        base_url: str,
        api_key: str | None = None,
        timeout: float = 60.0,
        retries: int = 3,
        proxy: ProxyTypes = None,
        user_agent: str | None = None,
    ) -> None:
        self.config = _make_config(
            base_url, api_key, timeout, retries, proxy, user_agent
        )
        self._transport = HttpxTransport(self.config)
        self.jobs, self.sources = (
            JobsResource(self._transport),
            SourcesResource(self._transport),
        )
        self.benchmarks, self.provider_api_keys = (
            BenchmarksResource(self._transport),
            ProviderApiKeysResource(self._transport),
        )
        self.info, self.auth = (
            InfoResource(self._transport),
            AuthResource(self._transport),
        )

    def close(self) -> None:
        self._transport.close()

    def __enter__(self) -> "KrakenClient":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()


class AsyncKrakenClient:
    def __init__(
        self,
        base_url: str,
        api_key: str | None = None,
        timeout: float = 60.0,
        retries: int = 3,
        proxy: ProxyTypes = None,
        user_agent: str | None = None,
    ) -> None:
        self.config = _make_config(
            base_url, api_key, timeout, retries, proxy, user_agent
        )
        self._transport = HttpxAsyncTransport(self.config)
        self.jobs, self.sources = (
            AsyncJobsResource(self._transport),
            AsyncSourcesResource(self._transport),
        )
        self.benchmarks, self.provider_api_keys = (
            AsyncBenchmarksResource(self._transport),
            AsyncProviderApiKeysResource(self._transport),
        )
        self.info, self.auth = (
            AsyncInfoResource(self._transport),
            AsyncAuthResource(self._transport),
        )

    async def close(self) -> None:
        await self._transport.close()

    async def __aenter__(self) -> "AsyncKrakenClient":
        return self

    async def __aexit__(self, *_: object) -> None:
        await self.close()
