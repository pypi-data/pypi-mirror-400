"""Sources resource for file uploads."""

from typing import BinaryIO

from .._generated.models import UploadResponse
from .._utils.files import get_file_content
from ._base import AsyncBaseResource, BaseResource


class SourcesResource(BaseResource):
    def upload(
        self, file: str | bytes | BinaryIO, name: str | None = None
    ) -> UploadResponse:
        """Upload a source file."""
        filename, content, content_type = get_file_content(file, name)
        files = {"file": (filename, content, content_type)}
        data = {"name": name} if name else {}
        return UploadResponse(
            **self._transport.request(
                "POST", "/api/v1/sources/upload", files=files, data=data
            )
        )


class AsyncSourcesResource(AsyncBaseResource):
    async def upload(
        self, file: str | bytes | BinaryIO, name: str | None = None
    ) -> UploadResponse:
        """Upload a source file."""
        filename, content, content_type = get_file_content(file, name)
        files = {"file": (filename, content, content_type)}
        data = {"name": name} if name else {}
        return UploadResponse(
            **await self._transport.request(
                "POST", "/api/v1/sources/upload", files=files, data=data
            )
        )
