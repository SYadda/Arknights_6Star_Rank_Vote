import asyncio
import time
from typing import Any

import aiohttp

BASE_URL = "http://127.0.0.1:8080"
CONCURRENCY = 1000
TOTAL_REQUESTS = 100000

HEADERS = {"Content-Type": "application/json"}
REQUEST_TIMEOUT = 10
SYSTEM_MAX_CONNECTIONS = 5000
new_compare_data = {"code": "000"}


class ErrorCounter:
    def __init__(self):
        self.count = 0
        self.lock = asyncio.Lock()

    async def increment(self):
        async with self.lock:
            self.count += 1


error_counter = ErrorCounter()


async def call_new_compare(session: aiohttp.ClientSession) -> dict[str, Any]:
    url = f"{BASE_URL}/new_compare"
    try:
        async with session.post(url, headers=HEADERS, json=new_compare_data) as response:
            if response.status != 200:
                await error_counter.increment()
                return {}
            return await response.json()
    except Exception as e:
        await error_counter.increment()
        return {}


async def call_save_score(session: aiohttp.ClientSession, data: dict[str, Any]) -> None:
    url = f"{BASE_URL}/save_score"
    try:
        async with session.post(url, json=data, headers=HEADERS) as response:
            if response.status != 200:
                await error_counter.increment()
    except Exception as e:
        await error_counter.increment()


async def worker(session: aiohttp.ClientSession, sem: asyncio.Semaphore):
    async with sem:
        start_time = time.monotonic()

        compare_result = await call_new_compare(session)
        if not compare_result:
            return

        if not all([compare_result.get("left"), compare_result.get("right"), compare_result.get("code")]):
            await error_counter.increment()
            return

        save_data = {
            "win_id": compare_result["left"],
            "lose_id": compare_result["right"],
            "code": compare_result["code"],
        }

        await call_save_score(session, save_data)

        latency = (time.monotonic() - start_time) * 1000
        if latency > 1000:
            pass


async def main():
    connector = aiohttp.TCPConnector(limit=SYSTEM_MAX_CONNECTIONS, force_close=True, enable_cleanup_closed=True)

    async with aiohttp.ClientSession(
        connector=connector, timeout=aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)
    ) as session:
        sem = asyncio.Semaphore(CONCURRENCY)
        tasks = [worker(session, sem) for _ in range(TOTAL_REQUESTS)]

        start_time = time.perf_counter()
        await asyncio.gather(*tasks)
        total_time = time.perf_counter() - start_time

    qps = TOTAL_REQUESTS / total_time
    error_rate = (error_counter.count / TOTAL_REQUESTS) * 100

    print(f"\n{' Benchmark Results ':=^40}")
    print(f"Total Requests: {TOTAL_REQUESTS}")
    print(f"Total Time: {total_time:.2f}s")
    print(f"QPS: {qps:.2f}")
    print(f"Errors: {error_counter.count}")
    print(f"Error Rate: {error_rate:.2f}%")
    print("=" * 40)


if __name__ == "__main__":
    try:
        import uvloop

        uvloop.install()
        print("Using uvloop for better performance")
    except ImportError:
        print("Using standard asyncio event loop")

    asyncio.run(main())
