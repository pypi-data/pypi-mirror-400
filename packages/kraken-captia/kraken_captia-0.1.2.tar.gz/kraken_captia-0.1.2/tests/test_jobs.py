"""Tests for Jobs resource."""

import respx
from httpx import Response

from kraken_sdk import KrakenClient
from kraken_sdk.types import JobSummary, ProcessResponse


@respx.mock
def test_jobs_create_single(client: KrakenClient) -> None:
    """Test creating a single job."""
    respx.post("https://api.kraken.test/api/v1/jobs").mock(
        return_value=Response(
            200,
            json={
                "success": True,
                "job_id": "job-123",
                "status": "PENDING",
                "submitted_at": "2024-01-01T00:00:00Z",
                "message": "Job created",
                "tasks_count": 1,
                "sources_count": 1,
            },
        )
    )

    from kraken_sdk.types import ExtractionTaskRequest

    task = ExtractionTaskRequest(
        task_type="extraction",
        ai_provider="openai",
        provider_model="gpt-4.1",
        source_id="source-123",
    )

    result = client.jobs.create_single(task)

    assert isinstance(result, ProcessResponse)
    assert result.job_id == "job-123"
    assert result.status == "PENDING"
    assert result.success is True


@respx.mock
def test_jobs_list(client: KrakenClient) -> None:
    """Test listing jobs."""
    respx.get("https://api.kraken.test/api/v1/jobs").mock(
        return_value=Response(
            200,
            json={
                "jobs": [
                    {
                        "id": "job-1",
                        "status": "COMPLETED",
                        "user_id": "user-1",
                        "submitted_at": "2024-01-01T00:00:00Z",
                        "progress": {},
                    },
                    {
                        "id": "job-2",
                        "status": "PENDING",
                        "user_id": "user-1",
                        "submitted_at": "2024-01-01T00:00:00Z",
                        "progress": {},
                    },
                ],
                "total_count": 2,
                "user_id": "user-1",
                "timestamp": "2024-01-01T00:00:00Z",
            },
        )
    )

    result = client.jobs.list(limit=10)

    assert result.total_count == 2
    assert len(result.jobs) == 2
    assert result.jobs[0].id == "job-1"
    assert result.jobs[0].status == "COMPLETED"


@respx.mock
def test_jobs_get(client: KrakenClient) -> None:
    """Test getting a specific job."""
    respx.get("https://api.kraken.test/api/v1/jobs/job-123").mock(
        return_value=Response(
            200,
            json={
                "id": "job-123",
                "status": "COMPLETED",
                "user_id": "user-1",
                "submitted_at": "2024-01-01T00:00:00Z",
                "completed_at": "2024-01-01T00:01:00Z",
                "progress": {"completed": 1, "total": 1},
            },
        )
    )

    result = client.jobs.get("job-123")

    assert isinstance(result, JobSummary)
    assert result.id == "job-123"
    assert result.status == "COMPLETED"


@respx.mock
def test_jobs_tasks(client: KrakenClient) -> None:
    """Test getting job tasks."""
    respx.get("https://api.kraken.test/api/v1/jobs/job-123/tasks").mock(
        return_value=Response(
            200,
            json={
                "job_id": "job-123",
                "tasks": [
                    {
                        "id": "task-1",
                        "job_id": "job-123",
                        "source_id": "source-1",
                        "task_type": "extraction",
                        "ai_provider": "openai",
                        "provider_model": "gpt-4.1",
                        "status": "COMPLETED",
                        "created_at": "2024-01-01T00:00:00Z",
                        "result": {"extracted_text": "Hello world"},
                    }
                ],
                "total_tasks": 1,
                "completed_tasks": 1,
                "timestamp": "2024-01-01T00:00:00Z",
            },
        )
    )

    result = client.jobs.tasks("job-123")

    assert result.job_id == "job-123"
    assert result.total_tasks == 1
    assert result.completed_tasks == 1
    assert len(result.tasks) == 1
    assert result.tasks[0].status == "COMPLETED"
