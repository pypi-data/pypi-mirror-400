"""Subprocess isolation utilities for clean memory measurement.

This module provides utilities for running benchmark measurements in isolated
subprocesses to avoid memory pollution from prior allocations.
"""

from __future__ import annotations

import gc
import multiprocessing as mp
import os
import time
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal, TypeVar

import psutil


T = TypeVar("T")


def _isolated_worker(
    queue: "mp.Queue[IsolatedResult]",
    fn: Callable,
    fn_args: tuple,
    fn_kwargs: dict,
) -> None:
    """Worker function that executes in isolated subprocess.

    Must be at module level to be picklable for spawn context.
    """
    start_time = time.perf_counter()
    try:
        result = fn(*fn_args, **fn_kwargs)

        # Force garbage collection before memory measurement
        gc.collect()
        memory = get_memory_mb()

        execution_time = time.perf_counter() - start_time
        queue.put(
            IsolatedResult(
                success=True,
                result=result,
                memory_mb=memory,
                execution_time_s=execution_time,
            )
        )
    except Exception as e:
        execution_time = time.perf_counter() - start_time
        queue.put(
            IsolatedResult(
                success=False,
                error=str(e),
                execution_time_s=execution_time,
            )
        )

    # Keep process alive briefly for external memory measurement
    time.sleep(1)


@dataclass
class IsolatedResult:
    """Result from an isolated subprocess execution."""

    success: bool
    result: Any | None = None
    error: str | None = None
    memory_mb: float = 0.0
    execution_time_s: float = 0.0


def get_memory_mb(pid: int | None = None) -> float:
    """Get process memory usage in MB (RSS).

    Args:
        pid: Process ID to measure. If None, uses current process.

    Returns:
        Memory usage in megabytes (RSS - Resident Set Size)
    """
    try:
        proc = psutil.Process(pid or os.getpid())
        return proc.memory_info().rss / 1024 / 1024
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return 0.0


def get_total_memory_mb(pids: list[int]) -> float:
    """Get total memory usage across multiple processes in MB (RSS).

    Args:
        pids: List of process IDs to measure

    Returns:
        Total memory usage in megabytes
    """
    total = 0.0
    for pid in pids:
        total += get_memory_mb(pid)
    return total


def get_dir_size_mb(path: Path) -> float:
    """Get total size of directory in MB.

    Args:
        path: Path to directory

    Returns:
        Total size in megabytes
    """
    if not path.exists():
        return 0.0
    total = sum(f.stat().st_size for f in path.rglob("*") if f.is_file())
    return total / 1024 / 1024


def run_isolated(
    func: Callable[..., T],
    args: tuple = (),
    kwargs: dict | None = None,
    timeout: float = 300.0,
    context: Literal["spawn", "fork"] = "spawn",
) -> IsolatedResult:
    """Run a function in an isolated subprocess.

    This ensures clean memory measurement by running in a fresh process
    that doesn't have any prior allocations.

    Args:
        func: Function to execute (must be picklable)
        args: Positional arguments for the function
        kwargs: Keyword arguments for the function
        timeout: Maximum time to wait for result in seconds
        context: Multiprocessing context ('spawn' for clean memory, 'fork' for COW)

    Returns:
        IsolatedResult with success status, result, and memory measurement
    """
    kwargs = kwargs or {}

    ctx = mp.get_context(context)
    result_queue: mp.Queue = ctx.Queue()

    process = ctx.Process(
        target=_isolated_worker, args=(result_queue, func, args, kwargs)
    )
    process.start()

    try:
        result = result_queue.get(timeout=timeout)
    except Exception as e:
        result = IsolatedResult(success=False, error=f"Timeout or error: {e}")

    # Clean up process
    process.join(timeout=5)
    if process.is_alive():
        process.terminate()
        process.join(timeout=2)

    return result


class WorkerPool:
    """Manager for parallel worker processes.

    Handles spawning, synchronization, and memory measurement
    for multiple worker processes.
    """

    def __init__(
        self,
        num_workers: int,
        context: Literal["spawn", "fork"] = "spawn",
    ):
        """Initialize worker pool.

        Args:
            num_workers: Number of worker processes
            context: Multiprocessing context to use
        """
        self.num_workers = num_workers
        self.context = context
        self._ctx = mp.get_context(context)
        self._processes: list[mp.Process] = []
        self._ready_events: list[mp.Event] = []
        self._start_event: mp.Event | None = None
        self._result_queue: mp.Queue | None = None

    def start_workers(
        self,
        worker_fn: Callable,
        worker_args: tuple = (),
        worker_kwargs: dict | None = None,
    ) -> None:
        """Start worker processes.

        Args:
            worker_fn: Function for each worker to execute
            worker_args: Arguments for worker function
            worker_kwargs: Keyword arguments for worker function
        """
        worker_kwargs = worker_kwargs or {}

        self._ready_events = [self._ctx.Event() for _ in range(self.num_workers)]
        self._start_event = self._ctx.Event()
        self._result_queue = self._ctx.Queue()

        for i in range(self.num_workers):
            p = self._ctx.Process(
                target=worker_fn,
                args=(
                    self._ready_events[i],
                    self._start_event,
                    self._result_queue,
                    *worker_args,
                ),
                kwargs=worker_kwargs,
            )
            p.start()
            self._processes.append(p)

    def wait_for_ready(self, timeout: float = 300.0) -> bool:
        """Wait for all workers to signal ready.

        Args:
            timeout: Maximum time to wait in seconds

        Returns:
            True if all workers ready, False if timeout
        """
        for evt in self._ready_events:
            if not evt.wait(timeout=timeout):
                return False
        return True

    def signal_start(self) -> None:
        """Signal all workers to proceed."""
        if self._start_event:
            self._start_event.set()

    def get_results(self, timeout: float = 120.0) -> list[Any]:
        """Collect results from all workers.

        Args:
            timeout: Maximum time to wait for each result

        Returns:
            List of results from workers
        """
        results = []
        if self._result_queue:
            for _ in range(self.num_workers):
                try:
                    results.append(self._result_queue.get(timeout=timeout))
                except Exception:
                    pass
        return results

    def get_total_memory_mb(self) -> float:
        """Get total memory usage across all workers."""
        pids = [p.pid for p in self._processes if p.pid is not None]
        return get_total_memory_mb(pids)

    def get_pids(self) -> list[int]:
        """Get list of worker process IDs."""
        return [p.pid for p in self._processes if p.pid is not None]

    def shutdown(self, timeout: float = 10.0) -> None:
        """Shutdown all worker processes.

        Args:
            timeout: Maximum time to wait for graceful shutdown
        """
        for p in self._processes:
            p.join(timeout=timeout / len(self._processes) if self._processes else timeout)
            if p.is_alive():
                p.terminate()
                p.join(timeout=2)

        self._processes = []
        self._ready_events = []
        self._start_event = None
        self._result_queue = None

    def __enter__(self) -> "WorkerPool":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.shutdown()


def measure_memory_in_subprocess(
    load_fn: Callable[[], Any],
    timeout: float = 300.0,
) -> tuple[float, float, Any]:
    """Measure memory usage of a loading function in an isolated subprocess.

    Args:
        load_fn: Function that loads something and returns it
        timeout: Maximum time to wait

    Returns:
        Tuple of (memory_mb, load_time_s, result)
    """
    result = run_isolated(load_fn, timeout=timeout)
    return (
        result.memory_mb,
        result.execution_time_s,
        result.result if result.success else None,
    )
