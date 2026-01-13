import asyncio
import time
from collections.abc import Awaitable, Callable
from typing import TypeVar

T = TypeVar("T")


def wait_sync(
    check_fn: Callable[[], T],
    is_done: Callable[[T], bool],
    interval: float = 1.0,
    timeout: float | None = None,
) -> T:
    start = time.time()
    while True:
        result = check_fn()
        if is_done(result):
            return result

        if timeout and (time.time() - start) > timeout:
            raise TimeoutError("Operation timed out")

        time.sleep(interval)


async def wait_async(
    check_fn: Callable[[], Awaitable[T]],
    is_done: Callable[[T], bool],
    interval: float = 1.0,
    timeout: float | None = None,
) -> T:
    start = time.time()
    while True:
        result = await check_fn()
        if is_done(result):
            return result

        if timeout and (time.time() - start) > timeout:
            raise TimeoutError("Operation timed out")

        await asyncio.sleep(interval)
