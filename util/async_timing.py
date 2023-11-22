import asyncio
import functools
import time
from typing import Callable, Any, TypeVar, Coroutine

async def delay(delay_seconds: int) -> int:
    print(f'sleeping for {delay_seconds} seconds')
    await asyncio.sleep(delay_seconds)
    print(f'finished sleedping for {delay_seconds} seconds')
    return delay_seconds
    
T = TypeVar('T')

def async_timed():
    def wrapper(func: Callable[..., Coroutine[Any, Any, T]]) -> Callable[..., Coroutine[Any, Any, T]]:
        @functools.wraps(func)
        async def wrapped(*args: Any, **kwargs: Any) -> Any:
            print(f'starting {func} with args {args} {kwargs}')
            start  = time.time()
            try:
                return await func(*args, **kwargs)
            finally:
                end = time.time()
                total = end - start
                print(f'finished {func} in {total:.4f} seconds')
        return wrapped
    return wrapper