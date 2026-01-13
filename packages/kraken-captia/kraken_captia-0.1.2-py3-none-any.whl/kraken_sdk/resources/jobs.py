"""Jobs resource for creating and managing processing jobs."""

from typing import Any, overload

from .._generated.models import (
    AnnotationTaskConfig,
    AnnotationTaskRequest,
    BulkProcessRequest,
    BulkProcessResponse,
    ExtractionTaskConfig,
    ExtractionTaskRequest,
    JobsListResponse,
    JobSummary,
    JobTasksResponse,
    MultiTaskProcessRequest,
    MultiTaskProcessResponse,
    ProcessRequest,
    ProcessResponse,
    TaskConfig,
    TaskCreationRequest,
)
from .._utils.polling import wait_async, wait_sync
from ._base import AsyncBaseResource, BaseResource

_TERMINAL_STATUSES = ("COMPLETED", "FAILED", "PARTIAL_SUCCESS", "COMPLETED_WITH_ERRORS")
TaskRequest = ExtractionTaskRequest | AnnotationTaskRequest | TaskCreationRequest
TaskConfigType = ExtractionTaskConfig | AnnotationTaskConfig | TaskConfig
JobRequest = ProcessRequest | BulkProcessRequest | MultiTaskProcessRequest
JobResponse = ProcessResponse | BulkProcessResponse | MultiTaskProcessResponse

_MODE_RESPONSE: dict[
    str, type[ProcessResponse | BulkProcessResponse | MultiTaskProcessResponse]
] = {
    "single": ProcessResponse,
    "bulk": BulkProcessResponse,
    "multitask": MultiTaskProcessResponse,
}


def _parse_response(mode: str, resp: Any) -> JobResponse:
    """Parse response based on mode."""
    return _MODE_RESPONSE[mode](**resp)


class JobsResource(BaseResource):
    """Sync jobs resource."""

    @overload
    def create(self, request: ProcessRequest) -> ProcessResponse: ...
    @overload
    def create(self, request: BulkProcessRequest) -> BulkProcessResponse: ...
    @overload
    def create(self, request: MultiTaskProcessRequest) -> MultiTaskProcessResponse: ...

    def create(self, request: JobRequest) -> JobResponse:
        """Create a job (low-level)."""
        resp = self._transport.request(
            "POST", "/api/v1/jobs", json=request.model_dump(mode="json")
        )
        return _parse_response(request.mode, resp)

    def create_single(self, task: TaskRequest) -> ProcessResponse:
        """Create a single-task job."""
        return self.create(ProcessRequest(task=task, mode="single"))

    def create_bulk(
        self, task_config: TaskConfigType, source_ids: list[str]
    ) -> BulkProcessResponse:
        """Create a bulk job (one config → multiple sources)."""
        return self.create(
            BulkProcessRequest(
                task_config=task_config, source_ids=source_ids, mode="bulk"
            )
        )

    def create_multitask(
        self, source_id: str, task_configs: list[TaskConfigType]
    ) -> MultiTaskProcessResponse:
        """Create a multitask job (one source → multiple configs)."""
        return self.create(
            MultiTaskProcessRequest(
                source_id=source_id, task_configs=task_configs, mode="multitask"
            )
        )

    def list(self, limit: int = 50, offset: int = 0) -> JobsListResponse:
        """List jobs."""
        return JobsListResponse(
            **self._transport.request(
                "GET", "/api/v1/jobs", params={"limit": limit, "offset": offset}
            )
        )

    def get(self, job_id: str) -> JobSummary:
        """Get job details."""
        return JobSummary(**self._transport.request("GET", f"/api/v1/jobs/{job_id}"))

    def tasks(self, job_id: str) -> JobTasksResponse:
        """Get tasks for a job."""
        return JobTasksResponse(
            **self._transport.request("GET", f"/api/v1/jobs/{job_id}/tasks")
        )

    def wait(
        self, job_id: str, interval: float = 1.0, timeout: float | None = None
    ) -> JobSummary:
        """Wait for job completion."""
        return wait_sync(
            lambda: self.get(job_id),
            lambda j: j.status in _TERMINAL_STATUSES,
            interval,
            timeout,
        )


class AsyncJobsResource(AsyncBaseResource):
    """Async jobs resource."""

    @overload
    async def create(self, request: ProcessRequest) -> ProcessResponse: ...
    @overload
    async def create(self, request: BulkProcessRequest) -> BulkProcessResponse: ...
    @overload
    async def create(
        self, request: MultiTaskProcessRequest
    ) -> MultiTaskProcessResponse: ...

    async def create(self, request: JobRequest) -> JobResponse:
        """Create a job (low-level)."""
        resp = await self._transport.request(
            "POST", "/api/v1/jobs", json=request.model_dump(mode="json")
        )
        return _parse_response(request.mode, resp)

    async def create_single(self, task: TaskRequest) -> ProcessResponse:
        """Create a single-task job."""
        return await self.create(ProcessRequest(task=task, mode="single"))

    async def create_bulk(
        self, task_config: TaskConfigType, source_ids: list[str]
    ) -> BulkProcessResponse:
        """Create a bulk job (one config → multiple sources)."""
        return await self.create(
            BulkProcessRequest(
                task_config=task_config, source_ids=source_ids, mode="bulk"
            )
        )

    async def create_multitask(
        self, source_id: str, task_configs: list[TaskConfigType]
    ) -> MultiTaskProcessResponse:
        """Create a multitask job (one source → multiple configs)."""
        return await self.create(
            MultiTaskProcessRequest(
                source_id=source_id, task_configs=task_configs, mode="multitask"
            )
        )

    async def list(self, limit: int = 50, offset: int = 0) -> JobsListResponse:
        """List jobs."""
        return JobsListResponse(
            **await self._transport.request(
                "GET", "/api/v1/jobs", params={"limit": limit, "offset": offset}
            )
        )

    async def get(self, job_id: str) -> JobSummary:
        """Get job details."""
        return JobSummary(
            **await self._transport.request("GET", f"/api/v1/jobs/{job_id}")
        )

    async def tasks(self, job_id: str) -> JobTasksResponse:
        """Get tasks for a job."""
        return JobTasksResponse(
            **await self._transport.request("GET", f"/api/v1/jobs/{job_id}/tasks")
        )

    async def wait(
        self, job_id: str, interval: float = 1.0, timeout: float | None = None
    ) -> JobSummary:
        """Wait for job completion."""
        return await wait_async(
            lambda: self.get(job_id),
            lambda j: j.status in _TERMINAL_STATUSES,
            interval,
            timeout,
        )
