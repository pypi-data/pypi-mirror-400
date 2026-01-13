from collections.abc import Mapping
from dataclasses import dataclass

from ._version import __version__

ProxyTypes = str | Mapping[str, str] | None


@dataclass
class Config:
    base_url: str
    api_key: str | None = None
    timeout: float = 60.0
    retries: int = 3
    proxy: ProxyTypes = None
    user_agent: str | None = None

    def __post_init__(self) -> None:
        self.base_url = self.base_url.rstrip("/")
        if not self.user_agent:
            self.user_agent = f"kraken-sdk-python/{__version__}"
