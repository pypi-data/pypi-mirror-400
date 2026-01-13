import os
import sys
import sysconfig
import time
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed, TimeoutError as FuturesTimeoutError
from dataclasses import dataclass
from typing import Callable, Iterable, List, Optional, TypeVar, Literal, Union

T = TypeVar("T")
R = TypeVar("R")

Mode = Literal["auto", "cpu", "io", "thread", "process"]
ResultOrder = Literal["input", "completed"]


@dataclass
class RunStats:
    total: int = 0
    success: int = 0
    failed: int = 0
    timeout: int = 0
    duration: float = 0.0
    executor: str = ""


class ExecutorMixIn:

    @classmethod
    def _run_process_pool(
            cls,
            task: Callable[[T], R],
            params_list: List[T],
            *,
            max_workers: int,
            timeout: Optional[float],
            timeout_total: Optional[float],
            ordered: bool,
            chunksize: int,
            return_exceptions: bool,
            stats: Optional[RunStats],
    ) -> List[R]:
        """
        运行参数化任务，使用进程池。

        :param task: 要运行的任务函数。
        :param params_list: 任务参数列表。
        :param max_workers: 最大进程数。
        :param timeout: 每个任务的超时时间（秒）。
        :param ordered: 是否按参数顺序返回结果。
        :param chunksize: 每个进程处理的参数块大小。
        :return: 任务结果列表。
        """
        started = time.monotonic()
        with ProcessPoolExecutor(max_workers=max_workers) as ex:
            if ordered:
                if timeout is None and timeout_total is None and not return_exceptions:
                    # 注意：这里 timeout 无法逐个控制；需要 submit 才能做到
                    results = list(ex.map(task, params_list, chunksize=chunksize))
                    if stats is not None:
                        stats.success += len(results)
                    return results
                futures = [ex.submit(task, p) for p in params_list]
                out: List[R] = []
                for f in futures:
                    out.append(cls._result_or_error(f, timeout, return_exceptions, stats, started, timeout_total))
                return out

            futures = [ex.submit(task, p) for p in params_list]
            out: List[R] = []
            try:
                for f in cls._iter_completed(futures, started, timeout_total):
                    out.append(cls._result_or_error(f, timeout, return_exceptions, stats, started, timeout_total))
                return out
            except FuturesTimeoutError as e:
                if stats is not None:
                    stats.timeout += 1
                    stats.failed += 1
                raise e

    @classmethod
    def _run_thread_pool(
            cls,
            task: Callable[[T], R],
            params_list: List[T],
            *,
            max_workers: int,
            thread_name_prefix: str,
            timeout: Optional[float],
            timeout_total: Optional[float],
            ordered: bool,
            return_exceptions: bool,
            stats: Optional[RunStats],
    ) -> List[R]:
        """
        运行参数化任务，使用线程池。

        :param task: 要运行的任务函数。
        :param params_list: 任务参数列表。
        :param max_workers: 最大线程数。
        :param thread_name_prefix: 线程名称前缀。
        :param timeout: 每个任务的超时时间（秒）。
        :param ordered: 是否按参数顺序返回结果。
        :return: 任务结果列表。
        """
        started = time.monotonic()
        with ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix=thread_name_prefix) as ex:
            futures = [ex.submit(task, p) for p in params_list]
            if ordered:
                out: List[R] = []
                for f in futures:
                    out.append(cls._result_or_error(f, timeout, return_exceptions, stats, started, timeout_total))
                return out

            out = []
            try:
                for f in cls._iter_completed(futures, started, timeout_total):
                    out.append(cls._result_or_error(f, timeout, return_exceptions, stats, started, timeout_total))
                return out
            except FuturesTimeoutError as e:
                if stats is not None:
                    stats.timeout += 1
                    stats.failed += 1
                raise e

    @staticmethod
    def _iter_completed(futures, started: float, timeout_total: Optional[float]):
        if timeout_total is None:
            return as_completed(futures)
        remaining = timeout_total - (time.monotonic() - started)
        if remaining <= 0:
            raise FuturesTimeoutError()
        return as_completed(futures, timeout=remaining)

    @staticmethod
    def _result_or_error(
        future,
        timeout: Optional[float],
        return_exceptions: bool,
        stats: Optional[RunStats],
        started: float,
        timeout_total: Optional[float],
    ):
        try:
            timeout_eff = timeout
            if timeout_total is not None:
                remaining = timeout_total - (time.monotonic() - started)
                if remaining <= 0:
                    raise FuturesTimeoutError()
                if timeout_eff is None or remaining < timeout_eff:
                    timeout_eff = remaining
            result = future.result(timeout=timeout_eff)
            if stats is not None:
                stats.success += 1
            return result
        except FuturesTimeoutError as e:
            if stats is not None:
                stats.timeout += 1
                stats.failed += 1
            if return_exceptions:
                return e
            raise
        except BaseException as e:
            if stats is not None:
                stats.failed += 1
            if return_exceptions:
                return e
            raise


class ThreadUtils(ExecutorMixIn):

    @classmethod
    def run_parameterized_task(
        cls,
        task: Callable[[T], R],
        params: Iterable[T],
        *,
        mode: Mode = "auto",
        max_workers: Optional[int] = None,
        thread_name_prefix: str = "default",
        timeout: Optional[float] = None,
        timeout_total: Optional[float] = None,
        ordered: bool = True,
        result_order: Optional[ResultOrder] = None,
        chunksize: int = 1,  # 仅对 ProcessPoolExecutor 的 map 更有意义
        max_tasks: Optional[int] = None,
        return_exceptions: bool = False,
        stats: Optional[RunStats] = None,
    ) -> List[Union[R, BaseException]]:
        params_list = list(params)
        if not params_list:
            return []
        if max_tasks is not None and len(params_list) > max_tasks:
            raise ValueError(f"params length {len(params_list)} exceeds max_tasks {max_tasks}")
        if result_order is not None:
            ordered = result_order == "input"
        # 根据模式选择 Executor 类
        executor_cls = cls._pick_executor(mode)
        # 若未指定 max_workers，根据 Executor 类默认值
        if max_workers is None:
            max_workers = cls._default_workers(executor_cls)
        if stats is not None:
            stats.total = len(params_list)
            stats.executor = executor_cls.__name__
            stats.success = 0
            stats.failed = 0
            stats.timeout = 0
            stats.duration = 0.0
        started = time.monotonic()
        if executor_cls is ThreadPoolExecutor:
            kwargs = dict(
                task=task,
                params_list=params_list,
                max_workers=max_workers,
                thread_name_prefix=thread_name_prefix,
                timeout=timeout,
                timeout_total=timeout_total,
                ordered=ordered,
                return_exceptions=return_exceptions,
                stats=stats,
            )
            try:
                return cls._run_thread_pool(**kwargs)
            finally:
                if stats is not None:
                    stats.duration = time.monotonic() - started

        elif executor_cls is ProcessPoolExecutor:
            kwargs = dict(
                task=task,
                params_list=params_list,
                max_workers=max_workers,
                timeout=timeout,
                timeout_total=timeout_total,
                ordered=ordered,
                chunksize=chunksize,
                return_exceptions=return_exceptions,
                stats=stats,
            )
            try:
                return cls._run_process_pool(**kwargs)
            finally:
                if stats is not None:
                    stats.duration = time.monotonic() - started
        else:
            raise ValueError(f"Unsupported executor class: {executor_cls}")

    @staticmethod
    def _is_free_threaded_runtime() -> bool:
        """
        True 表示当前解释器是 free-threaded 构建，且 GIL 处于关闭状态（若可检测）。
        兼容：旧版本没有 sys._is_gil_enabled 时，退化为仅判断构建是否支持。
        """
        supports_ft = bool(sysconfig.get_config_var("Py_GIL_DISABLED"))
        gil_enabled_fn = getattr(sys, "_is_gil_enabled", None)
        if callable(gil_enabled_fn):
            return supports_ft and (gil_enabled_fn() is False)
        return supports_ft

    @classmethod
    def _pick_executor(cls, mode: Mode) -> type:
        """根据模式选择合适的 Executor 类。"""
        ft = cls._is_free_threaded_runtime()
        if mode in ("thread", "io"):
            return ThreadPoolExecutor
        if mode == "process":
            return ProcessPoolExecutor
        # auto/cpu：3.13t 无GIL -> thread；否则 -> process
        return ThreadPoolExecutor if ft else ProcessPoolExecutor

    @classmethod
    def _default_workers(cls, executor_cls: type) -> int:
        """根据 Executor 类默认线程数。"""
        cpu = os.cpu_count() or 4
        if executor_cls is ThreadPoolExecutor:
            return min(32, max(4, cpu))
        return cpu


__all__ = ["ExecutorMixIn", "Mode", "ResultOrder", "RunStats", "ThreadUtils"]
