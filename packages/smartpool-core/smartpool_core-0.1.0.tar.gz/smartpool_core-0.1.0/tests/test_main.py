# -*- coding: utf-8 -*-
import logging
import os
import sys
import time
import traceback
from dataclasses import dataclass
from typing import Any, Callable, List

from smartpool import ThreadUtils  # 你的工具类


# -------------------------
# 日志（中文输出）
# -------------------------
def setup_logger() -> logging.Logger:
    logger = logging.getLogger("ThreadUtils测试")
    logger.setLevel(logging.INFO)
    logger.propagate = False

    if logger.handlers:
        return logger

    fmt = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    h = logging.StreamHandler(sys.stdout)
    h.setFormatter(fmt)
    logger.addHandler(h)
    return logger


log = setup_logger()


def now() -> float:
    return time.perf_counter()


def fmt_time(sec: float) -> str:
    return f"{sec*1000:.1f} 毫秒" if sec < 1 else f"{sec:.3f} 秒"


def line(ch: str = "─", n: int = 72) -> str:
    return ch * n


def print_title(text: str) -> None:
    log.info(line("═"))
    log.info(" %s", text)
    log.info(line("═"))


def print_section(text: str) -> None:
    log.info(line("─"))
    log.info(" %s", text)
    log.info(line("─"))


def OK(msg: str) -> None:
    log.info("✅ %s", msg)


def WARN(msg: str) -> None:
    log.warning("⚠️  %s", msg)


def FAIL(msg: str) -> None:
    log.error("❌ %s", msg)


def INFO(msg: str) -> None:
    log.info("ℹ️  %s", msg)


# -------------------------
# 任务函数（进程池必须是“顶层函数”，不能 lambda/闭包/局部函数）
# -------------------------
def 平方(x: int) -> int:
    return x * x


def 睡眠(x: float) -> float:
    time.sleep(x)
    return x


def CPU密集(x: int) -> int:
    s = 0
    for i in range(3_000_00):
        s += (i * (x + 1)) % 97
    return s


@dataclass
class CaseResult:
    名称: str
    是否通过: bool
    耗时: float
    详情: str = ""


def run_case(name: str, fn: Callable[[], Any]) -> CaseResult:
    t0 = now()
    try:
        detail = fn()
        return CaseResult(name, True, now() - t0, str(detail) if detail is not None else "")
    except Exception as e:
        tb = traceback.format_exc(limit=2)
        return CaseResult(name, False, now() - t0, f"{type(e).__name__}: {e}\n{tb}")


def assert_equal(got: Any, expected: Any) -> None:
    if got != expected:
        raise AssertionError(f"实际={got}，期望={expected}")


# -------------------------
# 用例定义
# -------------------------
def case_线程池_顺序():
    params = [1, 2, 3, 4, 5]
    got = ThreadUtils.run_parameterized_task(平方, params, mode="thread", max_workers=4, ordered=True)
    assert_equal(got, [1, 4, 9, 16, 25])
    return f"输出={got}"


def case_线程池_完成顺序():
    params = [0.2, 0.0, 0.1]
    got = ThreadUtils.run_parameterized_task(睡眠, params, mode="thread", max_workers=3, ordered=False)
    assert_equal(sorted(got), sorted(params))
    return f"输出={got}（按完成顺序返回）"


def case_进程池_顺序():
    params = [1, 2, 3, 4, 5]
    got = ThreadUtils.run_parameterized_task(平方, params, mode="process", max_workers=4, ordered=True)
    assert_equal(got, [1, 4, 9, 16, 25])
    return f"输出={got}"


def case_auto_选择执行器():
    ex = ThreadUtils._pick_executor("auto")
    return f"auto 选择：{ex}"


def bench_cpu(mode: str) -> float:
    params = list(range(12))
    t0 = now()
    ThreadUtils.run_parameterized_task(CPU密集, params, mode=mode, max_workers=12, ordered=True)
    return now() - t0


def case_timeout_应抛出():
    ThreadUtils.run_parameterized_task(睡眠, [0.5, 0.5, 0.5], mode="thread", max_workers=3, timeout=0.1)
    return "未超时（不符合预期）"


# -------------------------
# 主流程
# -------------------------
def main():
    print_title("ThreadUtils 测试套件（中文日志 / 更清晰）")

    INFO(f"Python：{sys.version.splitlines()[0]}")
    INFO(f"CPU 核心数：{os.cpu_count()}")

    # 1) 正确性
    print_section("1) 正确性：ordered / unordered")

    correctness_cases = [
        ("线程池 ordered=True：按入参顺序返回", case_线程池_顺序),
        ("线程池 ordered=False：按完成顺序返回", case_线程池_完成顺序),
        ("进程池 ordered=True：按入参顺序返回", case_进程池_顺序),
    ]

    results: List[CaseResult] = []
    for name, fn in correctness_cases:
        r = run_case(name, fn)
        results.append(r)
        if r.是否通过:
            OK(f"{r.名称}（耗时 {fmt_time(r.耗时)}） {r.详情}")
        else:
            FAIL(f"{r.名称}（耗时 {fmt_time(r.耗时)}）\n{r.详情}")

    # 2) auto 选择
    print_section("2) auto 选择展示")
    r = run_case("auto 选择执行器", case_auto_选择执行器)
    if r.是否通过:
        OK(f"{r.名称}（耗时 {fmt_time(r.耗时)}） {r.详情}")
    else:
        FAIL(f"{r.名称}（耗时 {fmt_time(r.耗时)}）\n{r.详情}")

    # 3) 性能冒烟
    print_section("3) 性能冒烟（CPU密集：线程 vs 进程）")
    t_thread = bench_cpu("thread")
    t_process = bench_cpu("process")

    INFO(f"CPU密集(thread)  耗时：{fmt_time(t_thread)}")
    INFO(f"CPU密集(process) 耗时：{fmt_time(t_process)}")

    if t_process > 0:
        ratio = t_thread / t_process
        if ratio > 1:
            OK(f"进程池更快：约 {ratio:.2f}x（thread/process）")
        else:
            OK(f"线程池更快：约 {1/ratio:.2f}x（process/thread）")

    # 4) timeout
    print_section("4) timeout 行为（预期抛 TimeoutError）")
    r = run_case("线程池 timeout：应抛 TimeoutError", case_timeout_应抛出)
    if r.是否通过:
        WARN(f"{r.名称}（耗时 {fmt_time(r.耗时)}） {r.详情}")
    else:
        if "TimeoutError" in r.详情:
            OK(f"{r.名称}（耗时 {fmt_time(r.耗时)}）已抛 TimeoutError（符合预期）")
        else:
            FAIL(f"{r.名称}（耗时 {fmt_time(r.耗时)}）\n{r.详情}")

    # 总结
    print_title("总结")
    passed = sum(1 for x in results if x.是否通过)
    total = len(results)
    INFO(f"正确性用例通过：{passed}/{total}")
    INFO("提示：进程池要求 task 是顶层函数（不能 lambda/闭包/局部函数）。")
    log.info(line("═"))


if __name__ == "__main__":
    main()
