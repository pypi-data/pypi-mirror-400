from typing import Any


class KrakenError(Exception):
    """Base exception for all Kraken SDK errors."""

    pass


class KrakenTransportError(KrakenError):
    """Raised when a network error occurs."""

    pass


class KrakenHttpError(KrakenError):
    """Raised when the API returns a non-2xx response."""

    def __init__(
        self,
        message: str,
        status_code: int,
        method: str,
        url: str,
        request_id: str | None = None,
        detail: Any = None,
        raw_body: str | None = None,
        retry_after: float | None = None,
    ):
        super().__init__(message)
        self.status_code = status_code
        self.method = method
        self.url = url
        self.request_id = request_id
        self.detail = detail
        self.raw_body = raw_body
        self.retry_after = retry_after

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(status_code={self.status_code}, "
            f"method={self.method}, url={self.url}, request_id={self.request_id})"
        )

    def __str__(self) -> str:
        base = f"{self.__class__.__name__}: HTTP {self.status_code} for {self.method} {self.url}"
        if self.request_id:
            base += f" (request_id={self.request_id})"
        return base


class KrakenValidationError(KrakenHttpError):
    """Raised when the API returns a 400 or 422 error."""

    pass


class KrakenAuthError(KrakenHttpError):
    """Raised when the API returns a 401 or 403 error."""

    pass


class KrakenNotFoundError(KrakenHttpError):
    """Raised when the API returns a 404 error."""

    pass


class KrakenConflictError(KrakenHttpError):
    """Raised when the API returns a 409 error."""

    pass


class KrakenRateLimitError(KrakenHttpError):
    """Raised when the API returns a 429 error."""


class KrakenServerError(KrakenHttpError):
    """Raised when the API returns a 5xx error."""

    pass
