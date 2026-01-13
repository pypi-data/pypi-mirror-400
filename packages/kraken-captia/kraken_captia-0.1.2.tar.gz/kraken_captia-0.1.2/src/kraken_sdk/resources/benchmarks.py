"""Benchmarks resource."""

from .._generated.models import (
    AggregatedBenchmarkReportResponse,
    BenchmarkReportResponse,
    BenchmarkResponse,
    CreateBenchmarkRequest,
)
from ._base import AsyncBaseResource, BaseResource

ReportType = BenchmarkReportResponse | AggregatedBenchmarkReportResponse


class BenchmarksResource(BaseResource):
    def create(self, request: CreateBenchmarkRequest) -> BenchmarkResponse:
        return BenchmarkResponse(
            **self._transport.request(
                "POST", "/api/v1/benchmarks", json=request.model_dump(mode="json")
            )
        )

    def list(self, limit: int = 50) -> list[BenchmarkResponse]:
        return [
            BenchmarkResponse(**i)
            for i in self._transport.request(
                "GET", "/api/v1/benchmarks", params={"limit": limit}
            )
        ]

    def get(self, benchmark_id: str) -> BenchmarkResponse:
        return BenchmarkResponse(
            **self._transport.request("GET", f"/api/v1/benchmarks/{benchmark_id}")
        )

    def get_report(self, benchmark_id: str) -> ReportType:
        resp = self._transport.request(
            "GET", f"/api/v1/benchmarks/{benchmark_id}/report"
        )
        cls = (
            AggregatedBenchmarkReportResponse
            if resp.get("report_type") == "aggregated"
            else BenchmarkReportResponse
        )
        return cls(**resp)


class AsyncBenchmarksResource(AsyncBaseResource):
    async def create(self, request: CreateBenchmarkRequest) -> BenchmarkResponse:
        return BenchmarkResponse(
            **await self._transport.request(
                "POST", "/api/v1/benchmarks", json=request.model_dump(mode="json")
            )
        )

    async def list(self, limit: int = 50) -> list[BenchmarkResponse]:
        return [
            BenchmarkResponse(**i)
            for i in await self._transport.request(
                "GET", "/api/v1/benchmarks", params={"limit": limit}
            )
        ]

    async def get(self, benchmark_id: str) -> BenchmarkResponse:
        return BenchmarkResponse(
            **await self._transport.request("GET", f"/api/v1/benchmarks/{benchmark_id}")
        )

    async def get_report(self, benchmark_id: str) -> ReportType:
        resp = await self._transport.request(
            "GET", f"/api/v1/benchmarks/{benchmark_id}/report"
        )
        cls = (
            AggregatedBenchmarkReportResponse
            if resp.get("report_type") == "aggregated"
            else BenchmarkReportResponse
        )
        return cls(**resp)
