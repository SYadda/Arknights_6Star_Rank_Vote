import asyncio
import aiohttp
import random
import time
from typing import Any, Dict

BASE_URL = "http://127.0.0.1:8080"
CONCURRENCY = 1000
TEST_TIMES = 10

HEADERS = {
    "Content-Type": "application/json",
}

error_count = 0


async def call_new_compare(session: aiohttp.ClientSession) -> Dict[str, Any]:
    url = f"{BASE_URL}/new_compare"
    async with session.post(url, headers=HEADERS) as response:
        if response.status != 200:
            print(f"Error calling /new_compare: {response.status}")
            global error_count
            error_count += 1
            return {}
        return await response.json()


async def call_save_score(session: aiohttp.ClientSession, data: Dict[str, Any]) -> None:
    url = f"{BASE_URL}/save_score"
    async with session.post(url, json=data, headers=HEADERS) as response:
        if response.status != 200:
            print(f"Error calling /save_score: {response.status}")
            global error_count
            error_count += 1


async def test_qps(session: aiohttp.ClientSession):
    """单次测试 QPS 的任务"""
    try:
        compare_result = await call_new_compare(session)
        if not compare_result:
            return

        left = compare_result.get("left")
        right = compare_result.get("right")
        code = compare_result.get("code")

        if not all([left, right, code]):
            print("Invalid response from /new_compare")
            return

        win_id, lose_id = (left, right) if random.random() > 0.5 else (right, left)
        save_score_data = {
            "win_id": win_id,
            "lose_id": lose_id,
            "code": code,
        }

        await call_save_score(session, save_score_data)

    except Exception as e:
        print(f"Exception in test_qps: {e}")


async def main():
    global error_count
    total_requests = 0
    start_time = time.time()

    async with aiohttp.ClientSession() as session:
        for _ in range(TEST_TIMES):
            tasks = [test_qps(session) for _ in range(CONCURRENCY)]
            await asyncio.gather(*tasks)

            total_requests += CONCURRENCY
            elapsed_time = time.time() - start_time
            qps = total_requests / elapsed_time

            print(
                f"Elapsed: {elapsed_time:.2f}s | Total Requests: {total_requests} | QPS: {qps:.2f} | Errors: {error_count}"
            )


if __name__ == "__main__":
    asyncio.run(main())