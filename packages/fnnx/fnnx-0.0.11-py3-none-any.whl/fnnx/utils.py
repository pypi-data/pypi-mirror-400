from asyncio import events
import functools
import contextvars
import sys


async def to_thread(executor, func, /, *args, **kwargs):
    loop = events.get_running_loop()
    ctx = contextvars.copy_context()
    func_call = functools.partial(ctx.run, func, *args, **kwargs)
    return await loop.run_in_executor(executor, func_call)


def get_python_version(micro: bool = True) -> str:
    if micro:
        return f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    return f"{sys.version_info.major}.{sys.version_info.minor}"
