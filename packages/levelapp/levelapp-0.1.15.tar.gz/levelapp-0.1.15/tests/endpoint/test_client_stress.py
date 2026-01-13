"""
Stress test suite for APIClient
Tests timeout handling, retries, concurrency, and error scenarios
"""
import asyncio
import time
import random
from typing import List, Dict, Any
from dataclasses import dataclass
from contextlib import asynccontextmanager

import httpx
from httpx import Response, Request


# Mock server responses for testing
class MockTransport(httpx.AsyncBaseTransport):
    """Mock HTTP transport for simulating various server behaviors"""

    def __init__(self, behavior: str = "normal"):
        self.behavior = behavior
        self.request_count = 0
        self.latencies: List[float] = []

    async def handle_async_request(self, request: Request) -> Response:
        """Simulate different server behaviors"""
        self.request_count += 1
        start = time.time()

        if self.behavior == "timeout":
            # Simulate server timeout (never responds)
            raise httpx.ReadTimeout("simulated read timeout")

        elif self.behavior == "slow":
            # Slow responses (2-5 seconds)
            await asyncio.sleep(random.uniform(2, 5))

        elif self.behavior == "intermittent":
            # 50% chance of timeout
            if random.random() < 0.5:
                raise httpx.ReadTimeout("Simulated intermittent timeout")
            else:
                await asyncio.sleep(0.1)

        elif self.behavior == "flaky":
            # Gradually improve: first 2 requests fail, then succeed
            if self.request_count <= 2:
                raise httpx.ReadTimeout("simulated flaky timeout")
            else:
                await asyncio.sleep(0.1)

        elif self.behavior == "normal":
            # Fast, successful responses
            await asyncio.sleep(random.uniform(0.01, 0.1))

        elif self.behavior == "error_500":
            # Return HTTP 500 errors
            await asyncio.sleep(0.1)
            return Response(
                status_code=500,
                content=b'{"error": "Internal Server Error"}',
                request=request
            )

        latency = time.time() - start
        self.latencies.append(latency)

        return Response(
            status_code=200,
            content=b'{"success": true, "data": "test"}',
            request=request,
            headers={"content-type": "application/json"}
        )


@dataclass
class StressTestResult:
    """Results from a stress test run"""
    test_name: str
    total_requests: int
    successful: int
    failed: int
    duration: float
    avg_latency: float
    min_latency: float
    max_latency: float
    requests_per_second: float
    error_types: Dict[str, int]

    def print_summary(self):
        """Print formatted test results"""
        print(f"\n{'=' * 60}")
        print(f"Test: {self.test_name}")
        print(f"{'=' * 60}")
        print(f"Total Requests:    {self.total_requests}")
        print(f"Successful:        {self.successful} ({self.successful / self.total_requests * 100:.1f}%)")
        print(f"Failed:            {self.failed} ({self.failed / self.total_requests * 100:.1f}%)")
        print(f"Duration:          {self.duration:.2f}s")
        print(f"Avg Latency:       {self.avg_latency * 1000:.2f}ms")
        print(f"Min Latency:       {self.min_latency * 1000:.2f}ms")
        print(f"Max Latency:       {self.max_latency * 1000:.2f}ms")
        print(f"Requests/sec:      {self.requests_per_second:.2f}")

        if self.error_types:
            print(f"\nError Breakdown:")
            for error_type, count in self.error_types.items():
                print(f"  {error_type}: {count}")
        print(f"{'=' * 60}\n")


class ClientStressTester:
    """Comprehensive stress testing for APIClient"""

    def __init__(self, client_class, config_class):
        self.client_class = client_class
        self.config_class = config_class

    @asynccontextmanager
    async def _create_test_client(self, behavior: str, **config_overrides):
        """Create a test client with mock transport"""

        # Base defaults
        base_config = dict(
            name="stress_test",
            base_url="https://mock.api.test",
            path="/test",
            method="POST",
            connect_timeout=1,
            read_timeout=2,
            write_timeout=1,
            pool_timeout=1,
        )

        # Allow overrides to replace defaults
        base_config.update(config_overrides)

        config = self.config_class(**base_config)

        client = self.client_class(config)

        # Replace transport with mock
        transport = MockTransport(behavior=behavior)
        client.client._transport = transport

        try:
            yield client, transport
        finally:
            await client.client.aclose()

    async def test_normal_load(self, num_requests: int = 100) -> StressTestResult:
        """Test normal server with concurrent requests"""
        start_time = time.time()
        successful = 0
        failed = 0
        error_types: Dict[str, int] = {}

        async with self._create_test_client(
                "normal",
                max_parallel_requests=20,
                retry_count=3
        ) as (client, transport):

            async def make_request():
                nonlocal successful, failed
                try:
                    await client.execute(payload={"test": "data"})
                    successful += 1
                except Exception as e:
                    failed += 1
                    error_name = type(e).__name__
                    error_types[error_name] = error_types.get(error_name, 0) + 1

            # Fire all requests concurrently
            await asyncio.gather(*[make_request() for _ in range(num_requests)])

        duration = time.time() - start_time
        latencies = transport.latencies

        return StressTestResult(
            test_name="Normal Load Test",
            total_requests=num_requests,
            successful=successful,
            failed=failed,
            duration=duration,
            avg_latency=sum(latencies) / len(latencies) if latencies else 0,
            min_latency=min(latencies) if latencies else 0,
            max_latency=max(latencies) if latencies else 0,
            requests_per_second=num_requests / duration,
            error_types=error_types
        )

    async def test_timeout_handling(self, num_requests: int = 10) -> StressTestResult:
        """Test behavior with server timeouts"""
        start_time = time.time()
        successful = 0
        failed = 0
        error_types: Dict[str, int] = {}

        async with self._create_test_client(
                "timeout",
                max_parallel_requests=5,
                retry_count=2,
                read_timeout=1
        ) as (client, transport):

            async def make_request():
                nonlocal successful, failed
                try:
                    await client.execute(payload={"test": "data"})
                    successful += 1
                except Exception as e:
                    failed += 1
                    error_name = type(e).__name__
                    error_types[error_name] = error_types.get(error_name, 0) + 1

            await asyncio.gather(*[make_request() for _ in range(num_requests)])

        duration = time.time() - start_time
        latencies = transport.latencies

        return StressTestResult(
            test_name="Timeout Handling Test",
            total_requests=num_requests,
            successful=successful,
            failed=failed,
            duration=duration,
            avg_latency=sum(latencies) / len(latencies) if latencies else 0,
            min_latency=min(latencies) if latencies else 0,
            max_latency=max(latencies) if latencies else 0,
            requests_per_second=num_requests / duration,
            error_types=error_types
        )

    async def test_retry_logic(self, num_requests: int = 20) -> StressTestResult:
        """Test retry behavior with flaky server"""
        start_time = time.time()
        successful = 0
        failed = 0
        error_types: Dict[str, int] = {}

        async with self._create_test_client(
                "flaky",
                max_parallel_requests=5,
                retry_count=3,
                read_timeout=1
        ) as (client, transport):

            async def make_request():
                nonlocal successful, failed
                try:
                    await client.execute(payload={"test": "data"})
                    successful += 1
                except Exception as e:
                    failed += 1
                    error_name = type(e).__name__
                    error_types[error_name] = error_types.get(error_name, 0) + 1

            await asyncio.gather(*[make_request() for _ in range(num_requests)])

        duration = time.time() - start_time
        latencies = transport.latencies

        return StressTestResult(
            test_name="Retry Logic Test (Flaky Server)",
            total_requests=num_requests,
            successful=successful,
            failed=failed,
            duration=duration,
            avg_latency=sum(latencies) / len(latencies) if latencies else 0,
            min_latency=min(latencies) if latencies else 0,
            max_latency=max(latencies) if latencies else 0,
            requests_per_second=num_requests / duration,
            error_types=error_types
        )

    async def test_concurrency_limits(self, num_requests: int = 100) -> StressTestResult:
        """Test semaphore concurrency control"""
        start_time = time.time()
        successful = 0
        failed = 0
        error_types: Dict[str, int] = {}
        max_concurrent = 0
        current_concurrent = 0

        async with self._create_test_client(
                "normal",
                max_parallel_requests=10,
                retry_count=1
        ) as (client, transport):

            async def make_request():
                nonlocal successful, failed, max_concurrent, current_concurrent

                current_concurrent += 1
                max_concurrent = max(max_concurrent, current_concurrent)

                try:
                    await client.execute(payload={"test": "data"})
                    successful += 1
                except Exception as e:
                    failed += 1
                    error_name = type(e).__name__
                    error_types[error_name] = error_types.get(error_name, 0) + 1
                finally:
                    current_concurrent -= 1

            await asyncio.gather(*[make_request() for _ in range(num_requests)])

        duration = time.time() - start_time
        latencies = transport.latencies

        print(f"Max concurrent requests observed: {max_concurrent}")

        return StressTestResult(
            test_name="Concurrency Limits Test",
            total_requests=num_requests,
            successful=successful,
            failed=failed,
            duration=duration,
            avg_latency=sum(latencies) / len(latencies) if latencies else 0,
            min_latency=min(latencies) if latencies else 0,
            max_latency=max(latencies) if latencies else 0,
            requests_per_second=num_requests / duration,
            error_types=error_types
        )

    async def test_http_errors(self, num_requests: int = 20) -> StressTestResult:
        """Test handling of HTTP error responses"""
        start_time = time.time()
        successful = 0
        failed = 0
        error_types: Dict[str, int] = {}

        async with self._create_test_client(
                "error_500",
                max_parallel_requests=5,
                retry_count=2
        ) as (client, transport):

            async def make_request():
                nonlocal successful, failed
                try:
                    await client.execute(payload={"test": "data"})
                    successful += 1
                except Exception as e:
                    failed += 1
                    error_name = type(e).__name__
                    error_types[error_name] = error_types.get(error_name, 0) + 1

            await asyncio.gather(*[make_request() for _ in range(num_requests)])

        duration = time.time() - start_time
        latencies = transport.latencies

        return StressTestResult(
            test_name="HTTP Error Handling Test",
            total_requests=num_requests,
            successful=successful,
            failed=failed,
            duration=duration,
            avg_latency=sum(latencies) / len(latencies) if latencies else 0,
            min_latency=min(latencies) if latencies else 0,
            max_latency=max(latencies) if latencies else 0,
            requests_per_second=num_requests / duration,
            error_types=error_types
        )

    async def run_all_tests(self):
        """Run complete stress test suite"""
        print("\n" + "=" * 60)
        print("STARTING COMPREHENSIVE STRESS TEST SUITE")
        print("=" * 60)

        results = []

        # Test 1: Normal load
        print("\n[1/5] Running normal load test...")
        result = await self.test_normal_load(num_requests=100)
        result.print_summary()
        results.append(result)

        # Test 2: Timeout handling
        print("\n[2/5] Running timeout handling test...")
        result = await self.test_timeout_handling(num_requests=10)
        result.print_summary()
        results.append(result)

        # Test 3: Retry logic
        print("\n[3/5] Running retry logic test...")
        result = await self.test_retry_logic(num_requests=20)
        result.print_summary()
        results.append(result)

        # Test 4: Concurrency limits
        print("\n[4/5] Running concurrency limits test...")
        result = await self.test_concurrency_limits(num_requests=100)
        result.print_summary()
        results.append(result)

        # Test 5: HTTP errors
        print("\n[5/5] Running HTTP error handling test...")
        result = await self.test_http_errors(num_requests=20)
        result.print_summary()
        results.append(result)

        # Overall summary
        print("\n" + "=" * 60)
        print("OVERALL SUMMARY")
        print("=" * 60)
        total_requests = sum(r.total_requests for r in results)
        total_successful = sum(r.successful for r in results)
        total_failed = sum(r.failed for r in results)
        total_duration = sum(r.duration for r in results)

        print(f"Total requests across all tests: {total_requests}")
        print(f"Total successful: {total_successful} ({total_successful / total_requests * 100:.1f}%)")
        print(f"Total failed: {total_failed} ({total_failed / total_requests * 100:.1f}%)")
        print(f"Total duration: {total_duration:.2f}s")
        print("=" * 60 + "\n")


# Example usage
async def main():
    """Run the stress tests"""
    # Import your actual client classes
    from levelapp.endpoint.client import APIClient, EndpointConfig

    tester = ClientStressTester(APIClient, EndpointConfig)
    await tester.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())