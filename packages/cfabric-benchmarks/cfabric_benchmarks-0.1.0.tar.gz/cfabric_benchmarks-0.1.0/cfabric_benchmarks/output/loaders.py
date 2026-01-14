"""Load benchmark results from saved files."""
from __future__ import annotations

import csv
import json
from pathlib import Path

import numpy as np

from cfabric_benchmarks.models.latency import (
    LatencyBenchmarkResult,
    QueryMeasurement,
    SearchQuery,
)
from cfabric_benchmarks.models.memory import CorpusStats, MemoryBenchmarkResult
from cfabric_benchmarks.models.progressive import ProgressiveLoadResult
from cfabric_benchmarks.models.statistics import StatisticalSummary


def _make_memory_stats(mean: float) -> StatisticalSummary:
    """Create a minimal StatisticalSummary with just the mean value."""
    return StatisticalSummary(
        metric_name="memory",
        unit="MB",
        mean=mean,
        median=mean,
        std=0,
        variance=0,
        min=mean,
        max=mean,
        range=0,
        n=1,
        ci_lower=mean,
        ci_upper=mean,
        p25=mean,
        p50=mean,
        p75=mean,
        p90=mean,
        p95=mean,
        p99=mean,
    )


def load_memory_results(results_dir: Path) -> list[MemoryBenchmarkResult]:
    """Load memory results from summary.csv.

    Args:
        results_dir: Directory containing benchmark results

    Returns:
        List of MemoryBenchmarkResult objects (minimal, for multi-corpus chart)
    """
    summary_path = results_dir / "memory/summary.csv"
    if not summary_path.exists():
        return []

    corpus_data: dict[str, dict] = {}
    with open(summary_path) as f:
        for row in csv.DictReader(f):
            if row["mode"] != "single":
                continue
            corpus = row["corpus"]
            corpus_data[corpus] = {
                "tf_mean": float(row["tf_memory_mean_mb"]),
                "cf_mean": float(row["cf_memory_mean_mb"]),
            }

    results = []
    for corpus, data in corpus_data.items():
        results.append(
            MemoryBenchmarkResult(
                corpus=corpus,
                corpus_stats=CorpusStats(
                    name=corpus,
                    max_slot=0,
                    max_node=0,
                    node_types=0,
                    node_features=0,
                    edge_features=0,
                ),
                measurements=[],
                tf_memory_stats=_make_memory_stats(data["tf_mean"]),
                cf_memory_stats=_make_memory_stats(data["cf_mean"]),
            )
        )
    return results


def load_progressive_result(results_dir: Path) -> ProgressiveLoadResult | None:
    """Load progressive results from CSV and JSON files.

    Args:
        results_dir: Directory containing benchmark results

    Returns:
        ProgressiveLoadResult or None if not found
    """
    from cfabric_benchmarks.models.progressive import (
        ProgressiveLoadStep,
        ScalingAnalysis,
    )

    steps_path = results_dir / "progressive/raw_steps.csv"
    scaling_path = results_dir / "progressive/scaling_analysis.json"

    if not steps_path.exists():
        return None

    # Load steps from CSV
    steps = []
    with open(steps_path) as f:
        for row in csv.DictReader(f):
            corpora_loaded = row["corpora_loaded"].split(";")
            steps.append(
                ProgressiveLoadStep(
                    step=int(row["step"]),
                    corpus_added=row["corpus_added"],
                    corpora_loaded=corpora_loaded,
                    implementation=row["implementation"],
                    run_id=int(row["run_id"]),
                    total_rss_mb=float(row["total_rss_mb"]),
                    incremental_rss_mb=float(row["incremental_rss_mb"]),
                    cumulative_load_time_s=float(row["cumulative_load_time_s"]),
                    step_load_time_s=float(row["step_load_time_s"]),
                )
            )

    if not steps:
        return None

    # Determine corpora order and max from steps
    tf_steps_run1 = [s for s in steps if s.implementation == "TF" and s.run_id == 1]
    tf_steps_run1.sort(key=lambda s: s.step)
    corpora_order = [s.corpus_added for s in tf_steps_run1]
    max_corpora = len(corpora_order)

    # Get unique run IDs
    run_ids = sorted(set(s.run_id for s in steps))
    num_runs = len(run_ids)

    # Calculate average memory by step
    def calc_avg_memory(impl: str) -> list[float]:
        impl_steps = [s for s in steps if s.implementation == impl]
        avg_by_step = []
        for step_num in range(1, max_corpora + 1):
            step_memories = [s.total_rss_mb for s in impl_steps if s.step == step_num]
            if step_memories:
                avg_by_step.append(float(np.mean(step_memories)))
        return avg_by_step

    tf_memory_by_step = calc_avg_memory("TF")
    cf_memory_by_step = calc_avg_memory("CF")

    # Load scaling analysis if available
    tf_scaling = None
    cf_scaling = None
    if scaling_path.exists():
        with open(scaling_path) as f:
            scaling_data = json.load(f)
            if "tf" in scaling_data:
                tf_scaling = ScalingAnalysis(**scaling_data["tf"])
            if "cf" in scaling_data:
                cf_scaling = ScalingAnalysis(**scaling_data["cf"])

    return ProgressiveLoadResult(
        max_corpora=max_corpora,
        corpora_order=corpora_order,
        num_runs=num_runs,
        steps=steps,
        tf_scaling=tf_scaling,
        cf_scaling=cf_scaling,
        tf_memory_by_step=tf_memory_by_step,
        cf_memory_by_step=cf_memory_by_step,
    )


def load_latency_result(results_dir: Path) -> LatencyBenchmarkResult | None:
    """Load latency results from CSV/JSON files.

    Args:
        results_dir: Directory containing benchmark results

    Returns:
        LatencyBenchmarkResult or None if not found
    """
    queries_path = results_dir / "latency/queries.json"
    measurements_path = results_dir / "latency/raw_measurements.csv"

    if not queries_path.exists() or not measurements_path.exists():
        return None

    # Load queries
    with open(queries_path) as f:
        queries = [SearchQuery(**q) for q in json.load(f)]

    # Load measurements
    measurements = []
    with open(measurements_path) as f:
        for row in csv.DictReader(f):
            measurements.append(
                QueryMeasurement(
                    query_id=row["query_id"],
                    implementation=row["implementation"],
                    run_id=int(row["run_id"]),
                    iteration=int(row["iteration"]),
                    execution_time_ms=float(row["execution_time_ms"]),
                    result_count=int(row["result_count"]),
                    success=row["success"].lower() == "true",
                    error=row.get("error"),
                )
            )

    # Calculate stats
    tf_times = [
        m.execution_time_ms
        for m in measurements
        if m.implementation == "TF" and m.success
    ]
    cf_times = [
        m.execution_time_ms
        for m in measurements
        if m.implementation == "CF" and m.success
    ]

    def make_stats(times: list[float]) -> StatisticalSummary | None:
        if not times:
            return None
        mean_val = float(np.mean(times))
        std_val = float(np.std(times))
        min_val = float(np.min(times))
        max_val = float(np.max(times))
        return StatisticalSummary(
            metric_name="latency",
            unit="ms",
            mean=mean_val,
            median=float(np.median(times)),
            std=std_val,
            variance=std_val**2,
            min=min_val,
            max=max_val,
            range=max_val - min_val,
            n=len(times),
            ci_lower=mean_val - 1.96 * std_val / np.sqrt(len(times)),
            ci_upper=mean_val + 1.96 * std_val / np.sqrt(len(times)),
            p25=float(np.percentile(times, 25)),
            p50=float(np.percentile(times, 50)),
            p75=float(np.percentile(times, 75)),
            p90=float(np.percentile(times, 90)),
            p95=float(np.percentile(times, 95)),
            p99=float(np.percentile(times, 99)),
        )

    # Determine corpus from results directory name or default
    corpus = "bhsa"

    return LatencyBenchmarkResult(
        corpus=corpus,
        queries=queries,
        measurements=measurements,
        statistics=[],
        tf_overall_stats=make_stats(tf_times),
        cf_overall_stats=make_stats(cf_times),
    )
