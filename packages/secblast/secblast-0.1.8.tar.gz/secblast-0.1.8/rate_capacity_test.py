#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "aiohttp",
# ]
# ///
"""
Rate Capacity Testing Script for SecBlast v2 API

Tests throughput and latency for all API endpoints at various concurrency levels.

Usage:
    uv run rate_capacity_test.py --help
    uv run rate_capacity_test.py --base-url http://localhost:3003 --api-key abc
"""

import asyncio
import argparse
import time
import statistics
from dataclasses import dataclass, field
from typing import Optional

import aiohttp


@dataclass
class EndpointConfig:
    """Configuration for a single API endpoint."""
    name: str
    path: str
    method: str = "GET"
    params: dict = field(default_factory=dict)
    json_body: Optional[dict] = None
    skip_in_quick_mode: bool = False


@dataclass
class TestResult:
    """Results from testing a single endpoint at one concurrency level."""
    endpoint: str
    concurrency: int
    total_requests: int
    successful_requests: int
    failed_requests: int
    total_time_seconds: float
    latencies_ms: list
    error_messages: list = field(default_factory=list)

    @property
    def rps(self) -> float:
        """Successful requests per second."""
        if self.total_time_seconds == 0:
            return 0
        return self.successful_requests / self.total_time_seconds

    @property
    def total_rps(self) -> float:
        """Total requests per second (including failures)."""
        if self.total_time_seconds == 0:
            return 0
        return self.total_requests / self.total_time_seconds

    @property
    def error_rate(self) -> float:
        if self.total_requests == 0:
            return 0
        return (self.failed_requests / self.total_requests) * 100

    def _percentile(self, p: float) -> float:
        """Calculate percentile using linear interpolation."""
        if not self.latencies_ms:
            return 0
        sorted_latencies = sorted(self.latencies_ms)
        n = len(sorted_latencies)
        if n == 1:
            return sorted_latencies[0]
        # Use 0-indexed position: p=0.50 with n=100 gives index 49.5
        pos = p * (n - 1)
        lower = int(pos)
        upper = min(lower + 1, n - 1)
        weight = pos - lower
        return sorted_latencies[lower] * (1 - weight) + sorted_latencies[upper] * weight

    @property
    def p50(self) -> float:
        return self._percentile(0.50)

    @property
    def p95(self) -> float:
        return self._percentile(0.95)

    @property
    def p99(self) -> float:
        return self._percentile(0.99)

    @property
    def mean_latency(self) -> float:
        if not self.latencies_ms:
            return 0
        return statistics.mean(self.latencies_ms)


# All v2 API endpoints to test
# Using CIK 1667919 and accession 0001445546-25-008723 as test data
ENDPOINTS = [
    # Infrastructure
    EndpointConfig(
        name="root",
        path="/",
        method="GET",
    ),
    EndpointConfig(
        name="health",
        path="/health",
        method="GET",
    ),
    # Core endpoints
    EndpointConfig(
        name="entity_lookup",
        path="/entity_lookup",
        method="GET",
        params={"ciks": "1667919"},
    ),
    EndpointConfig(
        name="filing_lookup",
        path="/filing_lookup",
        method="GET",
        params={"ciks": "1667919", "from": "0", "to": "5"},
    ),
    EndpointConfig(
        name="fulltext_search",
        path="/fulltext_search",
        method="GET",
        params={"query": "revenue", "from": "0", "to": "5"},
    ),
    EndpointConfig(
        name="document",
        path="/document",
        method="GET",
        params={"document_id": "0001445546-25-008723-1"},
        skip_in_quick_mode=True,
    ),
    EndpointConfig(
        name="filing_info",
        path="/filing_info",
        method="GET",
        params={"accession_number": "0001445546-25-008723"},
        skip_in_quick_mode=True,
    ),
    EndpointConfig(
        name="filing_sections",
        path="/filing_sections",
        method="GET",
        params={"document_id": "0001445546-25-008723-1"},
        skip_in_quick_mode=True,
    ),
    EndpointConfig(
        name="8k_items",
        path="/8k_items",
        method="POST",
        json_body={"accession_numbers": ["0001445546-25-008723"]},
        skip_in_quick_mode=True,
    ),
    EndpointConfig(
        name="pdf",
        path="/pdf",
        method="GET",
        params={"document_id": "0001445546-25-008723-1"},
        skip_in_quick_mode=True,
    ),
    # Financial endpoints (proxy to Python service on port 3008)
    EndpointConfig(
        name="financials/balance-sheet",
        path="/financials/balance-sheet",
        method="GET",
        params={"cik": "1667919"},
        skip_in_quick_mode=True,
    ),
    EndpointConfig(
        name="financials/income-statement",
        path="/financials/income-statement",
        method="GET",
        params={"cik": "1667919"},
        skip_in_quick_mode=True,
    ),
    EndpointConfig(
        name="financials/cash-flow",
        path="/financials/cash-flow",
        method="GET",
        params={"cik": "1667919"},
        skip_in_quick_mode=True,
    ),
    EndpointConfig(
        name="financials/raw",
        path="/financials/raw",
        method="GET",
        params={"cik": "1667919"},
        skip_in_quick_mode=True,
    ),
    EndpointConfig(
        name="financials/filings",
        path="/financials/filings",
        method="GET",
        params={"cik": "1667919"},
        skip_in_quick_mode=True,
    ),
    EndpointConfig(
        name="financials/history",
        path="/financials/history",
        method="GET",
        params={"cik": "1667919"},
        skip_in_quick_mode=True,
    ),
    EndpointConfig(
        name="financials/export/excel",
        path="/financials/export/excel",
        method="GET",
        params={"cik": "1667919"},
        skip_in_quick_mode=True,
    ),
]


async def make_request(
    session: aiohttp.ClientSession,
    base_url: str,
    endpoint: EndpointConfig,
    api_key: str,
    timeout: float,
) -> tuple[bool, float, str]:
    """
    Make a single HTTP request and return (success, latency_ms, error_message).
    """
    url = f"{base_url}{endpoint.path}"
    params = {**endpoint.params, "api_key": api_key}

    start_time = time.perf_counter()
    try:
        if endpoint.method == "GET":
            async with session.get(
                url,
                params=params,
                timeout=aiohttp.ClientTimeout(total=timeout),
            ) as response:
                await response.read()
                latency_ms = (time.perf_counter() - start_time) * 1000
                if response.status == 200:
                    return True, latency_ms, ""
                else:
                    return False, latency_ms, f"HTTP {response.status}"
        else:  # POST
            async with session.post(
                url,
                params=params,
                json=endpoint.json_body,
                timeout=aiohttp.ClientTimeout(total=timeout),
            ) as response:
                await response.read()
                latency_ms = (time.perf_counter() - start_time) * 1000
                if response.status == 200:
                    return True, latency_ms, ""
                else:
                    return False, latency_ms, f"HTTP {response.status}"
    except asyncio.TimeoutError:
        latency_ms = (time.perf_counter() - start_time) * 1000
        return False, latency_ms, "Timeout"
    except aiohttp.ClientError as e:
        latency_ms = (time.perf_counter() - start_time) * 1000
        return False, latency_ms, str(e)
    except Exception as e:
        latency_ms = (time.perf_counter() - start_time) * 1000
        return False, latency_ms, str(e)


async def test_endpoint(
    base_url: str,
    endpoint: EndpointConfig,
    api_key: str,
    concurrency: int,
    num_requests: int,
    timeout: float,
) -> TestResult:
    """
    Test an endpoint at a specific concurrency level.

    Fires `concurrency` requests in parallel, waits for all to complete,
    then fires the next batch. Repeats until num_requests total.
    """
    latencies = []
    errors = []
    successful = 0
    failed = 0

    # High limits to allow true parallel connections
    connector = aiohttp.TCPConnector(
        limit=0,  # No limit
        limit_per_host=0,  # No per-host limit
        force_close=False,
        enable_cleanup_closed=True,
    )

    client_timeout = aiohttp.ClientTimeout(total=timeout)

    async with aiohttp.ClientSession(connector=connector, timeout=client_timeout) as session:
        # Warmup - establish connections and verify endpoint works
        warmup_count = min(concurrency, 10)
        warmup_tasks = [make_request(session, base_url, endpoint, api_key, timeout) for _ in range(warmup_count)]
        warmup_results = await asyncio.gather(*warmup_tasks, return_exceptions=True)

        # Check warmup success rate
        warmup_failures = sum(1 for r in warmup_results if isinstance(r, Exception) or (isinstance(r, tuple) and not r[0]))
        if warmup_failures == warmup_count:
            # All warmup requests failed - return early with error
            return TestResult(
                endpoint=endpoint.name,
                concurrency=concurrency,
                total_requests=0,
                successful_requests=0,
                failed_requests=warmup_count,
                total_time_seconds=0,
                latencies_ms=[],
                error_messages=["All warmup requests failed - endpoint may be down"],
            )

        # Process in batches of `concurrency` size
        total_time = 0.0
        remaining = num_requests

        while remaining > 0:
            batch_size = min(concurrency, remaining)

            # Create all tasks for this batch
            tasks = [make_request(session, base_url, endpoint, api_key, timeout) for _ in range(batch_size)]

            # Fire all at once and measure
            start_time = time.perf_counter()
            results = await asyncio.gather(*tasks, return_exceptions=True)
            batch_time = time.perf_counter() - start_time
            total_time += batch_time

            # Process results
            for result in results:
                if isinstance(result, Exception):
                    failed += 1
                    errors.append(str(result))
                else:
                    success, latency, error = result
                    if success:
                        successful += 1
                        latencies.append(latency)  # Only include successful request latencies
                    else:
                        failed += 1
                        if error:
                            errors.append(error)

            remaining -= batch_size

    return TestResult(
        endpoint=endpoint.name,
        concurrency=concurrency,
        total_requests=num_requests,
        successful_requests=successful,
        failed_requests=failed,
        total_time_seconds=total_time,
        latencies_ms=latencies,
        error_messages=errors[:5],  # Keep first 5 errors
    )


def print_header():
    """Print the results table header."""
    print("\n" + "=" * 100)
    print("RATE CAPACITY TEST RESULTS")
    print("=" * 100)
    print(f"{'Endpoint':<30} {'Conc':>6} {'RPS':>10} {'p50(ms)':>10} {'p95(ms)':>10} {'p99(ms)':>10} {'Errors':>8}")
    print("-" * 100)


def print_result(result: TestResult):
    """Print a single test result row."""
    error_str = f"{result.error_rate:.1f}%"
    print(
        f"{result.endpoint:<30} "
        f"{result.concurrency:>6} "
        f"{result.rps:>10.1f} "
        f"{result.p50:>10.1f} "
        f"{result.p95:>10.1f} "
        f"{result.p99:>10.1f} "
        f"{error_str:>8}"
    )


def print_summary(all_results: list[TestResult]):
    """Print a summary of the test results."""
    print("\n" + "=" * 100)
    print("SUMMARY")
    print("=" * 100)

    # Find best RPS for each endpoint
    endpoint_best = {}
    for result in all_results:
        if result.endpoint not in endpoint_best:
            endpoint_best[result.endpoint] = result
        elif result.rps > endpoint_best[result.endpoint].rps:
            endpoint_best[result.endpoint] = result

    print(f"\n{'Endpoint':<30} {'Best RPS':>10} {'@ Conc':>8} {'Error%':>8}")
    print("-" * 60)
    for endpoint, result in sorted(endpoint_best.items(), key=lambda x: x[1].rps, reverse=True):
        print(f"{endpoint:<30} {result.rps:>10.1f} {result.concurrency:>8} {result.error_rate:>7.1f}%")

    # Identify bottlenecks
    print("\n" + "-" * 60)
    slowest = sorted(endpoint_best.values(), key=lambda x: x.rps)[:3]
    print("Slowest endpoints (potential bottlenecks):")
    for result in slowest:
        print(f"  - {result.endpoint}: {result.rps:.1f} RPS (p99: {result.p99:.1f}ms)")


async def main():
    parser = argparse.ArgumentParser(description="Rate capacity testing for SecBlast v2 API")
    parser.add_argument("--base-url", default="http://localhost:3003", help="API base URL")
    parser.add_argument("--api-key", default="abc", help="API key")
    parser.add_argument(
        "--concurrency",
        default="1,10,50,100,200,300,400,500",
        help="Comma-separated concurrency levels to test",
    )
    parser.add_argument("--requests", type=int, default=100, help="Number of requests per test")
    parser.add_argument("--timeout", type=float, default=30.0, help="Request timeout in seconds")
    parser.add_argument(
        "--endpoints",
        default=None,
        help="Comma-separated list of endpoints to test (default: all)",
    )
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Quick mode: skip slow endpoints like PDF and financials",
    )

    args = parser.parse_args()

    concurrency_levels = [int(c.strip()) for c in args.concurrency.split(",")]

    # Filter endpoints
    endpoints_to_test = ENDPOINTS
    if args.endpoints:
        names = [n.strip() for n in args.endpoints.split(",")]
        endpoints_to_test = [e for e in ENDPOINTS if e.name in names]
    elif args.quick:
        endpoints_to_test = [e for e in ENDPOINTS if not e.skip_in_quick_mode]

    if not endpoints_to_test:
        print("No endpoints to test!")
        return

    print(f"\nTesting {len(endpoints_to_test)} endpoints at concurrency levels: {concurrency_levels}")
    print(f"Requests per test: {args.requests}")
    print(f"Base URL: {args.base_url}")
    print(f"API Key: {args.api_key}")

    all_results = []

    print_header()

    for endpoint in endpoints_to_test:
        for concurrency in concurrency_levels:
            print(f"\rTesting {endpoint.name} @ {concurrency} concurrent...", end="", flush=True)

            result = await test_endpoint(
                base_url=args.base_url,
                endpoint=endpoint,
                api_key=args.api_key,
                concurrency=concurrency,
                num_requests=args.requests,
                timeout=args.timeout,
            )

            all_results.append(result)
            print("\r" + " " * 60 + "\r", end="")  # Clear progress line
            print_result(result)

            # Show first error if any
            if result.error_messages:
                print(f"  ^ First error: {result.error_messages[0][:60]}...")

    print_summary(all_results)


if __name__ == "__main__":
    asyncio.run(main())
