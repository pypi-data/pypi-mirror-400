import pytest
import respx
from httpx import Response

from kraken_sdk import AsyncKrakenClient


@pytest.mark.asyncio
@respx.mock
async def test_smoke_async():
    respx.get("https://api.kraken.com/api/v1/info").mock(
        return_value=Response(
            200,
            json={
                "service": "kraken-gateway",
                "version": "1.0.0",
                "description": "Gateway service",
                "timestamp": "2023-01-01T00:00:00Z",
                "capabilities": {
                    "supported_task_types": ["extraction"],
                    "max_sources_per_job": 10,
                    "max_tasks_per_job": 10,
                    "max_file_size_mb": 50,
                    "async_execution": True,
                    "task_workers": 5,
                },
                "endpoints": {
                    "process": "/process",
                    "jobs": "/jobs",
                    "job_status": "/jobs/{id}",
                    "health": "/health",
                    "info": "/info",
                },
            },
        )
    )

    async with AsyncKrakenClient(base_url="https://api.kraken.com") as client:
        info = await client.info.info()

        assert info.service == "kraken-gateway"
        assert info.version == "1.0.0"
