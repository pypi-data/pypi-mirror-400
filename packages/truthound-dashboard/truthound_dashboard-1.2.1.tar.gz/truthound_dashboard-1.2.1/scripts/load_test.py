#!/usr/bin/env python3
"""Load testing script for truthound-dashboard.

This script performs load testing against the dashboard API
to verify performance under concurrent load.

Features:
- Configurable concurrency and request count
- Multiple endpoint testing
- Latency percentile reporting
- Async implementation for high concurrency

Usage:
    python scripts/load_test.py
    python scripts/load_test.py --requests 500 --concurrency 20
    python scripts/load_test.py --base-url http://localhost:9000
"""

from __future__ import annotations

import argparse
import asyncio
import statistics
import time
from dataclasses import dataclass, field
from typing import Any

import httpx


@dataclass
class RequestResult:
    """Result of a single request.

    Attributes:
        url: Request URL.
        method: HTTP method.
        status_code: Response status code.
        duration_ms: Request duration in milliseconds.
        success: Whether request was successful.
        error: Error message if failed.
    """

    url: str
    method: str
    status_code: int | None = None
    duration_ms: float = 0.0
    success: bool = False
    error: str | None = None


@dataclass
class LoadTestResult:
    """Result of a load test run.

    Attributes:
        total_requests: Total number of requests.
        successful_requests: Number of successful requests.
        failed_requests: Number of failed requests.
        total_duration_ms: Total test duration in milliseconds.
        avg_latency_ms: Average latency in milliseconds.
        min_latency_ms: Minimum latency in milliseconds.
        max_latency_ms: Maximum latency in milliseconds.
        p50_latency_ms: 50th percentile latency.
        p95_latency_ms: 95th percentile latency.
        p99_latency_ms: 99th percentile latency.
        requests_per_second: Requests per second.
        results: Individual request results.
    """

    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_duration_ms: float = 0.0
    avg_latency_ms: float = 0.0
    min_latency_ms: float = 0.0
    max_latency_ms: float = 0.0
    p50_latency_ms: float = 0.0
    p95_latency_ms: float = 0.0
    p99_latency_ms: float = 0.0
    requests_per_second: float = 0.0
    results: list[RequestResult] = field(default_factory=list)
    status_codes: dict[int, int] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "total_requests": self.total_requests,
            "successful_requests": self.successful_requests,
            "failed_requests": self.failed_requests,
            "success_rate": (
                f"{self.successful_requests / self.total_requests * 100:.1f}%"
                if self.total_requests > 0
                else "N/A"
            ),
            "total_duration_ms": round(self.total_duration_ms, 2),
            "avg_latency_ms": round(self.avg_latency_ms, 2),
            "min_latency_ms": round(self.min_latency_ms, 2),
            "max_latency_ms": round(self.max_latency_ms, 2),
            "p50_latency_ms": round(self.p50_latency_ms, 2),
            "p95_latency_ms": round(self.p95_latency_ms, 2),
            "p99_latency_ms": round(self.p99_latency_ms, 2),
            "requests_per_second": round(self.requests_per_second, 2),
            "status_codes": self.status_codes,
        }


class LoadTester:
    """Async load tester for HTTP endpoints.

    Performs concurrent requests to test endpoint performance.
    """

    def __init__(
        self,
        base_url: str = "http://localhost:8765",
        timeout: float = 30.0,
    ) -> None:
        """Initialize load tester.

        Args:
            base_url: Base URL for the API.
            timeout: Request timeout in seconds.
        """
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout

    async def make_request(
        self,
        client: httpx.AsyncClient,
        method: str,
        path: str,
        **kwargs: Any,
    ) -> RequestResult:
        """Make a single HTTP request.

        Args:
            client: HTTP client instance.
            method: HTTP method.
            path: URL path.
            **kwargs: Additional request arguments.

        Returns:
            RequestResult with timing and status info.
        """
        url = f"{self._base_url}{path}"
        start_time = time.perf_counter()

        try:
            response = await client.request(method, url, **kwargs)
            duration_ms = (time.perf_counter() - start_time) * 1000

            return RequestResult(
                url=url,
                method=method,
                status_code=response.status_code,
                duration_ms=duration_ms,
                success=response.is_success,
            )

        except httpx.TimeoutException:
            duration_ms = (time.perf_counter() - start_time) * 1000
            return RequestResult(
                url=url,
                method=method,
                duration_ms=duration_ms,
                success=False,
                error="Timeout",
            )

        except Exception as e:
            duration_ms = (time.perf_counter() - start_time) * 1000
            return RequestResult(
                url=url,
                method=method,
                duration_ms=duration_ms,
                success=False,
                error=str(e),
            )

    async def run_test(
        self,
        endpoints: list[tuple[str, str]],
        num_requests: int = 100,
        concurrency: int = 10,
    ) -> LoadTestResult:
        """Run load test.

        Args:
            endpoints: List of (method, path) tuples.
            num_requests: Total number of requests to make.
            concurrency: Number of concurrent requests.

        Returns:
            LoadTestResult with test statistics.
        """
        result = LoadTestResult(total_requests=num_requests)
        semaphore = asyncio.Semaphore(concurrency)

        async def request_with_semaphore(
            client: httpx.AsyncClient,
            method: str,
            path: str,
        ) -> RequestResult:
            async with semaphore:
                return await self.make_request(client, method, path)

        start_time = time.perf_counter()

        async with httpx.AsyncClient(timeout=self._timeout) as client:
            tasks = []
            for i in range(num_requests):
                method, path = endpoints[i % len(endpoints)]
                tasks.append(request_with_semaphore(client, method, path))

            results = await asyncio.gather(*tasks)

        result.total_duration_ms = (time.perf_counter() - start_time) * 1000
        result.results = list(results)

        # Calculate statistics
        self._calculate_stats(result)

        return result

    def _calculate_stats(self, result: LoadTestResult) -> None:
        """Calculate statistics from results.

        Args:
            result: LoadTestResult to populate with statistics.
        """
        latencies = []
        status_codes: dict[int, int] = {}

        for r in result.results:
            if r.success:
                result.successful_requests += 1
                latencies.append(r.duration_ms)
            else:
                result.failed_requests += 1

            if r.status_code:
                status_codes[r.status_code] = status_codes.get(r.status_code, 0) + 1

        result.status_codes = status_codes

        if latencies:
            latencies.sort()
            result.avg_latency_ms = statistics.mean(latencies)
            result.min_latency_ms = min(latencies)
            result.max_latency_ms = max(latencies)

            # Percentiles
            result.p50_latency_ms = self._percentile(latencies, 50)
            result.p95_latency_ms = self._percentile(latencies, 95)
            result.p99_latency_ms = self._percentile(latencies, 99)

        if result.total_duration_ms > 0:
            result.requests_per_second = (
                result.total_requests / (result.total_duration_ms / 1000)
            )

    @staticmethod
    def _percentile(sorted_data: list[float], percentile: float) -> float:
        """Calculate percentile from sorted data.

        Args:
            sorted_data: Sorted list of values.
            percentile: Percentile to calculate (0-100).

        Returns:
            Percentile value.
        """
        if not sorted_data:
            return 0.0
        k = (len(sorted_data) - 1) * (percentile / 100)
        f = int(k)
        c = f + 1 if f + 1 < len(sorted_data) else f
        return sorted_data[f] + (k - f) * (sorted_data[c] - sorted_data[f])


def print_report(result: LoadTestResult) -> None:
    """Print formatted test report.

    Args:
        result: LoadTestResult to print.
    """
    print("\n" + "=" * 60)
    print("LOAD TEST REPORT")
    print("=" * 60)

    print(f"\n{'Total Requests:':<25} {result.total_requests}")
    print(f"{'Successful:':<25} {result.successful_requests}")
    print(f"{'Failed:':<25} {result.failed_requests}")

    if result.total_requests > 0:
        success_rate = result.successful_requests / result.total_requests * 100
        print(f"{'Success Rate:':<25} {success_rate:.1f}%")

    print(f"\n{'Total Duration:':<25} {result.total_duration_ms:.2f} ms")
    print(f"{'Requests/Second:':<25} {result.requests_per_second:.2f}")

    print(f"\n{'Latency Statistics:'}")
    print(f"{'  Average:':<25} {result.avg_latency_ms:.2f} ms")
    print(f"{'  Min:':<25} {result.min_latency_ms:.2f} ms")
    print(f"{'  Max:':<25} {result.max_latency_ms:.2f} ms")
    print(f"{'  P50:':<25} {result.p50_latency_ms:.2f} ms")
    print(f"{'  P95:':<25} {result.p95_latency_ms:.2f} ms")
    print(f"{'  P99:':<25} {result.p99_latency_ms:.2f} ms")

    if result.status_codes:
        print(f"\n{'Status Codes:'}")
        for code, count in sorted(result.status_codes.items()):
            print(f"  {code}: {count}")

    print("\n" + "=" * 60)


async def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Load test for truthound-dashboard",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/load_test.py
  python scripts/load_test.py --requests 500 --concurrency 20
  python scripts/load_test.py --base-url http://localhost:9000
        """,
    )
    parser.add_argument(
        "--base-url",
        default="http://localhost:8765",
        help="Base URL for the API (default: http://localhost:8765)",
    )
    parser.add_argument(
        "--requests",
        type=int,
        default=100,
        help="Total number of requests (default: 100)",
    )
    parser.add_argument(
        "--concurrency",
        type=int,
        default=10,
        help="Number of concurrent requests (default: 10)",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=30.0,
        help="Request timeout in seconds (default: 30.0)",
    )

    args = parser.parse_args()

    # Define endpoints to test
    endpoints = [
        ("GET", "/api/v1/health"),
        ("GET", "/api/v1/sources"),
        ("GET", "/api/v1/schedules"),
    ]

    print(f"\nStarting load test...")
    print(f"Base URL: {args.base_url}")
    print(f"Requests: {args.requests}")
    print(f"Concurrency: {args.concurrency}")
    print(f"Endpoints: {', '.join(f'{m} {p}' for m, p in endpoints)}")

    tester = LoadTester(base_url=args.base_url, timeout=args.timeout)

    result = await tester.run_test(
        endpoints=endpoints,
        num_requests=args.requests,
        concurrency=args.concurrency,
    )

    print_report(result)

    # Exit with error code if too many failures
    if result.total_requests > 0:
        failure_rate = result.failed_requests / result.total_requests
        if failure_rate > 0.1:  # More than 10% failures
            print("\nWARNING: High failure rate detected!")
            exit(1)


if __name__ == "__main__":
    asyncio.run(main())
