import functools
import time
from collections.abc import Callable
from typing import Any


def timed(func: Callable[..., Any]):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        duration = time.perf_counter() - start
        return result, duration

    return wrapper
