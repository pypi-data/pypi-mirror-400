"""Async usage example for tlshttp."""

import asyncio
import time

import tlshttp


async def main():
    print("Testing AsyncClient...")

    # Basic async request
    async with tlshttp.AsyncClient(profile="chrome_120") as client:
        response = await client.get("https://httpbin.org/get")
        print(f"Status: {response.status_code}")
        print(f"Origin: {response.json()['origin']}")

    # Concurrent requests
    print("\nMaking concurrent requests...")
    async with tlshttp.AsyncClient() as client:
        start = time.time()

        # Create 5 concurrent requests
        urls = [f"https://httpbin.org/delay/1?id={i}" for i in range(5)]
        tasks = [client.get(url) for url in urls]
        responses = await asyncio.gather(*tasks)

        elapsed = time.time() - start
        print(f"Made 5 requests with 1s delay each in {elapsed:.2f}s")
        print(f"Status codes: {[r.status_code for r in responses]}")

    # Error handling
    print("\nTesting error handling...")
    async with tlshttp.AsyncClient(timeout=5.0) as client:
        try:
            response = await client.get("https://httpbin.org/status/404")
            response.raise_for_status()
        except tlshttp.HTTPStatusError as e:
            print(f"Caught HTTP error: {e.response.status_code}")


if __name__ == "__main__":
    asyncio.run(main())
