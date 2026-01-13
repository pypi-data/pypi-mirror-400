from concurrent.futures import ThreadPoolExecutor, Future
from typing import Callable, Any


class BackgroundTask:
    def __init__(self, max_workers: int = 1):
        self.executor = ThreadPoolExecutor(max_workers=max_workers)

    def run(self, func: Callable, *args: Any, **kwargs: Any) -> Future:
        future = self.executor.submit(func, *args, **kwargs)
        return future
