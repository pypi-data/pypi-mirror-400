"""CSV output utilities for benchmark results."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from cfabric_benchmarks.models.memory import MemoryBenchmarkResult, MemoryMeasurement
from cfabric_benchmarks.models.latency import (
    LatencyBenchmarkResult,
    LatencyStatistics,
    QueryMeasurement,
    SearchQuery,
)
from cfabric_benchmarks.models.progressive import ProgressiveLoadResult, ProgressiveLoadStep


def write_memory_measurements_csv(
    measurements: list[MemoryMeasurement],
    output_path: Path,
) -> None:
    """Write memory measurements to CSV.

    Args:
        measurements: List of memory measurements
        output_path: Path to output CSV file
    """
    rows = []
    for m in measurements:
        rows.append({
            "run_id": m.run_id,
            "corpus": m.corpus,
            "implementation": m.implementation,
            "mode": m.mode,
            "compile_time_s": m.compile_time_s,
            "load_time_s": m.load_time_s,
            "rss_before_mb": m.rss_before_mb,
            "rss_after_mb": m.rss_after_mb,
            "memory_used_mb": m.memory_used_mb,
            "num_workers": m.num_workers,
            "total_rss_mb": m.total_rss_mb,
            "per_worker_rss_mb": m.per_worker_rss_mb,
            "cache_size_mb": m.cache_size_mb,
        })

    df = pd.DataFrame(rows)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)


def write_latency_measurements_csv(
    measurements: list[QueryMeasurement],
    output_path: Path,
) -> None:
    """Write latency measurements to CSV.

    Args:
        measurements: List of query measurements
        output_path: Path to output CSV file
    """
    rows = []
    for m in measurements:
        rows.append({
            "query_id": m.query_id,
            "implementation": m.implementation,
            "run_id": m.run_id,
            "iteration": m.iteration,
            "execution_time_ms": m.execution_time_ms,
            "result_count": m.result_count,
            "success": m.success,
            "error": m.error,
        })

    df = pd.DataFrame(rows)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)


def write_latency_statistics_csv(
    statistics: list[LatencyStatistics],
    output_path: Path,
) -> None:
    """Write latency statistics to CSV.

    Args:
        statistics: List of latency statistics
        output_path: Path to output CSV file
    """
    rows = []
    for s in statistics:
        rows.append({
            "query_id": s.query_id,
            "category": s.category,
            "implementation": s.implementation,
            "mean_ms": s.mean_ms,
            "std_ms": s.std_ms,
            "min_ms": s.min_ms,
            "max_ms": s.max_ms,
            "p50_ms": s.p50_ms,
            "p95_ms": s.p95_ms,
            "p99_ms": s.p99_ms,
            "sample_count": s.sample_count,
            "error_count": s.error_count,
        })

    df = pd.DataFrame(rows)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)


def write_queries_csv(
    queries: list[SearchQuery],
    output_path: Path,
) -> None:
    """Write search patterns to CSV.

    Args:
        queries: List of search queries
        output_path: Path to output CSV file
    """
    rows = []
    for p in queries:
        rows.append({
            "id": p.id,
            "category": p.category,
            "template": p.template,
            "description": p.description,
            "expected_complexity": p.expected_complexity,
            "validated": p.validated,
            "validation_error": p.validation_error,
        })

    df = pd.DataFrame(rows)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)


def write_progressive_steps_csv(
    steps: list[ProgressiveLoadStep],
    output_path: Path,
) -> None:
    """Write progressive loading steps to CSV.

    Args:
        steps: List of progressive load steps
        output_path: Path to output CSV file
    """
    rows = []
    for s in steps:
        rows.append({
            "step": s.step,
            "corpus_added": s.corpus_added,
            "corpora_loaded": ";".join(s.corpora_loaded),
            "implementation": s.implementation,
            "run_id": s.run_id,
            "total_rss_mb": s.total_rss_mb,
            "incremental_rss_mb": s.incremental_rss_mb,
            "cumulative_load_time_s": s.cumulative_load_time_s,
            "step_load_time_s": s.step_load_time_s,
        })

    df = pd.DataFrame(rows)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)


def write_memory_summary_csv(
    results: list[MemoryBenchmarkResult],
    output_path: Path,
) -> None:
    """Write memory benchmark summary to CSV.

    Args:
        results: List of memory benchmark results
        output_path: Path to output CSV file
    """
    rows = []
    for r in results:
        # Single process stats
        if r.tf_memory_stats and r.cf_memory_stats:
            rows.append({
                "corpus": r.corpus,
                "mode": "single",
                "tf_memory_mean_mb": r.tf_memory_stats.mean,
                "tf_memory_std_mb": r.tf_memory_stats.std,
                "cf_memory_mean_mb": r.cf_memory_stats.mean,
                "cf_memory_std_mb": r.cf_memory_stats.std,
                "reduction_percent": (
                    (r.tf_memory_stats.mean - r.cf_memory_stats.mean)
                    / r.tf_memory_stats.mean
                    * 100
                    if r.tf_memory_stats.mean > 0
                    else 0
                ),
            })

        # Load time stats
        if r.tf_load_time_stats and r.cf_load_time_stats:
            rows.append({
                "corpus": r.corpus,
                "mode": "load_time",
                "tf_memory_mean_mb": r.tf_load_time_stats.mean,
                "tf_memory_std_mb": r.tf_load_time_stats.std,
                "cf_memory_mean_mb": r.cf_load_time_stats.mean,
                "cf_memory_std_mb": r.cf_load_time_stats.std,
                "reduction_percent": None,  # Not applicable for time
            })

    df = pd.DataFrame(rows)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)


def write_comparison_csv(
    comparisons: list[dict],
    output_path: Path,
) -> None:
    """Write comparison results to CSV.

    Args:
        comparisons: List of comparison dictionaries
        output_path: Path to output CSV file
    """
    df = pd.DataFrame(comparisons)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)


def write_cross_corpus_summary_csv(
    results: list[MemoryBenchmarkResult],
    output_path: Path,
) -> None:
    """Write cross-corpus aggregate statistics to CSV.

    Computes mean/std/CI of reduction percentages across all corpora.

    Args:
        results: List of memory benchmark results (one per corpus)
        output_path: Path to output CSV file
    """
    import numpy as np
    from scipy import stats

    rows = []

    for mode in ["single", "spawn", "fork"]:
        reductions = []
        speedups = []

        for r in results:
            if mode == "single":
                tf_stats = r.tf_memory_stats
                cf_stats = r.cf_memory_stats
                tf_time = r.tf_load_time_stats
                cf_time = r.cf_load_time_stats
            elif mode == "spawn":
                tf_stats = r.tf_spawn_stats
                cf_stats = r.cf_spawn_stats
                tf_time = cf_time = None
            else:  # fork
                tf_stats = r.tf_fork_stats
                cf_stats = r.cf_fork_stats
                tf_time = cf_time = None

            if tf_stats and cf_stats and tf_stats.mean > 0:
                reduction = (tf_stats.mean - cf_stats.mean) / tf_stats.mean * 100
                reductions.append(reduction)

            if tf_time and cf_time and cf_time.mean > 0:
                speedup = tf_time.mean / cf_time.mean
                speedups.append(speedup)

        if reductions:
            arr = np.array(reductions)
            n = len(arr)
            mean = float(np.mean(arr))
            std = float(np.std(arr, ddof=1)) if n > 1 else 0.0

            # 95% CI
            if n > 1:
                sem = std / np.sqrt(n)
                t_val = stats.t.ppf(0.975, df=n - 1)
                ci_lower = mean - t_val * sem
                ci_upper = mean + t_val * sem
            else:
                ci_lower = ci_upper = mean

            rows.append({
                "metric": f"memory_reduction_{mode}",
                "unit": "%",
                "n_corpora": n,
                "mean": mean,
                "std": std,
                "ci_lower_95": ci_lower,
                "ci_upper_95": ci_upper,
                "min": float(np.min(arr)),
                "max": float(np.max(arr)),
            })

        if speedups:
            arr = np.array(speedups)
            n = len(arr)
            mean = float(np.mean(arr))
            std = float(np.std(arr, ddof=1)) if n > 1 else 0.0

            if n > 1:
                sem = std / np.sqrt(n)
                t_val = stats.t.ppf(0.975, df=n - 1)
                ci_lower = mean - t_val * sem
                ci_upper = mean + t_val * sem
            else:
                ci_lower = ci_upper = mean

            rows.append({
                "metric": "load_time_speedup",
                "unit": "x",
                "n_corpora": n,
                "mean": mean,
                "std": std,
                "ci_lower_95": ci_lower,
                "ci_upper_95": ci_upper,
                "min": float(np.min(arr)),
                "max": float(np.max(arr)),
            })

    df = pd.DataFrame(rows)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
