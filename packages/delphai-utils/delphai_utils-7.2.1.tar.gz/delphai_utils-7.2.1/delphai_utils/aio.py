import asyncio
import concurrent.futures
import functools
import threading

thread_local = threading.local()
default_executor = concurrent.futures.ThreadPoolExecutor(
    thread_name_prefix=f"{__package__}:executor"
)


def run_in_executor(func=None, *, context=None, executor=None):
    """
    Decorator to run synchronous function in the given or default executor

    Optionally within the given async context manager (e.g. to limit concurrency
    with `asyncio.Lock` or `asyncio.Semaphore`)
    """
    if executor is None:
        executor = default_executor

    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            loop = asyncio.get_running_loop()

            # Use dummy Lock() as contextlib.nullcontext for older python versions
            current_context = context or asyncio.Lock()

            stop_event = threading.Event()

            def entrypoint():
                thread_local.stop_event = stop_event
                return func(*args, **kwargs)

            async with current_context:
                try:
                    return await loop.run_in_executor(executor, entrypoint)
                finally:
                    stop_event.set()

        return wrapper

    return decorator(func) if func else decorator


def maybe_cancel():
    """
    Checks if the current function (running with `run_in_executor`) was cancelled.
    If so, raises `asyncio.CancelledError` and stop execution.
    The exception will be ignored, so there's no need to catch it.
    """
    stop_event = getattr(thread_local, "stop_event", None)

    if stop_event and stop_event.is_set():
        raise asyncio.CancelledError


run_in_executor_locked = functools.partial(run_in_executor, context=asyncio.Lock())
