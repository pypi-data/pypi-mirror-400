"""Tests for Sources upload functionality."""

import respx
from httpx import Response

from kraken_sdk import KrakenClient
from kraken_sdk.types import UploadResponse


@respx.mock
def test_upload_bytes(client: KrakenClient) -> None:
    """Test uploading bytes content."""
    respx.post("https://api.kraken.test/api/v1/sources/upload").mock(
        return_value=Response(
            200,
            json={
                "id": "source-123",
                "name": "test.txt",
                "type": "text",
                "size_bytes": 13,
                "content_hash": "sha256:abc123",
                "format": "text/plain",
                "deduplicated": False,
            },
        )
    )

    result = client.sources.upload(b"Hello, World!", name="test.txt")

    assert isinstance(result, UploadResponse)
    assert result.id == "source-123"
    assert result.name == "test.txt"
    assert result.deduplicated is False


@respx.mock
def test_upload_with_custom_name(client: KrakenClient) -> None:
    """Test uploading with a custom name."""
    respx.post("https://api.kraken.test/api/v1/sources/upload").mock(
        return_value=Response(
            200,
            json={
                "id": "source-456",
                "name": "custom_name.pdf",
                "type": "pdf",
                "size_bytes": 1024,
                "content_hash": "sha256:def456",
                "format": "application/pdf",
                "page_count": 5,
                "deduplicated": False,
            },
        )
    )

    result = client.sources.upload(b"PDF content here", name="custom_name.pdf")

    assert result.id == "source-456"
    assert result.name == "custom_name.pdf"
    assert result.page_count == 5


@respx.mock
def test_upload_deduplicated(client: KrakenClient) -> None:
    """Test upload when file already exists (deduplicated)."""
    respx.post("https://api.kraken.test/api/v1/sources/upload").mock(
        return_value=Response(
            200,
            json={
                "id": "source-existing",
                "name": "existing.txt",
                "type": "text",
                "size_bytes": 100,
                "content_hash": "sha256:existing",
                "format": "text/plain",
                "deduplicated": True,
            },
        )
    )

    result = client.sources.upload(b"Existing content")

    assert result.deduplicated is True
    assert result.id == "source-existing"
