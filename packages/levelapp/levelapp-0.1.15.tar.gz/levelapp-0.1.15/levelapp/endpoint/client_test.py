import asyncio
import logging
from levelapp.endpoint.client import APIClient, EndpointConfig
from levelapp.endpoint.schemas import HttpMethod

logging.basicConfig(level=logging.INFO)


async def stress_test():
    config = EndpointConfig(
        name="stress-test",
        base_url="http://127.0.0.1:8000",
        path="chat",
        method=HttpMethod.POST,
        max_parallel_requests=20,
        max_connections=20,
        retry_count=3,
        retry_backoff_max=30,
    )

    async with APIClient(config) as client:

        async def single_call(i: int):
            try:
                response = await client.execute(
                    payload={"message": f"test-{i}"}
                )
                return response.status_code
            except Exception as e:
                return f"ERROR: {type(e).__name__}"

        tasks = [single_call(i) for i in range(100)]
        results = await asyncio.gather(*tasks, return_exceptions=False)

        print("Results summary:")
        from collections import Counter
        print(Counter(results))


if __name__ == "__main__":
    asyncio.run(stress_test())
