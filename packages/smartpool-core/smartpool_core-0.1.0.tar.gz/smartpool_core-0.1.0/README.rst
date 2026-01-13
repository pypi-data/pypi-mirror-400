smartpool
=========

Auto-selecting thread/process pool utilities for parameterized tasks.

- English: README.md
- 简体中文: README_zh.md

Features
--------

- Unified interface for thread/process pools
- ``auto`` mode picks a reasonable executor for the runtime
- Ordered or completion-order results
- Timeout control per task and per run
- Lightweight stats collection via ``RunStats``
- Resource guard with ``max_tasks``
- PEP 561 typing with ``py.typed``

Target users & scope
--------------------

smartpool focuses on lightweight batch execution with a predictable API.

- Best for: IO-heavy tasks, CPU-heavy tasks, short batch jobs
- Not for: distributed scheduling, persistent queues, complex retry pipelines

Installation
------------

.. code-block:: bash

   pip install smartpool

Quickstart
----------

.. code-block:: python

   from smartpool import ThreadUtils

   def work(x: int) -> int:
       return x * 2

   result = ThreadUtils.run_parameterized_task(
       work,
       [1, 2, 3, 4],
       mode="auto",
       ordered=True,
   )
   print(result)

API
---

.. code-block:: python

   ThreadUtils.run_parameterized_task(
       task,
       params,
       *,
       mode="auto",          # auto | cpu | io | thread | process
       max_workers=None,
       thread_name_prefix="default",
       timeout=None,
       timeout_total=None,
       ordered=True,
       result_order=None,    # "input" | "completed"
       chunksize=1,          # meaningful for process + ordered=True
       max_tasks=None,
       return_exceptions=False,
       stats=None,           # RunStats
   )

Behavior notes
--------------

- Process pools require ``task`` to be a top-level function and parameters to be pickle-able.
- With ``ordered=True``, process pool uses ``map``; per-item timeout is not available.
- With ``ordered=False``, results are returned by completion order.
- For ordered process pools, enabling timeout/return_exceptions/timeout_total switches to ``submit`` and ignores ``chunksize``.
- ``timeout_total`` enforces a total runtime limit; it may raise ``TimeoutError``.
- When ``return_exceptions=True``, exceptions are returned in the result list.

License
-------

MIT License. See ``LICENSE`` for details.
