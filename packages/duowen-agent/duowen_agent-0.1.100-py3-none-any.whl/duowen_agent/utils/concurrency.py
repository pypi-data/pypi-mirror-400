import functools
import logging
import typing
from threading import Thread
from typing import ParamSpec, Union, List

import anyio.to_thread

P = ParamSpec("P")
T = typing.TypeVar("T")
from multiprocessing.pool import ThreadPool


def concurrent_execute(
    fn, data: Union[List[dict], List[str], List[tuple], List[list]], work_num=4
):
    def process_item(item):
        if isinstance(item, dict):
            return fn(**item)
        elif isinstance(item, tuple):
            return fn(*item)
        elif isinstance(item, list):
            return fn(*item)
        elif isinstance(item, (str, int, float, bool)):
            return fn(item)
        else:
            raise ValueError(f"Unsupported data type: {type(item)}")

    logging.debug(
        f"thread concurrent_execute,work_num:{work_num} fn:{fn.__name__} data: {repr(data)}"
    )

    with ThreadPool(work_num) as pool:
        results = pool.map(process_item, data)

    return results


def run_in_thread(fn):
    """
    @run_in_thread
    def test(abc):
        return abc

    test(123)
    """

    def wrapper(*k, **kw):
        t = Thread(target=fn, args=k, kwargs=kw)
        t.start()
        return t

    return wrapper


async def make_async(
    func: typing.Callable[P, T], *args: P.args, **kwargs: P.kwargs
) -> T:
    """
    Use it like this:

    ```Python
    def do_work(arg1, arg2, kwarg1="", kwarg2="") -> str:
            # Do work
            return "Some result"

    result = await make_async(do_work, "spam", "ham", kwarg1="a", kwarg2="b")
    print(result)
    ```

    """
    if kwargs:  # pragma: no cover
        # run_sync doesn't accept 'kwargs', so bind them in here
        func = functools.partial(func, **kwargs)
    return await anyio.to_thread.run_sync(func, *args)


class ProgressBar:
    def __init__(self, total: int, bar_length: int = 50, message: str = ""):
        self.total = total
        self.current = 0
        self.bar_length = bar_length  # 进度条的字符长度
        self.message = message

    def increment(self, step: int = 1):
        self.current = min(self.current + step, self.total)  # 避免超过总数

    def log_msg(self):
        if self.total == 0:
            return  # 避免除零错误

            # 计算进度百分比
        progress = self.current / self.total
        percentage = progress * 100

        # 计算进度条显示的字符数
        filled_length = int(self.bar_length * progress)
        bar = "#" * filled_length + "-" * (self.bar_length - filled_length)

        # 使用 \r 回到行首，覆盖原有内容；end='' 避免自动换行；flush=True 强制刷新输出
        return f"{self.message} [{bar}] {percentage:.2f}% ({self.current}/{self.total})"

    def show(self):
        _show = self.log_msg()

        # 使用 \r 回到行首，覆盖原有内容；end='' 避免自动换行；flush=True 强制刷新输出
        print(
            f"\r{_show}",
            end="",
            flush=True,
        )

        # 当进度完成时，手动换行，避免后续输出和进度条在同一行
        if self.current == self.total:
            print()  # 完成后换行


if __name__ == "__main__":
    import time

    p = ProgressBar(total=100, message="进度条")
    for i in range(100):
        p.increment()
        time.sleep(0.1)
        print(p.log_msg())

    print("=" * 100)

    p = ProgressBar(total=100, message="进度条")
    for i in range(100):
        p.increment()
        time.sleep(0.1)
        p.show()
